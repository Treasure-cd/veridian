import csv
import os
import sys
import uuid
from datetime import date, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import N_LEASES, OUTPUT_DIR, SEED

import random
random.seed(SEED + 3)


def load_csv(name):
    with open(f"{OUTPUT_DIR}/{name}", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


locations = load_csv("locations_sites.csv")
property_location_ids = [l["location_id"] for l in locations if l["site_type"] == "property"]
print(f"Found {len(property_location_ids):,} property-type locations to build on.")

DIVISION_CODES = ["RETAIL", "LOGISTICS", "VFS", "AGRI", "PROPERTIES", "GROUP"]


print("Generating tenants...")
tenants = []

INTERNAL_TENANT_DIVISIONS = ["RETAIL", "LOGISTICS", "AGRI"]
internal_tenant_ids = {}
for div in INTERNAL_TENANT_DIVISIONS:
    tid = str(uuid.uuid4())
    tenants.append({
        "tenant_id": tid, "tenant_type": "internal_division",
        "division_code": div, "external_tenant_name": "",
    })
    internal_tenant_ids[div] = tid

N_EXTERNAL_TENANTS = 40
external_tenant_ids = []
for _ in range(N_EXTERNAL_TENANTS):
    tid = str(uuid.uuid4())
    tenants.append({
        "tenant_id": tid, "tenant_type": "external",
        "division_code": "", "external_tenant_name": f"Tenant Enterprises {uuid.uuid4().hex[:6].upper()}",
    })
    external_tenant_ids.append(tid)

with open(f"{OUTPUT_DIR}/tenants.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=tenants[0].keys())
    writer.writeheader()
    writer.writerows(tenants)
print(f"  -> {OUTPUT_DIR}/tenants.csv ({len(tenants)} tenants: {len(INTERNAL_TENANT_DIVISIONS)} internal, {N_EXTERNAL_TENANTS} external)")

print("Generating properties...")
PROPERTY_TYPES = ["store_premises", "warehouse_depot", "processing_adjacent", "commercial", "residential"]
PROPERTY_TYPE_WEIGHTS = [0.35, 0.30, 0.10, 0.15, 0.10]  # roughly matches store+warehouse dominance from section 1.3

properties = []
for loc_id in property_location_ids:  # exactly 94 rows, one per property location
    ptype = random.choices(PROPERTY_TYPES, weights=PROPERTY_TYPE_WEIGHTS, k=1)[0]
    properties.append({
        "property_id": str(uuid.uuid4()),
        "location_id": loc_id,
        "property_type": ptype,
        "size_sqm": round(random.uniform(150, 5000), 2),
        "ownership_status": random.choices(["owned", "leased_in"], weights=[0.6, 0.4], k=1)[0],
    })

with open(f"{OUTPUT_DIR}/properties.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=properties[0].keys())
    writer.writeheader()
    writer.writerows(properties)
print(f"  -> {OUTPUT_DIR}/properties.csv ({len(properties)} properties)")


print("Generating leases...")
all_tenant_ids = list(internal_tenant_ids.values()) + external_tenant_ids
n_lease_target = N_LEASES // 2   # ~150, per the combined-target interpretation above

leases = []
tenant_has_active = set()

for _ in range(n_lease_target):
    prop = random.choice(properties)
    tenant_id = random.choice(all_tenant_ids)

    start = random_date(2019, 2025)
    end = start + timedelta(days=random.randint(365, 365 * 5))

    if tenant_id not in tenant_has_active and random.random() < 0.7:
        status = "active"
        tenant_has_active.add(tenant_id)
    else:
        status = random.choices(["expired", "terminated"], weights=[0.8, 0.2], k=1)[0]

    leases.append({
        "lease_id": str(uuid.uuid4()),
        "property_id": prop["property_id"],
        "tenant_id": tenant_id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "monthly_rent": round(random.uniform(50000, 3000000), 2),  # NGN
        "lease_status": status,
    })

with open(f"{OUTPUT_DIR}/leases.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=leases[0].keys())
    writer.writeheader()
    writer.writerows(leases)
print(f"  -> {OUTPUT_DIR}/leases.csv ({len(leases)} leases, {len(tenant_has_active)} tenants with an active lease)")


print("Generating maintenance requests...")
CATEGORIES = ["electrical", "plumbing", "structural", "hvac", "security", "other"]
n_maint_target = N_LEASES - n_lease_target  # ~150

maintenance_requests = []
for _ in range(n_maint_target):
    prop = random.choice(properties)
    requested = random_date(2024, 2026)
    status = random.choices(
        ["open", "in_progress", "resolved", "cancelled"],
        weights=[0.15, 0.15, 0.65, 0.05], k=1
    )[0]
    resolved = ""
    if status == "resolved":
        resolved = (requested + timedelta(days=random.randint(1, 30))).isoformat()

    maintenance_requests.append({
        "request_id": str(uuid.uuid4()),
        "property_id": prop["property_id"],
        "requested_date": requested.isoformat(),
        "category": random.choice(CATEGORIES),
        "status": status,
        "resolved_date": resolved,
    })

with open(f"{OUTPUT_DIR}/maintenance_requests.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=maintenance_requests[0].keys())
    writer.writeheader()
    writer.writerows(maintenance_requests)
print(f"  -> {OUTPUT_DIR}/maintenance_requests.csv ({len(maintenance_requests)} requests)")


print("Generating property valuations...")
property_valuations = []
for prop in properties:
    n_valuations = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
    for _ in range(n_valuations):
        property_valuations.append({
            "valuation_id": str(uuid.uuid4()),
            "property_id": prop["property_id"],
            "valuation_date": random_date(2020, 2026).isoformat(),
            "assessed_value": round(float(prop["size_sqm"]) * random.uniform(80000, 250000), 2),  # NGN per sqm, rough
        })

with open(f"{OUTPUT_DIR}/property_valuations.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=property_valuations[0].keys())
    writer.writeheader()
    writer.writerows(property_valuations)
print(f"  -> {OUTPUT_DIR}/property_valuations.csv ({len(property_valuations)} valuations)")


print("Generating utility accounts...")
UTILITY_TYPES = ["electricity", "water", "generator_diesel", "internet", "waste"]
PROVIDERS = {
    "electricity": ["Ikeja Electric", "Eko Electricity Distribution", "Abuja Electricity Distribution"],
    "water": ["Lagos Water Corporation", "State Water Board"],
    "generator_diesel": ["Local Diesel Supplier"],
    "internet": ["MTN Business", "Airtel Business", "Spectranet"],
    "waste": ["LAWMA", "Local Waste Management Co"],
}

utility_accounts = []
for prop in properties:
    n_utilities = random.randint(1, 3)
    chosen_types = random.sample(UTILITY_TYPES, k=min(n_utilities, len(UTILITY_TYPES)))
    for utype in chosen_types:
        utility_accounts.append({
            "utility_id": str(uuid.uuid4()),
            "property_id": prop["property_id"],
            "utility_type": utype,
            "provider_name": random.choice(PROVIDERS[utype]),
            "account_number": str(random.randint(10**9, 10**10 - 1)),
        })

with open(f"{OUTPUT_DIR}/utility_accounts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=utility_accounts[0].keys())
    writer.writeheader()
    writer.writerows(utility_accounts)
print(f"  -> {OUTPUT_DIR}/utility_accounts.csv ({len(utility_accounts)} accounts)")


print("Generating facility assets...")
ASSET_TYPES = ["Generator", "Cold storage unit", "Forklift", "HVAC unit", "Security camera system", "Elevator"]
CONDITIONS = ["excellent", "good", "fair", "poor"]
CONDITION_WEIGHTS = [0.2, 0.5, 0.25, 0.05]

facility_assets = []
for prop in properties:
    n_assets = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1], k=1)[0]
    for _ in range(n_assets):
        facility_assets.append({
            "asset_id": str(uuid.uuid4()),
            "property_id": prop["property_id"],
            "asset_type": random.choice(ASSET_TYPES),
            "installed_date": random_date(2015, 2026).isoformat(),
            "condition_rating": random.choices(CONDITIONS, weights=CONDITION_WEIGHTS, k=1)[0],
        })

with open(f"{OUTPUT_DIR}/facility_assets.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=facility_assets[0].keys())
    writer.writeheader()
    writer.writerows(facility_assets)
print(f"  -> {OUTPUT_DIR}/facility_assets.csv ({len(facility_assets)} assets)")

print("\nProperties module generation complete.")