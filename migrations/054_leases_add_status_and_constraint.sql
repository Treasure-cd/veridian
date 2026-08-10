-- we add a coulmn to the lease tablel
ALTER TABLE leases
    ADD COLUMN lease_status VARCHAR(20) NOT NULL DEFAULT 'active'
    CHECK (lease_status IN ('active','expired','terminated'));
-- the index enforces the rule: at least one active lease per tenant
CREATE UNIQUE INDEX idx_one_active_lease_per_tenant
    ON leases (tenant_id)
    WHERE lease_status = 'active';
