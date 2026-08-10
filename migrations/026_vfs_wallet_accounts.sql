-- Everyone that has a wallet account in veridian
CREATE TABLE wallet_accounts (
    wallet_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id       UUID NOT NULL REFERENCES customers(customer_id),
    account_ref_id    UUID NOT NULL REFERENCES financial_account_references(account_ref_id),
    balance            NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (balance >= 0),
    status              VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','dormant','closed'))
);
