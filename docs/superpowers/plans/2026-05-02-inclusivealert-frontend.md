# InclusiveAlert Frontend Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a professional split-panel emergency dashboard (Next.js 14 + Leaflet + shadcn/ui) inside `apps/web/` that renders a role-aware view for victim, respondent, and authority users against the existing FastAPI backend at `http://localhost:8000`.

**Architecture:** Fixed left sidebar + data panel (40%) + Leaflet map (60%). TanStack Query handles polling. Zustand manages selected alert and user location. All pages are client components (no SSR needed — everything is auth-gated).

**Tech Stack:** Next.js 14 (App Router), Tailwind CSS (dark mode), shadcn/ui, React Leaflet + OpenStreetMap, TanStack Query v5, Zustand, TypeScript

---

## File Map

```
apps/web/
  app/
    globals.css                    ← Tailwind + Leaflet CSS import
    layout.tsx                     ← Root layout with QueryClientProvider
    middleware.ts                  ← Redirect unauthenticated → /login
    (auth)/
      login/page.tsx               ← Login form
      register/page.tsx            ← Register form
    dashboard/
      layout.tsx                   ← Shell: sidebar + data panel + map panel
      page.tsx                     ← Role-aware redirect + stat cards
      alerts/page.tsx              ← Alert list tab
      shelters/page.tsx            ← Shelter list tab
      matching/page.tsx            ← Matching / respondent tab
      profile/page.tsx             ← View + edit profile
  components/
    layout/
      Sidebar.tsx                  ← Nav links, user badge, logout
      StatCard.tsx                 ← Single stat tile (label + value + icon)
    map/
      MapPanel.tsx                 ← Dynamic Leaflet wrapper (ssr:false)
      MapInner.tsx                 ← Actual Leaflet map + layer composition
      HazardLayer.tsx              ← Polygon per alert, colored by severity
      ShelterLayer.tsx             ← Marker per shelter, colored by score
      RespondentLayer.tsx          ← Marker per respondent (authority only)
      LayerToggle.tsx              ← Checkbox panel top-right of map
    alerts/
      AlertCard.tsx                ← Severity badge, headline, countdown
    shelters/
      ShelterCard.tsx              ← Score bar, accessibility icons
    matching/
      MatchCard.tsx                ← Score breakdown accordion
    ui/                            ← shadcn generated components (do not edit)
  lib/
    types.ts                       ← All TypeScript interfaces matching API schemas
    api.ts                         ← Typed fetch wrappers for every endpoint
    useAlerts.ts                   ← TanStack Query, 30s poll
    useShelters.ts                 ← TanStack Query, 60s poll
    useMatching.ts                 ← TanStack Query, 60s poll
  store/
    authStore.ts                   ← JWT, decoded user, role (Zustand + localStorage)
    mapStore.ts                    ← selectedAlertId, userLocation, layer visibility
  __tests__/
    api.test.ts                    ← Unit tests for api.ts fetch wrappers
    authStore.test.ts              ← Unit tests for token decode + store
```

---

## Task 1: Scaffold Next.js App + Install Dependencies

**Files:**
- Create: `apps/web/` (entire Next.js project)
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/tailwind.config.ts`
- Create: `apps/web/.env.local`

- [ ] **Step 1: Scaffold the app**

Run from monorepo root:
```bash
cd apps
npx create-next-app@latest web \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*" \
  --no-eslint
```
When prompted: select all defaults.

- [ ] **Step 2: Install runtime dependencies**

```bash
cd web
npm install \
  @tanstack/react-query@^5 \
  zustand@^4 \
  react-leaflet@^4 \
  leaflet@^1.9 \
  @types/leaflet \
  jwt-decode@^4 \
  date-fns@^3 \
  lucide-react
```

- [ ] **Step 3: Install shadcn/ui**

```bash
npx shadcn@latest init
```
When prompted:
- Style: **Default**
- Base color: **Slate**
- CSS variables: **yes**

Then add components:
```bash
npx shadcn@latest add button card badge tabs separator avatar scroll-area accordion skeleton
```

- [ ] **Step 4: Enable Tailwind dark mode class strategy**

In `tailwind.config.ts`, ensure:
```typescript
const config = {
  darkMode: ["class"],
  // ...rest stays the same
}
```

- [ ] **Step 5: Add Leaflet CSS + dark class to globals.css**

Replace the contents of `app/globals.css` with:
```css
@import "leaflet/dist/leaflet.css";
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: 222 47% 7%;
  --foreground: 210 40% 98%;
  --card: 222 47% 11%;
  --card-foreground: 210 40% 98%;
  --border: 217 33% 17%;
  --input: 217 33% 17%;
  --primary: 210 40% 98%;
  --primary-foreground: 222 47% 7%;
  --muted: 217 33% 17%;
  --muted-foreground: 215 20% 65%;
  --ring: 212 97% 55%;
}

* { @apply border-border; }
body { @apply bg-background text-foreground; }
```

- [ ] **Step 6: Add env file**

Create `apps/web/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 7: Delete boilerplate**

Delete `app/page.tsx` content and replace with a redirect:
```typescript
// app/page.tsx
import { redirect } from "next/navigation"
export default function Root() {
  redirect("/dashboard")
}
```

Delete `public/vercel.svg`, `public/next.svg`, `app/favicon.ico` (optional cleanup).

- [ ] **Step 8: Verify dev server starts**

```bash
npm run dev
```
Expected: server starts on `http://localhost:3000`, no compile errors in terminal.

- [ ] **Step 9: Commit**

```bash
git add apps/web
git commit -m "feat: scaffold Next.js 14 frontend with Tailwind, shadcn/ui, Leaflet, TanStack Query"
```

---

## Task 2: Type Definitions + API Client

**Files:**
- Create: `apps/web/lib/types.ts`
- Create: `apps/web/lib/api.ts`
- Create: `apps/web/__tests__/api.test.ts`

- [ ] **Step 1: Write the failing tests first**

Create `apps/web/__tests__/api.test.ts`:
```typescript
import { buildHeaders, buildFormData } from "@/lib/api"

describe("buildHeaders", () => {
  it("returns JSON content-type and Authorization when token provided", () => {
    const h = buildHeaders("my-token")
    expect(h["Content-Type"]).toBe("application/json")
    expect(h["Authorization"]).toBe("Bearer my-token")
  })

  it("omits Authorization when no token", () => {
    const h = buildHeaders(null)
    expect(h["Authorization"]).toBeUndefined()
  })
})

describe("buildFormData", () => {
  it("encodes key=value pairs as URL-encoded string", () => {
    const body = buildFormData({ username: "a@b.com", password: "pass" })
    expect(body).toBe("username=a%40b.com&password=pass")
  })
})
```

Install test runner:
```bash
cd apps/web
npm install -D jest @types/jest ts-jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom
```

Add to `package.json`:
```json
"jest": {
  "preset": "ts-jest",
  "testEnvironment": "node",
  "moduleNameMapper": { "^@/(.*)$": "<rootDir>/$1" }
},
"scripts": {
  "test": "jest"
}
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
npm test -- --testPathPattern=api.test
```
Expected: FAIL — "Cannot find module '@/lib/api'"

- [ ] **Step 3: Create `lib/types.ts`**

```typescript
// lib/types.ts
export type Role = "victim" | "respondent" | "authority"
export type Severity = "Extreme" | "Severe" | "Moderate" | "Minor" | "Unknown"
export type AvailabilityStatus = "available" | "on_break" | "unavailable"

export interface UserProfile {
  id: string
  email: string
  role: Role
  disability_needs: string[]
  mobility_aids: string[]
  communication_modes: string[]
  medical_equipment: string[]
  medication_dependency: boolean
  power_dependency: boolean
  service_animal: boolean
  preferred_language: string
  location_zip: string | null
  location_city: string | null
  location_state: string | null
}

export interface HazardEvent {
  id: string
  external_id: string
  source: string
  hazard_type: string
  severity: Severity
  certainty: string
  urgency: string
  headline: string | null
  description: string | null
  instruction: string | null
  area_description: string | null
  effective_at: string
  expires_at: string | null
  source_confidence: number
  is_active: boolean
}

export interface Shelter {
  name: string
  address: string | null
  distance_km: number
  wheelchair_accessible: boolean
  ada_compliant: boolean
  generator_onsite: boolean
  pet_policy: "pets_allowed" | "no_pets"
  status: string
  capacity: number | null
  current_occupancy: number | null
  shelter_score: number
  lat: number | null
  lon: number | null
  source: string
}

export interface MatchBreakdown {
  proximity: number
  skill_fit: number
  availability: number
  route_safety: number
  trust_tier: number
  communication_fit: number
}

export interface MatchResult {
  respondent_id: string
  score: number
  breakdown: MatchBreakdown
}

export interface MatchAssignmentResponse {
  results: MatchResult[]
  total: number
}

export interface RespondentProfile {
  id: string
  user_id: string
  skills: string[]
  languages: string[]
  availability_status: AvailabilityStatus
  max_radius_km: number
  location_lat: number | null
  location_lon: number | null
  trust_tier: number
  communication_modes: string[]
}
```

- [ ] **Step 4: Create `lib/api.ts`**

```typescript
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
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
npm test -- --testPathPattern=api.test
```
Expected: 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add apps/web/lib/types.ts apps/web/lib/api.ts apps/web/__tests__/api.test.ts apps/web/package.json
git commit -m "feat: typed API client + shared TypeScript interfaces"
```

---

## Task 3: Auth Store + Login + Register Pages

**Files:**
- Create: `apps/web/store/authStore.ts`
- Create: `apps/web/__tests__/authStore.test.ts`
- Create: `apps/web/middleware.ts`
- Create: `apps/web/app/(auth)/login/page.tsx`
- Create: `apps/web/app/(auth)/register/page.tsx`
- Modify: `apps/web/app/layout.tsx`

- [ ] **Step 1: Write failing auth store tests**

Create `apps/web/__tests__/authStore.test.ts`:
```typescript
import { decodeToken, type DecodedToken } from "@/store/authStore"

describe("decodeToken", () => {
  it("returns null for null input", () => {
    expect(decodeToken(null)).toBeNull()
  })

  it("returns null for malformed token", () => {
    expect(decodeToken("not.a.token")).toBeNull()
  })

  it("decodes a valid JWT payload", () => {
    // header.payload.signature — payload is base64url of {"sub":"a@b.com","role":"victim"}
    const payload = btoa(JSON.stringify({ sub: "a@b.com", role: "victim" }))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "")
    const token = `header.${payload}.sig`
    const result = decodeToken(token)
    expect(result?.sub).toBe("a@b.com")
    expect(result?.role).toBe("victim")
  })
})
```

- [ ] **Step 2: Run to confirm failure**

```bash
npm test -- --testPathPattern=authStore.test
```
Expected: FAIL — "Cannot find module '@/store/authStore'"

- [ ] **Step 3: Create `store/authStore.ts`**

```typescript
// store/authStore.ts
"use client"
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
```

- [ ] **Step 4: Run tests to confirm pass**

```bash
npm test -- --testPathPattern=authStore.test
```
Expected: 3 tests PASS

- [ ] **Step 5: Add QueryClientProvider + dark class to root layout**

Replace `app/layout.tsx`:
```typescript
// app/layout.tsx
"use client"
import "@/app/globals.css"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { retry: 1, staleTime: 20_000 } },
  }))
  return (
    <html lang="en" className="dark">
      <body>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  )
}
```

- [ ] **Step 6: Create middleware for auth redirect**

Create `apps/web/middleware.ts`:
```typescript
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(req: NextRequest) {
  const token = req.cookies.get("ia-auth")?.value
  const { pathname } = req.nextUrl

  const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/register")
  const isDashboard = pathname.startsWith("/dashboard")

  // Parse persisted Zustand store from cookie if present
  // Simpler: just check localStorage isn't available in middleware, use a cookie instead.
  // We'll do client-side redirect in the dashboard layout instead.
  return NextResponse.next()
}

export const config = { matcher: ["/dashboard/:path*"] }
```

Note: since Zustand persists to localStorage (not cookies), auth enforcement is done client-side in the dashboard layout.

- [ ] **Step 7: Create login page**

Create `apps/web/app/(auth)/login/page.tsx`:
```typescript
"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const setToken = useAuthStore((s) => s.setToken)
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { access_token } = await api.auth.login(email, password)
      setToken(access_token)
      router.push("/dashboard")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Card className="w-full max-w-sm bg-card border-border">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            InclusiveAlert
          </CardTitle>
          <p className="text-muted-foreground text-center text-sm">Sign in to your account</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            {error && <p className="text-red-400 text-xs">{error}</p>}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Signing in…" : "Sign in"}
            </Button>
            <p className="text-center text-xs text-muted-foreground">
              No account?{" "}
              <a href="/register" className="text-primary underline">Register</a>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 8: Create register page**

Create `apps/web/app/(auth)/register/page.tsx`:
```typescript
"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Role } from "@/lib/types"

export default function RegisterPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [role, setRole] = useState<Role>("victim")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await api.auth.register(email, password, role)
      router.push("/login")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Card className="w-full max-w-sm bg-card border-border">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Create Account</CardTitle>
          <p className="text-muted-foreground text-center text-sm">Join InclusiveAlert</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <input
              type="email" placeholder="Email" value={email}
              onChange={(e) => setEmail(e.target.value)} required
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <input
              type="password" placeholder="Password" value={password}
              onChange={(e) => setPassword(e.target.value)} required
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <select
              value={role} onChange={(e) => setRole(e.target.value as Role)}
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none"
            >
              <option value="victim">Victim (needs assistance)</option>
              <option value="respondent">Respondent (provides help)</option>
              <option value="authority">Authority (emergency operator)</option>
            </select>
            {error && <p className="text-red-400 text-xs">{error}</p>}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Creating…" : "Create account"}
            </Button>
            <p className="text-center text-xs text-muted-foreground">
              Have an account?{" "}
              <a href="/login" className="text-primary underline">Sign in</a>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
```

- [ ] **Step 9: Verify login page renders**

```bash
npm run dev
```
Open `http://localhost:3000/login` — should show the InclusiveAlert login card on a dark background. No console errors.

- [ ] **Step 10: Commit**

```bash
git add apps/web/store apps/web/__tests__/authStore.test.ts apps/web/app apps/web/middleware.ts
git commit -m "feat: auth store, login + register pages, root layout with QueryClientProvider"
```

---

## Task 4: Dashboard Shell — Sidebar + Split Panel Layout

**Files:**
- Create: `apps/web/components/layout/Sidebar.tsx`
- Create: `apps/web/components/layout/StatCard.tsx`
- Create: `apps/web/app/dashboard/layout.tsx`

- [ ] **Step 1: Create `StatCard.tsx`**

```typescript
// components/layout/StatCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  label: string
  value: string | number
  icon: LucideIcon
  accent?: "red" | "orange" | "green" | "blue"
}

const accentClasses = {
  red: "text-red-400",
  orange: "text-orange-400",
  green: "text-green-400",
  blue: "text-blue-400",
}

export function StatCard({ label, value, icon: Icon, accent = "blue" }: StatCardProps) {
  return (
    <Card className="bg-card border-border flex-1 min-w-[120px]">
      <CardContent className="p-4 flex items-center gap-3">
        <Icon className={`h-5 w-5 shrink-0 ${accentClasses[accent]}`} />
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-lg font-bold text-foreground">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
```

- [ ] **Step 2: Create `Sidebar.tsx`**

```typescript
// components/layout/Sidebar.tsx
"use client"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Bell, MapPin, Users, User, LogOut, Shield } from "lucide-react"
import { useAuthStore } from "@/store/authStore"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

const navItems = [
  { href: "/dashboard/alerts",   label: "Alerts",   icon: Bell },
  { href: "/dashboard/shelters", label: "Shelters", icon: MapPin },
  { href: "/dashboard/matching", label: "Matching", icon: Users },
  { href: "/dashboard/profile",  label: "Profile",  icon: User },
]

const roleColors: Record<string, string> = {
  victim: "bg-red-900 text-red-300",
  respondent: "bg-green-900 text-green-300",
  authority: "bg-blue-900 text-blue-300",
}

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { email, role, logout } = useAuthStore()

  function handleLogout() {
    logout()
    router.push("/login")
  }

  return (
    <aside className="w-60 shrink-0 flex flex-col h-screen bg-[#13151f] border-r border-border">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-blue-400" />
          <span className="font-bold text-foreground text-sm">InclusiveAlert</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-blue-950 text-blue-300 font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* User section */}
      <div className="px-4 py-4 border-t border-border flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-foreground">
            {email?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-foreground truncate">{email}</p>
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${roleColors[role ?? "victim"] ?? ""}`}>
              {role}
            </span>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogout}
          className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground text-xs"
        >
          <LogOut className="h-3 w-3" />
          Sign out
        </Button>
      </div>
    </aside>
  )
}
```

- [ ] **Step 3: Create dashboard layout**

Create `apps/web/app/dashboard/layout.tsx`:
```typescript
// app/dashboard/layout.tsx
"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"
import { Sidebar } from "@/components/layout/Sidebar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!token) router.replace("/login")
  }, [token, router])

  if (!token) return null

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      {/* Data panel */}
      <div className="w-[40%] flex flex-col h-screen overflow-y-auto border-r border-border">
        {children}
      </div>
      {/* Map panel — rendered by each page via a portal or in layout */}
      <div id="map-panel" className="flex-1 h-screen" />
    </div>
  )
}
```

- [ ] **Step 4: Create placeholder dashboard page**

Create `apps/web/app/dashboard/page.tsx`:
```typescript
// app/dashboard/page.tsx
"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"

export default function DashboardHome() {
  const { role } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (role === "respondent") router.replace("/dashboard/matching")
    else router.replace("/dashboard/alerts")
  }, [role, router])

  return null
}
```

- [ ] **Step 5: Verify layout renders**

```bash
npm run dev
```
Navigate to `http://localhost:3000` → should redirect to `/login`, then after login → `/dashboard/alerts` with sidebar visible. No console errors.

- [ ] **Step 6: Commit**

```bash
git add apps/web/components/layout apps/web/app/dashboard
git commit -m "feat: dashboard shell — sidebar, split-panel layout, auth guard"
```

---

## Task 5: Map Panel Base

**Files:**
- Create: `apps/web/store/mapStore.ts`
- Create: `apps/web/components/map/MapInner.tsx`
- Create: `apps/web/components/map/MapPanel.tsx`

- [ ] **Step 1: Create map store**

```typescript
// store/mapStore.ts
import { create } from "zustand"

interface MapState {
  selectedAlertId: string | null
  userLat: number | null
  userLon: number | null
  showHazards: boolean
  showShelters: boolean
  showRespondents: boolean
  setSelectedAlert: (id: string | null) => void
  setUserLocation: (lat: number, lon: number) => void
  toggleLayer: (layer: "showHazards" | "showShelters" | "showRespondents") => void
}

export const useMapStore = create<MapState>((set) => ({
  selectedAlertId: null,
  userLat: null,
  userLon: null,
  showHazards: true,
  showShelters: true,
  showRespondents: true,
  setSelectedAlert: (id) => set({ selectedAlertId: id }),
  setUserLocation: (lat, lon) => set({ userLat: lat, userLon: lon }),
  toggleLayer: (layer) => set((s) => ({ [layer]: !s[layer] })),
}))
```

- [ ] **Step 2: Create `MapInner.tsx` (actual Leaflet component)**

```typescript
// components/map/MapInner.tsx
"use client"
import { useEffect } from "react"
import { MapContainer, TileLayer, useMap } from "react-leaflet"
import { useMapStore } from "@/store/mapStore"
import { LayerToggle } from "./LayerToggle"

function LocationTracker() {
  const { setUserLocation } = useMapStore()
  useEffect(() => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserLocation(pos.coords.latitude, pos.coords.longitude),
      () => {} // silently ignore denied
    )
  }, [setUserLocation])
  return null
}

export function MapInner() {
  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={[39.5, -98.35]}
        zoom={4}
        style={{ width: "100%", height: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <LocationTracker />
        {/* Layer components added in later tasks */}
      </MapContainer>
      <LayerToggle />
    </div>
  )
}
```

- [ ] **Step 3: Create `LayerToggle.tsx`**

```typescript
// components/map/LayerToggle.tsx
"use client"
import { useMapStore } from "@/store/mapStore"

export function LayerToggle() {
  const { showHazards, showShelters, showRespondents, toggleLayer } = useMapStore()

  return (
    <div className="absolute top-3 right-3 z-[1000] bg-card border border-border rounded-md p-2 flex flex-col gap-1 text-xs shadow-lg">
      {([
        ["showHazards", showHazards, "Hazard Zones"],
        ["showShelters", showShelters, "Shelters"],
        ["showRespondents", showRespondents, "Respondents"],
      ] as const).map(([key, checked, label]) => (
        <label key={key} className="flex items-center gap-2 cursor-pointer text-foreground">
          <input
            type="checkbox"
            checked={checked}
            onChange={() => toggleLayer(key)}
            className="accent-blue-400"
          />
          {label}
        </label>
      ))}
    </div>
  )
}
```

- [ ] **Step 4: Create `MapPanel.tsx` with dynamic import (SSR-safe)**

```typescript
// components/map/MapPanel.tsx
"use client"
import dynamic from "next/dynamic"

const MapInner = dynamic(
  () => import("./MapInner").then((m) => ({ default: m.MapInner })),
  { ssr: false, loading: () => <div className="w-full h-full bg-muted animate-pulse" /> }
)

export function MapPanel() {
  return (
    <div className="w-full h-full">
      <MapInner />
    </div>
  )
}
```

- [ ] **Step 5: Wire MapPanel into the dashboard layout**

Update `app/dashboard/layout.tsx` — replace the `<div id="map-panel" .../>` line:
```typescript
import { MapPanel } from "@/components/map/MapPanel"

// Replace the map panel div with:
<div className="flex-1 h-screen">
  <MapPanel />
</div>
```

Full updated `app/dashboard/layout.tsx`:
```typescript
"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"
import { Sidebar } from "@/components/layout/Sidebar"
import { MapPanel } from "@/components/map/MapPanel"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!token) router.replace("/login")
  }, [token, router])

  if (!token) return null

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="w-[40%] flex flex-col h-screen overflow-y-auto border-r border-border">
        {children}
      </div>
      <div className="flex-1 h-screen">
        <MapPanel />
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Verify map renders**

```bash
npm run dev
```
Log in and navigate to `/dashboard`. The right 60% should show an OpenStreetMap tile map. The top-right corner of the map should show the layer toggle checkboxes. No "window is not defined" SSR errors.

- [ ] **Step 7: Commit**

```bash
git add apps/web/store/mapStore.ts apps/web/components/map
git commit -m "feat: Leaflet map panel with layer toggles and geolocation tracking"
```

---

## Task 6: Alerts View — Data Hook + AlertCard + HazardLayer

**Files:**
- Create: `apps/web/lib/useAlerts.ts`
- Create: `apps/web/components/alerts/AlertCard.tsx`
- Create: `apps/web/app/dashboard/alerts/page.tsx`
- Create: `apps/web/components/map/HazardLayer.tsx`
- Modify: `apps/web/components/map/MapInner.tsx`

- [ ] **Step 1: Create `useAlerts.ts`**

```typescript
// lib/useAlerts.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import type { HazardEvent } from "@/lib/types"

export function useAlerts() {
  const token = useAuthStore((s) => s.token)
  return useQuery<HazardEvent[]>({
    queryKey: ["alerts"],
    queryFn: () => api.alerts.active(token!),
    enabled: !!token,
    refetchInterval: 30_000,
    staleTime: 25_000,
  })
}
```

- [ ] **Step 2: Create `AlertCard.tsx`**

```typescript
// components/alerts/AlertCard.tsx
"use client"
import { formatDistanceToNow, parseISO } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import type { HazardEvent, Severity } from "@/lib/types"
import { useMapStore } from "@/store/mapStore"

const severityStyles: Record<Severity, string> = {
  Extreme: "bg-red-900 text-red-300 border-red-700",
  Severe:  "bg-orange-900 text-orange-300 border-orange-700",
  Moderate:"bg-yellow-900 text-yellow-300 border-yellow-700",
  Minor:   "bg-blue-900 text-blue-300 border-blue-700",
  Unknown: "bg-muted text-muted-foreground border-border",
}

const severityBorder: Record<Severity, string> = {
  Extreme: "border-l-red-500",
  Severe:  "border-l-orange-500",
  Moderate:"border-l-yellow-500",
  Minor:   "border-l-blue-400",
  Unknown: "border-l-muted",
}

interface AlertCardProps {
  alert: HazardEvent
  selected?: boolean
}

export function AlertCard({ alert, selected }: AlertCardProps) {
  const setSelectedAlert = useMapStore((s) => s.setSelectedAlert)
  const sev = alert.severity as Severity

  return (
    <Card
      id={`alert-${alert.id}`}
      onClick={() => setSelectedAlert(alert.id)}
      className={`bg-card border border-border border-l-4 ${severityBorder[sev]} cursor-pointer transition-all ${
        selected ? "ring-2 ring-blue-500" : "hover:border-border/80"
      }`}
    >
      <CardContent className="p-4 flex flex-col gap-2">
        <div className="flex items-start justify-between gap-2">
          <span className="text-sm font-semibold text-foreground leading-tight">
            {alert.headline ?? alert.hazard_type}
          </span>
          <Badge className={`text-[10px] shrink-0 border ${severityStyles[sev]}`}>
            {alert.severity}
          </Badge>
        </div>
        {alert.area_description && (
          <p className="text-xs text-muted-foreground">{alert.area_description}</p>
        )}
        <div className="flex items-center justify-between text-[10px] text-muted-foreground">
          <span>{alert.source.toUpperCase()} · {alert.hazard_type}</span>
          <span>
            {alert.expires_at
              ? `Expires ${formatDistanceToNow(parseISO(alert.expires_at), { addSuffix: true })}`
              : "No expiry"}
          </span>
        </div>
        {alert.instruction && (
          <p className="text-xs text-blue-300 border-t border-border pt-2">{alert.instruction}</p>
        )}
      </CardContent>
    </Card>
  )
}
```

- [ ] **Step 3: Create `alerts/page.tsx`**

```typescript
// app/dashboard/alerts/page.tsx
"use client"
import { Bell } from "lucide-react"
import { useAlerts } from "@/lib/useAlerts"
import { AlertCard } from "@/components/alerts/AlertCard"
import { useMapStore } from "@/store/mapStore"
import { Skeleton } from "@/components/ui/skeleton"
import { StatCard } from "@/components/layout/StatCard"

export default function AlertsPage() {
  const { data: alerts = [], isLoading } = useAlerts()
  const { selectedAlertId } = useMapStore()

  const extremeCount = alerts.filter((a) => a.severity === "Extreme" || a.severity === "Severe").length

  return (
    <div className="flex flex-col h-full">
      {/* Stats */}
      <div className="px-4 pt-4 pb-3 flex gap-3 border-b border-border shrink-0">
        <StatCard label="Active Alerts" value={alerts.length} icon={Bell} accent="red" />
        <StatCard label="Severe / Extreme" value={extremeCount} icon={Bell} accent="orange" />
      </div>

      {/* Alert list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
        {isLoading && Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-md" />
        ))}
        {!isLoading && alerts.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
            <Bell className="h-10 w-10 mb-2 opacity-30" />
            <p className="text-sm">No active alerts</p>
          </div>
        )}
        {alerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            selected={selectedAlertId === alert.id}
          />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create `HazardLayer.tsx`**

```typescript
// components/map/HazardLayer.tsx
"use client"
import { GeoJSON, useMap } from "react-leaflet"
import { useEffect } from "react"
import { useAlerts } from "@/lib/useAlerts"
import { useMapStore } from "@/store/mapStore"
import type { Severity } from "@/lib/types"
import type { Layer } from "leaflet"

const severityFill: Record<Severity, string> = {
  Extreme: "#ef4444",
  Severe:  "#f97316",
  Moderate:"#eab308",
  Minor:   "#60a5fa",
  Unknown: "#6b7280",
}

// Note: HazardEvent geometry is stored in PostGIS and not returned by the API yet.
// This layer renders a circle marker at alert centroid using area_description as label.
// Full polygon rendering requires a geometry field added to HazardEventResponse.
import { CircleMarker, Tooltip } from "react-leaflet"
import type { HazardEvent } from "@/lib/types"

export function HazardLayer() {
  const { data: alerts = [] } = useAlerts()
  const { showHazards, selectedAlertId, setSelectedAlert } = useMapStore()

  if (!showHazards) return null

  // Filter alerts that have geometry placeholders — for now render nothing
  // until the API exposes lat/lon centroids. This component is ready to use
  // once the backend adds centroid fields to HazardEventResponse.
  return null
}
```

Note: The current API's `HazardEventResponse` schema does not include lat/lon centroid. The HazardLayer is scaffolded and will render once the backend adds centroid fields. Alert cards still display and the map base tiles always show.

- [ ] **Step 5: Add HazardLayer to MapInner**

Update `components/map/MapInner.tsx` — add the import and component inside `<MapContainer>`:
```typescript
import { HazardLayer } from "./HazardLayer"

// Inside <MapContainer>, after <TileLayer>:
<HazardLayer />
```

- [ ] **Step 6: Verify alerts page**

```bash
npm run dev
```
Navigate to `/dashboard/alerts`. Should see the stat bar at top and a scrollable list of alert cards (or "No active alerts" if DB is empty). Cards should render with severity-colored left border. No console errors.

- [ ] **Step 7: Commit**

```bash
git add apps/web/lib/useAlerts.ts apps/web/components/alerts apps/web/app/dashboard/alerts apps/web/components/map/HazardLayer.tsx
git commit -m "feat: alerts view with 30s polling, AlertCard severity styling, HazardLayer scaffold"
```

---

## Task 7: Shelters View — Data Hook + ShelterCard + ShelterLayer

**Files:**
- Create: `apps/web/lib/useShelters.ts`
- Create: `apps/web/components/shelters/ShelterCard.tsx`
- Create: `apps/web/app/dashboard/shelters/page.tsx`
- Create: `apps/web/components/map/ShelterLayer.tsx`
- Modify: `apps/web/components/map/MapInner.tsx`

- [ ] **Step 1: Create `useShelters.ts`**

```typescript
// lib/useShelters.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { useMapStore } from "@/store/mapStore"
import type { Shelter } from "@/lib/types"

export function useShelters() {
  const token = useAuthStore((s) => s.token)
  const { userLat, userLon } = useMapStore()
  return useQuery<Shelter[]>({
    queryKey: ["shelters", userLat, userLon],
    queryFn: () => api.shelters.ranked(token!, userLat!, userLon!),
    enabled: !!token && userLat !== null && userLon !== null,
    refetchInterval: 60_000,
    staleTime: 55_000,
  })
}
```

- [ ] **Step 2: Create `ShelterCard.tsx`**

```typescript
// components/shelters/ShelterCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Shelter } from "@/lib/types"

interface ShelterCardProps {
  shelter: Shelter
  rank: number
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-yellow-500" : "bg-red-500"
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-muted-foreground w-7 text-right">{pct}%</span>
    </div>
  )
}

export function ShelterCard({ shelter, rank }: ShelterCardProps) {
  return (
    <Card className="bg-card border-border">
      <CardContent className="p-4 flex flex-col gap-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-[10px] text-muted-foreground">#{rank} · {shelter.distance_km.toFixed(1)} km away</span>
            <p className="text-sm font-semibold text-foreground leading-tight">{shelter.name}</p>
            {shelter.address && (
              <p className="text-xs text-muted-foreground">{shelter.address}</p>
            )}
          </div>
          <Badge
            className={`text-[10px] shrink-0 ${
              shelter.status === "open" ? "bg-green-900 text-green-300" : "bg-red-900 text-red-300"
            }`}
          >
            {shelter.status}
          </Badge>
        </div>

        <ScoreBar score={shelter.shelter_score} />

        <div className="flex flex-wrap gap-1">
          {shelter.wheelchair_accessible && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300">♿ Accessible</span>
          )}
          {shelter.generator_onsite && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-950 text-yellow-300">⚡ Generator</span>
          )}
          {shelter.pet_policy === "pets_allowed" && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-950 text-green-300">🐕 Pets OK</span>
          )}
          {shelter.ada_compliant && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-950 text-purple-300">ADA</span>
          )}
        </div>

        {shelter.capacity !== null && (
          <div className="text-[10px] text-muted-foreground">
            Capacity: {shelter.current_occupancy ?? "?"} / {shelter.capacity}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

- [ ] **Step 3: Create `shelters/page.tsx`**

```typescript
// app/dashboard/shelters/page.tsx
"use client"
import { MapPin } from "lucide-react"
import { useShelters } from "@/lib/useShelters"
import { ShelterCard } from "@/components/shelters/ShelterCard"
import { useMapStore } from "@/store/mapStore"
import { Skeleton } from "@/components/ui/skeleton"
import { StatCard } from "@/components/layout/StatCard"

export default function SheltersPage() {
  const { data: shelters = [], isLoading } = useShelters()
  const { userLat } = useMapStore()

  const openCount = shelters.filter((s) => s.status === "open").length
  const nearestKm = shelters[0]?.distance_km?.toFixed(1) ?? "—"

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 flex gap-3 border-b border-border shrink-0">
        <StatCard label="Open Shelters" value={openCount} icon={MapPin} accent="green" />
        <StatCard label="Nearest (km)" value={nearestKm} icon={MapPin} accent="blue" />
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
        {!userLat && (
          <div className="text-sm text-muted-foreground bg-muted rounded-md px-4 py-3">
            Allow location access to see ranked shelters near you.
          </div>
        )}
        {isLoading && Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-28 w-full rounded-md" />
        ))}
        {!isLoading && shelters.length === 0 && userLat && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
            <MapPin className="h-10 w-10 mb-2 opacity-30" />
            <p className="text-sm">No shelters found nearby</p>
          </div>
        )}
        {shelters.map((shelter, i) => (
          <ShelterCard key={`${shelter.name}-${i}`} shelter={shelter} rank={i + 1} />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create `ShelterLayer.tsx`**

```typescript
// components/map/ShelterLayer.tsx
"use client"
import { CircleMarker, Popup } from "react-leaflet"
import { useShelters } from "@/lib/useShelters"
import { useMapStore } from "@/store/mapStore"

function scoreColor(score: number): string {
  if (score >= 0.7) return "#22c55e"  // green-500
  if (score >= 0.4) return "#eab308"  // yellow-500
  return "#ef4444"                    // red-500
}

export function ShelterLayer() {
  const { data: shelters = [] } = useShelters()
  const { showShelters } = useMapStore()

  if (!showShelters) return null

  return (
    <>
      {shelters
        .filter((s) => s.lat !== null && s.lon !== null)
        .map((shelter, i) => (
          <CircleMarker
            key={`shelter-${i}`}
            center={[shelter.lat!, shelter.lon!]}
            radius={8}
            pathOptions={{
              fillColor: scoreColor(shelter.shelter_score),
              fillOpacity: 0.85,
              color: "#fff",
              weight: 1.5,
            }}
          >
            <Popup>
              <div className="text-xs">
                <p className="font-semibold">{shelter.name}</p>
                <p>{shelter.address}</p>
                <p>Score: {Math.round(shelter.shelter_score * 100)}%</p>
                <p>{shelter.distance_km.toFixed(1)} km away</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
    </>
  )
}
```

- [ ] **Step 5: Add ShelterLayer to MapInner**

Update `components/map/MapInner.tsx`:
```typescript
import { ShelterLayer } from "./ShelterLayer"

// Inside <MapContainer>, after <HazardLayer />:
<ShelterLayer />
```

- [ ] **Step 6: Verify shelters page**

```bash
npm run dev
```
Navigate to `/dashboard/shelters`. If geolocation was granted, shelter cards should appear (or "No shelters found" if FEMA API returned none). Green/yellow/red circle markers should appear on the map for shelters with coordinates. No console errors.

- [ ] **Step 7: Commit**

```bash
git add apps/web/lib/useShelters.ts apps/web/components/shelters apps/web/app/dashboard/shelters apps/web/components/map/ShelterLayer.tsx
git commit -m "feat: shelters view with score bars, accessibility badges, ShelterLayer map pins"
```

---

## Task 8: Matching View — Data Hook + MatchCard + RespondentLayer

**Files:**
- Create: `apps/web/lib/useMatching.ts`
- Create: `apps/web/components/matching/MatchCard.tsx`
- Create: `apps/web/app/dashboard/matching/page.tsx`
- Create: `apps/web/components/map/RespondentLayer.tsx`
- Modify: `apps/web/components/map/MapInner.tsx`

- [ ] **Step 1: Create `useMatching.ts`**

```typescript
// lib/useMatching.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { useMapStore } from "@/store/mapStore"
import type { MatchAssignmentResponse } from "@/lib/types"

export function useMatching() {
  const token = useAuthStore((s) => s.token)
  const { userLat, userLon } = useMapStore()
  return useQuery<MatchAssignmentResponse>({
    queryKey: ["matching", userLat, userLon],
    queryFn: () => api.matching.assign(token!, userLat!, userLon!),
    enabled: !!token && userLat !== null && userLon !== null,
    refetchInterval: 60_000,
    staleTime: 55_000,
  })
}
```

- [ ] **Step 2: Create `MatchCard.tsx`**

```typescript
// components/matching/MatchCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion"
import type { MatchResult } from "@/lib/types"

interface MatchCardProps {
  result: MatchResult
  rank: number
}

function MiniBar({ value, label }: { value: number; label: string }) {
  const pct = Math.round(value * 100)
  return (
    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
      <span className="w-28 truncate">{label}</span>
      <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="w-7 text-right">{pct}%</span>
    </div>
  )
}

export function MatchCard({ result, rank }: MatchCardProps) {
  const pct = Math.round(result.score * 100)
  const shortId = result.respondent_id.slice(0, 8)

  return (
    <Card className="bg-card border-border">
      <CardContent className="p-4 flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[10px] text-muted-foreground">#{rank} · Respondent {shortId}</span>
            <div className="flex items-center gap-2 mt-0.5">
              <div className="h-2 flex-1 max-w-[100px] bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-yellow-500" : "bg-red-500"}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-sm font-bold text-foreground">{pct}%</span>
            </div>
          </div>
        </div>

        <Accordion type="single" collapsible>
          <AccordionItem value="breakdown" className="border-none">
            <AccordionTrigger className="text-[10px] text-muted-foreground py-1 hover:no-underline">
              Score breakdown
            </AccordionTrigger>
            <AccordionContent className="flex flex-col gap-1.5 pb-0">
              <MiniBar value={result.breakdown.proximity} label="Proximity" />
              <MiniBar value={result.breakdown.skill_fit} label="Skill Fit" />
              <MiniBar value={result.breakdown.availability} label="Availability" />
              <MiniBar value={result.breakdown.trust_tier} label="Trust Tier" />
              <MiniBar value={result.breakdown.communication_fit} label="Communication" />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  )
}
```

- [ ] **Step 3: Create `matching/page.tsx`**

```typescript
// app/dashboard/matching/page.tsx
"use client"
import { Users } from "lucide-react"
import { useMatching } from "@/lib/useMatching"
import { MatchCard } from "@/components/matching/MatchCard"
import { useMapStore } from "@/store/mapStore"
import { Skeleton } from "@/components/ui/skeleton"
import { StatCard } from "@/components/layout/StatCard"

export default function MatchingPage() {
  const { data, isLoading } = useMatching()
  const { userLat } = useMapStore()
  const results = data?.results ?? []

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 flex gap-3 border-b border-border shrink-0">
        <StatCard label="Matched Respondents" value={data?.total ?? 0} icon={Users} accent="green" />
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
        {!userLat && (
          <div className="text-sm text-muted-foreground bg-muted rounded-md px-4 py-3">
            Allow location access to find nearby respondents.
          </div>
        )}
        {isLoading && Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-md" />
        ))}
        {!isLoading && results.length === 0 && userLat && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground">
            <Users className="h-10 w-10 mb-2 opacity-30" />
            <p className="text-sm">No available respondents</p>
          </div>
        )}
        {results.map((result, i) => (
          <MatchCard key={result.respondent_id} result={result} rank={i + 1} />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create `RespondentLayer.tsx`**

```typescript
// components/map/RespondentLayer.tsx
"use client"
import { CircleMarker, Popup } from "react-leaflet"
import { useMatching } from "@/lib/useMatching"
import { useMapStore } from "@/store/mapStore"
import { useAuthStore } from "@/store/authStore"

// The matching API returns respondent_id + score but not lat/lon.
// This layer is ready for when the backend includes respondent location in the response.
// Currently renders nothing — authority map pins require a future /respondents endpoint.
export function RespondentLayer() {
  const { showRespondents } = useMapStore()
  const role = useAuthStore((s) => s.role)

  if (!showRespondents || role !== "authority") return null

  // TODO: wire to a future GET /respondents endpoint that returns locations
  return null
}
```

- [ ] **Step 5: Add RespondentLayer to MapInner**

Update `components/map/MapInner.tsx`:
```typescript
import { RespondentLayer } from "./RespondentLayer"

// Inside <MapContainer>:
<RespondentLayer />
```

- [ ] **Step 6: Verify matching page**

```bash
npm run dev
```
Navigate to `/dashboard/matching`. Should show the stat card and match cards (or empty state). Score breakdown accordion should expand on click. No console errors.

- [ ] **Step 7: Commit**

```bash
git add apps/web/lib/useMatching.ts apps/web/components/matching apps/web/app/dashboard/matching apps/web/components/map/RespondentLayer.tsx
git commit -m "feat: matching view with MatchCard score breakdown accordion + RespondentLayer scaffold"
```

---

## Task 9: Profile Page

**Files:**
- Create: `apps/web/app/dashboard/profile/page.tsx`

- [ ] **Step 1: Create profile page**

```typescript
// app/dashboard/profile/page.tsx
"use client"
import { useEffect, useState } from "react"
import { User } from "lucide-react"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { UserProfile } from "@/lib/types"

const DISABILITY_OPTIONS = [
  { value: "deaf",              label: "Deaf / Hard of Hearing" },
  { value: "blind",             label: "Blind / Low Vision" },
  { value: "mobility_wheelchair", label: "Wheelchair User" },
  { value: "power_dependent",   label: "Power Dependent (medical)" },
]

export default function ProfilePage() {
  const { token, email, role } = useAuthStore()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [needs, setNeeds] = useState<string[]>([])
  const [zip, setZip] = useState("")
  const [state, setState] = useState("")
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (!token) return
    api.profiles.getVictim(token).then((p) => {
      setProfile(p)
      setNeeds(p.disability_needs ?? [])
      setZip(p.location_zip ?? "")
      setState(p.location_state ?? "")
    })
  }, [token])

  function toggleNeed(value: string) {
    setNeeds((prev) =>
      prev.includes(value) ? prev.filter((n) => n !== value) : [...prev, value]
    )
  }

  async function handleSave() {
    if (!token) return
    setSaving(true)
    try {
      await api.profiles.updateVictim(token, {
        disability_needs: needs,
        location_zip: zip || null,
        location_state: state || null,
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center text-lg font-bold">
            {email?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">{email}</p>
            <Badge className="text-[10px] mt-0.5 bg-blue-900 text-blue-300">{role}</Badge>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4 flex flex-col gap-3">
            <p className="text-xs font-semibold text-foreground">Disability Needs</p>
            <div className="flex flex-col gap-2">
              {DISABILITY_OPTIONS.map(({ value, label }) => (
                <label key={value} className="flex items-center gap-2 cursor-pointer text-sm text-foreground">
                  <input
                    type="checkbox"
                    checked={needs.includes(value)}
                    onChange={() => toggleNeed(value)}
                    className="accent-blue-400"
                  />
                  {label}
                </label>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardContent className="p-4 flex flex-col gap-3">
            <p className="text-xs font-semibold text-foreground">Location</p>
            <input
              type="text"
              placeholder="ZIP Code"
              value={zip}
              onChange={(e) => setZip(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <input
              type="text"
              placeholder="State (e.g. TX)"
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </CardContent>
        </Card>

        <Button onClick={handleSave} disabled={saving} className="w-full">
          {saving ? "Saving…" : saved ? "Saved ✓" : "Save profile"}
        </Button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify profile page**

```bash
npm run dev
```
Navigate to `/dashboard/profile`. Should show your email, role badge, disability checkboxes, and location fields. Clicking "Save profile" should POST to the API and show "Saved ✓" briefly. No console errors.

- [ ] **Step 3: Commit**

```bash
git add apps/web/app/dashboard/profile
git commit -m "feat: profile page with disability needs checklist and location fields"
```

---

## Task 10: Run All Tests + Final Verification

**Files:**
- Verify: `apps/web/__tests__/api.test.ts`
- Verify: `apps/web/__tests__/authStore.test.ts`

- [ ] **Step 1: Run full test suite**

```bash
cd apps/web
npm test
```
Expected output:
```
PASS __tests__/api.test.ts
PASS __tests__/authStore.test.ts

Test Suites: 2 passed, 2 total
Tests:       6 passed, 6 total
```

- [ ] **Step 2: Run TypeScript type check**

```bash
npx tsc --noEmit
```
Expected: no output (no type errors).

- [ ] **Step 3: Build production bundle**

```bash
npm run build
```
Expected: build completes successfully, no errors. Warnings about `img` vs `Image` are acceptable.

- [ ] **Step 4: Smoke-test the full user flow**

Start the FastAPI backend:
```bash
cd /Users/myangupta/Desktop/InclusiveAlert/inclusive-alert/apps/api
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Start the frontend:
```bash
cd /Users/myangupta/Desktop/InclusiveAlert/inclusive-alert/apps/web
npm run dev
```

Walk through:
1. `http://localhost:3000/register` → create a victim account
2. `http://localhost:3000/login` → sign in → redirects to `/dashboard/alerts`
3. Sidebar shows your email + "victim" role pill
4. Alerts tab → polling badge, alert cards or empty state
5. Shelters tab → allow geolocation → shelter cards or "No shelters found"
6. Matching tab → match cards or empty state
7. Profile tab → check "Wheelchair User" → Save → refresh → still checked
8. Map panel shows OpenStreetMap tiles, layer toggles in top-right
9. Shelter pins appear on map (green/yellow/red circles) if shelters returned
10. Sign out → redirected to `/login`, token cleared

- [ ] **Step 5: Final commit**

```bash
git add apps/web
git commit -m "feat: InclusiveAlert frontend dashboard — complete"
```
