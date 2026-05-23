export type StepKind = "trigger" | "action";

export type WorkflowStep = {
  label: string;
  app: string;
  kind: StepKind;
};

export type AutomationPlan = {
  id: string;
  title: string;
  status: "active" | "draft" | "failed" | "paused";
  trigger: string;
  actions: string[];
  summary: string;
  steps: WorkflowStep[];
};

export type AutomationSummary = AutomationPlan & {
  last_run_at?: string;
  error_count: number;
  run_count: number;
};

export type Integration = {
  id: string;
  name: string;
  description: string;
  status: "connected" | "available" | "mock";
};

export type ActivityLogRecord = {
  id: string;
  automation_id: string;
  status: string;
  message: string;
  created_at: string;
  metadata?: Record<string, unknown>;
};

