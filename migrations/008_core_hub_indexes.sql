-- Indexes on columns that can be FKed
CREATE INDEX idx_employees_division ON employees(division_id);
CREATE INDEX idx_employees_reports_to ON employees(reports_to);
CREATE INDEX idx_suppliers_division ON suppliers_vendors(primary_division_id);
CREATE INDEX idx_products_division ON product_service_catalogue(primary_division_id);
CREATE INDEX idx_account_refs_customer ON financial_account_references(customer_id);
CREATE INDEX idx_customers_country ON customers(registered_country);
CREATE INDEX idx_customers_contact ON customers(primary_contact);
CREATE INDEX idx_locations_city_country ON locations_sites(city, country_code);
CREATE INDEX idx_locations_site_type ON locations_sites(site_type);
CREATE INDEX idx_products_category ON product_service_catalogue(category);
CREATE INDEX idx_suppliers_status ON suppliers_vendors(status);