import { Card, CardContent } from "@/components/ui/card"
import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  label: string
  value: string | number
  icon: LucideIcon
  accent?: "red" | "orange" | "green" | "blue"
}

const accentClasses = {
  red: "text-red-400",
  orange: "text-orange-400",
  green: "text-green-400",
  blue: "text-blue-400",
}

export function StatCard({ label, value, icon: Icon, accent = "blue" }: StatCardProps) {
  return (
    <Card className="bg-card border-border flex-1 min-w-[120px]">
      <CardContent className="p-4 flex items-center gap-3">
        <Icon className={`h-5 w-5 shrink-0 ${accentClasses[accent]}`} />
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-lg font-bold text-foreground">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
