import { Cable, CheckCircle2, FlaskConical } from "lucide-react";

const integrations = [
  { name: "Gmail", description: "Auto reply and business inquiry workflows.", status: "available" },
  { name: "Google Sheets", description: "Save leads, orders, bookings, and summaries.", status: "available" },
  { name: "Telegram", description: "Instant owner alerts for important events.", status: "available" },
  { name: "WhatsApp", description: "Mock integration for reminders and replies.", status: "mock" },
  { name: "Forms/Webhooks", description: "Receive website forms and external events.", status: "connected" }
];

export default function IntegrationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black">Connect apps</h1>
        <p className="mt-2 text-ink/65 dark:text-white/65">Connect only the apps your automations need. Secrets stay server-side.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {integrations.map((integration) => (
          <article key={integration.name} className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
            <div className="flex items-start justify-between gap-4">
              <div className="flex gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-md bg-sky/15 text-sky">
                  <Cable className="h-5 w-5" />
                </span>
                <div>
                  <h2 className="font-black">{integration.name}</h2>
                  <p className="mt-1 text-sm text-ink/65 dark:text-white/65">{integration.description}</p>
                </div>
              </div>
              <span className="inline-flex min-w-fit items-center gap-1 rounded-md border border-ink/10 px-2 py-1 text-xs font-bold dark:border-white/10">
                {integration.status === "mock" ? <FlaskConical className="h-3 w-3 text-saffron" /> : <CheckCircle2 className="h-3 w-3 text-mint" />}
                {integration.status}
              </span>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

