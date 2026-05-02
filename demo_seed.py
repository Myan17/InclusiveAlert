#!/usr/bin/env python3
"""
InclusiveAlert Demo Seed Script
================================
Populates the database with realistic demo data for a compelling presentation:
  - 3 victim accounts with different disability profiles
  - 5 respondent accounts with varied skills (ASL, medical, mobility, etc.)
  - 6 realistic hazard alerts (tornado, flood, earthquake, wildfire, heat, hurricane)
  - 5 shelters with accessibility attributes

Usage:
    python3 inclusive-alert/demo_seed.py

After running, log in with any of these accounts at http://localhost:3001
  victim1@demo.ia  / Demo123!   (Deaf + Wheelchair user)
  victim2@demo.ia  / Demo123!   (Power dependent + blind)
  victim3@demo.ia  / Demo123!   (Service animal + medication)
  responder1@demo.ia / Demo123! (ASL fluent, medical)
  authority@demo.ia  / Demo123! (Authority role)
"""

import urllib.request
import urllib.parse
import json
import sys
from datetime import datetime, timezone, timedelta

BASE = "http://127.0.0.1:8001"

# ── helpers ──────────────────────────────────────────────────────────────────

def post(path, data, token=None, form=False):
    if form:
        body = urllib.parse.urlencode(data).encode()
        ct = "application/x-www-form-urlencoded"
    else:
        body = json.dumps(data).encode()
        ct = "application/json"
    headers = {"Content-Type": ct}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def get(path, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def register_and_login(email, password, role):
    resp, status = post("/auth/register", {"email": email, "password": password, "role": role})
    if status not in (200, 201) and "already registered" not in str(resp):
        print(f"  ⚠ Register {email}: {resp}")
    login_resp, _ = post("/auth/login", {"username": email, "password": password}, form=True)
    token = login_resp.get("access_token")
    if not token:
        print(f"  ✗ Login failed for {email}: {login_resp}")
        sys.exit(1)
    return token

def ok(label):
    print(f"  ✓ {label}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ── 1. Victims ────────────────────────────────────────────────────────────────

section("1. Creating victim accounts")

v1_token = register_and_login("victim1@demo.ia", "Demo123!", "victim")
post("/profiles/victim", {
    "disability_needs": ["deaf", "mobility_wheelchair"],
    "communication_modes": ["asl", "text", "haptic"],
    "mobility_aids": ["power_wheelchair"],
    "service_animal": False,
    "power_dependency": False,
    "preferred_language": "en",
    "location_zip": "77001",
    "location_city": "Houston",
    "location_state": "TX",
}, token=v1_token)
ok("victim1@demo.ia — Deaf + Wheelchair (Houston, TX)")

v2_token = register_and_login("victim2@demo.ia", "Demo123!", "victim")
post("/profiles/victim", {
    "disability_needs": ["blind", "power_dependent"],
    "communication_modes": ["voice", "text"],
    "medical_equipment": ["ventilator", "oxygen_concentrator"],
    "power_dependency": True,
    "service_animal": True,
    "preferred_language": "en",
    "location_zip": "77002",
    "location_city": "Houston",
    "location_state": "TX",
}, token=v2_token)
ok("victim2@demo.ia — Blind + Power Dependent + Service Animal (Houston, TX)")

v3_token = register_and_login("victim3@demo.ia", "Demo123!", "victim")
post("/profiles/victim", {
    "disability_needs": ["mobility_wheelchair"],
    "communication_modes": ["voice", "text"],
    "medication_dependency": True,
    "service_animal": True,
    "power_dependency": False,
    "preferred_language": "es",
    "location_zip": "77003",
    "location_city": "Houston",
    "location_state": "TX",
}, token=v3_token)
ok("victim3@demo.ia — Wheelchair + Medication + Service Animal, Spanish (Houston, TX)")

# ── 2. Respondents ────────────────────────────────────────────────────────────

section("2. Creating respondent accounts")

r1_token = register_and_login("responder1@demo.ia", "Demo123!", "respondent")
post("/profiles/respondent", {
    "skills": ["asl_interpreter", "sign_language", "first_aid", "cpr", "medication_admin"],
    "languages": ["en", "asl"],
    "asl_level": "native",
    "vehicle_type": "van_wheelchair",
    "equipment": ["wheelchair_ramp", "first_aid_kit", "aed"],
    "vetting_tier": "medical",
    "availability_status": "available",
    "max_radius_km": 30.0,
    "location_lat": 29.7604,
    "location_lon": -95.3698,
    "location_zip": "77004",
    "organization_id": "Houston_Deaf_Services",
    "background_verified": True,
}, token=r1_token)
ok("responder1@demo.ia — ASL Native + Medical + Wheelchair Van (Houston)")

r2_token = register_and_login("responder2@demo.ia", "Demo123!", "respondent")
post("/profiles/respondent", {
    "skills": ["guide_assistant", "first_aid", "cpr", "mobility_assistant"],
    "languages": ["en", "es"],
    "asl_level": "basic",
    "vehicle_type": "suv",
    "equipment": ["first_aid_kit", "white_cane_supply", "portable_generator"],
    "vetting_tier": "ngo",
    "availability_status": "available",
    "max_radius_km": 50.0,
    "location_lat": 29.7500,
    "location_lon": -95.3800,
    "location_zip": "77005",
    "organization_id": "Houston_Red_Cross",
    "background_verified": True,
}, token=r2_token)
ok("responder2@demo.ia — Guide + Mobility + Bilingual EN/ES (Houston)")

r3_token = register_and_login("responder3@demo.ia", "Demo123!", "respondent")
post("/profiles/respondent", {
    "skills": ["medical_technician", "first_aid", "cpr", "medication_admin", "oxygen_management"],
    "languages": ["en"],
    "asl_level": "none",
    "vehicle_type": "van_wheelchair",
    "equipment": ["portable_oxygen", "portable_generator", "medical_bag", "aed"],
    "vetting_tier": "medical",
    "availability_status": "available",
    "max_radius_km": 25.0,
    "location_lat": 29.7700,
    "location_lon": -95.3600,
    "location_zip": "77006",
    "organization_id": "Houston_EMS_Volunteer",
    "background_verified": True,
}, token=r3_token)
ok("responder3@demo.ia — Medical Tech + Oxygen + Generator (Houston)")

r4_token = register_and_login("responder4@demo.ia", "Demo123!", "respondent")
post("/profiles/respondent", {
    "skills": ["first_aid", "mobility_assistant", "animal_handler"],
    "languages": ["en", "es"],
    "asl_level": "none",
    "vehicle_type": "suv",
    "equipment": ["first_aid_kit", "pet_carrier"],
    "vetting_tier": "trained_volunteer",
    "availability_status": "available",
    "max_radius_km": 20.0,
    "location_lat": 29.7400,
    "location_lon": -95.3900,
    "location_zip": "77007",
    "background_verified": False,
}, token=r4_token)
ok("responder4@demo.ia — Animal Handler + Mobility (Houston)")

r5_token = register_and_login("responder5@demo.ia", "Demo123!", "respondent")
post("/profiles/respondent", {
    "skills": ["asl_interpreter", "sign_language", "guide_assistant", "first_aid"],
    "languages": ["en", "asl", "es"],
    "asl_level": "fluent",
    "vehicle_type": "van_wheelchair",
    "equipment": ["wheelchair_ramp", "first_aid_kit"],
    "vetting_tier": "authority_verified",
    "availability_status": "available",
    "max_radius_km": 40.0,
    "location_lat": 29.7550,
    "location_lon": -95.3750,
    "location_zip": "77008",
    "organization_id": "FEMA_Region6",
    "background_verified": True,
}, token=r5_token)
ok("responder5@demo.ia — ASL Fluent + FEMA Verified (Houston)")

# ── 3. Authority ──────────────────────────────────────────────────────────────

section("3. Creating authority account")
auth_token = register_and_login("authority@demo.ia", "Demo123!", "authority")
ok("authority@demo.ia — Emergency Operations Center")

# ── 4. Hazard Alerts ──────────────────────────────────────────────────────────

section("4. Seeding hazard alerts")

now = datetime.now(timezone.utc)

ALERTS = [
    {
        "external_id": "DEMO-NWS-TORNADO-001",
        "source": "nws",
        "hazard_type": "tornado_warning",
        "severity": "Extreme",
        "certainty": "Observed",
        "urgency": "Immediate",
        "headline": "TORNADO WARNING — Harris County TX until 9:45 PM CDT",
        "description": (
            "A CONFIRMED TORNADO has been detected by radar near Katy, TX moving northeast "
            "at 35 mph. This is a PARTICULARLY DANGEROUS SITUATION. Take shelter immediately "
            "in an interior room on the lowest floor of a sturdy building. Avoid windows."
        ),
        "instruction": (
            "🧏 ASL VIDEO: bit.ly/ia-tornado-asl | "
            "♿ Wheelchair users: move to interior hallway, away from windows. "
            "⚡ Power-dependent: activate backup power NOW. "
            "🐕 Service animals: keep leashed and sheltered with you."
        ),
        "area_description": "Harris County, Fort Bend County, Waller County TX",
        "effective_at": (now - timedelta(minutes=10)).isoformat(),
        "expires_at": (now + timedelta(hours=2)).isoformat(),
        "source_confidence": 0.98,
    },
    {
        "external_id": "DEMO-NWS-FLOOD-001",
        "source": "nws",
        "hazard_type": "flash_flood_warning",
        "severity": "Severe",
        "certainty": "Likely",
        "urgency": "Immediate",
        "headline": "FLASH FLOOD WARNING — Buffalo Bayou rising rapidly",
        "description": (
            "Flash flooding is occurring or imminent. Buffalo Bayou at Shepherd Drive "
            "is at 28.4 feet and rising. Flood stage is 25 feet. Do not attempt to "
            "drive through flooded roadways. Turn Around, Don't Drown."
        ),
        "instruction": (
            "🧏 ASL VIDEO: bit.ly/ia-flood-asl | "
            "♿ Wheelchair users: do NOT attempt to navigate flooded streets. Request evacuation assistance. "
            "⚡ Power-dependent: move medical equipment to highest floor immediately. "
            "🐕 Service animals: keep on leash, avoid floodwater."
        ),
        "area_description": "Houston Metro Area — Bayou corridors, Meyerland, Braeswood",
        "effective_at": (now - timedelta(minutes=30)).isoformat(),
        "expires_at": (now + timedelta(hours=6)).isoformat(),
        "source_confidence": 0.95,
    },
    {
        "external_id": "DEMO-NWS-HEAT-001",
        "source": "nws",
        "hazard_type": "excessive_heat_warning",
        "severity": "Severe",
        "certainty": "Likely",
        "urgency": "Expected",
        "headline": "EXCESSIVE HEAT WARNING — Heat index up to 115°F through Sunday",
        "description": (
            "Dangerously hot conditions expected. Heat index values up to 115°F. "
            "The combination of hot temperatures and high humidity will create a "
            "dangerous situation. Drink plenty of fluids, stay in air-conditioned rooms."
        ),
        "instruction": (
            "🧏 ASL VIDEO: bit.ly/ia-heat-asl | "
            "⚡ Power-dependent: ensure backup cooling is operational. "
            "♿ Wheelchair users: avoid outdoor exposure between 10am–6pm. "
            "💊 Medication-dependent: store medications below 77°F — check with pharmacist."
        ),
        "area_description": "Greater Houston Metropolitan Area",
        "effective_at": (now - timedelta(hours=2)).isoformat(),
        "expires_at": (now + timedelta(days=2)).isoformat(),
        "source_confidence": 0.92,
    },
    {
        "external_id": "DEMO-USGS-EQ-001",
        "source": "usgs",
        "hazard_type": "earthquake",
        "severity": "Moderate",
        "certainty": "Observed",
        "urgency": "Immediate",
        "headline": "M4.2 Earthquake — 12 miles NW of Houston, TX",
        "description": (
            "A magnitude 4.2 earthquake occurred at 2:34 PM local time. "
            "Depth: 8.3 km. Shaking felt across Harris and Montgomery counties. "
            "Check for structural damage before re-entering buildings."
        ),
        "instruction": (
            "🧏 ASL VIDEO: bit.ly/ia-eq-asl | "
            "♿ Wheelchair users: check for debris blocking exit routes. "
            "⚡ Power-dependent: check that medical equipment is undamaged. "
            "🐕 Service animals may be distressed — keep calm and reassure them."
        ),
        "area_description": "Harris County, Montgomery County TX",
        "effective_at": (now - timedelta(hours=1)).isoformat(),
        "expires_at": (now + timedelta(hours=12)).isoformat(),
        "source_confidence": 0.99,
    },
    {
        "external_id": "DEMO-NWS-HURRICANE-001",
        "source": "nws",
        "hazard_type": "hurricane_watch",
        "severity": "Extreme",
        "certainty": "Possible",
        "urgency": "Expected",
        "headline": "HURRICANE WATCH — Category 3 storm projected landfall 72 hrs",
        "description": (
            "Hurricane Helene has strengthened to Category 3 with 125 mph winds. "
            "Projected landfall near Galveston in 72 hours. Mandatory evacuation orders "
            "expected for Zone A and Zone B. Begin preparations now."
        ),
        "instruction": (
            "🧏 ASL VIDEO: bit.ly/ia-hurricane-asl | "
            "♿ Wheelchair users: register with Special Needs Registry NOW at 713-SPECIAL. "
            "⚡ Power-dependent: contact your power company's medical baseline program. "
            "🐕 Service animals: confirm pet-friendly shelter availability before evacuating. "
            "💊 Medication: obtain 7-day emergency supply from pharmacy."
        ),
        "area_description": "Galveston County, Brazoria County, Harris County TX — Coastal Zones",
        "effective_at": now.isoformat(),
        "expires_at": (now + timedelta(days=4)).isoformat(),
        "source_confidence": 0.87,
    },
    {
        "external_id": "DEMO-NWS-WINTER-001",
        "source": "nws",
        "hazard_type": "winter_storm_warning",
        "severity": "Severe",
        "certainty": "Likely",
        "urgency": "Expected",
        "headline": "WINTER STORM WARNING — 6–10 inches of snow, ice accumulation",
        "description": (
            "A significant winter storm will impact the region beginning tonight. "
            "Heavy snow 6–10 inches with ice accumulation of 0.25–0.5 inches. "
            "Power outages likely. Roads will become impassable."
        ),
        "instruction": (
            "🧏 ASL VIDEO: bit.ly/ia-winter-asl | "
            "⚡ Power-dependent: CRITICAL — charge all backup devices, contact utility for priority restoration. "
            "♿ Wheelchair users: power wheelchairs may fail in extreme cold — have manual backup. "
            "💊 Medication-dependent: ensure 72-hour medication supply at home."
        ),
        "area_description": "Northern Harris County, Montgomery County, Liberty County TX",
        "effective_at": (now + timedelta(hours=6)).isoformat(),
        "expires_at": (now + timedelta(days=2)).isoformat(),
        "source_confidence": 0.90,
    },
]

# Use admin token to insert alerts directly via a special endpoint,
# or insert via the DB using the API's internal structure.
# Since there's no admin POST /alerts endpoint, we use the auth token
# and call a direct DB insert via the existing session.
# We'll use the authority token and call the internal seed endpoint we'll add,
# OR we insert via psql. For now, use the Python DB approach via subprocess.

import subprocess
import os

SEED_SQL = ""
for a in ALERTS:
    eid = a["external_id"]
    src = a["source"]
    ht = a["hazard_type"]
    sev = a["severity"]
    cert = a["certainty"]
    urg = a["urgency"]
    headline = a["headline"].replace("'", "''")
    desc = a["description"].replace("'", "''")
    instr = a["instruction"].replace("'", "''")
    area = a["area_description"].replace("'", "''")
    eff = a["effective_at"]
    exp = a["expires_at"]
    conf = a["source_confidence"]

    SEED_SQL += f"""
INSERT INTO hazard_events (
    id, external_id, source, hazard_type, severity, certainty, urgency,
    headline, description, instruction, area_description,
    effective_at, expires_at, source_confidence, is_active, ingested_at
) VALUES (
    gen_random_uuid(), '{eid}', '{src}', '{ht}', '{sev}', '{cert}', '{urg}',
    '{headline}', '{desc}', '{instr}', '{area}',
    '{eff}', '{exp}', {conf}, true, NOW()
) ON CONFLICT (external_id) DO UPDATE SET
    headline = EXCLUDED.headline,
    description = EXCLUDED.description,
    instruction = EXCLUDED.instruction,
    expires_at = EXCLUDED.expires_at,
    is_active = true;
"""

# Write SQL to temp file and run via docker exec
sql_file = "/tmp/ia_demo_seed.sql"
with open(sql_file, "w") as f:
    f.write(SEED_SQL)

result = subprocess.run(
    ["docker", "exec", "-i", "inclusive-alert-db-1",
     "psql", "-U", "ia_user", "-d", "inclusivealert"],
    input=SEED_SQL, capture_output=True, text=True
)
if result.returncode != 0:
    # Try alternate container name
    result = subprocess.run(
        ["docker", "exec", "-i", "inclusive-alert-db-1",
         "psql", "-U", "ia_user", "-d", "inclusivealert"],
        input=SEED_SQL, capture_output=True, text=True
    )

if result.returncode == 0:
    ok(f"Inserted {len(ALERTS)} hazard alerts into DB")
else:
    # Fallback: try to find the container
    containers = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True
    ).stdout.strip().split("\n")
    db_container = next((c for c in containers if "db" in c.lower() and "inclusive" in c.lower()), None)
    if db_container:
        result2 = subprocess.run(
            ["docker", "exec", "-i", db_container,
             "psql", "-U", "ia_user", "-d", "inclusivealert"],
            input=SEED_SQL, capture_output=True, text=True
        )
        if result2.returncode == 0:
            ok(f"Inserted {len(ALERTS)} hazard alerts via container '{db_container}'")
        else:
            print(f"  ✗ DB insert failed: {result2.stderr[:200]}")
            print("  → Run manually: docker exec -i <db-container> psql -U ia_user -d inclusivealert < /tmp/ia_demo_seed.sql")
    else:
        print(f"  ✗ Could not find DB container. stderr: {result.stderr[:200]}")
        print(f"  → SQL written to {sql_file} — run manually.")

# ── 5. Shelters (via DB) ──────────────────────────────────────────────────────

section("5. Seeding demo shelters")

SHELTER_SQL = ""
SHELTERS = [
    {
        "name": "George R. Brown Convention Center",
        "address": "1001 Avenida de las Americas, Houston, TX 77010",
        "lat": 29.7527, "lon": -95.3601,
        "wheelchair": True, "ada": True, "generator": True,
        "pet_policy": "service_animals_only", "asl_support": True,
        "capacity": 10000, "occupancy": 3200, "status": "open",
    },
    {
        "name": "NRG Center — Special Needs Shelter",
        "address": "1 NRG Park, Houston, TX 77054",
        "lat": 29.6850, "lon": -95.4100,
        "wheelchair": True, "ada": True, "generator": True,
        "pet_policy": "service_animals_only", "asl_support": True,
        "capacity": 2000, "occupancy": 450, "status": "open",
    },
    {
        "name": "Delmar Stadium Community Shelter",
        "address": "2020 Mangum Rd, Houston, TX 77092",
        "lat": 29.8050, "lon": -95.4350,
        "wheelchair": True, "ada": False, "generator": True,
        "pet_policy": "pets_allowed", "asl_support": False,
        "capacity": 1500, "occupancy": 890, "status": "open",
    },
    {
        "name": "Pasadena Convention Center",
        "address": "7902 Fairmont Pkwy, Pasadena, TX 77507",
        "lat": 29.6910, "lon": -95.2090,
        "wheelchair": True, "ada": True, "generator": False,
        "pet_policy": "no_pets", "asl_support": False,
        "capacity": 800, "occupancy": 120, "status": "open",
    },
    {
        "name": "Katy High School Emergency Shelter",
        "address": "6331 Highway Blvd, Katy, TX 77494",
        "lat": 29.7858, "lon": -95.8244,
        "wheelchair": False, "ada": False, "generator": False,
        "pet_policy": "no_pets", "asl_support": False,
        "capacity": 600, "occupancy": 600, "status": "full",
    },
]

for s in SHELTERS:
    name = s["name"].replace("'", "''")
    addr = s["address"].replace("'", "''")
    SHELTER_SQL += f"""
INSERT INTO shelters (
    id, name, address, location, status, capacity, current_occupancy,
    wheelchair_accessible, ada_compliant, generator_onsite,
    pet_policy, asl_support, source, created_at
) VALUES (
    gen_random_uuid(),
    '{name}', '{addr}',
    ST_SetSRID(ST_MakePoint({s['lon']}, {s['lat']}), 4326),
    '{s['status']}', {s['capacity']}, {s['occupancy']},
    {str(s['wheelchair']).lower()}, {str(s['ada']).lower()}, {str(s['generator']).lower()},
    '{s['pet_policy']}', {str(s['asl_support']).lower()},
    'demo_seed', NOW()
) ON CONFLICT DO NOTHING;
"""

containers = subprocess.run(
    ["docker", "ps", "--format", "{{.Names}}"],
    capture_output=True, text=True
).stdout.strip().split("\n")
db_container = next((c for c in containers if "db" in c.lower() and "inclusive" in c.lower()), None)
if not db_container:
    db_container = "inclusive-alert-db-1"

result = subprocess.run(
    ["docker", "exec", "-i", db_container,
     "psql", "-U", "ia_user", "-d", "inclusivealert"],
    input=SHELTER_SQL, capture_output=True, text=True
)
if result.returncode == 0:
    ok(f"Inserted {len(SHELTERS)} shelters into DB")
else:
    print(f"  ✗ Shelter insert failed: {result.stderr[:200]}")

# ── 6. Verify ─────────────────────────────────────────────────────────────────

section("6. Verification")

alerts_resp, _ = get("/alerts/active", v1_token)
print(f"  Active alerts visible: {len(alerts_resp) if isinstance(alerts_resp, list) else '?'}")

matches_resp, _ = get("/matching/assign?lat=29.7604&lon=-95.3698", v1_token)
if isinstance(matches_resp, dict):
    print(f"  Respondents matched for victim1: {matches_resp.get('total', 0)}")
    for r in matches_resp.get("results", [])[:3]:
        print(f"    - {r['respondent_id'][:8]}… score={r['score']}")

# ── Summary ───────────────────────────────────────────────────────────────────

section("DEMO READY ✓")
print("""
  Login accounts (password: Demo123! for all):
  ┌─────────────────────────┬────────────┬──────────────────────────────────────┐
  │ Email                   │ Role       │ Profile                              │
  ├─────────────────────────┼────────────┼──────────────────────────────────────┤
  │ victim1@demo.ia         │ victim     │ Deaf + Wheelchair, Houston TX        │
  │ victim2@demo.ia         │ victim     │ Blind + Power Dependent + Dog        │
  │ victim3@demo.ia         │ victim     │ Wheelchair + Medication, Spanish     │
  │ responder1@demo.ia      │ respondent │ ASL Native + Medical + Wheelchair Van│
  │ responder2@demo.ia      │ respondent │ Guide + Mobility + EN/ES             │
  │ responder3@demo.ia      │ respondent │ Medical Tech + Oxygen Equipment      │
  │ authority@demo.ia       │ authority  │ Emergency Operations Center          │
  └─────────────────────────┴────────────┴──────────────────────────────────────┘

  Demo flow:
  1. Login as victim1@demo.ia → Alerts tab shows 6 active alerts
  2. Each alert has ASL video links + disability-specific instructions
  3. Matching tab shows 5 ranked respondents with score breakdowns
  4. Shelters tab shows 5 Houston shelters with accessibility badges
  5. Profile tab shows Deaf + Wheelchair needs pre-filled
  6. Login as authority@demo.ia to show operator view
""")
