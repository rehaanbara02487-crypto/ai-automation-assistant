from typing import Any, Dict

import httpx

from app.config import Settings
from app.models import AutomationPlan


class N8NClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def deploy(self, plan: AutomationPlan) -> Dict[str, Any]:
        workflow = self._to_internal_workflow(plan)

        if not self.settings.n8n_enabled:
            return {
                "provider": "mock-n8n",
                "workflow_id": f"mock-{plan.id}",
                "status": "active",
                "workflow": workflow,
            }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.settings.n8n_base_url.rstrip('/')}/api/v1/workflows",
                headers={"X-N8N-API-KEY": self.settings.n8n_api_key},
                json=workflow,
            )
            response.raise_for_status()
            payload = response.json()
            return {
                "provider": "n8n",
                "workflow_id": str(payload.get("id")),
                "status": "active",
            }

    async def activate(self, workflow_id: str, enabled: bool) -> Dict[str, str]:
        if workflow_id.startswith("mock-") or not self.settings.n8n_enabled:
            return {"workflow_id": workflow_id, "status": "active" if enabled else "paused"}

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.patch(
                f"{self.settings.n8n_base_url.rstrip('/')}/api/v1/workflows/{workflow_id}",
                headers={"X-N8N-API-KEY": self.settings.n8n_api_key},
                json={"active": enabled},
            )
            response.raise_for_status()
            return {"workflow_id": workflow_id, "status": "active" if enabled else "paused"}

    def _to_internal_workflow(self, plan: AutomationPlan) -> Dict[str, Any]:
        nodes = [
            {
                "name": step.label,
                "type": f"beingai.{step.app}.{step.kind}",
                "parameters": {"label": step.label},
                "position": [250 * index, 120],
            }
            for index, step in enumerate(plan.steps)
        ]

        connections = {
            nodes[index]["name"]: {"main": [[{"node": nodes[index + 1]["name"], "type": "main", "index": 0}]]}
            for index in range(len(nodes) - 1)
        }

        return {
            "name": plan.title,
            "active": True,
            "nodes": nodes,
            "connections": connections,
            "settings": {"executionTimeout": 120},
        }

