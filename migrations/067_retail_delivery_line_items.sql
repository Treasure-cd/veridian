-- delivery line items
CREATE TABLE delivery_line_items (
    delivery_line_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id       UUID NOT NULL REFERENCES supplier_deliveries(delivery_id),
    product_id        UUID NOT NULL REFERENCES product_service_catalogue(product_id),
    quantity           NUMERIC(10,2) NOT NULL CHECK (quantity > 0)
);

CREATE INDEX idx_delivery_line_items_delivery ON delivery_line_items(delivery_id);
CREATE INDEX idx_delivery_line_items_product ON delivery_line_items(product_id);
