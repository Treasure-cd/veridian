-- constituent of a single shipment, a shipment can have multiple
CREATE TABLE shipment_legs (
    leg_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id      UUID NOT NULL REFERENCES shipments(shipment_id),
    vehicle_id       UUID NOT NULL REFERENCES vehicles(vehicle_id),
    driver_id        UUID NOT NULL REFERENCES drivers(driver_id),
    departure_time    TIMESTAMP NOT NULL,
    arrival_time      TIMESTAMP,
    CHECK (arrival_time IS NULL OR arrival_time > departure_time)
);
