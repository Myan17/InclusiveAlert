#!/usr/bin/env python3
"""
Seed script: gets a token, checks alerts, creates a respondent, checks matching.
Run from the repo root: python3 inclusive-alert/seed.py
"""
import urllib.request
import urllib.parse
import json

BASE = "http://127.0.0.1:8001"

def post(path, data, headers=None, form=False):
    if form:
        body = urllib.parse.urlencode(data).encode()
        ct = "application/x-www-form-urlencoded"
    else:
        body = json.dumps(data).encode()
        ct = "application/json"
    h = {"Content-Type": ct}
    if headers:
        h.update(headers)
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def get(path, token=None):
    h = {}
    if token:
        h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

print("=" * 60)
print("1. Login as testuser@ia.dev")
login = post("/auth/login", {"username": "testuser@ia.dev", "password": "Test123!"}, form=True)
print(json.dumps(login, indent=2))
token = login.get("access_token")

if not token:
    print("Login failed — trying to register first...")
    reg = post("/auth/register", {"email": "testuser@ia.dev", "password": "Test123!", "role": "victim"})
    print(json.dumps(reg, indent=2))
    login = post("/auth/login", {"username": "testuser@ia.dev", "password": "Test123!"}, form=True)
    token = login.get("access_token")
    print("Token:", token[:40] + "..." if token else "FAILED")

print("\n" + "=" * 60)
print("2. Check active alerts")
alerts = get("/alerts/active", token)
if isinstance(alerts, list):
    print(f"  {len(alerts)} active alerts")
    for a in alerts[:3]:
        print(f"  - [{a.get('severity')}] {a.get('headline') or a.get('hazard_type')} ({a.get('source')})")
else:
    print(json.dumps(alerts, indent=2))

print("\n" + "=" * 60)
print("3. Register respondent account")
resp_reg = post("/auth/register", {"email": "responder@ia.dev", "password": "Test123!", "role": "respondent"})
print(json.dumps(resp_reg, indent=2))

print("\n" + "=" * 60)
print("4. Login as respondent")
resp_login = post("/auth/login", {"username": "responder@ia.dev", "password": "Test123!"}, form=True)
resp_token = resp_login.get("access_token")
print("Respondent token:", resp_token[:40] + "..." if resp_token else "FAILED")

print("\n" + "=" * 60)
print("5. Create respondent profile (available, near Minneapolis)")
profile = post("/profiles/respondent", {
    "skills": ["asl", "cpr", "medication_admin"],
    "languages": ["en", "es"],
    "asl_level": "fluent",
    "vehicle_type": "van_wheelchair",
    "vetting_tier": "trained_volunteer",
    "availability_status": "available",
    "max_radius_km": 50.0,
    "location_lat": 44.9778,
    "location_lon": -93.2650,
    "location_zip": "55403",
}, headers={"Authorization": f"Bearer {resp_token}"})
print(json.dumps(profile, indent=2))

print("\n" + "=" * 60)
print("6. Check matching (victim near Minneapolis)")
matches = get("/matching/assign?lat=44.9778&lon=-93.2650", token)
print(json.dumps(matches, indent=2))

print("\n" + "=" * 60)
print("7. Check shelters near Minneapolis")
shelters = get("/shelters/ranked?lat=44.9778&lon=-93.2650&radius_km=80", token)
if isinstance(shelters, list):
    print(f"  {len(shelters)} shelters found")
    for s in shelters[:3]:
        print(f"  - {s.get('name')} | score={s.get('shelter_score')} | {s.get('distance_km', 0):.1f}km")
else:
    print(json.dumps(shelters, indent=2))

print("\nDone!")
