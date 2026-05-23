"use client";

import type { LucideIcon } from "lucide-react";
import { Activity, AlertTriangle, Bot } from "lucide-react";
import { computeDashboardMetrics } from "@/lib/dashboard-metrics";
import type { AutomationSummary } from "@/types/automation";
import { Skeleton } from "@/components/ui/skeleton";

type DashboardMetricsProps = {
  automations: AutomationSummary[];
  loading: boolean;
};

export function DashboardMetrics({ automations, loading }: DashboardMetricsProps) {
  const metrics = computeDashboardMetrics(automations);

  const cards: { label: string; value: number; icon: LucideIcon }[] = [
    { label: "Active automations", value: metrics.activeCount, icon: Bot },
    { label: "Total runs", value: metrics.totalRuns, icon: Activity },
    { label: "Needs attention", value: metrics.needsAttention, icon: AlertTriangle }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {cards.map((card) => (
        <div key={card.label} className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
          <card.icon className="h-5 w-5 text-sky" />
          {loading ? (
            <Skeleton className="mt-4 h-9 w-16" />
          ) : (
            <p className="mt-4 text-3xl font-black">{card.value}</p>
          )}
          <p className="text-sm font-semibold text-ink/55 dark:text-white/55">{card.label}</p>
        </div>
      ))}
    </div>
  );
}
