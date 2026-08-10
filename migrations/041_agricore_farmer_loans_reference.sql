-- Reference that makes a peek into what a farmer's loan history looks like
CREATE TABLE farmer_loans_reference (
    reference_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farmer_id                UUID NOT NULL REFERENCES farmers(farmer_id),
    loan_id                  UUID NOT NULL REFERENCES loans(loan_id),
    visible_summary_status    VARCHAR(20) NOT NULL
                              CHECK (visible_summary_status IN ('current','overdue','closed'))
);
