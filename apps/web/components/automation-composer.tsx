"use client";

import { useState } from "react";
import { ArrowRight, Loader2, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { createAutomation } from "@/lib/api";
import type { AutomationPlan } from "@/lib/types";

const examples = [
  "Send appointment reminders automatically on WhatsApp.",
  "Save new website leads into Google Sheets and tell me on Telegram.",
  "Send daily sales summary every evening.",
  "Auto reply to new business inquiries from Gmail."
];

export function AutomationComposer({ compact = false }: { compact?: boolean }) {
  const [prompt, setPrompt] = useState(examples[1]);
  const [businessType, setBusinessType] = useState("local_shop");
  const [plan, setPlan] = useState<AutomationPlan | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    try {
      const result = await createAutomation(prompt, businessType);
      setPlan(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create automation");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-lg border border-ink/10 bg-white p-4 shadow-soft dark:border-white/10 dark:bg-white/10 sm:p-5">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-ink/70 dark:text-white/70">
        <Sparkles className="h-4 w-4 text-saffron" />
        Describe the task once. BeingAI builds the workflow.
      </div>
      <textarea
        value={prompt}
        onChange={(event) => setPrompt(event.target.value)}
        rows={compact ? 4 : 5}
        className="w-full resize-none rounded-md border border-ink/10 bg-[#fbfaf7] p-4 text-base outline-none ring-sky transition focus:ring-2 dark:border-white/10 dark:bg-black/30"
        placeholder="Example: When a customer submits my form, send them a WhatsApp message and save the lead."
      />
      <div className="mt-3 flex flex-col gap-3 sm:flex-row">
        <select
          value={businessType}
          onChange={(event) => setBusinessType(event.target.value)}
          className="h-11 rounded-md border border-ink/10 bg-white px-3 text-sm dark:border-white/10 dark:bg-black/30"
          aria-label="Business type"
        >
          <option value="local_shop">Local shop</option>
          <option value="gym">Gym</option>
          <option value="freelancer">Freelancer</option>
          <option value="agency">Agency</option>
          <option value="coach">Coach</option>
          <option value="creator">Creator</option>
        </select>
        <Button onClick={submit} disabled={loading || prompt.trim().length < 12} className="sm:ml-auto">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
          Create automation
        </Button>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {examples.map((example) => (
          <button
            key={example}
            onClick={() => setPrompt(example)}
            className="rounded-md border border-ink/10 px-3 py-2 text-left text-xs font-medium text-ink/70 hover:bg-ink/5 dark:border-white/10 dark:text-white/70 dark:hover:bg-white/10"
          >
            {example}
          </button>
        ))}
      </div>
      {error ? <p className="mt-3 text-sm font-medium text-rose">{error}</p> : null}
      {plan ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-5 rounded-md border border-mint/30 bg-mint/10 p-4">
          <p className="text-sm font-bold">{plan.title}</p>
          <p className="mt-1 text-sm text-ink/70 dark:text-white/70">{plan.summary}</p>
          <div className="mt-3 space-y-2">
            <p className="text-sm"><span className="font-semibold">Trigger:</span> {plan.trigger}</p>
            {plan.actions.map((action, index) => (
              <p key={action} className="text-sm"><span className="font-semibold">Action {index + 1}:</span> {action}</p>
            ))}
            <p className="text-sm"><span className="font-semibold">Status:</span> {plan.status}</p>
          </div>
        </motion.div>
      ) : null}
    </div>
  );
}

