from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from supabase import Client, create_client

from config import Settings
from models.schemas import ActivityLog, ActivityLogRecord, AutomationStatus, AutomationSummary


class AutomationStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client | None = None
        self.memory: Dict[str, AutomationSummary] = {}
        self.workflow_ids: Dict[str, str] = {}
        self.memory_logs: Dict[str, List[ActivityLogRecord]] = {}
        if settings.supabase_url and settings.supabase_service_role_key:
            self.client = create_client(settings.supabase_url, settings.supabase_service_role_key)

    async def ensure_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> None:
        if not self.client:
            return

        payload: dict = {"id": user_id}
        if email:
            payload["email"] = email
        if full_name:
            payload["full_name"] = full_name

        self.client.table("users").upsert(payload, on_conflict="id").execute()

    async def list_automations(self, user_id: str) -> List[AutomationSummary]:
        if not self.client:
            return list(self.memory.values())

        response = self.client.table("automations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return [self._from_row(row) for row in response.data]

    async def save_automation(self, user_id: str, automation: AutomationSummary, workflow_id: str) -> AutomationSummary:
        self.workflow_ids[automation.id] = workflow_id
        if not self.client:
            self.memory[automation.id] = automation
            return automation

        await self.ensure_user(user_id)

        self.client.table("automations").insert(
            {
                "id": automation.id,
                "user_id": user_id,
                "title": automation.title,
                "status": automation.status.value if hasattr(automation.status, "value") else automation.status,
                "trigger": automation.trigger,
                "actions": automation.actions,
                "summary": automation.summary,
                "steps": [step.model_dump(mode="json") for step in automation.steps],
                "workflow_id": workflow_id,
                "error_count": automation.error_count,
                "run_count": automation.run_count,
            }
        ).execute()
        return automation

    async def update_status(self, automation_id: str, status: AutomationStatus, user_id: str) -> AutomationSummary:
        if not self.client:
            item = self.memory.get(automation_id)
            if not item:
                raise KeyError(automation_id)
            item.status = status
            return item

        response = (
            self.client.table("automations")
            .update({"status": status.value})
            .eq("id", automation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not response.data:
            raise KeyError(automation_id)
        return self._from_row(response.data[0])

    async def get_workflow_id(self, automation_id: str, user_id: str) -> str:
        if automation_id in self.workflow_ids:
            if not self.client or automation_id in self.memory:
                return self.workflow_ids[automation_id]

        if not self.client:
            if automation_id not in self.memory:
                raise KeyError(automation_id)
            return self.workflow_ids.get(automation_id, f"mock-{automation_id}")

        response = (
            self.client.table("automations")
            .select("workflow_id")
            .eq("id", automation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not response.data:
            raise KeyError(automation_id)
        return response.data[0]["workflow_id"]

    async def automation_owned_by(self, automation_id: str, user_id: str) -> bool:
        if not self.client:
            return automation_id in self.memory

        response = (
            self.client.table("automations")
            .select("id")
            .eq("id", automation_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    async def get_automation(self, automation_id: str, user_id: str) -> AutomationSummary:
        if not self.client:
            item = self.memory.get(automation_id)
            if not item:
                raise KeyError(automation_id)
            return item

        response = (
            self.client.table("automations")
            .select("*")
            .eq("id", automation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not response.data:
            raise KeyError(automation_id)
        return self._from_row(response.data[0])

    async def record_run_success(self, automation_id: str, user_id: str, finished_at: str) -> AutomationSummary:
        if not self.client:
            item = self.memory.get(automation_id)
            if not item:
                raise KeyError(automation_id)
            item.run_count += 1
            item.last_run_at = finished_at
            if item.status == AutomationStatus.failed:
                item.status = AutomationStatus.active
            return item

        current = await self.get_automation(automation_id, user_id)
        response = (
            self.client.table("automations")
            .update(
                {
                    "run_count": current.run_count + 1,
                    "last_run_at": finished_at,
                    "status": AutomationStatus.active.value,
                    "updated_at": finished_at,
                }
            )
            .eq("id", automation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not response.data:
            raise KeyError(automation_id)
        return self._from_row(response.data[0])

    async def record_run_failure(self, automation_id: str, user_id: str, finished_at: str) -> AutomationSummary:
        if not self.client:
            item = self.memory.get(automation_id)
            if not item:
                raise KeyError(automation_id)
            item.error_count += 1
            item.last_run_at = finished_at
            item.status = AutomationStatus.failed
            return item

        current = await self.get_automation(automation_id, user_id)
        response = (
            self.client.table("automations")
            .update(
                {
                    "error_count": current.error_count + 1,
                    "last_run_at": finished_at,
                    "status": AutomationStatus.failed.value,
                    "updated_at": finished_at,
                }
            )
            .eq("id", automation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if not response.data:
            raise KeyError(automation_id)
        return self._from_row(response.data[0])

    async def log(self, log: ActivityLog) -> None:
        record = ActivityLogRecord(
            id=str(uuid4()),
            automation_id=log.automation_id,
            status=log.status,
            message=log.message,
            metadata=log.metadata,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        if not self.client:
            logs = self.memory_logs.setdefault(log.automation_id, [])
            logs.insert(0, record)
            self.memory_logs[log.automation_id] = logs[:50]
            return

        self.client.table("workflow_logs").insert(
            {
                "automation_id": log.automation_id,
                "status": log.status,
                "message": log.message,
                "metadata": log.metadata,
            }
        ).execute()

    async def list_logs(self, automation_id: str) -> List[ActivityLogRecord]:
        if not self.client:
            return self.memory_logs.get(automation_id, [])[:25]
        response = (
            self.client.table("workflow_logs")
            .select("*")
            .eq("automation_id", automation_id)
            .order("created_at", desc=True)
            .limit(25)
            .execute()
        )
        return [ActivityLogRecord(**row) for row in response.data]

    def _from_row(self, row: dict) -> AutomationSummary:
        return AutomationSummary(
            id=row["id"],
            title=row["title"],
            status=row["status"],
            trigger=row["trigger"],
            actions=row["actions"],
            summary=row["summary"],
            steps=row["steps"],
            last_run_at=row.get("last_run_at"),
            error_count=row.get("error_count", 0),
            run_count=row.get("run_count", 0),
        )
