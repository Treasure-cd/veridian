-- Indexes, faster lookups
CREATE INDEX idx_drivers_employee ON drivers(employee_id);

CREATE INDEX idx_routes_origin ON routes(origin_location_id);
CREATE INDEX idx_routes_destination ON routes(destination_location_id);

CREATE INDEX idx_shipments_origin ON shipments(origin_location_id);
CREATE INDEX idx_shipments_destination ON shipments(destination_location_id);
CREATE INDEX idx_shipments_status ON shipments(status);

CREATE INDEX idx_legs_shipment ON shipment_legs(shipment_id);
CREATE INDEX idx_legs_vehicle ON shipment_legs(vehicle_id);
CREATE INDEX idx_legs_driver ON shipment_legs(driver_id);

CREATE INDEX idx_warehouses_location ON warehouses(location_id);

CREATE INDEX idx_maintenance_vehicle ON maintenance_logs(vehicle_id);
CREATE INDEX idx_maintenance_date ON maintenance_logs(service_date);
