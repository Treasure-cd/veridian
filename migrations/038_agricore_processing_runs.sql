-- Processing runs
CREATE TABLE processing_runs (
    run_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    harvest_id            UUID NOT NULL REFERENCES harvest_batches(harvest_id),
    facility_location_id  UUID NOT NULL REFERENCES locations_sites(location_id),
    run_date               DATE NOT NULL,
    output_volume_kg        NUMERIC(12,2) NOT NULL CHECK (output_volume_kg >= 0)
);
