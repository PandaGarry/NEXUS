# NX-PROJECT-CHECKLIST-001 — Project Execution and Evidence Checklist

**Status:** ACTIVE — living execution register  
**Snapshot:** 2026-11-14  
**Branch:** `foundation/domain-kernel-reference-v0`  
**Scope:** NEXUS v1 foundation, documentation close-out, safe reference work and readiness-controlled implementation.

This checklist is the operational index for the next actions. It does not replace ADRs, specifications, owner decisions or readiness gates. Each checked item must point to a durable artifact or commit-specific evidence. A document being published is not the same as a decision being accepted; a test passing in a reference model is not production verification.

## 1. Status vocabulary

- `DONE` — exit criteria met and evidence linked.
- `IN PROGRESS` — bounded work is actively being changed.
- `BLOCKED` — cannot safely proceed; blocker and required evidence are named.
- `DEFERRED` — deliberately moved to a later gate with rationale.
- `OPEN` — not started or not sufficiently evidenced.

Never infer DONE from prose, a draft document, a green CI run on a different SHA, or an upstream project's feature list.

## 2. Current verified baseline

| Item | Current state | Evidence / limitation |
|---|---|---|
| Product scope | DONE for bounded v1 scope | OD-01 and OD-04 accepted; OD-15 partially accepted. See NX-OWNER-DECISIONS-001 |
| PR #10 | OPEN / Draft / unmerged | Current branch contains reference models and docs; not a production implementation |
| Exact-decimal oracle | DONE as reference slice only | 11 tests, 15 golden vectors and 1,000 deterministic rational-oracle property cases; exact PR-head CI passed on Python 3.11–3.13; no bounded production numeric type, dimensional wrappers, division or rounding |
| Command-gateway oracle | DONE as test-only slice only | 21 tests; fake adapter; local SQLite concurrency only |
| Stale dispatcher fencing | BLOCKED | NX-REF-EXEC-001 counterexample proves stale worker can still reach adapter after recovery |
| Late ACK state overwrite | DONE in reference model | Conditional state transition rejects stale ACK and records observation; does not stop external send |
| Egress fencing design | IN PROGRESS / PROPOSED | NX-REF-EXEC-002; no concrete provider, host fence, proxy or credentials boundary implemented |
| Prototype readiness | BLOCKED | G0D and G1–G9 remain blocked as applicable |
| Live trading | NOT AUTHORIZED | No credentials, orders, risk-limit values, deployment or live execution |

## 3. Foundation close-out packages (G0D)

| ID | Work package | Status | Required exit evidence |
|---|---|---|---|
| D1 | Integrate documentation PR sequence and resolve PR #8/#9 sibling relationship | BLOCKED | Explicit PR integration graph; no silently omitted banking research; all indexes and base branches reconciled |
| D2 | Cross-document architecture and status consistency | IN PROGRESS | No contradictory decision status, stale test counts, stale CI SHA or broken architecture links |
| D3 | Numeric/domain kernel | IN PROGRESS | Golden vectors, deterministic property tests, explicit unsupported operations; production bounds/rounding remain a later owner/architecture decision |
| D4 | Quality/evidence matrix | IN PROGRESS | Every G0/G1-critical invariant mapped to artifact, test type, evidence owner and acceptance gate |
| D5 | Persistence and operations | BLOCKED | Storage/transaction boundary, backup/restore, observability, RPO/RTO and deployment decisions either evidenced or explicitly deferred |
| D6 | Security controls mapping | OPEN | Each critical NX-SEC-001 threat mapped to concrete control, verification test and incident response owner |
| D7 | Venue qualification | BLOCKED | Written eligibility for exact nationality/residence/product/account/API and verified capability matrix; otherwise keep venue-neutral |
| D8 | Owner review | IN PROGRESS | Accepted decisions limited to OD-01/04 and partial OD-15; all other owner choices remain open/deferred by gate |

## 4. Technical workstreams

### W1 — Market data and instrument truth
- [ ] Publish a venue-neutral canonical instrument-spec schema and provenance/version rules.
- [ ] Define exact metadata fields: tick, quantity step, min/max quantity, min notional, contract type/value/multiplier, settlement, price bands, leverage tiers and status.
- [ ] Build venue fixtures only from official documented responses; preserve unknown/unsupported fields explicitly.
- [ ] Define stream identity, sequence scope, snapshot bridge, gap detection, stale/degraded states and replay evidence.
- [ ] Keep Tradoor public-data adapters as research candidates only; do not infer private execution capability.

**Exit:** NX-ADR-001/004/005 and ТЗ-NX-001 have consistent schemas, fixtures and conformance tests; unknown metadata fails closed.

### W2 — Professional analytics
- [ ] Define canonical trade aggressor semantics and source-quality labels.
- [ ] Specify Footprint aggregation, Delta/CVD, imbalance, stacked imbalance, DOM, Tape and profile formulas.
- [ ] Create independent golden datasets and hand-calculated fixtures.
- [ ] Define replay determinism and data-quality degradation behavior.
- [ ] Benchmark rendering/performance only after correctness fixtures exist.

**Exit:** ТЗ-NX-002 formula decisions and golden tests are reviewed; visual similarity alone is not acceptance.

### W3 — Quant and simulation
- [ ] Keep research, validation and untouched test data separated.
- [ ] Specify purging/embargo, walk-forward, multiple-testing accounting and experiment provenance.
- [ ] Qualify simulation fidelity per data segment and venue.
- [ ] Compare HFTBacktest/LEAN/ABIDES only against a named use case; no engine selection by popularity.
- [ ] Defer a separate NX-ADR-006 while NX-ADR-003 already contains the required validation protocol; reopen only if a distinct governance decision emerges.

**Exit:** ТЗ-NX-003 and NX-ADR-003 have owner-reviewed acceptance criteria and reproducible experiment fixtures.

### W4 — Execution, recovery and egress
- [ ] Preserve immutable command/approval/reservation/attempt identities.
- [ ] Keep unknown outcomes and exposure reservations until venue evidence resolves them.
- [ ] Implement/test state-version and authority-epoch conditional mutations in reference model.
- [ ] Specify an independently enforced egress fence; database lease or local token alone is insufficient.
- [ ] Test stale worker pause/resume, host partition, supervisor failover, delayed ACK, duplicate venue events and crash-after-send.
- [ ] Prove workers/AI cannot access venue credentials or direct private venue egress.
- [ ] Qualify venue client-order-ID/idempotency and reconciliation semantics separately.

**Exit:** NX-REF-EXEC-002 is converted into a concrete, reviewed design and adversarial tests pass against the actual egress boundary. Until then CREATE dispatch is not production-safe.

### W5 — Independent risk and ledger
- [ ] Define dimensional financial types and exact contract formulas.
- [ ] Define exclusive exposure buckets and atomic reservations.
- [ ] Define fill identity, deduplication, corrections/busts and balanced journal posting.
- [ ] Define risk transfer only after durable ledger posting and projection watermark.
- [ ] Keep numeric hard limits owner-controlled; never invent defaults.

**Exit:** NX-IF-001..005, ТЗ-NX-004..006 and ledger/risk acceptance fixtures agree; no unresolved double-count/omission path.

### W6 — Security and operations
- [ ] Map every critical threat to prevention, detection, response and test evidence.
- [ ] Choose credential vault/signing boundary only after threat and deployment review.
- [ ] Define operator access, MFA/step-up, halt/resume and break-glass governance.
- [ ] Define backups, restore drills, audit retention, observability and incident response.
- [ ] Verify dependency/license inventory, including Tradoor AGPL-3.0-only implications.

**Exit:** NX-SEC-001 controls matrix and operations runbooks have review evidence; no critical threat is left with an implicit mitigation.

### W7 — Implementation workspace and clients
- [ ] Do not create a production workspace until G0D/G1 readiness conditions and required owner reviews pass.
- [ ] Then establish pinned toolchain, reproducible builds, dependency policy, CI, code ownership and security scanning.
- [ ] Keep Desktop and Web as clients of one backend and authoritative state.
- [ ] Keep autonomous runtime server-side; UI/browser availability must not be required for execution.
- [ ] Build read-only/paper first; live is a separate authorization gate.

**Exit:** reproducible workspace and architecture conformance evidence; no production or live capability implied.

## 5. Ordered active queue

| Priority | Action | Status | Completion evidence |
|---|---|---|---|
| P0 | Correct documentation contradictions, stale counts and CI references | IN PROGRESS | Updated status, roadmap, index and changelog on one exact HEAD |
| P1 | Complete adversarial stale-egress analysis and concrete fencing design | IN PROGRESS | NX-REF-EXEC-002 plus threat/failure matrix; no fake safety pass |
| P2 | Strengthen numeric reference oracle with deterministic property tests and additional negative vectors | IN PROGRESS | 1,000 seeded rational-oracle cases added and exact PR-head CI passed on Python 3.11–3.13; broader fuzz/cross-language vectors remain open |
| P3 | Produce G0D evidence matrix and D1–D8 disposition | OPEN | Checklist + review doc + commit-specific evidence |
| P4 | Resolve PR integration sequence and owner review | BLOCKED | Explicit integration plan and required owner decisions |
| P5 | Prototype workspace readiness | BLOCKED | G0D/G1 PASS and explicit authorization for safe read-only/paper prototype |

## 6. Change-control and documentation rules

For every substantive code or architecture change:
1. Update the owning ADR/spec/reference-conformance document in the same work package.
2. Update this checklist only when status changes and attach evidence.
3. Update `docs/01-project-status.md`, `docs/02-roadmap.md`, architecture indexes and `CHANGELOG.md` when their statements are affected.
4. Record exact branch, commit SHA, CI run URL, runtime matrix and test counts.
5. Never copy an old CI result onto a newer SHA without stating that it is historical.
6. Keep PRs Draft until the bounded review is complete; do not merge into the default branch without the required approval.
7. No secret material, live credentials, private account data or personal financial identifiers in Git.

## 7. Explicit non-authorizations

This checklist does not authorize:
- real exchange credentials, private account connectivity or order placement;
- withdrawals, transfers or custody;
- numeric risk-limit selection or relaxation;
- production deployment, automatic cancel-all or flatten;
- merging architecture changes to the default branch;
- commercial, multi-tenant or third-party capital management.

**Current overall disposition: FOUNDATION IN PROGRESS; PROTOTYPE READINESS BLOCKED; LIVE NOT AUTHORIZED.**
