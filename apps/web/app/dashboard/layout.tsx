"use client"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"
import { Sidebar } from "@/components/layout/Sidebar"

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
      {/* Data panel — 40% width, scrollable */}
      <div className="w-[40%] flex flex-col h-screen overflow-y-auto border-r border-border">
        {children}
      </div>
      {/* Map panel placeholder — will be filled by Task 5 */}
      <div className="flex-1 h-screen bg-muted flex items-center justify-center text-muted-foreground text-sm">
        Map loading…
      </div>
    </div>
  )
}
