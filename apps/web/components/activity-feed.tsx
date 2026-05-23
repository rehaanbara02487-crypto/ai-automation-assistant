import { CheckCircle2, RefreshCcw, TriangleAlert } from "lucide-react";

const logs = [
  { status: "created", message: "Lead capture automation validated and deployed.", time: "10:25 AM", icon: CheckCircle2 },
  { status: "run_success", message: "New form lead saved and owner notified.", time: "11:40 AM", icon: CheckCircle2 },
  { status: "retry_queued", message: "Appointment reminder retry queued.", time: "Yesterday", icon: RefreshCcw },
  { status: "needs_attention", message: "WhatsApp mock provider needs production connection.", time: "Yesterday", icon: TriangleAlert }
];

export function ActivityFeed() {
  return (
    <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
      <h2 className="text-xl font-black">Activity logs</h2>
      <div className="mt-4 space-y-3">
        {logs.map((log) => (
          <div key={`${log.status}-${log.time}`} className="flex gap-3 rounded-md border border-ink/10 p-3 dark:border-white/10">
            <log.icon className="mt-0.5 h-4 w-4 text-mint" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold">{log.message}</p>
              <p className="mt-1 text-xs font-bold uppercase text-ink/45 dark:text-white/45">{log.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

