-- Shipments made
CREATE TABLE shipments (
    shipment_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_location_id       UUID NOT NULL REFERENCES locations_sites(location_id),
    destination_location_id  UUID NOT NULL REFERENCES locations_sites(location_id),
    client_type               VARCHAR(20) NOT NULL
                              CHECK (client_type IN ('internal','third_party')),
    status                     VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                               CHECK (status IN ('scheduled','in_transit','delivered','delayed','cancelled'))
);
