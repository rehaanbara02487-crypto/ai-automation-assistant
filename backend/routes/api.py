from fastapi import APIRouter, Depends, HTTPException

from app.ai_orchestrator import AIOrchestrator
from app.config import Settings, get_settings
from app.models import (
    ActivityLog,
    ActivityLogRecord,
    AutomationStatus,
    AutomationSummary,
    CreateAutomationRequest,
    Integration,
    ToggleAutomationRequest,
)
from app.n8n_client import N8NClient
from app.storage import AutomationStore
from app.validator import AutomationValidationError

router = APIRouter(prefix="/api")


def get_user_id(settings: Settings = Depends(get_settings)) -> str:
    return settings.mock_user_id


def get_store(settings: Settings = Depends(get_settings)) -> AutomationStore:
    if not hasattr(get_store, "_store"):
        get_store._store = AutomationStore(settings)  # type: ignore[attr-defined]
    return get_store._store  # type: ignore[attr-defined]


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "beingai-api"}


@router.post("/automations/create", response_model=AutomationSummary)
async def create_automation(
    payload: CreateAutomationRequest,
    settings: Settings = Depends(get_settings),
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_user_id),
) -> AutomationSummary:
    try:
        plan = await AIOrchestrator(settings).create_plan(payload.prompt, payload.business_type)
    except AutomationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    deployment = await N8NClient(settings).deploy(plan)
    summary = AutomationSummary(**plan.model_dump(), error_count=0, run_count=0)
    await store.save_automation(user_id, summary, deployment["workflow_id"])
    await store.log(ActivityLog(automation_id=summary.id, status="created", message="Automation validated and deployed."))
    return summary


@router.get("/automations", response_model=list[AutomationSummary])
async def list_automations(
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_user_id),
) -> list[AutomationSummary]:
    return await store.list_automations(user_id)


@router.post("/automations/{automation_id}/toggle", response_model=AutomationSummary)
async def toggle_automation(
    automation_id: str,
    payload: ToggleAutomationRequest,
    settings: Settings = Depends(get_settings),
    store: AutomationStore = Depends(get_store),
) -> AutomationSummary:
    workflow_id = await store.get_workflow_id(automation_id)
    await N8NClient(settings).activate(workflow_id, payload.enabled)
    status = AutomationStatus.active if payload.enabled else AutomationStatus.paused
    result = await store.update_status(automation_id, status)
    await store.log(ActivityLog(automation_id=automation_id, status=status.value, message="Automation status changed."))
    return result


@router.post("/automations/{automation_id}/retry")
async def retry_automation(
    automation_id: str,
    store: AutomationStore = Depends(get_store),
) -> dict:
    await store.log(ActivityLog(automation_id=automation_id, status="retry_queued", message="Retry requested by user."))
    return {"status": "retry_queued"}


@router.get("/automations/{automation_id}/logs", response_model=list[ActivityLogRecord])
async def automation_logs(
    automation_id: str,
    store: AutomationStore = Depends(get_store),
) -> list[ActivityLogRecord]:
    return await store.list_logs(automation_id)


@router.post("/billing/create-checkout-session")
async def create_checkout_session() -> dict:
    return {
        "status": "stripe_ready",
        "message": "Connect Stripe prices and create hosted checkout sessions here.",
    }


@router.get("/integrations", response_model=list[Integration])
async def integrations() -> list[Integration]:
    return [
        Integration(id="gmail", name="Gmail", description="Auto reply to customer inquiries.", status="available"),
        Integration(id="google_sheets", name="Google Sheets", description="Save leads and reports.", status="available"),
        Integration(id="telegram", name="Telegram", description="Owner alerts and quick updates.", status="available"),
        Integration(id="whatsapp", name="WhatsApp", description="Mock reminders and customer messages.", status="mock"),
        Integration(id="forms", name="Forms/Webhooks", description="Receive website leads and events.", status="connected"),
    ]
