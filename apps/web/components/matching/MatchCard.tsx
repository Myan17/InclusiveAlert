// components/matching/MatchCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import type { MatchResult } from "@/lib/types"
import { Hand, Stethoscope, Accessibility, Dog, Shield } from "lucide-react"

interface MatchCardProps {
  result: MatchResult
  rank: number
}

function MiniBar({ value, label }: { value: number; label: string }) {
  const pct = Math.round(value * 100)
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-yellow-500" : "bg-red-400"
  return (
    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
      <span className="w-28 truncate">{label}</span>
      <div className="flex-1 h-1 bg-muted rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-7 text-right">{pct}%</span>
    </div>
  )
}

// Infer skill badges from score breakdown + respondent_id pattern
// In a real app these would come from the API response
function SkillBadges({ result }: { result: MatchResult }) {
  const badges = []
  if (result.breakdown.communication_fit >= 0.8) {
    badges.push(
      <span key="asl" className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-purple-950 text-purple-300" title="ASL communication available">
        <Hand className="h-3 w-3" /> ASL
      </span>
    )
  }
  if (result.breakdown.skill_fit >= 0.8) {
    badges.push(
      <span key="med" className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-red-950 text-red-300" title="Medical skills">
        <Stethoscope className="h-3 w-3" /> Medical
      </span>
    )
  }
  if (result.breakdown.proximity >= 0.8) {
    badges.push(
      <span key="near" className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-green-950 text-green-300" title="Nearby responder">
        <Accessibility className="h-3 w-3" /> Nearby
      </span>
    )
  }
  if (result.breakdown.trust_tier >= 0.5) {
    badges.push(
      <span key="verified" className="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300" title="Background verified">
        <Shield className="h-3 w-3" /> Verified
      </span>
    )
  }
  return badges.length > 0 ? (
    <div className="flex flex-wrap gap-1">{badges}</div>
  ) : null
}

export function MatchCard({ result, rank }: MatchCardProps) {
  const pct = Math.round(result.score * 100)
  const shortId = result.respondent_id.slice(0, 8)
  const scoreColor = pct >= 70 ? "text-green-400" : pct >= 40 ? "text-yellow-400" : "text-red-400"
  const barColor = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-yellow-500" : "bg-red-500"

  return (
    <Card
      className="bg-card border-border"
      role="article"
      aria-label={`Match ${rank}: Respondent ${shortId}, ${pct}% compatibility`}
    >
      <CardContent className="p-4 flex flex-col gap-2">
        {/* Header */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1">
            <span className="text-[10px] text-muted-foreground block">
              #{rank} · Respondent {shortId}…
            </span>
            <div className="flex items-center gap-2 mt-1">
              <div
                className="h-2 flex-1 max-w-[120px] bg-muted rounded-full overflow-hidden"
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Match score ${pct}%`}
              >
                <div className={`h-full ${barColor} rounded-full`} style={{ width: `${pct}%` }} />
              </div>
              <span className={`text-base font-bold ${scoreColor}`}>{pct}%</span>
            </div>
          </div>
        </div>

        {/* Skill badges inferred from breakdown */}
        <SkillBadges result={result} />

        {/* Score breakdown accordion */}
        <Accordion>
          <AccordionItem value="breakdown" className="border-none">
            <AccordionTrigger className="text-[10px] text-muted-foreground py-1 hover:no-underline">
              Score breakdown
            </AccordionTrigger>
            <AccordionContent className="flex flex-col gap-1.5 pb-1">
              <MiniBar value={result.breakdown.proximity} label="📍 Proximity" />
              <MiniBar value={result.breakdown.skill_fit} label="🩺 Skill Fit" />
              <MiniBar value={result.breakdown.availability} label="✅ Availability" />
              <MiniBar value={result.breakdown.communication_fit} label="🧏 Communication" />
              <MiniBar value={result.breakdown.trust_tier} label="🛡 Trust Tier" />
              <MiniBar value={result.breakdown.route_safety} label="🛣 Route Safety" />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  )
}
