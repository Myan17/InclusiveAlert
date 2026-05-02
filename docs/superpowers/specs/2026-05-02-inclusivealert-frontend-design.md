# InclusiveAlert Frontend Dashboard — Design Spec
Date: 2026-05-02

## Overview

A professional, desktop-first emergency operations dashboard for InclusiveAlert. Role-aware: the same app renders a different view depending on whether the logged-in user is a victim, respondent, or authority. Built in `apps/web/` inside the existing monorepo.

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Framework | Next.js 14 (App Router) | Industry standard, great DX |
| Styling | Tailwind CSS + shadcn/ui | Best-looking component library, Radix primitives |
| Map | React Leaflet + OpenStreetMap | Free, no API key, street-level detail |
| Data fetching | TanStack Query (React Query) | Built-in polling, caching, loading states |
| Client state | Zustand | Lightweight — selected alert, map center, user location |
| Auth | JWT context | JWT already issued by FastAPI backend |

All API calls target `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). No BFF — Next.js talks directly to FastAPI.

## Layout: Split-Panel Command Center

```
┌─────────────────────────────────────────────────────────────┐
│ SIDEBAR (240px fixed) │ DATA PANEL (40%)  │  MAP (60%)      │
│                       │                   │                  │
│  Logo                 │  [stat cards row] │  Leaflet map     │
│  ─────────────        │  ─────────────── │  full height     │
│  Dashboard            │  Alert / Shelter  │                  │
│  Alerts               │  / Match cards    │  hazard polygons │
│  Shelters             │  scrollable list  │  shelter pins    │
│  Matching             │                   │  respondent pins │
│  Profile              │                   │                  │
│  ─────────────        │                   │                  │
│  [user badge]         │                   │                  │
│  [role pill]          │                   │                  │
│  Logout               │                   │                  │
└─────────────────────────────────────────────────────────────┘
```

- Sidebar: fixed 240px, dark background, logo at top, nav links, user info + role badge at bottom
- Data panel: scrollable, contains stat summary row + card list
- Map panel: Leaflet, fills remaining viewport height, no scroll

## Color System

Dark theme throughout (emergency ops standard).

| Token | Color | Usage |
|-------|-------|-------|
| bg-background | #0f1117 | App background |
| bg-card | #1a1d27 | Card surfaces |
| bg-sidebar | #13151f | Sidebar |
| Extreme severity | red-500 | Alert badges, map polygon fill |
| Severe | orange-500 | Alert badges, map polygon fill |
| Moderate | yellow-500 | Alert badges |
| Minor | blue-400 | Alert badges |
| Available | green-500 | Respondent status |
| On break | yellow-500 | Respondent status |

## Auth Flow

- `/login` — email + password → POST /auth/login → store JWT in localStorage
- `/register` — email + password + role → POST /auth/register
- All `/dashboard/*` routes redirect to `/login` if no JWT
- JWT decoded client-side to read `role` and `email`; stored in Zustand auth store

## Role-Specific Views

### Victim View
**Stat row:** Active alerts near me · Nearest shelter (km) · Available respondents

**Data panel — two tabs:**
- *Alerts tab:* AlertCards for active hazards in their area, sorted by severity
- *Shelters tab:* ShelterCards ranked by ShelterScore, showing distance + accessibility icons

**Map:** Hazard zone polygons (colored by severity) + shelter pins (green=high score, yellow=mid, red=low). User location blue dot. Clicking a shelter pin highlights its card.

### Respondent View
**Stat row:** My status toggle (available / on_break / unavailable) · Active assignments · Trust tier

**Data panel:** MatchCards — victims assigned to them, with disability needs tags and distance.

**Map:** Victim location pins. Respondent's own location. Route line (placeholder).

### Authority View
**Stat row:** Total active alerts · Open shelters · Available respondents · Registered victims

**Data panel — three tabs:**
- *Alerts tab:* Full alerts table with severity, type, area, expires countdown
- *Respondents tab:* Respondent status board — availability, trust tier, skills
- *Shelters tab:* All ranked shelters with capacity utilization bar

**Map:** All hazard polygons + all shelter pins + all respondent pins. Full situational awareness.

## Data Flow

| Data | Endpoint | Poll interval |
|------|----------|---------------|
| Active alerts | GET /alerts/active | 30s |
| Ranked shelters | GET /shelters/ranked?lat=&lon= | 60s |
| Matched respondents | GET /matching/assign?lat=&lon= | 60s |
| My profile | GET /auth/me | on mount |

User lat/lon: browser `navigator.geolocation` on first load, stored in Zustand. If denied, prompt user to enter zip (no map pins, text-only fallback).

## Map Interactions

- Click hazard polygon → scroll data panel to matching AlertCard, highlight with ring
- Click shelter pin → Leaflet popup with name/score + scroll to ShelterCard
- Click respondent pin (authority only) → popup with name/skills/status
- Map layers toggle: hazard zones / shelters / respondents (checkboxes in map top-right corner)
- Map auto-centers on user location on first load, then free pan/zoom

## Components

### AlertCard
Severity badge (colored) · hazard type · area description · effective time · expires countdown timer · "View details" expand for full description + instructions

### ShelterCard
Name · distance badge · ShelterScore bar (0–1) · accessibility icons: ♿ wheelchair · ⚡ generator · 🐕 pets · ASL chip · capacity fill bar · address

### MatchCard
Respondent ID (anonymized) · MatchScore bar · skill tags · availability pill · distance · breakdown accordion (proximity / skill_fit / availability / trust_tier / communication_fit)

### Sidebar
Logo · nav links with active state · bottom section: avatar circle + email + role badge + logout button

## Folder Structure

```
apps/web/
  app/
    (auth)/
      login/page.tsx
      register/page.tsx
    dashboard/
      layout.tsx          ← Shell: sidebar + data panel + map panel
      page.tsx            ← Redirects to role-appropriate default tab
      alerts/page.tsx
      shelters/page.tsx
      matching/page.tsx
      profile/page.tsx
  components/
    map/
      MapPanel.tsx        ← Leaflet map, layer management
      HazardLayer.tsx     ← Polygon rendering
      ShelterLayer.tsx    ← Shelter markers
      RespondentLayer.tsx ← Respondent markers (authority only)
    alerts/AlertCard.tsx
    shelters/ShelterCard.tsx
    matching/MatchCard.tsx
    layout/
      Sidebar.tsx
      StatCard.tsx        ← Individual stat summary tile
  lib/
    api.ts               ← Typed fetch wrappers for all endpoints
    auth.ts              ← JWT store (Zustand) + decode
    useAlerts.ts         ← TanStack Query hook, 30s polling
    useShelters.ts       ← TanStack Query hook, 60s polling
    useMatching.ts       ← TanStack Query hook, 60s polling
  store/
    mapStore.ts          ← Selected alert, map center, user location (Zustand)
    authStore.ts         ← JWT, decoded user, role (Zustand)
```

## Out of Scope

- WebSocket / SSE real-time push (polling is sufficient for v1)
- Mobile layout (desktop-first; responsive is a v2 concern)
- Internationalization
- Dark/light mode toggle (dark only for v1)
- Push notifications (browser notification API — v2)
