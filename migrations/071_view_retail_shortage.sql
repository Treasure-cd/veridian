CREATE OR REPLACE VIEW retail_supply_shortage_signal AS
WITH farm_avg_volume AS (
    SELECT farm_id, product_id, AVG(volume_kg) AS avg_volume_kg
    FROM harvest_batches
    GROUP BY farm_id, product_id
)
SELECT
    ws.wholesale_id,
    ws.destination_store_id,
    st.store_id,
    sv.legal_name AS supplier_name,
    hb.harvest_id,
    hb.harvest_date,
    hb.volume_kg AS harvest_volume_kg,
    fav.avg_volume_kg AS historical_avg_volume_kg,
    ROUND(hb.volume_kg / NULLIF(fav.avg_volume_kg, 0) * 100, 1) AS pct_of_average,
    sh.status AS shipment_status,
    CASE
        WHEN hb.volume_kg / NULLIF(fav.avg_volume_kg, 0) < 0.60 THEN 'high_risk_shortfall'
        WHEN hb.volume_kg / NULLIF(fav.avg_volume_kg, 0) < 0.85 THEN 'moderate_risk_shortfall'
        ELSE 'normal'
    END AS shortage_signal
FROM wholesale_shipments ws
JOIN processing_runs pr ON pr.run_id = ws.run_id
JOIN harvest_batches hb ON hb.harvest_id = pr.harvest_id
JOIN farms f ON f.farm_id = hb.farm_id
JOIN suppliers_vendors sv ON sv.supplier_id = f.supplier_id
JOIN farm_avg_volume fav ON fav.farm_id = hb.farm_id AND fav.product_id = hb.product_id
LEFT JOIN stores st ON st.store_id = ws.destination_store_id
LEFT JOIN shipments sh ON sh.shipment_id = ws.shipment_id
WHERE ws.destination_type = 'meridian_retail'
ORDER BY pct_of_average ASC NULLS LAST;