# Local Development

This project is designed to work on localhost before any production hosting.

## Folder Structure

```text
frontend/               Next.js frontend
  app/
  components/
  lib/
  hooks/
  services/
  types/
backend/                FastAPI backend
  routes/
  services/
  ai/
  automation/
  models/
  database/
  middleware/
docs/                   Setup, testing, deployment notes
samples/workflows/      Example readable automation plans
scripts/                Local helper scripts
supabase/migrations/    Database schema
```

## 1. Prerequisites

- Node.js 20 or newer
- npm
- Python 3.11 or newer
- Supabase project or local PostgreSQL database
- Clerk account
- OpenAI API key, optional for the first local demo because the backend has a safe fallback planner

## 2. Environment Files

Copy examples first:

```powershell
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env.local
Copy-Item backend/.env.example backend/.env
```

Set Clerk keys and `DATABASE_URL` before using the dashboard. Protected API routes require a Clerk bearer token.

Recommended local values:

```text
frontend/.env.local
NEXT_PUBLIC_APP_URL=http://127.0.0.1:3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

```text
backend/.env
APP_ENV=development
API_CORS_ORIGINS=http://127.0.0.1:3000,http://localhost:3000
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
CLERK_SECRET_KEY=sk_test_...
CLERK_JWT_ISSUER=https://your-app.clerk.accounts.dev
OPENAI_MODEL=gpt-4.1-mini
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
```

Never put real secrets in Git.

## 3. Install Dependencies

Frontend:

```powershell
cd frontend
npm install
```

Backend:

```powershell
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

## 4. Run Locally

Terminal 1, backend:

```powershell
cd backend
.venv/Scripts/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, frontend:

```powershell
cd frontend
npm run dev
```

Open:

- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000/docs`

## 5. Local Database

The backend requires PostgreSQL persistence through `DATABASE_URL`.

1. Create a Supabase project.
2. Run all files in `supabase/migrations/` in numeric order, or let backend startup create missing SQLAlchemy tables.
3. Add the Supabase Postgres connection string to `backend/.env` as `DATABASE_URL`.
4. Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to `frontend/.env.local`.

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
- If n8n is blank, deployment uses mock workflow execution.
- If Gmail variables are blank, `/api/gmail/send` returns a clear configuration error.
- If Clerk keys are blank, protected API routes return an auth configuration error.
