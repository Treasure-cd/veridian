-- Informations about farms
CREATE TABLE farms (
    farm_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id      UUID NOT NULL REFERENCES suppliers_vendors(supplier_id),
    location_id      UUID NOT NULL REFERENCES locations_sites(location_id),
    size_hectares    NUMERIC(10,2) NOT NULL CHECK (size_hectares > 0),
    primary_crop      VARCHAR(50) NOT NULL 
);
