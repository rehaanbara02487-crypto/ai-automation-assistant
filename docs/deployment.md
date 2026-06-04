# Production Deployment Guide

Deploy in this order: **Supabase → Backend (Render/Railway) → Clerk → Frontend (Vercel)**.

## Production architecture

```text
User browser
    → Vercel (Next.js frontend)
        → Clerk (auth session / JWT)
        → Render or Railway (FastAPI API)
            → Supabase (Postgres + RLS schema)
            → OpenAI (optional)
            → n8n (optional; mock mode if unset)
```

| Component | Host | Root directory |
|-----------|------|----------------|
| Frontend | Vercel | `frontend` |
| Backend | Render or Railway | `backend` |
| Database | Supabase | SQL in `supabase/migrations/` |

---

## Pre-deploy checklist

1. `npm run install:frontend && npm run build:frontend` succeeds locally.
2. `cd backend && pip install -r requirements.txt && uvicorn main:app --port 8000` starts.
3. `scripts/local-smoke-test.ps1` passes against local API.
4. Git repo pushed to GitHub (no `.env` files committed).

---

## Step 1 — Supabase (production database)

1. Create a project at [supabase.com](https://supabase.com).
2. Open **SQL Editor** and run the SQL files in `supabase/migrations/` in numeric order.
3. Copy from **Project Settings → Database → Connection string**:
   - Postgres connection string → `DATABASE_URL` (**backend only**)
4. Copy from **Project Settings → API** if you need Supabase client metadata later:
   - Project URL → `SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_URL`
   - `anon` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY` (frontend, optional today)
4. Confirm tables exist: `users`, `automations`, `workflow_logs`, `plans`.

**Production note:** The backend connects to Supabase Postgres through SQLAlchemy using `DATABASE_URL`. Do not ship backend database credentials to Vercel.

---

## Step 2 — Backend (Render or Railway)

### Render (Blueprint)

1. Connect the GitHub repo in Render.
2. Use the included `render.yaml` or create a **Web Service** manually:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/api/health`
3. Set environment variables from `backend/.env.example` (see table below).
4. Set `APP_ENV=production`.
5. Deploy and copy the public URL (e.g. `https://beingai-api.onrender.com`).

### Railway

1. New project → **Deploy from GitHub** → set root to `backend`.
2. Start command (Procfile): `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add the Railway environment variables below.
4. Generate a public domain.

Railway backend variables:

```env
APP_ENV=production
API_CORS_ORIGINS=https://your-app.vercel.app
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
CLERK_SECRET_KEY=sk_live_...
CLERK_JWT_ISSUER=https://your-app.clerk.accounts.dev
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
N8N_BASE_URL=
N8N_API_KEY=
N8N_WEBHOOK_BASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

### Verify backend

```bash
curl https://YOUR-API-URL/api/health
curl https://YOUR-API-URL/api/ready
```

- `/api/health` → `200` always when the process is up.
- `/api/ready` → `200` when database and Clerk config are present/reachable; `503` if required config is missing or the database is unreachable.

---

## Step 3 — Clerk (production auth)

1. Create a Clerk application at [clerk.com](https://clerk.com).
2. Add your Vercel production URL to **Allowed origins** and redirect URLs.
3. Copy keys:
   - **Publishable key** → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (Vercel)
   - **Secret key** → `CLERK_SECRET_KEY` (backend and Vercel server-side env)
   - **Frontend API URL** (issuer) → `CLERK_JWT_ISSUER` (backend only), e.g. `https://your-app.clerk.accounts.dev`
4. With both `CLERK_SECRET_KEY` and `CLERK_JWT_ISSUER` on the backend, JWT auth is required for automation and billing routes.

---

## Step 4 — Frontend (Vercel)

1. Import the GitHub repo in Vercel.
2. Set **Root Directory** to `frontend` (important).
3. Framework preset: **Next.js** (auto-detected).
4. Build command: `npm run build` (default).
5. Install command: `npm install` (default).
6. Set environment variables from `frontend/.env.example`:

| Variable | Example |
|----------|---------|
| `NEXT_PUBLIC_APP_URL` | `https://your-app.vercel.app` |
| `NEXT_PUBLIC_API_URL` | `https://your-api.onrender.com` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_...` |
| `CLERK_SECRET_KEY` | `sk_live_...` |

7. Deploy.

### Verify frontend

- Landing and dashboard load over HTTPS.
- Signed-in user can create an automation (network tab shows `Authorization: Bearer` on API calls).
- Dashboard metrics and activity update after create/retry.

---

## Step 5 — CORS (required)

On the backend, set `API_CORS_ORIGINS` to your exact Vercel URL(s), comma-separated:

```env
API_CORS_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com
```

No trailing slashes. Include `http://127.0.0.1:3000` only for local development.

---

## Environment variables reference

### Backend (Render / Railway)

| Variable | Required (prod) | Description |
|----------|-----------------|-------------|
| `APP_ENV` | Yes | `production` |
| `API_CORS_ORIGINS` | Yes | Frontend origin(s) |
| `DATABASE_URL` | Yes | Supabase Postgres connection string for SQLAlchemy |
| `SUPABASE_URL` | No | Reserved Supabase project metadata |
| `SUPABASE_SERVICE_ROLE_KEY` | No | Reserved for future server-side Supabase APIs |
| `CLERK_SECRET_KEY` | Yes | Verifies session tokens |
| `CLERK_JWT_ISSUER` | Yes | Clerk JWT issuer URL |
| `OPENAI_API_KEY` | No | AI planner; fallback if empty |
| `OPENAI_MODEL` | No | Default `gpt-4.1-mini` |
| `N8N_BASE_URL` | No | Real n8n; mock if empty |
| `N8N_API_KEY` | No | n8n API key |
| `N8N_WEBHOOK_BASE_URL` | No | Webhook trigger base URL |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client id for Gmail sending |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret for Gmail sending |
| `GOOGLE_REFRESH_TOKEN` | No | OAuth refresh token with Gmail send scope |
| `STRIPE_SECRET_KEY` | No | Billing (future) |
| `STRIPE_WEBHOOK_SECRET` | No | Billing webhooks (future) |

### Frontend (Vercel)

| Variable | Required (prod) | Description |
|----------|-----------------|-------------|
| `NEXT_PUBLIC_APP_URL` | Yes | Public site URL |
| `NEXT_PUBLIC_API_URL` | Yes | Backend public URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key |
| `CLERK_SECRET_KEY` | Yes | Clerk secret key for Next.js middleware |
| `NEXT_PUBLIC_SUPABASE_URL` | No | Reserved for client reads |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | No | Reserved for client reads |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | No | Billing (future) |

---

## Optional mock integrations

Leave `N8N_*` empty to keep mock workflow execution. Leave `OPENAI_API_KEY` empty for the keyword fallback planner.

Clerk and `DATABASE_URL` are required; authentication no longer falls back to a mock user.

---

## Optional: n8n

1. Host n8n Cloud or self-hosted instance.
2. Set `N8N_BASE_URL` and `N8N_API_KEY` on the backend.
3. Optionally set `N8N_WEBHOOK_BASE_URL` for webhook-triggered runs.
4. Map real node types in a future release; MVP uses internal workflow representation.

---

## Optional: Gmail Sending

The `POST /api/gmail/send` endpoint sends through the Gmail API using OAuth2.

Google Cloud Console setup:

1. Create or select a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Gmail API** for the project.
3. Configure **OAuth consent screen** and add your sending Gmail account as a test user if the app is in testing.
4. Create an **OAuth client ID** for a Web application.
5. Add `https://developers.google.com/oauthplayground` as an authorized redirect URI while generating the refresh token.
6. In OAuth Playground, authorize the scope `https://www.googleapis.com/auth/gmail.send`.
7. Exchange the authorization code for tokens and copy the refresh token.
8. Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` on Railway.

The refresh token belongs only in backend/Railway environment variables.

---

## Optional: Stripe

1. Create products matching `plans` in Supabase.
2. Set backend `STRIPE_*` and frontend `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`.
3. Wire checkout webhooks (endpoint stub exists at `/api/billing/create-checkout-session`).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS error in browser | Add exact Vercel URL to `API_CORS_ORIGINS` |
| `401 Authentication required` | Set Clerk keys on backend + frontend; sign in |
| Supabase FK error on create | Sign in again so `/api/auth/me` can create the `users` row |
| `/api/ready` returns 503 | Check `DATABASE_URL`, `CLERK_SECRET_KEY`, and `CLERK_JWT_ISSUER` |
| Vercel build fails | Confirm **Root Directory** = `frontend`, Node 20+ |
| API 500 in production | Check Render/Railway logs; generic message hides stack traces by design |

---

## Health endpoints

| Path | Purpose |
|------|---------|
| `GET /health` | Platform liveness (Render/Railway) |
| `GET /api/health` | App liveness + environment |
| `GET /api/ready` | Readiness (DB + config flags) |

OpenAPI docs (`/docs`) are **disabled** when `APP_ENV=production`.
