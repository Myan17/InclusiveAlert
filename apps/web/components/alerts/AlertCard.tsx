// components/alerts/AlertCard.tsx
"use client"
import { useState } from "react"
import { formatDistanceToNow, parseISO } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import type { HazardEvent, Severity } from "@/lib/types"
import { useMapStore } from "@/store/mapStore"
import { Volume2, Hand, Zap, Accessibility, Dog, ChevronDown, ChevronUp, Pill } from "lucide-react"
import { AslModal } from "./AslModal"

const severityConfig: Record<Severity, { border: string; bg: string; badge: string; glow: string }> = {
  Extreme: { border: "border-l-red-500",    bg: "bg-red-950/30",    badge: "bg-red-900 text-red-200 border-red-700",    glow: "shadow-red-900/30" },
  Severe:  { border: "border-l-orange-500", bg: "bg-orange-950/30", badge: "bg-orange-900 text-orange-200 border-orange-700", glow: "shadow-orange-900/20" },
  Moderate:{ border: "border-l-yellow-500", bg: "bg-yellow-950/20", badge: "bg-yellow-900 text-yellow-200 border-yellow-700", glow: "" },
  Minor:   { border: "border-l-blue-400",   bg: "bg-blue-950/20",   badge: "bg-blue-900 text-blue-200 border-blue-700",   glow: "" },
  Unknown: { border: "border-l-muted",      bg: "",                 badge: "bg-muted text-muted-foreground border-border", glow: "" },
}

const hazardEmoji: Record<string, string> = {
  tornado_warning:        "🌪️",
  flash_flood_warning:    "🌊",
  excessive_heat_warning: "🌡️",
  earthquake:             "🫨",
  hurricane_watch:        "🌀",
  winter_storm_warning:   "❄️",
  wildfire:               "🔥",
}

function parseAccessibilityTags(instruction: string | null) {
  if (!instruction) return { hasAsl: false, hasWheelchair: false, hasPower: false, hasDog: false, hasMed: false }
  return {
    hasAsl:        instruction.includes("🧏") || instruction.toLowerCase().includes("asl"),
    hasWheelchair: instruction.includes("♿") || instruction.toLowerCase().includes("wheelchair"),
    hasPower:      instruction.includes("⚡") || instruction.toLowerCase().includes("power-dependent"),
    hasDog:        instruction.includes("🐕") || instruction.toLowerCase().includes("service animal"),
    hasMed:        instruction.includes("💊") || instruction.toLowerCase().includes("medication"),
  }
}

function speakAlert(text: string) {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return
  window.speechSynthesis.cancel()
  const utt = new SpeechSynthesisUtterance(text)
  utt.rate = 0.88
  utt.pitch = 1
  window.speechSynthesis.speak(utt)
}

function cleanInstruction(raw: string | null): string | null {
  if (!raw) return null
  return raw.replace(/🧏[^|]*\|\s*/g, "").replace(/bit\.ly\/\S+/g, "").trim() || null
}

interface AlertCardProps {
  alert: HazardEvent
  selected?: boolean
}

export function AlertCard({ alert, selected }: AlertCardProps) {
  const setSelectedAlert = useMapStore((s) => s.setSelectedAlert)
  const [showAsl, setShowAsl] = useState(false)
  const [expanded, setExpanded] = useState(false)
  const sev = alert.severity as Severity
  // Defensive: never let an unexpected severity key crash the whole dashboard.
  const cfg = severityConfig[sev] ?? severityConfig.Unknown
  const tags = parseAccessibilityTags(alert.instruction)
  const instruction = cleanInstruction(alert.instruction)
  const emoji = hazardEmoji[alert.hazard_type] ?? "⚠️"
  const speakText = `${alert.severity} alert. ${alert.headline ?? alert.hazard_type}. ${instruction ?? ""}`

  return (
    <>
      {showAsl && (
        <AslModal
          hazardType={alert.hazard_type}
          headline={alert.headline ?? alert.hazard_type}
          onClose={() => setShowAsl(false)}
        />
      )}

      <Card
        id={`alert-${alert.id}`}
        onClick={() => { setSelectedAlert(alert.id); setExpanded((e) => !e) }}
        role="button"
        tabIndex={0}
        aria-label={`${alert.severity} alert: ${alert.headline ?? alert.hazard_type}`}
        aria-expanded={expanded}
        onKeyDown={(e) => e.key === "Enter" && setSelectedAlert(alert.id)}
        className={`border border-border/60 border-l-4 ${cfg.border} ${cfg.bg} cursor-pointer transition-all duration-200 shadow-lg ${cfg.glow} ${
          selected ? "ring-2 ring-blue-500 ring-offset-1 ring-offset-background" : "hover:border-border hover:brightness-110"
        }`}
      >
        <CardContent className="p-4 flex flex-col gap-2.5">
          {/* Header */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-start gap-2 flex-1 min-w-0">
              <span className="text-xl shrink-0 mt-0.5" aria-hidden="true">{emoji}</span>
              <span className="text-sm font-semibold text-foreground leading-snug">
                {alert.headline ?? alert.hazard_type.replace(/_/g, " ")}
              </span>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <Badge className={`text-[10px] border font-bold ${cfg.badge}`}>
                {alert.severity}
              </Badge>
              {expanded
                ? <ChevronUp className="h-3.5 w-3.5 text-muted-foreground" />
                : <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
              }
            </div>
          </div>

          {/* Area */}
          {alert.area_description && (
            <p className="text-xs text-muted-foreground pl-7">{alert.area_description}</p>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-1.5 flex-wrap pl-7">
            {tags.hasAsl && (
              <button
                onClick={(e) => { e.stopPropagation(); setShowAsl(true) }}
                className="flex items-center gap-1 text-[10px] px-2 py-1 rounded-md bg-purple-900/50 text-purple-300 hover:bg-purple-800/70 transition-colors border border-purple-700/50 font-medium"
                aria-label="Watch ASL video"
              >
                <Hand className="h-3 w-3" /> ASL Video
              </button>
            )}
            <button
              onClick={(e) => { e.stopPropagation(); speakAlert(speakText) }}
              className="flex items-center gap-1 text-[10px] px-2 py-1 rounded-md bg-blue-900/50 text-blue-300 hover:bg-blue-800/70 transition-colors border border-blue-700/50 font-medium"
              aria-label="Read aloud"
            >
              <Volume2 className="h-3 w-3" /> Read Aloud
            </button>
            {tags.hasWheelchair && <span className="text-[11px] px-1.5 py-0.5 rounded bg-blue-950/60 text-blue-300 border border-blue-800/40" title="Wheelchair guidance">♿</span>}
            {tags.hasPower      && <span className="text-[11px] px-1.5 py-0.5 rounded bg-yellow-950/60 text-yellow-300 border border-yellow-800/40" title="Power-dependent guidance">⚡</span>}
            {tags.hasDog        && <span className="text-[11px] px-1.5 py-0.5 rounded bg-green-950/60 text-green-300 border border-green-800/40" title="Service animal guidance">🐕</span>}
            {tags.hasMed        && <span className="text-[11px] px-1.5 py-0.5 rounded bg-pink-950/60 text-pink-300 border border-pink-800/40" title="Medication guidance">💊</span>}
          </div>

          {/* Meta row */}
          <div className="flex items-center justify-between text-[10px] text-muted-foreground pl-7">
            <span className="uppercase tracking-wide">{alert.source} · {alert.hazard_type.replace(/_/g, " ")}</span>
            <span className={alert.expires_at && new Date(alert.expires_at) < new Date(Date.now() + 3600000) ? "text-orange-400 font-medium" : ""}>
              {alert.expires_at
                ? `Expires ${formatDistanceToNow(parseISO(alert.expires_at), { addSuffix: true })}`
                : "No expiry"}
            </span>
          </div>

          {/* Expanded instruction */}
          {expanded && instruction && (
            <div className="border-t border-border/50 pt-2.5 pl-7 animate-in slide-in-from-top-1 duration-200">
              <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-widest mb-1.5">
                Accessibility Instructions
              </p>
              <div className="flex flex-col gap-1.5">
                {instruction.split(" · ").filter(Boolean).map((line, i) => (
                  <div key={i} className="flex items-start gap-1.5 text-xs text-blue-200/90 leading-relaxed">
                    <span className="shrink-0 mt-0.5">›</span>
                    <span>{line.trim()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  )
}
