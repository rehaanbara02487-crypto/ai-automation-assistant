from typing import Dict, List

from supabase import Client, create_client

from app.config import Settings
from app.models import ActivityLog, ActivityLogRecord, AutomationStatus, AutomationSummary


class AutomationStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client | None = None
        self.memory: Dict[str, AutomationSummary] = {}
        self.workflow_ids: Dict[str, str] = {}
        if settings.supabase_url and settings.supabase_service_role_key:
            self.client = create_client(settings.supabase_url, settings.supabase_service_role_key)

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

    async def update_status(self, automation_id: str, status: AutomationStatus) -> AutomationSummary:
        if not self.client:
            item = self.memory[automation_id]
            item.status = status
            return item

        row = self.client.table("automations").update({"status": status.value}).eq("id", automation_id).execute().data[0]
        return self._from_row(row)

    async def get_workflow_id(self, automation_id: str) -> str:
        if automation_id in self.workflow_ids:
            return self.workflow_ids[automation_id]
        if not self.client:
            return f"mock-{automation_id}"
        row = self.client.table("automations").select("workflow_id").eq("id", automation_id).single().execute().data
        return row["workflow_id"]

    async def log(self, log: ActivityLog) -> None:
        if not self.client:
            return
        self.client.table("workflow_logs").insert(log.model_dump()).execute()

    async def list_logs(self, automation_id: str) -> List[ActivityLogRecord]:
        if not self.client:
            return []
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
