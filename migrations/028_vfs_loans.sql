-- Loans are taken from the bank, this table keeps track of them
CREATE TABLE loans (
    loan_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    borrower_customer_id   UUID REFERENCES customers(customer_id),
    borrower_supplier_id   UUID REFERENCES suppliers_vendors(supplier_id),
    principal_amount        NUMERIC(14,2) NOT NULL CHECK (principal_amount > 0),
    status                   VARCHAR(20) NOT NULL DEFAULT 'active'
                             CHECK (status IN ('active','repaid','defaulted','written_off')),
    CHECK (
        (borrower_customer_id IS NOT NULL AND borrower_supplier_id IS NULL)
        OR (borrower_customer_id IS NULL AND borrower_supplier_id IS NOT NULL)
    )
);
