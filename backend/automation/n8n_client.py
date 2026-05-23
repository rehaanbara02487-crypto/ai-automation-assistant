from typing import Any, Dict
from uuid import uuid4

import httpx

from config import Settings
from models.schemas import AutomationPlan


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

    async def run_workflow(self, workflow_id: str, workflow_name: str = "") -> Dict[str, Any]:
        if workflow_id.startswith("mock-") or not self.settings.n8n_enabled:
            return {
                "provider": "mock-n8n",
                "execution_id": f"mock-run-{uuid4()}",
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
            }

        async with httpx.AsyncClient(timeout=30) as client:
            base = self.settings.n8n_base_url.rstrip("/")
            headers = {"X-N8N-API-KEY": self.settings.n8n_api_key}

            if self.settings.n8n_webhook_base_url:
                webhook_url = f"{self.settings.n8n_webhook_base_url.rstrip('/')}/{workflow_id}"
                response = await client.post(
                    webhook_url,
                    json={"source": "beingai-assistant", "workflow_id": workflow_id, "workflow_name": workflow_name},
                )
                response.raise_for_status()
                return {
                    "provider": "n8n-webhook",
                    "execution_id": response.headers.get("x-n8n-execution-id", f"webhook-{uuid4()}"),
                    "status": "success",
                    "workflow_id": workflow_id,
                }

            response = await client.post(
                f"{base}/api/v1/workflows/{workflow_id}/run",
                headers=headers,
                json={},
            )
            if response.status_code == 404:
                raise RuntimeError("n8n run endpoint unavailable. Set N8N_WEBHOOK_BASE_URL for webhook triggers.")

            response.raise_for_status()
            payload = response.json()
            return {
                "provider": "n8n",
                "execution_id": str(payload.get("executionId") or payload.get("id") or uuid4()),
                "status": "success",
                "workflow_id": workflow_id,
            }

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
