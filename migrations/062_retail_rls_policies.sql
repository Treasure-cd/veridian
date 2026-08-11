-- migrations/062_retail_rls_policies.sql

CREATE POLICY retail_and_exec_read ON stores
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

CREATE POLICY retail_and_exec_read ON pos_transactions
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

CREATE POLICY retail_and_exec_read ON transaction_line_items
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

CREATE POLICY retail_and_exec_read ON inventory_stock_levels
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

CREATE POLICY retail_and_exec_read ON promotions
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

CREATE POLICY retail_and_exec_read ON loyalty_accounts
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

CREATE POLICY retail_and_exec_read ON supplier_deliveries
    FOR SELECT
    USING ((auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive'));

-- Write access: retail_ops only
CREATE POLICY retail_write ON stores
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');

CREATE POLICY retail_write ON pos_transactions
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');

CREATE POLICY retail_write ON transaction_line_items
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');

CREATE POLICY retail_write ON inventory_stock_levels
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');

CREATE POLICY retail_write ON promotions
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');

CREATE POLICY retail_write ON loyalty_accounts
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');

CREATE POLICY retail_write ON supplier_deliveries
    FOR ALL
    USING ((auth.jwt() ->> 'user_role') = 'retail_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'retail_ops');
