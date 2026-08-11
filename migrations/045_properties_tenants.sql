CREATE TABLE tenants (
    tenant_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_type            VARCHAR(20) NOT NULL
                           CHECK (tenant_type IN ('internal_division','external')),
    division_id            SMALLINT REFERENCES divisions(division_id),
    external_tenant_name    VARCHAR(150),
    CHECK (
        (tenant_type = 'internal_division' AND division_id IS NOT NULL AND external_tenant_name IS NULL)
        OR
        (tenant_type = 'external' AND division_id IS NULL AND external_tenant_name IS NOT NULL)
    )
);
