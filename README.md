# BeingAI Assistant

BeingAI Assistant is a localhost-first MVP SaaS for small businesses in India. Users describe repetitive work in plain English and the product turns it into validated, human-readable automations.

The MVP is intentionally simple:

- Next.js 15 frontend with TailwindCSS and Framer Motion
- FastAPI backend with OpenAI orchestration
- Supabase database schema
- Clerk-ready authentication
- Stripe-ready billing model
- n8n-ready automation deployment adapter
- Mock-safe integrations for WhatsApp, Telegram, Gmail, Google Sheets, and webhooks

## Repository Structure

```text
beingai-assistant/
  frontend/               Next.js SaaS app
    app/
    components/
    hooks/
    lib/
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
  supabase/
    migrations/           SQL schema and policies
  samples/
    workflows/            Human-readable sample automation plans
  docs/
    deployment.md         Vercel, Railway/Render, Supabase setup
    architecture.md       System design and reliability notes
```

## Local-First Workflow

Build and test locally before thinking about deployment.

1. Local development: run frontend, backend, and optional Supabase connection on localhost.
2. Testing: verify API responses, automation creation, failure handling, retry, and auth behavior.
3. GitHub setup: initialize Git, commit clean code, then push.
4. Deployment: only after localhost works, deploy frontend, backend, and production database.

## Local Quick Start

Copy the environment templates:

```powershell
Copy-Item .env.example .env
Copy-Item frontend/.env.example frontend/.env.local
Copy-Item backend/.env.example backend/.env
```

Install frontend dependencies:

```powershell
npm run install:frontend
npm run dev:frontend
```

Install backend dependencies:

```powershell
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Frontend: `http://127.0.0.1:3000`
- Backend health: `http://127.0.0.1:8000/api/health`
- Backend docs: `http://127.0.0.1:8000/docs`

For the full local workflow, read [docs/local-development.md](docs/local-development.md).

## Local Testing

Run the smoke test after both servers are running:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/local-smoke-test.ps1
```

For manual test cases, read [docs/testing.md](docs/testing.md).

## MVP Scope

The automation engine validates requests against a supported action catalog before deployment. Unsupported or vague requests return beginner-friendly clarification errors instead of hallucinated workflows.

For local development, n8n deployment is simulated unless `N8N_BASE_URL` and `N8N_API_KEY` are configured. This keeps demos safe while preserving the production integration boundary.

## Deployment

Once localhost works and tests pass, follow [docs/github.md](docs/github.md), then the production guide in [docs/deployment.md](docs/deployment.md).

Quick targets:

- **Frontend:** Vercel, root directory `frontend`
- **Backend:** Render or Railway, root directory `backend`, health check `/api/health`
- **Database:** Supabase migration in `supabase/migrations/`
