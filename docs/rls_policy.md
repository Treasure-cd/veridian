# Row-Level Security Policy

This document summarizes the expected access model for Veridian modules and the roles permitted to read or manage each table.

## Access Principles

- Reference and shared-identity tables are broadly available to operational and executive roles.
- Financial data is restricted to the financial services team and, where appropriate, executive access is gated by customer consent.
- Sensitive or division-level data follows role-based access rules defined by module.

## Core Services Hub

| Table | Access |
| --- | --- |
| divisions | all roles (reference data) |
| customers | all roles (shared identity; sensitive fields such as financial visibility are handled separately by consent rules) |
| employees | all roles (shared identity) |
| suppliers_vendors | all roles (shared identity) |
| locations_sites | all roles (shared identity) |
| product_service_catalogue | all roles (shared identity) |
| financial_account_references | financial_services, group_executive (consent-gated) |

## Meridian Retail Module

| Table | Access |
| --- | --- |
| stores | retail_ops, group_executive |
| pos_transactions | retail_ops, group_executive |
| transaction_line_items | retail_ops, group_executive |
| inventory_stock_levels | retail_ops, group_executive |
| promotions | retail_ops, group_executive |
| loyalty_accounts | retail_ops, group_executive |
| supplier_deliveries | retail_ops, group_executive |

## Concord Logistics Module

| Table | Access |
| --- | --- |
| vehicles | logistics_ops, group_executive |
| drivers | logistics_ops, group_executive |
| routes | logistics_ops, group_executive |
| shipments | logistics_ops, group_executive |
| shipment_legs | logistics_ops, group_executive |
| warehouses | logistics_ops, properties_ops, group_executive |
| maintenance_logs | logistics_ops, group_executive |

## Veridian Financial Services Module

> Read access is restricted per the financial services policy and executive access is consent-gated where applicable.

| Table | Access |
| --- | --- |
| wallet_accounts | financial_services, group_executive (consent-gated) |
| wallet_transactions | financial_services, group_executive (consent-gated) |
| loans | financial_services, group_executive (consent-gated for customer borrowers; supplier/farmer borrowers are not consent-gated) |
| loan_repayments | financial_services, group_executive (consent-gated, inherited from loans) |
| kyc_records | financial_services only — no executive access |
| merchant_settlements | financial_services, group_executive (division-level, not consent-gated) |

## Agricore Module

| Table | Access |
| --- | --- |
| farms | agricore_ops, group_executive |
| farmers | agricore_ops, group_executive |
| harvest_batches | agricore_ops, group_executive |
| processing_runs | agricore_ops, group_executive |
| quality_grades | agricore_ops, group_executive |
| wholesale_shipments | agricore_ops, logistics_ops, group_executive |
| farmer_loans_reference | agricore_ops, financial_services, group_executive (summary-only, not full loan detail) |

## Veridian Properties Module

> This module is not yet built, but the intended access model is listed below.

| Table | Access |
| --- | --- |
| properties | properties_ops, group_executive |
| leases | properties_ops, group_executive |
| tenants | properties_ops, group_executive |
| maintenance_requests | properties_ops, group_executive |
| property_valuations | properties_ops, group_executive |
| utility_accounts | properties_ops, group_executive |
| facility_assets | properties_ops, group_executive |