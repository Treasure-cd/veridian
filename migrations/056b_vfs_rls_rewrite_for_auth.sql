DROP POLICY vfs_full_read ON wallet_accounts;
CREATE POLICY vfs_full_read ON wallet_accounts
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');
