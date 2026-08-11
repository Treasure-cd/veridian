DROP POLICY exec_consent_read ON wallet_accounts;

CREATE POLICY exec_consent_read ON wallet_accounts
    FOR SELECT
    USING (
        (auth.jwt() ->> 'user_role') = 'group_executive'
        AND EXISTS (
            SELECT 1 FROM customers c
            WHERE c.customer_id = wallet_accounts.customer_id
            AND c.consent_financial_visibility = true
        )
    );
