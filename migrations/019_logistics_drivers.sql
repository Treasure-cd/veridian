-- Drivers 
CREATE TABLE drivers (
    driver_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id       UUID NOT NULL REFERENCES employees(employee_id),
    licence_number    VARCHAR(30) NOT NULL UNIQUE,
    licence_expiry    DATE NOT NULL
);
