import { ShieldCheck } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-black">Settings</h1>
        <p className="mt-2 text-ink/65 dark:text-white/65">Workspace preferences for safe automation.</p>
      </div>
      <section className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
        <div className="flex items-start gap-3">
          <ShieldCheck className="h-5 w-5 text-mint" />
          <div>
            <h2 className="font-black">Reliability defaults</h2>
            <p className="mt-1 text-sm text-ink/65 dark:text-white/65">Every automation is validated before deployment, monitored after each run, and retry-ready if an app fails.</p>
          </div>
        </div>
        <div className="mt-5 grid gap-4">
          {["Email me when an automation fails", "Pause workflows after repeated failures", "Require approval before sending customer messages"].map((label) => (
            <label key={label} className="flex items-center justify-between rounded-md border border-ink/10 p-3 text-sm font-semibold dark:border-white/10">
              {label}
              <input type="checkbox" defaultChecked className="h-4 w-4 accent-ink dark:accent-white" />
            </label>
          ))}
        </div>
      </section>
    </div>
  );
}

