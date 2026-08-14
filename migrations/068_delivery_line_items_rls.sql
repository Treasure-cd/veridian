-- rls for newly added stuff
CREATE POLICY retail_and_exec_read ON delivery_line_items
    FOR SELECT
    USING ( (auth.jwt() ->> 'user_role') IN ('retail_ops','group_executive') );

CREATE POLICY retail_write ON delivery_line_items
    FOR ALL
    USING ( (auth.jwt() ->> 'user_role') = 'retail_ops' )
    WITH CHECK ( (auth.jwt() ->> 'user_role') = 'retail_ops' );
