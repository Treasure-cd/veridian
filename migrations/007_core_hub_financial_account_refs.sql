-- Financial Account References: controlled, non-sensitive pointer to a VFS account

CREATE TABLE financial_account_references (
    account_ref_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id      UUID NOT NULL REFERENCES customers(customer_id),
    account_type     VARCHAR(20) NOT NULL
                     CHECK (account_type IN ('wallet','savings','loan')),
    account_status   VARCHAR(20) NOT NULL DEFAULT 'active'
                     CHECK (account_status IN ('active','dormant','closed')),
    opened_date      DATE NOT NULL
);
