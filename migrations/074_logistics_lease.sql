CREATE OR REPLACE VIEW logistics_warehouse_lease_status AS
SELECT
    w.warehouse_id,
    w.capacity_units,
    p.property_id,
    l.lease_id,
    l.lease_status,
    t.tenant_type,
    t.division_id,
    l.start_date,
    l.end_date
FROM warehouses w
JOIN properties p ON p.property_id = w.leased_from_property_id
LEFT JOIN leases l ON l.property_id = p.property_id AND l.lease_status = 'active'
LEFT JOIN tenants t ON t.tenant_id = l.tenant_id
ORDER BY w.warehouse_id;