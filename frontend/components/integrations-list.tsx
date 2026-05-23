"use client";

import { useEffect, useState } from "react";
import { Cable, CheckCircle2, FlaskConical } from "lucide-react";
import { getIntegrations } from "@/services/api";
import type { Integration } from "@/types/automation";
import { Skeleton } from "@/components/ui/skeleton";

export function IntegrationsList() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getIntegrations()
      .then(setIntegrations)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load integrations"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
      </div>
    );
  }

  if (error) {
    return <p className="rounded-md bg-rose/15 px-3 py-2 text-sm font-semibold text-rose">{error}</p>;
  }

  if (integrations.length === 0) {
    return (
      <p className="rounded-md border border-dashed border-ink/15 px-4 py-6 text-center text-sm text-ink/60 dark:border-white/15 dark:text-white/60">
        No integrations available yet.
      </p>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {integrations.map((integration) => (
        <article key={integration.id} className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-white/10">
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
              {integration.status === "mock" ? (
                <FlaskConical className="h-3 w-3 text-saffron" />
              ) : (
                <CheckCircle2 className="h-3 w-3 text-mint" />
              )}
              {integration.status}
            </span>
          </div>
        </article>
      ))}
    </div>
  );
}
