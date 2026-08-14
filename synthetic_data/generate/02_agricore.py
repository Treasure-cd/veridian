import csv
import os
import sys
import uuid
from datetime import date, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import N_HARVEST_BATCHES, OUTPUT_DIR, SEED

import random
random.seed(SEED + 2)

CROPS = ["Maize", "Sorghum", "Cowpea", "Cassava", "Yam"]


def random_date(start_year=2019, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ── Load what we need from Core Hub output ──
def load_csv(name):
    with open(f"{OUTPUT_DIR}/{name}", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

suppliers = load_csv("suppliers_vendors.csv")
farmer_supplier_ids = [s["supplier_id"] for s in suppliers if s["supplier_type"] == "farmer"]
print(f"Found {len(farmer_supplier_ids):,} farmer-flagged suppliers to build on.")

locations = load_csv("locations_sites.csv")
facility_location_ids = [l["location_id"] for l in locations if l["site_type"] == "processing_facility"]
farm_location_ids_pool = [l["location_id"] for l in locations if l["site_type"] == "farm"]
if not farm_location_ids_pool:
    raise RuntimeError(
        "No 'farm' site_type locations found in locations_sites.csv. "
        "Re-run 01_core_hub.py after the update that adds farm_location_ids "
        "(requires migration 070_locations_add_farm_type.sql applied first)."
    )

products = load_csv("product_service_catalogue.csv")
agri_product_ids = [p["product_id"] for p in products if p["primary_division_code"] == "AGRI"]

employees = load_csv("employees.csv")
agri_employee_ids = [e["employee_id"] for e in employees if e["division_code"] == "AGRI"]
if not agri_employee_ids:
    raise RuntimeError("No AGRI employees found — check employees.csv was generated correctly.")



print(f"Generating {len(farmer_supplier_ids):,} farmer profiles...")
farmers = []
COOPERATIVES = ["Kano Grain Growers Coop", "Kaduna Smallholders Union",
                 "Northern Cowpea Alliance", ""]  # "" -> no cooperative (nullable)

for sid in farmer_supplier_ids:
    farmers.append({
        "farmer_id": str(uuid.uuid4()),
        "supplier_id": sid,
        "registration_date": random_date(2015, 2024).isoformat(),
        "cooperative_name": random.choice(COOPERATIVES),
    })

with open(f"{OUTPUT_DIR}/farmers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=farmers[0].keys())
    writer.writeheader()
    writer.writerows(farmers)
print(f"  -> {OUTPUT_DIR}/farmers.csv")



print("Generating farms...")
farms = []
for sid in farmer_supplier_ids:
    n_farms = random.choices([1, 2, 3], weights=[0.75, 0.20, 0.05], k=1)[0]
    for _ in range(n_farms):
        farms.append({
            "farm_id": str(uuid.uuid4()),
            "supplier_id": sid,
            "location_id": random.choice(farm_location_ids_pool),
            "size_hectares": round(random.uniform(0.5, 15.0), 2),
            "primary_crop": random.choice(CROPS),
        })

with open(f"{OUTPUT_DIR}/farms.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=farms[0].keys())
    writer.writeheader()
    writer.writerows(farms)
print(f"  -> {OUTPUT_DIR}/farms.csv ({len(farms):,} farms across {len(farmer_supplier_ids):,} farmers)")



print(f"Generating {N_HARVEST_BATCHES:,} harvest batches...")
farm_ids = [f["farm_id"] for f in farms]
harvest_batches = []

SEASON_START = date(2025, 9, 1)   # one representative seasonal cycle
SEASON_END = date(2026, 2, 28)
season_days = (SEASON_END - SEASON_START).days

for _ in range(N_HARVEST_BATCHES):
    harvest_batches.append({
        "harvest_id": str(uuid.uuid4()),
        "farm_id": random.choice(farm_ids),
        "product_id": random.choice(agri_product_ids),
        "harvest_date": (SEASON_START + timedelta(days=random.randint(0, season_days))).isoformat(),
        "volume_kg": round(random.uniform(50, 2000), 2),
        "field_agent_employee_id": random.choice(agri_employee_ids),
    })

with open(f"{OUTPUT_DIR}/harvest_batches.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=harvest_batches[0].keys())
    writer.writeheader()
    writer.writerows(harvest_batches)
print(f"  -> {OUTPUT_DIR}/harvest_batches.csv")


print("Generating processing runs...")
processing_runs = []
for hb in harvest_batches:
    if random.random() < 0.85:
        n_runs = random.choices([1, 2], weights=[0.9, 0.1], k=1)[0]
        for _ in range(n_runs):
            output_vol = round(float(hb["volume_kg"]) * random.uniform(0.6, 0.95) / n_runs, 2)
            run_date = date.fromisoformat(hb["harvest_date"]) + timedelta(days=random.randint(1, 10))
            processing_runs.append({
                "run_id": str(uuid.uuid4()),
                "harvest_id": hb["harvest_id"],
                "facility_location_id": random.choice(facility_location_ids),
                "run_date": run_date.isoformat(),
                "output_volume_kg": output_vol,
            })

with open(f"{OUTPUT_DIR}/processing_runs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=processing_runs[0].keys())
    writer.writeheader()
    writer.writerows(processing_runs)
print(f"  -> {OUTPUT_DIR}/processing_runs.csv ({len(processing_runs):,} runs from {len(harvest_batches):,} batches)")


print("Generating quality grades...")
quality_grades = []
for run in processing_runs:
    quality_grades.append({
        "grade_id": str(uuid.uuid4()),
        "run_id": run["run_id"],
        "grade_level": random.choices(["A", "B", "C", "reject"], weights=[0.35, 0.40, 0.20, 0.05], k=1)[0],
        "moisture_content": round(random.uniform(8.0, 18.0), 2),
        "inspector_employee_id": random.choice(agri_employee_ids),
    })

with open(f"{OUTPUT_DIR}/quality_grades.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=quality_grades[0].keys())
    writer.writeheader()
    writer.writerows(quality_grades)
print(f"  -> {OUTPUT_DIR}/quality_grades.csv")


print("Generating harvest payments...")
harvest_payments = []
for hb in harvest_batches:
    pay_date = date.fromisoformat(hb["harvest_date"]) + timedelta(days=random.randint(3, 21))
    status = random.choices(["paid", "pending", "failed"], weights=[0.85, 0.12, 0.03], k=1)[0]
    harvest_payments.append({
        "payment_id": str(uuid.uuid4()),
        "harvest_id": hb["harvest_id"],
        "amount": round(float(hb["volume_kg"]) * random.uniform(150, 400), 2),  # plausible NGN/kg rate
        "payment_date": pay_date.isoformat(),
        "payment_method": random.choices(["bank_transfer", "wallet", "cash"], weights=[0.5, 0.4, 0.1], k=1)[0],
        "status": status,
    })

with open(f"{OUTPUT_DIR}/harvest_payments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=harvest_payments[0].keys())
    writer.writeheader()
    writer.writerows(harvest_payments)
print(f"  -> {OUTPUT_DIR}/harvest_payments.csv")

print("\nAgriCore (self-contained tables) generation complete.")
print("REMAINING for a later cross-module pass: wholesale_shipments, farmer_loans_reference")