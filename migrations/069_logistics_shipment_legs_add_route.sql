ALTER TABLE shipment_legs
    ADD COLUMN route_id UUID REFERENCES routes(route_id);

CREATE INDEX idx_shipment_legs_route ON shipment_legs(route_id);