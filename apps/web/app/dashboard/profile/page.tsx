// app/dashboard/profile/page.tsx
// Routes to the correct profile wizard based on user role
"use client"
import { useAuthStore } from "@/store/authStore"
import { RespondentProfileWizard } from "./RespondentProfile"
import { VictimProfileWizard } from "./VictimProfile"

export default function ProfilePage() {
  const role = useAuthStore((s) => s.role)
  if (role === "respondent" || role === "authority") return <RespondentProfileWizard />
  return <VictimProfileWizard />
}
