# BeingAI Assistant Architecture

## Product Principle

BeingAI Assistant is not a generic chatbot. It is an automation outcome product. The user describes a business process, the system creates a validated automation plan, deploys it internally, and shows the result in plain language.

## System Flow

1. User enters a task in the Automation Builder.
2. Frontend sends the plain-English request to FastAPI.
3. AI orchestrator maps the request to a constrained automation catalog.
4. Validator rejects unsupported triggers, actions, missing fields, or risky assumptions.
5. n8n adapter deploys the workflow or runs in mock mode locally.
6. Backend stores automation, steps, deployment status, and activity logs in Supabase.
7. Dashboard shows status, latest activity, errors, and retry controls.

## Reliability Model

- The AI returns structured automation plans only.
- Plans are validated against `automation_catalog.py`.
- Deployment failures are logged with actionable user-facing messages.
- Failed executions can be retried through a dedicated API route.
- Integration secrets are never sent to the browser.
- n8n workflow JSON is never exposed to users.

## Supported MVP Apps

- Forms and webhooks
- Google Sheets
- Gmail
- Telegram
- WhatsApp via mock provider or future approved provider

## Production Boundaries

- Clerk handles user identity.
- Supabase stores app data with row-level security.
- FastAPI uses service role credentials server-side only.
- Stripe is prepared for subscriptions, with plan enforcement designed around `plans` and `subscriptions`.
- n8n remains an internal execution engine.

