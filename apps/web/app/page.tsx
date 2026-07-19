"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"

// Static export can't run a server-side redirect(), so route on the client:
// signed-in users go to the dashboard, everyone else to login.
export default function Root() {
  const { token, hasHydrated } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!hasHydrated) return
    router.replace(token ? "/dashboard" : "/login")
  }, [hasHydrated, token, router])

  return null
}
