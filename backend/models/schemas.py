from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AutomationStatus(str, Enum):
    active = "active"
    draft = "draft"
    failed = "failed"
    paused = "paused"


class ExecutionStatus(str, Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class StepKind(str, Enum):
    trigger = "trigger"
    action = "action"


class WorkflowStep(BaseModel):
    label: str
    app: str
    kind: StepKind


class AutomationPlan(BaseModel):
    id: str
    title: str
    status: AutomationStatus
    trigger: str
    actions: List[str]
    summary: str
    steps: List[WorkflowStep]


class AutomationSummary(AutomationPlan):
    last_run_at: Optional[str] = None
    error_count: int = 0
    run_count: int = 0


class CreateAutomationRequest(BaseModel):
    prompt: str = Field(min_length=12, max_length=1200)
    business_type: str = Field(default="local_shop", max_length=80)


class ToggleAutomationRequest(BaseModel):
    enabled: bool


class Integration(BaseModel):
    id: str
    name: str
    description: str
    status: str


class ActivityLog(BaseModel):
    automation_id: str
    status: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ActivityLogRecord(ActivityLog):
    id: str
    created_at: str
