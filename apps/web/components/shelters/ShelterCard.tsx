// components/shelters/ShelterCard.tsx
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Shelter } from "@/lib/types"
import { Accessibility, Zap, Dog, Hand, MapPin } from "lucide-react"

interface ShelterCardProps {
  shelter: Shelter
  rank: number
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? "bg-green-500" : pct >= 40 ? "bg-yellow-500" : "bg-red-500"
  const label = pct >= 70 ? "Good match" : pct >= 40 ? "Partial match" : "Poor match"
  return (
    <div className="flex items-center gap-2">
      <div
        className="flex-1 h-2 bg-muted rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Shelter match score: ${pct}% — ${label}`}
      >
        <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-muted-foreground w-16 text-right">{pct}% match</span>
    </div>
  )
}

interface AccessBadgeProps {
  icon: React.ReactNode
  label: string
  color: string
  title: string
}

function AccessBadge({ icon, label, color, title }: AccessBadgeProps) {
  return (
    <span
      className={`flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded font-medium ${color}`}
      title={title}
      aria-label={title}
    >
      {icon}
      {label}
    </span>
  )
}

export function ShelterCard({ shelter, rank }: ShelterCardProps) {
  const occupancyPct = shelter.capacity && shelter.current_occupancy != null
    ? Math.round((shelter.current_occupancy / shelter.capacity) * 100)
    : null

  // Honest data: never fabricate accessibility. When every attribute is unknown,
  // say so and offer the phone rather than implying inaccessibility.
  const accessUnconfirmed =
    shelter.wheelchair_accessible === null &&
    shelter.ada_compliant === null &&
    shelter.generator_onsite === null &&
    shelter.asl_support === null
  const sourceLabel = shelter.verified_by
    ? "✓ Verified"
    : shelter.source === "fema_nss"
    ? "FEMA NSS"
    : shelter.source

  return (
    <Card
      className="bg-card border-border"
      role="article"
      aria-label={`Shelter ${rank}: ${shelter.name}`}
    >
      <CardContent className="p-4 flex flex-col gap-2">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground mb-0.5">
              <MapPin className="h-3 w-3 shrink-0" />
              <span>#{rank} · {shelter.distance_km.toFixed(1)} km away</span>
              <span className="px-1 rounded bg-muted/60 text-muted-foreground/80" title={`Data source: ${sourceLabel}`}>
                {sourceLabel}
              </span>
            </div>
            <p className="text-sm font-semibold text-foreground leading-tight">{shelter.name}</p>
            {shelter.address && (
              <p className="text-xs text-muted-foreground mt-0.5">{shelter.address}</p>
            )}
          </div>
          <Badge
            className={`text-[10px] shrink-0 ${
              shelter.status === "open"
                ? "bg-green-900 text-green-300 border-green-700"
                : shelter.status === "full"
                ? "bg-orange-900 text-orange-300 border-orange-700"
                : "bg-red-900 text-red-300 border-red-700"
            }`}
          >
            {shelter.status}
          </Badge>
        </div>

        {/* Match score */}
        <ScoreBar score={shelter.shelter_score} />

        {/* Accessibility badges */}
        <div className="flex flex-wrap gap-1" role="list" aria-label="Accessibility features">
          {shelter.wheelchair_accessible === true && (
            <AccessBadge
              icon={<Accessibility className="h-3 w-3" />}
              label="Wheelchair"
              color="bg-blue-950 text-blue-300"
              title="Wheelchair accessible entrance and facilities"
            />
          )}
          {shelter.ada_compliant === true && (
            <AccessBadge
              icon={<span className="font-bold text-[9px]">ADA</span>}
              label="Compliant"
              color="bg-purple-950 text-purple-300"
              title="Fully ADA compliant — accessible restrooms, ramps, signage"
            />
          )}
          {shelter.generator_onsite === true && (
            <AccessBadge
              icon={<Zap className="h-3 w-3" />}
              label="Generator"
              color="bg-yellow-950 text-yellow-300"
              title="Backup generator — critical for power-dependent medical equipment"
            />
          )}
          {shelter.asl_support === true && (
            <AccessBadge
              icon={<Hand className="h-3 w-3" />}
              label="ASL Staff"
              color="bg-indigo-950 text-indigo-300"
              title="ASL-fluent staff on site for Deaf and Hard of Hearing individuals"
            />
          )}
          {shelter.pet_policy === "pets_allowed" && (
            <AccessBadge
              icon={<Dog className="h-3 w-3" />}
              label="Pets OK"
              color="bg-green-950 text-green-300"
              title="Pets and service animals welcome"
            />
          )}
          {shelter.pet_policy === "service_animals_only" && (
            <AccessBadge
              icon={<Dog className="h-3 w-3" />}
              label="Service Animals"
              color="bg-teal-950 text-teal-300"
              title="Service animals only (no pets)"
            />
          )}
        </div>

        {/* Honest unknown state — never imply accessibility we don't have. */}
        {accessUnconfirmed && (
          <p className="text-[10px] text-muted-foreground italic">
            Accessibility unconfirmed —{" "}
            {shelter.phone ? (
              <>call to verify: <a href={`tel:${shelter.phone}`} className="underline">{shelter.phone}</a></>
            ) : (
              "call ahead to confirm"
            )}
          </p>
        )}

        {/* Capacity bar */}
        {shelter.capacity !== null && occupancyPct !== null && (
          <div className="flex flex-col gap-1">
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>Capacity</span>
              <span>{shelter.current_occupancy?.toLocaleString()} / {shelter.capacity?.toLocaleString()}</span>
            </div>
            <div className="h-1 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  occupancyPct >= 90 ? "bg-red-500" : occupancyPct >= 70 ? "bg-yellow-500" : "bg-green-500"
                }`}
                style={{ width: `${Math.min(100, occupancyPct)}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
