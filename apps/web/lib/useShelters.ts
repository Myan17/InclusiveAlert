// lib/useShelters.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { useMapStore } from "@/store/mapStore"
import type { Shelter } from "@/lib/types"

// Houston demo fallback — used when geolocation is unavailable
const DEMO_LAT = 29.7604
const DEMO_LON = -95.3698

export function useShelters() {
  const token = useAuthStore((s) => s.token)
  const { userLat, userLon } = useMapStore()

  // Use actual location if available, otherwise fall back to demo coords
  const lat = userLat ?? DEMO_LAT
  const lon = userLon ?? DEMO_LON

  return useQuery<Shelter[]>({
    queryKey: ["shelters", lat, lon],
    queryFn: () => api.shelters.ranked(token!, lat, lon),
    enabled: !!token,
    refetchInterval: 60_000,
    staleTime: 55_000,
  })
}
