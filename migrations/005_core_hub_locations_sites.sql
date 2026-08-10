CREATE TABLE locations_sites (
    location_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_name       VARCHAR(150) NOT NULL,
    site_type       VARCHAR(30) NOT NULL
                    CHECK (site_type IN ('store','warehouse','processing_facility','property','office')),
    address         VARCHAR(255) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    country_code    CHAR(2) NOT NULL,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6)
);