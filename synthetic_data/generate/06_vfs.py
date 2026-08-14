import csv
import os
import sys
import uuid
from datetime import date, datetime, timedelta
import random


try:
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from synthetic_data.config import OUTPUT_DIR, SEED
except ImportError:
    OUTPUT_DIR = "."
    SEED = 42

random.seed(SEED + 5)


N_WALLETS = 40000
N_WALLET_TXNS = 300000
N_LOANS = 5000
N_MERCHANT_SETTLEMENTS = 90

# 3. Helper Functions
def load_csv(name):
    filepath = f"{OUTPUT_DIR}/{name}"
    if not os.path.exists(filepath):
        print(f"  [!] {name} not found in {OUTPUT_DIR}. Generating dummy fallback IDs to prevent crashes.")
        return [
            {"customer_id": str(uuid.uuid4()), "supplier_id": str(uuid.uuid4()), "account_ref_id": str(uuid.uuid4())} 
            for _ in range(5000)
        ]
    with open(filepath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def random_date(start_year, end_year):
    start = date(start_year, 1, 1)
    end = date(end_year, 8, 13)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(1, delta)))

def random_datetime_in(start_year, end_year):
    d = random_date(start_year, end_year)
    return datetime(d.year, d.month, d.day, random.randint(5, 20), random.choice([0, 15, 30, 45]))

def write_csv(filename, data):
    with open(f"{OUTPUT_DIR}/{filename}", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  -> {OUTPUT_DIR}/{filename} ({len(data):,} rows)")

print("Loading core dependencies...")
customers = load_csv("customers.csv")
customer_ids = [c.get("customer_id") for c in customers if c.get("customer_id")]

suppliers = load_csv("suppliers_vendors.csv")
supplier_ids = [s.get("supplier_id") for s in suppliers if s.get("supplier_id")]

account_refs = load_csv("financial_account_references.csv")
account_ref_ids = [r.get("account_ref_id") for r in account_refs if r.get("account_ref_id")]

print(f"Generating {N_WALLETS} wallets and KYC records...")
wallet_customers = random.sample(customer_ids, min(N_WALLETS, len(customer_ids)))

wallet_accounts = []
kyc_records = []
wallet_ids = []

for cid in wallet_customers:
    wid = str(uuid.uuid4())
    wallet_ids.append(wid)
    
    wallet_accounts.append({
        "wallet_id": wid,
        "customer_id": cid,
        "account_ref_id": random.choice(account_ref_ids) if account_ref_ids else str(uuid.uuid4()),
        "balance": round(random.uniform(0, 250000), 2),
        "status": random.choices(["active", "dormant", "closed"], weights=[0.85, 0.10, 0.05])[0]
    })
    
    kyc_records.append({
        "kyc_id": str(uuid.uuid4()),
        "customer_id": cid,
        "verification_level": random.choices(["tier1", "tier2", "tier3"], weights=[0.4, 0.4, 0.2])[0],
        "verified_date": random_date(2023, 2026).isoformat()
    })

write_csv("wallet_accounts.csv", wallet_accounts)
write_csv("kyc_records.csv", kyc_records)


print(f"Generating {N_WALLET_TXNS:,} wallet transactions...")
wallet_txns = []
for _ in range(N_WALLET_TXNS):
    wallet_txns.append({
        "wallet_txn_id": str(uuid.uuid4()),
        "wallet_id": random.choice(wallet_ids),
        "counterparty_type": random.choices(
            ['merchant', 'peer', 'loan_disbursement', 'loan_repayment', 'other'], 
            weights=[0.50, 0.25, 0.05, 0.10, 0.10]
        )[0],
        "amount": round(random.uniform(50, 15000), 2),
        "transaction_date": random_datetime_in(2026, 2026).isoformat(sep=" ")
    })

write_csv("wallet_transactions.csv", wallet_txns)

print(f"Generating {N_LOANS:,} loans and associated repayments...")
loans = []
loan_repayments = []

for _ in range(N_LOANS):
    lid = str(uuid.uuid4())
    
    # Simulate borrower being either a customer OR a supplier (farmer)
    is_customer = random.random() < 0.6
    b_cust = random.choice(customer_ids) if is_customer else ""
    b_supp = random.choice(supplier_ids) if not is_customer else ""
    
    principal = round(random.uniform(20000, 1500000), 2)
    status = random.choices(['active', 'repaid', 'defaulted', 'written_off'], weights=[0.70, 0.20, 0.05, 0.05])[0]
    
    loans.append({
        "loan_id": lid,
        "borrower_customer_id": b_cust,
        "borrower_supplier_id": b_supp,
        "principal_amount": principal,
        "status": status
    })
    
    for _ in range(random.randint(1, 5)):
        amount_due = round(principal / 12, 2)
        paid = amount_due if random.random() < 0.85 else 0
        
        loan_repayments.append({
            "repayment_id": str(uuid.uuid4()),
            "loan_id": lid,
            "due_date": random_date(2025, 2026).isoformat(),
            "amount_due": amount_due,
            "amount_paid": paid,
            "paid_date": random_date(2025, 2026).isoformat() if paid > 0 else ""
        })

write_csv("loans.csv", loans)
write_csv("loan_repayments.csv", loan_repayments)

print(f"Generating {N_MERCHANT_SETTLEMENTS} merchant settlements...")
merchant_settlements = []
for _ in range(N_MERCHANT_SETTLEMENTS):
    merchant_settlements.append({
        "settlement_id": str(uuid.uuid4()),
        "division_id": random.randint(1, 5),
        "settlement_date": random_date(2026, 2026).isoformat(),
        "total_amount": round(random.uniform(100000, 5000000), 2)
    })

write_csv("merchant_settlements.csv", merchant_settlements)
