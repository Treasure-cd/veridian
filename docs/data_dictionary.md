# Project Concord — Data Dictionary
## Part 1: Core Services Hub

The Core Services Hub contains entities shared across two or more
divisional modules. Per section 4.1 of the brief, each entity here
passed the test of appearing in at least two stakeholder scenarios
(section 2.4) or being referenced by at least two divisions.

---

### divisions
*Not part of the original brief's entity spec — added as a lookup
table to avoid repeating division names as free text across
`employees`, `suppliers_vendors`, `product_service_catalogue`, and
`tenants`. A deliberate, documented scope addition.*

| Column          | Type         | Constraints                    | Notes |
|-----------------|--------------|---------------------------------|-------|
| division_id     | SMALLSERIAL  | PRIMARY KEY                     | |
| division_name   | VARCHAR(50)  | NOT NULL, UNIQUE                | e.g. "Meridian Retail and Consumer" |
| division_code   | VARCHAR(10)  | NOT NULL, UNIQUE                | e.g. 'RETAIL', 'LOGISTICS', 'VFS', 'AGRI', 'PROPERTIES', 'GROUP' |

Seeded with the group's six divisions (five operating + group functions), section 1.2.

---

### customers
Single shared identity for any individual who transacts with one or
more Veridian divisions. Referenced by: Retail, Financial Services.

| Column                            | Type          | Constraints         | Notes |
|------------------------------------|---------------|----------------------|-------|
| customer_id                        | UUID          | PRIMARY KEY, default gen_random_uuid() | |
| full_name                          | VARCHAR(150)  | NOT NULL             | |
| date_of_birth                      | DATE          | nullable             | |
| primary_contact                    | VARCHAR(50)   | NOT NULL             | phone or email |
| registered_country                 | CHAR(2)       | NOT NULL             | ISO code: NG, GH, KE per section Executive Summary |
| consent_retail_personalisation     | BOOLEAN       | NOT NULL, default FALSE | governs retail's use of purchase history for personalisation (section 4.4) |
| consent_financial_visibility        | BOOLEAN       | NOT NULL, default FALSE | governs whether VFS/exec can see this customer's cross-divisional data (section 4.4) |
| created_date                        | DATE          | NOT NULL, default CURRENT_DATE | |


---

### employees
Single shared identity for group staff across all divisions.
Referenced by: Retail, Logistics, AgriCore, Properties.

| Column              | Type          | Constraints                              | Notes |
|----------------------|---------------|--------------------------------------------|-------|
| employee_id           | UUID          | PRIMARY KEY, default gen_random_uuid()    | |
| full_name             | VARCHAR(150)  | NOT NULL                                  | |
| division_id           | SMALLINT      | NOT NULL, REFERENCES divisions            | |
| role_title            | VARCHAR(100)  | NOT NULL                                  | |
| employment_status      | VARCHAR(20)   | NOT NULL, default 'active', CHECK IN ('active','on_leave','terminated') | |
| hire_date              | DATE          | NOT NULL                                  | |
| reports_to             | UUID          | REFERENCES employees(employee_id), nullable | self-referencing FK; NULL for top-level roles |

**Design note:** field agents, inspectors, and store managers do NOT get their own tables — they are ordinary `employees` rows, referenced by FK from wherever a divisional entity needs them (e.g. `harvest_batches.field_agent_employee_id`, `stores.manager_employee_id`). Only roles with genuinely extra attributes (e.g. drivers, with licence detail) get a thin divisional extension table.

---

### suppliers_vendors
Any external party who supplies goods or services to a division,
including AgriCore's farmers. Referenced by: Retail, AgriCore, Logistics.

| Column                | Type          | Constraints                                   | Notes |
|------------------------|---------------|-------------------------------------------------|-------|
| supplier_id             | UUID          | PRIMARY KEY, default gen_random_uuid()          | |
| legal_name              | VARCHAR(150)  | NOT NULL                                        | |
| supplier_type            | VARCHAR(30)   | NOT NULL, CHECK IN ('farmer','wholesale_supplier','service_vendor','other') | value list not specified by brief; grounded in section 1.1/1.3 divisional profiles |
| primary_division_id      | SMALLINT      | NOT NULL, REFERENCES divisions                  | |
| onboarding_date          | DATE          | NOT NULL                                        | |
| status                    | VARCHAR(20)   | NOT NULL, default 'active', CHECK IN ('active','inactive','suspended') | |

**Design note:** a farmer is modeled as an external supplier, not an employee — reflects the real business relationship (independent party selling to AgriCore, not Veridian personnel). See `farmers` in the AgriCore module for farmer-specific extension detail (1:1, UNIQUE constraint).

---

### locations_sites
Any physical site operated, leased, or visited by the group — the
single consistent address/geocoordinate standard across all divisions.
Referenced by: Retail, Logistics, AgriCore, Properties.

| Column          | Type            | Constraints                            | Notes |
|------------------|------------------|-------------------------------------------|-------|
| location_id       | UUID            | PRIMARY KEY, default gen_random_uuid()    | |
| site_name         | VARCHAR(150)    | NOT NULL                                  | |
| site_type          | VARCHAR(30)     | NOT NULL, CHECK IN ('store','warehouse','processing_facility','property','office') | 'warehouse' and 'depot' deliberately not split — see design note |
| address            | VARCHAR(255)    | NOT NULL                                  | |
| city                | VARCHAR(100)    | NOT NULL                                  | |
| country_code        | CHAR(2)         | NOT NULL                                  | |
| latitude             | NUMERIC(9,6)    | nullable                                  | |
| longitude            | NUMERIC(9,6)    | nullable                                  | |

**Design note:** section 1.3.2 refers to "warehouses and depots," but Concord Logistics' own `warehouses` entity (section 5.2.2) doesn't distinguish them — one table, one `warehouse_id`. Splitting `site_type` into separate `warehouse`/`depot` values at the hub level would create a classification the rest of the schema can't act on. If a depot/storage distinction is ever needed, it belongs as an attribute on the divisional `warehouses` table, not the shared `site_type` classification.

---

### product_service_catalogue
Shared master list of sellable products and services across divisions.
Referenced by: Retail, AgriCore.

| Column                | Type          | Constraints                             | Notes |
|------------------------|---------------|--------------------------------------------|-------|
| product_id               | UUID          | PRIMARY KEY, default gen_random_uuid()     | |
| product_name             | VARCHAR(150)  | NOT NULL                                   | |
| category                  | VARCHAR(50)   | NOT NULL, **no CHECK constraint**          | deliberately free text — see design note |
| unit_of_measure           | VARCHAR(20)   | NOT NULL                                   | e.g. 'kg', 'unit', 'litre' |
| primary_division_id       | SMALLINT      | NOT NULL, REFERENCES divisions             | |
| is_active                  | BOOLEAN       | NOT NULL, default TRUE                     | |

**Design note:** unlike other typed columns in this schema, `category` is intentionally left as unconstrained free text rather than a CHECK list. Retail and AgriCore categories (grocery/household goods vs. maize/sorghum/cowpea/processed goods, per section 1.1) are genuinely divergent and open-ended; a controlled vocabulary is documented here rather than DB-enforced, to avoid needing a constraint migration every time a new product category is introduced during data generation.

---

### financial_account_references
Controlled, non-sensitive reference linking a customer to a Veridian
Financial Services account, without duplicating core banking detail.
Referenced by: Financial Services (read-restricted elsewhere — see RLS notes).

| Column          | Type            | Constraints                              | Notes |
|------------------|------------------|----------------------------------------------|-------|
| account_ref_id    | UUID            | PRIMARY KEY, default gen_random_uuid()       | |
| customer_id        | UUID            | NOT NULL, REFERENCES customers               | |
| account_type        | VARCHAR(20)     | NOT NULL, CHECK IN ('wallet','savings','loan') | directly specified in section 1.3.3 — VFS's three named products |
| account_status       | VARCHAR(20)     | NOT NULL, default 'active', CHECK IN ('active','dormant','closed') | |
| opened_date           | DATE            | NOT NULL                                     | |

**Design note:** this table deliberately holds no balance, transaction, or loan detail — it exists purely as the sanctioned, non-sensitive bridge between a customer and their financial products. Full financial data lives exclusively in the VFS module, which is read-restricted per section 4.4.

---

## RLS Summary — Core Services Hub

| Table                          | Read access                                   | Write access |
|----------------------------------|--------------------------------------------------|----------------|
| divisions                        | any authenticated role                            | (not restricted — reference data) |
| customers                        | any authenticated role                            | — |
| employees                        | any authenticated role                            | — |
| suppliers_vendors                | any authenticated role                            | — |
| locations_sites                  | any authenticated role                            | — |
| product_service_catalogue        | any authenticated role                            | — |
| financial_account_references     | financial_services (full); group_executive (consent-gated via `consent_financial_visibility`) | financial_services only |

**Known infrastructure note:** Supabase enables RLS by default on every new table at creation time — every hub table required an explicit policy before being queryable via the REST API, even for "open to all roles" tables. This was discovered during testing when Core Hub tables silently returned zero rows to every role, including ones that should have had full access.


## Part 2: Meridian Retail and Consumer Module

Eight entities (seven from the original brief spec, plus
`delivery_line_items`, added to close a derivability gap — see design
note under `inventory_stock_levels`).

---

### stores
Each physical or online retail channel.

| Column                | Type          | Constraints                                     | Notes |
|------------------------|---------------|-----------------------------------------------------|-------|
| store_id                 | UUID          | PRIMARY KEY, default gen_random_uuid()             | |
| location_id               | UUID          | NOT NULL, REFERENCES locations_sites               | |
| store_format               | VARCHAR(20)   | NOT NULL, CHECK IN ('large_format','neighbourhood','online') | grounded in section 1.3.1 — large-format stores, neighbourhood outlets, MeridianGo (online) |
| opening_date                | DATE          | NOT NULL                                           | |
| manager_employee_id          | UUID          | REFERENCES employees, nullable                     | |

---

### pos_transactions
Individual point-of-sale or MeridianGo sales.

| Column              | Type            | Constraints                                    | Notes |
|-----------------------|-----------------|-----------------------------------------------------|-------|
| transaction_id          | UUID            | PRIMARY KEY, default gen_random_uuid()             | |
| store_id                 | UUID            | NOT NULL, REFERENCES stores                        | |
| customer_id               | UUID            | REFERENCES customers, **nullable**                 | not every sale is tied to a known/loyalty customer (walk-in cash sales) |
| transaction_date           | TIMESTAMP       | NOT NULL, default now()                            | |
| total_amount                 | NUMERIC(12,2)   | NOT NULL, CHECK >= 0                               | stored independently of line items — see design note |
| payment_method                | VARCHAR(20)     | NOT NULL, CHECK IN ('cash','card','wallet','other') | 'wallet' is a label only — no FK into VFS, see design note |

**Design note (total_amount):** `total_amount` is stored directly rather than derived by summing `transaction_line_items` on every read. This is a deliberate, common retail-system denormalization — not DB-enforced to always equal the line-item sum. Documented as an acknowledged tradeoff, not fixed with a trigger, to keep the schema at the complexity level appropriate for this engagement.

**Design note (payment_method = 'wallet'):** this column records *that* a wallet was used, not a link to the underlying wallet transaction. No FK exists into `wallet_transactions` because VFS is read-restricted per section 4.4 and treated as an externally-sourced system per section 3.3 — a direct FK would create a queryable join path around that boundary for any role with access to `pos_transactions`.

---

### transaction_line_items
Individual products within a transaction. Event log — one row per
product per sale, accumulates indefinitely.

| Column          | Type            | Constraints                             | Notes |
|------------------|------------------|----------------------------------------------|-------|
| line_item_id       | UUID            | PRIMARY KEY, default gen_random_uuid()       | |
| transaction_id       | UUID            | NOT NULL, REFERENCES pos_transactions        | |
| product_id            | UUID            | NOT NULL, REFERENCES product_service_catalogue | |
| quantity                | NUMERIC(10,2)   | NOT NULL, CHECK > 0                          | |
| unit_price                | NUMERIC(12,2)   | NOT NULL, CHECK >= 0                         | |

---

### inventory_stock_levels
Current stock on hand by store and product. Current-state snapshot —
one row per store-product pair, mutated in place (not an event log).

| Column              | Type            | Constraints                                          | Notes |
|-----------------------|-----------------|-----------------------------------------------------------|-------|
| stock_id                 | UUID            | PRIMARY KEY, default gen_random_uuid()                    | |
| store_id                  | UUID            | NOT NULL, REFERENCES stores                                | |
| product_id                 | UUID            | NOT NULL, REFERENCES product_service_catalogue             | |
| quantity_on_hand              | NUMERIC(10,2)   | NOT NULL, default 0, CHECK >= 0                            | |
| last_counted_date               | DATE            | nullable                                                   | represents the last PHYSICAL stock count/audit — updates roughly weekly, NOT on every sale/delivery |
| —                                | —               | UNIQUE(store_id, product_id)                                | enforces exactly one current-state row per pair |

**Design note:** originally described as derivable (deliveries received minus quantities sold), this was only true for the sales side — `supplier_deliveries` had no quantity-level detail, making the delivery side of that calculation impossible. Fixed by adding `delivery_line_items` (below). `quantity_on_hand` is now genuinely reconcilable as: Σ delivery_line_items.quantity − Σ transaction_line_items.quantity, for a given store+product.

**Realism note:** per section 1.3.1, real-world stock counts show a documented 3-8% discrepancy against system-recorded stock. Synthetic data generation should preserve this gap deliberately (see Appendix D) rather than keeping `quantity_on_hand` perfectly reconciled at all times.

---

### promotions
Time-bound pricing and marketing promotions.

| Column        | Type          | Constraints                                             | Notes |
|-----------------|---------------|--------------------------------------------------------------|-------|
| promotion_id      | UUID          | PRIMARY KEY, default gen_random_uuid()                       | |
| product_id          | UUID          | NOT NULL, REFERENCES product_service_catalogue                | |
| discount_type         | VARCHAR(20)   | NOT NULL, CHECK IN ('percentage','fixed_amount','bogo')       | |
| start_date              | DATE          | NOT NULL                                                      | |
| end_date                  | DATE          | NOT NULL, CHECK (end_date > start_date)                       | |

---

### loyalty_accounts
Customer enrolment in the retail loyalty programme.

| Column          | Type            | Constraints                                         | Notes |
|------------------|------------------|-----------------------------------------------------------|-------|
| loyalty_id          | UUID            | PRIMARY KEY, default gen_random_uuid()                     | |
| customer_id           | UUID            | NOT NULL, REFERENCES customers                             | |
| tier                    | VARCHAR(20)     | NOT NULL, default 'bronze', CHECK IN ('bronze','silver','gold','platinum') | |
| points_balance             | INTEGER         | NOT NULL, default 0, CHECK >= 0                            | opaque running total — see design note |
| enrolment_date               | DATE            | NOT NULL, default CURRENT_DATE                             | |

**Design note (points_balance):** unlike `inventory_stock_levels`, this balance has **no supporting earn/redeem transaction log** — it's a stored total with nothing to derive or reconcile it against. A `loyalty_points_transactions` table would fix this, mirroring the fix applied to stock — but is treated as a documented, deliberate simplification rather than built, since loyalty detail is not part of any of the four required stakeholder scenarios (section 3.1) and adding it would be scope creep beyond the brief's 40-55 table target.

---

### supplier_deliveries
Deliveries received from suppliers, including AgriCore.

| Column           | Type      | Constraints                                                      | Notes |
|--------------------|-----------|------------------------------------------------------------------------|-------|
| delivery_id           | UUID      | PRIMARY KEY, default gen_random_uuid()                                  | |
| supplier_id             | UUID      | NOT NULL, REFERENCES suppliers_vendors                                  | |
| store_id                 | UUID      | NOT NULL, REFERENCES stores                                             | |
| expected_date              | DATE      | NOT NULL                                                                | |
| received_date                | DATE      | nullable                                                                | |
| status                          | VARCHAR(20) | NOT NULL, default 'pending', CHECK IN ('pending','received','delayed','cancelled') | |

---

### delivery_line_items
*Added after the initial build to close a derivability gap — see
`inventory_stock_levels` design note above. Mirrors
`transaction_line_items` structurally.*

| Column              | Type            | Constraints                                    | Notes |
|-----------------------|-----------------|------------------------------------------------------|-------|
| delivery_line_id         | UUID            | PRIMARY KEY, default gen_random_uuid()               | |
| delivery_id                | UUID            | NOT NULL, REFERENCES supplier_deliveries              | |
| product_id                   | UUID            | NOT NULL, REFERENCES product_service_catalogue        | |
| quantity                       | NUMERIC(10,2)   | NOT NULL, CHECK > 0                                   | |

---

## RLS Summary — Retail Module

| Table                     | Read access                        | Write access |
|-----------------------------|---------------------------------------|-----------------|
| stores                        | retail_ops, group_executive            | retail_ops |
| pos_transactions               | retail_ops, group_executive            | retail_ops |
| transaction_line_items           | retail_ops, group_executive            | retail_ops |
| inventory_stock_levels             | retail_ops, group_executive            | retail_ops |
| promotions                           | retail_ops, group_executive            | retail_ops |
| loyalty_accounts                       | retail_ops, group_executive            | retail_ops |
| supplier_deliveries                      | retail_ops, group_executive            | retail_ops |
| delivery_line_items                        | retail_ops, group_executive            | retail_ops |

Tested end-to-end: confirmed `retail_ops` can read a seeded `stores`
row via the REST API; confirmed `logistics_ops` is correctly blocked
(`[]`) on the same table.

## Part 3: Concord Logistics Module

Seven entities per section 5.2.2, plus one column added after the
fact (`shipment_legs.route_id`) to close a connectivity gap.

---

### vehicles
Fleet assets owned or leased by Concord Logistics.

| Column                | Type            | Constraints                                            | Notes |
|-------------------------|-----------------|---------------------------------------------------------------|-------|
| vehicle_id                 | UUID            | PRIMARY KEY, default gen_random_uuid()                        | |
| registration_number          | VARCHAR(20)     | NOT NULL, UNIQUE                                              | |
| vehicle_type                    | VARCHAR(20)     | NOT NULL, CHECK IN ('van','truck')                            | grounded in section 1.3.2 — "small delivery vans... large freight trucks" |
| capacity_kg                        | NUMERIC(10,2)   | NOT NULL, CHECK > 0                                            | |
| status                                | VARCHAR(20)     | NOT NULL, default 'active', CHECK IN ('active','in_maintenance','retired') | |

---

### drivers
Employees or contracted drivers operating vehicles. Thin extension
table over `employees` — only exists because drivers have
licence-specific attributes an ordinary employee record doesn't capture.

| Column          | Type          | Constraints                          | Notes |
|------------------|---------------|-------------------------------------------|-------|
| driver_id           | UUID          | PRIMARY KEY, default gen_random_uuid()     | |
| employee_id           | UUID          | NOT NULL, REFERENCES employees             | |
| licence_number           | VARCHAR(30)   | NOT NULL, UNIQUE                           | |
| licence_expiry             | DATE          | NOT NULL                                   | |

---

### routes
Defined, reusable delivery routes.

| Column                    | Type            | Constraints                                   | Notes |
|------------------------------|-----------------|------------------------------------------------------|-------|
| route_id                        | UUID            | PRIMARY KEY, default gen_random_uuid()               | |
| route_name                        | VARCHAR(100)    | NOT NULL                                             | |
| origin_location_id                  | UUID            | NOT NULL, REFERENCES locations_sites                  | |
| destination_location_id               | UUID            | NOT NULL, REFERENCES locations_sites                    | |
| distance_km                              | NUMERIC(8,2)    | NOT NULL, CHECK > 0                                    | |

**Design note:** originally built but left disconnected from the rest of the schema — no other table referenced it, meaning "which route did this shipment take" was unanswerable despite the table existing. Fixed by adding `shipment_legs.route_id` (see below). This directly enables the analytical question named in section 1.3.2: "which routes are least profitable."

---

### shipments
Individual freight or delivery movements — the overall journey/order,
independent of which specific vehicle(s) fulfill it.

| Column                    | Type          | Constraints                                       | Notes |
|------------------------------|---------------|-----------------------------------------------------------|-------|
| shipment_id                    | UUID          | PRIMARY KEY, default gen_random_uuid()                    | |
| origin_location_id               | UUID          | NOT NULL, REFERENCES locations_sites                       | |
| destination_location_id            | UUID          | NOT NULL, REFERENCES locations_sites                         | |
| client_type                          | VARCHAR(20)   | NOT NULL, CHECK IN ('internal','third_party')                | maps to the 55%/45% internal-vs-external freight split, section 1.3.2 |
| status                                  | VARCHAR(20)   | NOT NULL, default 'scheduled', CHECK IN ('scheduled','in_transit','delivered','delayed','cancelled') | |

---

### shipment_legs
Individual vehicle-and-driver assignments fulfilling a shipment. A
single shipment may have one leg (simple, direct delivery) or
multiple legs (handoff between vehicles/depots).

| Column              | Type          | Constraints                                              | Notes |
|-----------------------|---------------|-----------------------------------------------------------------|-------|
| leg_id                   | UUID          | PRIMARY KEY, default gen_random_uuid()                            | |
| shipment_id                | UUID          | NOT NULL, REFERENCES shipments                                    | |
| vehicle_id                   | UUID          | NOT NULL, REFERENCES vehicles                                       | |
| driver_id                       | UUID          | NOT NULL, REFERENCES drivers                                        | |
| route_id                           | UUID          | REFERENCES routes, **nullable**                                     | added post-build — see `routes` design note. Nullable: a leg may be ad-hoc and not follow a predefined reusable route |
| departure_time                       | TIMESTAMP     | NOT NULL                                                            | |
| arrival_time                            | TIMESTAMP     | nullable, CHECK (arrival_time IS NULL OR arrival_time > departure_time) | nullable: a leg in progress won't have an arrival time yet |

---

### warehouses
Depot and warehouse facilities used for storage and cross-docking.
'Warehouse' and 'depot' deliberately not modeled as separate types —
see `locations_sites.site_type` design note in Part 1.

| Column                    | Type            | Constraints                                    | Notes |
|------------------------------|-----------------|--------------------------------------------------------|-------|
| warehouse_id                    | UUID            | PRIMARY KEY, default gen_random_uuid()                 | |
| location_id                        | UUID            | NOT NULL, REFERENCES locations_sites                     | |
| capacity_units                        | NUMERIC(12,2)   | NOT NULL, CHECK > 0                                       | |
| leased_from_property_id                  | UUID            | REFERENCES properties(property_id) — **added later**, see note | initially created without this FK since the Properties module didn't exist yet when this table was built |

**Design note:** this table is deliberately readable by `properties_ops` in addition to `logistics_ops` (non-standard RLS grant — see RLS summary below), since it represents the exact seam described in scenario 3 (section 2.4, Funmi/warehouse) — a lease detail owned by Properties but operationally critical to Logistics. This is the one warehouse-adjacent case where cross-divisional visibility is deliberately built in rather than mediated purely through the Core Hub.

---

### maintenance_logs
Vehicle servicing and repair history. Event log — accumulates one row
per service event.

| Column          | Type            | Constraints                            | Notes |
|------------------|------------------|----------------------------------------------|-------|
| maintenance_id      | UUID            | PRIMARY KEY, default gen_random_uuid()        | |
| vehicle_id            | UUID            | NOT NULL, REFERENCES vehicles                 | |
| service_date            | DATE            | NOT NULL                                      | |
| cost                       | NUMERIC(10,2)   | NOT NULL, CHECK >= 0                          | |
| description                   | VARCHAR(255)    | nullable                                      | |

**Purpose:** directly enables the analytical question named in section 1.3.2 — "which vehicles have the highest maintenance cost per kilometre" (joined against `shipment_legs`/`routes` for distance).

---

## RLS Summary — Logistics Module

| Table              | Read access                                          | Write access |
|-----------------------|-----------------------------------------------------------|-----------------|
| vehicles                 | logistics_ops, group_executive                             | logistics_ops |
| drivers                    | logistics_ops, group_executive                             | logistics_ops |
| routes                        | logistics_ops, group_executive                             | logistics_ops |
| shipments                        | logistics_ops, group_executive                             | logistics_ops |
| shipment_legs                        | logistics_ops, group_executive                             | logistics_ops |
| maintenance_logs                        | logistics_ops, group_executive                             | logistics_ops |
| **warehouses**                             | **logistics_ops, properties_ops, group_executive** (non-standard) | logistics_ops |

No FK from any Logistics table into VFS — consistent with the
read-restriction principle established in the Retail module.

## Part 4: Veridian Financial Services Module

Six entities per section 5.2.3. As established in section 4.4, this
module represents a curated, externally sourced view of VFS data —
not a reconstruction of the core banking system. Every entity here
is read-restricted by design; this is the module with the most
significant RLS logic in the whole platform.

---

### wallet_accounts
Mobile wallet accounts linked to a customer.

| Column          | Type            | Constraints                                       | Notes |
|------------------|------------------|-----------------------------------------------------------|-------|
| wallet_id            | UUID            | PRIMARY KEY, default gen_random_uuid()                      | |
| customer_id            | UUID            | NOT NULL, REFERENCES customers                                | |
| account_ref_id            | UUID            | NOT NULL, REFERENCES financial_account_references                | |
| balance                       | NUMERIC(14,2)   | NOT NULL, default 0, CHECK >= 0                                  | |
| status                          | VARCHAR(20)     | NOT NULL, default 'active', CHECK IN ('active','dormant','closed') | |

---

### wallet_transactions
Individual wallet payment or transfer events. Event log.

| Column              | Type            | Constraints                                                              | Notes |
|-----------------------|-----------------|----------------------------------------------------------------------------------|-------|
| wallet_txn_id            | UUID            | PRIMARY KEY, default gen_random_uuid()                                            | |
| wallet_id                  | UUID            | NOT NULL, REFERENCES wallet_accounts                                                | |
| counterparty_type             | VARCHAR(20)     | NOT NULL, CHECK IN ('merchant','peer','loan_disbursement','loan_repayment','other') | |
| amount                            | NUMERIC(12,2)   | NOT NULL                                                                            | |
| transaction_date                     | TIMESTAMP       | NOT NULL, default now()                                                             | |

**Design note:** no FK links a `'loan_repayment'`-type transaction to the specific `loan_repayments` row it satisfies, nor is there a link from a settlement-bound transaction to its `merchant_settlements` batch. This is treated as intentionally shallow, consistent with VFS being a curated external representation rather than a full core-banking reconstruction (section 3.3) — not a gap to be fixed.

---

### loans
Working capital and asset finance loans. Borrower is either a
customer or a supplier (farmer), never both, never neither — a
polymorphic reference pattern used three times across this schema
(see normalization notes).

| Column                  | Type            | Constraints                                                       | Notes |
|----------------------------|-----------------|----------------------------------------------------------------------|-------|
| loan_id                        | UUID            | PRIMARY KEY, default gen_random_uuid()                                | |
| borrower_customer_id               | UUID            | REFERENCES customers, nullable                                          | |
| borrower_supplier_id                   | UUID            | REFERENCES suppliers_vendors, nullable                                     | |
| principal_amount                          | NUMERIC(14,2)   | NOT NULL, CHECK > 0                                                          | |
| status                                       | VARCHAR(20)     | NOT NULL, default 'active', CHECK IN ('active','repaid','defaulted','written_off') | |
| —                                                | —               | CHECK: exactly one of borrower_customer_id / borrower_supplier_id is set        | encodes the two borrower scenarios in the brief: a customer, or a farmer via `suppliers_vendors` (scenario 2, Chinedu/Ibrahim) |

---

### loan_repayments
Individual repayment instalments against a loan. Event log.

| Column          | Type            | Constraints                                | Notes |
|------------------|------------------|--------------------------------------------------|-------|
| repayment_id         | UUID            | PRIMARY KEY, default gen_random_uuid()             | |
| loan_id                | UUID            | NOT NULL, REFERENCES loans                           | |
| due_date                  | DATE            | NOT NULL                                              | |
| amount_due                   | NUMERIC(12,2)   | NOT NULL, CHECK > 0                                    | |
| amount_paid                     | NUMERIC(12,2)   | NOT NULL, default 0, CHECK >= 0                          | |
| paid_date                          | DATE            | nullable                                                   | |

---

### kyc_records
Know-your-customer verification status. **The most restricted entity
in the entire platform** — per section 5.2.3, accessible to
`financial_services` only. No executive access, no exceptions.

| Column                  | Type          | Constraints                                     | Notes |
|----------------------------|---------------|------------------------------------------------------|-------|
| kyc_id                        | UUID          | PRIMARY KEY, default gen_random_uuid()                | |
| customer_id                      | UUID          | NOT NULL, REFERENCES customers                          | |
| verification_level                  | VARCHAR(20)   | NOT NULL, CHECK IN ('tier1','tier2','tier3')              | |
| verified_date                          | DATE          | NOT NULL                                                    | |

---

### merchant_settlements
Batch settlement of wallet payments to merchant divisions — division-
level, not customer-level, so not consent-gated the way other VFS
tables are.

| Column              | Type            | Constraints                            | Notes |
|-----------------------|-----------------|------------------------------------------------|-------|
| settlement_id            | UUID            | PRIMARY KEY, default gen_random_uuid()          | |
| division_id                | SMALLINT        | NOT NULL, REFERENCES divisions                    | |
| settlement_date               | DATE            | NOT NULL                                             | |
| total_amount                     | NUMERIC(14,2)   | NOT NULL, CHECK >= 0                                    | |

---

## RLS Summary — Financial Services Module

This is the platform's core regulatory-compliance implementation
(section 2.3/4.4). Every policy is claims-based, checking
`auth.jwt() ->> 'user_role'` — rewritten from an initial
Postgres-role-based approach (`TO financial_services`) that doesn't
work with Supabase's PostgREST/JWT auth model.

| Table                  | financial_services | group_executive                                    | write access |
|---------------------------|----------------------|----------------------------------------------------------|-----------------|
| wallet_accounts               | full read              | **consent-gated**: only rows where the linked customer has `consent_financial_visibility = true` | financial_services only |
| wallet_transactions               | full read              | consent-gated, via the linked wallet_account's customer     | financial_services only |
| loans                                 | full read              | consent-gated for customer borrowers; **not** gated for supplier/farmer borrowers (no consent flag exists on suppliers by design — see below) | financial_services only |
| loan_repayments                          | full read              | consent-gated, inherited from the parent loan's borrower logic | financial_services only |
| **kyc_records**                             | **full read**           | **NO ACCESS — no policy exists for this role at all**          | financial_services only |
| merchant_settlements                            | full read              | full read (division-level, no consent issue)                     | financial_services only |

**Design note (supplier borrowers not consent-gated):** the brief's
consent mechanism (section 4.4) is explicitly scoped to the
`customers` table only — there is no equivalent consent flag on
`suppliers_vendors`. Farmer-borrower loan visibility for the
executive role is therefore governed purely by role membership, not
consent, since no consent field exists to check. This distinction —
which entities are consent-gated vs. purely role-gated — is
deliberate and documented here rather than left implicit.

**Verified via live testing (not just policy inspection):**
- `financial_services` token → full read confirmed on `wallet_accounts`
- `retail_ops` token → correctly blocked (`[]`)
- `group_executive` token → initially incorrectly returned `[]` for a
  consenting customer; root-caused to two compounding issues:
  (1) `wallet_accounts.exec_consent_read` had not yet been migrated
  off the old Postgres-role syntax during the claims rewrite pass,
  and (2) the `customers` table itself had RLS enabled with zero
  policies, silently blocking the exec policy's own subquery into it
  regardless of the outer policy's correctness. Both fixed; re-tested
  and confirmed working.


  ## Part 5: AgriCore Module

Eight entities: seven per section 5.2.4, plus `harvest_payments`,
added after the fact to close a real gap — AgriCore paying farmers
for delivered harvests had no representation anywhere in the original
schema.

---

### farms
Registered farms linked to a supplier (farmer).

| Column            | Type            | Constraints                                | Notes |
|---------------------|-----------------|----------------------------------------------------|-------|
| farm_id                | UUID            | PRIMARY KEY, default gen_random_uuid()               | |
| supplier_id              | UUID            | NOT NULL, REFERENCES suppliers_vendors                 | |
| location_id                | UUID            | NOT NULL, REFERENCES locations_sites                     | |
| size_hectares                 | NUMERIC(10,2)   | NOT NULL, CHECK > 0                                        | |
| primary_crop                     | VARCHAR(50)     | NOT NULL, free text                                          | e.g. maize, sorghum, cowpea per section 1.1 |

**Cardinality note (section 5.3):** one farm belongs to exactly one supplier, but one supplier may register multiple farms — common among larger cooperative-affiliated growers.

---

### farmers
Individual farmer profile detail, linked 1:1 to the supplier core entity.

| Column              | Type          | Constraints                                   | Notes |
|-----------------------|---------------|------------------------------------------------------|-------|
| farmer_id                | UUID          | PRIMARY KEY, default gen_random_uuid()                | |
| supplier_id                | UUID          | NOT NULL, **UNIQUE**, REFERENCES suppliers_vendors        | enforces "at most one farmer profile per supplier" (section 5.3) |
| registration_date              | DATE          | NOT NULL                                                     | |
| cooperative_name                  | VARCHAR(150)  | nullable                                                        | not every farmer belongs to a cooperative |

**Design note:** see Part 1's design note on `suppliers_vendors` — a farmer is modeled as an external supplier, not an employee, reflecting the real business relationship: independent, not on Veridian's payroll.

---

### harvest_batches
Individual harvest collection events. Event log.

| Column                        | Type            | Constraints                              | Notes |
|-----------------------------------|-----------------|------------------------------------------------|-------|
| harvest_id                             | UUID            | PRIMARY KEY, default gen_random_uuid()          | |
| farm_id                                    | UUID            | NOT NULL, REFERENCES farms                        | |
| product_id                                     | UUID            | NOT NULL, REFERENCES product_service_catalogue     | |
| harvest_date                                        | DATE            | NOT NULL                                              | |
| volume_kg                                              | NUMERIC(12,2)   | NOT NULL, CHECK > 0                                     | |
| field_agent_employee_id                                    | UUID            | NOT NULL, REFERENCES employees                            | field agents are ordinary employees, not a dedicated table — see Part 1 |

---

### processing_runs
Processing and grading activity at AgriCore facilities.

| Column                    | Type            | Constraints                            | Notes |
|------------------------------|-----------------|------------------------------------------------|-------|
| run_id                          | UUID            | PRIMARY KEY, default gen_random_uuid()          | |
| harvest_id                          | UUID            | NOT NULL, REFERENCES harvest_batches               | |
| facility_location_id                    | UUID            | NOT NULL, REFERENCES locations_sites                  | |
| run_date                                    | DATE            | NOT NULL                                                 | |
| output_volume_kg                                | NUMERIC(12,2)   | NOT NULL, CHECK >= 0                                        | |

**Cardinality note (section 5.3):** one harvest batch may generate zero, one, or more processing runs; each run references exactly one harvest batch — preserves full farm-to-processed-product traceability.

---

### quality_grades
Grading outcomes applied to a processing run.

| Column                    | Type            | Constraints                                     | Notes |
|------------------------------|-----------------|--------------------------------------------------------|-------|
| grade_id                        | UUID            | PRIMARY KEY, default gen_random_uuid()                    | |
| run_id                              | UUID            | NOT NULL, REFERENCES processing_runs                          | |
| grade_level                             | VARCHAR(10)     | NOT NULL, CHECK IN ('A','B','C','reject')                        | value scale not specified by brief; a plausible, documented choice |
| moisture_content                            | NUMERIC(5,2)    | CHECK (0-100), nullable                                              | |
| inspector_employee_id                           | UUID            | NOT NULL, REFERENCES employees                                          | |

---

### wholesale_shipments
Outbound shipments to Meridian Retail or external clients.

| Column                        | Type          | Constraints                                                | Notes |
|-----------------------------------|---------------|-------------------------------------------------------------------|-------|
| wholesale_id                          | UUID          | PRIMARY KEY, default gen_random_uuid()                              | |
| run_id                                    | UUID          | NOT NULL, REFERENCES processing_runs                                    | |
| destination_type                              | VARCHAR(20)   | NOT NULL, CHECK IN ('meridian_retail','external_client')                    | |
| destination_store_id                              | UUID          | REFERENCES stores, nullable                                                    | populated only when destination_type = 'meridian_retail' |
| destination_external_name                             | VARCHAR(150)  | nullable                                                                          | populated only when destination_type = 'external_client'; no dedicated external-client entity exists (out of scope) |
| shipment_id                                               | UUID          | REFERENCES shipments, nullable                                                       | bridges to Concord Logistics; nullable — a wholesale shipment may be recorded before a logistics shipment is arranged |
| —                                                              | —             | CHECK: exactly one of destination_store_id / destination_external_name is set              | |

**Design note:** originally a single unconstrained `destination_id` + `destination_type` pair — corrected once identified as an unenforceable polymorphic reference (a plain FK can only point to one table). Rebuilt using the same exclusive-nullable-columns pattern used for `loans` and `tenants` (see normalization notes).

---

### farmer_loans_reference
Read-only visibility bridge for AgriCore staff into a farmer's VFS
loan status — a summary only, not full loan detail.

| Column                    | Type          | Constraints                                            | Notes |
|------------------------------|---------------|----------------------------------------------------------------|-------|
| reference_id                    | UUID          | PRIMARY KEY, default gen_random_uuid()                          | |
| farmer_id                          | UUID          | NOT NULL, REFERENCES farmers                                       | |
| loan_id                                | UUID          | NOT NULL, REFERENCES loans                                            | |
| visible_summary_status                     | VARCHAR(20)   | NOT NULL, CHECK IN ('current','overdue','closed')                        | |

**Design note:** this is a one-way visibility mechanism, not a payment record — AgriCore does not issue, manage, or fund loans. The loan itself is entirely VFS's product. This table lets AgriCore staff see a filtered status signal (e.g., for prioritizing farmer outreach) without exposing full loan amount/repayment detail, consistent with section 4.4's "summarised, appropriately permissioned" requirement. The actual credit-decision use case (scenario 2, Chinedu assessing Ibrahim) flows the opposite direction — VFS querying into AgriCore's harvest/supply data, not AgriCore reading VFS's loan data.

---

### harvest_payments
*Added after the initial build — the original schema had no way to
represent AgriCore paying farmers for delivered harvests at all.*

| Column          | Type            | Constraints                                                   | Notes |
|------------------|------------------|------------------------------------------------------------------|-------|
| payment_id           | UUID            | PRIMARY KEY, default gen_random_uuid()                                | |
| harvest_id             | UUID            | NOT NULL, REFERENCES harvest_batches                                    | |
| amount                    | NUMERIC(12,2)   | NOT NULL, CHECK > 0                                                        | |
| payment_date                 | DATE            | NOT NULL                                                                      | |
| payment_method                   | VARCHAR(20)     | NOT NULL, CHECK IN ('bank_transfer','wallet','cash')                            | 'wallet' is a label only, no FK into VFS — same pattern as `pos_transactions.payment_method` |
| status                               | VARCHAR(20)     | NOT NULL, default 'pending', CHECK IN ('pending','paid','failed')                  | |

**Design note (no direct supplier_id FK):** the paid farmer is derivable via `harvest_batches.farm_id → farms.supplier_id`, so `supplier_id` is deliberately not duplicated here — avoids storing a fact that could drift out of sync with the farm's actual registered owner. Flagged as a candidate for future denormalization only if "pay this farmer" query performance becomes a demonstrated problem (Phase 4 review), not applied preemptively.

**Business context:** distinct from VFS loans — this is AgriCore paying for goods received (farmer → AgriCore direction), separate from and unrelated to VFS lending farmers working capital (VFS → farmer direction, before harvest).

---

## RLS Summary — AgriCore Module

| Table                      | Read access                                                  | Write access |
|--------------------------------|-------------------------------------------------------------------|-----------------|
| farms                            | agricore_ops, group_executive                                        | agricore_ops |
| farmers                              | agricore_ops, group_executive                                            | agricore_ops |
| harvest_batches                          | agricore_ops, group_executive                                                | agricore_ops |
| processing_runs                              | agricore_ops, group_executive                                                    | agricore_ops |
| quality_grades                                   | agricore_ops, group_executive                                                        | agricore_ops |
| harvest_payments                                     | agricore_ops, group_executive                                                            | agricore_ops |
| **wholesale_shipments**                                  | **agricore_ops, logistics_ops, group_executive** (non-standard — goods physically hand off to Concord Logistics) | agricore_ops |
| **farmer_loans_reference**                                   | **agricore_ops, financial_services, group_executive** (non-standard — VFS-derived summary data) | agricore_ops |