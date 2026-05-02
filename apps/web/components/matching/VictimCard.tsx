// components/matching/VictimCard.tsx
"use client"
import { Card, CardContent } from "@/components/ui/card"
import type { VictimSummary } from "@/lib/types"
import { Phone, MessageSquare, Hand, Zap, Dog, AlertTriangle } from "lucide-react"

const NEED_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  deaf:               { label: "Deaf / HoH",    icon: "🧏", color: "bg-purple-950/60 text-purple-300 border-purple-700/40" },
  blind:              { label: "Blind / LV",     icon: "👁️", color: "bg-blue-950/60 text-blue-300 border-blue-700/40" },
  mobility_wheelchair:{ label: "Wheelchair",     icon: "♿", color: "bg-cyan-950/60 text-cyan-300 border-cyan-700/40" },
  power_dependent:    { label: "Power Dep.",     icon: "⚡", color: "bg-yellow-950/60 text-yellow-300 border-yellow-700/40" },
  cognitive:          { label: "Cognitive",      icon: "🧠", color: "bg-pink-950/60 text-pink-300 border-pink-700/40" },
  chronic_illness:    { label: "Medical",        icon: "🏥", color: "bg-red-950/60 text-red-300 border-red-700/40" },
}

const COMM_ICONS: Record<string, string> = {
  asl: "🧏", text: "💬", voice: "📞", haptic: "📳",
}

function UrgencyBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? "bg-red-500" : pct >= 40 ? "bg-orange-500" : "bg-yellow-500"
  const label = pct >= 70 ? "High" : pct >= 40 ? "Medium" : "Low"
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-[10px] font-bold w-12 text-right ${
        pct >= 70 ? "text-red-400" : pct >= 40 ? "text-orange-400" : "text-yellow-400"
      }`}>{label} {pct}%</span>
    </div>
  )
}

interface VictimCardProps {
  victim: VictimSummary
  rank: number
}

export function VictimCard({ victim, rank }: VictimCardProps) {
  const location = [victim.location_city, victim.location_state, victim.location_zip]
    .filter(Boolean).join(", ") || "Location not set"

  const shortId = victim.user_id.slice(0, 6)

  return (
    <Card
      className="bg-card border-border border-l-4 border-l-red-500/60"
      role="article"
      aria-label={`Victim ${rank} needing assistance`}
    >
      <CardContent className="p-4 flex flex-col gap-2.5">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground mb-0.5">
              <span>#{rank}</span>
              <span>·</span>
              <span>ID {shortId}…</span>
              <span>·</span>
              <span>📍 {location}</span>
            </div>
            <p className="text-sm font-semibold text-foreground">
              {victim.email.split("@")[0]}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            {victim.power_dependency && (
              <span className="flex items-center gap-1 text-[9px] px-1.5 py-0.5 rounded-full bg-yellow-900/60 text-yellow-300 border border-yellow-700/40 font-bold animate-pulse">
                <Zap className="h-2.5 w-2.5" /> POWER CRITICAL
              </span>
            )}
            {victim.service_animal && (
              <span className="flex items-center gap-1 text-[9px] px-1.5 py-0.5 rounded-full bg-green-900/60 text-green-300 border border-green-700/40">
                <Dog className="h-2.5 w-2.5" /> Service Animal
              </span>
            )}
          </div>
        </div>

        {/* Urgency */}
        <div>
          <p className="text-[9px] text-muted-foreground uppercase tracking-widest mb-1">Urgency</p>
          <UrgencyBar score={victim.urgency_score} />
        </div>

        {/* Needs */}
        {victim.disability_needs.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {victim.disability_needs.map((need) => {
              const cfg = NEED_LABELS[need]
              if (!cfg) return null
              return (
                <span
                  key={need}
                  className={`flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded border font-medium ${cfg.color}`}
                >
                  {cfg.icon} {cfg.label}
                </span>
              )
            })}
          </div>
        )}

        {/* Communication modes */}
        {victim.communication_modes.length > 0 && (
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <MessageSquare className="h-3 w-3 shrink-0" />
            <span>Reaches via: </span>
            <span className="text-foreground font-medium">
              {victim.communication_modes.map((m) => COMM_ICONS[m] ?? m).join("  ")}
              {" "}{victim.communication_modes.join(", ")}
            </span>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-2 pt-1 border-t border-border/50">
          <button className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-blue-600/20 text-blue-300 border border-blue-600/30 text-xs font-medium hover:bg-blue-600/30 transition-colors">
            <Phone className="h-3 w-3" /> Contact
          </button>
          <button className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-green-600/20 text-green-300 border border-green-600/30 text-xs font-medium hover:bg-green-600/30 transition-colors">
            <AlertTriangle className="h-3 w-3" /> Accept Assignment
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
