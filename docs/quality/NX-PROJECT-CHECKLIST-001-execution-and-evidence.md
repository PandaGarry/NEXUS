# NX-PROJECT-CHECKLIST-001 — Project Execution and Evidence Checklist

**Status:** ACTIVE — living execution register  
**Snapshot:** 2026-11-14  
**Branch:** `engineering/rust-execution-domain-conformance-v0`  
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
| Instrument specification validator | DONE as test-only reference slice | NX-REF-DOMAIN-001; 17 tests passed in run #43593302985 on Python 3.11–3.13; synthetic fixture only, no production authority |
| Dimensional financial types | IN PROGRESS as test-only reference slice | NX-REF-DOMAIN-003; 16 tests passed in run #43593302985 on Python 3.11–3.13 (93 tests per runtime across six isolated suites); reference-only, no production bounds, FX, derivatives, margin or ledger policy |
| Instrument registry | DONE as test-only reference slice | NX-REF-DOMAIN-002; 12 tests passed in run #43593302985 on Python 3.11–3.13; in-memory only, no persistence or distributed writer protocol |
| Exact-decimal oracle | DONE as reference slice only | 11 tests, 15 golden vectors and 1,000 deterministic rational-oracle property cases; exact PR-head CI passed on Python 3.11–3.13; no bounded production numeric type, dimensional wrappers, division or rounding |
| Command-gateway oracle | DONE as test-only slice only | 24 tests; fake adapter; local SQLite concurrency only; conditional state guards cover late ACK, pre-send rejection and adapter-error races; recovery scan is serialized |
| Stale dispatcher fencing | BLOCKED | NX-REF-EXEC-001 counterexample proves stale worker can still reach adapter after recovery |
| Stale dispatcher state overwrite | DONE in reference model only | Conditional transitions reject stale ACK, pre-send rejection and adapter-error writes after recovery; recovery scan is serialized; observations retained; does not stop external send |
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
- [x] Publish a first venue-neutral instrument-spec reference schema, provenance fields and immutable snapshot validator (NX-REF-DOMAIN-001).
- [ ] Qualify NX-REF-DOMAIN-002 registry history semantics against owner-approved identity, version assignment, source precedence, effective-time conflict and persistence decisions.
- [ ] Complete the canonical metadata contract for price bands, leverage tiers, margin brackets, order capabilities and all contract denomination semantics; the current reference slice covers only a narrow subset.
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


## 5. G0/G1 critical-invariant evidence matrix

This is a first-pass matrix, not a certification. "Current evidence" describes only what is actually checked in. Missing implementation evidence remains an explicit gap.

| Critical invariant | Owning artifacts | Required verification | Current evidence | Remaining gap / disposition |
|---|---|---|---|---|
| Financial scalars are exact; no authoritative float | NX-ARCH-003, NX-ADR-005 | Golden, property, overflow and cross-language tests | Python oracle: 15 vectors, 1,000 deterministic rational-oracle cases; CI on Python 3.11–3.13 | Production bounded type, typed units, overflow and cross-language tests OPEN |
| Instrument rules are known/versioned before order validation | NX-ADR-005, ТЗ-NX-001 | Venue fixtures, schema validation, historical-spec tests | Requirements only; Tradoor metadata gaps recorded in NX-RESEARCH-002 | No authoritative NEXUS instrument registry or venue fixture set |
| Market data cannot become LIVE_VALID across sequence gaps | NX-ADR-001/004, NX-IF-004 | Snapshot/delta bridge, sequence-gap, reconnect and replay fault tests | Proposed state machine and contracts | No NEXUS stream implementation or conformance harness |
| Command approval is bound to immutable payload and scope | NX-IF-001, NX-REF-EXEC-001 | Tamper, scope, expiry, replay and one-time-consumption tests | Python/SQLite fake model; 21 deterministic tests | Test HMAC only; production signer, canonical serialization and key custody OPEN |
| Command is durable before external side effect | NX-ADR-002, NX-REF-EXEC-001 | Crash-before/after-commit and dispatch-boundary tests | Local SQLite transaction model and fault injection | No production database/transaction semantics; no independent durable egress |
| Ambiguous send is never blindly retried | NX-ADR-002, NX-IF-004, NX-REF-EXEC-001 | Timeout, crash-after-send, restart and duplicate-attempt tests | Model preserves OUTCOME_UNKNOWN and denies redispatch | Venue reconciliation and private event coverage not implemented |
| Stale dispatcher cannot send after losing authority | NX-REF-EXEC-002, NX-IF-005 | Host/network fencing and adversarial stale-worker tests against actual egress | Counterexample proves current unfenced adapter can still be called; late ACK overwrite is rejected; test-only control-plane handover model added (13 tests; CI run #43590804814 passed on Python 3.11–3.13; actual network fencing remains absent) | **BLOCKER:** no concrete independently enforced egress fence |
| Risk reservations prevent concurrent over-allocation | NX-IF-002, ТЗ-NX-005 | Atomic multi-scope reservation, stale snapshot and concurrency tests | Single pre-created reservation fixture and approval-consumption race | No exposure calculator or production reservation service |
| Fills post exactly once to a balanced ledger | NX-IF-003, ТЗ-NX-006 | Inbox dedupe, atomic journal, correction/bust and replay tests | Contract design only | No ledger implementation or accounting fixtures |
| Recovery waits for complete source evidence | NX-IF-004, NX-ADR-004 | Watermark, freshness, quarantine and restart-barrier tests | Contract/state-machine design only | No recovery barrier runtime or venue-specific completeness proof |
| AI/strategy cannot bypass Risk or access venue credentials | NX-SEC-001, NX-IF-001, NX-ARCH-001 | Network isolation, secret access and policy-bypass tests | Threat model and architecture requirements | No deployed trust boundary, vault, signer or isolation tests |
| Halt/emergency operations are scoped and fail closed | NX-IF-005, ТЗ-NX-004/005 | Halt epoch, stale worker, cancel/fill race and resume authorization tests | Proposed operation matrix and halt contracts | No operator workflow, venue capability certification or runtime implementation |

**D4 disposition:** IN PROGRESS. This matrix makes the critical evidence gaps explicit; it does not close them. Every row must reach a verified or explicitly deferred disposition before the relevant readiness gate can pass.

## 6. Ordered active queue

| Priority | Action | Status | Completion evidence |
|---|---|---|---|
| P0 | Correct documentation contradictions, stale counts and CI references | IN PROGRESS | Updated status, roadmap, index and changelog on one exact HEAD |
| P1 | Complete adversarial stale-egress analysis and concrete fencing design | IN PROGRESS | NX-REF-EXEC-002 plus threat/failure matrix; no fake safety pass |
| P2 | Strengthen numeric reference oracle with deterministic property tests and additional negative vectors | IN PROGRESS | 1,000 seeded rational-oracle cases added; exact PR-head CI run #43590395882 passed on Python 3.11–3.13; broader fuzz/cross-language vectors remain open |
| P3 | Produce G0D evidence matrix and D1–D8 disposition | OPEN | Checklist + review doc + commit-specific evidence |
| P4 | Resolve PR integration sequence and owner review | BLOCKED | Explicit integration plan and required owner decisions |
| P5 | Prototype workspace readiness | BLOCKED | G0D/G1 PASS and explicit authorization for safe read-only/paper prototype |

## 7. Change-control and documentation rules

For every substantive code or architecture change:
1. Update the owning ADR/spec/reference-conformance document in the same work package.
2. Update this checklist only when status changes and attach evidence.
3. Update `docs/01-project-status.md`, `docs/02-roadmap.md`, architecture indexes and `CHANGELOG.md` when their statements are affected.
4. Record exact branch, commit SHA, CI run URL, runtime matrix and test counts.
5. Never copy an old CI result onto a newer SHA without stating that it is historical.
6. Keep PRs Draft until the bounded review is complete; do not merge into the default branch without the required approval.
7. No secret material, live credentials, private account data or personal financial identifiers in Git.

## 8. Latest domain-kernel increment

- Added `AssetAmount`, `Money`, `Price`, `Notional` and instrument-scoped `ContractCount`, all backed by `ExactDecimal`.
- Only same-dimension/same-unit addition and subtraction are supported. `Price × matching AssetAmount` yields quote-denominated `Notional`; contract counts cannot be treated as asset quantity.
- 16 dedicated tests passed in GitHub Actions run [#43593302985](https://github.com/PandaGarry/NEXUS/actions/runs/43593302985) on Python 3.11, 3.12 and 3.13. Historical six-suite evidence only: 11 decimal, 24 gateway, 13 egress, 17 instrument-spec, 12 registry and 16 dimensional-type tests (93 per runtime; 279 matrix executions). The latest seven-suite run also includes 16 instrument-unit tests (109 per runtime; 327 matrix executions).
- This does not resolve `InstrumentSpec.quantity_unit` mapping, derivative formulas, FX, margin, fees, P&L, production numeric bounds or accounting policy.

## 9. Explicit non-authorizations

This checklist does not authorize:
- real exchange credentials, private account connectivity or order placement;
- withdrawals, transfers or custody;
- numeric risk-limit selection or relaxation;
- production deployment, automatic cancel-all or flatten;
- merging architecture changes to the default branch;
- commercial, multi-tenant or third-party capital management.

**Current overall disposition: FOUNDATION IN PROGRESS; PROTOTYPE READINESS BLOCKED; LIVE NOT AUTHORIZED.**

## 10. Instrument quantity-unit semantics increment

- Added `InstrumentUnitModel`, pinned to exact `InstrumentSpec` version and identity.
- Spot maps explicitly to base-asset amount; linear contracts use base-asset units per contract; inverse contracts use quote-asset units per contract.
- QUANTO is explicitly unsupported; inverse base exposure remains blocked until exact division and rounding/precision policy exist.
- Venue `quantity_unit` remains opaque: quantity kind and multiplier dimension are caller-declared, never inferred from a string.
- Dedicated 16-test suite and CI workflow step added. GitHub Actions run [#43593795698](https://github.com/PandaGarry/NEXUS/actions/runs/43593795698) passed exact HEAD `ba8df9def72bff82625669bc236430bb8d21592d` on Python 3.11–3.13: 109 tests per runtime / 327 matrix executions across seven isolated suites.


## 11. Exact rational division and quantization increment

- Added `ExactRational` reduced numerator/positive-denominator representation.
- Decimal division returns an exact rational and never silently truncates or rounds; division by zero is rejected.
- Exact conversion to finite decimal succeeds only for denominators containing factors 2 and/or 5.
- Quantization requires an explicit `RoundingMode`; seven modes are covered for positive and negative inputs.
- Added 1,000 deterministic rational quantization property cases and language-neutral division golden vectors.
- Dedicated 18-test suite added. GitHub Actions run [#43594118145](https://github.com/PandaGarry/NEXUS/actions/runs/43594118145) passed exact PR HEAD `a46b49a2cbb7a5960ce483f93a736a3fbc945554` on Python 3.11–3.13: 127 tests per runtime / 381 matrix executions across eight isolated suites.
- No operation-specific trading/accounting rounding policy is approved.


## 12. Inverse contract rational exposure increment

- Added `RationalAssetAmount`, preserving inverse base exposure as a reduced rational rather than rounding to a finite decimal.
- Inverse exposure uses quote notional / quote-per-base price and requires settlement in the base asset for this reference model.
- Exact finite-decimal conversion is conditional; quantization requires explicit scale and rounding mode.
- Synthetic tests cover terminating and non-terminating outcomes, explicit quantization and settlement mismatch.
- Dedicated suite is part of the Python 3.11–3.13 CI workflow; current-head evidence pending.


## 13. Bounded numeric context and canonical scalar wire increment

- Added BoundedNumericContext as a separate preflight/admission layer; the arbitrary-precision oracle remains unchanged.
- NumericLimits are mandatory and caller-supplied; no default or production profile is selected. Zero scale and zero power-of-ten budgets are valid; input/digit/intermediate budgets must be positive.
- Added preflight guards for input characters, coefficient digits, scale, scale-alignment powers, multiplication scale/growth, division pre-reduction numerator/denominator, rational bounds and quantization expansion.
- Added bounded compare, step divisibility, exact terminating conversion and canonical wire parsing.
- Added nxd1 decimal and nxr1 rational encodings with strict canonical grammar, normalized/reduced forms, version tags and mandatory max_chars parsing.
- Conservative division preflight may reject a quotient whose unreduced values exceed budget even if GCD reduction would fit; this behavior is documented.
- Dedicated bounded numeric (32 tests) and numeric wire (11 tests, including shared language-neutral vectors) suites passed PR run [#43595449902](https://github.com/PandaGarry/NEXUS/actions/runs/43595199511) on exact PR HEAD `6200bae99e9b7ce865487a40312d0074c0e2a276`, Python 3.11–3.13; full matrix 172 tests per runtime / 516 executions.
- No production limits, fixed-width integer choice, resource-safety proof, Rust implementation or cross-language conformance is approved.

## 14. Operation-specific financial rounding and valuation increment

- [x] Publish NX-REF-DOMAIN-009 as a proposed design contract enumerating tick/lot, minimum notional, fees, funding, realized/unrealized P&L, margin, liquidation, FX/collateral valuation and Ledger posting boundaries.
- [x] Separate exact mathematical invariants from venue/product/account semantics and owner-controlled accounting policy.
- [x] Define evidence classes, provenance requirements, calculation pipeline, fixture schema and venue qualification dossier.
- [x] Cross-review NX-REF-DOMAIN-009 against NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006; no blocking contradiction found, with owner/venue gaps retained.
- [ ] Owner review of inventory/position matching, realized P&L, fee/funding treatment, FX/collateral and accounting rounding.
- [ ] Select and legally qualify exact venue/product/account before filling venue-specific formulas or fixtures.

**Disposition:** DESIGN DRAFT PUBLISHED; G0/G1 remain BLOCKED. No generic production rounding mode, fee/funding formula, margin/liquidation model, FX source, numeric limit or accounting method is selected. No code or financial runtime was added.


### 14.1 Cross-document review result

Reviewed NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006 at their exact branch blob SHAs recorded in NX-REF-DOMAIN-009. Their authority boundaries align: Instrument Specification owns immutable product semantics; Risk consumes qualified valuation/exposure; Ledger owns authoritative accounting; Execution supplies immutable fill/account evidence. No blocking contradiction was found. Owner accounting decisions, venue qualification and production formulas remain OPEN/BLOCKED.


### 14.2 Exact-head regression evidence

- GitHub Actions run [#43596156300](https://github.com/PandaGarry/NEXUS/actions/runs/43596156300) passed exact PR HEAD `546a0e74fa055acba2c2de6694c1ba43f65debf5` on Python 3.11, 3.12 and 3.13.
- Ten existing reference suites passed on each runtime: 11 exact-decimal, 24 execution-gateway, 13 egress-handover, 17 instrument-specification, 12 instrument-registry, 16 dimensional-types, 18 instrument-units, 18 exact-division, 32 bounded-numeric and 11 numeric-wire tests (172 per runtime / 516 executions).
- This is regression evidence for pre-existing test-only reference models. It does not test or validate the proposed financial-operation policies, and it is not production/runtime/venue conformance evidence.

## 15. Venue-neutral financial math fixture increment

- [x] Add language-neutral, synthetic exact vectors for spot notional, explicitly mapped linear contract notional, inverse rational base exposure and partial-fill weighted-average arithmetic.
- [x] Add test-only conformance tests with independent `fractions.Fraction` checks for selected outputs.
- [x] Preserve repeating inverse exposure as a rational; assert that exact decimal conversion rejects a non-terminating result rather than rounding.
- [x] Add the suite to the Python 3.11/3.12/3.13 reference workflow.
- [x] Verify exact PR-head code/test commit and inspect all three runtime logs: run [#43596710483](https://github.com/PandaGarry/NEXUS/actions/runs/43596710483), commit `9d0bf48c3ddc66facf408d60b1c64beb971eebb6`, passed 179/179 tests on each of Python 3.11, 3.12 and 3.13.
- [ ] Add cross-language implementation only after a production-language contract and resource profile are approved.

**Disposition:** TEST-ONLY MATHEMATICAL FIXTURES; no venue/account semantics or production financial policies are qualified. Fees, funding, P&L, margin, liquidation, FX and accounting remain BLOCKED/OWNER-DECISION as defined by NX-REF-DOMAIN-009. G0/G1 unchanged.

### 15.1 Initial CI evidence

- Push run [#43596630780](https://github.com/PandaGarry/NEXUS/actions/runs/43596630780) passed exact commit `af7949f183389c25fa6ce5c4ac3648c1dd4ae851` on Python 3.11/3.12/3.13.
- Each runtime: 179 tests across 11 isolated suites, including 7 new financial math fixture tests.
- All three jobs completed successfully. This is test-only Python reference evidence; a fresh run on the final PR head is required after documentation close-out.

### 15.2 Expanded deterministic property evidence

- [x] Add 250 seeded spot-notional products checked against `fractions.Fraction`.
- [x] Add 200 seeded partial-fill permutation/partition invariance cases.
- [x] Add 200 seeded inverse exposure identity cases.
- [x] GitHub Actions run [#43596851904](https://github.com/PandaGarry/NEXUS/actions/runs/43596851904) passed exact code/test commit `0f0b44e927aacf67d6f7a5678b160b3e3c6088e0`: 182 tests per runtime on Python 3.11/3.12/3.13; all three jobs successful.
- [ ] Cross-language conformance remains deferred until production language/runtime and resource limits are approved.

## 16. Russia jurisdiction and first-venue eligibility gate

- [x] Publish NX-RESEARCH-009 with Federal Law No. 282-FZ, CBR guidance, Directive 7441-U, domestic operator/derivative candidates and foreign venue screening.
- [x] Record Directive 7441-U effective date (2026-11-17), RUB 300,000 annual cumulative broker-acquisition cap for non-qualified residents, and BTC/ETH/USDT eligible-admission list; crypto-exchange organization applicability remains a legal question.
- [x] Mark NX-RESEARCH-003/004 historical and superseded for current live-venue selection.
- [x] Draft NX-ADR-007 with immutable VenueEligibilityRecord, fail-closed activation states, independent Risk authorization and egress-bound eligibility epoch fencing.
- [x] Perform bounded consistency review against NX-IF-001..005, NX-SEC-001 and NX-ADR-002; no blocking authority-boundary contradiction found.
- [ ] Owner/legal acceptance of ADR-007 and qualified legal opinion on Articles 30–32 / Article 30(2).
- [ ] Confirm qualified-investor status and T-Invest product/API eligibility using authenticated account evidence; no orders.
- [ ] Confirm T-Invest Lab crypto service and API availability in writing.
- [x] Add test-only NX-REF-VENUE-001 conformance evaluator and 28 fail-closed tests; exact-head CI run 43598506837 passed 210 tests/runtime on Python 3.11/3.12/3.13.
- [x] Add NX-REF-VENUE-002 test-only dispatch/suspension race model and 21 tests; run 43599182263 passed 231 tests/runtime across Python 3.11/3.12/3.13.
- [ ] Design production evidence authentication/signing, trusted time, persistence, distributed revocation, cross-process egress fencing, reviewer roles and crash recovery before implementation.

**Disposition:** FIRST VENUE BLOCKED. No venue selected, no account/API credentials connected, no orders/transfers/deposits/withdrawals, and no live trading authorized. All foreign venues remain RESEARCH_ONLY.

## 17. Rust execution and cross-language conformance work package

**Owning artifact:** [NX-ARCH-004](../architecture/NX-ARCH-004-rust-execution-cross-language-conformance.md)  
**Tracking:** GitHub Issue #15  
**Branch:** `engineering/rust-execution-domain-conformance-v0`  
**Status:** IN PROGRESS — documentation design only; implementation readiness remains BLOCKED.

- [x] Publish NX-ARCH-004 as a PROPOSED architecture design with explicit non-authorizations.
- [x] Define NEXUS-owned command, Risk, durable outbox, trusted egress, adapter, Ledger and recovery authority boundaries.
- [x] Define language-neutral conformance expectations and rejection-class comparison.
- [x] Define crash/replay/duplicate/partial-fill/cancel-fill/eligibility-suspension/stale-worker failure matrix.
- [ ] Review RUST-01..06 with the owner; publication is not acceptance.
- [x] Cross-review NX-ARCH-004 against NX-IF-001..005, NX-ARCH-003, NX-ADR-002/005/007 and NX-SEC-001; no remaining blocking authority-order contradiction found in the reviewed documentation path.
- [ ] Approve production Rust toolchain/workspace only after applicable G0D/G1 gates.
- [ ] Implement Rust pure-domain slice and run existing golden vectors.
- [ ] Add Python/Rust differential and bounded-resource tests under an approved numeric profile.
- [ ] Prove a concrete independently enforced egress fence against stale-worker network-send attempts.
- [ ] Record exact commit SHA, toolchain, lockfile and CI evidence before claiming conformance.

**Disposition:** no Rust source, Cargo workspace, production numeric profile, venue adapter, trusted egress, credentials or live capability added. Prototype readiness BLOCKED; live NOT AUTHORIZED.


### 17.1 Cross-contract ordering closure — 2026-11-14

- [x] Correct NX-ADR-002 so durable `PRE_DISPATCH_RESERVATION` commits across all affected scopes before Risk issues `RiskApprovalCapability`.
- [x] Require the Command Coordinator to atomically consume the single-use approval while committing the canonical command, reservation reference and outbox record.
- [x] Clarify the durable pre-egress attempt marker: it conservatively moves exposure to `DISPATCH_OUTCOME_UNKNOWN`; a crash before the socket write remains potentially sent until authoritative reconciliation.
- [x] Align NX-ARCH-004 sequence and cross-contract review note with NX-IF-001, NX-IF-002, NX-IF-005, NX-ADR-002 and NX-SEC-001.
- [ ] Obtain owner/architecture/security acceptance; documentation harmonization is not implementation evidence.

**Evidence boundary:** documentation-only closure. No transaction store, signer, dispatcher, network fence, venue adapter or runtime behavior was implemented or tested by this change.


## 18. Language-neutral conformance fixture and runner design

**Owning artifact:** [NX-ARCH-005](../architecture/NX-ARCH-005-language-neutral-conformance-fixture-and-runner.md)  
**Tracking:** GitHub Issue #15  
**Status:** PROPOSED — design only; no common schema or runner implemented.

- [x] Inventory existing decimal, rational, numeric-wire, financial-math and instrument-spec fixture formats.
- [x] Verify current repository has no Cargo manifest, Rust toolchain file, Rust source tree or Rust runner; Rust implementation remains gated.
- [x] Define a proposed common envelope, tagged VALUE/REJECT outcomes, stable error-class families and strict typed comparison rules.
- [x] Define fixture/suite versioning, migration rules, deterministic runner responsibilities and CI evidence fields.
- [x] Classify each existing v1 fixture family as structural, semantic-annotation-required or new-expected-behavior-required; preserve legacy files unchanged.
- [x] Define initial stable operation IDs and canonical inputs/results for decimal, rational, numeric-wire and dimensional-math fixtures.
- [x] Identify the current numeric-wire exception granularity gap; do not infer stable rejection classes from message strings.
- [x] Add catch-compatible typed numeric-wire exception subclasses with stable machine-readable classes and dedicated tests; retain the `NumericWireError` base contract.
- [x] Update NX-ARCH-005 operation registry and reference-model README to enumerate all stable numeric-wire rejection classes.
- [ ] Review and accept operation registry and error mapping before writing the executable schema.
- [ ] Owner/architecture review of NX-ARCH-005 and stable rejection taxonomy.
- [ ] Map all existing v1 fixtures to the normalized envelope without changing legacy files.
- [ ] Publish and validate a machine-readable schema after dependency-policy review.
- [ ] Implement a Python-only normalized runner; keep current direct unit tests intact.
- [ ] Implement Rust runner and differential CI only after G0D/G1 approval.

**Disposition:** design only. Existing fixture files and current Python workflows remain unchanged. No cross-language conformance is claimed.
