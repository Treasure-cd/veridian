# NORMALIZATION & DESIGN DECISIONS — PROJECT CONCORD


## DELIBERATE DENORMALIZATION: inventory_stock_levels - Meridian Retail
   - Stock per store-product is technically a DERIVABLE value
     (sum of deliveries received minus sum of quantities sold via
     transaction_line_items).

   - It is stored directly as a mutable, current-state row instead of being
     recomputed from full transaction history on every read. So each product gets a row, and every change to the derivable tables (retail_line_items and retail_delivery_line_items) produces a change in the inventory_stock_levels table.

   - **Justification**: a retail floor stock lookup needs to be instant;
     recomputing from millions of historical line items on every query
     would be prohibitively slow.

   - UNIQUE(store_id, product_id) enforces exactly one current-state
     row per store-product pair — this is what makes it a snapshot,
     not an event log, distinguishing it structurally from
     transaction_line_items (which accumulates one row per event).



## POLYMORPHIC REFERENCE PATTERN (applied 3x)
We used exclusive nullable
   columns + CHECK constraint wherever an entity can point to
   exactly one of several different kinds of related things.

-  **loans** — borrower_customer_id / borrower_supplier_id
      A loan is taken out by either a retail customer or a
      farmer/supplier, never both, never neither.

-  **tenants** — division_id / external_tenant_name
      A lease tenant is either an internal Veridian division or an
      external third party, never both, never neither.

-  **wholesale_shipments** — destination_store_id / destination_external_name
      (originally a single unconstrained destination_id + destination_type
      column — corrected once the integrity gap was identified: a plain
      FK can only point to one table, and a shipment can go to either
      a known internal store OR an unmodeled external client.)

   All three use the same shape; two nullable columns representing the
   two possible destinations/relationships, plus a CHECK enforcing
   that exactly one is populated. This was chosen to be implemented over an external table or a UUID.


## DELIBERATE NON-RELATIONSHIP

No FK from Retail/AgriCore payment
   fields into VFS tables
   - pos_transactions.payment_method and harvest_payments.payment_method
     both include a plain 'wallet' value with NO foreign key into
     wallet_transactions.

   - **Justification**: VFS is read-restricted, and should have no FK relationships with external tables
     as an externally-sourced system, as stated in the requirements. A direct FK would
     create a queryable join path around RLS for any role with access
     to the referencing table, which is what the regulatory
     boundary is meant to prevent. The column records THAT a wallet was
     used, not a link to the underlying protected transaction.


## CONSENT-GATING AS DATA MODEL, NOT JUST ACCESS CONTROL
-   customers carries explicit boolean consent flags
     (consent_retail_personalisation, consent_financial_visibility)
     rather than a single blanket "shareable" flag.

-   This directly encodes the purpose-limitation requirement from
     Nigeria's Data Protection Act into the schema
     itself, not just into application logic — RLS policies query
     these flags directly (see farmer_loans_reference, exec_consent_read
     policies across VFS tables).

## HARVEST PAYMENTS FK TO harvest_id, NOT DUPLICATED supplier_id
   - harvest_payments references harvest_batches(harvest_id) only.
   - The paid farmer is derivable via harvest_batches.farm_id →
     farms.supplier_id, so storing supplier_id directly on
     harvest_payments would be redundant, denormalized data that
     could drift out of sync with the farm's actual registered owner.

## LEASE ACTIVITY AS A STORED COLUMN, NOT A DERIVED DATE COMPARISON
   - Added lease_status (active/expired/terminated) rather than relying
     on CURRENT_DATE between start_date and end_date to determine if a
     lease is active.
   - Necessary because Postgres partial unique indexes require an
     immutable predicate;"today's date" cannot be evaluated inside an
     index definition. This enabled a real constraint (at most one
     active lease per tenant, per the requirement) that couldn't otherwise
     be enforced at the database layer.
   - **Side effect**: end_date is no longer the sole signal of an active
     lease — it becomes more of a "planned end" reference, useful for
     "leases approaching renewal" queries, while
     lease_status is the authoritative current-state field.

## FARMERS AS SUPPLIERS, NOT EMPLOYEES — reinforcing existing hub design
   - farmers extends suppliers_vendors (1:1, UNIQUE constraint), not
     employees, even though field agents (who ARE employees) are the
     ones who interact with them.
   - Reflects the real business relationship: farmers are independent
     external parties selling goods to AgriCore, not Veridian
     personnel — matching the Core Hub's own definition of
     suppliers_vendors as "any external party who supplies goods or
     services to a division, including AgriCore's farmers".


## FIXED
- delivery_line_items added (inventory_stock_levels now genuinely derivable)
- shipment_legs.route_id added (routes table now connected/queryable)

## DOCUMENTED, DELIBERATE SIMPLIFICATIONS (not fixed, by design):
- pos_transactions.total_amount stored independently, not DB-enforced
  against the sum of transaction_line_items (common, defensible retail
  pattern, avoids recomputing on every read)
- loyalty_accounts.points_balance has no supporting earn/redeem
  transaction log, an opaque running total, not derivable
  (loyalty isn't part of the four required stakeholder scenarios;
  deeper modeling here would be scope creep)
- VFS internal traceability is intentionally shallow, no FK linking
  wallet_transactions to the specific loan_repayments they satisfy,
  or to the merchant_settlements batch they roll into — consistent
  with VFS being a curated external representation, not a full
  core-banking reconstruction.