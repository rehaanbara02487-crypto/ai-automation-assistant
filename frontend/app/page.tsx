import Link from "next/link";
import {
  ArrowRight,
  BellRing,
  CheckCircle2,
  Clock3,
  FileSpreadsheet,
  Mail,
  MessageCircle,
  ShieldCheck,
  Sparkles,
  Zap
} from "lucide-react";
import { LandingNav } from "@/components/landing-nav";
import { AutomationComposer } from "@/components/automation-composer";
import { WorkflowPreview } from "@/components/workflow-preview";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const examples = [
  { icon: MessageCircle, title: "WhatsApp reminders", text: "Send appointment reminders before visits." },
  { icon: FileSpreadsheet, title: "Lead capture", text: "Save form leads to Google Sheets." },
  { icon: BellRing, title: "Owner alerts", text: "Notify you on Telegram instantly." },
  { icon: Mail, title: "Inquiry replies", text: "Auto reply to customer emails." }
];

const features = [
  { icon: Sparkles, title: "Plain-English setup", text: "Describe the work like you would explain it to a new assistant." },
  { icon: ShieldCheck, title: "Validated workflows", text: "Every plan is checked against supported apps before deployment." },
  { icon: Clock3, title: "Monitored runs", text: "See recent activity, failures, retries, and automation status." }
];

const steps = [
  "Describe the repetitive task",
  "BeingAI creates workflow steps",
  "Review the readable summary",
  "Turn it on and monitor results"
];

const testimonials = [
  "Set up lead alerts without hiring an operations person.",
  "Our class reminders became automatic in one afternoon.",
  "Finally a tool that speaks business, not workflow diagrams."
];

const faqs = [
  ["Is this a chatbot?", "No. BeingAI creates and monitors automations. The chat-like input is only the easiest way to describe work."],
  ["Do I need n8n to test locally?", "No. Local mode uses a mock n8n deployment adapter so you can test the product flow safely."],
  ["Can I use real apps later?", "Yes. The backend separates app validation, workflow deployment, logs, and retries."]
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-paper text-ink dark:bg-[#111] dark:text-white">
      <LandingNav />
      <section className="relative mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="absolute inset-0 -z-10 bg-[linear-gradient(135deg,rgba(255,181,69,0.18),transparent_34%),linear-gradient(45deg,rgba(63,140,255,0.12),transparent_42%),linear-gradient(180deg,transparent,rgba(59,191,159,0.10))]" />
        <div>
          <Badge tone="warning" className="mb-4">Built for small businesses in India</Badge>
          <h1 className="max-w-4xl text-5xl font-black leading-[1.02] sm:text-6xl lg:text-7xl">
            Your AI Employee For Repetitive Business Tasks
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-ink/70 dark:text-white/70">
            Describe your workflow in plain English and let AI automate it.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/builder">
              <Button>
                Describe Your First Automation
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary">View dashboard</Button>
            </Link>
          </div>
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
              <Card key={item.label} className="p-4 text-center">
                <item.icon className="mx-auto h-5 w-5 text-sky" />
                <p className="mt-2 text-sm font-bold">{item.label}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-ink/10 bg-white/70 py-16 backdrop-blur-xl dark:border-white/10 dark:bg-white/5">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <h2 className="text-3xl font-black">Popular automations</h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {examples.map((example) => (
              <Card key={example.title} className="p-5 transition hover:-translate-y-1 hover:shadow-soft">
                <example.icon className="h-6 w-6 text-sky" />
                <h3 className="mt-4 font-black">{example.title}</h3>
                <p className="mt-2 text-sm leading-6 text-ink/65 dark:text-white/65">{example.text}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <div className="grid gap-4 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="p-6">
              <feature.icon className="h-6 w-6 text-mint" />
              <h2 className="mt-4 text-xl font-black">{feature.title}</h2>
              <p className="mt-2 text-sm leading-6 text-ink/65 dark:text-white/65">{feature.text}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6">
        <div className="grid gap-8 rounded-lg border border-ink/10 bg-ink p-6 text-white shadow-soft dark:border-white/10 dark:bg-white/10 lg:grid-cols-[0.8fr_1.2fr]">
          <div>
            <Badge tone="info">How it works</Badge>
            <h2 className="mt-4 text-3xl font-black">From instruction to automation in minutes.</h2>
            <p className="mt-3 text-white/70">No workflow diagrams. No technical setup screens. Just a clear outcome and a monitored automation.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {steps.map((step, index) => (
              <div key={step} className="rounded-lg border border-white/10 bg-white/10 p-4">
                <p className="text-sm font-black text-saffron">0{index + 1}</p>
                <p className="mt-2 font-bold">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-8 px-4 pb-16 sm:px-6 lg:grid-cols-3">
        {testimonials.map((quote) => (
          <blockquote key={quote} className="rounded-lg border border-ink/10 bg-white/80 p-5 text-lg font-semibold shadow-soft backdrop-blur-xl dark:border-white/10 dark:bg-white/10">
            "{quote}"
            <footer className="mt-4 text-sm text-ink/50 dark:text-white/50">Early customer placeholder</footer>
          </blockquote>
        ))}
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6">
        <div className="flex flex-col justify-between gap-5 rounded-lg bg-ink p-6 text-white dark:bg-white dark:text-ink sm:flex-row sm:items-center">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-bold text-mint">
              <CheckCircle2 className="h-4 w-4" />
              Freemium SaaS
            </div>
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

      <section className="mx-auto max-w-4xl px-4 pb-16 sm:px-6">
        <h2 className="text-3xl font-black">FAQ</h2>
        <div className="mt-6 space-y-3">
          {faqs.map(([question, answer]) => (
            <Card key={question} className="p-5">
              <h3 className="font-black">{question}</h3>
              <p className="mt-2 text-sm leading-6 text-ink/65 dark:text-white/65">{answer}</p>
            </Card>
          ))}
        </div>
      </section>

      <footer className="border-t border-ink/10 py-8 dark:border-white/10">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 text-sm text-ink/55 dark:text-white/55 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p className="font-bold text-ink dark:text-white">BeingAI Assistant</p>
          <p>Local-first AI automation SaaS for small businesses.</p>
        </div>
      </footer>
    </main>
  );
}

