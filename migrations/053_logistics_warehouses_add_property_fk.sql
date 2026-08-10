-- Alter the warehouses table, so we can add a foreign key to properties (which now exists)
ALTER TABLE warehouses
    ADD CONSTRAINT fk_warehouses_property
    FOREIGN KEY (leased_from_property_id) REFERENCES properties(property_id);

CREATE INDEX idx_warehouses_property ON warehouses(leased_from_property_id);
