"use client";

import { useCallback, useEffect, useState } from "react";
import { getAutomations } from "@/services/api";
import type { AutomationSummary } from "@/types/automation";

const AUTOMATIONS_CHANGED = "beingai:automations-changed";

export function notifyAutomationsChanged() {
  window.dispatchEvent(new CustomEvent(AUTOMATIONS_CHANGED));
}

export function useAutomations() {
  const [automations, setAutomations] = useState<AutomationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const items = await getAutomations();
      setAutomations(items);
    } catch (err) {
      setAutomations([]);
      setError(err instanceof Error ? err.message : "Could not load automations");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const onChanged = () => {
      refresh();
    };
    window.addEventListener(AUTOMATIONS_CHANGED, onChanged);
    return () => window.removeEventListener(AUTOMATIONS_CHANGED, onChanged);
  }, [refresh]);

  return { automations, loading, error, refresh };
}
