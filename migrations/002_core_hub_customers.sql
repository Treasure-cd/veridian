-- Customers - single shared Identity for anyone who interacts with Veridian
CREATE TABLE customers (
    customer_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name                  VARCHAR(150) NOT NULL,
    date_of_birth               DATE,
    primary_contact             VARCHAR(50) NOT NULL,
    registered_country          CHAR(2) NOT NULL,
	-- Consent flags
    consent_retail_personalisation   BOOLEAN NOT NULL DEFAULT FALSE,
    consent_financial_visibility     BOOLEAN NOT NULL DEFAULT FALSE,
    created_date                DATE NOT NULL DEFAULT CURRENT_DATE
);