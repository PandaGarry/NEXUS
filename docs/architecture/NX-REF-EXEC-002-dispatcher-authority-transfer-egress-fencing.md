# NX-REF-EXEC-002 — Dispatcher Authority Transfer and Egress Fencing

**Status:** PROPOSED DESIGN / REFERENCE CONFORMANCE PLAN — NOT IMPLEMENTED  
**Date:** 2026-11-14  
**Related contracts:** NX-IF-001, NX-IF-002, NX-IF-004, NX-IF-005, NX-ADR-002, NX-SEC-001  
**Scope:** Account-scoped CREATE dispatch authority transfer and stale-worker containment. No venue adapter or production deployment.

## 1. Problem statement

NX-REF-EXEC-001 contains an adversarial counterexample: a dispatcher can pass its final local halt/expiry check, pause before network transmission, lose operational authority while recovery marks its command OUTCOME_UNKNOWN, then resume and send. An earlier model revision also allowed a late ACK to overwrite recovery state; the current conditional state transition rejects that overwrite and records the response as a stale venue observation. The external send race remains unresolved.

A database lease, heartbeat, fencing integer, or local token check is not sufficient when the stale process still has venue credentials, an open network route, or direct access to the adapter. The stale process can ignore the token or have already passed the check.

**Safety objective:** after authority transfer is declared complete, no process from the previous authority generation can cause a venue-side state change or mutate authoritative command state.

## 2. Terms and authority boundaries

- **Account dispatch scope:** the initial hard boundary is one venue account/subaccount as recorded by the account registry.
- **Authority epoch:** monotonically increasing account-scoped generation, persisted by the authoritative control plane.
- **Dispatcher worker:** computes/claims work but has no venue credentials and no direct venue network egress.
- **Egress authority:** the only service/process allowed to hold venue credentials and establish venue connections for that account.
- **Egress fence:** independently enforced revocation of the old authority's ability to reach the venue, not merely a database flag.
- **Dispatch attempt:** immutable attempt identity linked to command ID, authority epoch, and client order identifier where venue semantics support it.
- **Outcome unknown:** no assumption of success or failure until venue evidence/reconciliation resolves the attempt.

## 3. Non-negotiable invariants

1. Exactly one active egress authority exists per account scope.
2. Strategy, AI, API clients, schedulers, and ordinary dispatcher workers never possess venue credentials or direct venue egress.
3. Lease expiry is a signal to begin takeover, not proof that the old egress path is fenced.
4. The control plane must not grant a new egress capability until it has positive evidence that the previous process/network identity/credential path is revoked or the old host is externally fenced.
5. If old-path fencing cannot be proven, account CREATE dispatch remains HALTED. Availability is subordinate to preventing duplicate external effects.
6. Every command attempt is bound to account scope, authority epoch, command digest, approval, reservation, instrument-spec version, and a unique attempt ID.
7. State transitions use compare-and-swap against the current authority epoch and expected prior state. A stale epoch cannot overwrite a newer recovery or reconciliation state.
8. A late response from a stale worker is retained as untrusted evidence for reconciliation; it cannot directly set authoritative ACKNOWLEDGED/FILLED state.
9. DISPATCHING at takeover becomes OUTCOME_UNKNOWN unless authoritative venue evidence proves a terminal result. It is never blindly resent.
10. Venue idempotency/client-order IDs are defense in depth only. They do not replace egress fencing and must be qualified per venue/product.

## 4. Required architecture

### 4.1 Credential and network isolation

- Only the account-scoped Egress Authority receives the venue API credential and network permission.
- Workers submit immutable, authenticated command envelopes to the Egress Authority over a private authenticated interface.
- Venue credentials are not mounted in strategy, AI, API, scheduler, notebook, or general worker environments.
- Network policy denies direct venue egress from all components except the Egress Authority boundary.
- The Egress Authority is itself single-writer for an account scope; multiple workers may enqueue but cannot call the venue adapter.
- Production deployment must select and verify a concrete fencing mechanism: confirmed host/VM termination, revocable workload identity plus enforced egress proxy/firewall policy, or another independently controlled mechanism with equivalent evidence.
- A database lease or advisory lock held only by the potentially stale process is not accepted as the sole fence.

### 4.2 Durable command state

The authoritative store records:
- account scope;
- authority epoch and egress identity;
- command ID and canonical digest;
- approval ID and reservation ID;
- attempt ID and client order ID (when supported);
- state and monotonic state version;
- timestamps and source provenance;
- venue observations and reconciliation status.

A transition is accepted only when the account scope, authority epoch, command ID, expected state, and state version match the current row. Stale workers cannot mutate the authoritative command projection. Their messages may be appended to an observation inbox for later reconciliation.

### 4.3 Takeover protocol

1. **Freeze:** control plane durably marks account CREATE dispatch HALTING and rejects new increases.
2. **Advance epoch:** allocate a new authority epoch; old epoch becomes revoked for future state mutations.
3. **Fence old egress:** revoke the old workload identity/network route/credential, or externally terminate/fence its host. Wait for positive fence evidence. Timeout or uncertainty means remain HALTED.
4. **Quarantine:** every old-epoch DISPATCHING attempt becomes OUTCOME_UNKNOWN. Preserve command, reservation and exposure; do not release capacity.
5. **Reconcile:** query venue open orders, order history, fills, and private event stream using venue-qualified identifiers/cursors. Reconcile gaps and ambiguous results. If evidence is incomplete, remain HALTED and preserve UNKNOWN exposure.
6. **Grant:** only after old egress is fenced and required reconciliation evidence is complete may the control plane issue the new epoch's egress capability.
7. **Resume:** require NX-IF-005 resume authorization and current NX-IF-004 recovery evidence. CREATE remains blocked until all gates pass.

The old worker may later return an ACK or timeout. That response is recorded as stale-epoch evidence only. It cannot restore its send capability or overwrite the current command state.

## 5. Critical failure behavior

| Failure | Required behavior |
|---|---|
| Lease expires, old host status unknown | Do not grant new egress authority; HALT |
| Control plane unavailable | No new CREATE dispatch |
| Fence operation times out | HALT; operator intervention |
| Old worker resumes after epoch advance | Reject state mutation; egress must already be unreachable |
| Late ACK arrives after recovery | Append observation; reconcile; never overwrite state directly |
| Venue query/history incomplete | Keep OUTCOME_UNKNOWN and exposure reservation |
| Venue lacks reliable idempotency | Never automatic resend after ambiguous attempt |
| Egress Authority crashes after send | Recover as OUTCOME_UNKNOWN; reconcile before any retry |
| Two egress authorities appear active | Security incident; revoke both paths, HALT and reconcile |

## 6. Reference conformance scenarios

A test-only Python control-plane state machine now exists at `foundation/reference-model/egress-fencing/`. Its unit tests cover transition ordering (HALTING → FENCING → FENCED → RECONCILING → READY_TO_GRANT), stale epoch rejection and fail-closed behavior. It does not revoke a network route, terminate a host, validate trusted fence attestations or prove actual egress isolation. A passing state-machine test is not a production fence.

A production-grade conformance harness must prove:
1. A worker paused immediately before egress cannot send after its egress identity is revoked.
2. A new authority cannot obtain credentials/route before positive fence acknowledgement.
3. A stale epoch cannot update command state after authority epoch changes.
4. A late ACK is retained as an observation and cannot overwrite OUTCOME_UNKNOWN.
5. A failed/unknown fence operation leaves the account HALTED.
6. A crash after egress but before ACK persistence becomes OUTCOME_UNKNOWN and is reconciled, never blindly resent.
7. Concurrent takeover requests produce one authority epoch transition and one egress owner.
8. Process restart, host restart, network partition, clock skew, delayed messages, and duplicate events fail closed.
9. Venue idempotency behavior is separately tested for each venue/product/account mode.
10. No strategy/AI process can bypass the egress boundary even if it constructs a valid-looking command.

The harness must distinguish a simulated trusted egress broker from a database-only token check. A test that merely checks an epoch immediately before a fake adapter call does not prove the real network path is fenced.

## 7. Unresolved production decisions

- Hosting provider, region, workload identity and host-fencing mechanism.
- Authoritative database and transaction/isolation model.
- Egress proxy/broker technology and high-availability design.
- Venue/product support for client order IDs, idempotency, order lookup and private event replay.
- Reconciliation completeness criteria and operator authority.
- RPO/RTO, failover timing and manual break-glass process.
- Credential rotation/revocation and incident response.
- Numeric and operational halt thresholds remain separate owner decisions.

## 8. Exit criteria

This contract is not implementation-ready until:
- security and operations review the concrete egress isolation/fencing mechanism;
- the old authority can be positively fenced under host/network partition scenarios;
- all state mutations are epoch- and version-conditional;
- adversarial stale-worker tests pass against the actual egress boundary;
- venue-specific reconciliation/idempotency capabilities are evidenced;
- recovery and resume policy is approved under NX-IF-004/NX-IF-005.

No live credential, order, risk-limit change, production deployment, or live-trading permission is granted by this document.
