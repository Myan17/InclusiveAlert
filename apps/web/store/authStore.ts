import { create } from "zustand"
import { persist } from "zustand/middleware"

export interface DecodedToken {
  sub: string   // email
  role: string
  exp?: number
}

export function decodeToken(token: string | null): DecodedToken | null {
  if (!token) return null
  try {
    const parts = token.split(".")
    if (parts.length !== 3) return null
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/")
    const json = atob(payload)
    return JSON.parse(json) as DecodedToken
  } catch {
    return null
  }
}

interface AuthState {
  token: string | null
  email: string | null
  role: string | null
  setToken: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      email: null,
      role: null,
      setToken: (token) => {
        const decoded = decodeToken(token)
        set({ token, email: decoded?.sub ?? null, role: decoded?.role ?? null })
      },
      logout: () => set({ token: null, email: null, role: null }),
    }),
    { name: "ia-auth" }
  )
)
