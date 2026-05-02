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
          <div className="text-xs text-muted-foreground bg-muted/50 rounded-md px-3 py-2 border border-border">
            📍 Showing shelters near Houston, TX (demo). Allow location for results near you.
          </div>
        )}
        {isLoading &&
          Array.from({ length: 3 }).map((_, i) => (
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
