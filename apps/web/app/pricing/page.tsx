import Link from "next/link";
import { CheckCircle2 } from "lucide-react";
import { LandingNav } from "@/components/landing-nav";
import { Button } from "@/components/ui/button";

const plans = [
  { name: "Free", price: "Rs 0", features: ["2 active automations", "50 runs per month", "Mock WhatsApp support"] },
  { name: "Pro", price: "Rs 999/mo", features: ["20 active automations", "2,000 runs per month", "Priority retries", "Stripe-ready billing"] },
  { name: "Team", price: "Soon", features: ["Shared workspace", "Approval controls", "Advanced monitoring"] }
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-paper text-ink dark:bg-[#111] dark:text-white">
      <LandingNav />
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <h1 className="text-4xl font-black sm:text-5xl">Simple pricing for small teams</h1>
        <p className="mt-4 max-w-2xl text-ink/65 dark:text-white/65">Start free and upgrade only when BeingAI is saving real hours.</p>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {plans.map((plan) => (
            <article key={plan.name} className="rounded-lg border border-ink/10 bg-white p-6 shadow-soft dark:border-white/10 dark:bg-white/10">
              <h2 className="text-xl font-black">{plan.name}</h2>
              <p className="mt-3 text-3xl font-black">{plan.price}</p>
              <div className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <p key={feature} className="flex items-center gap-2 text-sm font-semibold">
                    <CheckCircle2 className="h-4 w-4 text-mint" />
                    {feature}
                  </p>
                ))}
              </div>
              <Link href="/sign-up">
                <Button className="mt-6 w-full" variant={plan.name === "Pro" ? "primary" : "secondary"}>
                  Choose {plan.name}
                </Button>
              </Link>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

