-- creating a user roles table
CREATE TABLE user_roles (
    user_id    UUID PRIMARY KEY REFERENCES auth.users(id),
    user_role  VARCHAR(30) NOT NULL
               CHECK (user_role IN ('retail_ops','logistics_ops','agricore_ops',
                                     'properties_ops','financial_services','group_executive'))
);
