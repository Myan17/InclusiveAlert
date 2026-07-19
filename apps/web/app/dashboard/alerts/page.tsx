// app/dashboard/alerts/page.tsx
"use client"
import { Bell } from "lucide-react"
import { useAlerts } from "@/lib/useAlerts"
import { AlertCard } from "@/components/alerts/AlertCard"
import { useMapStore } from "@/store/mapStore"
import { Skeleton } from "@/components/ui/skeleton"

function StatCard({ label, value, iconColor }: { label: string; value: number | string; iconColor: string }) {
  return (
    <div className="flex-1 rounded-xl border border-border bg-card px-5 py-4">
      <div className="flex items-center gap-2 mb-1.5">
        <Bell className={`h-4 w-4 ${iconColor}`} />
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <p className="text-3xl font-bold text-foreground">{value}</p>
    </div>
  )
}

export default function AlertsPage() {
  const { data: alerts = [], isLoading } = useAlerts()
  const { selectedAlertId } = useMapStore()

  const extremeCount = alerts.filter((a) => a.severity === "Extreme").length
  const severeCount  = alerts.filter((a) => a.severity === "Severe").length

  return (
    <div className="flex flex-col h-full">
      {/* Stat header — two summary cards */}
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex gap-3">
          <StatCard label="Active Alerts" value={alerts.length} iconColor="text-red-400" />
          <StatCard label="Severe / Extreme" value={severeCount + extremeCount} iconColor="text-yellow-400" />
        </div>
      </div>

      {/* Alert list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-2.5">
        {isLoading && Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-xl" />
        ))}
        {!isLoading && alerts.length === 0 && (
          <div className="flex flex-col items-center justify-center h-48 text-muted-foreground gap-3">
            <div className="h-16 w-16 rounded-full bg-muted/30 flex items-center justify-center">
              <Bell className="h-8 w-8 opacity-20" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium">No active alerts</p>
              <p className="text-xs text-muted-foreground/60 mt-0.5">Polling every 30 seconds</p>
            </div>
          </div>
        )}
        {alerts.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            selected={selectedAlertId === alert.id}
          />
        ))}
      </div>
    </div>
  )
}
