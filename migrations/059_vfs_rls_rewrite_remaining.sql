-- adjustments made to the other tables
DROP POLICY vfs_full_read ON wallet_transactions;
DROP POLICY exec_consent_read ON wallet_transactions;

CREATE POLICY vfs_full_read ON wallet_transactions
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY exec_consent_read ON wallet_transactions
    FOR SELECT
    USING (
        (auth.jwt() ->> 'user_role') = 'group_executive'
        AND EXISTS (
            SELECT 1 FROM wallet_accounts wa
            JOIN customers c ON c.customer_id = wa.customer_id
            WHERE wa.wallet_id = wallet_transactions.wallet_id
            AND c.consent_financial_visibility = true
        )
    );

-- ── loans ──
DROP POLICY vfs_full_read ON loans;
DROP POLICY exec_consent_read ON loans;

CREATE POLICY vfs_full_read ON loans
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY exec_consent_read ON loans
    FOR SELECT
    USING (
        (auth.jwt() ->> 'user_role') = 'group_executive'
        AND (
            (borrower_customer_id IS NOT NULL AND EXISTS (
                SELECT 1 FROM customers c
                WHERE c.customer_id = loans.borrower_customer_id
                AND c.consent_financial_visibility = true
            ))
            OR (borrower_supplier_id IS NOT NULL)
        )
    );

-- ── loan_repayments ──
DROP POLICY vfs_full_read ON loan_repayments;
DROP POLICY exec_consent_read ON loan_repayments;

CREATE POLICY vfs_full_read ON loan_repayments
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY exec_consent_read ON loan_repayments
    FOR SELECT
    USING (
        (auth.jwt() ->> 'user_role') = 'group_executive'
        AND EXISTS (
            SELECT 1 FROM loans l
            WHERE l.loan_id = loan_repayments.loan_id
            AND (
                (l.borrower_customer_id IS NOT NULL AND EXISTS (
                    SELECT 1 FROM customers c
                    WHERE c.customer_id = l.borrower_customer_id
                    AND c.consent_financial_visibility = true
                ))
                OR (l.borrower_supplier_id IS NOT NULL)
            )
        )
    );

-- ── kyc_records ── (financial_services ONLY, no executive access at all)
DROP POLICY vfs_only_read ON kyc_records;

CREATE POLICY vfs_only_read ON kyc_records
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');

-- ── merchant_settlements ── (division-level, no consent gating needed)
DROP POLICY vfs_full_read ON merchant_settlements;
DROP POLICY exec_read ON merchant_settlements;

CREATE POLICY vfs_full_read ON merchant_settlements
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY exec_read ON merchant_settlements
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') = 'group_executive');

-- ── write policies, all six tables: financial_services only ──
DROP POLICY vfs_write ON wallet_accounts;
DROP POLICY vfs_write ON wallet_transactions;
DROP POLICY vfs_write ON loans;
DROP POLICY vfs_write ON loan_repayments;
DROP POLICY vfs_write ON kyc_records;
DROP POLICY vfs_write ON merchant_settlements;

CREATE POLICY vfs_write ON wallet_accounts
    FOR INSERT, UPDATE, DELETE
    USING ((auth.jwt() ->> 'user_role') = 'financial_services')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY vfs_write ON wallet_transactions
    FOR INSERT, UPDATE, DELETE
    USING ((auth.jwt() ->> 'user_role') = 'financial_services')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY vfs_write ON loans
    FOR INSERT, UPDATE, DELETE
    USING ((auth.jwt() ->> 'user_role') = 'financial_services')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY vfs_write ON loan_repayments
    FOR INSERT, UPDATE, DELETE
    USING ((auth.jwt() ->> 'user_role') = 'financial_services')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY vfs_write ON kyc_records
    FOR INSERT, UPDATE, DELETE
    USING ((auth.jwt() ->> 'user_role') = 'financial_services')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'financial_services');

CREATE POLICY vfs_write ON merchant_settlements
    FOR INSERT, UPDATE, DELETE
    USING ((auth.jwt() ->> 'user_role') = 'financial_services')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'financial_services');
