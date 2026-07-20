"use client"
import { useEffect, useState, useCallback } from "react"
import { useAuthStore } from "@/store/authStore"
import { api } from "@/lib/api"
import type { ShelterDetail } from "@/lib/types"
import { ClipboardCheck, Plus, Loader2 } from "lucide-react"

// null = unconfirmed, true = yes, false = no
const TRI = [
  { v: "unknown", label: "Unknown" },
  { v: "yes", label: "Yes" },
  { v: "no", label: "No" },
]
const toTri = (b: boolean | null): string => (b === true ? "yes" : b === false ? "no" : "unknown")
const fromTri = (s: string): boolean | null => (s === "yes" ? true : s === "no" ? false : null)

const ACCESS_FIELDS: { key: keyof ShelterDetail; label: string }[] = [
  { key: "wheelchair_accessible", label: "Wheelchair accessible" },
  { key: "ada_compliant", label: "ADA compliant" },
  { key: "generator_onsite", label: "Generator on-site" },
  { key: "asl_support", label: "ASL support" },
]

function TriSelect({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="flex items-center justify-between gap-2 text-xs text-foreground">
      <span>{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-muted border border-border rounded px-2 py-1 text-xs"
      >
        {TRI.map((t) => <option key={t.v} value={t.v}>{t.label}</option>)}
      </select>
    </label>
  )
}

export default function ManageSheltersPage() {
  const { token, role } = useAuthStore()
  const [shelters, setShelters] = useState<ShelterDetail[]>([])
  const [selected, setSelected] = useState<ShelterDetail | null>(null)
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [creating, setCreating] = useState({ name: "", lat: "", lon: "", address: "", capacity: "", phone: "" })

  const load = useCallback(async () => {
    if (!token) return
    try { setShelters(await api.shelters.list(token)) } catch { setMsg("Failed to load shelters") }
  }, [token])

  useEffect(() => { load() }, [load])

  if (role !== "authority") {
    return <div className="p-6 text-sm text-muted-foreground">Authority access only.</div>
  }

  async function saveAccessibility() {
    if (!token || !selected) return
    setSaving(true); setMsg(null)
    try {
      const updated = await api.shelters.patch(token, selected.id, {
        wheelchair_accessible: selected.wheelchair_accessible,
        ada_compliant: selected.ada_compliant,
        generator_onsite: selected.generator_onsite,
        asl_support: selected.asl_support,
        pet_policy: selected.pet_policy,
        status: selected.status,
        capacity: selected.capacity,
        phone: selected.phone,
      })
      setMsg(`Saved — ${updated.name} verified.`)
      await load()
    } catch { setMsg("Save failed") } finally { setSaving(false) }
  }

  async function addFacility() {
    if (!token || !creating.name || !creating.lat || !creating.lon) { setMsg("Name, lat, lon required"); return }
    setSaving(true); setMsg(null)
    try {
      await api.shelters.create(token, {
        name: creating.name,
        lat: parseFloat(creating.lat),
        lon: parseFloat(creating.lon),
        address: creating.address || null,
        capacity: creating.capacity ? parseInt(creating.capacity) : null,
        phone: creating.phone || null,
      })
      setMsg(`Added ${creating.name}.`)
      setCreating({ name: "", lat: "", lon: "", address: "", capacity: "", phone: "" })
      await load()
    } catch { setMsg("Create failed") } finally { setSaving(false) }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 pt-4 pb-3 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-blue-900/40 border border-blue-700/40 flex items-center justify-center">
            <ClipboardCheck className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-foreground">Manage Shelters</h1>
            <p className="text-[10px] text-muted-foreground">Confirm accessibility on real shelters · add local facilities</p>
          </div>
        </div>
        {msg && <p className="mt-2 text-[11px] text-blue-300">{msg}</p>}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4">
        {/* Add facility */}
        <div className="rounded-xl border border-border bg-card p-3">
          <p className="text-xs font-semibold text-foreground mb-2 flex items-center gap-1"><Plus className="h-3 w-3" /> Add a facility</p>
          <div className="grid grid-cols-2 gap-2">
            <input className="col-span-2 bg-muted border border-border rounded px-2 py-1 text-xs" placeholder="Name (e.g. Lincoln High School)" value={creating.name} onChange={(e) => setCreating({ ...creating, name: e.target.value })} />
            <input className="bg-muted border border-border rounded px-2 py-1 text-xs" placeholder="Latitude" value={creating.lat} onChange={(e) => setCreating({ ...creating, lat: e.target.value })} />
            <input className="bg-muted border border-border rounded px-2 py-1 text-xs" placeholder="Longitude" value={creating.lon} onChange={(e) => setCreating({ ...creating, lon: e.target.value })} />
            <input className="col-span-2 bg-muted border border-border rounded px-2 py-1 text-xs" placeholder="Address" value={creating.address} onChange={(e) => setCreating({ ...creating, address: e.target.value })} />
            <input className="bg-muted border border-border rounded px-2 py-1 text-xs" placeholder="Capacity" value={creating.capacity} onChange={(e) => setCreating({ ...creating, capacity: e.target.value })} />
            <input className="bg-muted border border-border rounded px-2 py-1 text-xs" placeholder="Phone" value={creating.phone} onChange={(e) => setCreating({ ...creating, phone: e.target.value })} />
          </div>
          <button onClick={addFacility} disabled={saving} className="mt-2 w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded px-3 py-1.5 flex items-center justify-center gap-1">
            {saving ? <Loader2 className="h-3 w-3 animate-spin" /> : <Plus className="h-3 w-3" />} Add facility
          </button>
        </div>

        {/* Shelter list */}
        <div className="flex flex-col gap-1.5">
          <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{shelters.length} shelters</p>
          {shelters.map((s) => (
            <button key={s.id} onClick={() => setSelected(s)}
              className={`text-left rounded-lg border px-3 py-2 text-xs ${selected?.id === s.id ? "border-blue-500/50 bg-blue-950/30" : "border-border bg-card hover:bg-white/5"}`}>
              <span className="font-medium text-foreground">{s.name}</span>
              <span className="ml-2 text-[10px] text-muted-foreground">{s.verified_by ? "✓ verified" : s.source}</span>
            </button>
          ))}
        </div>

        {/* Edit selected */}
        {selected && (
          <div className="rounded-xl border border-blue-500/40 bg-blue-950/20 p-3 flex flex-col gap-2">
            <p className="text-xs font-semibold text-foreground">{selected.name}</p>
            {ACCESS_FIELDS.map((f) => (
              <TriSelect key={f.key} label={f.label}
                value={toTri(selected[f.key] as boolean | null)}
                onChange={(v) => setSelected({ ...selected, [f.key]: fromTri(v) })} />
            ))}
            <label className="flex items-center justify-between gap-2 text-xs text-foreground">
              <span>Pet policy</span>
              <select value={selected.pet_policy} onChange={(e) => setSelected({ ...selected, pet_policy: e.target.value })}
                className="bg-muted border border-border rounded px-2 py-1 text-xs">
                {["unknown", "no_pets", "service_animals_only", "pets_allowed"].map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>
            <label className="flex items-center justify-between gap-2 text-xs text-foreground">
              <span>Status</span>
              <select value={selected.status} onChange={(e) => setSelected({ ...selected, status: e.target.value })}
                className="bg-muted border border-border rounded px-2 py-1 text-xs">
                {["open", "full", "closed"].map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </label>
            <button onClick={saveAccessibility} disabled={saving}
              className="mt-1 w-full bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white text-xs font-medium rounded px-3 py-1.5 flex items-center justify-center gap-1">
              {saving ? <Loader2 className="h-3 w-3 animate-spin" /> : <ClipboardCheck className="h-3 w-3" />} Save &amp; verify
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
