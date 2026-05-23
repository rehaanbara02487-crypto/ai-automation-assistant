"use client";

import { useState } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, Clock3, PlusCircle, RefreshCcw, ToggleLeft, ToggleRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { notifyAutomationsChanged } from "@/hooks/use-automations";
import { retryAutomation, toggleAutomation } from "@/services/api";
import type { AutomationSummary } from "@/types/automation";

type AutomationListProps = {
  automations: AutomationSummary[];
  loading: boolean;
  onRefresh?: () => Promise<void>;
};

export function AutomationList({ automations, loading, onRefresh }: AutomationListProps) {
  const [notice, setNotice] = useState("");

  async function onToggle(item: AutomationSummary) {
    const next = item.status !== "active";
    setNotice("");
    try {
      await toggleAutomation(item.id, next);
      await onRefresh?.();
      notifyAutomationsChanged();
    } catch {
      setNotice("Could not update automation status. Try again.");
    }
  }

  async function onRetry(item: AutomationSummary) {
    setNotice("");
    try {
      await retryAutomation(item.id);
      setNotice(`Retry queued for ${item.title}.`);
      await onRefresh?.();
      notifyAutomationsChanged();
    } catch {
      setNotice("Could not queue retry. Try again.");
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (automations.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-ink/15 bg-white/50 p-8 text-center dark:border-white/15 dark:bg-white/5">
        <p className="font-bold">No automations yet</p>
        <p className="mt-2 text-sm text-ink/65 dark:text-white/65">Describe your first task and BeingAI will build it for you.</p>
        <Link href="/builder" className="mt-4 inline-block">
          <Button>
            <PlusCircle className="h-4 w-4" />
            Create automation
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {notice ? <p className="rounded-md bg-saffron/20 px-3 py-2 text-sm font-semibold">{notice}</p> : null}
      {automations.map((item) => (
        <article key={item.id} className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-lg font-black">{item.title}</h3>
                <span className="inline-flex items-center gap-1 rounded-md bg-mint/15 px-2 py-1 text-xs font-bold text-mint">
                  {item.status === "active" ? <CheckCircle2 className="h-3 w-3" /> : <Clock3 className="h-3 w-3" />}
                  {item.status}
                </span>
                {item.error_count > 0 ? (
                  <span className="inline-flex items-center gap-1 rounded-md bg-rose/15 px-2 py-1 text-xs font-bold text-rose">
                    <AlertTriangle className="h-3 w-3" />
                    {item.error_count} error
                  </span>
                ) : null}
              </div>
              <p className="mt-2 text-sm text-ink/65 dark:text-white/65">{item.summary}</p>
              <div className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
                <p>
                  <span className="font-bold">Trigger:</span> {item.trigger}
                </p>
                <p>
                  <span className="font-bold">Runs:</span> {item.run_count}
                </p>
                <p>
                  <span className="font-bold">Last run:</span> {item.last_run_at ?? "Not yet"}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={() => onToggle(item)}
                title={item.status === "active" ? "Pause automation" : "Enable automation"}
              >
                {item.status === "active" ? <ToggleRight className="h-4 w-4" /> : <ToggleLeft className="h-4 w-4" />}
              </Button>
              <Button variant="secondary" onClick={() => onRetry(item)} title="Retry failed workflow">
                <RefreshCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
