# Egress authority handover reference model

**Status:** Test-only control-plane state-machine model; not an egress security boundary.

This package models the required ordering for an account-scoped authority handover:

`ACTIVE → HALTING → FENCING → FENCED → RECONCILING → READY_TO_GRANT → ACTIVE(new epoch)`

It checks that:
- takeover revokes old-epoch eligibility at the modeled control plane;
- a new authority cannot be granted before positive old-egress fence evidence;
- reconciliation cannot begin before fencing;
- a new authority cannot be granted before reconciliation evidence;
- unknown fencing outcomes fail closed;
- stale identities/epochs cannot regain dispatch eligibility through the model.

A separate `HaltEgressGate` oracle models the final EgressBoundaryAuthorization / halt-epoch race:

- halt epoch commits first: the new final gate is denied;
- final gate commits first: the attempt is in-flight and blocks halt acknowledgement until socket initiation is observed or the sender is positively fenced;
- sender fencing prevents future socket initiation but does not prove that no earlier side effect occurred; without a trusted initiation report, the attempt remains OUTCOME_UNKNOWN, retains its reservation and requires reconciliation;
- socket-initiated attempts remain reconciliation obligations after HALTED acknowledgement;
- authoritative halt-store outage blocks new final gates and leaves a request pending rather than claiming HALTED.

The `HaltEgressGate` oracle currently has 24 tests; together with 13 authority-handover tests, this package runs 37 tests. It covers idempotent attempt-grant issuance (exact retry returns the original attempt; changed bindings conflict), single-use HEGC grant consumption before socket initiation, lost consume responses, store outage/recovery, signed 64-bit halt-epoch bounds, duplicate halt idempotency and preservation of the initiating halt cause.

The model uses sequential method calls to represent the two commit orders. `SOCKET_INITIATED` represents the first transport write of one logical venue request, not one operating-system syscall, complete delivery or venue acceptance. The model does not emulate HTTP/TLS client retries, redirects, proxy replay or WebSocket reconnect behavior; those remain explicit production transport qualification gates. It does not prove database lock semantics or real concurrent linearizability. PostgreSQL SERIALIZABLE/SSI alone does not prove the required wall-clock commit-order visibility for overlapping source writers; G1 still requires the separately enforced per-scope HEGC commit-order guard described in NX-RESEARCH-012 §4.2. A positive sender-fence fixture never classifies an attempt as DEFINITELY_NOT_SENT; reconciliation and reservation retention remain mandatory when socket initiation was not authoritatively observed.

Run:

```bash
python -m unittest -v
```

## Critical limitations

The model is deliberately not capable of fencing a real process or network route. Its fence receipt is an opaque test string supplied by the caller; there is no trusted attestation verifier, cloud/host supervisor, firewall/proxy integration, credential revocation, network policy or distributed database.

Therefore:
- a passing test proves only the modeled transition ordering;
- it does not prove a stale process cannot use already-held credentials or an open socket;
- it does not prove a host has been terminated or an egress route revoked;
- it is not production code and must not be imported into a trading service.

Production qualification still requires NX-REF-EXEC-002's independently controlled egress fence, positive evidence, reconciliation and adversarial tests against the actual network boundary.
