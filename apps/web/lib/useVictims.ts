// lib/useVictims.ts
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import type { VictimListResponse } from "@/lib/types"

export function useVictims() {
  const token = useAuthStore((s) => s.token)
  const role = useAuthStore((s) => s.role)
  return useQuery<VictimListResponse>({
    queryKey: ["victims"],
    queryFn: () => api.matching.victims(token!),
    enabled: !!token && (role === "respondent" || role === "authority"),
    refetchInterval: 30_000,
    staleTime: 25_000,
  })
}
