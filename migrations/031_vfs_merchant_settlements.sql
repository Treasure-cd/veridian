-- Merchant settlements
CREATE TABLE merchant_settlements (
    settlement_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    division_id       SMALLINT NOT NULL REFERENCES divisions(division_id),
    settlement_date    DATE NOT NULL,
    total_amount        NUMERIC(14,2) NOT NULL CHECK (total_amount >= 0)
);
