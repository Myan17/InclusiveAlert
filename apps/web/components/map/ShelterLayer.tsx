// components/map/ShelterLayer.tsx
"use client"
import { useEffect } from "react"
import { CircleMarker, Popup, Tooltip, useMap } from "react-leaflet"
import { useShelters } from "@/lib/useShelters"
import { useMapStore } from "@/store/mapStore"
import type { Shelter } from "@/lib/types"
import L from "leaflet"

function scoreColor(score: number, status: string): string {
  if (status === "full")   return "#f97316"
  if (status === "closed") return "#6b7280"
  if (score >= 0.7) return "#22c55e"
  if (score >= 0.4) return "#eab308"
  return "#ef4444"
}

function accessIcons(shelter: Shelter): string {
  const icons: string[] = []
  if (shelter.wheelchair_accessible)            icons.push("♿")
  if (shelter.generator_onsite)                 icons.push("⚡")
  if (shelter.asl_support)                      icons.push("🧏")
  if (shelter.ada_compliant)                    icons.push("ADA")
  if (shelter.pet_policy === "pets_allowed")    icons.push("🐕")
  if (shelter.pet_policy === "service_animals_only") icons.push("🦮")
  return icons.join("  ")
}

// Auto-fit map to show all shelter pins
function FitBounds({ shelters }: { shelters: Shelter[] }) {
  const map = useMap()
  useEffect(() => {
    const pts = shelters.filter((s) => s.lat !== null && s.lon !== null)
    if (pts.length === 0) return
    const bounds = L.latLngBounds(pts.map((s) => [s.lat!, s.lon!]))
    map.fitBounds(bounds, { padding: [60, 60], maxZoom: 12 })
  }, [map, shelters.length]) // eslint-disable-line react-hooks/exhaustive-deps
  return null
}

export function ShelterLayer() {
  const { data: shelters = [] } = useShelters()
  const { showShelters } = useMapStore()

  if (!showShelters) return null

  const visible = shelters.filter((s) => s.lat !== null && s.lon !== null)

  return (
    <>
      <FitBounds shelters={visible} />
      {visible.map((shelter, i) => {
        const color = scoreColor(shelter.shelter_score, shelter.status)
        const pct = Math.round(shelter.shelter_score * 100)
        const occupancyPct = shelter.capacity && shelter.current_occupancy != null
          ? Math.min(100, Math.round((shelter.current_occupancy / shelter.capacity) * 100))
          : null

        return (
          <CircleMarker
            key={`shelter-${i}`}
            center={[shelter.lat!, shelter.lon!]}
            radius={13}
            pathOptions={{
              fillColor: color,
              fillOpacity: 0.92,
              color: "#ffffff",
              weight: 2.5,
            }}
          >
            {/* Permanent short label above pin */}
            <Tooltip
              permanent
              direction="top"
              offset={[0, -15]}
            >
              <div style={{
                background: color,
                color: "#fff",
                padding: "2px 6px",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: "700",
                whiteSpace: "nowrap",
                boxShadow: "0 1px 4px rgba(0,0,0,0.4)",
                border: "1px solid rgba(255,255,255,0.3)",
              }}>
                {shelter.name.length > 18 ? shelter.name.slice(0, 17) + "…" : shelter.name}
                {" · "}{pct}%
              </div>
            </Tooltip>

            {/* Click popup */}
            <Popup maxWidth={270} minWidth={220}>
              <div style={{ fontFamily: "system-ui, sans-serif", fontSize: "12px", lineHeight: "1.6" }}>
                <div style={{ fontWeight: "700", fontSize: "13px", marginBottom: "2px" }}>
                  {shelter.name}
                </div>
                {shelter.address && (
                  <div style={{ color: "#777", fontSize: "11px", marginBottom: "6px" }}>
                    📍 {shelter.address}
                  </div>
                )}

                {/* Status row */}
                <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "6px", flexWrap: "wrap" }}>
                  <span style={{
                    background: color, color: "#fff",
                    padding: "2px 8px", borderRadius: "4px",
                    fontSize: "11px", fontWeight: "700", textTransform: "uppercase",
                  }}>
                    {shelter.status}
                  </span>
                  <span style={{ fontSize: "11px", color: "#444" }}>
                    Match: <strong style={{ color }}>{pct}%</strong>
                  </span>
                  <span style={{ fontSize: "11px", color: "#666" }}>
                    {shelter.distance_km.toFixed(1)} km away
                  </span>
                </div>

                {/* Capacity */}
                {shelter.capacity && (
                  <div style={{ marginBottom: "8px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "#666", marginBottom: "3px" }}>
                      <span>Capacity</span>
                      <span>{shelter.current_occupancy ?? "?"} / {shelter.capacity.toLocaleString()}</span>
                    </div>
                    <div style={{ height: "6px", background: "#e5e7eb", borderRadius: "3px", overflow: "hidden" }}>
                      <div style={{
                        height: "100%",
                        width: `${occupancyPct ?? 0}%`,
                        background: (occupancyPct ?? 0) >= 90 ? "#ef4444" : (occupancyPct ?? 0) >= 70 ? "#f97316" : "#22c55e",
                        borderRadius: "3px",
                        transition: "width 0.3s",
                      }} />
                    </div>
                  </div>
                )}

                {/* Accessibility */}
                <div style={{ fontSize: "14px", letterSpacing: "3px", marginBottom: "4px" }}>
                  {accessIcons(shelter) || "—"}
                </div>
                <div style={{ fontSize: "10px", color: "#aaa", borderTop: "1px solid #eee", paddingTop: "4px" }}>
                  ♿ Wheelchair · ⚡ Generator · 🧏 ASL · 🐕 Pets · 🦮 Service Animals
                </div>
              </div>
            </Popup>
          </CircleMarker>
        )
      })}
    </>
  )
}
