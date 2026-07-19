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
  // False until zustand-persist has rehydrated from localStorage. Guards must
  // wait for this before redirecting, or a refresh/deep-link bounces to /login
  // while token is still transiently null.
  hasHydrated: boolean
  setToken: (token: string) => void
  logout: () => void
  setHasHydrated: (v: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      email: null,
      role: null,
      hasHydrated: false,
      setToken: (token) => {
        const decoded = decodeToken(token)
        set({ token, email: decoded?.sub ?? null, role: decoded?.role ?? null })
      },
      logout: () => set({ token: null, email: null, role: null }),
      setHasHydrated: (v) => set({ hasHydrated: v }),
    }),
    {
      name: "ia-auth",
      // Only persist the identity fields, never the hydration flag.
      partialize: (s) => ({ token: s.token, email: s.email, role: s.role }),
      onRehydrateStorage: () => (state) => state?.setHasHydrated(true),
    }
  )
)
