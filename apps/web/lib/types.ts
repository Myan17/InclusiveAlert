// lib/types.ts
export type Role = "victim" | "respondent" | "authority"
export type Severity = "Extreme" | "Severe" | "Moderate" | "Minor" | "Unknown"
export type AvailabilityStatus = "available" | "on_break" | "unavailable"

export interface UserProfile {
  id: string
  email: string
  role: Role
  disability_needs: string[]
  mobility_aids: string[]
  communication_modes: string[]
  medical_equipment: string[]
  medication_dependency: boolean
  power_dependency: boolean
  service_animal: boolean
  preferred_language: string
  location_zip: string | null
  location_city: string | null
  location_state: string | null
}

export interface HazardEvent {
  id: string
  external_id: string
  source: string
  hazard_type: string
  severity: Severity
  certainty: string
  urgency: string
  headline: string | null
  description: string | null
  instruction: string | null
  area_description: string | null
  effective_at: string
  expires_at: string | null
  source_confidence: number
  is_active: boolean
}

export interface Shelter {
  name: string
  address: string | null
  distance_km: number
  wheelchair_accessible: boolean
  ada_compliant: boolean
  generator_onsite: boolean
  pet_policy: "pets_allowed" | "no_pets"
  status: string
  capacity: number | null
  current_occupancy: number | null
  shelter_score: number
  lat: number | null
  lon: number | null
  source: string
}

export interface MatchBreakdown {
  proximity: number
  skill_fit: number
  availability: number
  route_safety: number
  trust_tier: number
  communication_fit: number
}

export interface MatchResult {
  respondent_id: string
  score: number
  breakdown: MatchBreakdown
}

export interface MatchAssignmentResponse {
  results: MatchResult[]
  total: number
}
