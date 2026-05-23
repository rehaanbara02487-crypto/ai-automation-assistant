import Link from "next/link";
import { Activity, AlertTriangle, Bot, PlusCircle } from "lucide-react";
import { ActivityFeed } from "@/components/activity-feed";
import { AutomationList } from "@/components/automation-list";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-black">Dashboard</h1>
          <p className="mt-2 text-ink/65 dark:text-white/65">See what your AI operations assistant is handling today.</p>
        </div>
        <Link href="/builder">
          <Button><PlusCircle className="h-4 w-4" /> New automation</Button>
        </Link>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[
          { label: "Active automations", value: "2", icon: Bot },
          { label: "Runs this month", value: "57", icon: Activity },
          { label: "Needs attention", value: "1", icon: AlertTriangle }
        ].map((metric) => (
          <div key={metric.label} className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
            <metric.icon className="h-5 w-5 text-sky" />
            <p className="mt-4 text-3xl font-black">{metric.value}</p>
            <p className="text-sm font-semibold text-ink/55 dark:text-white/55">{metric.label}</p>
          </div>
        ))}
      </div>
      <section>
        <h2 className="mb-4 text-xl font-black">Your automations</h2>
        <AutomationList />
      </section>
      <ActivityFeed />
    </div>
  );
}
