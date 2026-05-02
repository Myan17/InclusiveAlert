// app/dashboard/matching/page.tsx
"use client"
import { Users, Zap, Shield, Hand, AlertTriangle, UserCheck } from "lucide-react"
import { useMatching } from "@/lib/useMatching"
import { useVictims } from "@/lib/useVictims"
import { MatchCard } from "@/components/matching/MatchCard"
import { VictimCard } from "@/components/matching/VictimCard"
import { useMapStore } from "@/store/mapStore"
import { useAuthStore } from "@/store/authStore"
import { Skeleton } from "@/components/ui/skeleton"

// ── Victim view (for respondents / authority) ─────────────────────────────────

function RespondentMatchingView() {
  const { data, isLoading } = useVictims()
  const victims = data?.victims ?? []
  const powerCritical = victims.filter((v) => v.power_dependency).length
  const highUrgency   = victims.filter((v) => v.urgency_score >= 0.5).length
  const aslNeeded     = victims.filter((v) => v.disability_needs.includes("deaf")).length

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2 mb-3">
          <div className="h-7 w-7 rounded-lg bg-red-900/40 border border-red-700/40 flex items-center justify-center">
            <UserCheck className="h-3.5 w-3.5 text-red-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-foreground">Victims Needing Help</h1>
            <p className="text-[10px] text-muted-foreground">Sorted by urgency · Accept assignments to respond</p>
          </div>
        </div>

        <div className="flex gap-2">
          <div className="flex-1 rounded-xl border bg-card border-border p-3">
            <p className="text-2xl font-bold text-foreground">{data?.total ?? 0}</p>
            <p className="text-[10px] text-muted-foreground">Total</p>
          </div>
          <div className="flex-1 rounded-xl border bg-red-950/30 border-red-800/40 p-3">
            <p className="text-2xl font-bold text-red-400">{highUrgency}</p>
            <p className="text-[10px] text-muted-foreground">High Urgency</p>
          </div>
          <div className="flex-1 rounded-xl border bg-yellow-950/30 border-yellow-800/40 p-3">
            <p className="text-2xl font-bold text-yellow-400">{powerCritical}</p>
            <p className="text-[10px] text-muted-foreground">⚡ Power Dep.</p>
          </div>
          <div className="flex-1 rounded-xl border bg-purple-950/30 border-purple-800/40 p-3">
            <p className="text-2xl font-bold text-purple-400">{aslNeeded}</p>
            <p className="text-[10px] text-muted-foreground">🧏 ASL Needed</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-2.5">
        {isLoading && Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-36 w-full rounded-xl" />
        ))}
        {!isLoading && victims.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-3">
            <div className="h-16 w-16 rounded-full bg-muted/30 flex items-center justify-center">
              <Users className="h-8 w-8 opacity-20" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium">No victims registered yet</p>
              <p className="text-xs text-muted-foreground/60 mt-0.5">Victims appear when they create profiles</p>
            </div>
          </div>
        )}
        {victims.map((victim, i) => (
          <VictimCard key={victim.user_id} victim={victim} rank={i + 1} />
        ))}
      </div>
    </div>
  )
}

// ── Respondent view (for victims) ─────────────────────────────────────────────

function VictimMatchingView() {
  const { data, isLoading } = useMatching()
  const { userLat } = useMapStore()
  const results = data?.results ?? []
  const topScore      = results[0]?.score ?? 0
  const aslCount      = results.filter((r) => r.breakdown.communication_fit >= 0.8).length
  const verifiedCount = results.filter((r) => r.breakdown.trust_tier >= 0.5).length

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2 mb-3">
          <div className="h-7 w-7 rounded-lg bg-green-900/40 border border-green-700/40 flex items-center justify-center">
            <Users className="h-3.5 w-3.5 text-green-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-foreground">Matched Responders</h1>
            <p className="text-[10px] text-muted-foreground">Ranked by compatibility with your needs</p>
          </div>
        </div>

        <div className="flex gap-2">
          <div className="flex-1 rounded-xl border bg-card border-border p-3">
            <p className="text-2xl font-bold text-foreground">{data?.total ?? 0}</p>
            <p className="text-[10px] text-muted-foreground">Available</p>
          </div>
          <div className="flex-1 rounded-xl border bg-green-950/30 border-green-800/40 p-3">
            <p className="text-2xl font-bold text-green-400">{Math.round(topScore * 100)}%</p>
            <p className="text-[10px] text-muted-foreground">Best Match</p>
          </div>
          <div className="flex-1 rounded-xl border bg-purple-950/30 border-purple-800/40 p-3">
            <p className="text-2xl font-bold text-purple-400">{aslCount}</p>
            <p className="text-[10px] text-muted-foreground">🧏 ASL</p>
          </div>
          <div className="flex-1 rounded-xl border bg-blue-950/30 border-blue-800/40 p-3">
            <p className="text-2xl font-bold text-blue-400">{verifiedCount}</p>
            <p className="text-[10px] text-muted-foreground">✓ Verified</p>
          </div>
        </div>

        {!userLat && (
          <p className="text-[10px] text-muted-foreground mt-2 bg-muted/30 rounded-lg px-3 py-1.5 border border-border">
            📍 Showing matches near Houston, TX (demo). Allow location for results near you.
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-2.5">
        {isLoading && Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-28 w-full rounded-xl" />
        ))}
        {!isLoading && results.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-3">
            <div className="h-16 w-16 rounded-full bg-muted/30 flex items-center justify-center">
              <Users className="h-8 w-8 opacity-20" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium">No available respondents</p>
              <p className="text-xs text-muted-foreground/60 mt-0.5">Respondents appear when they set status to available</p>
            </div>
          </div>
        )}
        {results.map((result, i) => (
          <MatchCard key={result.respondent_id} result={result} rank={i + 1} />
        ))}
      </div>
    </div>
  )
}

// ── Root: role-aware ──────────────────────────────────────────────────────────

export default function MatchingPage() {
  const role = useAuthStore((s) => s.role)
  if (role === "respondent" || role === "authority") return <RespondentMatchingView />
  return <VictimMatchingView />
}
