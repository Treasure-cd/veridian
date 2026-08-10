-- Harvest payments (new table)
CREATE TABLE harvest_payments (
    payment_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    harvest_id       UUID NOT NULL REFERENCES harvest_batches(harvest_id),
    amount             NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    payment_date       DATE NOT NULL,
    payment_method      VARCHAR(20) NOT NULL
                        CHECK (payment_method IN ('bank_transfer','wallet','cash')),
    status               VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','paid','failed'))
);
