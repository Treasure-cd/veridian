-- Record for all the vehicles
CREATE TABLE vehicles (
    vehicle_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_number  VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type         VARCHAR(20) NOT NULL
                          CHECK (vehicle_type IN ('van','truck')),
    capacity_kg           NUMERIC(10,2) NOT NULL CHECK (capacity_kg > 0),
    status                 VARCHAR(20) NOT NULL DEFAULT 'active'
                           CHECK (status IN ('active','in_maintenance','retired'))
);
