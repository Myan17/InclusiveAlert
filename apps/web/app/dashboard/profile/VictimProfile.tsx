// app/dashboard/profile/VictimProfile.tsx
"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { UserProfile } from "@/lib/types"
import {
  ChevronRight, ChevronLeft, CheckCircle,
  Accessibility, Shield, MessageSquare, MapPin
} from "lucide-react"

const STEPS = [
  { id: "disability",    label: "Access Needs",  icon: Accessibility },
  { id: "additional",   label: "Additional",     icon: Shield },
  { id: "communication",label: "Communication",  icon: MessageSquare },
  { id: "location",     label: "Location",       icon: MapPin },
  { id: "review",       label: "Review",         icon: CheckCircle },
]

const DISABILITY_OPTIONS = [
  { value: "deaf",               label: "Deaf / Hard of Hearing",       icon: "🧏", description: "ASL-fluent responders prioritized. Text & haptic alerts enabled.", border: "border-purple-600/50 bg-purple-950/30", activeBorder: "border-purple-500 bg-purple-950/60 ring-1 ring-purple-500/40" },
  { value: "blind",              label: "Blind / Low Vision",           icon: "👁️", description: "Voice-capable responders and guide assistance prioritized.",       border: "border-blue-600/50 bg-blue-950/30",   activeBorder: "border-blue-500 bg-blue-950/60 ring-1 ring-blue-500/40" },
  { value: "mobility_wheelchair",label: "Wheelchair User",              icon: "♿", description: "Wheelchair-accessible shelters and van transport prioritized.",    border: "border-cyan-600/50 bg-cyan-950/30",   activeBorder: "border-cyan-500 bg-cyan-950/60 ring-1 ring-cyan-500/40" },
  { value: "power_dependent",    label: "Power-Dependent Equipment",    icon: "⚡", description: "Generator shelters required. Utility company notified.",           border: "border-yellow-600/50 bg-yellow-950/30",activeBorder: "border-yellow-500 bg-yellow-950/60 ring-1 ring-yellow-500/40" },
  { value: "cognitive",          label: "Cognitive / Developmental",    icon: "🧠", description: "Plain-language alerts and patient, trained responders.",           border: "border-pink-600/50 bg-pink-950/30",   activeBorder: "border-pink-500 bg-pink-950/60 ring-1 ring-pink-500/40" },
  { value: "chronic_illness",    label: "Chronic Illness / Medical",    icon: "🏥", description: "Medical-trained responders and shelters with medical staff.",      border: "border-red-600/50 bg-red-950/30",     activeBorder: "border-red-500 bg-red-950/60 ring-1 ring-red-500/40" },
]

const COMM_OPTIONS = [
  { value: "asl",          label: "ASL",           icon: "🧏", desc: "Responders who sign" },
  { value: "text",         label: "Text / SMS",    icon: "💬", desc: "Text-based alerts" },
  { value: "voice",        label: "Voice / Phone", icon: "📞", desc: "Spoken instructions" },
  { value: "haptic",       label: "Haptic",        icon: "📳", desc: "Vibration alerts" },
  { value: "high_contrast",label: "High Contrast", icon: "🔲", desc: "High-contrast UI" },
  { value: "large_print",  label: "Large Print",   icon: "🔤", desc: "Enlarged text" },
]

const LANGUAGES = [
  { value: "en", label: "English" }, { value: "es", label: "Español" },
  { value: "zh", label: "中文" },    { value: "vi", label: "Tiếng Việt" },
  { value: "ar", label: "العربية" }, { value: "fr", label: "Français" },
]

export function VictimProfileWizard() {
  const { token, email, role } = useAuthStore()
  const [step, setStep] = useState(0)
  const [needs, setNeeds] = useState<string[]>([])
  const [commModes, setCommModes] = useState<string[]>([])
  const [serviceAnimal, setServiceAnimal] = useState(false)
  const [powerDep, setPowerDep] = useState(false)
  const [medDep, setMedDep] = useState(false)
  const [language, setLanguage] = useState("en")
  const [zip, setZip] = useState("")
  const [state, setState] = useState("")
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    api.profiles.getVictim(token).then((p) => {
      setNeeds(p.disability_needs ?? [])
      setCommModes(p.communication_modes ?? [])
      setServiceAnimal(p.service_animal ?? false)
      setPowerDep(p.power_dependency ?? false)
      setMedDep((p as any).medication_dependency ?? false)
      setLanguage((p as any).preferred_language ?? "en")
      setZip(p.location_zip ?? "")
      setState(p.location_state ?? "")
    }).catch(() => {})
  }, [token])

  function toggle<T>(arr: T[], val: T): T[] {
    return arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val]
  }

  async function handleSave() {
    if (!token) return
    setSaving(true); setError(null)
    try {
      await api.profiles.updateVictim(token, {
        disability_needs: needs, communication_modes: commModes,
        service_animal: serviceAnimal, power_dependency: powerDep,
        location_zip: zip || null, location_state: state || null,
      } as Partial<UserProfile>)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed")
    } finally { setSaving(false) }
  }

  const progress = (step / (STEPS.length - 1)) * 100

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-3 mb-3">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-base font-bold text-white shrink-0">
            {email?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">{email}</p>
            <Badge className="text-[10px] mt-0.5 bg-blue-900/60 text-blue-300 border border-blue-700/50">{role}</Badge>
          </div>
        </div>
        <div className="flex items-center gap-0.5 mb-2">
          {STEPS.map((s, i) => {
            const Icon = s.icon; const done = i < step; const active = i === step
            return (
              <button key={s.id} onClick={() => setStep(i)}
                className={`flex-1 flex flex-col items-center gap-0.5 py-1.5 rounded-md transition-all text-[9px] font-medium ${active ? "bg-blue-600/20 text-blue-300 border border-blue-500/40" : done ? "text-green-400" : "text-muted-foreground hover:text-foreground"}`}>
                {done ? <CheckCircle className="h-3.5 w-3.5 text-green-400" /> : <Icon className={`h-3.5 w-3.5 ${active ? "text-blue-400" : ""}`} />}
                <span className="hidden sm:block">{s.label}</span>
              </button>
            )
          })}
        </div>
        <div className="h-1 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {step === 0 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">What are your access needs?</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Personalizes alerts, shelter matches, and responder assignments.</p>
            </div>
            {DISABILITY_OPTIONS.map(({ value, label, icon, description, border, activeBorder }) => {
              const checked = needs.includes(value)
              return (
                <button key={value} onClick={() => setNeeds(toggle(needs, value))}
                  className={`flex items-start gap-3 p-3 rounded-xl border text-left transition-all w-full ${checked ? activeBorder : `${border} hover:brightness-110`}`}>
                  <span className="text-xl shrink-0 mt-0.5">{icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-semibold text-foreground">{label}</span>
                      <div className={`h-4 w-4 rounded-full border-2 shrink-0 flex items-center justify-center transition-all ${checked ? "bg-blue-500 border-blue-500" : "border-muted-foreground"}`}>
                        {checked && <div className="h-2 w-2 rounded-full bg-white" />}
                      </div>
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-0.5 leading-relaxed">{description}</p>
                  </div>
                </button>
              )
            })}
          </div>
        )}

        {step === 1 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Additional needs</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Affects shelter eligibility and responder matching.</p>
            </div>
            {[
              { checked: serviceAnimal, set: setServiceAnimal, icon: "🦮", label: "Service Animal", desc: "Shelters with service animal policies prioritized.", color: "border-green-600/50 bg-green-950/30", activeColor: "border-green-500 bg-green-950/60 ring-1 ring-green-500/40" },
              { checked: powerDep, set: setPowerDep, icon: "⚡", label: "Power-Dependent Medical Equipment", desc: "Ventilator, oxygen, or other powered devices. Generator shelters required.", color: "border-yellow-600/50 bg-yellow-950/30", activeColor: "border-yellow-500 bg-yellow-950/60 ring-1 ring-yellow-500/40" },
              { checked: medDep, set: setMedDep, icon: "💊", label: "Medication Dependent", desc: "Requires regular medication. Pharmacy alerts included.", color: "border-pink-600/50 bg-pink-950/30", activeColor: "border-pink-500 bg-pink-950/60 ring-1 ring-pink-500/40" },
            ].map(({ checked, set, icon, label, desc, color, activeColor }) => (
              <button key={label} onClick={() => set(!checked)}
                className={`flex items-start gap-3 p-3 rounded-xl border text-left transition-all w-full ${checked ? activeColor : `${color} hover:brightness-110`}`}>
                <span className="text-xl shrink-0 mt-0.5">{icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-foreground">{label}</span>
                    <div className={`h-4 w-4 rounded-full border-2 shrink-0 flex items-center justify-center ${checked ? "bg-blue-500 border-blue-500" : "border-muted-foreground"}`}>
                      {checked && <div className="h-2 w-2 rounded-full bg-white" />}
                    </div>
                  </div>
                  <p className="text-[10px] text-muted-foreground mt-0.5 leading-relaxed">{desc}</p>
                </div>
              </button>
            ))}
          </div>
        )}

        {step === 2 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">How do you want to be reached?</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Select all communication modes that work for you.</p>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {COMM_OPTIONS.map(({ value, label, icon, desc }) => {
                const checked = commModes.includes(value)
                return (
                  <button key={value} onClick={() => setCommModes(toggle(commModes, value))}
                    className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border text-center transition-all ${checked ? "border-blue-500 bg-blue-950/50 ring-1 ring-blue-500/40" : "border-border bg-card hover:border-muted-foreground/40"}`}>
                    <span className="text-2xl">{icon}</span>
                    <span className="text-xs font-semibold text-foreground leading-tight">{label}</span>
                    <span className="text-[9px] text-muted-foreground">{desc}</span>
                    {checked && <span className="text-[9px] text-blue-400 font-bold">✓ Selected</span>}
                  </button>
                )
              })}
            </div>
            <div className="mt-1">
              <p className="text-xs font-semibold text-foreground mb-2">Preferred Language</p>
              <div className="grid grid-cols-3 gap-1.5">
                {LANGUAGES.map(({ value, label }) => (
                  <button key={value} onClick={() => setLanguage(value)}
                    className={`py-2 px-3 rounded-lg text-xs font-medium border transition-all ${language === value ? "border-blue-500 bg-blue-950/50 text-blue-300" : "border-border text-muted-foreground hover:border-muted-foreground/60"}`}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="flex flex-col gap-4">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Where are you located?</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Only ZIP and state stored — never precise GPS.</p>
            </div>
            <Card className="bg-card border-border">
              <CardContent className="p-4 flex flex-col gap-3">
                <div>
                  <label className="text-xs font-medium text-foreground block mb-1.5">ZIP Code</label>
                  <input type="text" placeholder="e.g. 77001" value={zip} onChange={(e) => setZip(e.target.value)} maxLength={10}
                    className="w-full px-3 py-2.5 rounded-lg bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
                </div>
                <div>
                  <label className="text-xs font-medium text-foreground block mb-1.5">State</label>
                  <input type="text" placeholder="e.g. TX" value={state} onChange={(e) => setState(e.target.value.toUpperCase())} maxLength={2}
                    className="w-full px-3 py-2.5 rounded-lg bg-muted border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring" />
                </div>
              </CardContent>
            </Card>
            <div className="rounded-xl border border-border bg-muted/30 p-3 text-xs text-muted-foreground flex items-start gap-2">
              <span className="text-base shrink-0">🔒</span>
              <span>Your location is used only for emergency matching and is never shared without consent.</span>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="flex flex-col gap-3">
            <div className="mb-1">
              <h2 className="text-sm font-bold text-foreground">Review your profile</h2>
              <p className="text-xs text-muted-foreground mt-0.5">Confirm everything looks right before saving.</p>
            </div>
            <Card className="bg-card border-border">
              <CardContent className="p-4 flex flex-col gap-2.5">
                <ReviewRow label="Access Needs" value={needs.length > 0 ? needs.map((n) => DISABILITY_OPTIONS.find((d) => d.value === n)?.label ?? n).join(", ") : "None"} />
                <ReviewRow label="Service Animal" value={serviceAnimal ? "Yes" : "No"} />
                <ReviewRow label="Power Dependent" value={powerDep ? "Yes" : "No"} />
                <ReviewRow label="Medication" value={medDep ? "Yes" : "No"} />
                <ReviewRow label="Communication" value={commModes.length > 0 ? commModes.join(", ") : "None"} />
                <ReviewRow label="Language" value={LANGUAGES.find((l) => l.value === language)?.label ?? language} />
                <ReviewRow label="Location" value={zip && state ? `${zip}, ${state}` : zip || state || "Not set"} />
              </CardContent>
            </Card>
            {error && <div className="rounded-lg bg-red-950/40 border border-red-800/50 px-3 py-2 text-xs text-red-300">{error}</div>}
            <Button onClick={handleSave} disabled={saving}
              className="w-full h-11 text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 border-0">
              {saving ? "Saving…" : saved ? "✓ Profile Saved!" : "Save Profile"}
            </Button>
            {saved && (
              <div className="rounded-lg bg-green-950/40 border border-green-800/50 px-3 py-2 text-xs text-green-300 text-center">
                ✓ Profile saved. Alerts and matches are now personalized.
              </div>
            )}
          </div>
        )}
      </div>

      <div className="px-4 pb-4 pt-2 border-t border-border shrink-0 flex gap-2">
        {step > 0 && (
          <Button variant="ghost" onClick={() => setStep((s) => s - 1)} className="flex-1 gap-1 text-muted-foreground">
            <ChevronLeft className="h-4 w-4" /> Back
          </Button>
        )}
        {step < STEPS.length - 1 && (
          <Button onClick={() => setStep((s) => s + 1)} className="flex-1 gap-1 bg-blue-600 hover:bg-blue-500">
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
