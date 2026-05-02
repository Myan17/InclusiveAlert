"use client"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Bell, MapPin, Users, User, LogOut, Shield } from "lucide-react"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"

const navItems = [
  { href: "/dashboard/alerts",   label: "Alerts",   icon: Bell },
  { href: "/dashboard/shelters", label: "Shelters", icon: MapPin },
  { href: "/dashboard/matching", label: "Matching", icon: Users },
  { href: "/dashboard/profile",  label: "Profile",  icon: User },
]

const roleColors: Record<string, string> = {
  victim:     "bg-red-900 text-red-300",
  respondent: "bg-green-900 text-green-300",
  authority:  "bg-blue-900 text-blue-300",
}

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { email, role, logout } = useAuthStore()

  function handleLogout() {
    logout()
    router.push("/login")
  }

  return (
    <aside className="w-60 shrink-0 flex flex-col h-screen bg-[#13151f] border-r border-border">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-blue-400" />
          <span className="font-bold text-foreground text-sm">InclusiveAlert</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-blue-950 text-blue-300 font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* User section */}
      <div className="px-4 py-4 border-t border-border flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-foreground">
            {email?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-foreground truncate">{email}</p>
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${roleColors[role ?? "victim"] ?? ""}`}>
              {role}
            </span>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogout}
          className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground text-xs"
        >
          <LogOut className="h-3 w-3" />
          Sign out
        </Button>
      </div>
    </aside>
  )
}
