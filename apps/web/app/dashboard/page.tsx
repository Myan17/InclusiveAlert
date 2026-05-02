"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"

export default function DashboardHome() {
  const { role } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (role === "respondent") router.replace("/dashboard/matching")
    else router.replace("/dashboard/alerts")
  }, [role, router])

  return null
}
