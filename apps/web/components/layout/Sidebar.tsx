"use client"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Bell, MapPin, Users, User, LogOut, Shield, AlertTriangle } from "lucide-react"
import { useAuthStore } from "@/store/authStore"
import { useAlerts } from "@/lib/useAlerts"
import { Button } from "@/components/ui/button"

const navItems = [
  { href: "/dashboard/alerts",   label: "Alerts",   icon: Bell },
  { href: "/dashboard/shelters", label: "Shelters", icon: MapPin },
  { href: "/dashboard/matching", label: "Matching", icon: Users },
  { href: "/dashboard/profile",  label: "Profile",  icon: User },
]

const roleConfig: Record<string, { color: string; bg: string; label: string }> = {
  victim:     { color: "text-red-300",   bg: "bg-red-900/60",   label: "Needs Assistance" },
  respondent: { color: "text-green-300", bg: "bg-green-900/60", label: "Responder" },
  authority:  { color: "text-blue-300",  bg: "bg-blue-900/60",  label: "Authority" },
}

function AlertBadge() {
  const { data: alerts = [] } = useAlerts()
  const extreme = alerts.filter((a) => a.severity === "Extreme" || a.severity === "Severe").length
  if (extreme === 0) return null
  return (
    <span className="ml-auto flex items-center justify-center h-4 min-w-4 px-1 rounded-full bg-red-500 text-white text-[9px] font-bold animate-pulse">
      {extreme}
    </span>
  )
}

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { email, role, logout } = useAuthStore()
  const rc = roleConfig[role ?? "victim"] ?? roleConfig.victim

  function handleLogout() {
    logout()
    router.replace("/login")
  }

  return (
    <aside className="w-60 shrink-0 flex flex-col h-screen border-r border-border"
      style={{ background: "linear-gradient(180deg, #0d0f1a 0%, #111320 100%)" }}
    >
      {/* Logo */}
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
            <Shield className="h-4 w-4 text-blue-400" />
          </div>
          <div>
            <span className="font-bold text-foreground text-sm tracking-tight">InclusiveAlert</span>
            <p className="text-[9px] text-muted-foreground leading-none mt-0.5">Emergency Response System</p>
          </div>
        </div>
      </div>

      {/* Live status bar */}
      <div className="mx-3 mt-3 px-3 py-2 rounded-lg bg-green-950/40 border border-green-800/40 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse shrink-0" />
        <span className="text-[10px] text-green-300 font-medium">System Active · Live Data</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-3 flex flex-col gap-0.5">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 ${
                active
                  ? "bg-blue-600/20 text-blue-300 font-semibold border border-blue-500/30"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              }`}
            >
              <Icon className={`h-4 w-4 shrink-0 ${active ? "text-blue-400" : ""}`} />
              <span className="flex-1">{label}</span>
              {label === "Alerts" && <AlertBadge />}
            </Link>
          )
        })}
      </nav>

      {/* Divider */}
      <div className="mx-3 border-t border-border" />

      {/* User section */}
      <div className="px-3 py-3 flex flex-col gap-2">
        <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg bg-white/5">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {email?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-foreground truncate font-medium">{email}</p>
            <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${rc.bg} ${rc.color}`}>
              {rc.label}
            </span>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs text-muted-foreground hover:text-red-400 hover:bg-red-950/30 transition-colors w-full"
        >
          <LogOut className="h-3 w-3" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
