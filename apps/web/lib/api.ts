// lib/api.ts
import type {
  UserProfile, HazardEvent, Shelter, MatchAssignmentResponse
} from "@/lib/types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

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
  },
  alerts: {
    active: (token: string) =>
      request<HazardEvent[]>("/alerts/active", {}, token),
  },
  shelters: {
    ranked: (token: string, lat: number, lon: number, radius_km = 80) =>
      request<Shelter[]>(
        `/shelters/ranked?lat=${lat}&lon=${lon}&radius_km=${radius_km}`,
        {},
        token
      ),
  },
  matching: {
    assign: (token: string, lat: number, lon: number) =>
      request<MatchAssignmentResponse>(
        `/matching/assign?lat=${lat}&lon=${lon}`,
        {},
        token
      ),
  },
}
