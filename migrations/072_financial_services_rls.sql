CREATE POLICY "financial_services_read_farms" ON farms
FOR SELECT TO authenticated
USING (auth.jwt() ->> 'user_role' = 'financial_services');

CREATE POLICY "financial_services_read_harvest_batches" ON harvest_batches
FOR SELECT TO authenticated
USING (auth.jwt() ->> 'user_role' = 'financial_services');