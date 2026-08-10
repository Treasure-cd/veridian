-- Quality grade for rach processing run
CREATE TABLE quality_grades (
    grade_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id                 UUID NOT NULL REFERENCES processing_runs(run_id),
    grade_level             VARCHAR(10) NOT NULL
                            CHECK (grade_level IN ('A','B','C','reject')),
    moisture_content         NUMERIC(5,2) CHECK (moisture_content >= 0 AND moisture_content <= 100),
    inspector_employee_id   UUID NOT NULL REFERENCES employees(employee_id)
);
