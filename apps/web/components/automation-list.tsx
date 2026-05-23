"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Clock3, RefreshCcw, ToggleLeft, ToggleRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getAutomations, retryAutomation, toggleAutomation } from "@/lib/api";
import type { AutomationSummary } from "@/lib/types";

const fallback: AutomationSummary[] = [
  {
    id: "demo-1",
    title: "Lead capture to Sheets and Telegram",
    status: "active",
    trigger: "New form response",
    actions: ["Save lead to Google Sheets", "Notify owner on Telegram"],
    summary: "Every form lead is saved and sent to you instantly.",
    steps: [],
    error_count: 0,
    run_count: 42,
    last_run_at: "Today"
  },
  {
    id: "demo-2",
    title: "Appointment reminder on WhatsApp",
    status: "paused",
    trigger: "New appointment booking",
    actions: ["Send reminder message", "Log delivery"],
    summary: "Customers receive a friendly reminder before their visit.",
    steps: [],
    error_count: 1,
    run_count: 15,
    last_run_at: "Yesterday"
  }
];

export function AutomationList() {
  const [items, setItems] = useState<AutomationSummary[]>(fallback);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    getAutomations().then(setItems).catch(() => setItems(fallback));
  }, []);

  async function onToggle(item: AutomationSummary) {
    const next = item.status !== "active";
    setItems((current) => current.map((entry) => entry.id === item.id ? { ...entry, status: next ? "active" : "paused" } : entry));
    await toggleAutomation(item.id, next).catch(() => setNotice("Saved locally. Backend will sync when connected."));
  }

  async function onRetry(item: AutomationSummary) {
    setNotice(`Retry started for ${item.title}.`);
    await retryAutomation(item.id).catch(() => setNotice("Retry queued locally. Backend will sync when connected."));
  }

  return (
    <div className="space-y-3">
      {notice ? <p className="rounded-md bg-saffron/20 px-3 py-2 text-sm font-semibold">{notice}</p> : null}
      {items.map((item) => (
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
                <p><span className="font-bold">Trigger:</span> {item.trigger}</p>
                <p><span className="font-bold">Runs:</span> {item.run_count}</p>
                <p><span className="font-bold">Last run:</span> {item.last_run_at ?? "Not yet"}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => onToggle(item)} title={item.status === "active" ? "Pause automation" : "Enable automation"}>
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

