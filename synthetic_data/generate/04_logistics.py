import csv
import os
import sys
import uuid
from datetime import date, datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import N_SHIPMENTS, OUTPUT_DIR, SEED

import random
random.seed(SEED + 4)

N_VEHICLES = 310
N_WAREHOUSES_TARGET = 6 
N_ROUTES = 40 
N_DRIVERS = 180 


def load_csv(name):
    with open(f"{OUTPUT_DIR}/{name}", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def random_datetime_in(start_year, end_year):
    d = random_date(start_year, end_year)
    return datetime(d.year, d.month, d.day, random.randint(5, 20), random.choice([0, 15, 30, 45]))


locations = load_csv("locations_sites.csv")
warehouse_location_ids = [l["location_id"] for l in locations if l["site_type"] == "warehouse"]
store_location_ids = [l["location_id"] for l in locations if l["site_type"] == "store"]
facility_location_ids = [l["location_id"] for l in locations if l["site_type"] == "processing_facility"]
farm_location_ids = [l["location_id"] for l in locations if l["site_type"] == "farm"]
shippable_location_ids = warehouse_location_ids + store_location_ids + facility_location_ids

employees = load_csv("employees.csv")
logistics_employee_ids = [e["employee_id"] for e in employees if e["division_code"] == "LOGISTICS"]
if not logistics_employee_ids:
    raise RuntimeError("No LOGISTICS employees found — check employees.csv.")

properties = load_csv("properties.csv")
warehouse_depot_property_ids = [p["property_id"] for p in properties if p["property_type"] == "warehouse_depot"]



print(f"Generating {N_VEHICLES} vehicles...")
vehicles = []
used_registration_numbers = set()
for i in range(N_VEHICLES):
    vtype = random.choices(["van", "truck"], weights=[0.4, 0.6], k=1)[0]
    while True:
        reg = f"VCH-{random.randint(100,999)}-{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}"
        if reg not in used_registration_numbers:
            used_registration_numbers.add(reg)
            break
    vehicles.append({
        "vehicle_id": str(uuid.uuid4()),
        "registration_number": reg,
        "vehicle_type": vtype,
        "capacity_kg": round(random.uniform(500, 2000) if vtype == "van" else random.uniform(5000, 20000), 2),
        "status": random.choices(["active", "in_maintenance", "retired"], weights=[0.85, 0.10, 0.05], k=1)[0],
    })

with open(f"{OUTPUT_DIR}/vehicles.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=vehicles[0].keys())
    writer.writeheader()
    writer.writerows(vehicles)
print(f"  -> {OUTPUT_DIR}/vehicles.csv")


print(f"Generating {N_DRIVERS} drivers...")
driver_employee_pool = random.sample(
    logistics_employee_ids, k=min(N_DRIVERS, len(logistics_employee_ids))
)
if len(driver_employee_pool) < N_DRIVERS:
    print(f"  Note: only {len(driver_employee_pool)} LOGISTICS employees available "
          f"(wanted {N_DRIVERS}) — using all of them, no duplicates.")

drivers = []
used_licence_numbers = set()
for eid in driver_employee_pool:
    while True:
        licence = f"DL-{random.randint(1000000, 9999999)}"
        if licence not in used_licence_numbers:
            used_licence_numbers.add(licence)
            break
    drivers.append({
        "driver_id": str(uuid.uuid4()),
        "employee_id": eid,
        "licence_number": licence,
        "licence_expiry": random_date(2026, 2029).isoformat(),
    })

with open(f"{OUTPUT_DIR}/drivers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=drivers[0].keys())
    writer.writeheader()
    writer.writerows(drivers)
print(f"  -> {OUTPUT_DIR}/drivers.csv ({len(drivers)} drivers)")


print(f"Generating {N_ROUTES} routes...")
ROUTE_NAME_TEMPLATES = ["Regional Freight Route", "Cross-Depot Route", "Farm-to-Warehouse Route", "Last-Mile Route"]

routes = []
for i in range(N_ROUTES):
    origin = random.choice(shippable_location_ids)
    dest = random.choice([l for l in shippable_location_ids if l != origin])
    routes.append({
        "route_id": str(uuid.uuid4()),
        "route_name": f"{random.choice(ROUTE_NAME_TEMPLATES)} {i+1}",
        "origin_location_id": origin,
        "destination_location_id": dest,
        "distance_km": round(random.uniform(15, 800), 2),
    })

with open(f"{OUTPUT_DIR}/routes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=routes[0].keys())
    writer.writeheader()
    writer.writerows(routes)
print(f"  -> {OUTPUT_DIR}/routes.csv")


print(f"Generating {N_SHIPMENTS:,} shipments...")
shipments = []
for _ in range(N_SHIPMENTS):
    origin = random.choice(shippable_location_ids)
    dest = random.choice([l for l in shippable_location_ids if l != origin])
    shipments.append({
        "shipment_id": str(uuid.uuid4()),
        "origin_location_id": origin,
        "destination_location_id": dest,
        "client_type": random.choices(["internal", "third_party"], weights=[0.55, 0.45], k=1)[0],
        "status": random.choices(
            ["scheduled", "in_transit", "delivered", "delayed", "cancelled"],
            weights=[0.05, 0.05, 0.80, 0.07, 0.03], k=1
        )[0],
    })

with open(f"{OUTPUT_DIR}/shipments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=shipments[0].keys())
    writer.writeheader()
    writer.writerows(shipments)
print(f"  -> {OUTPUT_DIR}/shipments.csv")



print("Generating shipment legs...")
active_vehicle_ids = [v["vehicle_id"] for v in vehicles if v["status"] == "active"]
driver_ids = [d["driver_id"] for d in drivers]
route_ids = [r["route_id"] for r in routes]

shipment_legs = []
for shp in shipments:
    n_legs = random.choices([1, 2], weights=[0.85, 0.15], k=1)[0]
    departure = random_datetime_in(2025, 2026)
    for leg_num in range(n_legs):
        leg_departure = departure + timedelta(hours=leg_num * random.randint(4, 12))
        has_arrived = shp["status"] in ("delivered", "in_transit") and random.random() < 0.9
        arrival = ""
        if has_arrived:
            arrival = (leg_departure + timedelta(hours=random.randint(1, 18))).isoformat(sep=" ")
        shipment_legs.append({
            "leg_id": str(uuid.uuid4()),
            "shipment_id": shp["shipment_id"],
            "vehicle_id": random.choice(active_vehicle_ids),
            "driver_id": random.choice(driver_ids),
            "route_id": random.choice(route_ids) if random.random() < 0.7 else "",  # nullable — not every leg follows a defined route
            "departure_time": leg_departure.isoformat(sep=" "),
            "arrival_time": arrival,
        })

with open(f"{OUTPUT_DIR}/shipment_legs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=shipment_legs[0].keys())
    writer.writeheader()
    writer.writerows(shipment_legs)
print(f"  -> {OUTPUT_DIR}/shipment_legs.csv ({len(shipment_legs):,} legs across {len(shipments):,} shipments)")


print(f"Generating {len(warehouse_location_ids)} warehouses...")
warehouses = []
for loc_id in warehouse_location_ids:
    leased_from = random.choice(warehouse_depot_property_ids) if warehouse_depot_property_ids and random.random() < 0.8 else ""
    warehouses.append({
        "warehouse_id": str(uuid.uuid4()),
        "location_id": loc_id,
        "capacity_units": round(random.uniform(5000, 50000), 2),
        "leased_from_property_id": leased_from,
    })

with open(f"{OUTPUT_DIR}/warehouses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=warehouses[0].keys())
    writer.writeheader()
    writer.writerows(warehouses)
print(f"  -> {OUTPUT_DIR}/warehouses.csv "
      f"({sum(1 for w in warehouses if w['leased_from_property_id'])} linked to a Properties lease)")



print("Generating maintenance logs...")
maintenance_logs = []
for v in vehicles:
    if v["status"] == "active":
        n_logs = random.randint(1, 5)
    else:
        n_logs = random.randint(2, 6)  # more history for vehicles now retired/in maintenance
    for _ in range(n_logs):
        maintenance_logs.append({
            "maintenance_id": str(uuid.uuid4()),
            "vehicle_id": v["vehicle_id"],
            "service_date": random_date(2023, 2026).isoformat(),
            "cost": round(random.uniform(15000, 450000), 2),  # NGN
            "description": random.choice([
                "Routine service", "Brake replacement", "Tyre replacement",
                "Engine diagnostics", "Oil change", "Suspension repair",
            ]),
        })

with open(f"{OUTPUT_DIR}/maintenance_logs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=maintenance_logs[0].keys())
    writer.writeheader()
    writer.writerows(maintenance_logs)
print(f"  -> {OUTPUT_DIR}/maintenance_logs.csv ({len(maintenance_logs):,} logs)")

print("\nLogistics module generation complete.")