# Local Testing Guide

Run these checks before GitHub and deployment.

## Automated Smoke Test

Start both servers, then run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/local-smoke-test.ps1
```

Expected result:

- Backend health returns `ok`.
- Integration catalog returns supported apps.
- Automation creation returns a readable trigger and actions.
- Retry endpoint returns `retry_queued`.

## Manual Test Checklist

1. Landing page loads at `http://127.0.0.1:3000`.
2. Natural language automation box accepts a beginner-style request.
3. Builder returns a human-readable workflow summary.
4. Dashboard shows active automations.
5. Toggle button changes local automation state.
6. Retry button queues a retry.
7. Integrations page lists Gmail, Google Sheets, Telegram, WhatsApp, and Forms/Webhooks.
8. Pricing page shows Free, Pro, and Team-ready plans.
9. Settings page shows reliability defaults.
10. Login/signup pages require Clerk configuration; protected pages require login.

## API Failure Handling Tests

Short prompt should fail validation:

```powershell
$body = @{ prompt = "Do it"; business_type = "shop" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/automations/create `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Expected result: HTTP validation error.

Unsupported apps should not be deployed as raw invented actions. The planner maps only to the supported catalog in `backend/automation/catalog.py`.

## Authentication Test

- Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to `frontend/.env.local`.
- Add `CLERK_SECRET_KEY` to `frontend/.env.local`.
- Add `CLERK_SECRET_KEY` and `CLERK_JWT_ISSUER` to `backend/.env`.
- Restart `npm run dev`.
- Protected pages should require login.
- After login, call `/api/auth/me` or load the dashboard; a row should exist in `users` with the Clerk user id.

## Workflow Execution Test

Mock n8n mode:

- Leave `N8N_BASE_URL` and `N8N_API_KEY` blank.
- Create an automation.
- Response should include status `active`.

## Gmail Sending Test

- Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN` in `backend/.env`.
- Sign in so API calls include a Clerk bearer token.
- POST to `/api/gmail/send` with `to`, `subject`, and `body`.
- A successful response includes `success: true` and a Gmail `message_id`.

Real n8n mode:

- Add `N8N_BASE_URL` and `N8N_API_KEY` to `backend/.env`.
- Restart backend.
- Create an automation.
- Confirm the workflow appears in n8n.
