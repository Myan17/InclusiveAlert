import { create } from "zustand"

interface MapState {
  selectedAlertId: string | null
  userLat: number | null
  userLon: number | null
  showHazards: boolean
  showShelters: boolean
  showRespondents: boolean
  setSelectedAlert: (id: string | null) => void
  setUserLocation: (lat: number, lon: number) => void
  toggleLayer: (layer: "showHazards" | "showShelters" | "showRespondents") => void
}

export const useMapStore = create<MapState>((set) => ({
  selectedAlertId: null,
  userLat: null,
  userLon: null,
  showHazards: true,
  showShelters: true,
  showRespondents: true,
  setSelectedAlert: (id) => set({ selectedAlertId: id }),
  setUserLocation: (lat, lon) => set({ userLat: lat, userLon: lon }),
  toggleLayer: (layer) => set((s) => ({ [layer]: !s[layer] })),
}))
