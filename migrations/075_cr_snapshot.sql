CREATE OR REPLACE VIEW group_consolidated_revenue_snapshot AS
SELECT 'Meridian Retail and Consumer' AS division_name,
       'retail_pos_sales' AS revenue_source,
       pt.transaction_date::date AS activity_date,
       SUM(pt.total_amount) AS amount
FROM pos_transactions pt
GROUP BY pt.transaction_date::date

UNION ALL

SELECT 'Veridian Properties' AS division_name,
       'active_lease_rent' AS revenue_source,
       CURRENT_DATE AS activity_date,
       SUM(l.monthly_rent) AS amount
FROM leases l
WHERE l.lease_status = 'active'
GROUP BY CURRENT_DATE

UNION ALL

SELECT d.division_name,
       'vfs_wallet_settlement' AS revenue_source,
       ms.settlement_date AS activity_date,
       SUM(ms.total_amount) AS amount
FROM merchant_settlements ms
JOIN divisions d ON d.division_id = ms.division_id
GROUP BY d.division_name, ms.settlement_date

ORDER BY activity_date DESC;