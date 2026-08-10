-- Wallet transactions: every transactions that happens in here
CREATE TABLE wallet_transactions (
    wallet_txn_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id          UUID NOT NULL REFERENCES wallet_accounts(wallet_id),
    counterparty_type  VARCHAR(20) NOT NULL
                       CHECK (counterparty_type IN ('merchant','peer','loan_disbursement','loan_repayment','other')),
    amount              NUMERIC(12,2) NOT NULL,
    transaction_date    TIMESTAMP NOT NULL DEFAULT now()
);
