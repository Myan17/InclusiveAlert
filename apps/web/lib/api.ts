// lib/api.ts
import type {
  UserProfile, HazardEvent, Shelter, MatchAssignmentResponse, VictimListResponse, RespondentProfile, Severity, ShelterDetail
} from "@/lib/types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// The API emits lowercase severity/urgency ("severe", "immediate"), but the
// frontend types and lookups are Capitalized. Normalize at the boundary so
// every consumer sees the declared shape (and no lookup returns undefined).
const SEVERITIES: Severity[] = ["Extreme", "Severe", "Moderate", "Minor", "Unknown"]
function capitalize(s: string): string {
  return s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : s
}
function normalizeAlert(a: HazardEvent): HazardEvent {
  const sev = capitalize(a.severity as unknown as string) as Severity
  return {
    ...a,
    severity: SEVERITIES.includes(sev) ? sev : "Unknown",
    urgency: capitalize(a.urgency),
  }
}

export function buildHeaders(token: string | null): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`
  return headers
}

export function buildFormData(params: Record<string, string>): string {
  return Object.entries(params)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&")
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token: string | null = null
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { ...buildHeaders(token), ...(options.headers ?? {}) },
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request<{ access_token: string; token_type: string }>("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: buildFormData({ username: email, password }),
      }),
    register: (email: string, password: string, role: string) =>
      request<{ id: string; email: string; role: string }>("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, role }),
      }),
    me: (token: string) =>
      request<UserProfile>("/auth/me", {}, token),
  },
  profiles: {
    getVictim: (token: string) =>
      request<UserProfile>("/profiles/victim", {}, token),
    updateVictim: (token: string, data: Partial<UserProfile>) =>
      request<UserProfile>("/profiles/victim", {
        method: "POST",
        body: JSON.stringify(data),
      }, token),
    getRespondent: (token: string) =>
      request<RespondentProfile>("/profiles/respondent", {}, token),
    updateRespondent: (token: string, data: Partial<RespondentProfile>) =>
      request<RespondentProfile>("/profiles/respondent", {
        method: "POST",
        body: JSON.stringify(data),
      }, token),
  },
  alerts: {
    active: (token: string) =>
      request<HazardEvent[]>("/alerts/active", {}, token).then((rows) => rows.map(normalizeAlert)),
  },
  shelters: {
    ranked: (token: string, lat: number, lon: number, radius_km = 80) =>
      request<Shelter[]>(
        `/shelters/ranked?lat=${lat}&lon=${lon}&radius_km=${radius_km}`,
        {},
        token
      ),
    // Authority-only management endpoints.
    list: (token: string) => request<ShelterDetail[]>("/shelters", {}, token),
    create: (token: string, data: Record<string, unknown>) =>
      request<ShelterDetail>("/shelters", { method: "POST", body: JSON.stringify(data) }, token),
    patch: (token: string, id: string, data: Record<string, unknown>) =>
      request<ShelterDetail>(`/shelters/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token),
  },
  matching: {
    assign: (token: string, lat: number, lon: number) =>
      request<MatchAssignmentResponse>(
        `/matching/assign?lat=${lat}&lon=${lon}`,
        {},
        token
      ),
    victims: (token: string) =>
      request<VictimListResponse>("/matching/victims", {}, token),
  },
}
