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
- [x] Specify strict JSON ingestion, duplicate-key/non-finite/float rejection, UTF-8 handling, raw-byte fixture hashing and explicit runner resource limits.
- [ ] Review and accept operation registry and error mapping before writing the executable schema.
- [ ] Owner/architecture review of NX-ARCH-005 and stable rejection taxonomy.
- [ ] Map all existing v1 fixtures to the normalized envelope without changing legacy files.
- [ ] Publish and validate a machine-readable schema after dependency-policy review.
- [ ] Implement a Python-only normalized runner; keep current direct unit tests intact.
- [ ] Implement Rust runner and differential CI only after G0D/G1 approval.

**Reference-model evidence:** workflow [#43602394909](https://github.com/PandaGarry/NEXUS/actions/runs/43602394909) passed exact HEAD `e126f67b5779969ad3cffb67cfbb505760668518`: 13 isolated suites / 232 tests on each of Python 3.11, 3.12 and 3.13 (696 successful executions). The numeric-wire suite now has 12 tests, including stable error-class mapping.

**Disposition:** design only. Existing fixture files and current Python workflows remain unchanged. No normalized schema, validator, Python runner or cross-language conformance is claimed.

## 14. NX-ARCH-005 cross-review correction (2026-11-14)

- Corrected the illustrative fixture envelope: removed a trailing comma so the example is valid strict JSON.
- Audited the proposed operation registry against the current reference-model surface. Decimal/rational operations map to `nexus_decimal.py`; numeric-wire operations map to `numeric_wire.py` with explicit profile-bounded `max_chars`.
- Clarified that financial fixture labels for linear-contract notional, inverse exposure and partial-fill aggregation are fixture-level targets, not currently callable reference operations. They remain non-executable migration targets until adapters, reference implementations and tests exist. `Price.notional_for` is the currently evidenced spot primitive.
- Clarified that instrument-spec validation remains deferred as a normalized executable operation.
- Recorded that numeric-wire classes are machine-readable; decimal/domain mappings outside the explicit typed classes still require operation-aware review. `NumericLimitExceeded` requires reviewed mapping to `NUMERIC.RESOURCE_LIMIT`; `DimensionMismatch` must not be classified by parsing exception text.
- No fixture schema, validator, runner, Rust code or production numeric profile was created. NX-ARCH-005 remains PROPOSED and owner-review gated.

## Financial reference-surface audit correction (2026-11-14)

The earlier NX-ARCH-005 cross-review note incorrectly stated that linear-contract and inverse-exposure callable references were absent. A second direct inspection of `instrument_units.py` and `test_financial_math_fixtures.py` supersedes that statement: spot (`Price.notional_for`), linear (`InstrumentUnitModel.linear_base_exposure` / `linear_notional`) and inverse (`inverse_quote_notional` / `inverse_base_exposure`) paths have executable reference coverage. Inverse exposure remains rational. Partial-fill weighted-average aggregation is tested, including permutation/partition invariance, but is currently inline in the test module and should be extracted as a named pure oracle before becoming a reusable normalized operation.

The exact decimal oracle is arbitrary precision; `BoundedNumericContext` wraps it with mandatory explicit synthetic `NumericLimits`. Map `NumericLimitExceeded` by exception type to the candidate `NUMERIC.RESOURCE_LIMIT`, never by message text. Keep malformed API arguments (e.g. negative/boolean quantization scale or invalid rounding mode) separate from valid mathematical inexactness. No production numeric profile is implied.


### 18.1 Partial-fill arithmetic extraction — 2026-11-14

- [x] Extract the weighted-average partial-fill calculation into `financial_aggregation.aggregate_partial_fills` as a named test-only reference operation.
- [x] Preserve dimensional output types: base `AssetAmount`, quote `Notional`, exact rational average.
- [x] Add explicit tests for empty input, base/quote dimension mismatch and non-terminating averages; retain seeded permutation/partition invariance through the extracted callable.
- [ ] Add the operation to normalized fixtures only after NX-ARCH-005 owner review and schema/runner approval.

**Boundary:** arithmetic over supplied typed values only; no venue fill validation, fees, funding, P&L, accounting or rounding policy. No production code or authorization is added.

- [x] Pin the zero-total-quantity boundary: non-empty signed inputs with zero aggregate quantity raise typed `DivisionByZero`; empty input and malformed argument types remain separate input-contract failures.


### 18.2 Reference exception mapping audit — 2026-11-14

- [x] Audit typed numeric, bounded-context, dimensional-domain and financial-aggregation exception surfaces against actual callable implementations.
- [x] Separate mathematical rejection candidates from malformed API/type/parameter failures; prohibit exception-message parsing.
- [x] Record candidate mappings for invalid decimal syntax, exactness, division by zero, invalid step, resource limits, unit mismatch and unsupported unit operations in NX-ARCH-005.
- [ ] Owner approval of the stable rejection taxonomy, including unresolved invalid-domain-value and identity-mismatch cases.
- [ ] Implement normalized adapters only after the operation registry and rejection taxonomy are approved.

**Disposition:** audit only; proposed mappings are not accepted wire behavior. No schema, validator, runner or production adapter is authorized.

- [x] Harden `ExactDecimal.is_multiple_of` to reject non-`ExactDecimal` step arguments with explicit `TypeError`, not incidental attribute access failure; add regression coverage.


### 18.3 Cross-contract pre-egress ordering clarification — 2026-11-14

### 18.4 Reservation/dispatch finding disposition refresh — 2026-11-14

- [x] Refresh NX-ARCH-REVIEW-001 F-02 to distinguish the original documentation gap from the subsequently published NX-IF-001 / NX-IF-002 / NX-ADR-002 design ordering.
- [x] Record the design-level sequence: reservation durable before approval; single-use approval consumption atomic with command/outbox commit; reservation retained through ambiguous outcome.
- [ ] Owner acceptance, concrete transaction/isolation selection, crash/replay/concurrency proof, reservation lifecycle evidence and independently enforced egress-fence proof remain open.

**Disposition:** F-02 is partially resolved as a documentation/design contract only. No runtime transaction, distributed atomicity or egress guarantee is claimed.


- [x] Clarify IF-002 so the durable pre-egress attempt marker is committed before any external network side effect.
- [x] Explicitly state that the marker moves exposure to `DISPATCH_OUTCOME_UNKNOWN` but is not proof that bytes were sent.
- [x] Preserve the full conservative reservation until authoritative outcome/reconciliation; align review note with ADR-002, IF-001, IF-003, IF-004 and IF-005.
- [ ] Select and prove the production transactional store, dispatcher fencing and trusted-egress enforcement model.
- [ ] Implement crash/partition/stale-worker fault injection after owner/security review.

**Disposition:** documentation ambiguity resolved; runtime and distributed-safety proof remain NOT IMPLEMENTED / NOT VERIFIED.


### 18.5 Transaction-boundary and stale-egress crash analysis — 2026-11-14

- [x] Specify separate ordered Risk reservation and Command acceptance commits; do not imply a cross-service distributed ACID transaction.
- [x] Require capability single-use consumption atomic with canonical command + reservation reference + outbox persistence.
- [x] Specify attempt marker persistence before egress and keep reservation held through ambiguous outcomes.
- [x] Define account-scoped credential-owning Egress boundary; dispatcher/adapter workers have no direct venue credentials or route.
- [x] Add a crash-point matrix spanning reservation, capability, command/outbox, attempt marker, socket write, venue acceptance, fill/Ledger posting, halt fencing and RecoveryBarrier.
- [ ] Select authoritative storage/isolation, workload identity, host/network fence and egress topology under OD-09/OD-10/OD-12.
- [ ] Approve capability serialization/signing and key custody under OD-08/security review.
- [ ] Implement process/network fault injection against the actual send boundary; a fake adapter or database-only epoch test is insufficient.
- [ ] Prove old egress is positively fenced under host/network partition before granting a new authority generation.

**Disposition:** design recommendation and test plan only. OD-09 remains open; no provider, database, cryptographic scheme, network fence, credential or production runtime was selected or implemented. CREATE remains non-production-safe.


## 18.6 Persistence and trusted-egress option analysis — 2026-11-14

- [x] Compared shared-transaction, service-owned local relational transactions, separate databases and event-store/coordination options at design level.
- [x] Defined candidate boundary: Risk commits all required reservations locally before capability issuance; Command atomically consumes the single-use capability with command + outbox in its own local transaction; Ledger posting remains separately atomic/idempotent.
- [x] Compared DB lease, gateway/proxy, isolated workload and dedicated host options; rejected lease/local epoch as sole egress fence.
- [x] Defined positive external fence acknowledgement and fail-closed takeover requirements.
- [ ] OD-09 storage/isolation selection and transaction proof.
- [ ] OD-08 canonicalization/signing/key custody; OD-10 recovery objectives; OD-12 operator/break-glass governance.
- [ ] Real egress-boundary fault injection, network bypass testing and host/workload fencing evidence.

Disposition: PROPOSED design analysis only. No database/provider/crypto/network technology selected or implemented; no new runtime or venue capability. See NX-REF-EXEC-002 §4.5.



### Exact-head CI verification after persistence/egress analysis — 2026-11-14

- Documentation analysis head verified: `3187a69e443157ac3e66b874b4dcbb29588ddc70`.
- GitHub Actions run [#43606550889](https://github.com/PandaGarry/NEXUS/actions/runs/43606550889) completed successfully on that exact head.
- Three jobs passed: Python 3.11, 3.12 and 3.13. Each executed 13 isolated reference-model suites with counts 11, 24, 13, 17, 12, 16, 18, 18, 32, 12, 15, 28 and 21 = 237 tests per runtime; 711 successful test executions total.
- This CI run verifies the existing Python reference-model suites at the exact documentation-analysis head. It does not test the newly documented transaction alternatives, database isolation, production egress topology, external host/network fencing, Rust, venue behavior or live safety.


## 18.7 Open-source component qualification — 2026-11-14

- [x] Create NX-RESEARCH-010 candidate matrix and qualification rules.
- [x] Record authority exclusions: no module owns Risk, reservations, command/outbox, Ledger, halt or trusted venue-send authority by default.
- [x] Identify PostgreSQL as leading persistence candidate for evaluation only; OpenTelemetry Collector as preferred observability candidate; OpenBao as secrets candidate; NATS as optional later transport; Cilium conditional on Kubernetes; Temporal deferred; NautilusTrader remains test-only.
- [ ] Establish dependency policy, license register, SBOM, provenance and vulnerability scanning in G0D.
- [ ] Run exact-version PostgreSQL transaction/concurrency/crash/restore evaluation before OD-09 selection.
- [ ] Define OpenTelemetry redaction, bounded-cardinality and telemetry-isolation tests.
- [ ] Complete OpenBao/managed KMS/HSM threat and license review before secrets integration.
- [ ] Add NATS only if measured fan-out/replay requirements justify its operational cost.

Disposition: research-only. No package, service, broker, database, vault or deployment module has been added to runtime. See NX-RESEARCH-010.


## 18.8 Modular product and trust-boundary design (PROPOSED)

- [x] Publish NX-ARCH-006 as a design proposal: bounded contexts, protected core, versioned contracts, module manifest/admission, workload identity, capability allowlists, independent data ownership, failure containment, and lifecycle controls.
- [x] Specify hard Demo/live separation: distinct account namespace and ledger, simulator-only execution, no production credentials or live-egress route, server-enforced type checks, and adversarial cross-domain tests.
- [x] Specify Learning/Wiki as a low-privilege domain with sanitized content and no trading/secret write access.
- [x] Exact branch-head reference workflow #43608583358 passed on the then-current head e15e47f9512bc07a1f6534a4f41b0d27d7d42578: Python 3.11/3.12/3.13 each passed 13 isolated suites / 237 tests (711 executions total). This is Python reference regression only; no module runtime, identity, isolation, DB, secrets or egress behavior is tested.
- [ ] Cross-review NX-ARCH-006 against NX-ARCH-001..005, NX-SEC-001, NX-IF-001..005 and NX-OWNER-DECISIONS-001; resolve contradictions and owner/security review findings.
- [ ] Draft module inventory, data classification, service ownership and capability matrix for the bounded v1 product scope.
- [ ] Add contract compatibility, forged-identity/IDOR, module-compromise, demo-to-live, secret-isolation, network-egress and rollback adversarial test plans to the D4/D6 evidence matrix.
- [ ] Decide modular-monolith/process boundaries and storage isolation only after G0D threat/deployment review and OD-09; no premature microservice decomposition.
- [ ] Do not implement public registration, third-party plugin loading, production identity, or module runtime before owner/security gate approval.

**Disposition:** documentation/design only. No package, identity provider, plugin framework, database, service, public user account or live capability was installed or enabled. NX-ARCH-006 does not pass G0D/G1 by publication.


## 18.9 Platform extensibility and commercial entitlement foundation (PROPOSED)

- [x] Publish NX-ARCH-007 candidate product-domain taxonomy and extensibility principles without treating candidate capabilities as delivery commitments.
- [x] Separate product capability, commercial entitlement and security authorization decision planes; subscription/payment/feature flags cannot grant Risk, Ledger, venue or egress authority.
- [x] Define stable namespaced feature identifiers, auditable entitlement grants, subscription lifecycle, webhook replay/deduplication, quota separation and downgrade/data-retention principles.
- [x] Define versioned module contracts, compatibility/deprecation/rollback, optional-module failure isolation and no arbitrary public plugin marketplace.
- [x] Preserve multi-tenancy and public SaaS as future gated decisions, not implicit v1 scope.
- [ ] Cross-review NX-ARCH-007 against NX-ARCH-001..006, NX-SEC-001, NX-IF-001..005 and NX-OWNER-DECISIONS-001.
- [ ] Define the first controlled module catalog schema and ownership/data-classification registry; validate dependency graph and contract compatibility rules.
- [ ] Add adversarial tests for forged plan claims, stale/revoked entitlements, replayed/out-of-order billing webhooks, downgrade, quota bypass, tenant confusion and billing-service outage.
- [ ] Ensure order dispatch/Risk/egress paths have no synchronous dependency on billing, learning, analytics, notifications or payment providers.
- [ ] Obtain separate owner/legal/security approval before public registration, paid plans, payment integration, teams/multi-tenancy or commercial launch.

**Disposition:** strategic design only. No subscription, price, payment integration, entitlement service, tenant, public account, feature flag or commercial promise was created. NX-ARCH-007 publication passes no implementation or launch gate.


## 18.10 Module registry, admission and capability governance (PROPOSED)

- [x] Publish NX-ARCH-008 defining immutable module/release identity, registry record and manifest requirements, lifecycle state machine, module classes and trust tiers.
- [x] Separate capability definitions, module declarations, independently issued workload grants and request-time authorization.
- [x] Define a proposed cross-domain data-access matrix, protected-core exclusions, contract/dependency compatibility and revocation/rollback rules.
- [x] Add 20 adversarial qualification scenarios covering forged identity, artifact/signature mismatch, stale grants, entitlement forgery, direct DB/venue access, Demo-to-live routing, SSRF, resource exhaustion, revocation races and telemetry leakage.
- [ ] Cross-review NX-ARCH-008 against NX-ARCH-001..007, NX-SEC-001, NX-IF-001..005 and NX-OWNER-DECISIONS-001; resolve contradictions and owner/security findings.
- [ ] Define and approve the canonical module registry/manifest schema, signing and provenance trust roots, workload identity and grant issuance policy.
- [ ] Map each proposed permission-matrix cell to an owned API, enforcement point, data classification and testable deny case.
- [ ] Define runtime isolation, secret/egress controls, revocation propagation objectives and resource budgets after deployment/security review.
- [ ] Select one low-risk first-party read-model module for G1 only after G0D approval; prove actual boundary enforcement with adversarial tests.
- [ ] Keep public plugin registration, third-party executable code, paid subscriptions, multi-tenancy and live authority separately gated.

**Disposition:** design only. No registry, manifest validator, signing service, grant issuer, sandbox, module runtime, deployment technology or external dependency was added. NX-ARCH-008 publication passes no readiness or implementation gate.


## 18.11 Exact-head CI evidence for NX-ARCH-008


### NX-ARCH-008 exact-head regression verification — 2026-11-14

- Exact branch HEAD `b1d3201a1fe1706909218943f5464eba43ea1041` passed GitHub Actions [#43611030968](https://github.com/PandaGarry/NEXUS/actions/runs/43611030968).
- All three jobs completed successfully: Python 3.11, 3.12 and 3.13; 13 isolated reference-model suites / 237 tests per runtime; 711 successful test executions total.
- This verifies the existing Python reference-model regression workflow at that exact documentation head. It does **not** test NX-ARCH-008's proposed registry, schema, identity, grant issuance, module isolation, secret handling, database permissions, network/egress enforcement, Rust, venue behavior or live-trading safety.
- The exact-head CI result is regression evidence only; NX-ARCH-008 remains PROPOSED / DESIGN ONLY and G0D/G1 remain open.


## 18.12 Final synchronized documentation-head verification


### Final synchronized documentation-head verification — 2026-11-14

The synchronized documentation head `c5c00d37b26f365b79690a9f3297ab571d9ec6f2` passed exact-head GitHub Actions [#43611122433](https://github.com/PandaGarry/NEXUS/actions/runs/43611122433). Python 3.11, 3.12 and 3.13 jobs all completed successfully; each ran 13 isolated reference-model suites / 237 tests (711 successful executions total). This is existing Python reference-model regression evidence only. It does not test NX-ARCH-008's proposed registry, manifest, workload identity, grants, module runtime/isolation, secrets, database permissions, network/egress enforcement, Rust, venue behavior or live-trading safety. NX-ARCH-008 remains PROPOSED / DESIGN ONLY; G0D/G1 remain open.


## 18.13 Module governance cross-architecture review

- [x] Cross-review NX-ARCH-001, NX-ARCH-006, NX-ARCH-007, NX-ARCH-008, NX-SEC-001, NX-IF-001..005 and NX-OWNER-DECISIONS-001; publish NX-ARCH-REVIEW-002.
- [x] Clarify that the Contract Gateway performs admission-level checks while each resource-owning service remains authoritative for operation/resource authorization.
- [x] Clarify that T4 is a protection classification, not a shared Risk/Command/Ledger/Egress workload identity or permission set.
- [x] Record remaining findings F-03..F-08: executable permission mapping, revocation objective, trust roots, actual storage/network/host isolation, first G1 module/resource budgets, and operator/support authority.
- [ ] Close findings F-03..F-08 with owner/security decisions and observed enforcement-boundary evidence before the corresponding G0D/G1 gates.
- [ ] Map each permission matrix cell to a contract, owner, data scope, enforcement point, audit event and negative test.
- [ ] Define measurable revocation propagation/cache and in-flight cancellation objectives before any module prototype.
- [ ] Do not infer acceptance, implementation readiness or security certification from the cross-review.

**Disposition:** design cross-review complete; acceptance not granted. No runtime or dependency selected. See [NX-ARCH-REVIEW-002](../architecture/NX-ARCH-REVIEW-002-module-governance-cross-review.md).


## 18.14 Capability catalog and authorization contract model

- [x] Publish NX-ARCH-009 with platform-owned capability definitions, stable identifiers/versioning and explicit owner/enforcement authority.
- [x] Separate capability definitions, module declarations, workload grants, user entitlements, user authorization and request-time domain authorization.
- [x] Define typed resource-scope grammar, field/data classifications and fail-closed handling for unknown/ambiguous scopes.
- [x] Propose initial first-party capability catalog and map each candidate to owner, scope, data class, consumer and negative test.
- [x] Explicitly exclude Risk mutation, reservations, command/outbox, Ledger posting, halt/recovery, credentials and Trusted Egress from optional-module grants.
- [x] Define authorization decision fields, revocation/cache/outage requirements, audit constraints and 18 adversarial CAP scenarios.
- [ ] Cross-review NX-ARCH-009 against NX-ARCH-006/007/008, NX-SEC-001, NX-IF-001..005 and owner decisions; resolve any policy/contract mismatch.
- [ ] Obtain domain-owner and security approval for each capability definition, scope grammar and data classification.
- [ ] Map every accepted capability to an existing or newly approved contract, API boundary, audit event, data owner and executable deny test.
- [ ] Define field-level classification, retention/legal basis, revocation propagation objective and cache freshness before G1.
- [ ] Implement schema/validator/policy only after G0D acceptance and applicable OD decisions; do not treat this design publication as an implementation gate.

**Disposition:** proposed design only. No executable schema, policy engine, grant issuer, permission, module activation or dependency was created.


## 18.15 Capability catalog cross-review

- [x] Cross-review NX-ARCH-009 against NX-ARCH-006/007/008, NX-ARCH-REVIEW-002, NX-SEC-001 and owner decisions; publish NX-ARCH-REVIEW-003.
- [x] Constrain billing subscription capability to user-authorized intent submission; Billing owner alone validates provider state and writes entitlement lifecycle.
- [x] Confirm optional modules receive no Risk, reservation, command/outbox, Ledger, halt/recovery or Trusted Egress capability.
- [x] Record CAP-R-02..09 covering ID approval semantics, canonical resource binding, field-level projection lineage, contract mapping, revocation objectives, audit custody, incomplete catalog scope and billing/execution decoupling.
- [x] Extend adversarial plan with CAP-19..26 for parser ambiguity, projection leakage, forged payment claims, webhook replay, generic privilege, audit compromise, billing outage and retired capability replay.
- [ ] Close CAP-R-02..09 with owner/security decisions and boundary-observed evidence before G0D/G1.
- [ ] Approve every capability ID, owner, scope, data class, contract and negative test; no candidate row is an active permission.
- [ ] Define numeric revocation/cache objectives, field-level retention/legal basis and independent audit custody.
- [ ] Implement no executable schema or policy engine until G0D approval and relevant OD-08/09/10/12 decisions.

**Disposition:** design cross-review complete; acceptance not granted. No permission, grant, runtime or dependency activated.


## 18.16 NX-ARCH-009 / NX-ARCH-REVIEW-003 exact-head regression evidence

- Exact branch HEAD `c906f855b0084eb12582e5adc8e1f7992dd2a94a` passed GitHub Actions [#43612365312](https://github.com/PandaGarry/NEXUS/actions/runs/43612365312).
- Python 3.11, 3.12 and 3.13 jobs all succeeded. Each runtime executed 13 isolated reference-model suites and 237 tests; total 711 successful test executions.
- This verifies the existing Python reference-model regression workflow only. It does not execute NX-ARCH-009's proposed capability catalog, schema, grants, authorization service, module runtime, isolation, data-classification controls, billing provider flow, Rust or venue integration.
- NX-ARCH-009 and NX-ARCH-REVIEW-003 remain PROPOSED / DESIGN ONLY; no capability is approved or active. CAP-R-02..09 remain open. G0D/G1 remain open.


## 18.17 Capability-to-interface contract traceability

- [x] Locate and inspect canonical NX-IF-001..005, NX-SEC-001 and NX-OWNER-DECISIONS-001 on the active engineering branch.
- [x] Publish NX-ARCH-REVIEW-004 mapping all 12 NX-ARCH-009 candidate capabilities to existing contract evidence or an explicit missing-contract gap.
- [x] Identify protected Risk/reservation, command/egress, Ledger, recovery/halt and credential boundaries that optional modules cannot receive.
- [x] Record owner-approved v1 account-scope constraints and distinguish them from still-open OD decisions.
- [x] Create a grounded source-data inventory by contract while explicitly marking field-level classification, lineage and retention as unresolved.
- [x] Define cross-cutting requirements for identity/resource binding, transaction/idempotency, timeout/retry, audit, negative tests and boundary-observed evidence.
- [ ] Obtain domain-owner/security approval for each candidate capability and any new product-domain contract before implementation.
- [ ] Approve field-level classification, projection lineage, minimization, retention/legal basis and export policy.
- [ ] Set measurable revocation/cache/outage objectives and prove stale-workload/process/DB/secret/network behavior before G1.
- [ ] Keep all capabilities proposal-only; no executable schema, grant, policy engine, module runtime or dependency until G0D acceptance and relevant OD decisions.

**Disposition:** design traceability complete; acceptance not granted. See [NX-ARCH-REVIEW-004](../architecture/NX-ARCH-REVIEW-004-capability-to-interface-contract-traceability.md).


## 18.18 NX-ARCH-REVIEW-004 exact-head regression evidence

- Exact branch HEAD `f78fc7d006ea475cf596ee2bd8bd65b9a7d37afa` passed GitHub Actions [#43613212116](https://github.com/PandaGarry/NEXUS/actions/runs/43613212116).
- Python 3.11, 3.12 and 3.13 jobs all completed successfully. Each runtime executed 13 isolated reference-model suites and 237 tests; 711 successful test executions total.
- This verifies the existing Python reference-model regression workflow only. It does not execute NX-ARCH-REVIEW-004's traceability matrix, proposed capabilities, new domain contracts, schema/grants, authorization service, module runtime/isolation, field-level data controls, Rust or venue integration.
- NX-ARCH-REVIEW-004 is a design traceability artifact; domain-owner/security acceptance, field-level classification/retention, revocation objectives and boundary-observed G1 evidence remain open. No capability is approved or active.


## 18.19 Revocation, freshness and control-plane outage objectives

- [x] Reconcile NX-ARCH-008/009 revocation rules with NX-IF-004 freshness/recovery and NX-IF-005 halt propagation.
- [x] Explicitly separate authorization freshness, source-data freshness, control propagation and RecoveryBarrier readiness.
- [x] Publish NX-ARCH-REVIEW-005 with candidate cache/revocation profiles, in-flight cancellation semantics and a control-plane outage matrix.
- [x] Preserve per-source/per-scope/per-operation freshness; do not define a global TTL or invent venue thresholds.
- [x] Define required measurement dimensions and actual process/DB/secret/network boundary evidence.
- [ ] Obtain owner/security acceptance of authorization cache, revocation, cancellation and hard-containment objectives.
- [ ] Obtain source-owner/OD-10 approval of freshness, completeness, retention, clock uncertainty, retry, RTO and RPO values.
- [ ] Obtain OD-12 approval of halt propagation deadline, operator roles, dual control and containment path.
- [ ] Measure and fault-inject stale-worker, process-pause, partition, secret-revocation and external-egress fencing before G1/G3.

**Disposition:** proposed engineering baseline only. Numeric values in NX-ARCH-REVIEW-005 are not accepted SLOs or production guarantees. No runtime control was implemented.


## 18.20 NX-ARCH-REVIEW-005 exact-head regression evidence

- Exact branch HEAD `97a1819527bf6b1973793b12a084ef8cd0dee776` passed GitHub Actions [#43613493976](https://github.com/PandaGarry/NEXUS/actions/runs/43613493976).
- Python 3.11, 3.12 and 3.13 jobs all completed successfully. Each runtime executed 13 isolated reference-model suites and 237 tests; 711 successful test executions total.
- This verifies the existing Python reference-model regression workflow only. It does not execute NX-ARCH-REVIEW-005's proposed cache/revocation targets, outage matrix, source freshness policy, halt propagation, cancellation, process/DB/secret/network fencing, Rust or venue integration.
- NX-ARCH-REVIEW-005 remains a proposal; all numeric objectives are unaccepted candidates. OD-10/12, domain-owner/security approval and G1/G3 boundary evidence remain open.

## 18.21 CI supply-chain hardening and stacked-PR integration audit — 2026-11-14

- [x] Confirm the PR integration graph from live GitHub metadata: PR #13 `foundation/financial-math-fixtures-v0` -> PR #14 `research/russia-venue-eligibility-v0` -> PR #16 `engineering/rust-execution-domain-conformance-v0`.
- [x] Verify each child PR base SHA equals the parent PR head SHA: #14 base `bb6400502640818fd5eba8a93eb3ae8dc54581d2` = #13 head; #16 base `ab6976933cb4de9b5320b73531034d02edc53907` = #14 head. This is an intentional stacked-PR chain, not an incorrect base.
- [x] Upgrade CI actions to current verified releases and pin immutable upstream commit SHAs: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1), `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (v7.1.0).
- [x] Verify the action-upgrade commit exact HEAD `e35d81cb34aeae1c13e25def0320e8a4a4b649bb` with GitHub Actions [#43614458632](https://github.com/PandaGarry/NEXUS/actions/runs/43614458632).
- [x] Confirm all 3 runtime jobs passed; each ran 13 isolated suites with counts 11, 24, 13, 17, 12, 16, 18, 18, 32, 12, 15, 28 and 21 = 237 tests; total 711 successful executions.
- [x] Inspect all three job logs: the prior Node.js 20 deprecation and Node `punycode` deprecation warnings are absent after the action upgrade.
- [ ] Add a repeatable workflow dependency lock/SBOM or equivalent transitive action dependency inventory; current full-SHA pins lock the two direct actions only.
- [ ] Review every transitive action dependency and establish automated update/security-advisory monitoring.
- [ ] Complete exact-head CI after the documentation synchronization commits recorded below; the run above is exact for `e35d81c` only.

**PR disposition:** PR #13, #14 and #16 remain open/Draft/unmerged. Preserve stack order; review and integrate parent PRs before their dependants. PR #16's 205 commits are measured from the PR #14 head and do not include PR #14's 82 commits. The 28-file / 3,730-addition scope remains a reviewability concern; split only if a dependency-aware review proves independent packages can be separated without duplicating or destabilizing the stack.

**Verification boundary:** this CI validates existing Python reference models only. It does not execute Rust, NX-ARCH-005's proposed normalized fixture schema/runner, production database transactions, process/host/network fencing, Trusted Egress, venue adapters, or live trading.


## 18.22 Numeric wire resource-boundary hardening — 2026-11-14

- [x] Audit numeric wire parsing against explicit resource-budget and stable rejection-class requirements.
- [x] Bound decimal scale: optional max_scale; default ceiling is the caller-supplied max_chars budget.
- [x] Normalize interpreter integer-string conversion budget failures into typed NumericWireResourceLimit / NUMERIC.RESOURCE_LIMIT for decimal and rational parsing.
- [x] Add regression tests for default/explicit scale bounds, invalid scale-budget configuration and oversized decimal/rational integers.
- [x] Update NX-ARCH-005 operation mapping and reference-model README; no production numeric profile or fixture runner selected.
- [x] Verify exact code/test HEAD b0fb99d4505ba5eb405788fee8ce447f28437479 with GitHub Actions [#43614612130](https://github.com/PandaGarry/NEXUS/actions/runs/43614612130): 13 isolated suites, 239 tests per Python 3.11/3.12/3.13 runtime; 717 successful executions total.
- [ ] Port the same bounded-resource semantics into a future normalized adapter only after NX-ARCH-005 and its explicit numeric profile are accepted.
- [ ] Add cross-language fixtures for oversized scale and interpreter-independent integer budget behavior before Rust conformance work.

**Disposition:** reference-model resource hardening complete and CI-verified at the exact code/test SHA. Production numeric bounds, Rust parser, normalized schema/runner and cross-language parity remain OPEN / gated.



## 18.23 Delegated G1 technical baseline selection — 2026-11-14

- [x] Publish NX-ADR-008 selecting the G1 design baseline for canonical command encoding, capability signing, persistence, transaction ownership, freshness/recovery and emergency operations.
- [x] Select RFC 8949 restricted deterministic CBOR, SHA-256 domain-separated command digest and COSE_Sign1 fully specified COSE Ed25519 algorithm (-19, RFC 9864) for G1 qualification; keep exact libraries and non-exportable key custody provider gated.
- [x] Select PostgreSQL 18 as the G1 persistence evaluation target; one primary, service-owned schemas/roles, separate Risk/Command/Ledger local ACID transactions, no distributed ACID or automatic failover.
- [x] Select source-specific EvidenceRequirementSet/FreshnessPolicy with explicit watermarks/completeness and fail-closed UNKNOWN; no global TTL.
- [x] Select single-owner emergency defaults: Owner-only step-up resume after RecoveryBarrier, no automatic cancel-all/flatten, no offline emergency order plan, break-glass containment only.
- [x] Update NX-OWNER-DECISIONS-001, NX-IF-001, NX-REF-EXEC-002, NX-RESEARCH-010 and architecture index to reference the selected G1 baseline.
- [ ] Qualify exact Python/Rust CBOR/COSE libraries, versions, licenses, supply-chain provenance and cross-language golden vectors.
- [ ] Prove non-exportable Ed25519 key custody and rotation/revocation in the selected provider; obtain security and jurisdictional review.
- [ ] Prove PostgreSQL reservation concurrency, serialization retries, ambiguous commit, backup/restore/PITR and old-primary fencing on the exact version.
- [ ] Obtain source-owner numeric freshness/retention/clock and OD-10 RTO/RPO decisions; keep affected risk-increasing operations blocked until configured.
- [ ] Implement and fault-test the real process/host/network Trusted Egress fence before G1/G3 readiness claims.

**Disposition:** technical direction selected for G1 evaluation under delegated authority. No database, key, secret manager, cloud, venue, credentials, production deployment or live capability is installed/selected/authorized. Owner-only risk, accounting, venue, legal and production decisions remain open.

## 18.24 COSE algorithm identifier standards correction — 2026-11-14

- [x] Cross-check the signing profile against RFC 9864, published October 2025.
- [x] Replace polymorphic COSE EdDSA (-8) with fully specified COSE Ed25519 (-19).
- [x] Constrain COSE key to OKP / Ed25519; reject Ed448, -8, algorithm/key mismatch and substitution.
- [x] Treat protected kid as a lookup hint only; issuer/algorithm/purpose/validity/revocation/generation-bound lookup must yield exactly one eligible key.
- [ ] Qualify exact COSE libraries and provider interoperability; add rejection vectors before implementation.

## 18.25 Canonical CBOR decoder acceptance boundary — 2026-11-14

- [x] Verify RFC 8949 §4.2.1 core deterministic map ordering is bytewise lexicographic over deterministic key encodings (not legacy length-first ordering).
- [x] Clarify that canonicality is an ingress requirement, not merely an encoder preference.
- [x] Restrict command map keys to schema-defined ASCII text field names; reject non-ASCII, unknown and duplicate keys; Unicode remains valid in values under strict UTF-8.
- [x] Require decoder rejection of non-preferred integer/length encodings, indefinite lengths, unsorted maps and trailing bytes before object materialization.
- [ ] Add byte-level negative vectors for non-shortest integer/length encodings, wrong map order, duplicate keys, trailing bytes, nested limits and invalid UTF-8 in both language implementations.
- [ ] Confirm selected Python/Rust CBOR libraries expose raw-token/duplicate detection and deterministic-profile validation; reject a library if it normalizes malformed input before NEXUS can inspect it.

**Disposition:** protocol requirement clarified; no CBOR implementation or dependency selected. Cross-language parser proof remains G1-gated.


## 18.26 Full stacked-PR ancestry and current exact-head CI — 2026-11-14

- [x] Verify PR #1 -> #2 -> #3 -> #4 -> #5 -> #6 -> #7 -> #9 -> #10 -> #11 -> #12 -> #13 -> #14 -> #16 by exact base-SHA / parent-head-SHA equality.
- [x] Verify PR #8 is a parallel branch from the v1-scope base, not an ancestor of PR #16.
- [x] Confirm all PRs in the direct ancestry are currently open, Draft and unmerged. PR #16 base remains PR #14 head; do not retarget or merge it ahead of its parents.
- [x] Record current PR #16 diff: 248 commits beyond its base, 32 changed files, 4,399 additions and 72 deletions. This is an integration/reviewability concern, not evidence of incorrect branch ancestry.
- [x] Verify current exact branch HEAD 7914772358d2ee49c87374373bad5c589d0a2905 with GitHub Actions [#43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349): 13 isolated suites, 239 tests per Python 3.11/3.12/3.13 runtime; 717 successful executions total.
- [x] Inspect all three logs: no Node.js 20 or punycode deprecation warning remains after full-SHA action pinning.
- [ ] Prepare a parent-first integration/review plan for the full stack; no merge, retarget, rebase or branch rewrite is performed without the required owner authorization.
- [ ] Consider splitting independent architecture packages from PR #16 only if the file/commit dependency audit proves the split is safe and reduces reviewer burden.

**Disposition:** PR #16 is correctly stacked but is not independently mergeable. The blocking condition is its open Draft ancestry, not a wrong base branch. Exact-head CI verifies Python reference models only; no Rust, PostgreSQL, COSE implementation, Trusted Egress, venue adapter or live-trading behavior is tested.

## 18.27 Final synchronized G1 baseline / standards-correction exact-head CI — 2026-11-14

- [x] Verify final branch HEAD `7914772358d2ee49c87374373bad5c589d0a2905` with GitHub Actions [#43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349).
- [x] Confirm Python 3.11, 3.12 and 3.13 jobs all succeeded.
- [x] Confirm 13 isolated suites per runtime with counts 11, 24, 13, 17, 12, 16, 18, 18, 32, 14, 15, 28 and 21 = 239 tests per runtime; 717 successful test executions total.
- [x] Inspect all three job logs: no test failures, Node.js 20 deprecation warnings or `punycode` deprecation warnings.
- [x] Record exact-head evidence in status, roadmap, changelog and PR #16 body.
- [ ] Do not interpret this reference-model CI as validation of Rust, CBOR/COSE implementation, PostgreSQL transactions, process/host/network fencing, Trusted Egress, venue adapters or live-trading safety.

**Disposition:** exact synchronized branch-head Python reference regression passed. G0D/G1 implementation/evidence gates remain open; PR #16 remains Draft; live trading NOT AUTHORIZED.

## 18.28 Post-synchronization exact-head regression — 2026-11-14

- [x] Verify branch HEAD `928d5fd261553676c3fad6a8e88b984a862af338` with workflow [#43615282210](https://github.com/PandaGarry/NEXUS/actions/runs/43615282210).
- [x] Confirm Python 3.11/3.12/3.13 all passed; 13 isolated suites / 239 tests per runtime; 717 successful executions.
- [x] Inspect all three logs; no test failures or Node.js 20 / `punycode` deprecation warnings.
- [ ] Keep verification scope limited to Python reference models; this run does not exercise the proposed CBOR/COSE implementation, PostgreSQL, Rust, egress fencing, venue behavior or live safety.

**Disposition:** exact tested SHA passed. This evidence is regression-only; G0D/G1 implementation gates remain open.


## 18.29 Verified full stacked ancestry and current exact-head CI — 2026-11-14

- [x] Verify the direct PR chain by exact base/head SHA equality: #1 → #2 → #3 → #4 → #5 → #6 → #7 → #9 → #10 → #11 → #12 → #13 → #14 → #16.
- [x] Verify PR #8 is a parallel branch based on PR #7, not an ancestor of #16.
- [x] Confirm all PRs in the direct chain are currently open, Draft and unmerged; PR #16's base is exactly PR #14's head.
- [x] Verify current branch HEAD `9e9035033da77d958601cb6b69128e13e2551a0d` with [workflow #43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737).
- [x] Confirm Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all three logs: no failures and no Node.js 20 / `punycode` deprecation warnings.
- [ ] Preserve parent-first review/integration; do not retarget or merge PR #16 independently.
- [ ] Split broad PR scope only if a clean dependency-aware decomposition can be created without corrupting the stacked ancestry.

**Disposition:** PR ancestry is correct and intentionally stacked. PR #16 remains Draft/open/unmerged. CI is Python reference-only and does not close G0D/G1 or establish Rust, persistence, egress or live readiness.

## 18.30 Post-sync exact-head verification — 2026-11-14

- [x] Verify post-normalization branch HEAD `9e9035033da77d958601cb6b69128e13e2551a0d` with GitHub Actions [#43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737).
- [x] All 3 Python runtime jobs passed; 13 isolated suites / 239 tests per Python 3.11, 3.12 and 3.13 (717 successful executions).
- [x] Confirm no Node.js 20 or punycode deprecation warnings in any job log.
- [x] Confirm current PR #16 snapshot: 265 commits beyond base, 32 changed files, 4,467 additions and 72 deletions; PR remains Draft/open/unmerged.
- [ ] Do not claim this matrix verifies Rust, PostgreSQL, COSE signing, Trusted Egress, venue or live behavior.

The exact-head workflow above verifies the current normalized documentation tree plus the existing Python reference suites. The last code change remains the numeric-wire resource hardening at b0fb99d; no production runtime has been introduced.

## 18.31 CBOR / COSE implementation library qualification — 2026-11-14

- [x] Audit current Rust CBOR candidates against RFC 8949 §4.2.1 deterministic encoding and the strict NEXUS ingress profile.
- [x] Distinguish canonical encoder support from strict decoder acceptance; confirm Rust `cbor2` RawValue/validate_slice preserve/check well-formed bytes but do not establish deterministic-profile acceptance.
- [x] Reject `cbor-core` as a drop-in protocol codec: it targets a draft profile, uses length-first ordering, and documents an unstable API.
- [x] Qualify `coset` 0.4.2 as a test-only COSE structure candidate with alg=-19, original protected-header byte preservation and custom signing/verifying closures; record its maturity and underlying-CBOR caveats.
- [x] Record that `cose2` built-in Ed25519 provider uses deprecated alg=-8 and is not acceptable without a custom alg=-19 signer/verifier.
- [x] Reject `pycose` 1.1.0 as the conformance oracle because of stale release/provenance evidence and no demonstrated RFC 9864 support.
- [ ] Build bounded cross-language positive/negative byte vectors and a strict raw-byte validator before selecting any parser.
- [ ] Verify exact crate release provenance, full transitive SBOM, licenses, advisories, reproducible builds, panic surface and fuzz behavior under G0D.
- [ ] Keep all libraries uninstalled/unselected until G0D and OD-08 security review.

**Disposition:** NX-RESEARCH-011 published. No dependency, Rust workspace, CBOR parser, COSE signer/verifier, key or runtime was added. G0D/G1 remain open.

## 18.32 Final exact-head verification after NX-RESEARCH-011 and OD-08 profile refinement — 2026-11-14

- [x] Verify branch HEAD `1bb2192e6746e0f86659f006ef204990adc81188` with workflow [#43615753905](https://github.com/PandaGarry/NEXUS/actions/runs/43615753905).
- [x] Python 3.11, 3.12 and 3.13 all passed 13 isolated suites / 239 tests per runtime; 717 successful test executions total.
- [x] Inspect all three logs; no test failures and no Node.js 20 / `punycode` deprecation warnings.
- [x] Record that NX-RESEARCH-011 and the ASCII command-map-key refinement are documentation/design-only; no dependency or parser was added.
- [ ] Keep G0D/G1 library, strict-validator, cross-language, cryptographic and runtime gates open.

**Disposition:** exact synchronized branch-head Python reference regression passed. It does not exercise Rust, CBOR/COSE libraries, PostgreSQL, Trusted Egress, external fencing, venues or live trading.

## 18.33 Final CI action-runtime and serialization-research exact-head verification — 2026-11-14

- [x] Verify current branch HEAD `69657a0808b859b17ab94a6d3e008a2ae9671cc7` with [workflow #43615820603](https://github.com/PandaGarry/NEXUS/actions/runs/43615820603).
- [x] Confirm Python 3.11, 3.12 and 3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all three logs: no test failures, Node.js 20 deprecation or `punycode` warnings.
- [x] Independently fetch the exact pinned `action.yml` files: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` and `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` both declare `runs.using: node24`.
- [x] Confirm current PR #16 snapshot: 33 files, 4,758 additions, 72 deletions; Draft/open/unmerged and correctly stacked on PR #14.
- [ ] Continue to treat CI as Python reference-model regression only; no CBOR/COSE parser, Rust, PostgreSQL, Trusted Egress, venue or live-safety proof is implied.

**Disposition:** exact-head reference CI passed and direct action runtime pins are verified. G0D/G1 implementation, strict parser and crypto-provider qualification remain open.

## 18.34 COSE pre-verification trust and key-material boundary — 2026-11-14

- [x] Clarify that protected `kid`, `alg` and token-supplied issuer/audience are untrusted until signature verification succeeds.
- [x] Restrict candidate key lookup to a bounded local versioned registry; prohibit token-directed remote key retrieval.
- [x] Require local expected issuer/audience and key-purpose binding before and after signature verification; signed claims must match local expected context.
- [x] Require exactly one eligible key; fail closed on ambiguity, stale generation, revocation or mismatch.
- [x] Restrict verification material to public OKP/Ed25519 with 32-byte public key; reject private `d` material outside Risk; require 64-byte signature.
- [ ] Add positive/negative cross-language COSE vectors for wrong issuer/audience, remote key URL, duplicate/ambiguous kid, private key leakage, malformed key/signature lengths and stale registry generation.
- [ ] Verify selected COSE libraries preserve raw protected-header bytes and reject untrusted header/claim misuse without network key discovery.

**Disposition:** protocol trust boundary tightened in NX-ADR-008 and NX-RESEARCH-011. No COSE implementation, key or runtime added; G0D/OD-08 remain open.

## 18.35 COSE_Sign1 exact wire profile — 2026-11-14

- [x] Pin the NEXUS COSE object to an untagged, embedded-payload, four-element COSE_Sign1 array.
- [x] Require exactly two protected-header labels: alg (1) = -19 and 1–64-byte kid (4); unprotected map is empty.
- [x] Require capability claims as one NEXUS restricted deterministic-CBOR map inside payload bstr; validate original bytes before typed claim use.
- [x] Preserve the received protected-header bstr and construct Sig_structure using RFC 9052 §9 deterministic encoding.
- [x] Reject tag 18, detached/null payload, extra protected parameters, non-empty unprotected headers, duplicate/colliding labels and alternate COSE message types.
- [ ] Add byte-exact cross-language vectors for protected-header bstr, payload bstr, Sig_structure, Ed25519 signature and all rejection cases.
- [ ] Prove selected library preserves original protected bytes and does not silently accept or normalize profile violations.

**Disposition:** exact wire profile is now specified in NX-ADR-008 / NX-RESEARCH-011. No library or cryptographic runtime approved; G0D/OD-08 remain open.

## 18.36 Exact-head regression after COSE key-resolution hardening — 2026-11-14

- [x] Verify branch HEAD `6fefd9a44ff2f272b6516265d10f41c46a13cf7a` with [workflow #43615911362](https://github.com/PandaGarry/NEXUS/actions/runs/43615911362).
- [x] Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all job logs: no failures or Node.js 20 / `punycode` deprecation warnings.
- [x] Confirm key-resolution design rejects remote token-directed key retrieval, binds lookup to local expected issuer/audience and requires signed claims to match after verification.
- [ ] Add cross-language adversarial COSE vectors for issuer/audience substitution, malicious key URLs, ambiguous kid, stale/revoked registry, malformed key/signature and private-key exposure.

**Disposition:** exact-head Python reference regression passed; it does not exercise the proposed COSE verifier or key registry. OD-08/G0D/G1 remain open for implementation and security review.

## 18.37 Exact-head CI after COSE key-resolution and protected-header profile refinement — 2026-11-14

- [x] Verify branch HEAD `88fcb30068507d85fb35802ca5d2195fd528c000` with [workflow #43616054657](https://github.com/PandaGarry/NEXUS/actions/runs/43616054657).
- [x] Python 3.11, 3.12 and 3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all three job logs: no failures or Node.js 20 / `punycode` deprecation warnings.
- [x] Confirm the protected COSE header is narrowed to deterministic map labels 1 (alg=-19) and 4 (kid), with empty unprotected map, and local registry-bound key selection.
- [ ] Add cross-language COSE positive/negative vectors and prove exact protected-header bytes, Sig_structure, external AAD and signature verification.
- [ ] Keep the current CI result scoped to Python reference models; it does not validate the COSE profile implementation or key registry.

**Disposition:** exact-head Python reference regression passed. COSE signing/verifying and G0D/G1 security evidence remain unimplemented.

## 18.38 Exact-head CI after COSE_Sign1 wire-profile specification — 2026-11-14

- [x] Verify branch HEAD `8d2c2f404782b718f1a3a422bb0ce918bb6b922d` with [workflow #43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308).
- [x] Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests; 717 successful executions.
- [x] Inspect all three job logs; no test failures or Node.js 20 / `punycode` warnings.
- [x] Confirm the exact COSE_Sign1 wire profile is design-only and cross-language byte/signature vectors remain open.
- [ ] Do not infer that this Python-only run validates the COSE parser, signer, verifier or key registry.

**Disposition:** exact-head reference-model regression passed; cryptographic implementation and G0D/OD-08 evidence remain open.

## 18.39 Current exact-head regression and full PR-chain verification — 2026-11-14

- [x] Verify PR #16 branch HEAD `8d2c2f404782b718f1a3a422bb0ce918bb6b922d` with GitHub Actions [#43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308).
- [x] Python 3.11, 3.12 and 3.13 all passed 13 isolated suites / 239 tests per runtime; 717 successful executions total.
- [x] Inspect all three job logs: no test failures, Node.js 20 deprecation or `punycode` warnings.
- [x] Re-fetch PR #1–#14 and #16 metadata; verify exact child-base / parent-head SHA equality for #1 → #2 → #3 → #4 → #5 → #6 → #7 → #9 → #10 → #11 → #12 → #13 → #14 → #16.
- [x] Verify PR #8 is a parallel branch based on PR #7 and not in PR #16's direct ancestry.
- [x] Confirm every PR in the direct ancestry is currently open, Draft and unmerged; PR #16 remains based on PR #14's exact head.
- [x] Record current PR #16 snapshot: 33 changed files, 4,937 additions, 72 deletions and 322 commits in the stacked comparison (includes parent history).
- [x] Update PR #16 title/body with current scope, exact-head evidence, COSE profile and non-authorizations.
- [ ] Preserve parent-first review/integration; do not retarget, merge or rewrite the stack automatically.
- [ ] Keep this CI evidence scoped to Python reference models; it does not verify Rust, CBOR/COSE implementation, PostgreSQL, external fencing, Trusted Egress, venues or live execution.

**Disposition:** branch ancestry is valid and deliberately stacked; all direct-chain PRs remain Draft. Exact-head Python reference CI passed. PR #16 remains open/Draft/unmerged; no owner approval for merge or production/live action is implied.

## 18.40 Final exact-head CI after COSE wire profile and documentation synchronization — 2026-11-14

- [x] Verify branch HEAD `71afa64c00affed017c1f072600f4f0e4aaeccc6` with [workflow #43616247630](https://github.com/PandaGarry/NEXUS/actions/runs/43616247630).
- [x] Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all three job logs: no test failures, Node.js 20 deprecation or `punycode` warnings.
- [x] Confirm CI workflow direct actions remain full-SHA pinned and exact manifests declare Node 24.
- [x] Confirm all current serialization/COSE changes remain design/research only; no parser, signer, verifier or key registry was added.
- [ ] Continue to keep G0D/OD-08/G1 strict-parser, COSE interoperability, PostgreSQL and Trusted Egress evidence gates open.

**Disposition:** exact-head Python reference-model regression passed. It is not cryptographic, Rust, persistence, egress, venue or live-trading evidence.

## 18.41 Final synchronized PR #16 exact-head regression — 2026-11-14

- [x] Verify branch HEAD `3af0453897545b77fee358b9902a6301f662232e` with [workflow #43616348161](https://github.com/PandaGarry/NEXUS/actions/runs/43616348161).
- [x] Python 3.11, 3.12 and 3.13 all passed 13 isolated suites / 239 tests per runtime; 717 successful executions total.
- [x] Inspect all job logs: no test failures, Node.js 20 deprecation or `punycode` warnings.
- [x] Confirm PR #16 and Issue #15 bodies were synchronized to current ancestry, scope, gates and verification boundaries.
- [ ] Keep CI claims limited to Python reference models; this run does not exercise Rust, CBOR/COSE, PostgreSQL, egress, venues or live safety.

**Disposition:** final synchronized branch-head reference regression passed. PR #16 remains Draft/open/unmerged and parent-first integration is required.

## 18.42 Risk-owned reservation serialization and PostgreSQL concurrency proof plan — 2026-11-14

- [x] Define a Risk-owned scope-state record as the common serialization point for reservation commits and Risk exposure-projection updates.
- [x] Preserve Ledger journal ownership; Ledger MUST NOT write Risk-owned projection/scope-state records directly.
- [x] Require Risk to consume Ledger/venue/external exposure events through an idempotent inbox and update projection, source watermark and scope-state in one Risk-owned local transaction.
- [x] Require multi-scope account/child reservation to update every pre-provisioned scope-state record in deterministic canonical scope-ID order and commit all reservations/totals/idempotency state atomically.
- [x] Specify fail-closed behavior for missing scope rows, stale/incomplete source watermarks and unresolved primary/commit authority.
- [x] Specify same request identity + same digest replay behavior and different digest conflict behavior.
- [x] Clarify that an absent row is not proof of rollback while the original transaction may still be in flight; only same-identity/digest retry may arbitrate through the unique constraint, otherwise halt.
- [x] Specify whole-transaction bounded retry for PostgreSQL SQLSTATE 40001 / 40P01; no statement-only retry or stale snapshot reuse.
- [x] Cross-check PostgreSQL 18 SERIALIZABLE, application-level consistency, explicit locking, serialization failure and ON CONFLICT semantics against official documentation.
- [ ] Build adversarial concurrency tests: simultaneous capacity race; projection update racing reservation; overlapping parent/child scopes; duplicate/reordered projection event; missing scope row; idempotency collision; 40001/40P01 retry; lost commit response; stale/incomplete watermark.
- [ ] Run on exact PostgreSQL 18 patch with role separation, query plan, lock wait, retry-budget and crash/failover instrumentation.
- [ ] Prove the Risk projection's source lineage and freshness requirements cover every exposure-affecting venue/Ledger/manual event before G1 acceptance.

**Disposition:** design protocol clarified in NX-ADR-008 §5.3, NX-IF-002 §6.4 and OD-09. No PostgreSQL instance/schema, reservation service or concurrency runtime was implemented. G1 remains gated on exact-version evidence.

## 18.43 Field-level data lineage and projection governance — 2026-11-14

- [x] Inspect actual field definitions in NX-IF-001..005 and security asset/trust boundaries in NX-SEC-001.
- [x] Map TradeIntent, CanonicalTradeCommand, RiskDecision, RiskApprovalCapability, RiskScope, ExposureItem, ExposureSnapshot, RiskReservation, ExecutionEvent, StateEvidenceVector, FreshnessPolicy, RecoveryCase, RecoveryBarrier, HaltState, EmergencyActionPlan and EmergencyCommand fields.
- [x] Distinguish opaque-but-linkable IDs, financial values, source evidence references, security metadata, personal/identity data and true SECRET material.
- [x] Define source-owner projection restrictions for Analytics, Portfolio, Notifications, Strategy, Demo, Learning, Billing and future Support.
- [x] Explicitly record that NX-IF-003 does not enumerate the complete Ledger journal-leg schema; no fields were invented.
- [x] Record retention/legal basis and field-level classification as proposals requiring owner/security approval.
- [ ] Obtain source-owner/security approval of every field/combination classification and projection allowlist.
- [ ] Author Ledger journal and Analytics/Portfolio projection contracts before any read API or query service.
- [ ] Define retention, deletion, rebuild, audit custody and declassification controls with legal/accounting review.
- [ ] Add row/field leakage, cross-account, source-lineage, stale-watermark, partial-coverage and forbidden-field tests at actual boundaries.

**Disposition:** NX-ARCH-REVIEW-006 published. Field inventory is source-grounded; classifications and retention are proposed, not accepted. No API, schema, database table, grant or runtime was implemented.

## 18.44 Risk reservation concurrency contract synchronization — 2026-11-14

- [x] Synchronize NX-ADR-008 §5.3, NX-IF-002 §6.4 / §11, NX-REF-EXEC-002 §4.5 and OD-09 around one Risk-owned scope-state serialization point.
- [x] Keep Ledger as journal owner; Risk consumes Ledger/venue/external events through idempotent projection inbox transactions.
- [x] Specify atomic multi-scope account/child reservation, deterministic scope-ID order, pre-provisioned scope rows and fail-closed missing/stale evidence.
- [x] Add acceptance cases for reservation/projection races, duplicate/reordered events, 40001/40P01 whole-transaction retries, ambiguous commits and idempotency conflicts.
- [x] Cross-check PostgreSQL 18 transaction isolation, serialization failures, application-level consistency, row locks and ON CONFLICT behavior against official documentation.
- [ ] Prove all acceptance cases on the exact PostgreSQL 18 patch with separate service roles, fault injection, backup/restore/PITR and primary-fencing evidence.
- [ ] Keep PostgreSQL as G1 evaluation target only; no production database, schema or reservation service is installed.

**Disposition:** design and test obligations synchronized; no database/runtime behavior is implemented or verified. G1 remains gated.

## 18.45 Risk scope serialization and PostgreSQL concurrency review — 2026-11-14

- [x] Cross-review NX-ADR-008 §5.3–5.4, NX-IF-002 §6.3–7 and OD-09 against PostgreSQL 18 official documentation.
- [x] Require projection updates to lock/update every affected parent/account and child scope row atomically.
- [x] Require privileged scope-hierarchy changes to serialize with reservations/projections and advance scope_config_version.
- [x] Define minimum logical scope-state version metadata without selecting a physical SQL schema.
- [x] Require the account/root scope-state row in every v1 reservation/projection transaction and recheck root scope_config_version after locking the full set.
- [x] Keep market/index/FX/fee/collateral inputs as immutable versioned valuation snapshots bound to reservation/capability; do not rewrite scope-state on every market-data tick.
- [x] Clarify SQLSTATE 23505 idempotency collision resolution; prohibit generic unique/exclusion retry.
- [x] Define whole-transaction retry for 40001/40P01, ambiguous commit handling and primary authority requirements.
- [x] Add concurrency/fault matrix for capacity races, projection fan-out, scope changes, duplicate/reordered events, idempotency collisions, stale writers, direct Ledger writes and failover.
- [ ] Implement and run the PostgreSQL 18 test harness with exact patch, role separation, concurrency/load/failover instrumentation.
- [ ] Prove source completeness and freshness for every exposure-affecting venue/Ledger/manual event before G1 acceptance.

**Disposition:** NX-ARCH-REVIEW-007 published; transaction design refined and synchronized into ADR-008, IF-002 and OD-09. No database, schema, migration or runtime was implemented.

## 18.46 Exact-head CI after Risk scope concurrency review — 2026-11-14

- [x] Verify branch HEAD `e7c5461ae7ccea4f29fc77461db91d44566aba36` with [workflow #43616908979](https://github.com/PandaGarry/NEXUS/actions/runs/43616908979).
- [x] Python 3.11, 3.12 and 3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all three logs: no test failures or Node.js 20 / `punycode` deprecation warnings.
- [x] Confirm NX-ARCH-REVIEW-007 and synchronized ADR-008 / IF-002 / OD-09 changes are design-only; no PostgreSQL schema, instance or runtime exists.
- [ ] Execute the PostgreSQL 18 concurrency, idempotency, failover and external-fencing proof matrix before G1 acceptance.

**Disposition:** exact-head Python reference regression passed. PostgreSQL concurrency design is refined but not implemented or proven.

## 18.47 Numeric-wire integer conversion determinism — 2026-11-14

- [x] Remove dependence on Python's interpreter-configurable integer-string conversion threshold for ordinary wire acceptance.
- [x] Add a fixed 512-decimal-digit budget for coefficient, scale, numerator and denominator fields, independent of max_chars.
- [x] Reject values over the fixed budget as NUMERIC.RESOURCE_LIMIT before calling int().
- [x] Add boundary tests: 512 digits accepted and 513 rejected for decimal and rational wire values.
- [ ] Mirror the same 512-digit parser budget in the future Rust implementation and language-neutral negative fixtures.
- [ ] Decide whether the future production wire profile needs a different bound; do not infer this reference-model bound as a production financial limit.

**Disposition:** Python reference parser now has deterministic integer-digit resource behavior. Cross-language fixture parity remains open; this does not establish production numeric policy.

## 18.48 Immutable valuation-input vector and dispatch-time race control — 2026-11-14

- [x] Separate source-owned mark/index/FX/fee/collateral snapshots from Risk's PostgreSQL scope-state serialization records.
- [x] State explicitly that source snapshots are not assumed to share the Risk database transaction or a distributed transaction.
- [x] Bind Risk reservation and approval to an immutable version vector with source identity, value/digest, completeness/watermark and freshness evidence.
- [x] Require Trusted Egress to revalidate the exact bound valuation_input_vector_id/version against the authoritative persisted Risk evidence manifest and source-specific freshness/drift policy immediately before send.
- [x] Prohibit Egress from fetching replacement market/FX/fee/collateral values or calling source services on the dispatch path; unavailable/unverifiable manifest denies send.
- [x] Prohibit silently replacing the approval's valuation inputs when a newer source snapshot arrives; require a new Risk evaluation/reservation if the old vector is no longer admissible.
- [ ] Define the source-owner interface schema and cross-source snapshot-coherence contract without inventing fields before source contracts are approved.
- [ ] Add race tests: source update during reservation, update after approval/before dispatch, missing watermark, contradictory vector, stale mark, drift-bound breach and unconfigured policy.
- [ ] Keep numeric freshness/drift thresholds owner/domain-controlled; no universal defaults.

**Disposition:** design boundary clarified across NX-ADR-008, NX-IF-002 and NX-ARCH-REVIEW-007. No valuation service, schema or dispatch runtime implemented.

## 18.49 PostgreSQL 18.7 exact G1 evaluation target — 2026-11-14

- [x] Verify PostgreSQL 18.7 is the latest supported PostgreSQL 18 minor release on 2026-11-14.
- [x] Select 18.7 as the exact G1 database qualification patch only; production remains unselected.
- [x] Review official 18.7 migration notes: index-corruption/REINDEX caveats, incremental-backup chain warning, C-extension rebuild requirements and privilege/extension hardening changes.
- [x] Record initial G1 constraints: no third-party/C extensions, no unreviewed extension scripts, no dblink, no untrusted replication subscriptions, no privileged COPY FROM ON_ERROR path; use a fresh full backup for PITR tests.
- [ ] Pin exact package/image digest, checksum, provenance, host OS/architecture and configuration before harness creation.
- [ ] Review every 18.7 REINDEX note against actual schema/indexes and test full backup/restore/PITR.
- [ ] Requalify the latest supported 18.x patch before any future deployment decision.

**Disposition:** PostgreSQL 18.7 is the bounded G1 evaluation target only. No instance, schema, extension or production topology is selected or installed.

## 18.50 Persisted valuation-evidence manifest at Trusted Egress — 2026-11-14

- [x] Define immutable ValuationInputVector identity/version and source provenance in NX-IF-002.
- [x] Bind ExposureSnapshot, RiskReservation and RiskApprovalCapability to the same exact vector ID/version.
- [x] Require Trusted Egress to read the authoritative persisted Risk evidence manifest and latest consumed source-watermark/correction status.
- [x] Prohibit Egress from calling market/FX/fee/collateral source services or fetching replacement values on the dispatch path.
- [x] Require the manifest to prove watermark continuity and bounded ingestion lag; missing/stale/unknown evidence denies send.
- [x] Define policy semantics for a newer tick: older immutable vector remains valid only while source-specific freshness/clock/quality/drift policy passes; a policy may explicitly require latest.
- [ ] Define the source ingestion and invalidation SLA/measurement contract, including delayed correction events and stream gaps.
- [ ] Add race tests for source update, correction/revocation, watermark gap and stale manifest after approval but before send.

**Disposition:** synchronized NX-IF-002, NX-ADR-008, NX-ARCH-REVIEW-007 and NX-REF-EXEC-002. No valuation service, evidence store, egress runtime or numeric threshold is implemented.

## 18.51 Trusted Egress send-authorization linearization — 2026-11-14

- [x] Define the final egress decision as a short attempt-scoped transaction over the persisted valuation manifest generation and active reservation/halt/eligibility/dispatcher fence versions.
- [x] Bind a single-use EgressBoundaryAuthorization to the exact attempt ID and observed versions.
- [x] Define the commit as the send-authorization linearization point.
- [x] Require immediate socket-write initiation by the single-writer Egress process after commit; no source fetch, queue hop or unbounded async preparation.
- [x] Prohibit holding a database transaction open across network I/O.
- [x] Define post-gate updates as causally later; the attempt remains potentially sent and must be reconciled.
- [ ] Define source ingestion-lag/correction objectives and prove the persisted manifest covers delayed/reordered invalidations.
- [ ] Add crash/race tests at final-gate commit, immediately-before-socket-write and after socket-write initiation; inspect durable attempt and actual instrumented egress boundary.

**Disposition:** semantic protocol added to NX-IF-002 and NX-REF-EXEC-002. No egress authorization runtime or database schema implemented.

## 18.52 Risk approval / valuation evidence cross-contract synchronization — 2026-11-14

- [x] Align NX-IF-001 RiskEvaluationRequest, RiskDecision and RiskApprovalCapability with immutable valuation_input_vector_id/version from NX-IF-002.
- [x] Align NX-IF-001 COSE profile with NX-ADR-008: untagged embedded four-element COSE_Sign1, alg=-19, bounded kid, empty unprotected map and deterministic payload.
- [x] Require exact protected/payload byte preservation, local-only bounded key registry and rejection of token-directed remote key discovery.
- [x] Require Egress to validate the signed vector against the authoritative persisted Risk evidence manifest and latest consumed source watermark/correction state.
- [x] Prohibit remote market/FX/fee/collateral source calls or valuation replacement on the dispatch path; missing/unverifiable manifest denies send.
- [x] Add negative conformance vectors for malformed COSE wire forms, key ambiguity, private-key exposure, manifest gaps/corrections and valuation-input changes.
- [ ] Execute cross-language COSE vectors and Egress manifest race/fault tests after G0D/G1 readiness; no signer, verifier or egress runtime is implemented.

**Disposition:** NX-IF-001/002, NX-ADR-008, NX-ARCH-REVIEW-007 and NX-REF-EXEC-002 now share the same proposed contract. Runtime and security evidence remain open.

## 18.53 PostgreSQL 18.7 security and migration qualification — 2026-11-14

- [x] Verify official PostgreSQL 18.7 release date (2026-11-12) and current supported-minor status.
- [x] Record 52 security fixes and 140+ bug fixes in the official release.
- [x] Identify ON CONFLICT/updatable-view and RLS visibility fixes; prohibit using either as the sole isolation boundary.
- [x] Identify dblink/replication-subscription arbitrary-file-write risk; exclude both from initial G1.
- [x] Identify C-extension rebuild and extension-script risks; exclude extensions from initial G1.
- [x] Record index corruption / REINDEX caveats and pre-update incremental-backup invalidity.
- [ ] Review all release-note REINDEX entries against the actual G1 schema and selected indexes.
- [ ] Prove fresh full backup, restore, WAL continuity and PITR on the exact 18.7 package.
- [ ] Pin vendor package/image digest, provenance, host platform and configuration before harness execution.

**Disposition:** PostgreSQL 18.7 remains a G1 evaluation target only. No database instance, extension, schema or production topology was installed or approved.

## 18.54 Exact-head reference CI after valuation / PostgreSQL qualification — 2026-11-14

- [x] Verify PR #16 branch HEAD `7fb396df5f3e700adf0ad151c446e38930fdadb0` on [workflow #43617626344](https://github.com/PandaGarry/NEXUS/actions/runs/43617626344).
- [x] Pass 13 isolated suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 executions).
- [x] Inspect all three job logs: no test failures or Node.js 20 / `punycode` deprecation warnings.
- [x] Confirm numeric-wire 512-digit acceptance / 513-digit rejection is included in the matrix.
- [ ] Keep Rust, strict CBOR/COSE, PostgreSQL 18.7 concurrency/restore, Trusted Egress, host/network fencing and venue evidence as separate G1 gates.

**Disposition:** exact branch-head Python reference CI passed. No production implementation or live authority is implied.

## 18.55 NX-IF-004 alignment with selected G1 profile and Trusted Egress ownership — 2026-11-14

- [x] Bind RiskApprovalCapability to both StateEvidenceVector and the exact immutable ValuationInputVector ID/version.
- [x] Move the final compatibility-check authority from generic Execution wording to Trusted Egress at the attempt-scoped send-authorization gate.
- [x] Align the evidence contract's canonical serialization/digest/signature reference with NX-ADR-008 and NX-IF-001: restricted deterministic CBOR, domain-separated SHA-256, COSE Ed25519 alg=-19.
- [x] Keep library selection, non-exportable key custody, key ceremony/rotation, security review and jurisdictional acceptance open.
- [ ] Add cross-contract conformance tests for StateEvidenceVector + ValuationInputVector invalidation and final egress gate ordering.

**Disposition:** documentation consistency correction only; no signer, verifier, key or dispatch runtime implemented.

## 18.56 WP-D StateEvidenceVector / ValuationInputVector / Egress synchronization — 2026-11-14

- [x] Keep StateEvidenceVector (NX-IF-004) distinct from ValuationInputVector (NX-IF-002); RiskApprovalCapability binds both exact immutable IDs/versions and required digests/policy references.
- [x] Require Trusted Egress to validate the signed valuation vector against the authoritative persisted Risk evidence manifest and latest consumed source watermark/correction state.
- [x] Prohibit remote market/FX/fee/collateral source calls or replacement valuation fetches on the dispatch path; missing/stale/incomplete/unverifiable manifest denies send.
- [x] Specify that a newer monotonic market-data tick alone does not invalidate an admissible bound vector unless versioned source/operation policy requires latest; no silent rebind.
- [x] Add WP-D conformance cases for source identity/watermark/clock/correction lineage, cross-source coherence, valuation manifest invalidation and separation of RecoveryBarrier readiness from command approval.
- [ ] Prove source-owned snapshot immutability, vector coherence, manifest freshness and no-fetch behavior at instrumented process/network boundaries after G0D/G1 readiness.

**Disposition:** NX-IF-001/002/004, NX-ADR-008, NX-ARCH-REVIEW-007 and NX-REF-EXEC-002 are aligned at the design level. No runtime or production authorization exists.



## 18.57 Halt / egress race exact-head documentation synchronization — 2026-11-14

- [x] Synchronize NX-IF-005, NX-ADR-008, NX-ARCH-REVIEW-005 and NX-REF-EXEC-002 on the shared halt/final-egress serialization point.
- [x] Define both race outcomes and require Egress to drain or positively fence gate-committed attempts before halt acknowledgement.
- [x] Normalize duplicate checklist section identifiers 18.31, 18.50 and 18.51 to unique 18.53–18.55.
- [ ] Run exact-head CI after this documentation synchronization and record the resulting SHA/run.
- [ ] Execute actual halt/gate race tests at the instrumented Egress boundary; documentation synchronization is not runtime proof.

## 18.58 Halt / final-egress authorization race semantics — 2026-11-14

- [x] Identify and reconcile the ambiguity between NX-IF-005's "immediately before send" halt check and NX-ADR-008's persisted send-authorization linearization point.
- [x] Require halt-epoch commit and final EgressBoundaryAuthorization commit to serialize against the same authoritative halt-state generation.
- [x] Define both commit orders: halt-first denies socket initiation; gate-first creates an irrevocable in-flight attempt requiring reservation retention and reconciliation.
- [x] Require Egress to track gate-committed attempts until socket initiation is observed or the sender is positively fenced.
- [x] Prevent Egress from acknowledging the new halt epoch while a paused pre-halt authorized attempt could still resume and initiate a socket write.
- [x] Clarify that HALTED means no stale/queued attempt can newly initiate a write after boundary acknowledgement; it does not recall bytes already initiated or prevent venue processing of in-flight requests.
- [ ] Add fault-injection tests for halt-first, gate-first, pause-after-gate-before-socket, process crash, network partition, positive fence and acknowledgement ordering; inspect the actual instrumented egress boundary.
- [ ] Decide whether the product requires the stronger guarantee "no socket initiation after halt commit"; if so, design and prove a transport-level cancellation/fencing primitive before production.

**Disposition:** semantic race closed at design level across NX-IF-005, NX-ADR-008, NX-ARCH-REVIEW-005 and NX-REF-EXEC-002. No runtime or transport fence is implemented; halt propagation remains unproven.

## 18.59 Halt epoch versus final Egress authorization race — 2026-11-14

- [x] Require halt epoch transition and final EgressBoundaryAuthorization to serialize on the same authoritative halt-state generation.
- [x] Define halt-wins ordering: final Egress gate observes new epoch and denies socket initiation.
- [x] Define gate-wins ordering: attempt is logically in-flight, retains reservation and requires reconciliation; halt cannot retroactively revoke it.
- [x] Require Egress to track gate-committed attempts until socket-write initiation is observed or sender is positively fenced; it cannot acknowledge a later halt epoch while a paused old attempt could resume.
- [x] State the guarantee precisely: after boundary acknowledgement, no stale/queued attempt may newly initiate a socket write; do not claim no bytes can leave after wall-clock halt request or recall venue-processed requests.
- [x] Separate Risk Engine outage from authoritative halt-store outage; independent Control Plane can commit halt when store is available, while store uncertainty blocks Egress gate and prevents a fully-enforced HALTED claim.
- [ ] Inject halt-before-gate, gate-before-halt, paused process, crash after gate commit, control-store outage and sender-fencing failures; inspect durable state and actual egress boundary.

**Disposition:** ordering and failure semantics specified in NX-IF-005, NX-ADR-008, NX-ARCH-REVIEW-005 and NX-REF-EXEC-002. No halt store, egress runtime or network fence is implemented.

## 18.60 Halt / Egress final-gate adversarial cases — 2026-11-14

- [x] Add explicit cases 36–42 to NX-IF-005 for halt-before-gate, gate-before-halt, paused process after gate commit, unproven external fence, halt-store outage, late venue acceptance and instrumented socket-boundary proof.
- [x] Require zero socket-write initiation when halt epoch commits before final Egress authorization.
- [x] Require gate-committed attempts to remain reserved and tracked until socket-write initiation is observed or sender is positively fenced.
- [x] Keep boundary unacknowledged when an old process could resume; do not claim fully enforced HALTED.
- [ ] Implement and run all seven cases with actual instrumented socket/network boundary and independent process/host/path fencing.
- [ ] Verify post-ack venue acceptance of an earlier initiated request is reconciled without blind resend.

**Disposition:** adversarial requirements documented only; no runtime or external fencing proof exists.

## 18.61 Halt epoch / final Egress authorization linearization — 2026-11-14

- [x] Define the final EgressBoundaryAuthorization commit and halt-epoch commit as serialized against the same authoritative halt-state record/generation.
- [x] Define both outcomes: halt commits first → final gate denies; gate commits first → attempt is in-flight and cannot be retroactively revoked.
- [x] Require Egress to track every gate-committed attempt until socket-write initiation is observed or the old sender is positively fenced.
- [x] Prohibit halt-boundary acknowledgement while a paused pre-halt authorized attempt could still resume and initiate a write.
- [x] Distinguish halt commit from fully enforced HALTED acknowledgement; previously initiated bytes may still be accepted/processed by the venue and must be reconciled.
- [x] Define fail-closed behavior when the authoritative halt store is unavailable or external fence evidence is uncertain.
- [x] Add crash-point rows and IF-005 conformance cases for both lock orders, paused process, lost ack, unknown socket outcome, unavailable control store and post-ack venue acceptance.
- [ ] Prove both lock orders and paused-process behavior at the actual Egress socket/network boundary; database-only or mock-adapter tests are insufficient.
- [ ] Prove external process/host/network fencing and that no stale/queued attempt can initiate a socket write after boundary acknowledgement.

**Disposition:** linearization semantics are specified across NX-IF-005, NX-REF-EXEC-002 and NX-ARCH-REVIEW-005. No egress runtime, halt store or network fence is implemented; production halt guarantee remains unproven.

## 18.62 Exact-head CI after halt / Egress linearization review — 2026-11-14

- [x] Verify SHA `73841573e4e02b34a0c0363bbbe21155828d0c08` with [workflow #43617906166](https://github.com/PandaGarry/NEXUS/actions/runs/43617906166).
- [x] Python 3.11, 3.12 and 3.13 each passed 13 isolated suites / 239 tests; 717 successful executions total.
- [x] Inspect all three job logs: no test failures, Node.js 20 deprecation or `punycode` deprecation warnings.
- [x] Include the halt-first/gate-first/pause-after-gate/positive-fence semantics in NX-IF-005's adversarial acceptance matrix (cases 36–42).
- [x] Resolve all duplicate `18.x` checklist section identifiers; the current sequence is unique through 18.60.
- [ ] Re-run exact-head CI after the final documentation-only synchronization commits below/after this entry.
- [ ] Execute the halt/Egress race matrix at an instrumented socket boundary; the Python reference CI does not test this architecture contract.

**Disposition:** latest verified CI is exact for `7384157`; subsequent commits are documentation-only. No halt store, Egress runtime or external fence exists.

## 18.63 Risk approval signing versus venue signing authority separation — 2026-11-14

- [x] Separate RiskApprovalCapability private signing authority from venue API credentials and venue request-signing authority.
- [x] Require distinct keys, workload identities and policies; key reuse is prohibited.
- [x] Keep Risk approval private key only in the Risk signing authority; Execution/Trusted Egress receive public verification material only.
- [x] Keep venue credentials and venue request-signing capability only in Trusted Egress, which owns the actual venue socket.
- [x] Define EgressBoundaryAuthorization as a separate one-use attempt-scoped control record, not a substitute for Risk approval or venue credentials.
- [ ] Test that Strategy/AI/API/Execution cannot forge approvals or obtain venue secrets; Egress cannot mint Risk approvals; Risk signer cannot access venue credentials/socket.
- [ ] Qualify KMS/HSM/vault policies, key ceremony, rotation, revocation, backup and recovery before any key implementation.

**Disposition:** authority separation recorded in NX-SEC-001 and aligned with NX-IF-001 / NX-ADR-008. No keys, vault, signer or venue credentials are implemented.

## 18.64 Exact-head CI after halt and signing-authority clarification — 2026-11-14

- [x] Verify PR #16 HEAD `dbfba513b86a79b8b6574a80c1beb136b28836c7` on [workflow #43618114058](https://github.com/PandaGarry/NEXUS/actions/runs/43618114058).
- [x] Pass 13 isolated suites / 239 tests on Python 3.11, 3.12 and 3.13 (717 executions).
- [x] Inspect all three logs: no failures or Node.js 20 / `punycode` deprecation warnings.
- [x] Confirm current matrix includes numeric-wire 512/513-digit resource boundary tests.
- [ ] Keep signing key custody, halt-store, Egress gate, PostgreSQL, Rust and external fencing evidence separate from Python reference CI.

**Disposition:** exact PR-head reference CI passed. No production signing or live execution authority is implied.

## 18.65 Execution preflight / Trusted Egress final authorization boundary — 2026-11-14

- [x] Define Execution verification as non-authorizing preflight and defense in depth.
- [x] Define Trusted Egress as the sole final send-authorization boundary and sole owner of venue socket initiation.
- [x] Require final Egress revalidation of persisted Risk approval, reservation, both evidence vectors, source manifest, eligibility, halt and fence generations.
- [x] Bind final Egress authorization and halt transition to the same authoritative halt-state generation.
- [ ] Add conformance tests proving stale state introduced after Execution preflight is rejected by the final Egress gate.
- [ ] Verify at the process/network boundary that only Trusted Egress has venue credentials and direct venue egress.

**Disposition:** contract wording aligned; runtime and boundary-observed proof remain open.

## 18.66 Test-only halt / final Egress gate reference oracle — 2026-11-14

- [x] Add `halt_egress_gate.py` as a pure test-only state-machine oracle; no production imports or dependencies.
- [x] Add 12 tests for halt-first denial, gate-first in-flight ordering, paused-process acknowledgement blocking, positive sender fencing, single-use attempt identity, halt-store outage and post-socket reconciliation.
- [x] Treat a sender fence without trusted socket-initiation evidence as OUTCOME_UNKNOWN; retain reservation and reconciliation obligation.
- [x] Ensure a gate-committed attempt remains eligible to initiate while halt is propagating, but prevents HALTED acknowledgement until socket initiation is observed or sender is positively fenced.
- [x] Ensure both socket-initiated attempts and fenced attempts without a trusted initiation report remain reconciliation obligations after HALTED acknowledgement.
- [x] Document that sequential oracle tests do not prove real database linearizability, process/host/network fencing or socket behavior.
- [x] Initial 11-test revision passed on code SHA `e45ea01c6047e1f1207a6987a2cd05d7440853b1` (250 tests/runtime, 750 total) on workflow #43618215618; later sender-fence hardening and expanded edge coverage are recorded in 18.69–18.71.
- [ ] Implement actual shared-row/conditional-update ordering and fault-inject both commit orders, process pause, store outage and positive fence at the real Egress boundary.

**Disposition:** reference model and unit tests added; runtime, durable halt store, transport and external fence remain unimplemented.

## 18.67 Exact-head CI with HaltEgressGate reference tests — 2026-11-14

- [x] Verify PR #16 HEAD `772943e9e37272af7065fc26ad01eae5d48af22b` on [workflow #43618240612](https://github.com/PandaGarry/NEXUS/actions/runs/43618240612).
- [x] Pass 13 isolated suites / 250 tests on Python 3.11, 3.12 and 3.13 (750 successful executions).
- [x] Confirm egress-fencing suite contains 24 tests, including 11 HaltEgressGate cases for halt/gate ordering, paused senders, fencing and store outage.
- [x] Inspect all logs: no test failures or deprecated Node.js runtime warnings.
- [ ] Prove the same semantics with real PostgreSQL transactions, concurrent processes, instrumented sockets and independent host/network fencing.

**Disposition:** sequential reference state-machine tests pass; no production linearizability or fencing guarantee is established.

## 18.68 HEGC control authority and idempotent attempt-grant recovery — 2026-11-14

- [x] Define HEGC as the logical sole writer of HaltState and EgressBoundaryAuthorization, separate from Risk, Command Coordinator and credential-owning Egress.
- [x] Require HEGC to hold no venue credentials/socket and no Risk approval signing key; Egress holds no direct write permission to HEGC control records.
- [x] Require narrow read-only access to Risk/Command/eligibility/evidence/dispatcher records and write access only to the control-owned schema.
- [x] Make grant issuance idempotent on stable attempt ID: exact retry returns the same persisted grant; any changed binding conflicts.
- [x] Require Trusted Egress to independently verify the RiskApprovalCapability signature, exact command digest, active reservation, evidence bindings, audience, expiry and single-use consumption; HEGC grant cannot replace Risk approval.
- [x] Define ambiguous HEGC response recovery by reading the same attempt ID; no replacement attempt or second grant while the first may still send.
- [ ] Implement and test HEGC transaction semantics, durable uniqueness constraints, Egress grant verification/consumption and restart recovery.
- [ ] Test response loss after grant commit, duplicate request, changed digest, changed evidence generation, Egress pause, HEGC restart and positive sender fencing.
- [ ] Qualify the HEGC workload identity, service role, audit trail and independent recovery/fencing before any deployment.

**Disposition:** logical authority and retry contract documented in NX-ADR-008 / NX-IF-001 / NX-IF-005 / NX-REF-EXEC-002. No HEGC runtime or database schema implemented.

## 18.69 Sender-fence versus definitely-not-sent semantic correction — 2026-11-14

- [x] Identify that external process/host fencing proves no future send authority, not that a prior socket side effect did not occur.
- [x] Replace the model's `FENCED_NOT_SENT` state with `SENDER_FENCED_UNKNOWN`.
- [x] Keep fenced-without-initiation-report attempts in the reconciliation-required set.
- [x] Add a regression test proving sender fencing cannot erase an unknown prior socket side effect.
- [x] Verify the expanded 16-case HaltEgressGate suite on Python 3.11/3.12/3.13 at exact code/test HEAD `f1c0bd0576bd42058ca2482706533248bcf6069b` (workflow #43618694545).
- [ ] Prove trusted socket-initiation evidence, fence attestation and reconciliation at the actual Egress boundary; never release reservation from fence receipt alone.

**Disposition:** reference model now distinguishes "cannot send again" from "definitely did not send". Production evidence remains open.

## 18.70 HEGC ownership and halt-gate reference-model edge coverage — 2026-11-14

- [x] Select HEGC as the sole logical writer of HaltState and EgressBoundaryAuthorization; separate it from Risk, Command Coordinator and credential-owning Egress.
- [x] Define HEGC as no-credentials/no-socket/no-Risk-signing-key; Egress has no direct write access to halt/gate records and receives one-use attempt-scoped grants.
- [x] Define one active HEGC instance, PostgreSQL 18.7 control-owned schema/role, fail-closed outage and no automatic failover before fencing/grant reconciliation.
- [x] Add a test-only Python oracle for the two legal halt/gate commit orders, pause-after-gate, positive sender fencing, unknown outcome and halt-store outage.
- [x] Extend the oracle with pending-halt/store-recovery races, repeated halt idempotency and signed-64-bit halt-epoch exhaustion.
- [x] Model durable `ConsumeEgressGrant` as a one-use transition from GATE_COMMITTED to GRANT_CONSUMED; only a positive response permits one socket-write attempt.
- [x] Cover lost/indeterminate consume response, no second permit/send, store outage before consume and an already-consumed grant during a later store outage.
- [x] Current `test_halt_egress_gate.py` contains 21 state-machine tests.
- [ ] Add duplicate halt-request regressions during store outage and after HALTED (completed later at code/test SHA `2e94edd73f8933f0d510eed940452316ec5b8832`). At the verified `f1c0` checkpoint the oracle had 16 tests.
- [x] Verify code/test HEAD `f1c0bd0576bd42058ca2482706533248bcf6069b` with workflow [#43618694545](https://github.com/PandaGarry/NEXUS/actions/runs/43618694545): 13 isolated suites / 255 tests on each Python runtime; the egress-fencing package ran 29 tests (13 authority-handover + 16 halt-gate).
- [x] Inspect all three runtime logs: no failures, Node.js 20 deprecation or `punycode` warnings.
- [ ] Prove HEGC role grants, API authentication, one-use grant consumption, workload identity and audit integrity.
- [ ] Prove actual socket-initiation reporting and independent process/host/network fencing; the Python oracle is sequential and not a production concurrency proof.

**Disposition:** logical ownership and test-only state-machine semantics are specified. HEGC, database schema, API, grants, network fence and production Egress remain NOT IMPLEMENTED.


## 18.71 Expanded HEGC halt-gate oracle and exact-head CI — 2026-11-14

- [x] Verify exact code/test HEAD `f1c0bd0576bd42058ca2482706533248bcf6069b` on [workflow #43618694545](https://github.com/PandaGarry/NEXUS/actions/runs/43618694545).
- [x] Pass 13 isolated suites / 255 tests on each of Python 3.11, 3.12 and 3.13 (765 successful executions total).
- [x] Confirm the egress-fencing package passed 29 tests, including 16 HaltEgressGate tests at that historical SHA.
- [x] Inspect all three job logs; no test failures or deprecation warnings.
- [x] Preserve OUTCOME_UNKNOWN and reservation retention when a positive sender fence exists without trusted socket-initiation evidence.
- [ ] Implement and prove HEGC idempotent grant persistence, changed-binding conflicts, restart recovery and least-privilege role enforcement.
- [ ] Prove halt/gate serialization with real PostgreSQL concurrent transactions and fault injection.
- [ ] Prove trusted socket-initiation observation and independent process/host/network fencing; reconcile ambiguous venue outcomes without blind resend.

**Disposition:** exact code/test HEAD passed Python reference CI. Sequential tests do not prove production concurrency, durable control state, actual socket behavior, external fencing or live-trading safety.

## 18.72 Exact-head CI after 18-case halt-gate model and HEGC transaction review — 2026-11-14

- [x] Verify PR #16 HEAD `9b88eabb80e44510e29013fe02315c354c4b488b` with [workflow #43618875958](https://github.com/PandaGarry/NEXUS/actions/runs/43618875958).
- [x] Python 3.11, 3.12 and 3.13 each passed 13 isolated suites / 257 tests: 771 successful executions total.
- [x] Confirm egress-fencing package passed 31 tests, including 18 HaltEgressGate state-machine tests.
- [x] Inspect all three logs: no failures, Node.js 20 deprecation or `punycode` warnings.
- [x] Verify sender-fenced attempts without trusted initiation report remain OUTCOME_UNKNOWN and reservation-held.
- [ ] Re-run exact-head CI after the signed-64-bit epoch exhaustion grant-denial and HEGC consistency documentation updates.
- [ ] Prove HEGC SERIALIZABLE participation by all gate-critical writers, role grants, one-use grant consumption and actual process/socket fencing.

**Disposition:** exact code/test HEAD passed Python reference CI. Later commits add one fail-closed epoch-boundary assertion and documentation; no HEGC or production egress runtime exists.

## 18.73 HaltEgressGate 18-case code/test-head CI — 2026-11-14

- [x] Fix duplicate halt requests during store outage so they do not downgrade an already committed HALTING/HALTED epoch.
- [x] Assert sender fencing retains the reservation while socket initiation remains unobserved and outcome remains UNKNOWN.
- [x] Add two regressions: duplicate halt request during store outage while HALTING; duplicate request after HALTED during store outage.
- [x] Verify exact code/test HEAD `2e94edd73f8933f0d510eed940452316ec5b8832` on [workflow #43618796109](https://github.com/PandaGarry/NEXUS/actions/runs/43618796109).
- [x] Pass 13 suites / 257 tests on Python 3.11, 3.12 and 3.13 (771 successful executions).
- [x] Confirm egress-fencing package passes 31 tests (13 authority-handover + 18 HaltEgressGate).
- [x] Inspect all three logs: no test failures or deprecation warnings.
- [ ] Run a fresh CI on the current documentation-only PR head after synchronization.
- [ ] Prove the same ordering with PostgreSQL transactions, concurrent processes, instrumented sockets and independently verified process/host/network fences.

**Disposition:** exact code/test head passed; PR #16 head `09775625327c74cc31f27f18b0280e89bee4878d` contains only documentation changes after it. No production concurrency or fencing proof is established.


## 18.74 HEGC one-use grant consumption and exact code/test-head CI — 2026-11-14

- [x] Add explicit GATE_COMMITTED → GRANT_CONSUMED → SOCKET_INITIATED transitions to the test-only oracle.
- [x] Test single-use grant consumption and denial of a second consume.
- [x] Test lost consume response: same attempt remains consumed/in-flight; no replacement permit or blind resend.
- [x] Test consume-store outage fails closed and does not authorize socket initiation.
- [x] Test already-consumed grant across halt/store outage; socket initiation must be observed or sender fenced before HALTED acknowledgement.
- [x] Fix stale test expectations exposed by workflow #43618969753.
- [x] Verify exact code/test HEAD 9d618131ac9951e23c589491b2fb1039f6dc1d86 on [workflow #43619194630](https://github.com/PandaGarry/NEXUS/actions/runs/43619194630).
- [x] Pass 13 isolated suites / 260 tests on each of Python 3.11, 3.12 and 3.13 (780 successful executions total).
- [x] Confirm egress-fencing passes 34 tests, including 21 HaltEgressGate cases; inspect all three job logs.
- [ ] Prove ambiguous consume status resolution, durable grant idempotency and Egress process-incarnation binding against the HEGC service/database.
- [ ] Prove PostgreSQL SSI plus an enforced shared scope-generation/guard gives the required real-time commit-order semantics; SERIALIZABLE alone is insufficient evidence.
- [ ] Prove actual socket initiation, process/host/network fencing and venue reconciliation.

**Disposition:** corrected reference tests pass on all supported Python runtimes. HEGC, durable grant store, common commit-order guard, production Egress and external fencing remain unimplemented.


## 18.75 Duplicate-halt cause preservation and exact code/test-head CI — 2026-11-14

- [x] Preserve the initiating halt reason across duplicate requests in one active halt episode.
- [x] Add tests for duplicate halt requests while HALTING and HALT_PENDING.
- [x] Verify exact code/test HEAD fedc4879fee5ed97f03dea094c3d5f3fb6aaf7c8 on [workflow #43619194630](https://github.com/PandaGarry/NEXUS/actions/runs/43619194630).
- [x] Pass 13 isolated suites / 262 tests on Python 3.11, 3.12 and 3.13 (786 successful executions total).
- [x] Confirm egress-fencing passes 36 tests, including 23 HaltEgressGate tests; inspect all three job logs.
- [ ] Prove original halt-cause persistence, audit-event append semantics and idempotency in the durable HEGC store.
- [ ] Prove grant-consumption ambiguity, per-scope commit-order guard and actual socket/process/network fencing in integration tests.

**Disposition:** duplicate-halt cause behavior is verified in the sequential reference model only; production persistence and control-plane guarantees remain open.


## 18.76 HEGC shared scope-guard function candidate — 2026-11-14

- [x] Identify that PostgreSQL SERIALIZABLE alone does not prove the required commit-order visibility for overlapping transactions.
- [x] Record a preferred G1 evaluation shape: SECURITY DEFINER scope-guard function, dedicated NOLOGIN/non-superuser owner, guard-table-only write rights, caller EXECUTE-only grants and direct-DML bypass prevention.
- [x] Require the guard to be acquired as the first SQL statement after BEGIN, before protected reads/writes, and held through source mutation or HEGC grant commit.
- [x] Require a fresh post-wait view or 40001 whole-transaction restart when the SERIALIZABLE snapshot predates a concurrent guard update.
- [x] Specify fixed trusted search_path with pg_temp last, schema-qualified objects, no dynamic SQL, PUBLIC EXECUTE revoked, explicit grants and caller/scope authorization.
- [ ] Prove the guard function and all invalidating writer procedures use the same guard rows in the same outer PostgreSQL 18.7 transaction.
- [ ] Prove source-table direct DML is denied to bypassing roles and guard-owner privileges cannot mutate Risk/Command source records.
- [ ] Fault-inject source-writer-first and HEGC-first ordering, stale snapshot, 40001/40P01, connection loss, ambiguous commit, duplicate attempt and multi-scope deadlock ordering.
- [ ] Measure guard contention, bounded scope limits, throughput and retry behavior under realistic G1 load.

**Disposition:** preferred database-boundary pattern recorded for evaluation only. No function, schema, role, grant or PostgreSQL integration harness is implemented or approved.

## 18.77 PostgreSQL SSI commit-order and HEGC guard qualification — 2026-11-14

- [x] Cross-check PostgreSQL SSI internals and research: SERIALIZABLE guarantees equivalence to some serial order, not necessarily wall-clock commit order for overlapping transactions.
- [x] Separate Risk aggregate scope-state guard from HEGC gate-validation commit-order guard; do not assume one row proves both invariants.
- [x] Require HEGC and every invalidating writer to acquire the shared gate guard as the first SQL statement after BEGIN, before any protected read/write, and hold it through commit.
- [x] Require stale-snapshot transactions to abort/retry; multi-scope guards are acquired in deterministic order, root/account first.
- [x] Record a least-privilege coordination-schema / SECURITY DEFINER guard function as a G1 candidate only; fixed search_path, fully qualified names, no dynamic SQL, PUBLIC execution revoked, no direct DML bypass.
- [ ] On PostgreSQL 18.7, test writer-first and HEGC-first ordering, wait/retry behavior, stale snapshots, all invalidating writer classes, bypass denial, deadlocks, ambiguous commits and multi-scope lock order.
- [ ] Select physical guard ownership/procedure only after the G1 concurrency harness proves commit order and role grants.

**Disposition:** design correction based on PostgreSQL SSI semantics; no guard table/function/schema/runtime implemented. See NX-RESEARCH-012 §4.2.

## 18.78 Grant-consumption red-CI analysis and recovery — 2026-11-14

- [x] Record failures #43618969753 (SHA `913ef9e`) and #43619038468 (SHA `f9f385d`): two test sequences did not model the newly required GRANT_CONSUMED transition before socket initiation, and one stale assertion expected a sender-fenced attempt to initiate a later socket write.
- [x] Correct the gate-first/store-outage scenario to consume the already committed grant before the outage, then treat it as in-flight through recovery.
- [x] Correct sender-fence scenario: fencing prevents any future socket initiation; the attempt remains OUTCOME_UNKNOWN and reconciliation-required.
- [x] Verify corrected code/test HEAD `fedc4879fee5ed97f03dea094c3d5f3fb6aaf7c8` on workflow #43619194630: 262 tests/runtime across Python 3.11/3.12/3.13 (786 executions), egress-fencing 36 tests / HaltEgressGate 23 tests.
- [ ] Keep a regression test for each crash/response-loss boundary; do not suppress or downgrade a failing CI result.

**Disposition:** both red runs were investigated and resolved; the corrected exact code/test HEAD passed all three runtimes. No production HEGC behavior is inferred from these reference tests.

## 18.79 HEGC guard first-statement enforcement and least-privilege API — 2026-11-14

- [x] Identify that a standalone SECURITY DEFINER guard function does not itself prevent a caller from performing protected reads before invoking it.
- [x] Require either one reviewed HEGC transaction entrypoint that acquires the guard before validation reads and grant write, or a DB-enforced transaction API with guard as the first SQL statement.
- [x] Require every invalidating writer to mutate source state only through guarded procedures; direct DML and advisory-lock bypasses are prohibited.
- [x] Keep guard owner NOLOGIN/non-superuser, guard-row-only writes, fixed trusted search_path with pg_temp last, schema-qualified names, no dynamic SQL, PUBLIC EXECUTE revoked and caller EXECUTE-only grants.
- [ ] Test privilege escalation, search_path spoofing, function overloading, temp-object shadowing, caller pre-read, direct DML bypass and procedure bypass.
- [ ] Verify actual transaction snapshot behavior and commit-order guarantee on PostgreSQL 18.7.

**Disposition:** threat-model and G1 candidate refined; no database function, role, schema or runtime exists.
