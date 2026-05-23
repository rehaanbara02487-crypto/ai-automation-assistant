import { IntegrationsList } from "@/components/integrations-list";

export default function IntegrationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-black">Connect apps</h1>
        <p className="mt-2 text-ink/65 dark:text-white/65">Connect only the apps your automations need. Secrets stay server-side.</p>
      </div>
      <IntegrationsList />
    </div>
  );
}
