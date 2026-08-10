-- Routes taken
CREATE TABLE routes (
    route_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_name            VARCHAR(100) NOT NULL,
    origin_location_id    UUID NOT NULL REFERENCES locations_sites(location_id),
    destination_location_id UUID NOT NULL REFERENCES locations_sites(location_id),
    distance_km            NUMERIC(8,2) NOT NULL CHECK (distance_km > 0)
);
