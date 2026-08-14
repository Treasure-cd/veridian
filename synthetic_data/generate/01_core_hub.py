import csv
import os
import sys
import uuid
from datetime import date, timedelta

from faker import Faker

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import (
    N_CUSTOMERS, N_EMPLOYEES, N_SUPPLIERS, FARMER_SHARE_OF_SUPPLIERS,
    COUNTRIES, COUNTRY_WEIGHTS, OUTPUT_DIR, SEED
)

import random
random.seed(SEED)
Faker.seed(SEED)

fake_ng = Faker("en_NG")
fake_gh = Faker("tw_GH")
fake_ke = Faker("en_KE")
fake = Faker()  # fallback, used only for non-person text (addresses, companies)

FAKER_BY_COUNTRY = {"NG": fake_ng, "GH": fake_gh, "KE": fake_ke}

def name_for_country(country_code):
    return FAKER_BY_COUNTRY[country_code].name()

os.makedirs(OUTPUT_DIR, exist_ok=True)


DIVISION_CODES = ["RETAIL", "LOGISTICS", "VFS", "AGRI", "PROPERTIES", "GROUP"]

DIVISION_WEIGHTS = {
    "RETAIL": 6200, "LOGISTICS": 2850, "VFS": 1340,
    "AGRI": 3400, "PROPERTIES": 88, "GROUP": 722
}
_total_hc = sum(DIVISION_WEIGHTS.values())
DIVISION_PROBS = [DIVISION_WEIGHTS[c] / _total_hc for c in DIVISION_CODES]


def random_date(start_year=2015, end_year=2026):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def gen_phone(country_code):
    prefixes = {"NG": "+234", "GH": "+233", "KE": "+254"}
    return f"{prefixes[country_code]}{random.randint(700000000, 999999999)}"


print(f"Generating {N_CUSTOMERS:,} customers...")
customers = []
for _ in range(N_CUSTOMERS):
    cid = str(uuid.uuid4())
    country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
    dob = fake.date_of_birth(minimum_age=18, maximum_age=75)
    consent_retail = random.random() < 0.65 
    consent_financial = random.random() < 0.35 
    consent_marketing = random.random() < 0.50
    customers.append({
        "customer_id": cid,
        "full_name": name_for_country(country),
        "date_of_birth": dob.isoformat(),
        "primary_contact": gen_phone(country),
        "registered_country": country,
        "consent_retail_personalisation": consent_retail,
        "consent_financial_visibility": consent_financial,
        "consent_marketing": consent_marketing,
        "created_date": random_date(2018, 2026).isoformat(),
    })

with open(f"{OUTPUT_DIR}/customers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=customers[0].keys())
    writer.writeheader()
    writer.writerows(customers)
print(f"  -> {OUTPUT_DIR}/customers.csv")


print(f"Generating {N_EMPLOYEES:,} employees...")

ROLE_TITLES = {
    "RETAIL": ["Store Manager", "Cashier", "Stock Clerk", "Regional Retail Lead"],
    "LOGISTICS": ["Dispatcher", "Fleet Coordinator", "Warehouse Supervisor", "Field Agent"],
    "VFS": ["Loan Officer", "KYC Analyst", "Branch Teller", "Credit Risk Analyst"],
    "AGRI": ["Field Agent", "Quality Inspector", "Facility Manager", "Agronomist"],
    "PROPERTIES": ["Property Manager", "Maintenance Coordinator", "Leasing Officer"],
    "GROUP": ["Finance Analyst", "HR Business Partner", "Executive Assistant"],
}

employees = []
senior_pool_by_division = {c: [] for c in DIVISION_CODES}

n_senior = max(1, N_EMPLOYEES // 20)  # ~5% senior/manager tier
for _ in range(n_senior):
    eid = str(uuid.uuid4())
    div = random.choices(DIVISION_CODES, weights=DIVISION_PROBS, k=1)[0]
    _country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
    employees.append({
        "employee_id": eid,
        "full_name": name_for_country(_country),
        "division_code": div,   # resolved to division_id at load time
        "role_title": random.choice(ROLE_TITLES[div]).replace("Manager", "Senior Manager"),
        "employment_status": "active",
        "hire_date": random_date(2010, 2023).isoformat(),
        "reports_to": "",  # top of the chain
    })
    senior_pool_by_division[div].append(eid)

for div in DIVISION_CODES:
    if not senior_pool_by_division[div]:
        # guarantee at least one manager per division to report to
        eid = str(uuid.uuid4())
        _country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
        employees.append({
            "employee_id": eid, "full_name": name_for_country(_country), "division_code": div,
            "role_title": random.choice(ROLE_TITLES[div]),
            "employment_status": "active",
            "hire_date": random_date(2010, 2020).isoformat(), "reports_to": "",
        })
        senior_pool_by_division[div].append(eid)

for _ in range(N_EMPLOYEES - len(employees)):
    eid = str(uuid.uuid4())
    div = random.choices(DIVISION_CODES, weights=DIVISION_PROBS, k=1)[0]
    manager_id = random.choice(senior_pool_by_division[div])
    status = random.choices(
        ["active", "on_leave", "terminated"], weights=[0.90, 0.05, 0.05], k=1
    )[0]
    _country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS, k=1)[0]
    employees.append({
        "employee_id": eid,
        "full_name": name_for_country(_country),
        "division_code": div,
        "role_title": random.choice(ROLE_TITLES[div]),
        "employment_status": status,
        "hire_date": random_date(2015, 2026).isoformat(),
        "reports_to": manager_id,
    })

with open(f"{OUTPUT_DIR}/employees.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=employees[0].keys())
    writer.writeheader()
    writer.writerows(employees)
print(f"  -> {OUTPUT_DIR}/employees.csv")


print(f"Generating {N_SUPPLIERS:,} suppliers/vendors...")
suppliers = []
n_farmers = int(N_SUPPLIERS * FARMER_SHARE_OF_SUPPLIERS)

for i in range(N_SUPPLIERS):
    sid = str(uuid.uuid4())
    if i < n_farmers:
        stype = "farmer"
        div = "AGRI"
        name = name_for_country("NG")
    else:
        stype = random.choices(
            ["wholesale_supplier", "service_vendor", "other"],
            weights=[0.5, 0.4, 0.1], k=1
        )[0]
        div = random.choices(["RETAIL", "AGRI", "LOGISTICS"], weights=[0.5, 0.3, 0.2], k=1)[0]
        name = fake.company()  # companies stay locale-generic; not a person's name
    suppliers.append({
        "supplier_id": sid,
        "legal_name": name,
        "supplier_type": stype,
        "primary_division_code": div,
        "onboarding_date": random_date(2010, 2026).isoformat(),
        "status": random.choices(["active", "inactive", "suspended"], weights=[0.9, 0.07, 0.03], k=1)[0],
    })

with open(f"{OUTPUT_DIR}/suppliers_vendors.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=suppliers[0].keys())
    writer.writeheader()
    writer.writerows(suppliers)
print(f"  -> {OUTPUT_DIR}/suppliers_vendors.csv ({n_farmers:,} flagged as farmers)")


print("Generating locations/sites...")
locations = []

def add_location(site_type, city, country):
    lid = str(uuid.uuid4())
    lat = round(random.uniform(4.0, 13.5), 6)
    lon = round(random.uniform(-3.5, 41.5), 6)
    locations.append({
        "location_id": lid,
        "site_name": f"{city} {site_type.replace('_', ' ').title()}",
        "site_type": site_type,
        "address": fake.street_address(),
        "city": city,
        "country_code": country,
        "latitude": lat,
        "longitude": lon,
    })
    return lid

NG_CITIES = ["Lagos", "Enugu", "Kano", "Ibadan", "Kaduna", "Port Harcourt", "Abuja"]
GH_CITIES = ["Accra", "Kumasi"]
KE_CITIES = ["Nairobi", "Mombasa"]
CITY_TO_COUNTRY = {c: "NG" for c in NG_CITIES}
CITY_TO_COUNTRY.update({c: "GH" for c in GH_CITIES})
CITY_TO_COUNTRY.update({c: "KE" for c in KE_CITIES})

def add_location_from_city(site_type, city):
    return add_location(site_type, city, CITY_TO_COUNTRY[city])

store_location_ids = [add_location_from_city("store", random.choice(NG_CITIES + GH_CITIES)) for _ in range(68)]
warehouse_location_ids = [add_location_from_city("warehouse", random.choice(NG_CITIES)) for _ in range(6)]
facility_location_ids = [add_location_from_city("processing_facility", random.choice(NG_CITIES)) for _ in range(4)]
property_location_ids = [add_location_from_city("property", random.choice(NG_CITIES + GH_CITIES + KE_CITIES)) for _ in range(94)]
office_location_ids = [add_location_from_city("office", "Lagos") for _ in range(5)]

farm_location_ids = [add_location_from_city("farm", random.choice(NG_CITIES)) for _ in range(500)]

with open(f"{OUTPUT_DIR}/locations_sites.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=locations[0].keys())
    writer.writeheader()
    writer.writerows(locations)
print(f"  -> {OUTPUT_DIR}/locations_sites.csv ({len(locations)} total)")


with open(f"{OUTPUT_DIR}/_location_pools.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["pool", "location_id"])
    for lid in store_location_ids: writer.writerow(["store", lid])
    for lid in warehouse_location_ids: writer.writerow(["warehouse", lid])
    for lid in facility_location_ids: writer.writerow(["processing_facility", lid])
    for lid in property_location_ids: writer.writerow(["property", lid])
    for lid in office_location_ids: writer.writerow(["office", lid])
    for lid in farm_location_ids: writer.writerow(["farm", lid])



print("Generating product/service catalogue...")
RETAIL_PRODUCTS = [
    ("Rice (bag)", "grocery", "kg"), ("Cooking Oil", "grocery", "l"),
    ("Tomatoes", "grocery", "kg"), ("Plantain", "grocery", "kg"),
    ("Bottled Water", "beverages", "unit"), ("Soap", "household", "unit"),
    ("Detergent", "household", "unit"), ("Maize Flour", "grocery", "kg"),
    ("Beans", "grocery", "kg"), ("Sugar", "grocery", "kg"),
]
AGRI_PRODUCTS = [
    ("Maize", "grain", "kg"), ("Sorghum", "grain", "kg"),
    ("Cowpea", "legume", "kg"), ("Cassava", "tuber", "kg"),
    ("Yam", "tuber", "kg"),
]

products = []
for name, cat, uom in RETAIL_PRODUCTS:
    products.append({
        "product_id": str(uuid.uuid4()), "product_name": name, "category": cat,
        "unit_of_measure": uom, "primary_division_code": "RETAIL", "is_active": True,
    })
for name, cat, uom in AGRI_PRODUCTS:
    products.append({
        "product_id": str(uuid.uuid4()), "product_name": name, "category": cat,
        "unit_of_measure": uom, "primary_division_code": "AGRI", "is_active": True,
    })

with open(f"{OUTPUT_DIR}/product_service_catalogue.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=products[0].keys())
    writer.writeheader()
    writer.writerows(products)
print(f"  -> {OUTPUT_DIR}/product_service_catalogue.csv ({len(products)} products)")

print("\nCore Hub generation complete.")