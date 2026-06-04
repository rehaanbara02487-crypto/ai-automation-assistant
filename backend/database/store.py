from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Automation, User, WorkflowLog
from models.schemas import (
    ActivityLog,
    ActivityLogRecord,
    AutomationStatus,
    AutomationSummary,
    CreateAutomationRecordRequest,
    StepKind,
    UpdateAutomationRecordRequest,
    WorkflowStep,
)


class AutomationStore:
    def __init__(self, db: Session):
        self.db = db

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    async def ensure_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> User:
        now = datetime.now(timezone.utc)
        user = self.db.get(User, user_id)
        if not user:
            user = User(id=user_id, email=email, full_name=full_name, last_login_at=now)
            self.db.add(user)
        else:
            if email:
                user.email = email
            if full_name:
                user.full_name = full_name
            user.last_login_at = now
        self._commit()
        self.db.refresh(user)
        return user

    async def get_user(self, user_id: str) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise KeyError(user_id)
        return user

    async def list_automations(self, user_id: str) -> List[AutomationSummary]:
        rows = self.db.scalars(
            select(Automation).where(Automation.user_id == user_id).order_by(Automation.created_at.desc())
        ).all()
        return [self._from_model(row) for row in rows]

    async def create_automation_record(
        self,
        user_id: str,
        payload: CreateAutomationRecordRequest,
    ) -> AutomationSummary:
        await self.ensure_user(user_id)
        workflow_json = self._normalize_workflow_json(
            payload.workflow_json,
            trigger_type=payload.trigger_type,
            description=payload.description,
        )
        automation = Automation(
            user_id=user_id,
            title=payload.title,
            description=payload.description,
            trigger_type=payload.trigger_type,
            status=payload.status.value,
            workflow_json=workflow_json,
        )
        self.db.add(automation)
        self._commit()
        self.db.refresh(automation)
        return self._from_model(automation)

    async def update_automation_record(
        self,
        automation_id: str,
        user_id: str,
        payload: UpdateAutomationRecordRequest,
    ) -> AutomationSummary:
        automation = self._get_model(automation_id, user_id)
        if payload.title is not None:
            automation.title = payload.title
        if payload.description is not None:
            automation.description = payload.description
        if payload.trigger_type is not None:
            automation.trigger_type = payload.trigger_type
        if payload.status is not None:
            automation.status = payload.status.value
        if payload.workflow_json is not None:
            automation.workflow_json = self._normalize_workflow_json(
                payload.workflow_json,
                trigger_type=automation.trigger_type,
                description=automation.description,
            )
        self._commit()
        self.db.refresh(automation)
        return self._from_model(automation)

    async def delete_automation(self, automation_id: str, user_id: str) -> None:
        automation = self._get_model(automation_id, user_id)
        self.db.delete(automation)
        self._commit()

    async def save_automation(self, user_id: str, automation: AutomationSummary, workflow_id: str) -> AutomationSummary:
        await self.ensure_user(user_id)
        workflow_json = {
            "trigger": automation.trigger,
            "actions": automation.actions,
            "summary": automation.summary,
            "steps": [step.model_dump(mode="json") for step in automation.steps],
            "workflow_id": workflow_id,
            "error_count": automation.error_count,
            "run_count": automation.run_count,
            "last_run_at": automation.last_run_at,
        }
        row = Automation(
            id=automation.id,
            user_id=user_id,
            title=automation.title,
            description=automation.summary,
            trigger_type=automation.trigger,
            status=automation.status.value if hasattr(automation.status, "value") else automation.status,
            workflow_json=workflow_json,
        )
        self.db.add(row)
        self._commit()
        self.db.refresh(row)
        return self._from_model(row)

    async def update_status(self, automation_id: str, status: AutomationStatus, user_id: str) -> AutomationSummary:
        automation = self._get_model(automation_id, user_id)
        automation.status = status.value
        self._commit()
        self.db.refresh(automation)
        return self._from_model(automation)

    async def get_workflow_id(self, automation_id: str, user_id: str) -> str:
        automation = self._get_model(automation_id, user_id)
        workflow_id = self._workflow_json(automation).get("workflow_id")
        return str(workflow_id or f"mock-{automation_id}")

    async def automation_owned_by(self, automation_id: str, user_id: str) -> bool:
        return self.db.scalar(
            select(Automation.id).where(Automation.id == automation_id, Automation.user_id == user_id).limit(1)
        ) is not None

    async def get_automation(self, automation_id: str, user_id: str) -> AutomationSummary:
        return self._from_model(self._get_model(automation_id, user_id))

    async def record_run_success(self, automation_id: str, user_id: str, finished_at: str) -> AutomationSummary:
        automation = self._get_model(automation_id, user_id)
        data = self._workflow_json(automation)
        data["run_count"] = int(data.get("run_count", 0)) + 1
        data["last_run_at"] = finished_at
        if automation.status == AutomationStatus.failed.value:
            automation.status = AutomationStatus.active.value
        automation.workflow_json = data
        self._commit()
        self.db.refresh(automation)
        return self._from_model(automation)

    async def record_run_failure(self, automation_id: str, user_id: str, finished_at: str) -> AutomationSummary:
        automation = self._get_model(automation_id, user_id)
        data = self._workflow_json(automation)
        data["error_count"] = int(data.get("error_count", 0)) + 1
        data["last_run_at"] = finished_at
        automation.status = AutomationStatus.failed.value
        automation.workflow_json = data
        self._commit()
        self.db.refresh(automation)
        return self._from_model(automation)

    async def log(self, log: ActivityLog) -> None:
        self.db.add(
            WorkflowLog(
                automation_id=log.automation_id,
                status=log.status,
                message=log.message,
                metadata_json=log.metadata,
            )
        )
        self._commit()

    async def list_logs(self, automation_id: str) -> List[ActivityLogRecord]:
        rows = self.db.scalars(
            select(WorkflowLog)
            .where(WorkflowLog.automation_id == automation_id)
            .order_by(WorkflowLog.created_at.desc())
            .limit(25)
        ).all()
        return [
            ActivityLogRecord(
                id=row.id,
                automation_id=row.automation_id,
                status=row.status,
                message=row.message,
                metadata=row.metadata_json,
                created_at=self._to_iso(row.created_at),
            )
            for row in rows
        ]

    def _get_model(self, automation_id: str, user_id: str) -> Automation:
        automation = self.db.scalar(
            select(Automation).where(Automation.id == automation_id, Automation.user_id == user_id).limit(1)
        )
        if not automation:
            raise KeyError(automation_id)
        return automation

    def _workflow_json(self, automation: Automation) -> dict[str, Any]:
        return dict(automation.workflow_json or {})

    def _normalize_workflow_json(
        self,
        workflow_json: dict[str, Any],
        *,
        trigger_type: str,
        description: str,
    ) -> dict[str, Any]:
        data = dict(workflow_json or {})
        data.setdefault("trigger", trigger_type)
        data.setdefault("actions", [])
        data.setdefault("summary", description)
        data.setdefault("steps", [{"label": trigger_type, "app": "manual", "kind": StepKind.trigger.value}])
        data.setdefault("workflow_id", f"mock-{uuid4()}")
        data.setdefault("error_count", 0)
        data.setdefault("run_count", 0)
        data.setdefault("last_run_at", None)
        return data

    def _from_model(self, row: Automation) -> AutomationSummary:
        data = self._workflow_json(row)
        steps = data.get("steps") or [{"label": row.trigger_type, "app": "manual", "kind": StepKind.trigger.value}]
        return AutomationSummary(
            id=row.id,
            title=row.title,
            status=row.status,
            trigger=str(data.get("trigger") or row.trigger_type),
            actions=list(data.get("actions") or []),
            summary=str(data.get("summary") or row.description),
            steps=[step if isinstance(step, WorkflowStep) else WorkflowStep(**step) for step in steps],
            last_run_at=data.get("last_run_at"),
            error_count=int(data.get("error_count", 0)),
            run_count=int(data.get("run_count", 0)),
        )

    def _to_iso(self, value: datetime | None) -> str:
        return (value or datetime.now(timezone.utc)).isoformat()
