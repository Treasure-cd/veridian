-- Information on farmers
CREATE TABLE farmers (
    farmer_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id         UUID NOT NULL UNIQUE REFERENCES suppliers_vendors(supplier_id),
    registration_date    DATE NOT NULL,
    cooperative_name      VARCHAR(150)
);
