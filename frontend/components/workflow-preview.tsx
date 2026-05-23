import { CheckCircle2, CircleDot, Send, Table2 } from "lucide-react";

export function WorkflowPreview() {
  const rows = [
    { icon: CircleDot, label: "Trigger", value: "New form response" },
    { icon: Table2, label: "Action 1", value: "Save lead to Google Sheets" },
    { icon: Send, label: "Action 2", value: "Notify owner on WhatsApp" },
    { icon: CheckCircle2, label: "Status", value: "Active and monitored" }
  ];

  return (
    <div className="rounded-lg border border-ink/10 bg-white p-4 shadow-soft dark:border-white/10 dark:bg-white/10">
      <div className="mb-4 rounded-md bg-[#f5f1ea] p-3 text-sm text-ink/80 dark:bg-black/30 dark:text-white/80">
        "When someone fills my form, save the lead and message me."
      </div>
      <div className="space-y-3">
        {rows.map((row) => (
          <div key={row.label} className="flex items-start gap-3 rounded-md border border-ink/10 p-3 dark:border-white/10">
            <row.icon className="mt-0.5 h-5 w-5 text-mint" />
            <div>
              <p className="text-xs font-semibold uppercase text-ink/50 dark:text-white/50">{row.label}</p>
              <p className="text-sm font-semibold">{row.value}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

