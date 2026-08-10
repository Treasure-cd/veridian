-- At this moment, how many of this product do we have
CREATE TABLE inventory_stock_levels (
    stock_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id            UUID NOT NULL REFERENCES stores(store_id),
    product_id          UUID NOT NULL REFERENCES product_service_catalogue(product_id),
    quantity_on_hand    NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (quantity_on_hand >= 0),
    last_counted_date   DATE,
    UNIQUE (store_id, product_id)
);