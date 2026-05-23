from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from automation.n8n_client import N8NClient
from config import Settings
from database.store import AutomationStore
from models.schemas import ActivityLog, AutomationStatus, AutomationSummary, ExecutionStatus


class WorkflowExecutor:
    def __init__(self, settings: Settings, store: AutomationStore):
        self.settings = settings
        self.store = store
        self.n8n = N8NClient(settings)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def _log(
        self,
        automation_id: str,
        status: str,
        message: str,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        payload = metadata or {}
        payload.setdefault("recorded_at", self._now())
        await self.store.log(
            ActivityLog(
                automation_id=automation_id,
                status=status,
                message=message,
                metadata=payload,
            )
        )

    async def run_automation(
        self,
        automation_id: str,
        user_id: str,
        *,
        trigger: str = "manual",
    ) -> Dict[str, Any]:
        summary = await self.store.get_automation(automation_id, user_id)
        if summary.status == AutomationStatus.paused:
            raise ValueError("Automation is paused. Enable it before running.")

        workflow_id = await self.store.get_workflow_id(automation_id, user_id)
        run_id = str(uuid4())
        started_at = self._now()

        base_meta = {
            "run_id": run_id,
            "trigger": trigger,
            "started_at": started_at,
            "workflow_id": workflow_id,
        }

        await self._log(
            automation_id,
            ExecutionStatus.queued.value,
            "Workflow run queued.",
            {**base_meta, "queued_at": started_at},
        )

        running_at = self._now()
        await self._log(
            automation_id,
            ExecutionStatus.running.value,
            "Workflow execution started.",
            {**base_meta, "queued_at": started_at, "running_at": running_at},
        )

        try:
            result = await self.n8n.run_workflow(workflow_id, summary.title)
            finished_at = self._now()
            updated = await self.store.record_run_success(automation_id, user_id, finished_at)

            await self._log(
                automation_id,
                ExecutionStatus.success.value,
                "Workflow completed successfully.",
                {
                    **base_meta,
                    "queued_at": started_at,
                    "running_at": running_at,
                    "finished_at": finished_at,
                    "provider": result.get("provider"),
                    "execution_id": result.get("execution_id"),
                },
            )

            return {
                "status": ExecutionStatus.success.value,
                "run_id": run_id,
                "run_count": updated.run_count,
                "last_run_at": updated.last_run_at,
                "error_count": updated.error_count,
            }
        except Exception as exc:
            finished_at = self._now()
            updated = await self.store.record_run_failure(automation_id, user_id, finished_at)

            await self._log(
                automation_id,
                ExecutionStatus.failed.value,
                f"Workflow run failed: {exc}",
                {
                    **base_meta,
                    "queued_at": started_at,
                    "running_at": running_at,
                    "finished_at": finished_at,
                    "error": str(exc),
                },
            )

            return {
                "status": ExecutionStatus.failed.value,
                "run_id": run_id,
                "run_count": updated.run_count,
                "last_run_at": updated.last_run_at,
                "error_count": updated.error_count,
                "detail": str(exc),
            }
