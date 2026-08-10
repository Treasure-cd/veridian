-- Warehouse information, linking to property id
CREATE TABLE warehouses (
    warehouse_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id                UUID NOT NULL REFERENCES locations_sites(location_id),
    capacity_units              NUMERIC(12,2) NOT NULL CHECK (capacity_units > 0),
    leased_from_property_id    UUID
);
