from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ai.orchestrator import AIOrchestrator
from auth.deps import get_current_user, get_store
from automation.executor import WorkflowExecutor
from automation.n8n_client import N8NClient
from automation.validator import AutomationValidationError
from config import Settings, get_settings
from database.store import AutomationStore
from models.schemas import (
    ActivityLog,
    ActivityLogRecord,
    AutomationStatus,
    AutomationSummary,
    CreateAutomationRequest,
    CreateAutomationRecordRequest,
    CurrentUserResponse,
    GmailSendRequest,
    GmailSendResponse,
    Integration,
    ToggleAutomationRequest,
    UpdateAutomationRecordRequest,
)
from services.gmail_service import GmailService

router = APIRouter(prefix="/api")


@router.get("/auth/me", response_model=CurrentUserResponse)
async def current_user_profile(
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> CurrentUserResponse:
    try:
        user = await store.get_user(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
    return CurrentUserResponse(id=user.id, email=user.email, full_name=user.full_name)


@router.post("/gmail/send", response_model=GmailSendResponse)
async def send_gmail(
    payload: GmailSendRequest,
    settings: Settings = Depends(get_settings),
    user_id: str = Depends(get_current_user),
) -> GmailSendResponse | JSONResponse:
    try:
        result = GmailService(settings).send_email(to=payload.to, subject=payload.subject, body=payload.body)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content=GmailSendResponse(success=False, message=str(exc.detail)).model_dump(),
        )

    return GmailSendResponse(
        success=True,
        message="Email sent successfully.",
        message_id=result["message_id"],
    )


@router.post("/automations", response_model=AutomationSummary)
async def create_automation_record(
    payload: CreateAutomationRecordRequest,
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> AutomationSummary:
    return await store.create_automation_record(user_id, payload)


@router.post("/automations/create", response_model=AutomationSummary)
async def create_automation(
    payload: CreateAutomationRequest,
    settings: Settings = Depends(get_settings),
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> AutomationSummary:
    try:
        plan = await AIOrchestrator(settings).create_plan(payload.prompt, payload.business_type)
    except AutomationValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    deployment = await N8NClient(settings).deploy(plan)
    summary = AutomationSummary(**plan.model_dump(), error_count=0, run_count=0)
    await store.save_automation(user_id, summary, deployment["workflow_id"])
    await store.log(
        ActivityLog(
            automation_id=summary.id,
            status="created",
            message="Automation validated and deployed.",
            metadata={"workflow_id": deployment["workflow_id"], "provider": deployment.get("provider")},
        )
    )

    executor = WorkflowExecutor(settings, store)
    await executor.run_automation(summary.id, user_id, trigger="create")
    return await store.get_automation(summary.id, user_id)


@router.get("/automations", response_model=list[AutomationSummary])
async def list_automations(
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> list[AutomationSummary]:
    return await store.list_automations(user_id)


@router.get("/automations/{automation_id}", response_model=AutomationSummary)
async def get_automation(
    automation_id: str,
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> AutomationSummary:
    try:
        return await store.get_automation(automation_id, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Automation not found") from exc


@router.put("/automations/{automation_id}", response_model=AutomationSummary)
async def update_automation(
    automation_id: str,
    payload: UpdateAutomationRecordRequest,
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> AutomationSummary:
    try:
        return await store.update_automation_record(automation_id, user_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Automation not found") from exc


@router.delete("/automations/{automation_id}")
async def delete_automation(
    automation_id: str,
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> dict[str, str]:
    try:
        await store.delete_automation(automation_id, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Automation not found") from exc
    return {"status": "deleted"}


@router.post("/automations/{automation_id}/toggle", response_model=AutomationSummary)
async def toggle_automation(
    automation_id: str,
    payload: ToggleAutomationRequest,
    settings: Settings = Depends(get_settings),
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> AutomationSummary:
    try:
        workflow_id = await store.get_workflow_id(automation_id, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Automation not found") from exc

    await N8NClient(settings).activate(workflow_id, payload.enabled)
    status = AutomationStatus.active if payload.enabled else AutomationStatus.paused
    try:
        result = await store.update_status(automation_id, status, user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Automation not found") from exc
    await store.log(ActivityLog(automation_id=automation_id, status=status.value, message="Automation status changed."))
    return result


@router.post("/automations/{automation_id}/retry")
async def retry_automation(
    automation_id: str,
    settings: Settings = Depends(get_settings),
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> dict:
    if not await store.automation_owned_by(automation_id, user_id):
        raise HTTPException(status_code=404, detail="Automation not found")

    await store.log(
        ActivityLog(
            automation_id=automation_id,
            status="retry_requested",
            message="Retry requested by user.",
            metadata={"trigger": "retry"},
        )
    )

    executor = WorkflowExecutor(settings, store)
    try:
        return await executor.run_automation(automation_id, user_id, trigger="retry")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/automations/{automation_id}/logs", response_model=list[ActivityLogRecord])
async def automation_logs(
    automation_id: str,
    store: AutomationStore = Depends(get_store),
    user_id: str = Depends(get_current_user),
) -> list[ActivityLogRecord]:
    if not await store.automation_owned_by(automation_id, user_id):
        raise HTTPException(status_code=404, detail="Automation not found")
    return await store.list_logs(automation_id)


@router.post("/billing/create-checkout-session")
async def create_checkout_session(user_id: str = Depends(get_current_user)) -> dict:
    return {
        "status": "stripe_ready",
        "message": "Connect Stripe prices and create hosted checkout sessions here.",
        "user_id": user_id,
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
