// components/map/HazardLayer.tsx
"use client"
import { useAlerts } from "@/lib/useAlerts"
import { useMapStore } from "@/store/mapStore"

// Note: HazardEvent geometry is stored in PostGIS and not returned by the API yet.
// This layer is scaffolded and will render polygons once the backend adds
// centroid/geometry fields to HazardEventResponse.
export function HazardLayer() {
  const { data: alerts = [] } = useAlerts()
  const { showHazards } = useMapStore()

  if (!showHazards) return null

  // No lat/lon centroid on HazardEvent yet — renders nothing until backend adds it.
  return null
}
