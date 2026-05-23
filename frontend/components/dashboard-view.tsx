"use client";

import Link from "next/link";
import { PlusCircle } from "lucide-react";
import { ActivityFeed } from "@/components/activity-feed";
import { AutomationList } from "@/components/automation-list";
import { DashboardMetrics } from "@/components/dashboard-metrics";
import { Button } from "@/components/ui/button";
import { useAutomations } from "@/hooks/use-automations";

export function DashboardView() {
  const { automations, loading, error, refresh } = useAutomations();

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-black">Dashboard</h1>
          <p className="mt-2 text-ink/65 dark:text-white/65">See what your AI operations assistant is handling today.</p>
        </div>
        <Link href="/builder">
          <Button>
            <PlusCircle className="h-4 w-4" /> New automation
          </Button>
        </Link>
      </div>

      <DashboardMetrics automations={automations} loading={loading} />

      {error ? <p className="rounded-md bg-rose/15 px-3 py-2 text-sm font-semibold text-rose">{error}</p> : null}

      <section>
        <h2 className="mb-4 text-xl font-black">Your automations</h2>
        <AutomationList automations={automations} loading={loading} onRefresh={refresh} />
      </section>

      <ActivityFeed automations={automations} loading={loading} />
    </div>
  );
}
