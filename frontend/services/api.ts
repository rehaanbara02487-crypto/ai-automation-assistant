import type { AutomationPlan, AutomationSummary, Integration } from "@/types/automation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "Something went wrong");
  }

  return response.json();
}

export function createAutomation(input: string, businessType: string) {
  return request<AutomationPlan>("/api/automations/create", {
    method: "POST",
    body: JSON.stringify({ prompt: input, business_type: businessType })
  });
}

export function getAutomations() {
  return request<AutomationSummary[]>("/api/automations");
}

export function getIntegrations() {
  return request<Integration[]>("/api/integrations");
}

export function toggleAutomation(id: string, enabled: boolean) {
  return request<AutomationSummary>(`/api/automations/${id}/toggle`, {
    method: "POST",
    body: JSON.stringify({ enabled })
  });
}

export function retryAutomation(id: string) {
  return request<{ status: string }>(`/api/automations/${id}/retry`, {
    method: "POST"
  });
}
