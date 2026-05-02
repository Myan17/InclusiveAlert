// lib/useMatching.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { useMapStore } from "@/store/mapStore"
import type { MatchAssignmentResponse } from "@/lib/types"

const DEMO_LAT = 29.7604
const DEMO_LON = -95.3698

export function useMatching() {
  const token = useAuthStore((s) => s.token)
  const { userLat, userLon } = useMapStore()

  const lat = userLat ?? DEMO_LAT
  const lon = userLon ?? DEMO_LON

  return useQuery<MatchAssignmentResponse>({
    queryKey: ["matching", lat, lon],
    queryFn: () => api.matching.assign(token!, lat, lon),
    enabled: !!token,
    refetchInterval: 60_000,
    staleTime: 55_000,
  })
}
