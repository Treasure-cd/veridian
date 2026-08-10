-- Loyalty Accounts - custimers who have loyalty accounts
CREATE TABLE loyalty_accounts (
    loyalty_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id       UUID NOT NULL REFERENCES customers(customer_id),
    tier               VARCHAR(20) NOT NULL DEFAULT 'bronze'
                       CHECK (tier IN ('bronze','silver','gold','platinum')),
    points_balance     INTEGER NOT NULL DEFAULT 0 CHECK (points_balance >= 0),
    enrolment_date      DATE NOT NULL DEFAULT CURRENT_DATE
);