// lib/useAlerts.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import type { HazardEvent } from "@/lib/types"

export function useAlerts() {
  const token = useAuthStore((s) => s.token)
  return useQuery<HazardEvent[]>({
    queryKey: ["alerts"],
    queryFn: () => api.alerts.active(token!),
    enabled: !!token,
    refetchInterval: 30_000,
    staleTime: 25_000,
  })
}
