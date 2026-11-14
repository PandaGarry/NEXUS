# NX-REF-EXEC-002 — Dispatcher Authority Transfer and Egress Fencing

**Status:** PROPOSED DESIGN / REFERENCE CONFORMANCE PLAN — NOT IMPLEMENTED  
**Date:** 2026-11-14  
**Related contracts:** NX-IF-001, NX-IF-002, NX-IF-004, NX-IF-005, NX-ADR-002, NX-ADR-008, NX-SEC-001  
**Scope:** Account-scoped CREATE dispatch authority transfer and stale-worker containment. No venue adapter or production deployment.

## 1. Problem statement

NX-REF-EXEC-001 contains an adversarial counterexample: a dispatcher can pass its final local halt/expiry check, pause before network transmission, lose operational authority while recovery marks its command OUTCOME_UNKNOWN, then resume and send. An earlier model revision also allowed a late ACK to overwrite recovery state; conditional state transitions reject late ACK, stale pre-send rejection and adapter-error writes after recovery, recording stale evidence without overwriting the authoritative state. The external send race remains unresolved.

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
8. Late ACKs and dispatch errors from a stale worker are retained as untrusted evidence for reconciliation; conditional state transitions prevent them from overwriting authoritative recovery state.
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

### 4.4 Recommended implementation decomposition (PROPOSED; OD-09 remains open)

The following decomposition is the recommended starting point for G1 design. It deliberately avoids a distributed transaction across Risk, Command and Egress. It is not a selected database, broker, cloud provider or production topology.

1. **Risk reservation transaction — Risk-owned authority.** In one serializable/linearizable logical transaction, validate the current exposure/scope versions, idempotency key and fencing versions; commit every required account-scope reservation and the durable request/result record; only after commit may Risk return an approval capability. A retry with the same request ID and digest returns the original reservation result. A request-ID/digest mismatch is a hard conflict. Multi-scope partial commit must never authorize.
2. **Command acceptance transaction — Command Coordinator-owned authority.** Independently validate the capability's account/scope, command digest, reservation identity/version, policy/exposure/spec versions, halt epoch and expiry. In one local atomic transaction, consume the single-use nonce/approval and persist the immutable canonical command, reservation reference and outbox row. If the commit result is ambiguous to the caller, recover by the stable command/request identity and read the committed state; never issue a second command or consume a second reservation to "fix" uncertainty.
3. **Attempt transaction — dispatcher/control-plane authority.** Claim an outbox item with a monotonic account-scoped epoch/fence and persist a unique attempt plus the conservative DISPATCH_OUTCOME_UNKNOWN marker before asking Egress to transmit. A stale claimant may append observations but cannot mutate authoritative state after epoch/version change.
4. **Send boundary — Egress-owned authority.** Egress receives only a persisted command/attempt reference, loads the canonical payload from the authoritative store, validates all bound authorization and eligibility evidence, and is the only component holding credentials and the venue socket. The dispatcher/adapter cannot submit arbitrary payload bytes or open a parallel venue connection.
5. **Authority transfer — external fence plus reconciliation.** A new egress generation is not granted merely because a lease expired or a database epoch advanced. The old egress identity/host/network path must be positively revoked or externally fenced, then all possibly-sent attempts reconciled before CREATE resumes.

**Transaction boundary conclusion:** Risk reservation and Command acceptance are two ordered, separately durable commits, not one distributed ACID transaction. The capability is the hand-off between them. The only atomicity required at Command acceptance is single-use capability consumption together with command + reservation reference + outbox persistence. Risk capacity remains held independently until authoritative venue/ledger reconciliation permits a terminal transfer or release. This preserves fail-closed recovery without requiring a cross-service two-phase commit.

**Capability implementation remains undecided:** an opaque server-side handle or a signed envelope may be evaluated. Whichever is selected must provide command-digest binding, scope and version binding, expiry, unique single-use identity, revocation/invalidation semantics and durable replay prevention. Cryptographic algorithm, canonical serialization and key custody remain OD-08/security decisions; no signature scheme is selected here.

**Egress topology recommendation:** prefer one account-scoped credential-owning egress boundary with workers lacking venue credentials and direct venue routes. The egress boundary must own the actual socket/send operation; a proxy that only checks an epoch and then hands bytes to a stale credential-bearing worker does not close the race. Takeover requires independently controlled revocation of the old egress process identity or host/network path and positive evidence of revocation. If the selected infrastructure cannot prove that property during partition or control-plane outage, remain HALTED. Active-active egress for one account is excluded until an equivalent single-writer and revocation proof exists.

**Open selection:** authoritative database/isolation, workload identity, host-fencing mechanism, network enforcement point, egress availability topology and operator break-glass remain OD-09/OD-10/OD-12 and deployment/security review items. This recommendation does not close those decisions.

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

### 5.1 Crash-point matrix for implementation and fault injection

The matrix below is a minimum G1 test plan. It defines expected recovery behavior; it does not claim these guarantees are implemented.

| Crash / ambiguity point | Durable facts that may exist | Required recovery behavior | Forbidden shortcut |
|---|---|---|---|
| Before Risk reservation commit | No committed reservation result | Retry same request idempotently; reevaluate current exposure | Issue approval from in-memory calculation |
| After Risk reservation commit, before capability response | Reservation and request/result record committed | Read and return the original reservation/capability result under the same request identity; keep capacity held | Reserve again or release on timeout |
| After capability issued, before Command consume | Reservation committed; capability may be held by caller | Capability remains single-use and bounded by expiry/version; retry is idempotent or rejected as already consumed | Treat lost response as proof no capability exists |
| During Command consume + command/outbox transaction, commit result unknown | Transaction may have committed or rolled back | Query by stable command/request identity; if committed, return existing command; if absent, retry same idempotency identity | Create a second command or consume another approval |
| After outbox claim, before attempt marker commit | Claim may be leased; no send is permitted yet | Reclaim only after claim/fence validation; create a new attempt only when no marker/send could have occurred | Send based on an uncommitted in-memory claim |
| After attempt marker commit, before socket operation | DISPATCH_OUTCOME_UNKNOWN is durable; venue may not have seen bytes | Preserve full reservation; reconcile; a definitely-not-sent conclusion requires authoritative transport evidence and fenced attempt | Release because socket write was not observed locally |
| During socket write / connection reset | Partial or complete request may have reached venue | OUTCOME_UNKNOWN; reconcile by qualified identifiers/history/stream and account snapshots | Blind retry |
| After venue acceptance, before response reaches Egress | Venue-side order may exist; local result absent | Reconcile venue state; preserve reservation | Assume rejection from timeout |
| After response received, before result persistence | Venue response existed only in process memory | Treat recovered state as unknown unless durable evidence exists; reconcile | Trust volatile memory after restart |
| Fill event persisted, before Ledger posting | Execution fact durable; journal not yet posted | Retry idempotent Ledger inbox/posting; keep fill-pending exposure | Transfer Risk exposure to confirmed position prematurely |
| Ledger journal committed, before acknowledgement/projection watermark | Posting may exist; consumer may replay | Read by stable posting/event identity; idempotently acknowledge and advance watermark only with evidence | Post a duplicate journal entry |
| After Ledger watermark, before Risk exposure transfer | Ledger projection is ahead of Risk transfer | Reconcile matching fill, journal and watermark; then perform one version-checked transfer | Drop fill-pending reserve before transfer commit |
| Halt epoch advanced, before old egress fence acknowledgement | New halt is durable; old egress may still possess a route/socket | Block new CREATE; fence old path and retain uncertain attempts | Grant new egress because epoch changed |
| Old host/process status unknown during takeover | Old egress may still transmit | Remain HALTED until external fence evidence is positive | Treat lease expiry or heartbeat loss as fencing |
| RecoveryBarrier evidence missing, stale or contradictory | Some sources/projections may be incomplete | Keep affected scope quarantined; no risk-increasing resume | Resume on process restart or reconnect alone |
| Halt epoch commits before final EgressBoundaryAuthorization | New halt generation is authoritative | Final gate observes new generation and denies; no socket-write initiation | Trust cached epoch or asynchronous notification |
| Final EgressBoundaryAuthorization commits before halt epoch | One attempt is durably gate-committed/in-flight | Retain full reservation; track until socket-write initiation is observed or old sender is positively fenced | Claim the already committed authorization was retroactively revoked |
| Egress process pauses after gate commit, before socket write | Old process could resume and initiate a write | Do not acknowledge halt epoch until write is observed or process/host/network path is positively fenced | Treat DB commit or local "send started" flag as proof the socket call occurred |
| Halt control store unavailable/authority uncertain | Current halt generation cannot be established | Deny final Egress gates; halt remains pending and cannot be reported fully enforced | Allow send using last cached epoch |
| Socket write initiated before halt boundary acknowledgement; venue accepts after acknowledgement | External request may still be processed | Keep order/attempt potentially live; reconcile venue state and retain exposure until terminal evidence | Assume halt acknowledgement recalled bytes or canceled venue order |
| After halt boundary acknowledgement | New epoch acknowledged or old sender positively isolated | No stale/queued attempt may newly initiate a socket write; already initiated external effects remain reconcilable | Claim that the venue cannot process previously sent bytes |

Fault-injection assertions must inspect both authoritative durable state and an instrumented external-send boundary. A mock adapter result or a database-only state assertion is insufficient for the stale-egress race. Tests must inject process kill, delayed scheduling, network partition, lost commit response, duplicate delivery, reordered ACK/fill, clock skew and concurrent takeover; each run records the exact code, schema, configuration and fault schedule.

## 6. Reference conformance scenarios

The gateway reference now also conditionally guards stale pre-send and adapter-error state updates after recovery; two adversarial tests cover those races. Recovery now uses a serialized transaction and conditional update; a third concurrency test verifies two recovery workers claim one DISPATCHING command exactly once. The 24-test gateway suite and 13-test handover state machine passed run #43591524490 on Python 3.11–3.13 at exact PR HEAD `4f836d0f9d1a43161927331c05e6cc19bb12072b`. This still does not fence network egress. A test-only Python control-plane state machine now exists at `foundation/reference-model/egress-fencing/`. Its 13 unit tests cover transition ordering (HALTING → FENCING → FENCED → RECONCILING → READY_TO_GRANT), stale epoch rejection and fail-closed behavior. GitHub Actions run [#43590804814](https://github.com/PandaGarry/NEXUS/actions/runs/43590804814) passed the suite on Python 3.11–3.13 at exact branch HEAD `a7ee5426077005a6135e9f1b6f1c4044cc41d459`. It does not revoke a network route, terminate a host, validate trusted fence attestations or prove actual egress isolation. A passing state-machine test is not a production fence.

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


### 4.5 Persistence and trusted-egress option analysis (PROPOSED; G1 baselines selected in NX-ADR-008; production qualification open)

This section reconciles the execution/egress design with the G1 technical baseline selected in NX-ADR-008. PostgreSQL 18.7 is selected as the exact G1 persistence evaluation patch, not as a production database/deployment selection. No hosting provider, database topology, key-custody provider or egress deployment product is selected.

#### A. Risk reservation and Command acceptance persistence

| Option | Strengths | Failure/correctness concerns | Disposition |
|---|---|---|---|
| One relational database, one shared transaction across Risk and Command | Superficially simple atomicity | Couples service authority; risks collapsing reservation and command ownership; does not solve venue-side ambiguity; broad transaction can become a distributed service boundary in disguise | Do not make this the conceptual contract |
| PostgreSQL 18.7 evaluation cluster, service-owned schemas/tables and separate local transactions | Mature ACID primitives; one operational database failure domain; clear table ownership; no distributed transaction required for capability hand-off | Shared cluster is still a common availability/administration blast radius; strict ownership and database roles are mandatory; local transactions do not make Risk+Command atomic | G1 evaluation target selected by NX-ADR-008; production topology and threat review remain open |
| Separate authoritative databases per service | Stronger fault/ownership isolation; independent scaling and operational lifecycle | Capability hand-off becomes cross-database messaging; more recovery, backup, observability and idempotency complexity; no atomic commit across stores | Valid later option; likely premature before workload and RPO/RTO evidence |
| Event store/consensus coordination service as primary authority | Can provide ordered durable log and fencing primitives | Operational complexity; semantics vary; still needs transaction boundaries, projections and proof of multi-scope atomicity | Defer until a measured requirement justifies it |

**Candidate transaction model:**

1. Risk owns reservation records, its derived exposure projection, source watermarks and account/child scope-state records. Ledger remains the journal authority and MUST NOT write Risk-owned state directly. Risk consumes Ledger/venue/external exposure events through an idempotent inbox. Reservation commits and projection updates both update the same Risk-owned scope-state record in local Risk transactions. A reservation transaction processes all required pre-provisioned scope rows in deterministic canonical scope-ID order, evaluates the current complete projection and active reservations, writes every reservation and the durable request/result record, updates scope totals, and commits atomically. No capability is returned before commit.
2. Command Coordinator owns command, capability-consumption and outbox records. A separate local transaction validates the capability claims and atomically consumes its unique nonce while inserting the immutable canonical command, reservation reference and outbox row. A unique constraint on the capability/nonce and stable command/request identity is required.
3. The two commits are deliberately ordered, not presented as one distributed ACID transaction. A crash between them leaves a durable reservation that can be recovered or safely expire only after proving dispatch impossible. A lost commit response is resolved by reading the stable request/command identity; never repeat a non-idempotent operation merely because the caller did not receive the response.
4. Multi-scope reservation must be all-or-nothing inside Risk's authoritative transaction. A saga or sequential partial reservation must never produce an approval while any required scope is missing.
5. Ledger journal posting remains its own local atomic transaction with idempotent inbox/event identity; Execution-to-Ledger delivery is durable and replayable, not a cross-service transaction.

**G1 transaction baseline:** PostgreSQL 18.7 SERIALIZABLE is the default G1 evaluation target for Risk reservations/projection updates, combined with a Risk-owned scope-state serialization point, deterministic scope-ID lock/update order, state-version/CAS guards and unique idempotency constraints. SQLSTATE 40001/40P01 requires bounded whole-transaction retry from a fresh snapshot. Same request identity + same digest returns the original result; a different digest conflicts. An unknown commit is resolved by the same durable identity on the authoritative primary; unresolved primary/commit authority keeps the scope HALTED. Exact queries, package provenance/digest, role grants, timeouts, backup/restore/PITR, migration compatibility and concurrency/fault evidence remain open. No correctness claim may rely solely on an application mutex, cache lock or lease.

#### B. Trusted Egress topology

| Option | What it can guarantee | Main limitation | Disposition |
|---|---|---|---|
| DB lease/epoch checked by ordinary worker | Rejects stale database writes when every write is conditional | Cannot stop a paused process that already passed its check from later opening a socket; lease expiry is not external fencing | Rejected as sole egress control |
| Network gateway/proxy that owns the venue connection and credentials | Centralizes the actual socket and can deny worker direct egress; can enforce current generation at the network boundary | Unsafe if it merely checks a token and hands bytes to a credential-bearing worker; proxy HA/takeover still needs single-writer fencing | Required architectural property; candidate mechanism |
| Dedicated credential-owning process/workload with deny-by-default network policy | Clear security boundary; workers cannot sign or reach venue directly; process can be restarted/revoked independently | Process-local epoch is not enough; network policy and identity revocation must be independently enforced and evidenced | Preferred logical boundary |
| Dedicated isolated host/VM per account egress | Stronger containment and a potentially independent power/network fence | More expensive operations; host replacement and recovery are slower; provider control-plane guarantees must be verified | Strong candidate for initial low-availability prototype if simpler isolation cannot be proven |
| Active-active egress for one account | Higher nominal availability | Requires consensus/single-writer and proof that the losing writer cannot still send | Excluded until equivalent fencing evidence exists |

**Candidate topology:** one active account-scoped Egress Authority owns the venue credentials, signing capability and actual venue socket. Dispatcher, strategy, AI, API and adapter workers hold neither venue credentials nor a direct venue route; they submit immutable command/attempt references to Egress. The separate Halt/Egress Gate Coordinator (HEGC) owns the control-plane halt-state and EgressBoundaryAuthorization records and is the sole writer to both. Egress loads the persisted canonical payload, durable reservation and authoritative Risk evidence manifest, then requests a one-use attempt-scoped grant from HEGC. HEGC validates approval consumption, active reservation, command digest, signed valuation_input_vector_id/version, source-specific freshness/clock/quality/correction/drift policy, halt epoch, eligibility revision, attempt identity, dispatcher generation and Egress workload identity in a short transaction that serializes against halt-epoch changes and writes the EgressBoundaryAuthorization. The grant is an opaque persisted reference, not a RiskApprovalCapability. HEGC has no venue credentials or socket; Egress has no direct write access to halt-state or gate-authorization records. The grant commit is the send-authorization linearization point. HEGC grant issuance is idempotent on the stable attempt ID: exact retries return the same persisted grant, changed bindings conflict, and an ambiguous response is recovered by reading the same attempt ID. No replacement attempt or second grant may be created while the first grant may still initiate a socket write. HEGC reads all gate-critical source state from the authoritative primary in the same logical PostgreSQL database at SERIALIZABLE isolation; every invalidating writer must participate in that protocol or a proven shared version/CAS guard. It uses a finite whole-transaction retry budget and same-attempt-ID unknown-commit recovery. Egress consumes the grant through HEGC, not direct table writes. A sender fence without a trusted initiation report leaves the attempt OUTCOME_UNKNOWN and reservation held until venue reconciliation. Egress immediately initiates exactly one socket-write attempt in its single-writer process, with no subsequent source fetch, queue hop or unbounded async preparation. After the socket-write syscall has been invoked/returned, Egress reports the observed initiation to HEGC; a local flag set before the syscall is not proof. If the process pauses/crashes before reporting, HEGC retains the attempt as in-flight until the write is observed or the old sender is positively fenced. The database transaction is never held across network I/O. Updates committed before the grant must be observed; updates committed after it are causally later than the authorized attempt, which remains potentially sent and must be reconciled. Egress MUST NOT fetch replacement market/FX/fee/collateral values or call source services on the dispatch path; if the persisted manifest is unavailable or cannot prove the bound vector admissible, HEGC denies the grant. A newer monotonic market-data tick alone does not invalidate the bound immutable vector unless the applicable policy requires latest data or the bound vector exceeds its freshness/drift limits. Egress never substitutes a newer valuation vector or rebinds the approval; if the bound vector is invalid, it refuses the send and requires Risk re-evaluation.

The test-only Python oracle `foundation/reference-model/egress-fencing/halt_egress_gate.py` and `test_halt_egress_gate.py` model both commit orders, pause-after-gate acknowledgement blocking, positive sender-fence handling, single-use attempt identity and halt-store outage. The model represents ordering with sequential calls; it does not prove real concurrent linearizability, PostgreSQL row-lock behavior, durable state, socket behavior or external fencing.

A halt-epoch commit and the final EgressBoundaryAuthorization commit MUST serialize on the same authoritative halt-state generation. If halt wins, the final gate denies. If the gate wins, that attempt is logically in-flight and cannot be retroactively revoked; the Egress boundary must track it until socket-write initiation is observed or the sender is positively fenced. It cannot acknowledge the later halt epoch while a paused pre-halt authorized attempt could still resume and initiate a write. A request already initiated before acknowledgement may still be processed by the venue and must be reconciled. This does not promise that no bytes can be emitted after the wall-clock halt request; it promises that no old/queued attempt can newly initiate a write after the boundary has acknowledged the halt epoch. Positive fencing of the sender only prevents a future socket initiation. If the initiation report is missing, the attempt may already have caused an external side effect; preserve OUTCOME_UNKNOWN and the full reservation until authoritative venue reconciliation. A fence receipt alone is not proof of DEFINITELY_NOT_SENT.

The control plane may request takeover, but it cannot grant the successor authority merely because a lease expired or an epoch incremented. It must obtain positive evidence from an independently controlled enforcement point that the prior workload identity and network path are revoked, or that the prior host is externally terminated/fenced. The successor receives credentials/route only after that acknowledgement and the account's possibly-sent attempts have entered reconciliation. If the enforcement point is unavailable, ambiguous, or cannot identify the old generation, CREATE remains HALTED. A proxy that checks the epoch and then forwards to a stale credential-bearing worker does not satisfy this design.

#### C. Required proof before selecting a concrete topology

- Prove a worker paused immediately before socket write cannot transmit after revocation.
- Prove no alternate route, DNS/proxy bypass, local credential copy or secondary client can reach the venue.
- Prove old identity/host revocation is acknowledged by an authority independent of the old process.
- Prove a successor cannot receive credentials or route before the old fence is positive.
- Inject control-plane partition, enforcement-point outage, delayed/replayed fence acknowledgement, clock skew, stale process resume, simultaneous takeover and lost database commit response.
- Inspect both authoritative database state and the instrumented real egress boundary; a mock adapter or local token check is insufficient.
- Record exact runtime identity, policy version, network enforcement evidence, host/workload generation and fault schedule for every conformance run.

#### D. Decision boundary

The delegated G1 technical baselines for OD-08/09/10/12 are recorded in [NX-ADR-008](NX-ADR-008-g1-technical-baseline-storage-and-capability-signing.md): deterministic CBOR/SHA-256/COSE Ed25519; PostgreSQL 18.7 as the exact G1 persistence evaluation patch with Risk-owned scope-state serialization and separate local transactions; source-specific freshness; and single-owner, fail-closed emergency defaults. This does **not** select a hosting provider, vault, proxy product, key custody provider, database deployment topology or production availability objective. The single credential/socket-owning Egress workload and independent external fencing remain mandatory design properties. No implementation or live authority is implied.
