import json
from uuid import uuid4

from openai import AsyncOpenAI

from app.automation_catalog import infer_capabilities
from app.config import Settings
from app.models import AutomationPlan, AutomationStatus, StepKind, WorkflowStep
from app.validator import validate_plan


SYSTEM_PROMPT = """
You are BeingAI Assistant, an automation planner for small businesses in India.
Return simple, reliable automation plans only.
Never invent apps outside the supported catalog.
Never expose n8n JSON.
Use beginner-friendly wording.
"""


class AIOrchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def create_plan(self, prompt: str, business_type: str) -> AutomationPlan:
        if not self.client:
            return validate_plan(self._fallback_plan(prompt, business_type))

        capabilities = infer_capabilities(prompt)
        catalog_context = [
            {
                "key": capability.key,
                "app": capability.app,
                "label": capability.label,
                "kind": capability.kind,
            }
            for capability in capabilities
        ]

        response = await self.client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "business_type": business_type,
                            "request": prompt,
                            "available_capabilities": catalog_context,
                            "required_shape": {
                                "title": "short automation name",
                                "trigger": "one trigger label",
                                "actions": ["plain action labels"],
                                "summary": "one sentence user-facing summary",
                            },
                        }
                    ),
                },
            ],
            text={"format": {"type": "json_object"}},
        )

        payload = json.loads(response.output_text)
        return validate_plan(self._plan_from_payload(payload, capabilities))

    def _fallback_plan(self, prompt: str, business_type: str) -> AutomationPlan:
        capabilities = infer_capabilities(prompt)
        trigger = next(item for item in capabilities if item.kind == "trigger")
        actions = [item for item in capabilities if item.kind == "action"]
        title = self._title_for(prompt, business_type)

        return AutomationPlan(
            id=str(uuid4()),
            title=title,
            status=AutomationStatus.active,
            trigger=trigger.label,
            actions=[action.label for action in actions],
            summary=f"BeingAI will start from {trigger.label.lower()} and complete {len(actions)} action{'s' if len(actions) != 1 else ''}.",
            steps=[
                WorkflowStep(label=trigger.label, app=trigger.app, kind=StepKind.trigger),
                *[WorkflowStep(label=action.label, app=action.app, kind=StepKind.action) for action in actions],
            ],
        )

    def _plan_from_payload(self, payload: dict, capabilities) -> AutomationPlan:
        by_label = {capability.label: capability for capability in capabilities}
        trigger_label = payload.get("trigger") or next(item.label for item in capabilities if item.kind == "trigger")
        action_labels = payload.get("actions") or [item.label for item in capabilities if item.kind == "action"]

        trigger = by_label.get(trigger_label) or next(item for item in capabilities if item.kind == "trigger")
        action_caps = [by_label[label] for label in action_labels if label in by_label and by_label[label].kind == "action"]

        if not action_caps:
            action_caps = [item for item in capabilities if item.kind == "action"]

        return AutomationPlan(
            id=str(uuid4()),
            title=payload.get("title") or "New business automation",
            status=AutomationStatus.active,
            trigger=trigger.label,
            actions=[action.label for action in action_caps],
            summary=payload.get("summary") or "BeingAI created a validated automation for this task.",
            steps=[
                WorkflowStep(label=trigger.label, app=trigger.app, kind=StepKind.trigger),
                *[WorkflowStep(label=action.label, app=action.app, kind=StepKind.action) for action in action_caps],
            ],
        )

    def _title_for(self, prompt: str, business_type: str) -> str:
        normalized = " ".join(prompt.strip().split())
        if len(normalized) <= 52:
            return normalized.rstrip(".")
        label = business_type.replace("_", " ").title()
        return f"{label} automation"

