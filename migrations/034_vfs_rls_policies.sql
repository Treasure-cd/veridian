-- To enable RLS on each of the tables
ALTER TABLE wallet_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE loans ENABLE ROW LEVEL SECURITY;
ALTER TABLE loan_repayments ENABLE ROW LEVEL SECURITY;
ALTER TABLE kyc_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE merchant_settlements ENABLE ROW LEVEL SECURITY;

-- ── wallet_accounts ──
CREATE POLICY vfs_full_read ON wallet_accounts
    FOR SELECT TO financial_services USING (true);
CREATE POLICY exec_consent_read ON wallet_accounts
    FOR SELECT TO group_executive
    USING (
        EXISTS (
            SELECT 1 FROM customers c
            WHERE c.customer_id = wallet_accounts.customer_id
            AND c.consent_financial_visibility = true
        )
    );

-- ── wallet_transactions ──
CREATE POLICY vfs_full_read ON wallet_transactions
    FOR SELECT TO financial_services USING (true);

CREATE POLICY exec_consent_read ON wallet_transactions
    FOR SELECT TO group_executive
    USING (
        EXISTS (
            SELECT 1 FROM wallet_accounts wa
            JOIN customers c ON c.customer_id = wa.customer_id
            WHERE wa.wallet_id = wallet_transactions.wallet_id
            AND c.consent_financial_visibility = true
        )
    );

-- ── loans ──
CREATE POLICY vfs_full_read ON loans
    FOR SELECT TO financial_services USING (true);

CREATE POLICY exec_consent_read ON loans
    FOR SELECT TO group_executive
    USING (
        -- consumer borrower: check customer consent
        (borrower_customer_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM customers c
            WHERE c.customer_id = loans.borrower_customer_id
            AND c.consent_financial_visibility = true
        ))
        OR
        (borrower_supplier_id IS NOT NULL)
    );

-- ── loan_repayments ──
CREATE POLICY vfs_full_read ON loan_repayments
    FOR SELECT TO financial_services USING (true);

CREATE POLICY exec_consent_read ON loan_repayments
    FOR SELECT TO group_executive
    USING (
        EXISTS (
            SELECT 1 FROM loans l
            WHERE l.loan_id = loan_repayments.loan_id
        )
    );

-- ── kyc_records ──
CREATE POLICY vfs_only_read ON kyc_records
    FOR SELECT TO financial_services USING (true);

-- ── merchant_settlements ──
CREATE POLICY vfs_full_read ON merchant_settlements
    FOR SELECT TO financial_services USING (true);

CREATE POLICY exec_read ON merchant_settlements
    FOR SELECT TO group_executive USING (true);

-- Only financial_services can write to any VFS table
CREATE POLICY vfs_write ON wallet_accounts FOR ALL TO financial_services USING (true) WITH CHECK (true);
CREATE POLICY vfs_write ON wallet_transactions FOR ALL TO financial_services USING (true) WITH CHECK (true);
CREATE POLICY vfs_write ON loans FOR ALL TO financial_services USING (true) WITH CHECK (true);
CREATE POLICY vfs_write ON loan_repayments FOR ALL TO financial_services USING (true) WITH CHECK (true);
CREATE POLICY vfs_write ON kyc_records FOR ALL TO financial_services USING (true) WITH CHECK (true);
CREATE POLICY vfs_write ON merchant_settlements FOR ALL TO financial_services USING (true) WITH CHECK (true);
