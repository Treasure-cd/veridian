CREATE TABLE utility_accounts (
    utility_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id       UUID NOT NULL REFERENCES properties(property_id),
    utility_type       VARCHAR(20) NOT NULL
                      CHECK (utility_type IN ('electricity','water','generator_diesel','internet','waste')),
    provider_name       VARCHAR(100) NOT NULL,
    account_number       VARCHAR(50) NOT NULL
);
