CREATE TABLE leases (
    lease_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id       UUID NOT NULL REFERENCES properties(property_id),
    tenant_id         UUID NOT NULL REFERENCES tenants(tenant_id),
    start_date         DATE NOT NULL,
    end_date           DATE NOT NULL,
    monthly_rent        NUMERIC(12,2) NOT NULL CHECK (monthly_rent >= 0),
    CHECK (end_date > start_date)
);
