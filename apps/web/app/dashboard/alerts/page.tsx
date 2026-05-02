// app/dashboard/alerts/page.tsx
"use client"
import { Bell, AlertTriangle, Clock, Radio } from "lucide-react"
import { useAlerts } from "@/lib/useAlerts"
import { AlertCard } from "@/components/alerts/AlertCard"
import { useMapStore } from "@/store/mapStore"
import { Skeleton } from "@/components/ui/skeleton"

function StatPill({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <div className={`flex-1 rounded-xl border p-3 flex flex-col gap-1 ${color}`}>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-[10px] text-muted-foreground leading-tight">{label}</p>
    </div>
  )
}

export default function AlertsPage() {
  const { data: alerts = [], isLoading, dataUpdatedAt } = useAlerts()
  const { selectedAlertId } = useMapStore()

  const extremeCount  = alerts.filter((a) => a.severity === "Extreme").length
  const severeCount   = alerts.filter((a) => a.severity === "Severe").length
  const imminentCount = alerts.filter((a) => a.urgency === "Immediate").length
  const lastUpdate    = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-red-900/40 border border-red-700/40 flex items-center justify-center">
              <Bell className="h-3.5 w-3.5 text-red-400" />
            </div>
            <h1 className="text-sm font-bold text-foreground">Active Alerts</h1>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Radio className="h-3 w-3 text-green-400 animate-pulse" />
            <span>Updated {lastUpdate}</span>
          </div>
        </div>

        {/* Stat pills */}
        <div className="flex gap-2">
          <StatPill label="Total Active" value={alerts.length} color="bg-card border-border" />
          <StatPill label="Extreme" value={extremeCount} color="bg-red-950/30 border-red-800/40" />
          <StatPill label="Severe" value={severeCount} color="bg-orange-950/30 border-orange-800/40" />
          <StatPill label="Immediate" value={imminentCount} color="bg-yellow-950/30 border-yellow-800/40" />
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
