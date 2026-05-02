"use client"
import dynamic from "next/dynamic"

const MapInner = dynamic(
  () => import("./MapInner").then((m) => ({ default: m.MapInner })),
  {
    ssr: false,
    loading: () => <div className="w-full h-full bg-muted animate-pulse" />,
  }
)

export function MapPanel() {
  return (
    <div className="w-full h-full">
      <MapInner />
    </div>
  )
}
