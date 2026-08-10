CREATE TABLE facility_assets (
    asset_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id        UUID NOT NULL REFERENCES properties(property_id),
    asset_type          VARCHAR(50) NOT NULL,  -- free text: generator, cold storage unit, forklift, etc.
    installed_date        DATE NOT NULL,
    condition_rating       VARCHAR(20) NOT NULL DEFAULT 'good'
                          CHECK (condition_rating IN ('excellent','good','fair','poor'))
);
