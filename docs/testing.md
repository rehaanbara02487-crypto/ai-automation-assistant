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
10. Login/signup pages render demo placeholders locally when Clerk keys are missing.

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

Unsupported apps should not be deployed as raw invented actions. The planner maps only to the supported catalog in `apps/api/app/automation_catalog.py`.

## Authentication Test

Local demo mode:

- Leave Clerk keys blank.
- Visit `/sign-in` and `/sign-up`.
- You should see local demo placeholders.

Real Clerk mode:

- Add `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` to `apps/web/.env.local`.
- Add `CLERK_SECRET_KEY` to `apps/web/.env.local`.
- Restart `npm run dev`.
- Protected pages should require login.

## Workflow Execution Test

Mock n8n mode:

- Leave `N8N_BASE_URL` and `N8N_API_KEY` blank.
- Create an automation.
- Response should include status `active`.

Real n8n mode:

- Add `N8N_BASE_URL` and `N8N_API_KEY` to `apps/api/.env`.
- Restart backend.
- Create an automation.
- Confirm the workflow appears in n8n.

