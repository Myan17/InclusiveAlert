"use client"
import { useEffect, useRef } from "react"
import { MapContainer, TileLayer, useMap } from "react-leaflet"
import L from "leaflet"
import { useMapStore } from "@/store/mapStore"
import { LayerToggle } from "./LayerToggle"
import { HazardLayer } from "./HazardLayer"
import { ShelterLayer } from "./ShelterLayer"
import { RespondentLayer } from "./RespondentLayer"

L.Icon.Default.imagePath = "https://unpkg.com/leaflet@1.9.4/dist/images/"

// Houston — demo data center
const DEMO_LAT = 29.7604
const DEMO_LON = -95.3698

function LocationTracker() {
  const { setUserLocation } = useMapStore()
  const didSet = useRef(false)

  useEffect(() => {
    if (didSet.current) return
    // Pin to the Houston demo location, where all seeded shelters and
    // responders live. Real geolocation is intentionally NOT used: the demo
    // dataset is Houston-only, so a viewer's actual location would show
    // "no shelters nearby" and poor match scores. (To run against a viewer's
    // real location, restore navigator.geolocation.getCurrentPosition here.)
    setUserLocation(DEMO_LAT, DEMO_LON)
    didSet.current = true
  }, [setUserLocation])

  return null
}

// Pan map to user location when it changes from the demo default
function MapController() {
  const map = useMap()
  const { userLat, userLon } = useMapStore()
  const prevLat = useRef<number | null>(null)

  useEffect(() => {
    if (userLat === null || userLon === null) return
    // Only fly if location actually changed from demo default (i.e. real GPS)
    const isDemoLocation = Math.abs(userLat - DEMO_LAT) < 0.001 && Math.abs(userLon - DEMO_LON) < 0.001
    if (!isDemoLocation && prevLat.current !== userLat) {
      map.flyTo([userLat, userLon], 11, { duration: 1.5 })
      prevLat.current = userLat
    }
  }, [map, userLat, userLon])

  return null
}

export function MapInner() {
  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={[DEMO_LAT, DEMO_LON]}
        zoom={11}
        style={{ width: "100%", height: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <LocationTracker />
        <MapController />
        <HazardLayer />
        <ShelterLayer />
        <RespondentLayer />
      </MapContainer>
      <LayerToggle />
    </div>
  )
}
