# Local Development

This project is designed to work on localhost before any production hosting.

## Folder Structure

```text
apps/
  web/                  Next.js frontend
  api/                  FastAPI backend
docs/                   Setup, testing, deployment notes
samples/workflows/      Example readable automation plans
scripts/                Local helper scripts
supabase/migrations/    Database schema
```

## 1. Prerequisites

- Node.js 20 or newer
- npm
- Python 3.11 or newer
- Supabase project, optional for the first local demo
- Clerk account, optional for the first local demo
- OpenAI API key, optional for the first local demo because the backend has a safe fallback planner

## 2. Environment Files

Copy examples first:

```powershell
Copy-Item .env.example .env
Copy-Item apps/web/.env.example apps/web/.env.local
Copy-Item apps/api/.env.example apps/api/.env
```

For the fastest local demo, leave Clerk, Supabase, OpenAI, n8n, and Stripe keys blank.

Recommended local values:

```text
apps/web/.env.local
NEXT_PUBLIC_APP_URL=http://127.0.0.1:3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

```text
apps/api/.env
APP_ENV=development
API_CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
OPENAI_MODEL=gpt-4.1-mini
```

Never put real secrets in Git.

## 3. Install Dependencies

Frontend:

```powershell
cd apps/web
npm install
```

Backend:

```powershell
cd apps/api
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

## 4. Run Locally

Terminal 1, backend:

```powershell
cd apps/api
.venv/Scripts/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, frontend:

```powershell
cd apps/web
npm run dev
```

Open:

- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000/docs`

## 5. Local Database

The backend runs without Supabase by using an in-memory store. This is best for the first demo.

To connect Supabase locally:

1. Create a Supabase project.
2. Run `supabase/migrations/001_initial_schema.sql`.
3. Add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to `apps/api/.env`.
4. Add `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` to `apps/web/.env.local`.

## 6. Local API Testing

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Create an automation:

```powershell
$body = @{
  prompt = "When someone fills my form, send WhatsApp message and save lead."
  business_type = "local_shop"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/automations/create `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

List automations:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/automations
```

Retry automation:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/automations/YOUR_AUTOMATION_ID/retry `
  -Method Post
```

## 7. Debugging

- If the frontend cannot call the backend, check `NEXT_PUBLIC_API_URL`.
- If CORS fails, check `API_CORS_ORIGINS`.
- If OpenAI is blank, the backend uses the deterministic fallback planner.
- If n8n is blank, deployment uses mock mode.
- If Clerk keys are blank, auth pages show local demo placeholders.

