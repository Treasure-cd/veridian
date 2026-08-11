-- run in pgAdmin, superuser context — just to have something to query
INSERT INTO customers (full_name, primary_contact, registered_country, consent_financial_visibility)
VALUES ('Test Customer', '+2348000000000', 'NG', true)
RETURNING customer_id;
-- copy the returned customer_id, use it below

INSERT INTO financial_account_references (customer_id, account_type, opened_date)
VALUES ('62104e8f-bb9b-40f2-aecb-5f88bedbd7b4', 'wallet', CURRENT_DATE)
RETURNING account_ref_id;

INSERT INTO wallet_accounts (customer_id, account_ref_id, balance)
VALUES ('62104e8f-bb9b-40f2-aecb-5f88bedbd7b4', 'f59444ae-d0a9-48d9-bc87-53b2c90ed9b9', 5000.00);