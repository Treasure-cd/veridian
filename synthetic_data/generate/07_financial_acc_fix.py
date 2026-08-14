import csv

OUTPUT_DIR = "/home/treasure/Desktop/veridian/synthetic_data/output"

with open(f"{OUTPUT_DIR}/financial_account_references.csv", "r", encoding="utf-8") as f:
    refs = list(csv.DictReader(f))

# Deduplicate by account_ref_id
unique_refs = {r["account_ref_id"]: r for r in refs}

with open(f"{OUTPUT_DIR}/financial_account_references.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=refs[0].keys())
    writer.writeheader()
    writer.writerows(unique_refs.values())
