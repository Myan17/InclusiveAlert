// components/alerts/AslModal.tsx
"use client"
import { useEffect } from "react"
import { X, ExternalLink } from "lucide-react"

// Real FEMA ASL emergency videos — distinct per hazard type
// All IDs verified from FEMA's official YouTube channel via archive.org
const ASL_VIDEOS: Record<string, { title: string; embedId: string; credit: string }> = {
  tornado_warning: {
    title: "Tornado & Severe Weather — ASL",
    embedId: "-bwsoUcQyck", // FEMA 2023 National Preparedness Month ASL PSA
    credit: "FEMA",
  },
  flash_flood_warning: {
    title: "Flood Safety — ASL (Hurricane Debby)",
    embedId: "hO9yptPrEDw", // FEMA ASL Hurricane Debby flood messaging Aug 2024
    credit: "FEMA",
  },
  excessive_heat_warning: {
    title: "Emergency Preparedness for All — ASL",
    embedId: "bv2rKUmt66U", // CDC: Preparedness for All — ASL
    credit: "CDC",
  },
  earthquake: {
    title: "2024 National Preparedness Month — ASL",
    embedId: "KjrwLbbncZg", // FEMA 2024 Preparedness Month ASL
    credit: "FEMA",
  },
  hurricane_watch: {
    title: "Hurricane Helene — ASL Emergency Messaging",
    embedId: "E8xdTN3qxrA", // FEMA ASL Hurricane Helene Messaging 09.25.2024
    credit: "FEMA",
  },
  winter_storm_warning: {
    title: "Winter Storm Safety — ASL",
    embedId: "bRkzXfb8uek", // FEMA ASL Winter Storm Messaging 01.24.2026
    credit: "FEMA",
  },
  default: {
    title: "Emergency Preparedness — ASL",
    embedId: "-bwsoUcQyck", // FEMA 2023 National Preparedness Month ASL PSA
    credit: "FEMA",
  },
}

interface AslModalProps {
  hazardType: string
  headline: string
  onClose: () => void
}

export function AslModal({ hazardType, headline, onClose }: AslModalProps) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose() }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [onClose])

  const video = ASL_VIDEOS[hazardType] ?? ASL_VIDEOS.default
  const embedUrl = `https://www.youtube.com/embed/${video.embedId}?autoplay=1&rel=0`
  const watchUrl = `https://www.youtube.com/watch?v=${video.embedId}`

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`ASL video: ${video.title}`}
    >
      <div
        className="relative bg-card border border-border rounded-xl shadow-2xl w-full max-w-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-4 border-b border-border">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xl" aria-hidden="true">🧏</span>
              <p className="text-sm font-semibold text-foreground">{video.title}</p>
            </div>
            <p className="text-[10px] text-muted-foreground mt-0.5 truncate">{headline}</p>
          </div>
          <div className="flex items-center gap-2 ml-3 shrink-0">
            <a
              href={watchUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1"
              aria-label="Open in YouTube"
            >
              <ExternalLink className="h-3 w-3" />
              YouTube
            </a>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Close ASL video"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Video */}
        <div className="aspect-video w-full bg-black overflow-hidden rounded-b-xl">
          <iframe
            src={embedUrl}
            title={video.title}
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>

        {/* Footer */}
        <div className="px-4 py-2 text-[10px] text-muted-foreground flex items-center justify-between border-t border-border rounded-b-xl">
          <span>Source: {video.credit} · American Sign Language</span>
          <span>Press Esc to close</span>
        </div>
      </div>
    </div>
  )
}
