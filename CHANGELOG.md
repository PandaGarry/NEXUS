# Changelog

Заметные изменения проекта фиксируются в обратном хронологическом порядке. Release notes пишутся понятным языком; инженерные детали остаются в ADR/PR.

## Unreleased

### Added — Bounded exact numeric context and canonical scalar wire (test-only; CI verified)
- Added mandatory caller-supplied NumericLimits and BoundedNumericContext preflight for decimal input, scale alignment, multiplication, rational division, compare, step checks, exact conversion and quantization.
- Added strict versioned scalar wire formats nxd1 (decimal) and nxr1 (reduced rational); parsers require explicit input character budgets and reject non-canonical forms.
- Added dedicated bounded-numeric (32 tests) and wire-conformance (11 tests, including language-neutral golden vectors) suites. PR run #43595449902 passed exact PR HEAD `6200bae99e9b7ce865487a40312d0074c0e2a276` on Python 3.11–3.13: 172 tests per runtime / 516 executions. No production limits or cross-language adoption are approved.


### Added — Exact rational inverse base exposure (test-only; CI verified)
- Added `RationalAssetAmount` and a conventional inverse-contract formula: quote notional divided by quote-per-base price.
- Preserves repeating results as reduced rationals (e.g. 1/300 BTC); finite decimal conversion is conditional and quantization requires an explicit mode.
- Requires base-asset settlement in this reference model. Venue-specific product qualification remains open.


### Added — Exact rational division and explicit quantization (test-only; CI verified)
- `ExactDecimal.divide_exact` returns a reduced `ExactRational`; division by zero fails closed and no rounding is implicit.
- Added exact terminating-decimal conversion and explicit quantization modes: UNNECESSARY, DOWN, UP, FLOOR, CEILING, HALF_UP and HALF_EVEN.
- Added 1,000 deterministic rational property cases, language-neutral division vectors and a dedicated Python 3.11–3.13 CI step. Run [#43594118145](https://github.com/PandaGarry/NEXUS/actions/runs/43594118145) passed exact PR HEAD `a46b49a2cbb7a5960ce483f93a736a3fbc945554`: eight isolated suites, 127 tests per runtime / 381 matrix executions. Operation-specific financial rounding policies remain unapproved.


### Added — Instrument quantity-unit semantics reference (test-only; CI verified)
- Added `InstrumentUnitModel`, explicitly bound to an immutable `InstrumentSpec` version, for spot base-asset quantities, linear contract counts and inverse contract counts.
- Linear multiplier is typed as base-asset units per contract; inverse multiplier is typed as quote-asset units per contract. Inverse base exposure and QUANTO remain explicitly blocked.
- Added a dedicated 16-test Python 3.11–3.13 conformance suite. Run [#43593795698](https://github.com/PandaGarry/NEXUS/actions/runs/43593795698) passed exact HEAD `ba8df9def72bff82625669bc236430bb8d21592d`: seven isolated suites, 109 tests per runtime and 327 matrix executions. No production venue mapping or order authority is implied.


### Added — Dimensional financial types reference (test-only; CI verified)
- Added `AssetAmount`, `Money`, `Price`, `Notional` and instrument-scoped `ContractCount`, backed exclusively by `ExactDecimal`.
- Added 16 focused tests for exact quote notional calculation, unit compatibility, cross-dimension rejection, contract-count separation and signed position deltas.
- Added the dedicated suite to the Python 3.11–3.13 reference-model workflow. PR run [#43593305970](https://github.com/PandaGarry/NEXUS/actions/runs/43593305970) checked out merge ref `5f8dad3` (PR code/workflow head `5a1369435dd9024191f193df70651f1c00a36c6e` merged into base `3458ffac87adda08650a040f6be0861784fb509b`): six isolated suites, 93 tests per runtime and 279 matrix executions. This remains test-only evidence; no production domain types, FX, derivatives, margin, fees, P&L or accounting policy are implemented.


### Added — Append-only instrument registry reference (stacked Draft PR; CI verified)
- Added a test-only in-memory registry for immutable InstrumentSpec snapshots: historical lookup, idempotent identical replays, same-version content conflicts, monotonic version checks, stable internal identity checks and effective-time regression checks across unknown intermediate timestamps.
- Added 12 deterministic registry tests and a dedicated Python 3.11–3.13 CI step. Run [#43592862627](https://github.com/PandaGarry/NEXUS/actions/runs/43592862627) passed exact code/index HEAD `7654c67774f3b6131b498a57c5de6b6621f6513f` across Python 3.11–3.13: 77 tests per runtime across all five reference suites. No persistence, concurrent-writer protocol, venue source precedence, freshness policy or production authority is implemented.


### Added — Instrument specification reference slice (stacked Draft PR; CI verified)
- Added immutable venue-neutral instrument snapshots with explicit identity, market/contract/lifecycle types, provenance and timestamps.
- Added exact tick-size, quantity-step, min/max quantity and minimum-notional checks; UNKNOWN metadata fails closed and NOT_APPLICABLE must be explicit.
- Added a synthetic fixture and 17 focused tests. Exact implementation HEAD `b8eee65facd3f62d351c803844005c41ddd245b5` passed GitHub Actions run [#43592464265](https://github.com/PandaGarry/NEXUS/actions/runs/43592464265) on Python 3.11–3.13. This evidence is code-test-only; derivative validation, spot quote-quantity semantics, venue adapters, registry persistence, freshness policy, contract formulas and production order authority are explicitly out of scope.


### Fixed — Serialized recovery ownership
- Restart recovery now serializes its scan and state transitions in one write transaction, then conditionally changes only commands still in DISPATCHING. This prevents a late response committed before recovery from being overwritten and prevents concurrent recovery workers from claiming the same row twice in the local SQLite reference model.
- Added a two-connection recovery race test. The command-gateway reference suite now contains 24 tests.
- GitHub Actions run [#43591524490](https://github.com/PandaGarry/NEXUS/actions/runs/43591524490) passed exact PR HEAD `4f836d0f9d1a43161927331c05e6cc19bb12072b` on Python 3.11–3.13 (11 decimal + 24 gateway + 13 egress tests per runtime). This is local SQLite reference evidence only; it does not establish distributed recovery or egress fencing.


### Fixed — Stale dispatcher state transitions
- Added compare-and-swap guards to the post-marker pre-send rejection and adapter-error paths. If recovery has already moved a command out of DISPATCHING, a stale worker can no longer overwrite OUTCOME_UNKNOWN; it records a separate dispatch observation instead.
- Added two adversarial tests for recovery during the final pre-send guard and during a simulated ambiguous adapter timeout. The gateway reference suite now has 23 tests.
- GitHub Actions run [#43591389103](https://github.com/PandaGarry/NEXUS/actions/runs/43591389103) passed exact PR HEAD `f2dc357e9c65f0c2e108e670c4211bb36ff1a162` on Python 3.11–3.13 (11 decimal + 23 gateway + 13 egress tests per runtime). This is test-only state-integrity evidence; stale network egress remains unresolved.


### Added — Egress authority handover reference model
- Added a test-only control-plane state machine and 13 deterministic tests for freeze, fence-attestation sequencing, reconciliation gating, epoch transition and fail-closed behavior. GitHub Actions run [#43590804814](https://github.com/PandaGarry/NEXUS/actions/runs/43590804814) passed exact branch HEAD `a7ee5426077005a6135e9f1b6f1c4044cc41d459` on Python 3.11–3.13. It checks protocol ordering only; it cannot revoke real network access, terminate stale hosts or verify trusted fence attestations. Actual egress fencing remains BLOCKED.
- Extended the Python reference-model CI matrix to run the egress handover suite on Python 3.11, 3.12 and 3.13.


### Added — Exact-decimal property verification
- Added 1,000 deterministic seeded property cases cross-checked against Python's independent rational `fractions.Fraction` representation for add/subtract/multiply/compare, canonical round-trip, step divisibility and exact quantization. GitHub Actions run [#43590395882](https://github.com/PandaGarry/NEXUS/actions/runs/43590395882) passed exact PR HEAD `3fb21aa53c9d6c72afcf6761493388f417fcb56b`: 11 decimal and 21 gateway tests on Python 3.11–3.13. This is reference-oracle evidence only.


### Updated — Execution control and evidence baseline
- Added [NX-PROJECT-CHECKLIST-001](docs/quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md), a living register for G0D D1–D8, engineering workstreams, ordered priorities, evidence rules and non-authorizations.
- Updated current verification evidence: GitHub Actions run [#43589753391](https://github.com/PandaGarry/NEXUS/actions/runs/43589753391) passed exact PR HEAD `b761f9249064f881cef994dfe8724b66034ebe02` with 10 exact-decimal and 21 gateway tests on Python 3.11–3.13.
- Explicitly deferred NX-ADR-006 because current strategy-validation governance is already covered by NX-ADR-003; reopen only if a distinct decision is identified.
- Corrected owner-decision status: OD-01/04 accepted, OD-15 partially accepted; no other owner decisions are inferred.


### Added
- NX-ARCH-002: proposed personal-first product/deployment profiles defining single-owner closed use, PERSONAL_DEV/PERSONAL_TEST/PERSONAL_PRODUCTION and separately gated future COMMERCIAL scope; no runtime enforcement or live authorization claimed.
- NX-IF-001: proposed Canonical Trade Command & Risk Approval Contract defining TradeIntent separation, immutable command envelope, canonicalization/digest, signed scoped approval capability, one-time consumption, invalidation and negative conformance matrix; implementation and tests not started.
- NX-IF-002: proposed Exposure Snapshot & Risk Reservation Contract defining exclusive exposure buckets, source ownership, durable reservations, atomic multi-scope capacity checks, fencing, partial-fill transfer, unknown-outcome retention and recovery/conformance scenarios; implementation and tests not started.
- NX-IF-003: proposed Execution Event & Ledger Posting Contract defining canonical fill identity, durable Execution outbox/Ledger inbox, atomic balanced journal posting, fee/correction handling, replay and projection-watermark exposure handoff; implementation and tests not started.
- NX-IF-004: proposed State Evidence, Freshness & Recovery Barrier Contract defining source-specific evidence vectors, freshness policies, quarantine/recovery cases, scoped generation-fenced barriers and restart/reconciliation ordering; implementation and tests not started.
- NX-IF-005: proposed Emergency Operations, Halt & Risk-Reduction Authorization Contract defining monotonic scoped halt epochs, command-class authorization, bounded emergency plans, protective-order handling, operator governance and controlled resume; implementation and tests not started.
- NX-OWNER-DECISIONS-001: proposed owner decision register consolidating OD-01..OD-15 across G0–G3; OD-01/04 accepted and OD-15 partially accepted by explicit owner direction, all other decisions remain open/deferred.
- NX-ARCH-REVIEW-001: proposed cross-specification review covering 12 interface and recovery findings, five bounded closure work packages and explicit design blockers; no implementation or runtime verification claimed.
- ТЗ-NX-006: proposed Portfolio & Financial Ledger requirements covering immutable journal events, exact accounting, balances/positions, P&L, fees/funding, reconciliation, snapshots and deterministic replay; implementation not started.
- ТЗ-NX-005: proposed Independent Risk Engine requirements covering deterministic pre-trade authorization, exact exposure calculation, hierarchical hard limits, concurrent risk reservations, signed payload-bound approvals, continuous monitoring and kill-switch governance; implementation not started.
- ТЗ-NX-004: proposed Autonomous Execution Engine requirements covering durable command/outbox, order lifecycle, ambiguous outcomes, private execution events, reconciliation, kill switch, credential isolation and adapter certification; implementation not started.
- ТЗ-NX-003: proposed Quant & Strategy Engine requirements covering immutable strategy artifacts, deterministic DecisionContext/TradeIntent contracts, research provenance, bias controls, simulation fidelity and promotion gates; implementation not started.
- ТЗ-NX-002: proposed requirements for Footprint, Delta/CVD, DOM, Tape, Volume Profile, TPO, quality, replay and golden tests; implementation not started.
- NX-ADR-001: proposed canonical market-event envelope, typed payload semantics, provenance, exact units, ordering and schema evolution; no implementation claimed.
- NX-ARCH-001: proposed logical architecture, trust boundaries, deployment baseline and critical command/data flows; no technology stack selected.
- NX-RESEARCH-001: initial evidence-based comparison of HFTBacktest, QuantConnect LEAN and ABIDES; no engine selected.
- NX-WP-001: рабочий регламент AI Project Lead с правилами исследования, evidence, контроля качества, согласований и Definition of Done.
- NX-OPS-001: ежедневный pulse, еженедельный deep review и событийный анализ внешних изменений.

### Added — Project foundation
- Создана базовая структура документации NEXUS TRADING.
- Зафиксированы устав проекта, текущий статус, roadmap и readiness gates.
- Добавлены реестры ADR, спецификаций, исследований и безопасности.

### Added — Foundation documentation review and domain reference slice
- NX-DOC-REVIEW-001: bounded final documentation review with PR integration findings, cross-document corrections, G0 close-out packages and finite exit criteria.
- NX-ARCH-003: proposed venue-neutral exact numeric domain-kernel contract; production language, numeric bounds and rounding policy remain open.
- Added a dependency-free Python exact-decimal reference oracle plus language-neutral golden vectors v1.0.0 (15 cases) and 10 unit tests for parsing, canonicalization, exact arithmetic, comparison, quantization and tick/lot divisibility. Local tests passed; this is not production runtime evidence.
- Corrected NX-ARCH-001 stale reference to NX-ADR-001 and added a separate G0D documentation-baseline gate. No prototype/live permission is granted.

### Added — Reference platform fit assessment
- NX-RESEARCH-006: evidence-backed first assessment of NautilusTrader against NEXUS execution, risk, persistence, reconciliation, numeric and simulation contracts. NautilusTrader remains a leading candidate, not selected; no dependency integration or live use authorized.
- Project status distinguishes isolated execution of the 10 exact-decimal reference tests from unavailable GitHub Actions evidence and absent production runtime.

### Added — NautilusTrader v2 release baseline review
- NX-RESEARCH-007: pinned v2.0.0rc9 tag/commit, verified its pre-release status and compared it with the previously inspected develop snapshot (diverged histories: 77 ahead / 72 behind).
- Recorded RC9 precision conversion, SBE compatibility, at-least-once Redis retry and modify/cancel-denied semantics as mandatory NEXUS conformance topics.
- NautilusTrader remains a leading candidate, not selected; RC9 is test-only and not approved for production use.

### Added — NautilusTrader RC9 execution boundary audit
- NX-RESEARCH-008: exact v2.0.0rc9 source audit confirms asynchronous best-effort persistence before transport, non-universal RiskEngine routing and process-local dispatched-order markers absent after restart.
- NautilusTrader is not approved as NEXUS execution authority. NEXUS-owned durable outbox, non-bypassable Risk gateway, ledger and recovery barrier remain mandatory.

### Added — Dispatcher authority transfer and egress fencing
- NX-REF-EXEC-002 proposes an account-scoped authority-transfer protocol: freeze, advance epoch, positively fence old egress, quarantine ambiguous attempts, reconcile venue evidence, then grant new egress capability. Lease expiry alone is explicitly not a fence. Design only; no production mechanism implemented.

### Added — Command gateway reference conformance slice
- NX-REF-EXEC-001 and `foundation/reference-model/execution-gateway/`: a narrow Python/SQLite test model for payload-bound CREATE authorization, one-time approval/reservation consumption, durable-before-dispatch state, and conservative unknown-outcome recovery.
- Added 21 deterministic fault and negative-path tests, including two independent SQLite-connection race tests and an explicit split-brain counterexample showing a stale worker can still send after recovery. A local state-CAS guard now rejects its late ACK as an authoritative transition and records it as a stale venue observation, preserving OUTCOME_UNKNOWN. Egress fencing remains unresolved; this is not a safety pass. The model is explicitly test-only; no production signer, database, multi-process fencing, Risk calculation, ledger or venue integration is claimed.
- Added GitHub Actions conformance workflow for the exact-decimal and command-gateway reference suites on Python 3.11, 3.12 and 3.13. Run #43588971888 passed on exact HEAD `d22d417da0d11dab5b9bb79298edd379eab46867`; both suites passed on all three runtimes (10 + 20 tests per runtime at that historical revision). The two-connection concurrency cases exercise local SQLite transaction serialization only, not distributed leases/fencing. A later adversarial counterexample reproduces stale-worker egress after recovery. A follow-up state-CAS guard prevents stale ACK overwrite and records late responses as observations; its code revision passed CI on Python 3.11–3.13. This remains reference-model evidence only.

### Added — Operation-specific financial rounding and valuation contract (proposed; documentation only)
- Added NX-REF-DOMAIN-009 covering tick/lot normalization, minimum notional, fees, funding, realized/unrealized P&L, margin, liquidation, FX/collateral valuation and Ledger posting/reconciliation.
- Defined exactness, dimensionality, provenance, no-implicit-rounding invariants; separated authoritative venue/account facts from estimates and display values.
- Added explicit BLOCKED/OWNER-DECISION boundaries, evidence classes, a venue qualification dossier and a language-neutral fixture schema.
- Comparative official Binance Spot, OKX and Bybit documentation is cited as evidence of product differences only; no venue/product/account or production policy is selected.
- Documentation only: no calculator, runtime, numeric limits, rounding defaults, venue adapter or live capability added.

### Added — Venue-neutral financial math fixtures (test-only)
- Added NX-REF-DOMAIN-010 and language-neutral synthetic vectors for spot notional, explicit linear contract notional, inverse rational exposure and partial-fill weighted-average arithmetic.
- Added independent rational-oracle assertions, dimension/instrument-identity negative tests and exact non-terminating rational preservation.
- Added the new test suite to the Python 3.11–3.13 reference workflow.
- No venue, fee/funding/P&L/margin/liquidation/FX/accounting policy or production rounding rule was selected.

### Expanded — Deterministic financial math property checks
- Added 650 seeded property cases across spot notional, partial-fill permutation/partition invariance and inverse exposure identity.
- Exact code/test commit `0f0b44e927aacf67d6f7a5678b160b3e3c6088e0` passed 182 tests per runtime on Python 3.11–3.13 in GitHub Actions run [#43596851904](https://github.com/PandaGarry/NEXUS/actions/runs/43596851904).
- No production policy or venue/account behavior is inferred from these synthetic tests.

### Added — Russia jurisdiction and venue eligibility research (documentation only)
- Added NX-RESEARCH-009 with Federal Law No. 282-FZ, CBR guidance, Directive 7441-U, domestic regulated crypto products and foreign venue eligibility.
- Recorded the 2026-11-17 effective date of Directive 7441-U, RUB 300,000 annual cumulative broker-acquisition cap for non-qualified residents, and BTC/ETH/USDT eligible-admission list; scope for crypto-exchange organizations remains subject to legal interpretation.
- Added proposed NX-ADR-007 for a scope-bound VenueEligibilityRecord, fail-closed adapter states, separate Risk authorization and trusted-egress eligibility fencing.
- Added NX-REF-VENUE-001 test-only evidence evaluator and 28 conformance tests.
- Added NX-REF-VENUE-002 single-process egress fencing reference and 21 race/ordering tests; CI run 43599182263 passed 231 tests/runtime on Python 3.11/3.12/3.13 (693 executions).
- Updated historical venue research, architecture index, roadmap, project status and checklist. No venue selected, no live capability or production code added.

### Added — Rust execution and cross-language conformance architecture (proposed; documentation only)

- Added NX-ARCH-004 defining candidate Rust domain/execution boundaries, NEXUS-owned command/Risk/trusted-egress authority, adapter evidence classes, exact numeric constraints, language-neutral conformance fixtures and adversarial failure scenarios.
- Created Issue #15 and branch `engineering/rust-execution-domain-conformance-v0`, based on exact PR #14 head `ab6976933cb4de9b5320b73531034d02edc53907`.
- Updated architecture index, project checklist, roadmap and project status.
- No Rust source, Cargo workspace, production numeric limits, venue adapter, credentials, network egress or live-trading capability added. Python models remain test-only references; no Rust/Python conformance is claimed.


### Updated — Execution ordering cross-contract harmonization (proposed; documentation only)

- Corrected NX-ADR-002 so all required `PRE_DISPATCH_RESERVATION` scopes are durably committed before Risk issues a `RiskApprovalCapability`.
- Made single-use approval consumption atomic with the durable canonical command/reservation-reference/outbox commit.
- Clarified the pre-egress attempt marker and conservative `DISPATCH_OUTCOME_UNKNOWN` exposure semantics across crashes before/during/after network send.
- Updated NX-ARCH-004, architecture index, project checklist, status and roadmap after cross-review against NX-IF-001..005, NX-ARCH-003, NX-ADR-002/005/007 and NX-SEC-001.
- No runtime, Rust source, database transaction, signer, network fence, venue adapter or live-trading capability was added; owner acceptance and G0D/G1 gates remain open.


### Added — Language-neutral conformance fixture and runner contract (proposed; documentation only)

- Added NX-ARCH-005 after auditing existing decimal, rational, numeric-wire, financial-math and instrument-spec fixture formats.
- Defined a proposed common fixture envelope, tagged VALUE/REJECT outcomes, stable rejection classes, strict typed comparison rules, suite versioning and migration policy.
- Defined deterministic runner responsibilities, normalized reports, CI provenance/evidence and layered differential/property/adversarial test strategy.
- Confirmed the tracked repository has no Cargo workspace, Rust toolchain pin, Rust source tree or Rust runner; no Rust implementation is started before G0D/G1 approval.
- Existing v1 fixture files and current Python unittest workflows remain unchanged. No schema validator, runner or cross-language conformance is claimed.

- Added a per-family legacy fixture migration assessment to NX-ARCH-005, distinguishing structural conversion from rejection-class annotation and newly derived instrument-spec expectations; all existing v1 files remain untouched.

- Expanded NX-ARCH-005 with an initial operation-ID/input/result registry and stable error mapping. Added catch-compatible typed numeric-wire error subclasses and tests for stable error classes; existing callers can continue catching `NumericWireError`. Updated the reference-model README and operation registry. No fixture migration or production parser qualification is claimed.

- Added strict fixture-ingestion requirements to NX-ARCH-005: UTF-8 validation, duplicate-key/non-finite/float rejection, bounded control integers, raw-byte SHA-256 and explicit runner resource limits. No validator or runner implementation is claimed.

### Corrected — NX-ARCH-005 contract-to-code cross-review (2026-11-14)

- Fixed the illustrative fixture envelope so it is valid strict JSON.
- Distinguished implemented decimal/rational and numeric-wire reference APIs from financial fixture operation labels that do not yet have callable reference implementations/adapters.
- Kept instrument-spec operation migration deferred and clarified that non-numeric rejection classes require reviewed operation-aware mapping, never exception-message parsing.
- Documentation and audit refinement only; no fixture migration, schema validator, runner, Rust source or production numeric profile added.

### Audit correction — financial and numeric reference coverage (2026-11-14)

- Corrected the earlier NX-ARCH-005 audit statement: spot, linear and inverse financial math paths have executable reference coverage through `domain_types.py` / `instrument_units.py` and the financial fixture suite.
- Identified partial-fill weighted-average aggregation as tested but inline-only; extraction to a reusable pure oracle remains follow-up work.
- Clarified arbitrary-precision oracle versus explicit bounded numeric wrapper, candidate resource-limit mapping, and malformed API input versus mathematical inexactness.
- Documentation correction only; no production numeric profile or Rust implementation added.


### Added — typed partial-fill aggregation reference operation (2026-11-14)

- Extracted weighted-average partial-fill arithmetic into `financial_aggregation.aggregate_partial_fills`.
- Returns typed base-asset quantity, quote notional and an exact rational weighted-average price; does not silently round non-terminating results.
- Updated golden-vector and seeded permutation/partition tests to use the named callable; added empty-input, dimension-mismatch and non-terminating-average tests.
- Updated NX-ARCH-005 audit, reference README, checklist, roadmap and project status. This is a test-only arithmetic oracle, not venue fill validation or production financial policy. Normalized fixture/schema/runner work remains owner-review gated.

- Added a zero-total-quantity regression: the partial-fill helper preserves the typed `DivisionByZero` path, distinct from empty-input and malformed-argument failures.


### Updated — operation-specific reference exception audit (2026-11-14)

- Added a proposed operation-to-exception-to-rejection mapping audit in NX-ARCH-005 for decimal, rational, bounded numeric, dimensional, instrument-unit and partial-fill operations.
- Explicitly separated mathematical failures from malformed API parameters/types and identified unresolved domain-invalid-value/identity cases.
- Prohibited exception-message parsing and retained owner approval as a prerequisite for normalized schema/runner behavior.
- Documentation/audit only; no stable wire mapping, validator, runner or production adapter is approved.


### Fixed — exact divisibility API type boundary (2026-11-14)

- `ExactDecimal.is_multiple_of` now validates that `step` is an `ExactDecimal` before accessing its fields and raises explicit `TypeError` for malformed operand types.
- Added a regression test; non-positive exact-decimal steps continue to raise the existing typed `InvalidStep`.
- This is a reference-model API-hardening change, not a new numeric policy or production implementation.


### Clarified — pre-egress exposure transition (2026-11-14)

### Corrected — stale reservation/dispatch review finding (2026-11-14)

- Refreshed NX-ARCH-REVIEW-001 F-02: its original statement that reservation/command ordering was unspecified had become stale after NX-IF-001 / NX-IF-002 / NX-ADR-002 were harmonized.
- Marked the finding partially resolved at design level only and enumerated the remaining owner, transaction/isolation, crash/concurrency, reservation-lifecycle and egress-fence proof requirements.
- Updated the living checklist and project status. No implementation, transaction guarantee or live authorization added.


- Reworded the NX-IF-002 lifecycle row to require the durable pre-egress attempt marker before any network side effect.
- Explicitly separated the marker from proof of transmission and retained conservative exposure through outcome reconciliation.
- Recorded the cross-contract clarification in NX-ARCH-REVIEW-001, checklist, project status and roadmap. No runtime behavior or production safety guarantee is implied.


### Added — transaction decomposition and execution crash-point matrix (2026-11-14)

- Expanded NX-REF-EXEC-002 with the recommended logical transaction split: Risk commits all required reservations before approval; Command atomically consumes the single-use capability with canonical command/reservation-reference/outbox persistence; dispatcher records the pre-egress attempt marker; trusted Egress owns credentials and the actual venue socket.
- Explicitly avoided claiming a distributed ACID transaction across Risk and Command. Added ambiguous-commit recovery by stable idempotency identity and conservative reservation retention.
- Added a crash-point matrix from reservation/capability through socket write, venue acceptance, fills/Ledger posting, halt takeover and RecoveryBarrier.
- Kept database/isolation, capability signing, host/network fence, provider, availability and operator decisions open under OD-08/09/10/12. Design/test plan only; no production runtime, credentials or egress fence implemented.


### Added — Persistence and trusted-egress option analysis (2026-11-14)

Expanded NX-REF-EXEC-002 §4.5 with an evidence-oriented comparison of relational/service-owned transaction boundaries, separate databases and event-store coordination, plus DB lease, proxy/gateway, isolated workload and dedicated-host egress options. Recorded a candidate baseline without selecting a provider: separate Risk and Command local ACID commits; one account-scoped credential/socket-owning Egress Authority; positive independently enforced old-generation fencing before takeover; fail-closed CREATE halt when fence evidence is absent. OD-08/09/10/12 remain open. Documentation-only; no implementation or new CI evidence claimed.



### Exact-head CI verification after persistence/egress analysis — 2026-11-14

- Documentation analysis head verified: `3187a69e443157ac3e66b874b4dcbb29588ddc70`.
- GitHub Actions run [#43606550889](https://github.com/PandaGarry/NEXUS/actions/runs/43606550889) completed successfully on that exact head.
- Three jobs passed: Python 3.11, 3.12 and 3.13. Each executed 13 isolated reference-model suites with counts 11, 24, 13, 17, 12, 16, 18, 18, 32, 12, 15, 28 and 21 = 237 tests per runtime; 711 successful test executions total.
- This CI run verifies the existing Python reference-model suites at the exact documentation-analysis head. It does not test the newly documented transaction alternatives, database isolation, production egress topology, external host/network fencing, Rust, venue behavior or live safety.


### Added — Open-source component qualification shortlist (2026-11-14)

Published NX-RESEARCH-010. PostgreSQL, OpenTelemetry Collector, OpenBao, NATS JetStream, Cilium and Temporal are qualified by potential role and gate; NautilusTrader's existing test-only disposition is retained. Established explicit authority exclusions and dependency qualification requirements. Research only: no dependency, package, runtime service, broker, database, vault or deployment topology added.
