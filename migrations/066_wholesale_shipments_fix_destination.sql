-- migrations/066_wholesale_shipments_fix_destination.sql

ALTER TABLE wholesale_shipments
    DROP COLUMN destination_id;

ALTER TABLE wholesale_shipments
    ADD COLUMN destination_store_id      UUID REFERENCES stores(store_id),
    ADD COLUMN destination_external_name VARCHAR(150);

ALTER TABLE wholesale_shipments
    ADD CONSTRAINT chk_destination_exclusive CHECK (
        (destination_type = 'meridian_retail' AND destination_store_id IS NOT NULL AND destination_external_name IS NULL)
        OR
        (destination_type = 'external_client' AND destination_store_id IS NULL AND destination_external_name IS NOT NULL)
    );

CREATE INDEX idx_wholesale_destination_store ON wholesale_shipments(destination_store_id);
