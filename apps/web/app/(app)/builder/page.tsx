import { AutomationComposer } from "@/components/automation-composer";

export default function BuilderPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-black">Create automation</h1>
        <p className="mt-2 text-ink/65 dark:text-white/65">Tell BeingAI what repetitive task you want handled. Keep it natural.</p>
      </div>
      <AutomationComposer />
    </div>
  );
}

