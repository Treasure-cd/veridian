-- POS Transactions: transactions that happen in the retail stores
CREATE TABLE pos_transactions (
    transaction_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id           UUID NOT NULL REFERENCES stores(store_id),
    customer_id        UUID REFERENCES customers(customer_id),
    transaction_date   TIMESTAMP NOT NULL DEFAULT now(),
    total_amount        NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
    payment_method      VARCHAR(20) NOT NULL
                        CHECK (payment_method IN ('cash','card','wallet','other'))
);