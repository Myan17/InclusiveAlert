"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"

// Static export can't run a server-side redirect(), so route on the client:
// signed-in users go to the dashboard, everyone else to login.
export default function Root() {
  const { token } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    router.replace(token ? "/dashboard" : "/login")
  }, [token, router])

  return null
}
