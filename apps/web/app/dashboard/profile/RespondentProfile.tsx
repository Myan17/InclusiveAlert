// app/dashboard/profile/RespondentProfile.tsx
"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { RespondentProfile } from "@/lib/types"
import {
  ChevronRight, ChevronLeft, CheckCircle,
  Stethoscope, Car, Hand, Shield, MapPin, ToggleLeft, Briefcase
} from "lucide-react"

const STEPS = [
  { id: "skills",       label: "Skills",        icon: Stethoscope },
  { id: "asl",          label: "ASL & Comms",   icon: Hand },
  { id: "vehicle",      label: "Transport",     icon: Car },
  { id: "availability", label: "Availability",  icon: ToggleLeft },
  { id: "location",     label: "Location",      icon: MapPin },
  { id: "review",       label: "Review",        icon: CheckCircle },
]

const SKILL_OPTIONS = [
  { value: "asl_interpreter",  label: "ASL Interpreter",       icon: "🧏", desc: "Certified or fluent ASL communication" },
  { value: "first_aid",        label: "First Aid / CPR",        icon: "🩹", desc: "Basic emergency medical response" },
  { value: "medical_technician",label: "Medical Technician",   icon: "🩺", desc: "EMT, paramedic, or clinical training" },
  { value: "medication_admin", label: "Medication Admin",       icon: "💊", desc: "Can administer medications safely" },
  { value: "oxygen_management",label: "Oxygen / Ventilator",   icon: "🫁", desc: "Portable oxygen and ventilator support" },
  { value: "guide_assistant",  label: "Guide / Visual Assist",  icon: "👁️", desc: "Assists blind or low-vision individuals" },
  { value: "mobility_assistant",label: "Mobility Assistance",  icon: "♿", desc: "Wheelchair handling and mobility support" },
  { value: "animal_handler",   label: "Animal Handler",         icon: "🦮", desc: "Comfortable with service animals" },
  { value: "heavy_lift",       label: "Heavy Lifting",          icon: "💪", desc: "Physical evacuation assistance" },
  { value: "mental_health",    label: "Mental Health Support",  icon: "🧠", desc: "Crisis counseling or de-escalation" },
]

const ASL_LEVELS = [
  { value: "none",   label: "None",         desc: "No ASL knowledge" },
  { value: "basic",  label: "Basic",        desc: "Simple signs and fingerspelling" },
  { value: "fluent", label: "Fluent",       desc: "Conversational ASL" },
  { value: "native", label: "Native / Certified", desc: "Native signer or certified interpreter" },
]

const VEHICLE_OPTIONS = [
  { value: "none",          label: "No Vehicle",       icon: "🚶" },
  { value: "car",           label: "Car / Sedan",      icon: "🚗" },
  { value: "suv",           label: "SUV / Truck",      icon: "🚙" },
  { value: "van_wheelchair",label: "Wheelchair Van",   icon: "🚐" },
  { value: "motorcycle",    label: "Motorcycle",       icon: "🏍️" },
  { value: "bicycle",       label: "Bicycle",          icon: "🚲" },
]

const VETTING_TIERS = [
  { value: "neighbor",          label: "Community Member",    color: "border-gray-600/50 bg-gray-950/30" },
  { value: "trained_volunteer", label: "Trained Volunteer",   color: "border-blue-600/50 bg-blue-950/30" },
  { value: "ngo",               label: "NGO / Nonprofit",     color: "border-green-600/50 bg-green-950/30" },
  { value: "medical",           label: "Medical Professional",color: "border-red-600/50 bg-red-950/30" },
  { value: "authority_verified",label: "Authority Verified",  color: "border-yellow-600/50 bg-yellow-950/30" },
]

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "es", label: "Español" },
  { value: "asl", label: "ASL" },
  { value: "zh", label: "中文" },
  { value: "vi", label: "Tiếng Việt" },
  { value: "ar", label: "العربية" },
]

export function RespondentProfileWizard() {
  const { token, email, role } = useAuthStore()
  const [step, setStep] = useState(0)
  const [skills, setSkills] = useState<string[]>([])
  const [aslLevel, setAslLevel] = useState("none")
  const [languages, setLanguages] = useState<string[]>(["en"])
  const [commModes, setCommModes] = useState<string[]>(["voice", "text"])
  const [vehicleType, setVehicleType] = useState("none")
  const [vettingTier, setVettingTier] = useState("neighbor")
  const [availability, setAvailability] = useState<"available" | "unavailable" | "on_break">("unavailable")
  const [maxRadius, setMaxRadius] = useState(20)
  const [zip, setZip] = useState("")
  const [org, setOrg] = useState("")
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    api.profiles.getRespondent(token).then((p) => {
      setSkills(p.skills ?? [])
      setAslLevel(p.asl_level ?? "none")
      setLanguages(p.languages ?? ["en"])
      setCommModes(p.communication_modes ?? ["voice", "text"])
      setVehicleType(p.vehicle_type ?? "none")
      setVettingTier(p.vetting_tier ?? "neighbor")
      setAvailability((p.availability_status as any) ?? "unavailable")
      setMaxRadius(p.max_radius_km ?? 20)
      setZip(p.location_zip ?? "")
      setOrg(p.organization_id ?? "")
    }).catch(() => {})
  }, [token])

  function toggle<T>(arr: T[], val: T): T[] {
    return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val]
  }

  async function handleSave() {
    if (!token) return
    setSaving(true)
    setError(null)
    try {
      await api.profiles.updateRespondent(token, {
        skills,
        asl_level: aslLevel,
        languages,
        communication_modes: commModes,
        vehicle_type: vehicleType === "none" ? null : vehicleType,
        vetting_tier: vettingTier,
        availability_status: availability,
        max_radius_km: maxRadius,
        location_zip: zip || null,
        organization_id: org || null,
      } as Partial<RespondentProfile>)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed")
    } finally {
      setSaving(false)
    }
  }

  const progress = (step / (STEPS.length - 1)) * 100

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center text-base font-bold text-white shrink-0">
            {email?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">{email}</p>
            <Badge className="text-[10px] mt-0.5 bg-green-900/60 text-green-300 border border-green-700/50">Responder</Badge>
          </div>
        </div>

        {/* Step tabs */}
        <div className="flex items-center gap-0.5 mb-2">
          {STEPS.map((s, i) => {
            const Icon = s.icon
            const done = i < step
            const active = i === step
            return (
              <button
                key={s.id}
                onClick={() => setStep(i)}
                className={`flex-1 flex flex-col items-center gap-0.5 py-1.5 rounded-md transition-all text-[9px] font-medium ${
                  active ? "bg-green-600/20 text-green-300 border border-green-500/40" :
                  done   ? "text-green-400" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {done
                  ? <CheckCircle className="h-3.5 w-3.5 text-green-400" />
                  : <Icon className={`h-3.5 w-3.5 ${active ? "text-green-400" : ""}`} />
                }
                <span className="hidden sm:block">{s.label}</span>
              </button>
            )
          })}
        </div>
        <div className="h-1 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-teal-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step content */}
      <div className="flex-1 overflow-y-auto px-4 py-4">

        {/* Step 0: Skills */}
        {step === 0 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">What are your skills?</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Select all that apply. Used to match you with victims who need your specific capabilities.</p>
            </div>
            <div className="flex flex-col gap-2">
              {SKILL_OPTIONS.map(({ value, label, icon, desc }) => {
                const checked = skills.includes(value)
                return (
                  <button
                    key={value}
                    onClick={() => setSkills(toggle(skills, value))}
                    className={`flex items-center gap-3 p-3 rounded-xl border text-left transition-all w-full ${
                      checked
                        ? "border-green-500 bg-green-950/50 ring-1 ring-green-500/30"
                        : "border-border bg-card hover:border-muted-foreground/40"
                    }`}
                  >
                    <span className="text-xl shrink-0">{icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-foreground">{label}</span>
                        <div className={`h-4 w-4 rounded-full border-2 shrink-0 flex items-center justify-center ${
                          checked ? "bg-green-500 border-green-500" : "border-muted-foreground"
                        }`}>
                          {checked && <div className="h-2 w-2 rounded-full bg-white" />}
                        </div>
                      </div>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{desc}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* Step 1: ASL & Communication */}
        {step === 1 && (
          <div className="flex flex-col gap-4">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">ASL & Communication</h2>
              <p className="text-xs text-muted-foreground mt-0.5">ASL-fluent responders are prioritized for Deaf victims.</p>
            </div>

            <div>
              <p className="text-xs font-semibold text-foreground mb-2">ASL Proficiency Level</p>
              <div className="flex flex-col gap-2">
                {ASL_LEVELS.map(({ value, label, desc }) => (
                  <button
                    key={value}
                    onClick={() => setAslLevel(value)}
                    className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
                      aslLevel === value
                        ? "border-purple-500 bg-purple-950/50 ring-1 ring-purple-500/30"
                        : "border-border bg-card hover:border-muted-foreground/40"
                    }`}
                  >
                    <div>
                      <p className="text-sm font-semibold text-foreground">{label}</p>
                      <p className="text-[10px] text-muted-foreground">{desc}</p>
                    </div>
                    <div className={`h-4 w-4 rounded-full border-2 shrink-0 ${
                      aslLevel === value ? "bg-purple-500 border-purple-500" : "border-muted-foreground"
                    }`} />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-foreground mb-2">Languages Spoken</p>
              <div className="grid grid-cols-3 gap-1.5">
                {LANGUAGES.map(({ value, label }) => (
                  <button
                    key={value}
                    onClick={() => setLanguages(toggle(languages, value))}
                    className={`py-2 px-3 rounded-lg text-xs font-medium border transition-all ${
                      languages.includes(value)
                        ? "border-green-500 bg-green-950/50 text-green-300"
                        : "border-border text-muted-foreground hover:border-muted-foreground/60"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Vehicle */}
        {step === 2 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Transport & Equipment</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Wheelchair vans are critical for mobility-impaired victims.</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {VEHICLE_OPTIONS.map(({ value, label, icon }) => (
                <button
                  key={value}
                  onClick={() => setVehicleType(value)}
                  className={`flex flex-col items-center gap-2 p-4 rounded-xl border transition-all ${
                    vehicleType === value
                      ? "border-green-500 bg-green-950/50 ring-1 ring-green-500/30"
                      : "border-border bg-card hover:border-muted-foreground/40"
                  }`}
                >
                  <span className="text-3xl">{icon}</span>
                  <span className="text-xs font-semibold text-foreground text-center">{label}</span>
                  {vehicleType === value && <span className="text-[9px] text-green-400 font-bold">✓ Selected</span>}
                </button>
              ))}
            </div>

            <div>
              <p className="text-xs font-semibold text-foreground mb-2">Vetting / Trust Tier</p>
              <div className="flex flex-col gap-1.5">
                {VETTING_TIERS.map(({ value, label, color }) => (
                  <button
                    key={value}
                    onClick={() => setVettingTier(value)}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-xl border transition-all ${
                      vettingTier === value
                        ? `${color} ring-1 ring-white/10`
                        : "border-border bg-card hover:border-muted-foreground/40"
                    }`}
                  >
                    <span className="text-sm font-medium text-foreground">{label}</span>
                    <div className={`h-4 w-4 rounded-full border-2 ${
                      vettingTier === value ? "bg-green-500 border-green-500" : "border-muted-foreground"
                    }`} />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Availability */}
        {step === 3 && (
          <div className="flex flex-col gap-4">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Availability Status</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Only "Available" responders appear in victim matching.</p>
            </div>

            {([
              { value: "available",   label: "Available Now",    desc: "Ready to respond immediately", color: "border-green-500 bg-green-950/50", dot: "bg-green-400 animate-pulse" },
              { value: "on_break",    label: "On Break",         desc: "Available within 30 minutes",  color: "border-yellow-500 bg-yellow-950/50", dot: "bg-yellow-400" },
              { value: "unavailable", label: "Unavailable",      desc: "Not available to respond",     color: "border-gray-600 bg-gray-950/30", dot: "bg-gray-500" },
            ] as const).map(({ value, label, desc, color, dot }) => (
              <button
                key={value}
                onClick={() => setAvailability(value)}
                className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
                  availability === value ? `${color} ring-1 ring-white/10` : "border-border bg-card hover:border-muted-foreground/40"
                }`}
              >
                <span className={`h-3 w-3 rounded-full shrink-0 ${dot}`} />
                <div className="flex-1 text-left">
                  <p className="text-sm font-semibold text-foreground">{label}</p>
                  <p className="text-[10px] text-muted-foreground">{desc}</p>
                </div>
                <div className={`h-4 w-4 rounded-full border-2 shrink-0 ${
                  availability === value ? "bg-green-500 border-green-500" : "border-muted-foreground"
                }`} />
              </button>
            ))}

            <div>
              <p className="text-xs font-semibold text-foreground mb-2">
                Max Response Radius: <span className="text-green-400">{maxRadius} km</span>
              </p>
              <input
                type="range"
                min={5} max={100} step={5}
                value={maxRadius}
                onChange={(e) => setMaxRadius(Number(e.target.value))}
                className="w-full accent-green-500"
              />
              <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
                <span>5 km</span><span>50 km</span><span>100 km</span>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Location */}
        {step === 4 && (
          <div className="flex flex-col gap-4">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Your Location</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Used to calculate proximity to victims. Only ZIP is stored.</p>
            </div>
            <Card className="bg-card border-border">
              <CardContent className="p-4 flex flex-col gap-3">
                <div>
                  <label className="text-xs font-medium text-foreground block mb-1.5">ZIP Code</label>
                  <input
                    type="text" placeholder="e.g. 77001" value={zip}
                    onChange={(e) => setZip(e.target.value)} maxLength={10}
                    className="w-full px-3 py-2.5 rounded-lg bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-foreground block mb-1.5">Organization (optional)</label>
                  <input
                    type="text" placeholder="e.g. Houston Red Cross" value={org}
                    onChange={(e) => setOrg(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-lg bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 5: Review */}
        {step === 5 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Review your responder profile</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Confirm before saving.</p>
            </div>
            <Card className="bg-card border-border">
              <CardContent className="p-4 flex flex-col gap-2.5">
                <ReviewRow label="Skills" value={skills.length > 0 ? `${skills.length} selected` : "None"} />
                <ReviewRow label="ASL Level" value={ASL_LEVELS.find((l) => l.value === aslLevel)?.label ?? aslLevel} />
                <ReviewRow label="Languages" value={languages.join(", ")} />
                <ReviewRow label="Vehicle" value={VEHICLE_OPTIONS.find((v) => v.value === vehicleType)?.label ?? vehicleType} />
                <ReviewRow label="Vetting Tier" value={VETTING_TIERS.find((t) => t.value === vettingTier)?.label ?? vettingTier} />
                <ReviewRow label="Status" value={availability} />
                <ReviewRow label="Max Radius" value={`${maxRadius} km`} />
                <ReviewRow label="ZIP" value={zip || "Not set"} />
                {org && <ReviewRow label="Organization" value={org} />}
              </CardContent>
            </Card>

            {/* Availability quick-set */}
            <div className="flex gap-2">
              {(["available", "on_break", "unavailable"] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => setAvailability(s)}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold border transition-all ${
                    availability === s
                      ? s === "available" ? "bg-green-600 border-green-500 text-white"
                        : s === "on_break" ? "bg-yellow-600 border-yellow-500 text-white"
                        : "bg-gray-700 border-gray-600 text-white"
                      : "border-border text-muted-foreground hover:border-muted-foreground/60"
                  }`}
                >
                  {s === "available" ? "🟢 Available" : s === "on_break" ? "🟡 On Break" : "🔴 Unavailable"}
                </button>
              ))}
            </div>

            {error && (
              <div className="rounded-lg bg-red-950/40 border border-red-800/50 px-3 py-2 text-xs text-red-300">{error}</div>
            )}

            <Button
              onClick={handleSave}
              disabled={saving}
              className="w-full h-11 text-sm font-semibold bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-500 hover:to-teal-500 border-0"
            >
              {saving ? "Saving…" : saved ? "✓ Profile Saved!" : "Save Responder Profile"}
            </Button>

            {saved && (
              <div className="rounded-lg bg-green-950/40 border border-green-800/50 px-3 py-2 text-xs text-green-300 text-center">
                ✓ Profile saved. You are now {availability === "available" ? "visible to victims" : "set as " + availability}.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="px-4 pb-4 pt-2 border-t border-border shrink-0 flex gap-2">
        {step > 0 && (
          <Button variant="ghost" onClick={() => setStep((s) => s - 1)} className="flex-1 gap-1 text-muted-foreground">
            <ChevronLeft className="h-4 w-4" /> Back
          </Button>
        )}
        {step < STEPS.length - 1 && (
          <Button onClick={() => setStep((s) => s + 1)} className="flex-1 gap-1 bg-green-600 hover:bg-green-500">
            Next <ChevronRight className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-3 text-xs">
      <span className="text-muted-foreground shrink-0 w-28">{label}</span>
      <span className="text-foreground text-right font-medium">{value}</span>
    </div>
  )
}
