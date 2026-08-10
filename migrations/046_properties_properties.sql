CREATE TABLE properties (
    property_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id        UUID NOT NULL REFERENCES locations_sites(location_id),
    property_type       VARCHAR(20) NOT NULL
                        CHECK (property_type IN ('store_premises','warehouse_depot','processing_adjacent','commercial','residential')),
    size_sqm             NUMERIC(10,2) NOT NULL CHECK (size_sqm > 0),
    ownership_status      VARCHAR(20) NOT NULL
                          CHECK (ownership_status IN ('owned','leased_in'))
);
