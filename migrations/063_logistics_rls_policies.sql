-- Standard: logistics_ops + group_executive read, logistics_ops writes
CREATE POLICY logistics_and_exec_read ON vehicles
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','group_executive'));
CREATE POLICY logistics_write ON vehicles
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');

CREATE POLICY logistics_and_exec_read ON drivers
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','group_executive'));
CREATE POLICY logistics_write ON drivers
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');

CREATE POLICY logistics_and_exec_read ON routes
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','group_executive'));
CREATE POLICY logistics_write ON routes
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');

CREATE POLICY logistics_and_exec_read ON shipments
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','group_executive'));
CREATE POLICY logistics_write ON shipments
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');

CREATE POLICY logistics_and_exec_read ON shipment_legs
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','group_executive'));
CREATE POLICY logistics_write ON shipment_legs
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');

CREATE POLICY logistics_and_exec_read ON maintenance_logs
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','group_executive'));
CREATE POLICY logistics_write ON maintenance_logs
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');

-- NON-STANDARD: warehouses — also readable by properties_ops (per access matrix,
-- since warehouses lease from Properties and Funmi's scenario needs cross-visibility)
CREATE POLICY logistics_props_exec_read ON warehouses
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('logistics_ops','properties_ops','group_executive'));
CREATE POLICY logistics_write ON warehouses
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'logistics_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'logistics_ops');
