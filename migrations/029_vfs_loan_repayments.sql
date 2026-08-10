-- When the loans are repayed back
CREATE TABLE loan_repayments (
    repayment_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id          UUID NOT NULL REFERENCES loans(loan_id),
    due_date          DATE NOT NULL,
    amount_due         NUMERIC(12,2) NOT NULL CHECK (amount_due > 0),
    amount_paid         NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (amount_paid >= 0),
    paid_date          DATE
);
