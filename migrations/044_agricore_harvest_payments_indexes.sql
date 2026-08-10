-- Indices for harvest payments
CREATE INDEX idx_harvest_payments_harvest ON harvest_payments(harvest_id);
CREATE INDEX idx_harvest_payments_status ON harvest_payments(status);
CREATE INDEX idx_harvest_payments_date ON harvest_payments(payment_date);
