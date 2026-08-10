-- migrations/042_agricore_indexes.sql
CREATE INDEX idx_farms_supplier ON farms(supplier_id);
CREATE INDEX idx_farms_location ON farms(location_id);

CREATE INDEX idx_farmers_supplier ON farmers(supplier_id);

CREATE INDEX idx_harvest_farm ON harvest_batches(farm_id);
CREATE INDEX idx_harvest_product ON harvest_batches(product_id);
CREATE INDEX idx_harvest_agent ON harvest_batches(field_agent_employee_id);
CREATE INDEX idx_harvest_date ON harvest_batches(harvest_date);

CREATE INDEX idx_runs_harvest ON processing_runs(harvest_id);
CREATE INDEX idx_runs_facility ON processing_runs(facility_location_id);

CREATE INDEX idx_grades_run ON quality_grades(run_id);
CREATE INDEX idx_grades_inspector ON quality_grades(inspector_employee_id);

CREATE INDEX idx_wholesale_run ON wholesale_shipments(run_id);
CREATE INDEX idx_wholesale_shipment ON wholesale_shipments(shipment_id);

CREATE INDEX idx_farmer_loans_farmer ON farmer_loans_reference(farmer_id);
CREATE INDEX idx_farmer_loans_loan ON farmer_loans_reference(loan_id);
