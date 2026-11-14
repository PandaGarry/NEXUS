-- Test-only PostgreSQL 18.7 HEGC guard qualification fixture.
-- This is deliberately isolated from production schemas and credentials.
BEGIN;

CREATE ROLE nexus_guard_owner NOLOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS;
CREATE ROLE nexus_hegc_owner  NOLOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS;
CREATE ROLE nexus_writer_owner NOLOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS;
CREATE ROLE nexus_hegc LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS PASSWORD 'hegc-test-only';
CREATE ROLE nexus_writer LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS PASSWORD 'writer-test-only';
CREATE ROLE nexus_membership_admin LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS PASSWORD 'membership-test-only';

CREATE SCHEMA nexus_control;
CREATE SCHEMA nexus_source;
CREATE SCHEMA nexus_hegc;

REVOKE ALL ON SCHEMA nexus_control, nexus_source, nexus_hegc FROM PUBLIC;
GRANT USAGE ON SCHEMA nexus_control TO nexus_guard_owner, nexus_hegc_owner, nexus_writer_owner, nexus_hegc, nexus_writer, nexus_membership_admin;
GRANT USAGE ON SCHEMA nexus_source TO nexus_hegc_owner, nexus_writer_owner, nexus_writer;
GRANT USAGE ON SCHEMA nexus_hegc TO nexus_hegc_owner, nexus_hegc;

CREATE TABLE nexus_control.scope_membership (
    account_id uuid NOT NULL,
    scope_id uuid NOT NULL,
    active boolean NOT NULL DEFAULT true,
    PRIMARY KEY (account_id, scope_id)
);
CREATE TABLE nexus_control.service_principal (
    principal name NOT NULL,
    service_kind text NOT NULL CHECK (service_kind IN ('hegc', 'writer', 'membership_admin')),
    account_id uuid NOT NULL,
    PRIMARY KEY (principal, account_id, service_kind)
);
CREATE TABLE nexus_control.scope_guard (
    account_id uuid NOT NULL,
    scope_id uuid NOT NULL,
    generation bigint NOT NULL DEFAULT 0 CHECK (generation >= 0),
    PRIMARY KEY (account_id, scope_id)
);
CREATE TABLE nexus_source.exposure (
    account_id uuid NOT NULL,
    scope_id uuid NOT NULL,
    exposure_units bigint NOT NULL,
    PRIMARY KEY (account_id, scope_id)
);
CREATE TABLE nexus_hegc.egress_grant (
    attempt_id uuid PRIMARY KEY,
    grant_id uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    account_id uuid NOT NULL,
    binding_digest text NOT NULL,
    scope_ids uuid[] NOT NULL,
    snapshot_total bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

ALTER TABLE nexus_control.scope_membership OWNER TO nexus_guard_owner;
ALTER TABLE nexus_control.service_principal OWNER TO nexus_guard_owner;
ALTER TABLE nexus_control.scope_guard OWNER TO nexus_guard_owner;
ALTER TABLE nexus_source.exposure OWNER TO nexus_writer_owner;
ALTER TABLE nexus_hegc.egress_grant OWNER TO nexus_hegc_owner;

GRANT SELECT ON nexus_control.scope_membership, nexus_control.service_principal TO nexus_guard_owner;
GRANT SELECT, UPDATE ON nexus_control.scope_guard TO nexus_guard_owner;
GRANT SELECT ON nexus_control.scope_membership, nexus_control.service_principal TO nexus_hegc_owner, nexus_writer_owner;
GRANT SELECT ON nexus_source.exposure TO nexus_hegc_owner;
GRANT UPDATE ON nexus_source.exposure TO nexus_writer_owner;
GRANT SELECT, INSERT ON nexus_hegc.egress_grant TO nexus_hegc_owner;

-- Force RLS even for the source-table owner (writer definer).
ALTER TABLE nexus_source.exposure ENABLE ROW LEVEL SECURITY;
ALTER TABLE nexus_source.exposure FORCE ROW LEVEL SECURITY;
CREATE POLICY exposure_hegc_read ON nexus_source.exposure
    FOR SELECT TO nexus_hegc_owner
    USING (EXISTS (
        SELECT 1 FROM nexus_control.service_principal sp
         WHERE sp.principal = session_user AND sp.account_id = exposure.account_id
           AND sp.service_kind = 'hegc'
    ));
CREATE POLICY exposure_writer_read ON nexus_source.exposure
    FOR SELECT TO nexus_writer_owner
    USING (EXISTS (
        SELECT 1 FROM nexus_control.service_principal sp
         WHERE sp.principal = session_user AND sp.account_id = exposure.account_id
           AND sp.service_kind = 'writer'
    ));
CREATE POLICY exposure_writer_update ON nexus_source.exposure
    FOR UPDATE TO nexus_writer_owner
    USING (EXISTS (
        SELECT 1 FROM nexus_control.service_principal sp
         WHERE sp.principal = session_user AND sp.account_id = exposure.account_id
           AND sp.service_kind = 'writer'
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM nexus_control.service_principal sp
         WHERE sp.principal = session_user AND sp.account_id = exposure.account_id
           AND sp.service_kind = 'writer'
    ));

CREATE FUNCTION nexus_control.acquire_scope_guards(p_account uuid, p_scope_ids uuid[])
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_control, pg_temp
AS $function$
DECLARE
    v_expected uuid[];
    v_scope uuid;
    v_rows integer;
BEGIN
    IF p_scope_ids IS NULL
       OR cardinality(p_scope_ids) < 1
       OR cardinality(p_scope_ids) > 16
       OR array_position(p_scope_ids, NULL::uuid) IS NOT NULL
       OR cardinality(p_scope_ids) <> (
            SELECT count(DISTINCT x) FROM unnest(p_scope_ids) AS u(x)
       ) THEN
        RAISE EXCEPTION 'invalid or unbounded scope set' USING ERRCODE = '22023';
    END IF;

    -- Root/account guard is always acquired before deriving and locking children.
    UPDATE nexus_control.scope_guard g
       SET generation = generation + 1
     WHERE g.account_id = p_account
       AND g.scope_id = p_account
       AND EXISTS (
            SELECT 1
              FROM nexus_control.service_principal sp
             WHERE sp.principal = session_user
               AND sp.account_id = p_account
               AND sp.service_kind IN ('hegc', 'writer', 'membership_admin')
       );
    GET DIAGNOSTICS v_rows = ROW_COUNT;
    IF v_rows <> 1 THEN
        RAISE EXCEPTION 'unauthorized caller or missing root guard' USING ERRCODE = '42501';
    END IF;

    SELECT array_agg(sm.scope_id ORDER BY (sm.scope_id = p_account) DESC, uuid_send(sm.scope_id))
      INTO v_expected
      FROM nexus_control.scope_membership sm
     WHERE sm.account_id = p_account
       AND sm.active;

    IF v_expected IS NULL OR p_scope_ids IS DISTINCT FROM v_expected THEN
        RAISE EXCEPTION 'scope set is incomplete, stale, or non-canonical' USING ERRCODE = '22023';
    END IF;

    FOR v_scope IN
        SELECT x.scope_id
          FROM unnest(v_expected) AS x(scope_id)
         WHERE x.scope_id <> p_account
         ORDER BY uuid_send(x.scope_id)
    LOOP
        UPDATE nexus_control.scope_guard
           SET generation = generation + 1
         WHERE account_id = p_account
           AND scope_id = v_scope;
        GET DIAGNOSTICS v_rows = ROW_COUNT;
        IF v_rows <> 1 THEN
            RAISE EXCEPTION 'missing child guard' USING ERRCODE = '55000';
        END IF;
    END LOOP;
END
$function$;
ALTER FUNCTION nexus_control.acquire_scope_guards(uuid, uuid[]) OWNER TO nexus_guard_owner;
REVOKE ALL ON FUNCTION nexus_control.acquire_scope_guards(uuid, uuid[]) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_control.acquire_scope_guards(uuid, uuid[]) TO nexus_hegc_owner, nexus_writer_owner;

CREATE FUNCTION nexus_hegc.issue_egress_grant(
    p_account uuid,
    p_scope_ids uuid[],
    p_attempt_id uuid,
    p_binding_digest text
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_hegc, nexus_control, nexus_source, pg_temp
AS $function$
DECLARE
    v_existing nexus_hegc.egress_grant%ROWTYPE;
    v_grant_id uuid;
    v_total bigint;
BEGIN
    -- First protected operation in this entrypoint: common guard acquisition.
    PERFORM nexus_control.acquire_scope_guards(p_account, p_scope_ids);

    SELECT * INTO v_existing
      FROM nexus_hegc.egress_grant
     WHERE attempt_id = p_attempt_id;
    IF FOUND THEN
        IF v_existing.account_id <> p_account
           OR v_existing.binding_digest <> p_binding_digest
           OR v_existing.scope_ids IS DISTINCT FROM p_scope_ids THEN
            RAISE EXCEPTION 'attempt identity reused with changed binding' USING ERRCODE = '23505';
        END IF;
        RETURN v_existing.grant_id;
    END IF;

    SELECT COALESCE(sum(e.exposure_units), 0)
      INTO v_total
      FROM nexus_source.exposure e
     WHERE e.account_id = p_account
       AND e.scope_id = ANY (p_scope_ids);

    INSERT INTO nexus_hegc.egress_grant (
        attempt_id, account_id, binding_digest, scope_ids, snapshot_total
    ) VALUES (
        p_attempt_id, p_account, p_binding_digest, p_scope_ids, v_total
    )
    RETURNING grant_id INTO v_grant_id;

    RETURN v_grant_id;
END
$function$;
ALTER FUNCTION nexus_hegc.issue_egress_grant(uuid, uuid[], uuid, text) OWNER TO nexus_hegc_owner;
REVOKE ALL ON FUNCTION nexus_hegc.issue_egress_grant(uuid, uuid[], uuid, text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_hegc.issue_egress_grant(uuid, uuid[], uuid, text) TO nexus_hegc;

CREATE FUNCTION nexus_source.apply_exposure(p_account uuid, p_scope_ids uuid[], p_delta bigint)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_source, nexus_control, pg_temp
AS $function$
DECLARE
    v_rows integer;
BEGIN
    -- First protected operation in this entrypoint: common guard acquisition.
    PERFORM nexus_control.acquire_scope_guards(p_account, p_scope_ids);

    UPDATE nexus_source.exposure
       SET exposure_units = exposure_units + p_delta
     WHERE account_id = p_account
       AND scope_id = ANY (p_scope_ids);
    GET DIAGNOSTICS v_rows = ROW_COUNT;
    IF v_rows <> cardinality(p_scope_ids) THEN
        RAISE EXCEPTION 'source scope set does not match guarded scope set' USING ERRCODE = '55000';
    END IF;
END
$function$;
ALTER FUNCTION nexus_source.apply_exposure(uuid, uuid[], bigint) OWNER TO nexus_writer_owner;
REVOKE ALL ON FUNCTION nexus_source.apply_exposure(uuid, uuid[], bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_source.apply_exposure(uuid, uuid[], bigint) TO nexus_writer;

-- Scope membership changes use the same root-first serialization boundary.
CREATE FUNCTION nexus_control.set_scope_active(
    p_account uuid,
    p_current_scope_ids uuid[],
    p_target_scope uuid,
    p_active boolean
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_control, pg_temp
AS $function$
DECLARE
    v_rows integer;
BEGIN
    IF p_target_scope IS NULL OR p_target_scope = p_account OR p_active IS NULL THEN
        RAISE EXCEPTION 'invalid scope membership change' USING ERRCODE = '22023';
    END IF;

    PERFORM nexus_control.acquire_scope_guards(p_account, p_current_scope_ids);

    IF p_active THEN
        INSERT INTO nexus_control.scope_guard(account_id, scope_id, generation)
        VALUES (p_account, p_target_scope, 0)
        ON CONFLICT (account_id, scope_id) DO NOTHING;

        INSERT INTO nexus_control.scope_membership(account_id, scope_id, active)
        VALUES (p_account, p_target_scope, true)
        ON CONFLICT (account_id, scope_id)
        DO UPDATE SET active = true;
    ELSE
        UPDATE nexus_control.scope_membership
           SET active = false
         WHERE account_id = p_account
           AND scope_id = p_target_scope
           AND active;
        GET DIAGNOSTICS v_rows = ROW_COUNT;
        IF v_rows <> 1 THEN
            RAISE EXCEPTION 'target scope is not currently active' USING ERRCODE = '22023';
        END IF;
    END IF;
END
$function$;
ALTER FUNCTION nexus_control.set_scope_active(uuid, uuid[], uuid, boolean) OWNER TO nexus_guard_owner;
REVOKE ALL ON FUNCTION nexus_control.set_scope_active(uuid, uuid[], uuid, boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_control.set_scope_active(uuid, uuid[], uuid, boolean) TO nexus_membership_admin;

CREATE FUNCTION nexus_control.set_service_principal(
    p_account uuid,
    p_current_scope_ids uuid[],
    p_principal name,
    p_service_kind text,
    p_enabled boolean
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_control, pg_temp
AS $function$
DECLARE
    v_rows integer;
BEGIN
    IF p_principal IS NULL
       OR p_principal = session_user
       OR p_service_kind NOT IN ('hegc', 'writer')
       OR p_enabled IS NULL THEN
        RAISE EXCEPTION 'invalid service-principal mutation' USING ERRCODE = '22023';
    END IF;

    -- Authorization-map mutations share the same account root guard as gate
    -- and source writes, so a stale transaction cannot use revoked authority.
    PERFORM nexus_control.acquire_scope_guards(p_account, p_current_scope_ids);

    IF p_enabled THEN
        INSERT INTO nexus_control.service_principal(principal, service_kind, account_id)
        VALUES (p_principal, p_service_kind, p_account)
        ON CONFLICT (principal, account_id, service_kind) DO NOTHING;
    ELSE
        DELETE FROM nexus_control.service_principal
         WHERE principal = p_principal
           AND service_kind = p_service_kind
           AND account_id = p_account;
        GET DIAGNOSTICS v_rows = ROW_COUNT;
        IF v_rows <> 1 THEN
            RAISE EXCEPTION 'service principal is not active' USING ERRCODE = '22023';
        END IF;
    END IF;
END
$function$;
ALTER FUNCTION nexus_control.set_service_principal(uuid, uuid[], name, text, boolean) OWNER TO nexus_guard_owner;
REVOKE ALL ON FUNCTION nexus_control.set_service_principal(uuid, uuid[], name, text, boolean) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_control.set_service_principal(uuid, uuid[], name, text, boolean) TO nexus_membership_admin;

REVOKE ALL ON ALL TABLES IN SCHEMA nexus_control, nexus_source, nexus_hegc FROM nexus_membership_admin;

REVOKE ALL ON ALL TABLES IN SCHEMA nexus_control, nexus_source, nexus_hegc FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA nexus_control, nexus_source, nexus_hegc FROM nexus_hegc, nexus_writer, nexus_membership_admin;

COMMIT;
