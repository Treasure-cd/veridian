-- Customer KYC details
CREATE TABLE kyc_records (
    kyc_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id           UUID NOT NULL REFERENCES customers(customer_id),
    verification_level    VARCHAR(20) NOT NULL
                          CHECK (verification_level IN ('tier1','tier2','tier3')),
    verified_date          DATE NOT NULL
);
