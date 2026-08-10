-- Suppler details
CREATE TABLE supplier_deliveries (
    delivery_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id      UUID NOT NULL REFERENCES suppliers_vendors(supplier_id),
    store_id         UUID NOT NULL REFERENCES stores(store_id),
    expected_date    DATE NOT NULL,
    received_date    DATE,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending','received','delayed','cancelled'))
);