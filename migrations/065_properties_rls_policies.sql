CREATE POLICY properties_and_exec_read ON tenants
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON tenants
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');

CREATE POLICY properties_and_exec_read ON properties
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON properties
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');

CREATE POLICY properties_and_exec_read ON leases
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON leases
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');

CREATE POLICY properties_and_exec_read ON maintenance_requests
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON maintenance_requests
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');

CREATE POLICY properties_and_exec_read ON property_valuations
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON property_valuations
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');

CREATE POLICY properties_and_exec_read ON utility_accounts
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON utility_accounts
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');

CREATE POLICY properties_and_exec_read ON facility_assets
    FOR SELECT USING ((auth.jwt() ->> 'user_role') IN ('properties_ops','group_executive'));
CREATE POLICY properties_write ON facility_assets
    FOR ALL USING ((auth.jwt() ->> 'user_role') = 'properties_ops')
    WITH CHECK ((auth.jwt() ->> 'user_role') = 'properties_ops');
