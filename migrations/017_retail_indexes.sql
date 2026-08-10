-- INdexes for fast looksup
CREATE INDEX idx_stores_location ON stores(location_id);
CREATE INDEX idx_stores_manager ON stores(manager_employee_id);

CREATE INDEX idx_pos_txn_store ON pos_transactions(store_id);
CREATE INDEX idx_pos_txn_customer ON pos_transactions(customer_id);
CREATE INDEX idx_pos_txn_date ON pos_transactions(transaction_date);

CREATE INDEX idx_line_items_transaction ON transaction_line_items(transaction_id);
CREATE INDEX idx_line_items_product ON transaction_line_items(product_id);

CREATE INDEX idx_stock_store ON inventory_stock_levels(store_id);
CREATE INDEX idx_stock_product ON inventory_stock_levels(product_id);

CREATE INDEX idx_promotions_product ON promotions(product_id);
CREATE INDEX idx_promotions_dates ON promotions(start_date, end_date);

CREATE INDEX idx_loyalty_customer ON loyalty_accounts(customer_id);

CREATE INDEX idx_deliveries_supplier ON supplier_deliveries(supplier_id);
CREATE INDEX idx_deliveries_store ON supplier_deliveries(store_id);
CREATE INDEX idx_deliveries_status ON supplier_deliveries(status);