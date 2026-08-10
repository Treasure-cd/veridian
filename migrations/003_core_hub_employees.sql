-- Employees: single shared identity for group staff
CREATE TABLE employees (
    employee_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name          VARCHAR(150) NOT NULL,
    division_id        SMALLINT NOT NULL REFERENCES divisions(division_id),
    role_title         VARCHAR(100) NOT NULL,
    employment_status  VARCHAR(20) NOT NULL DEFAULT 'active'
                        CHECK (employment_status IN ('active','on_leave','terminated')),
    hire_date          DATE NOT NULL,
    reports_to         UUID REFERENCES employees(employee_id)
);