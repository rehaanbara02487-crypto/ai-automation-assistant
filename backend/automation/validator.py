from typing import List

from automation.catalog import CAPABILITIES, SUPPORTED_APPS
from models.schemas import AutomationPlan, StepKind


class AutomationValidationError(ValueError):
    pass


def validate_plan(plan: AutomationPlan) -> AutomationPlan:
    if not plan.title.strip():
        raise AutomationValidationError("Please describe the automation goal a little more clearly.")

    triggers = [step for step in plan.steps if step.kind == StepKind.trigger]
    actions = [step for step in plan.steps if step.kind == StepKind.action]

    if len(triggers) != 1:
        raise AutomationValidationError("Each automation needs exactly one starting event.")

    if not actions:
        raise AutomationValidationError("Each automation needs at least one action.")

    unsupported = [step.app for step in plan.steps if step.app not in SUPPORTED_APPS]
    if unsupported:
        raise AutomationValidationError(f"{unsupported[0]} is not supported in the MVP yet.")

    allowed_labels = {capability.label for capability in CAPABILITIES.values()}
    hallucinated: List[str] = [step.label for step in plan.steps if step.label not in allowed_labels]
    if hallucinated:
        raise AutomationValidationError("This request includes an action BeingAI cannot safely automate yet.")

    return plan
