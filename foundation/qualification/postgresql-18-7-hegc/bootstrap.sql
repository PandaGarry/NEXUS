\set ON_ERROR_STOP on

-- NON-PRODUCTION, EPHEMERAL QUALIFICATION FIXTURE ONLY.
-- This schema is created in a disposable PostgreSQL 18.7 CI container.
-- It is not a migration, production schema, or deployable NEXUS component.

CREATE ROLE nexus_control_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE nexus_hegc_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE nexus_risk_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE nexus_command_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

CREATE ROLE hegc_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE risk_writer LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE egress_gen_1 LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE egress_gen_2 LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE untrusted_runtime LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

REVOKE ALL ON DATABASE nexus_qualification FROM PUBLIC;
GRANT CONNECT ON DATABASE nexus_qualification TO hegc_runtime, risk_writer, egress_gen_1, egress_gen_2, untrusted_runtime;
GRANT TEMP ON DATABASE nexus_qualification TO hegc_runtime;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

CREATE SCHEMA nexus_control AUTHORIZATION nexus_control_owner;
CREATE SCHEMA nexus_hegc AUTHORIZATION nexus_hegc_owner;
CREATE SCHEMA nexus_risk AUTHORIZATION nexus_risk_owner;
CREATE SCHEMA nexus_command AUTHORIZATION nexus_command_owner;

GRANT USAGE ON SCHEMA nexus_control TO nexus_hegc_owner, nexus_risk_owner;
GRANT USAGE ON SCHEMA nexus_hegc, nexus_risk, nexus_command TO nexus_hegc_owner;
GRANT USAGE ON SCHEMA nexus_risk TO nexus_risk_owner;
GRANT USAGE ON SCHEMA nexus_hegc TO hegc_runtime, egress_gen_1, egress_gen_2;
GRANT USAGE ON SCHEMA nexus_risk TO risk_writer;
GRANT USAGE ON SCHEMA nexus_command TO untrusted_runtime;

CREATE TABLE nexus_control.scope_config (
    account_root uuid NOT NULL,
    scope_id uuid NOT NULL,
    is_root boolean NOT NULL,
    active boolean NOT NULL,
    PRIMARY KEY (account_root, scope_id),
    CHECK ((is_root AND scope_id = account_root) OR NOT is_root)
);
ALTER TABLE nexus_control.scope_config OWNER TO nexus_control_owner;

CREATE TABLE nexus_control.scope_guard (
    account_root uuid NOT NULL,
    scope_id uuid NOT NULL,
    is_root boolean NOT NULL,
    generation bigint NOT NULL DEFAULT 0 CHECK (generation >= 0),
    PRIMARY KEY (account_root, scope_id),
    CHECK ((is_root AND scope_id = account_root) OR NOT is_root)
);
ALTER TABLE nexus_control.scope_guard OWNER TO nexus_control_owner;

CREATE TABLE nexus_risk.risk_state (
    account_root uuid NOT NULL,
    scope_id uuid NOT NULL,
    exposure numeric(30, 8) NOT NULL,
    version bigint NOT NULL DEFAULT 1,
    PRIMARY KEY (account_root, scope_id)
);
ALTER TABLE nexus_risk.risk_state OWNER TO nexus_risk_owner;
ALTER TABLE nexus_risk.risk_state ENABLE ROW LEVEL SECURITY;
CREATE POLICY hegc_account_read ON nexus_risk.risk_state
    FOR SELECT TO nexus_hegc_owner
    USING (account_root = '00000000-0000-0000-0000-000000000001'::uuid);

CREATE TABLE nexus_command.command_outbox (
    command_id uuid PRIMARY KEY,
    account_root uuid NOT NULL,
    scope_ids uuid[] NOT NULL,
    command_digest text NOT NULL,
    reservation_active boolean NOT NULL,
    observed_halt_epoch bigint NOT NULL,
    eligibility_revision bigint NOT NULL,
    dispatcher_generation bigint NOT NULL
);
ALTER TABLE nexus_command.command_outbox OWNER TO nexus_command_owner;

CREATE TABLE nexus_hegc.halt_state (
    account_root uuid PRIMARY KEY,
    epoch bigint NOT NULL CHECK (epoch > 0),
    phase text NOT NULL CHECK (phase IN ('ACTIVE', 'HALTING', 'HALTED'))
);
ALTER TABLE nexus_hegc.halt_state OWNER TO nexus_hegc_owner;

CREATE TABLE nexus_hegc.workload_registry (
    account_root uuid PRIMARY KEY,
    egress_principal name NOT NULL,
    workload_generation bigint NOT NULL,
    artifact_digest text NOT NULL,
    environment text NOT NULL,
    active boolean NOT NULL
);
ALTER TABLE nexus_hegc.workload_registry OWNER TO nexus_hegc_owner;

CREATE TABLE nexus_hegc.egress_grant (
    attempt_id uuid PRIMARY KEY,
    command_id uuid NOT NULL,
    command_digest text NOT NULL,
    account_root uuid NOT NULL,
    scope_ids uuid[] NOT NULL,
    halt_epoch bigint NOT NULL,
    eligibility_revision bigint NOT NULL,
    dispatcher_generation bigint NOT NULL,
    egress_principal name NOT NULL,
    workload_generation bigint NOT NULL,
    artifact_digest text NOT NULL,
    status text NOT NULL CHECK (status IN ('GATE_COMMITTED', 'GRANT_CONSUMED', 'SOCKET_INITIATED', 'SENDER_FENCED_UNKNOWN'))
);
ALTER TABLE nexus_hegc.egress_grant OWNER TO nexus_hegc_owner;

INSERT INTO nexus_control.scope_config(account_root, scope_id, is_root, active) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', true, true),
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', false, true),
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000003', false, true),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000010', true, true),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000011', false, true),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000012', false, true);

INSERT INTO nexus_control.scope_guard(account_root, scope_id, is_root) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', true),
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', false),
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000003', false),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000010', true),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000011', false),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000012', false);

INSERT INTO nexus_risk.risk_state(account_root, scope_id, exposure) VALUES
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 10),
('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000003', 10),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000011', 10),
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000012', 10);

INSERT INTO nexus_command.command_outbox(
    command_id, account_root, scope_ids, command_digest, reservation_active,
    observed_halt_epoch, eligibility_revision, dispatcher_generation
) VALUES
(
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    ARRAY[
      '00000000-0000-0000-0000-000000000001'::uuid,
      '00000000-0000-0000-0000-000000000002'::uuid,
      '00000000-0000-0000-0000-000000000003'::uuid
    ],
    'sha256:fixture-command-a',
    true, 7, 1, 1
),
(
    '10000000-0000-0000-0000-000000000010',
    '00000000-0000-0000-0000-000000000010',
    ARRAY[
      '00000000-0000-0000-0000-000000000010'::uuid,
      '00000000-0000-0000-0000-000000000011'::uuid,
      '00000000-0000-0000-0000-000000000012'::uuid
    ],
    'sha256:fixture-command-b',
    true, 7, 1, 1
);

INSERT INTO nexus_hegc.halt_state(account_root, epoch, phase) VALUES
('00000000-0000-0000-0000-000000000001', 7, 'ACTIVE'),
('00000000-0000-0000-0000-000000000010', 7, 'ACTIVE');

INSERT INTO nexus_hegc.workload_registry(
    account_root, egress_principal, workload_generation, artifact_digest, environment, active
) VALUES
('00000000-0000-0000-0000-000000000001', 'egress_gen_1', 1, 'sha256:egress-one', 'qualification', true),
('00000000-0000-0000-0000-000000000010', 'egress_gen_2', 2, 'sha256:egress-two', 'qualification', true);

GRANT SELECT ON nexus_control.scope_config TO nexus_control_owner;
GRANT UPDATE ON nexus_control.scope_guard TO nexus_control_owner;
GRANT SELECT ON nexus_risk.risk_state TO nexus_hegc_owner;
GRANT SELECT ON nexus_command.command_outbox TO nexus_hegc_owner;
GRANT SELECT, INSERT, UPDATE ON nexus_hegc.egress_grant TO nexus_hegc_owner;
GRANT SELECT, UPDATE ON nexus_hegc.halt_state TO nexus_hegc_owner;
GRANT SELECT ON nexus_hegc.workload_registry TO nexus_hegc_owner;
GRANT UPDATE ON nexus_risk.risk_state TO nexus_risk_owner;

CREATE FUNCTION nexus_control.acquire_scope_guards(p_scope_ids uuid[])
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_control, pg_temp
AS $$
DECLARE
    v_root uuid;
    v_expected uuid[];
    v_actual uuid[];
    v_scope uuid;
BEGIN
    IF session_user NOT IN ('hegc_runtime', 'risk_writer') THEN
        RAISE EXCEPTION 'caller is not allowed to acquire execution guards'
            USING ERRCODE = '42501';
    END IF;

    IF p_scope_ids IS NULL OR cardinality(p_scope_ids) < 1 OR p_scope_ids[1] IS NULL THEN
        RAISE EXCEPTION 'scope set must contain the account/root guard first'
            USING ERRCODE = '22023';
    END IF;

    v_root := p_scope_ids[1];

    -- This is deliberately the first protected SQL operation: acquire root before
    -- reading scope configuration or any Risk/Command source record.
    UPDATE nexus_control.scope_guard
       SET generation = generation + 1
     WHERE account_root = v_root AND scope_id = v_root AND is_root
     RETURNING scope_id INTO v_scope;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'pre-provisioned account/root guard is missing'
            USING ERRCODE = 'P0001';
    END IF;

    SELECT array_agg(scope_id ORDER BY pg_catalog.uuid_send(scope_id))
      INTO v_expected
      FROM nexus_control.scope_config
     WHERE account_root = v_root AND active AND NOT is_root;

    IF v_expected IS NULL THEN
        v_expected := ARRAY[]::uuid[];
    END IF;

    IF EXISTS (SELECT 1 FROM unnest(p_scope_ids[2:cardinality(p_scope_ids)]) AS x(scope_id) WHERE scope_id IS NULL) THEN
        RAISE EXCEPTION 'NULL child scope is prohibited' USING ERRCODE = '22023';
    END IF;

    SELECT array_agg(scope_id ORDER BY pg_catalog.uuid_send(scope_id))
      INTO v_actual
      FROM unnest(p_scope_ids[2:cardinality(p_scope_ids)]) AS x(scope_id);

    IF v_actual IS DISTINCT FROM v_expected THEN
        RAISE EXCEPTION 'scope set is incomplete, duplicated, unknown or not active'
            USING ERRCODE = '22023';
    END IF;

    FOR v_scope IN
        SELECT scope_id
          FROM unnest(v_expected) AS x(scope_id)
         ORDER BY pg_catalog.uuid_send(scope_id)
    LOOP
        UPDATE nexus_control.scope_guard
           SET generation = generation + 1
         WHERE account_root = v_root AND scope_id = v_scope AND NOT is_root;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'pre-provisioned child scope guard is missing'
                USING ERRCODE = 'P0001';
        END IF;
    END LOOP;
END;
$$;
ALTER FUNCTION nexus_control.acquire_scope_guards(uuid[]) OWNER TO nexus_control_owner;
REVOKE ALL ON FUNCTION nexus_control.acquire_scope_guards(uuid[]) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_control.acquire_scope_guards(uuid[]) TO nexus_hegc_owner, nexus_risk_owner;

CREATE FUNCTION nexus_risk.apply_invalidation(p_scope_ids uuid[], p_exposure numeric)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_risk, pg_temp
AS $$
DECLARE
    v_rows bigint;
BEGIN
    IF session_user <> 'risk_writer' THEN
        RAISE EXCEPTION 'caller is not Risk writer' USING ERRCODE = '42501';
    END IF;

    PERFORM nexus_control.acquire_scope_guards(p_scope_ids);

    UPDATE nexus_risk.risk_state
       SET exposure = p_exposure, version = version + 1
     WHERE account_root = p_scope_ids[1]
       AND scope_id = ANY(p_scope_ids[2:cardinality(p_scope_ids)]);

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    IF v_rows <> cardinality(p_scope_ids) - 1 THEN
        RAISE EXCEPTION 'Risk source update did not cover every requested scope'
            USING ERRCODE = 'P0001';
    END IF;

    RETURN 'RISK_UPDATED';
END;
$$;
ALTER FUNCTION nexus_risk.apply_invalidation(uuid[], numeric) OWNER TO nexus_risk_owner;
REVOKE ALL ON FUNCTION nexus_risk.apply_invalidation(uuid[], numeric) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_risk.apply_invalidation(uuid[], numeric) TO risk_writer;

CREATE FUNCTION nexus_hegc.identity_probe()
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_hegc, pg_temp
AS $$
    SELECT session_user::text || '|' || current_user::text
$$;
ALTER FUNCTION nexus_hegc.identity_probe() OWNER TO nexus_hegc_owner;
REVOKE ALL ON FUNCTION nexus_hegc.identity_probe() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_hegc.identity_probe() TO hegc_runtime, egress_gen_1, egress_gen_2;

CREATE FUNCTION nexus_hegc.authorize_egress_attempt(
    p_attempt_id uuid,
    p_command_id uuid,
    p_scope_ids uuid[]
)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_hegc, pg_temp
AS $$
DECLARE
    v_command nexus_command.command_outbox%ROWTYPE;
    v_existing nexus_hegc.egress_grant%ROWTYPE;
    v_halt nexus_hegc.halt_state%ROWTYPE;
    v_workload nexus_hegc.workload_registry%ROWTYPE;
    v_exposure numeric;
    v_source_rows bigint;
BEGIN
    IF session_user <> 'hegc_runtime' THEN
        RAISE EXCEPTION 'caller is not HEGC runtime' USING ERRCODE = '42501';
    END IF;

    -- Guard acquisition is the first protected read/write. All source reads follow it.
    PERFORM nexus_control.acquire_scope_guards(p_scope_ids);

    SELECT * INTO v_command
      FROM nexus_command.command_outbox
     WHERE command_id = p_command_id;

    IF NOT FOUND OR NOT v_command.reservation_active
       OR v_command.account_root <> p_scope_ids[1]
       OR v_command.scope_ids IS DISTINCT FROM p_scope_ids THEN
        RAISE EXCEPTION 'canonical command/reservation/scope binding invalid'
            USING ERRCODE = 'P0001';
    END IF;

    -- Check idempotency before current HALT/freshness checks: exact retry returns
    -- the original attempt, never a new grant. Changed binding is a conflict.
    SELECT * INTO v_existing
      FROM nexus_hegc.egress_grant
     WHERE attempt_id = p_attempt_id
     FOR UPDATE;

    IF FOUND THEN
        IF v_existing.command_id <> p_command_id
           OR v_existing.command_digest <> v_command.command_digest
           OR v_existing.account_root <> v_command.account_root
           OR v_existing.scope_ids IS DISTINCT FROM v_command.scope_ids
           OR v_existing.halt_epoch <> v_command.observed_halt_epoch
           OR v_existing.eligibility_revision <> v_command.eligibility_revision
           OR v_existing.dispatcher_generation <> v_command.dispatcher_generation THEN
            RAISE EXCEPTION 'attempt ID reused with changed binding'
                USING ERRCODE = '23505';
        END IF;
        RETURN 'EXISTING:' || v_existing.status;
    END IF;

    SELECT * INTO v_halt
      FROM nexus_hegc.halt_state
     WHERE account_root = v_command.account_root;

    IF NOT FOUND OR v_halt.phase <> 'ACTIVE'
       OR v_halt.epoch <> v_command.observed_halt_epoch THEN
        RETURN 'DENIED_HALT';
    END IF;

    SELECT * INTO v_workload
      FROM nexus_hegc.workload_registry
     WHERE account_root = v_command.account_root AND active;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'no active Egress workload identity' USING ERRCODE = 'P0001';
    END IF;

    SELECT count(*), COALESCE(sum(exposure), 0)
      INTO v_source_rows, v_exposure
      FROM nexus_risk.risk_state
     WHERE account_root = v_command.account_root
       AND scope_id = ANY(v_command.scope_ids[2:cardinality(v_command.scope_ids)]);

    -- RLS-hidden or missing source rows must fail closed, never look like zero exposure.
    IF v_source_rows <> cardinality(v_command.scope_ids) - 1 THEN
        RAISE EXCEPTION 'authoritative Risk source set incomplete or not visible'
            USING ERRCODE = '42501';
    END IF;

    IF v_exposure >= 100 THEN
        RETURN 'DENIED_RISK';
    END IF;

    INSERT INTO nexus_hegc.egress_grant(
        attempt_id, command_id, command_digest, account_root, scope_ids,
        halt_epoch, eligibility_revision, dispatcher_generation,
        egress_principal, workload_generation, artifact_digest, status
    ) VALUES (
        p_attempt_id, p_command_id, v_command.command_digest, v_command.account_root,
        v_command.scope_ids, v_command.observed_halt_epoch, v_command.eligibility_revision,
        v_command.dispatcher_generation, v_workload.egress_principal,
        v_workload.workload_generation, v_workload.artifact_digest, 'GATE_COMMITTED'
    );

    RETURN 'GRANTED';
END;
$$;
ALTER FUNCTION nexus_hegc.authorize_egress_attempt(uuid, uuid, uuid[]) OWNER TO nexus_hegc_owner;
REVOKE ALL ON FUNCTION nexus_hegc.authorize_egress_attempt(uuid, uuid, uuid[]) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_hegc.authorize_egress_attempt(uuid, uuid, uuid[]) TO hegc_runtime;

CREATE FUNCTION nexus_hegc.consume_egress_grant(p_attempt_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_hegc, pg_temp
AS $$
DECLARE
    v_grant nexus_hegc.egress_grant%ROWTYPE;
BEGIN
    SELECT * INTO v_grant
      FROM nexus_hegc.egress_grant
     WHERE attempt_id = p_attempt_id
     FOR UPDATE;

    IF NOT FOUND OR v_grant.egress_principal::text <> session_user::text THEN
        RAISE EXCEPTION 'attempt is not bound to this Egress generation'
            USING ERRCODE = '42501';
    END IF;

    IF v_grant.status = 'GATE_COMMITTED' THEN
        UPDATE nexus_hegc.egress_grant
           SET status = 'GRANT_CONSUMED'
         WHERE attempt_id = p_attempt_id;
        RETURN 'CONSUMED_ONCE';
    ELSIF v_grant.status = 'GRANT_CONSUMED' THEN
        RETURN 'ALREADY_CONSUMED_NO_SEND';
    END IF;

    RAISE EXCEPTION 'grant is not consumable in current state' USING ERRCODE = '55000';
END;
$$;
ALTER FUNCTION nexus_hegc.consume_egress_grant(uuid) OWNER TO nexus_hegc_owner;
REVOKE ALL ON FUNCTION nexus_hegc.consume_egress_grant(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_hegc.consume_egress_grant(uuid) TO egress_gen_1, egress_gen_2;

CREATE FUNCTION nexus_hegc.report_socket_initiated(p_attempt_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_hegc, pg_temp
AS $$
DECLARE
    v_rows bigint;
BEGIN
    UPDATE nexus_hegc.egress_grant
       SET status = 'SOCKET_INITIATED'
     WHERE attempt_id = p_attempt_id
       AND egress_principal::text = session_user::text
       AND status = 'GRANT_CONSUMED';

    GET DIAGNOSTICS v_rows = ROW_COUNT;
    IF v_rows <> 1 THEN
        RAISE EXCEPTION 'socket initiation report is not authorized for this attempt'
            USING ERRCODE = '42501';
    END IF;

    RETURN 'SOCKET_INITIATED';
END;
$$;
ALTER FUNCTION nexus_hegc.report_socket_initiated(uuid) OWNER TO nexus_hegc_owner;
REVOKE ALL ON FUNCTION nexus_hegc.report_socket_initiated(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_hegc.report_socket_initiated(uuid) TO egress_gen_1, egress_gen_2;

CREATE FUNCTION nexus_hegc.get_attempt_status(p_attempt_id uuid)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, nexus_hegc, pg_temp
AS $$
DECLARE
    v_grant nexus_hegc.egress_grant%ROWTYPE;
BEGIN
    SELECT * INTO v_grant FROM nexus_hegc.egress_grant WHERE attempt_id = p_attempt_id;
    IF NOT FOUND THEN
        RETURN 'NOT_FOUND';
    END IF;
    IF session_user <> 'hegc_runtime'
       AND v_grant.egress_principal::text <> session_user::text THEN
        RAISE EXCEPTION 'attempt status is not visible to this workload'
            USING ERRCODE = '42501';
    END IF;
    RETURN v_grant.status;
END;
$$;
ALTER FUNCTION nexus_hegc.get_attempt_status(uuid) OWNER TO nexus_hegc_owner;
REVOKE ALL ON FUNCTION nexus_hegc.get_attempt_status(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nexus_hegc.get_attempt_status(uuid) TO hegc_runtime, egress_gen_1, egress_gen_2;

REVOKE ALL ON ALL TABLES IN SCHEMA nexus_control FROM PUBLIC, hegc_runtime, risk_writer, egress_gen_1, egress_gen_2, untrusted_runtime;
REVOKE ALL ON ALL TABLES IN SCHEMA nexus_hegc FROM PUBLIC, hegc_runtime, risk_writer, egress_gen_1, egress_gen_2, untrusted_runtime;
REVOKE ALL ON ALL TABLES IN SCHEMA nexus_risk FROM PUBLIC, hegc_runtime, risk_writer, egress_gen_1, egress_gen_2, untrusted_runtime;
REVOKE ALL ON ALL TABLES IN SCHEMA nexus_command FROM PUBLIC, hegc_runtime, risk_writer, egress_gen_1, egress_gen_2, untrusted_runtime;

-- Only the dedicated NOLOGIN owners can access the underlying tables.
GRANT SELECT ON nexus_control.scope_config TO nexus_control_owner;
GRANT UPDATE ON nexus_control.scope_guard TO nexus_control_owner;
GRANT SELECT ON nexus_risk.risk_state TO nexus_hegc_owner;
GRANT SELECT ON nexus_command.command_outbox TO nexus_hegc_owner;
GRANT SELECT, INSERT, UPDATE ON nexus_hegc.egress_grant TO nexus_hegc_owner;
GRANT SELECT, UPDATE ON nexus_hegc.halt_state TO nexus_hegc_owner;
GRANT SELECT ON nexus_hegc.workload_registry TO nexus_hegc_owner;
GRANT UPDATE ON nexus_risk.risk_state TO nexus_risk_owner;

-- Ensure only reviewed entrypoints are executable by runtime principals.
GRANT USAGE ON SCHEMA nexus_control TO nexus_hegc_owner, nexus_risk_owner;
GRANT USAGE ON SCHEMA nexus_hegc TO hegc_runtime, egress_gen_1, egress_gen_2;
GRANT USAGE ON SCHEMA nexus_risk TO risk_writer;
