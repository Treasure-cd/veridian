-- Suppliers and Vendors: includes AgriCore's farmers (farmer detail lives in AgriCore module)
CREATE TABLE suppliers_vendors (
    supplier_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name           VARCHAR(150) NOT NULL,
    supplier_type        VARCHAR(30) NOT NULL
                          CHECK (supplier_type IN ('farmer','wholesale_supplier','service_vendor','other')),
    primary_division_id  SMALLINT NOT NULL REFERENCES divisions(division_id),
    onboarding_date      DATE NOT NULL,
    status                VARCHAR(20) NOT NULL DEFAULT 'active'
                          CHECK (status IN ('active','inactive','suspended'))
);