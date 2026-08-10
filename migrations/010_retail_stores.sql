-- Stores: Store meta-data
CREATE TABLE stores (
    store_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id          UUID NOT NULL REFERENCES locations_sites(location_id),
    store_format         VARCHAR(20) NOT NULL
                          CHECK (store_format IN ('large_format','neighbourhood','online')),
    opening_date          DATE NOT NULL,
    manager_employee_id  UUID REFERENCES employees(employee_id)
);