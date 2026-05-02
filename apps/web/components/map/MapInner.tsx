"use client"
import { useEffect } from "react"
import { MapContainer, TileLayer } from "react-leaflet"
import L from "leaflet"
import { useMapStore } from "@/store/mapStore"
import { LayerToggle } from "./LayerToggle"

// Fix Leaflet default marker icons in webpack/Next.js builds
// Using imagePath approach to avoid TypeScript/webpack PNG import complexity
L.Icon.Default.imagePath = "https://unpkg.com/leaflet@1.9.4/dist/images/"

function LocationTracker() {
  const { setUserLocation } = useMapStore()
  useEffect(() => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      (pos) => setUserLocation(pos.coords.latitude, pos.coords.longitude),
      () => {} // silently ignore denied permission
    )
  }, [setUserLocation])
  return null
}

export function MapInner() {
  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={[39.5, -98.35]}
        zoom={4}
        style={{ width: "100%", height: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <LocationTracker />
        {/* Layer components added in Tasks 6-8 */}
      </MapContainer>
      <LayerToggle />
    </div>
  )
}
