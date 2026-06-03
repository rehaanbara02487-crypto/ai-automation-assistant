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


class CreateAutomationRecordRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    trigger_type: str = Field(default="manual", max_length=120)
    status: AutomationStatus = AutomationStatus.draft
    workflow_json: Dict[str, Any] = Field(default_factory=dict)


class UpdateAutomationRecordRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=4000)
    trigger_type: Optional[str] = Field(default=None, max_length=120)
    status: Optional[AutomationStatus] = None
    workflow_json: Optional[Dict[str, Any]] = None


class CreateAutomationRequest(BaseModel):
    prompt: str = Field(min_length=12, max_length=1200)
    business_type: str = Field(default="local_shop", max_length=80)


class ToggleAutomationRequest(BaseModel):
    enabled: bool


class SaveAutomationRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    trigger_type: str = Field(min_length=2, max_length=120)
    action_type: str = Field(min_length=2, max_length=120)
    status: str = Field(default="queued", max_length=50)


class SaveAutomationResponse(BaseModel):
    id: str
    user_id: str
    prompt: str
    trigger_type: str
    action_type: str
    status: str
    created_at: str


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
