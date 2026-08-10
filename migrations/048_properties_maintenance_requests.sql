CREATE TABLE maintenance_requests (
    request_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id      UUID NOT NULL REFERENCES properties(property_id),
    requested_date    DATE NOT NULL,
    category           VARCHAR(30) NOT NULL
                      CHECK (category IN ('electrical','plumbing','structural','hvac','security','other')),
    status              VARCHAR(20) NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open','in_progress','resolved','cancelled')),
    resolved_date      DATE
);
