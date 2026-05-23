import Link from "next/link";
import { ArrowRight, Clock3, ShieldCheck, Zap } from "lucide-react";
import { LandingNav } from "@/components/landing-nav";
import { AutomationComposer } from "@/components/automation-composer";
import { WorkflowPreview } from "@/components/workflow-preview";
import { Button } from "@/components/ui/button";

const examples = [
  "Send appointment reminders on WhatsApp",
  "Save leads from forms into Google Sheets",
  "Send daily sales summary every evening",
  "Notify me on Telegram when a form is submitted",
  "Auto reply to new business inquiries"
];

const testimonials = [
  "Set up lead alerts without hiring an operations person.",
  "Our class reminders became automatic in one afternoon.",
  "Finally a tool that speaks business, not workflow diagrams."
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-paper text-ink dark:bg-[#111] dark:text-white">
      <LandingNav />
      <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <p className="mb-4 inline-flex rounded-md bg-saffron/20 px-3 py-2 text-sm font-bold text-ink dark:text-white">
            Built for small businesses in India
          </p>
          <h1 className="max-w-4xl text-5xl font-black leading-[1.02] sm:text-6xl lg:text-7xl">
            Your AI Employee For Repetitive Business Tasks
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-ink/70 dark:text-white/70">
            Describe your workflow in plain English and let AI automate it.
          </p>
          <div className="mt-8 max-w-2xl">
            <AutomationComposer compact />
          </div>
        </div>
        <div className="space-y-4">
          <WorkflowPreview />
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: Zap, label: "Fast setup" },
              { icon: ShieldCheck, label: "Validated" },
              { icon: Clock3, label: "Monitored" }
            ].map((item) => (
              <div key={item.label} className="rounded-lg border border-ink/10 bg-white p-4 text-center shadow-soft dark:border-white/10 dark:bg-white/10">
                <item.icon className="mx-auto h-5 w-5 text-sky" />
                <p className="mt-2 text-sm font-bold">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="border-y border-ink/10 bg-white py-16 dark:border-white/10 dark:bg-white/5">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <h2 className="text-3xl font-black">Popular automations</h2>
          <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {examples.map((example) => (
              <div key={example} className="rounded-lg border border-ink/10 p-4 text-sm font-semibold dark:border-white/10">
                {example}
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="mx-auto grid max-w-7xl gap-8 px-4 py-16 sm:px-6 lg:grid-cols-3">
        {testimonials.map((quote) => (
          <blockquote key={quote} className="rounded-lg border border-ink/10 bg-white p-5 text-lg font-semibold shadow-soft dark:border-white/10 dark:bg-white/10">
            "{quote}"
            <footer className="mt-4 text-sm text-ink/50 dark:text-white/50">Early customer placeholder</footer>
          </blockquote>
        ))}
      </section>
      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6">
        <div className="flex flex-col justify-between gap-5 rounded-lg bg-ink p-6 text-white dark:bg-white dark:text-ink sm:flex-row sm:items-center">
          <div>
            <h2 className="text-2xl font-black">Start free, upgrade when automations save real time.</h2>
            <p className="mt-2 text-white/70 dark:text-ink/70">Free plan includes limited automations. Pro is ready for growing teams.</p>
          </div>
          <Link href="/pricing">
            <Button variant="secondary">
              View pricing
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>
    </main>
  );
}

