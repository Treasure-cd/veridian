
CREATE TABLE maintenance_logs (
    maintenance_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id        UUID NOT NULL REFERENCES vehicles(vehicle_id),
    service_date       DATE NOT NULL,
    cost                NUMERIC(10,2) NOT NULL CHECK (cost >= 0),
    description          VARCHAR(255)
);
