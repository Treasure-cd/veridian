CREATE INDEX idx_tenants_division ON tenants(division_id);

CREATE INDEX idx_properties_location ON properties(location_id);
CREATE INDEX idx_properties_type ON properties(property_type);

CREATE INDEX idx_leases_property ON leases(property_id);
CREATE INDEX idx_leases_tenant ON leases(tenant_id);
CREATE INDEX idx_leases_dates ON leases(start_date, end_date);

CREATE INDEX idx_maint_req_property ON maintenance_requests(property_id);
CREATE INDEX idx_maint_req_status ON maintenance_requests(status);

CREATE INDEX idx_valuations_property ON property_valuations(property_id);

CREATE INDEX idx_utility_property ON utility_accounts(property_id);

CREATE INDEX idx_assets_property ON facility_assets(property_id);
