import csv
import os
import sys
import uuid
from datetime import date, datetime, timedelta
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import (
    N_POS_TRANSACTIONS, AVG_LINE_ITEMS_PER_TRANSACTION,
    PCT_LOYALTY_CUSTOMERS_WITH_WALLET, OUTPUT_DIR, SEED
)

import random
random.seed(SEED + 5)

N_SUPPLIER_DELIVERIES = 5_000 


def load_csv(name):
    with open(f"{OUTPUT_DIR}/{name}", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def random_datetime_recent(days_back=60):
    # section 5.4: "approximately one to two months of realistic transaction volume"
    end = datetime(2026, 8, 13, 20, 0)
    start = end - timedelta(days=days_back)
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta_seconds))


locations = load_csv("locations_sites.csv")
store_location_ids = [l["location_id"] for l in locations if l["site_type"] == "store"]
office_location_ids = [l["location_id"] for l in locations if l["site_type"] == "office"]

employees = load_csv("employees.csv")
retail_employee_ids = [e["employee_id"] for e in employees if e["division_code"] == "RETAIL"]

products = load_csv("product_service_catalogue.csv")
retail_products = [p for p in products if p["primary_division_code"] == "RETAIL"]
retail_product_ids = [p["product_id"] for p in retail_products]

customers = load_csv("customers.csv")
customer_ids = [c["customer_id"] for c in customers]

suppliers = load_csv("suppliers_vendors.csv")
retail_supplier_ids = [s["supplier_id"] for s in suppliers if s["primary_division_code"] == "RETAIL"]
if not retail_supplier_ids:
    raise RuntimeError("No RETAIL-division suppliers found in suppliers_vendors.csv.")


print("Generating stores...")
stores = []
for loc_id in store_location_ids:
    stores.append({
        "store_id": str(uuid.uuid4()),
        "location_id": loc_id,
        "store_format": random.choices(["large_format", "neighbourhood"], weights=[0.4, 0.6], k=1)[0],
        "opening_date": random_date(2011, 2025).isoformat(),
        "manager_employee_id": random.choice(retail_employee_ids) if retail_employee_ids else "",
    })
# MeridianGo — the online channel (section 1.3.1: ~12% of divisional revenue)
stores.append({
    "store_id": str(uuid.uuid4()),
    "location_id": random.choice(office_location_ids),
    "store_format": "online",
    "opening_date": date(2021, 3, 1).isoformat(),  # section 1.3.1: "launched in 2021"
    "manager_employee_id": random.choice(retail_employee_ids) if retail_employee_ids else "",
})

with open(f"{OUTPUT_DIR}/stores.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=stores[0].keys())
    writer.writeheader()
    writer.writerows(stores)
print(f"  -> {OUTPUT_DIR}/stores.csv ({len(stores)} stores: {len(store_location_ids)} physical + 1 online)")

store_ids = [s["store_id"] for s in stores]
physical_store_ids = [s["store_id"] for s in stores if s["store_format"] != "online"]
online_store_id = [s["store_id"] for s in stores if s["store_format"] == "online"][0]


print("Generating loyalty accounts...")
loyalty_customer_ids = random.sample(customer_ids, k=int(len(customer_ids) * 0.55))
loyalty_accounts = []
for cid in loyalty_customer_ids:
    loyalty_accounts.append({
        "loyalty_id": str(uuid.uuid4()),
        "customer_id": cid,
        "tier": random.choices(["bronze", "silver", "gold", "platinum"], weights=[0.5, 0.3, 0.15, 0.05], k=1)[0],
        "points_balance": random.randint(0, 15000),
        "enrolment_date": random_date(2018, 2026).isoformat(),
    })

with open(f"{OUTPUT_DIR}/loyalty_accounts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=loyalty_accounts[0].keys())
    writer.writeheader()
    writer.writerows(loyalty_accounts)
print(f"  -> {OUTPUT_DIR}/loyalty_accounts.csv ({len(loyalty_accounts):,} accounts, "
      f"{len(loyalty_customer_ids)/len(customer_ids):.0%} of customer base)")


print("Generating promotions...")
promotions = []
for _ in range(30):
    start = random_date(2025, 2026)
    end = start + timedelta(days=random.randint(3, 30))
    promotions.append({
        "promotion_id": str(uuid.uuid4()),
        "product_id": random.choice(retail_product_ids),
        "discount_type": random.choices(["percentage", "fixed_amount", "bogo"], weights=[0.5, 0.3, 0.2], k=1)[0],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    })

with open(f"{OUTPUT_DIR}/promotions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=promotions[0].keys())
    writer.writeheader()
    writer.writerows(promotions)
print(f"  -> {OUTPUT_DIR}/promotions.csv ({len(promotions)} promotions)")

print(f"Generating {N_SUPPLIER_DELIVERIES:,} supplier deliveries...")
supplier_deliveries = []
delivery_line_items = []
# Track delivered quantity per (store, product) for stock derivation later
delivered_qty = defaultdict(float)

for _ in range(N_SUPPLIER_DELIVERIES):
    did = str(uuid.uuid4())
    store_id = random.choice(physical_store_ids)  # online store doesn't receive physical deliveries
    expected = random_date(2026, 2026)
    status = random.choices(["pending", "received", "delayed", "cancelled"], weights=[0.10, 0.75, 0.10, 0.05], k=1)[0]
    received = ""
    if status == "received":
        received = (expected + timedelta(days=random.randint(0, 3))).isoformat()

    supplier_deliveries.append({
        "delivery_id": did,
        "supplier_id": random.choice(retail_supplier_ids),
        "store_id": store_id,
        "expected_date": expected.isoformat(),
        "received_date": received,
        "status": status,
    })

    if status == "received":
        n_items = random.randint(1, 4)
        chosen_products = random.sample(retail_product_ids, k=min(n_items, len(retail_product_ids)))
        for pid in chosen_products:
            qty = round(random.uniform(20, 300), 2)
            delivery_line_items.append({
                "delivery_line_id": str(uuid.uuid4()),
                "delivery_id": did,
                "product_id": pid,
                "quantity": qty,
            })
            delivered_qty[(store_id, pid)] += qty

with open(f"{OUTPUT_DIR}/supplier_deliveries.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=supplier_deliveries[0].keys())
    writer.writeheader()
    writer.writerows(supplier_deliveries)
print(f"  -> {OUTPUT_DIR}/supplier_deliveries.csv ({len(supplier_deliveries):,} deliveries)")

with open(f"{OUTPUT_DIR}/delivery_line_items.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["delivery_line_id", "delivery_id", "product_id", "quantity"])
    writer.writeheader()
    writer.writerows(delivery_line_items)
print(f"  -> {OUTPUT_DIR}/delivery_line_items.csv ({len(delivery_line_items):,} line items)")


print(f"Generating {N_POS_TRANSACTIONS:,} POS transactions + line items (streamed)...")

sold_qty = defaultdict(float)  # (store_id, product_id) -> total sold, for stock derivation

txn_path = f"{OUTPUT_DIR}/pos_transactions.csv"
line_path = f"{OUTPUT_DIR}/transaction_line_items.csv"

PAYMENT_METHODS = ["cash", "card", "wallet", "other"]
PAYMENT_WEIGHTS = [0.35, 0.30, 0.30, 0.05]

with open(txn_path, "w", newline="", encoding="utf-8") as tf, \
     open(line_path, "w", newline="", encoding="utf-8") as lf:

    txn_writer = csv.writer(tf)
    txn_writer.writerow(["transaction_id", "store_id", "customer_id", "transaction_date", "total_amount", "payment_method"])

    line_writer = csv.writer(lf)
    line_writer.writerow(["line_item_id", "transaction_id", "product_id", "quantity", "unit_price"])

    n_line_items_total = 0
    for i in range(N_POS_TRANSACTIONS):
        tid = str(uuid.uuid4())
        store_id = random.choice(store_ids)
        # ~30% of transactions have no linked customer (walk-in cash sales)
        cust_id = random.choice(customer_ids) if random.random() > 0.30 else ""
        txn_dt = random_datetime_recent(days_back=60)
        payment_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS, k=1)[0]

        n_items = max(1, round(random.gauss(AVG_LINE_ITEMS_PER_TRANSACTION, 1.2)))
        chosen_products = random.choices(retail_product_ids, k=n_items)

        total_amount = 0.0
        for pid in chosen_products:
            qty = round(random.uniform(1, 6), 2)
            unit_price = round(random.uniform(300, 8000), 2)  # NGN, plausible grocery item range
            line_total = round(qty * unit_price, 2)
            total_amount += line_total

            line_writer.writerow([str(uuid.uuid4()), tid, pid, qty, unit_price])
            sold_qty[(store_id, pid)] += qty
            n_line_items_total += 1

        txn_writer.writerow([tid, store_id, cust_id, txn_dt.isoformat(sep=" "), round(total_amount, 2), payment_method])

        if (i + 1) % 100_000 == 0:
            print(f"  ...{i+1:,} transactions generated so far")

print(f"  -> {txn_path} ({N_POS_TRANSACTIONS:,} transactions)")
print(f"  -> {line_path} ({n_line_items_total:,} line items, avg {n_line_items_total/N_POS_TRANSACTIONS:.2f}/transaction)")


# ─────────────────────────────────────────────
# INVENTORY STOCK LEVELS (one row per store-product pair that has
# EITHER a delivery or a sale — derived as delivered minus sold, with
# a deliberate injected discrepancy per section 1.3.1's documented
# 3-8% real-world stock count gap. last_counted_date set to a date
# BEFORE the most recent activity, reflecting that counts happen
# roughly weekly, not continuously.)
# ─────────────────────────────────────────────
print("Deriving inventory stock levels...")
all_store_product_pairs = set(delivered_qty.keys()) | set(sold_qty.keys())

inventory_stock_levels = []
for (store_id, pid) in all_store_product_pairs:
    delivered = delivered_qty.get((store_id, pid), 0.0)
    sold = sold_qty.get((store_id, pid), 0.0)
    true_stock = max(0.0, delivered - sold)

    # inject the documented 3-8% discrepancy against what the system "shows"
    discrepancy_pct = random.uniform(0.03, 0.08) * random.choice([-1, 1])
    system_recorded_stock = max(0.0, round(true_stock * (1 + discrepancy_pct), 2))

    inventory_stock_levels.append({
        "stock_id": str(uuid.uuid4()),
        "store_id": store_id,
        "product_id": pid,
        "quantity_on_hand": system_recorded_stock,
        "last_counted_date": random_date(2026, 2026).isoformat(),  # last WEEKLY count, not live-updated
    })

with open(f"{OUTPUT_DIR}/inventory_stock_levels.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=inventory_stock_levels[0].keys())
    writer.writeheader()
    writer.writerows(inventory_stock_levels)
print(f"  -> {OUTPUT_DIR}/inventory_stock_levels.csv ({len(inventory_stock_levels):,} store-product rows)")

print("\nRetail module generation complete.")