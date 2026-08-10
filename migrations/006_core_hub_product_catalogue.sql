-- Product and Service Catalogue: shared master list across divisions
CREATE TABLE product_service_catalogue (
    product_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name          VARCHAR(150) NOT NULL,
    category               VARCHAR(50) NOT NULL,  -- free text, controlled vocabulary documented separately
    unit_of_measure        VARCHAR(20) NOT NULL,
    primary_division_id   SMALLINT NOT NULL REFERENCES divisions(division_id),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE
);