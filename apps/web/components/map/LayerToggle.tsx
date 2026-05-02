"use client"
import { useMapStore } from "@/store/mapStore"

export function LayerToggle() {
  const { showHazards, showShelters, showRespondents, toggleLayer } = useMapStore()

  return (
    <div className="absolute top-3 right-3 z-[1000] bg-card border border-border rounded-md p-2 flex flex-col gap-1 text-xs shadow-lg">
      {([
        ["showHazards", showHazards, "Hazard Zones"],
        ["showShelters", showShelters, "Shelters"],
        ["showRespondents", showRespondents, "Respondents"],
      ] as const).map(([key, checked, label]) => (
        <label key={key} className="flex items-center gap-2 cursor-pointer text-foreground">
          <input
            type="checkbox"
            checked={checked}
            onChange={() => toggleLayer(key)}
            className="accent-blue-400"
          />
          {label}
        </label>
      ))}
    </div>
  )
}
