CREATE TABLE property_valuations (
    valuation_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id       UUID NOT NULL REFERENCES properties(property_id),
    valuation_date      DATE NOT NULL,
    assessed_value      NUMERIC(14,2) NOT NULL CHECK (assessed_value > 0)
);
