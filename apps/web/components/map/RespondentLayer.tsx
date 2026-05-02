// components/map/RespondentLayer.tsx
"use client"
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
