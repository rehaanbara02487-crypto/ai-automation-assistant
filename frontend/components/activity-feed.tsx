"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, RefreshCcw, TriangleAlert } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { formatLogTime } from "@/lib/format-log-time";
import { getAutomationLogs } from "@/services/api";
import type { ActivityLogRecord, AutomationSummary } from "@/types/automation";
import { Skeleton } from "@/components/ui/skeleton";

type ActivityFeedProps = {
  automations: AutomationSummary[];
  loading: boolean;
};

type FeedEntry = ActivityLogRecord & {
  automationTitle: string;
};

function iconForStatus(status: string): LucideIcon {
  if (status.includes("retry")) {
    return RefreshCcw;
  }
  if (status.includes("fail") || status.includes("attention") || status.includes("error")) {
    return TriangleAlert;
  }
  return CheckCircle2;
}

export function ActivityFeed({ automations, loading }: ActivityFeedProps) {
  const [entries, setEntries] = useState<FeedEntry[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (automations.length === 0) {
      setEntries([]);
      return;
    }

    let cancelled = false;

    async function loadLogs() {
      setLogsLoading(true);
      try {
        const results = await Promise.all(
          automations.map(async (automation) => {
            const logs = await getAutomationLogs(automation.id).catch(() => [] as ActivityLogRecord[]);
            return logs.map((log) => ({ ...log, automationTitle: automation.title }));
          })
        );

        if (cancelled) {
          return;
        }

        const merged = results
          .flat()
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 25);

        setEntries(merged);
      } finally {
        if (!cancelled) {
          setLogsLoading(false);
        }
      }
    }

    loadLogs();
    return () => {
      cancelled = true;
    };
  }, [automations, loading]);

  const showSkeleton = loading || logsLoading;

  return (
    <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
      <h2 className="text-xl font-black">Activity logs</h2>
      <div className="mt-4 space-y-3">
        {showSkeleton ? (
          <>
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </>
        ) : null}

        {!showSkeleton && entries.length === 0 ? (
          <p className="rounded-md border border-dashed border-ink/15 px-4 py-6 text-center text-sm text-ink/60 dark:border-white/15 dark:text-white/60">
            No activity yet. Create an automation and actions will appear here.
          </p>
        ) : null}

        {!showSkeleton
          ? entries.map((log) => {
              const Icon = iconForStatus(log.status);
              return (
                <div key={log.id} className="flex gap-3 rounded-md border border-ink/10 p-3 dark:border-white/10">
                  <Icon className="mt-0.5 h-4 w-4 shrink-0 text-mint" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold">{log.message}</p>
                    <p className="mt-1 text-xs font-bold uppercase text-ink/45 dark:text-white/45">
                      {log.automationTitle} · {formatLogTime(log.created_at)}
                    </p>
                  </div>
                </div>
              );
            })
          : null}
      </div>
    </div>
  );
}
