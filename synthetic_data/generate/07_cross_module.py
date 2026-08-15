"""
Project Concord — Cross-Module Linking Pass

Generates the two tables that were deliberately deferred during
AgriCore generation because they depend on tables from other modules
that didn't exist yet:

- wholesale_shipments: AgriCore processing runs shipped OUT to either
  a Meridian Retail store or an external client. Requires stores.csv
  (Retail) and, optionally, shipments.csv (Logistics) for the
  physical handoff.
- farmer_loans_reference: AgriCore's read-only visibility bridge into
  a farmer's VFS loan status. Requires loans.csv (VFS) — specifically
  the farmer-borrower loans generated in 06_vfs.py, which already
  drew directly from farmers.csv, so this table is a near-mechanical
  join back onto that same overlap rather than fresh random sampling.

Run from the project root, AFTER 01 through 06 have all been run:
    python synthetic_data/generate/07_cross_module.py
"""

import csv
import os
import sys
import uuid
from datetime import date, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import OUTPUT_DIR, SEED

import random
random.seed(SEED + 7)


def load_csv(name):
    with open(f"{OUTPUT_DIR}/{name}", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(1, delta)))


# ─────────────────────────────────────────────
# WHOLESALE SHIPMENTS
# One row per (a sample of) processing_runs, sent either to a
# Meridian Retail store or an "external client" (no dedicated entity
# for these per the schema's polymorphic design — see data
# dictionary note on wholesale_shipments). Not every run is fully
# shipped out yet; some remain unshipped (no row) — realistic, since
# not all processed goods have a buyer lined up immediately.
# ─────────────────────────────────────────────
print("Loading dependencies...")
processing_runs = load_csv("processing_runs.csv")
stores = load_csv("stores.csv")
physical_store_ids = [s["store_id"] for s in stores if s["store_format"] != "online"]
shipments = load_csv("shipments.csv")
# Only shipments plausibly carrying AgriCore->Retail freight (internal,
# not third_party) are eligible to be linked as the physical carrier
internal_shipment_ids = [s["shipment_id"] for s in shipments if s["client_type"] == "internal"]

EXTERNAL_CLIENT_NAMES = [
    "Sahel Grain Traders Ltd", "Lagos Wholesale Foods Co", "Kaduna Agro Exports",
    "Northern Produce Exchange", "West Africa Grain Consortium",
]

print(f"Generating wholesale_shipments from {len(processing_runs):,} processing runs...")
wholesale_shipments = []

# ~70% of processing runs get shipped out; the rest represent
# recently-processed goods still awaiting a buyer/shipment assignment
shippable_runs = random.sample(processing_runs, k=int(len(processing_runs) * 0.70))

for run in shippable_runs:
    dest_type = random.choices(["meridian_retail", "external_client"], weights=[0.65, 0.35], k=1)[0]
    # Not every wholesale shipment has a logistics shipment arranged yet
    # (shipment_id is nullable per the schema — see data dictionary)
    has_logistics_shipment = random.random() < 0.75

    wholesale_shipments.append({
        "wholesale_id": str(uuid.uuid4()),
        "run_id": run["run_id"],
        "destination_type": dest_type,
        "destination_store_id": random.choice(physical_store_ids) if dest_type == "meridian_retail" else "",
        "destination_external_name": random.choice(EXTERNAL_CLIENT_NAMES) if dest_type == "external_client" else "",
        "shipment_id": random.choice(internal_shipment_ids) if (has_logistics_shipment and internal_shipment_ids) else "",
    })

with open(f"{OUTPUT_DIR}/wholesale_shipments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=wholesale_shipments[0].keys())
    writer.writeheader()
    writer.writerows(wholesale_shipments)

n_retail = sum(1 for w in wholesale_shipments if w["destination_type"] == "meridian_retail")
n_external = len(wholesale_shipments) - n_retail
n_linked_shipment = sum(1 for w in wholesale_shipments if w["shipment_id"])
print(f"  -> {OUTPUT_DIR}/wholesale_shipments.csv ({len(wholesale_shipments):,} rows: "
      f"{n_retail:,} to Meridian Retail, {n_external:,} to external clients, "
      f"{n_linked_shipment:,} linked to a Logistics shipment)")


# ─────────────────────────────────────────────
# FARMER LOANS REFERENCE
# Built directly from the SAME farmer-borrower loans generated in
# 06_vfs.py (which already honored PCT_FARMERS_WITH_VFS_LOAN) — this
# is a mechanical join, not a fresh random sample, since the whole
# point of this table is to summarize a loan that genuinely exists.
# ─────────────────────────────────────────────
print("Loading loans and farmers for farmer_loans_reference...")
loans = load_csv("loans.csv")
farmers = load_csv("farmers.csv")

supplier_to_farmer_id = {f["supplier_id"]: f["farmer_id"] for f in farmers}

farmer_loans = [l for l in loans if l["borrower_supplier_id"]]
print(f"Found {len(farmer_loans):,} farmer-borrower loans to build references for...")

STATUS_MAP = {
    # loans.status -> a plausible visible_summary_status. Not a strict
    # 1:1 mapping (an 'active' loan could still show 'overdue' if a
    # repayment was missed), so this adds a little independent noise
    # rather than mechanically mirroring the loan's own status field.
    "active": ["current", "current", "overdue"],
    "repaid": ["closed"],
    "defaulted": ["overdue", "closed"],
    "written_off": ["closed"],
}

farmer_loans_reference = []
skipped_no_farmer = 0
for loan in farmer_loans:
    supplier_id = loan["borrower_supplier_id"]
    farmer_id = supplier_to_farmer_id.get(supplier_id)
    if not farmer_id:
        skipped_no_farmer += 1
        continue  # shouldn't happen since 06_vfs.py drew directly from farmers.csv, but guard anyway

    farmer_loans_reference.append({
        "reference_id": str(uuid.uuid4()),
        "farmer_id": farmer_id,
        "loan_id": loan["loan_id"],
        "visible_summary_status": random.choice(STATUS_MAP[loan["status"]]),
    })

with open(f"{OUTPUT_DIR}/farmer_loans_reference.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=farmer_loans_reference[0].keys())
    writer.writeheader()
    writer.writerows(farmer_loans_reference)
print(f"  -> {OUTPUT_DIR}/farmer_loans_reference.csv ({len(farmer_loans_reference):,} rows)"
      + (f" [{skipped_no_farmer} loans skipped — no matching farmer found]" if skipped_no_farmer else ""))

print("\nCross-module linking pass complete. Every table in the schema now has generated data.")