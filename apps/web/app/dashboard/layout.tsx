"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"
import { Sidebar } from "@/components/layout/Sidebar"
import { MapPanel } from "@/components/map/MapPanel"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!token) router.replace("/login")
  }, [token, router])

  if (!token) return null

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="w-[40%] flex flex-col h-screen overflow-y-auto border-r border-border">
        {children}
      </div>
      <div className="flex-1 h-screen">
        <MapPanel />
      </div>
    </div>
  )
}
