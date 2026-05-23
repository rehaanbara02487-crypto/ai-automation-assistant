import type { AutomationSummary } from "@/types/automation";

export type DashboardMetrics = {
  activeCount: number;
  totalRuns: number;
  needsAttention: number;
};

export function computeDashboardMetrics(automations: AutomationSummary[]): DashboardMetrics {
  return {
    activeCount: automations.filter((item) => item.status === "active").length,
    totalRuns: automations.reduce((sum, item) => sum + item.run_count, 0),
    needsAttention: automations.filter((item) => item.error_count > 0 || item.status === "failed").length
  };
}
