"""
Project Concord — Veridian Financial Services Synthetic Data Generator

Generates: financial_account_references (Core Hub table — gap in the
original 01_core_hub.py, closed here since it's entirely VFS-driven
in practice), wallet_accounts, wallet_transactions, loans,
loan_repayments, kyc_records, merchant_settlements.

Fixes applied vs. an earlier draft of this script:
1. wallet_accounts.account_ref_id now correctly points to the SAME
   customer's own financial_account_references row — the earlier
   draft picked a random account_ref_id from the whole pool, which
   could silently bridge one customer's wallet to a different
   customer's account reference.
2. merchant_settlements.division_id now resolved via division_code +
   staging-table join at load time (same pattern used throughout this
   project), instead of a hardcoded random.randint(1,5) guess that
   assumed division IDs are sequential 1-5 in a specific order.
3. loans now deliberately honors config.py's cross-divisional overlap
   targets — PCT_FARMERS_WITH_VFS_LOAN and PCT_LOYALTY_CUSTOMERS_WITH_WALLET
   — by drawing borrowers from farmers.csv and wallet holders with
   real overlap against loyalty_accounts.csv, rather than a generic
   unweighted random split. This is what Appendix D actually asks for
   ("a meaningful proportion of farmers should also appear as VFS
   loan customers") — the earlier draft didn't reference either file.
4. wallet_transactions windowed to the same 60-day recent period as
   pos_transactions, for a consistent demo/dashboard date range.

Run from the project root:
    python synthetic_data/generate/06_vfs.py
"""

import csv
import os
import sys
import uuid
from datetime import date, datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from synthetic_data.config import (
    N_WALLET_TRANSACTIONS, PCT_FARMERS_WITH_VFS_LOAN,
    PCT_LOYALTY_CUSTOMERS_WITH_WALLET, OUTPUT_DIR, SEED
)

import random
random.seed(SEED + 6)

PCT_CUSTOMERS_WITH_WALLET = 0.50
N_MERCHANT_SETTLEMENTS = 90
N_CUSTOMER_LOANS_PCT = 0.03


def load_csv(name):
    with open(f"{OUTPUT_DIR}/{name}", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(1, delta)))

def random_datetime_recent(days_back=60):
    end = datetime(2026, 8, 13, 20, 0)
    start = end - timedelta(days=days_back)
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta_seconds))


print("Loading dependencies...")
customers = load_csv("customers.csv")
customer_ids = [c["customer_id"] for c in customers]

loyalty_accounts = load_csv("loyalty_accounts.csv")
loyalty_customer_ids = set(l["customer_id"] for l in loyalty_accounts)

farmers = load_csv("farmers.csv")


target_wallet_count = int(len(customer_ids) * PCT_CUSTOMERS_WITH_WALLET)
n_from_loyalty = int(len(loyalty_customer_ids) * PCT_LOYALTY_CUSTOMERS_WITH_WALLET)

loyalty_pool = list(loyalty_customer_ids)
random.shuffle(loyalty_pool)
wallet_customers_from_loyalty = loyalty_pool[:n_from_loyalty]

remaining_needed = max(0, target_wallet_count - len(wallet_customers_from_loyalty))
non_loyalty_pool = [c for c in customer_ids if c not in loyalty_customer_ids]
wallet_customers_other = random.sample(non_loyalty_pool, k=min(remaining_needed, len(non_loyalty_pool)))

wallet_customer_ids = list(set(wallet_customers_from_loyalty + wallet_customers_other))
print(f"Wallet holders: {len(wallet_customer_ids):,} total "
      f"({len(wallet_customers_from_loyalty):,} drawn from loyalty members, "
      f"honoring the {PCT_LOYALTY_CUSTOMERS_WITH_WALLET:.0%} overlap target)")


print("Generating financial_account_references...")
account_refs = []
customer_to_account_ref = {}

for cid in wallet_customer_ids:
    ref_id = str(uuid.uuid4())
    customer_to_account_ref[cid] = ref_id
    account_refs.append({
        "account_ref_id": ref_id,
        "customer_id": cid,
        "account_type": "wallet",
        "account_status": random.choices(["active", "dormant", "closed"], weights=[0.85, 0.10, 0.05], k=1)[0],
        "opened_date": random_date(2019, 2026).isoformat(),
    })

with open(f"{OUTPUT_DIR}/financial_account_references.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=account_refs[0].keys())
    writer.writeheader()
    writer.writerows(account_refs)
print(f"  -> {OUTPUT_DIR}/financial_account_references.csv ({len(account_refs):,} rows)")



print("Generating wallet_accounts and kyc_records...")
wallet_accounts = []
kyc_records = []
customer_to_wallet_id = {}

for cid in wallet_customer_ids:
    wid = str(uuid.uuid4())
    customer_to_wallet_id[cid] = wid
    wallet_accounts.append({
        "wallet_id": wid,
        "customer_id": cid,
        "account_ref_id": customer_to_account_ref[cid],   # <-- the actual fix
        "balance": round(random.uniform(0, 250000), 2),
        "status": random.choices(["active", "dormant", "closed"], weights=[0.85, 0.10, 0.05], k=1)[0],
    })
    kyc_records.append({
        "kyc_id": str(uuid.uuid4()),
        "customer_id": cid,
        "verification_level": random.choices(["tier1", "tier2", "tier3"], weights=[0.4, 0.4, 0.2], k=1)[0],
        "verified_date": random_date(2023, 2026).isoformat(),
    })

with open(f"{OUTPUT_DIR}/wallet_accounts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=wallet_accounts[0].keys())
    writer.writeheader()
    writer.writerows(wallet_accounts)
print(f"  -> {OUTPUT_DIR}/wallet_accounts.csv ({len(wallet_accounts):,} rows)")

with open(f"{OUTPUT_DIR}/kyc_records.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=kyc_records[0].keys())
    writer.writeheader()
    writer.writerows(kyc_records)
print(f"  -> {OUTPUT_DIR}/kyc_records.csv ({len(kyc_records):,} rows)")

print(f"Generating {N_WALLET_TRANSACTIONS:,} wallet transactions...")
wallet_ids = list(customer_to_wallet_id.values())

with open(f"{OUTPUT_DIR}/wallet_transactions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["wallet_txn_id", "wallet_id", "counterparty_type", "amount", "transaction_date"])
    for i in range(N_WALLET_TRANSACTIONS):
        writer.writerow([
            str(uuid.uuid4()),
            random.choice(wallet_ids),
            random.choices(
                ["merchant", "peer", "loan_disbursement", "loan_repayment", "other"],
                weights=[0.50, 0.25, 0.05, 0.10, 0.10], k=1
            )[0],
            round(random.uniform(50, 15000), 2),
            random_datetime_recent(days_back=60).isoformat(sep=" "),
        ])
        if (i + 1) % 100_000 == 0:
            print(f"  ...{i+1:,} wallet transactions generated so far")
print(f"  -> {OUTPUT_DIR}/wallet_transactions.csv ({N_WALLET_TRANSACTIONS:,} rows)")


print("Generating loans and loan_repayments...")

n_farmer_loans = int(len(farmers) * PCT_FARMERS_WITH_VFS_LOAN)
farmer_borrower_supplier_ids = [
    f["supplier_id"] for f in random.sample(farmers, k=min(n_farmer_loans, len(farmers)))
]

n_customer_loans = int(len(wallet_customer_ids) * N_CUSTOMER_LOANS_PCT)
customer_borrower_ids = random.sample(wallet_customer_ids, k=min(n_customer_loans, len(wallet_customer_ids)))

loans = []
loan_repayments = []

def build_loan(borrower_customer_id, borrower_supplier_id):
    lid = str(uuid.uuid4())
    principal = round(random.uniform(20000, 1500000), 2)
    status = random.choices(["active", "repaid", "defaulted", "written_off"], weights=[0.70, 0.20, 0.05, 0.05], k=1)[0]
    loans.append({
        "loan_id": lid,
        "borrower_customer_id": borrower_customer_id or "",
        "borrower_supplier_id": borrower_supplier_id or "",
        "principal_amount": principal,
        "status": status,
    })
    n_installments = random.randint(1, 12)
    installment_amount = round(principal / 12, 2)
    for _ in range(n_installments):
        paid_flag = random.random() < 0.85
        due = random_date(2025, 2026)
        loan_repayments.append({
            "repayment_id": str(uuid.uuid4()),
            "loan_id": lid,
            "due_date": due.isoformat(),
            "amount_due": installment_amount,
            "amount_paid": installment_amount if paid_flag else 0,
            "paid_date": (due + timedelta(days=random.randint(0, 5))).isoformat() if paid_flag else "",
        })
    return lid

for sid in farmer_borrower_supplier_ids:
    build_loan(borrower_customer_id=None, borrower_supplier_id=sid)

for cid in customer_borrower_ids:
    build_loan(borrower_customer_id=cid, borrower_supplier_id=None)

with open(f"{OUTPUT_DIR}/loans.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=loans[0].keys())
    writer.writeheader()
    writer.writerows(loans)
print(f"  -> {OUTPUT_DIR}/loans.csv ({len(loans):,} loans: "
      f"{len(farmer_borrower_supplier_ids):,} farmer, {len(customer_borrower_ids):,} customer — "
      f"{len(farmer_borrower_supplier_ids)/len(farmers):.0%} of all farmers, honoring the "
      f"{PCT_FARMERS_WITH_VFS_LOAN:.0%} config target)")

with open(f"{OUTPUT_DIR}/loan_repayments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=loan_repayments[0].keys())
    writer.writeheader()
    writer.writerows(loan_repayments)
print(f"  -> {OUTPUT_DIR}/loan_repayments.csv ({len(loan_repayments):,} rows)")



print(f"Generating {N_MERCHANT_SETTLEMENTS} merchant settlements...")
SETTLEMENT_DIVISIONS = ["RETAIL", "LOGISTICS", "AGRI"]  # the divisions VFS actually settles wallet payments to

merchant_settlements = []
for _ in range(N_MERCHANT_SETTLEMENTS):
    merchant_settlements.append({
        "settlement_id": str(uuid.uuid4()),
        "division_code": random.choice(SETTLEMENT_DIVISIONS),
        "settlement_date": random_date(2026, 2026).isoformat(),
        "total_amount": round(random.uniform(100000, 5000000), 2),
    })

with open(f"{OUTPUT_DIR}/merchant_settlements.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=merchant_settlements[0].keys())
    writer.writeheader()
    writer.writerows(merchant_settlements)
print(f"  -> {OUTPUT_DIR}/merchant_settlements.csv ({len(merchant_settlements)} rows) "
      f"— NOTE: division_code column, needs staging+join at load time like employees/suppliers_vendors")

print("\nVFS module generation complete.")