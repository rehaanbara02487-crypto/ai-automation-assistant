import type { ActivityLogRecord, AutomationPlan, AutomationSummary, Integration } from "@/types/automation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type TokenGetter = () => Promise<string | null>;

let authTokenGetter: TokenGetter | null = null;

export function setAuthTokenGetter(getter: TokenGetter | null) {
  authTokenGetter = getter;
}

export type CurrentUser = {
  id: string;
  email?: string | null;
  full_name?: string | null;
};

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return "Request failed";
      })
      .join(", ");
  }
  return "Something went wrong";
}

async function buildHeaders(init?: RequestInit): Promise<HeadersInit> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string> | undefined)
  };

  if (authTokenGetter) {
    const token = await authTokenGetter();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  return headers;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: await buildHeaders(init),
    cache: "no-store"
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(formatDetail(payload.detail));
  }

  return response.json();
}

export function createAutomation(input: string, businessType: string) {
  return request<AutomationPlan>("/api/automations/create", {
    method: "POST",
    body: JSON.stringify({ prompt: input, business_type: businessType })
  });
}

export function syncCurrentUser() {
  return request<CurrentUser>("/api/auth/me");
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

export function getAutomationLogs(automationId: string) {
  return request<ActivityLogRecord[]>(`/api/automations/${automationId}/logs`);
}
