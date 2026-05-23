# Deployment

Deployment is Phase 4. Do not start here.

Before deployment:

1. Run the frontend locally with `npm run dev`.
2. Run the backend locally with `uvicorn`.
3. Run `scripts/local-smoke-test.ps1`.
4. Test auth locally with Clerk keys or demo placeholders.
5. Push clean code to GitHub.

## Frontend: Vercel

1. Create a Vercel project from `apps/web`.
2. Set the build command to `npm run build`.
3. Set the output framework to Next.js.
4. Add environment variables from `apps/web/.env.example`.
5. Set `NEXT_PUBLIC_API_URL` to the deployed backend URL.

## Backend: Railway or Render

1. Create a Python service from `apps/api`.
2. Use Python 3.11 or newer.
3. Install with `pip install -r requirements.txt`.
4. Start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Add environment variables from `apps/api/.env.example`.

## Supabase

1. Create a Supabase project.
2. Run `supabase/migrations/001_initial_schema.sql`.
3. Copy the project URL, anon key, and service role key into the frontend and backend env files.
4. Keep the service role key backend-only.

## n8n

1. Host n8n privately or use n8n Cloud.
2. Create an API key.
3. Set `N8N_BASE_URL`, `N8N_API_KEY`, and `N8N_WEBHOOK_BASE_URL`.
4. Keep n8n workflow JSON internal. Users should only see readable summaries.

## Stripe

1. Create products for Free, Pro, and Team-ready plans.
2. Set `STRIPE_SECRET_KEY` and webhook secret on the backend.
3. Set publishable key on the frontend.
4. Connect webhook events to update subscription records.
