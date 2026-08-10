-- Harvest batches information
CREATE TABLE harvest_batches (
    harvest_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id                   UUID NOT NULL REFERENCES farms(farm_id),
    product_id                UUID NOT NULL REFERENCES product_service_catalogue(product_id),
    harvest_date                DATE NOT NULL,
    volume_kg                    NUMERIC(12,2) NOT NULL CHECK (volume_kg > 0),
    field_agent_employee_id    UUID NOT NULL REFERENCES employees(employee_id)
);
