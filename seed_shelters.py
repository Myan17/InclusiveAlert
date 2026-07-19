#!/usr/bin/env python3
"""Seed the 5 Houston demo shelters into the (Render) Postgres DB over SSL."""
import sys
import psycopg2

DB_URL = sys.argv[1]

SHELTERS = [
    ("George R. Brown Convention Center", "1001 Avenida de las Americas, Houston, TX 77010",
     29.7527, -95.3601, True, True, True, "service_animals_only", True, 10000, 3200, "open"),
    ("NRG Center — Special Needs Shelter", "1 NRG Park, Houston, TX 77054",
     29.6850, -95.4100, True, True, True, "service_animals_only", True, 2000, 450, "open"),
    ("Delmar Stadium Community Shelter", "2020 Mangum Rd, Houston, TX 77092",
     29.8050, -95.4350, True, False, True, "pets_allowed", False, 1500, 890, "open"),
    ("Pasadena Convention Center", "7902 Fairmont Pkwy, Pasadena, TX 77507",
     29.6910, -95.2090, True, True, False, "no_pets", False, 800, 120, "open"),
    ("Katy High School Emergency Shelter", "6331 Highway Blvd, Katy, TX 77494",
     29.7858, -95.8244, False, False, False, "no_pets", False, 600, 600, "full"),
]

conn = psycopg2.connect(DB_URL, sslmode="require")
conn.autocommit = False
cur = conn.cursor()

# Introspect NOT NULL columns without a default so we never violate a constraint.
cur.execute("""
    SELECT column_name, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'shelters' ORDER BY ordinal_position
""")
cols = cur.fetchall()
print("shelters columns:", [(c[0], c[1]) for c in cols])
required = [c[0] for c in cols if c[1] == "NO" and c[2] is None
            and c[0] not in ("id", "location", "lat", "lon", "name", "address",
                             "status", "capacity", "current_occupancy",
                             "wheelchair_accessible", "ada_compliant", "generator_onsite",
                             "pet_policy", "asl_support", "source", "created_at")]
print("other required cols to handle:", required)

# Idempotent: clear any prior demo_seed rows first.
cur.execute("DELETE FROM shelters WHERE source = 'demo_seed'")

has_pop = any(c[0] == "population_types" for c in cols)
for (name, addr, lat, lon, wc, ada, gen, pet, asl, cap, occ, status) in SHELTERS:
    extra_col = ", population_types" if has_pop else ""
    extra_val = ", '[]'::json" if has_pop else ""
    cur.execute(f"""
        INSERT INTO shelters (
            id, name, address, location, status, capacity, current_occupancy,
            wheelchair_accessible, ada_compliant, generator_onsite,
            pet_policy, asl_support, source, created_at{extra_col}
        ) VALUES (
            gen_random_uuid(), %s, %s,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326),
            %s, %s, %s, %s, %s, %s, %s, %s, 'demo_seed', NOW(){extra_val}
        )
    """, (name, addr, lon, lat, status, cap, occ, wc, ada, gen, pet, asl))

conn.commit()
cur.execute("SELECT count(*) FROM shelters WHERE source = 'demo_seed'")
print("demo_seed shelters now in DB:", cur.fetchone()[0])
cur.close()
conn.close()
print("OK")
