CREATE POLICY authenticated_read ON customers
    FOR SELECT
    USING (auth.jwt() ->> 'user_role' IS NOT NULL);

CREATE POLICY authenticated_read ON employees
    FOR SELECT
    USING (auth.jwt() ->> 'user_role' IS NOT NULL);

CREATE POLICY authenticated_read ON suppliers_vendors
    FOR SELECT
    USING (auth.jwt() ->> 'user_role' IS NOT NULL);

CREATE POLICY authenticated_read ON locations_sites
    FOR SELECT
    USING (auth.jwt() ->> 'user_role' IS NOT NULL);

CREATE POLICY authenticated_read ON product_service_catalogue
    FOR SELECT
    USING (auth.jwt() ->> 'user_role' IS NOT NULL);

CREATE POLICY authenticated_read ON divisions
    FOR SELECT
    USING (auth.jwt() ->> 'user_role' IS NOT NULL);

CREATE POLICY vfs_full_read ON financial_account_references
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY exec_consent_read ON financial_account_references
    FOR SELECT
    USING (
        (auth.jwt() ->> 'user_role') = 'group_executive'
        AND EXISTS (
            SELECT 1 FROM customers c
            WHERE c.customer_id = financial_account_references.customer_id
            AND c.consent_financial_visibility = true
        )
    );
