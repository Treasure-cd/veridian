-- make it so that the jwt tokens have user role embedded into them
CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    claims jsonb;
    user_role_val text;
BEGIN
    SELECT ur.user_role INTO user_role_val
    FROM public.user_roles ur
    WHERE ur.user_id = (event->>'user_id')::uuid;

    claims := event->'claims';

    IF user_role_val IS NOT NULL THEN
        claims := jsonb_set(claims, '{user_role}', to_jsonb(user_role_val));
    END IF;

    event := jsonb_set(event, '{claims}', claims);
    RETURN event;
END;
$$;

-- permission supabase needs to
GRANT EXECUTE ON FUNCTION public.custom_access_token_hook TO supabase_auth_admin;
REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM authenticated, anon, public;
