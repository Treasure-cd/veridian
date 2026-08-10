-- Transaction Line Items: Record of every item that has been sold
CREATE TABLE transaction_line_items (
    line_item_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id   UUID NOT NULL REFERENCES pos_transactions(transaction_id),
    product_id       UUID NOT NULL REFERENCES product_service_catalogue(product_id),
    quantity          NUMERIC(10,2) NOT NULL CHECK (quantity > 0),
    unit_price         NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0)
);