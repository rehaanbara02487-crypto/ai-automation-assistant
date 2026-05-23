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
2. Open **SQL Editor** and run `supabase/migrations/001_initial_schema.sql`.
3. Copy from **Project Settings → API**:
   - Project URL → `SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_URL`
   - `anon` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY` (frontend, optional today)
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (**backend only**)
4. Confirm tables exist: `users`, `automations`, `workflow_logs`, `plans`.

**Production note:** The backend uses the **service role** server-side. RLS protects direct client access; do not ship the service role to Vercel.

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
3. Add the same environment variables as Render.
4. Generate a public domain.

### Verify backend

```bash
curl https://YOUR-API-URL/api/health
curl https://YOUR-API-URL/api/ready
```

- `/api/health` → `200` always when the process is up.
- `/api/ready` → `200` when configured services are reachable; `503` if Supabase is set but unreachable.

---

## Step 3 — Clerk (production auth)

1. Create a Clerk application at [clerk.com](https://clerk.com).
2. Add your Vercel production URL to **Allowed origins** and redirect URLs.
3. Copy keys:
   - **Publishable key** → `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (Vercel)
   - **Secret key** → `CLERK_SECRET_KEY` (backend only)
   - **Frontend API URL** (issuer) → `CLERK_JWT_ISSUER` (backend only), e.g. `https://your-app.clerk.accounts.dev`
4. With both `CLERK_SECRET_KEY` and `CLERK_JWT_ISSUER` on the backend, demo `mock_user_id` mode is disabled and JWT auth is required.

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
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Server-side DB access |
| `CLERK_SECRET_KEY` | Yes | Verifies session tokens |
| `CLERK_JWT_ISSUER` | Yes | Clerk JWT issuer URL |
| `OPENAI_API_KEY` | No | AI planner; fallback if empty |
| `OPENAI_MODEL` | No | Default `gpt-4.1-mini` |
| `N8N_BASE_URL` | No | Real n8n; mock if empty |
| `N8N_API_KEY` | No | n8n API key |
| `N8N_WEBHOOK_BASE_URL` | No | Webhook trigger base URL |
| `MOCK_USER_ID` | No | Local demo only |
| `STRIPE_SECRET_KEY` | No | Billing (future) |
| `STRIPE_WEBHOOK_SECRET` | No | Billing webhooks (future) |

### Frontend (Vercel)

| Variable | Required (prod) | Description |
|----------|-----------------|-------------|
| `NEXT_PUBLIC_APP_URL` | Yes | Public site URL |
| `NEXT_PUBLIC_API_URL` | Yes | Backend public URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key |
| `NEXT_PUBLIC_SUPABASE_URL` | No | Reserved for client reads |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | No | Reserved for client reads |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | No | Billing (future) |

---

## Mock mode in production (demos only)

Leave `N8N_*` empty to keep mock workflow execution. Leave `OPENAI_API_KEY` empty for the keyword fallback planner.

**Do not** disable Clerk or Supabase in real production tenants—use a staging project with demo keys instead.

---

## Optional: n8n

1. Host n8n Cloud or self-hosted instance.
2. Set `N8N_BASE_URL` and `N8N_API_KEY` on the backend.
3. Optionally set `N8N_WEBHOOK_BASE_URL` for webhook-triggered runs.
4. Map real node types in a future release; MVP uses internal workflow representation.

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
| Supabase FK error on create | Ensure Clerk user sync runs (`ensure_user` on first request) |
| `/api/ready` returns 503 | Check `SUPABASE_URL` and service role key |
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
