CREATE OR REPLACE VIEW vfs_borrower_supply_history AS
SELECT
    sv.supplier_id,
    sv.legal_name AS farmer_name,
    f.farm_id,
    f.primary_crop,
    COUNT(hb.harvest_id) AS total_harvests_recorded,
    MIN(hb.harvest_date) AS first_harvest_date,
    MAX(hb.harvest_date) AS most_recent_harvest_date,
    ROUND(AVG(hb.volume_kg), 1) AS avg_harvest_volume_kg,
    SUM(hb.volume_kg) AS lifetime_volume_kg
FROM suppliers_vendors sv
JOIN farms f ON f.supplier_id = sv.supplier_id
JOIN harvest_batches hb ON hb.farm_id = f.farm_id
WHERE sv.supplier_type = 'farmer'
GROUP BY sv.supplier_id, sv.legal_name, f.farm_id, f.primary_crop
ORDER BY sv.legal_name;