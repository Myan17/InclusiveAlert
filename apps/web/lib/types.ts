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
  asl_support: boolean
  pet_policy: "pets_allowed" | "no_pets" | "service_animals_only"
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

export interface RespondentProfile {
  id: string
  user_id: string
  skills: string[]
  languages: string[]
  asl_level: string
  vehicle_type: string | null
  equipment: string[]
  vetting_tier: string
  availability_status: AvailabilityStatus
  max_radius_km: number
  location_lat: number | null
  location_lon: number | null
  location_zip: string | null
  organization_id: string | null
  background_verified: boolean
  trust_tier: number
  communication_modes: string[]
}

export interface VictimSummary {
  user_id: string
  email: string
  disability_needs: string[]
  communication_modes: string[]
  service_animal: boolean
  power_dependency: boolean
  location_zip: string | null
  location_city: string | null
  location_state: string | null
  urgency_score: number
}

export interface VictimListResponse {
  victims: VictimSummary[]
  total: number
}
