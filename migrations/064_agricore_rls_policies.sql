CREATE POLICY agricore_and_exec_read ON farms
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','group_executive'));
CREATE POLICY agricore_write ON farms
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

CREATE POLICY agricore_and_exec_read ON farmers
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','group_executive'));
CREATE POLICY agricore_write ON farmers
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

CREATE POLICY agricore_and_exec_read ON harvest_batches
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','group_executive'));
CREATE POLICY agricore_write ON harvest_batches
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

CREATE POLICY agricore_and_exec_read ON processing_runs
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','group_executive'));
CREATE POLICY agricore_write ON processing_runs
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

CREATE POLICY agricore_and_exec_read ON quality_grades
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','group_executive'));
CREATE POLICY agricore_write ON quality_grades
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

CREATE POLICY agricore_and_exec_read ON harvest_payments
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','group_executive'));
CREATE POLICY agricore_write ON harvest_payments
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

-- NON-STANDARD: wholesale_shipments — also readable by logistics_ops
-- (goods physically hand off to Concord Logistics for delivery)
CREATE POLICY agricore_logistics_exec_read ON wholesale_shipments
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','logistics_ops','group_executive'));
CREATE POLICY agricore_write ON wholesale_shipments
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');

-- NON-STANDARD: farmer_loans_reference — also readable by financial_services
-- (VFS-derived summary data, per section 4.4)
CREATE POLICY agricore_vfs_exec_read ON farmer_loans_reference
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('agricore_ops','financial_services','group_executive'));
CREATE POLICY agricore_write ON farmer_loans_reference
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'agricore_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'agricore_ops');
