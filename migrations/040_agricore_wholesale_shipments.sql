-- Wholesale shipments
CREATE TABLE wholesale_shipments (
    wholesale_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID NOT NULL REFERENCES processing_runs(run_id),
    destination_type    VARCHAR(20) NOT NULL
                        CHECK (destination_type IN ('meridian_retail','external_client')),
    destination_id      UUID NOT NULL, 
    shipment_id          UUID REFERENCES shipments(shipment_id)
);
