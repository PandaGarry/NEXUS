# Changelog

Заметные изменения проекта фиксируются в обратном хронологическом порядке. Release notes пишутся понятным языком; инженерные детали остаются в ADR/PR.

## Unreleased

### Clarified — Execution preflight versus Trusted Egress final authorization (2026-11-14)

- Reframed NX-IF-001 Execution checks as non-authorizing preflight and defense in depth.
- Made Trusted Egress the sole final send-authorization boundary: it reloads persisted evidence, serializes the one-use gate with halt generation, and alone initiates the venue socket.
- Explicitly tied the gate-first halt race to pending-attempt drain/fencing before HALTED acknowledgement.
- No runtime, credential, signer, database schema or network fence was implemented.


### Added — Capability authorization cross-review (2026-11-14)

- Added NX-ARCH-REVIEW-003 reviewing the capability catalog, scope/data-classification model, entitlement separation and request-time authorization.
- Constrained billing subscription management to intent submission; Billing alone validates provider state and writes entitlement lifecycle.
- Added CAP-R-02..09 findings and CAP-19..26 adversarial scenarios covering canonicalization, projection leakage, forged payment claims, webhook replay, audit custody and outage independence.
- Synchronized architecture index, checklist, status and roadmap. Design review only; no candidate capability or grant was approved or activated.

### Added — Capability catalog and authorization contract model (2026-11-14)

- Added NX-ARCH-009 defining platform-owned capability identities/versions, ownership and enforcement authority, typed scopes, data classifications and request-time decision semantics.
- Proposed an initial first-party capability catalog and mapped module consumers to owner services, scope rules and negative tests.
- Explicitly excluded protected financial mutation and Trusted Egress from optional-module grants; separated workload grants from commercial entitlements and user authorization.
- Added revocation/cache/outage, audit/privacy requirements and 18 adversarial CAP scenarios.
- Synchronized architecture index, checklist, status and roadmap. Design only; no executable schema, policy engine, grant, permission, module runtime or dependency created.

### Added — Module governance cross-architecture review (2026-11-14)

- Added NX-ARCH-REVIEW-002, reviewing NX-ARCH-001/006/007/008, NX-SEC-001, NX-IF-001..005 and NX-OWNER-DECISIONS-001.
- Clarified gateway admission versus owning-service authorization and confirmed T4 is not a shared Risk/Command/Ledger/Egress identity or permission set.
- Retained F-03..F-08 as open blockers covering executable permission mapping, revocation objectives, trust roots, actual DB/host/network isolation, first G1 module/resource budgets and operator/support governance.
- Synchronized architecture index, checklist, status and roadmap. Design cross-review only; no gate, owner decision or implementation authorization is closed.

### Final synchronized documentation-head verification — 2026-11-14

The synchronized documentation head `c5c00d37b26f365b79690a9f3297ab571d9ec6f2` passed [GitHub Actions #43611122433](https://github.com/PandaGarry/NEXUS/actions/runs/43611122433): Python 3.11/3.12/3.13 all succeeded, 13 isolated reference-model suites / 237 tests per runtime (711 executions). This is reference regression only; no NX-ARCH-008 registry, identity, grants, module isolation, secrets, database permissions, egress, Rust, venue or live safety is tested. NX-ARCH-008 remains design-only; G0D/G1 remain open.

### Verification — NX-ARCH-008 documentation head (2026-11-14)

Exact branch HEAD `b1d3201a1fe1706909218943f5464eba43ea1041` passed [GitHub Actions #43611030968](https://github.com/PandaGarry/NEXUS/actions/runs/43611030968): Python 3.11/3.12/3.13 all succeeded, 13 isolated reference-model suites / 237 tests per runtime (711 executions). This verifies existing Python reference regression only; it does not test the proposed module registry, grants, identity, isolation, secrets, DB permissions, egress, Rust, venues or live safety. NX-ARCH-008 remains design-only; G0D/G1 remain open.

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


### Added — Modular product boundaries and trust isolation proposal (2026-11-14)

- Added NX-ARCH-006 defining a protected domain core and independently governed product modules behind versioned contracts and deny-by-default admission.
- Specified workload identities, least-privilege capability grants, signed immutable artifact admission, module data ownership, failure containment, rollback and adversarial verification requirements.
- Defined Identity & Access as security-critical but non-authoritative for Risk/Ledger/venue egress; proposed Demo and Learning/Wiki as separate bounded domains.
- Required hard Demo/live separation through distinct account namespace and ledger, simulator-only execution, independent storage permissions and no route to production credentials/live egress.
- Preferred an initial modular monolith / limited trust-domain split over premature microservices or arbitrary in-process plugin loading.
- Updated architecture index, living checklist, project status and roadmap. Design only: no service, package, identity provider, plugin framework, database, deployment topology, public registration or live capability added; cross-review and owner/security approval remain open.


### Exact-head reference CI for modular architecture documentation increment — 2026-11-14

The then-current branch head `e15e47f9512bc07a1f6534a4f41b0d27d7d42578` passed GitHub Actions [#43608583358](https://github.com/PandaGarry/NEXUS/actions/runs/43608583358). Python 3.11, 3.12 and 3.13 jobs all succeeded; each ran 13 isolated reference suites / 237 tests (711 successful executions total). This verifies existing Python reference-model regression only. It does not test NX-ARCH-006 module isolation, identity/authentication, database boundaries, secret handling, runtime integration, egress fencing or live trading.


### Added — Platform extensibility and entitlement foundation proposal (2026-11-14)

- Added NX-ARCH-007 with a candidate long-term product-domain taxonomy and modular platform extension principles.
- Separated product capability, commercial entitlement and security authorization; payment status, plans and feature flags cannot grant Risk/Ledger/venue/egress authority.
- Specified stable feature identifiers, auditable entitlement grants, subscription lifecycle, replay-safe billing event processing, product quotas distinct from trading Risk limits, downgrade/data-retention behavior and compatibility rules.
- Preserved multi-tenancy, public SaaS, paid plans, payment providers, registration and commercial launch as future gated decisions, not v1 commitments.
- Updated architecture index, checklist, project status and roadmap. Design only; no payment integration, subscription service, tenant runtime, module or product feature implemented.


### Added — Capability-to-interface contract traceability review (2026-11-14)

- Added NX-ARCH-REVIEW-004 after locating and inspecting the actual canonical NX-IF-001..005, NX-SEC-001 and owner decision register paths.
- Mapped every NX-ARCH-009 candidate capability to existing contract evidence or an explicit missing product-domain contract; no endpoints or permissions were invented.
- Reaffirmed protected Risk/reservation, command/egress, Ledger, recovery/halt and credential boundaries; optional modules receive no direct authority over them.
- Added a source-grounded data inventory, cross-cutting contract checklist, open findings and G0D/G1 gates.
- Updated architecture index, project checklist, status and roadmap. Design traceability only; no executable schema, grant, policy engine, runtime, dependency or production integration added.


### Exact-head regression evidence for NX-ARCH-REVIEW-004 — 2026-11-14

Exact branch HEAD `f78fc7d006ea475cf596ee2bd8bd65b9a7d37afa` passed GitHub Actions [#43613212116](https://github.com/PandaGarry/NEXUS/actions/runs/43613212116): Python 3.11/3.12/3.13, 13 isolated suites / 237 tests per runtime, 711 successful executions. This is Python reference-model regression only; it does not execute the new traceability artifact, capability policy, domain APIs, grants, module isolation, Rust or venue behavior. No capability or runtime was activated.


### Added — Revocation, freshness and control-plane outage objective proposal (2026-11-14)

- Added NX-ARCH-REVIEW-005 reconciling NX-ARCH-008/009 revocation, NX-IF-004 source freshness/recovery, NX-IF-005 halt propagation and NX-SEC-001 credential isolation.
- Separated authorization freshness, data freshness, control propagation and RecoveryBarrier readiness; defined a control-plane outage matrix and in-flight side-effect semantics.
- Proposed conservative numeric targets only for low-risk authorization cache and cancellation discussion. They are explicitly not accepted SLOs, production guarantees or defaults.
- Kept venue/source freshness thresholds, halt deadline, RTO/RPO, OD-10 and OD-12 owner decisions open. No executable policy, cache, revocation service, dependency, secret manager, network fence or runtime added.
- Updated architecture index, checklist, status, roadmap and changelog.


### Exact-head regression evidence for NX-ARCH-REVIEW-005 — 2026-11-14

Exact branch HEAD `97a1819527bf6b1973793b12a084ef8cd0dee776` passed GitHub Actions [#43613493976](https://github.com/PandaGarry/NEXUS/actions/runs/43613493976): Python 3.11/3.12/3.13, 13 reference-model suites / 237 tests per runtime, 711 successful executions. This does not validate the proposed authorization cache/revocation targets, outage matrix, source freshness, halt propagation, cancellation or runtime isolation. No numeric objective was accepted and no runtime control was implemented.

### CI action supply-chain hardening and exact-head verification — 2026-11-14

- Updated `.github/workflows/reference-model.yml` from Node 20-era action releases to `actions/checkout` v7.0.1 and `actions/setup-python` v7.1.0.
- Pinned the actions to verified upstream full commit SHAs: `3d3c42e5aac5ba805825da76410c181273ba90b1` and `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`.
- Exact action-upgrade HEAD `e35d81cb34aeae1c13e25def0320e8a4a4b649bb` passed [workflow #43614458632](https://github.com/PandaGarry/NEXUS/actions/runs/43614458632): 13 isolated suites / 237 tests on each of Python 3.11, 3.12 and 3.13; 711 successful executions.
- Verified the previous Node.js 20 and `punycode` deprecation warnings are absent from all three job logs.
- Audited the stacked PR ancestry: #13 -> #14 -> #16; each child base SHA equals the parent head SHA. No base retarget, merge or stack rewrite performed.
- This verifies existing Python reference models and CI action execution only. It does not establish Rust conformance, transitive dependency integrity, production persistence/egress safety, venue behavior or live readiness.


### Numeric wire parser resource-boundary hardening — 2026-11-14

- Added an explicit decimal max_scale option; absent an override, the reference parser bounds scale by the caller-supplied max_chars budget.
- Normalized interpreter integer-string conversion budget failures into the stable NUMERIC.RESOURCE_LIMIT rejection for decimal coefficient/scale and rational numerator/denominator parsing.
- Added adversarial tests for extreme scales and oversized integer strings.
- Exact code/test HEAD b0fb99d4505ba5eb405788fee8ce447f28437479 passed [workflow #43614612130](https://github.com/PandaGarry/NEXUS/actions/runs/43614612130): 13 suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 successful executions).
- Test-only reference hardening; no production numeric profile, normalized fixture runner or Rust implementation was introduced.

### COSE signing profile corrected to fully specified Ed25519 — 2026-11-14

- Standards review found RFC 9053's polymorphic COSE EdDSA identifier (-8) is superseded for fully specified algorithm selection by RFC 9864.
- Updated NX-ADR-008 to use COSE Ed25519 algorithm identifier -19, with OKP / Ed25519 key constraints.
- Added rejection requirements for deprecated -8, Ed448, algorithm/key mismatch and substitution.
- Clarified that protected `kid` is a lookup hint, not a unique or security-authoritative identity; key resolution must bind issuer, algorithm, purpose, status and registry generation and fail closed on ambiguity.
- No signer/verifier implementation, cryptographic dependency, key material or key custody provider was added.


### Strict deterministic CBOR ingress profile clarified — 2026-11-14

- Tightened NX-ADR-008 so deterministic CBOR is validated on ingress before object materialization, not merely emitted by the encoder.
- Require preferred shortest forms, definite lengths, RFC 8949 core bytewise-lexicographic map ordering, schema-defined text keys, duplicate/unknown-key rejection and rejection of trailing bytes.
- Explicitly reject legacy length-first ordering and parser behavior that silently normalizes malformed input.
- No CBOR library or runtime dependency selected; cross-language adversarial byte vectors and decoder qualification remain open.


### Full PR ancestry audit and exact-head CI — 2026-11-14

- Verified the direct stacked ancestry #1 -> #2 -> #3 -> #4 -> #5 -> #6 -> #7 -> #9 -> #10 -> #11 -> #12 -> #13 -> #14 -> #16 by exact child-base / parent-head SHA equality; PR #8 is a parallel branch.
- Confirmed all direct ancestors remain open/Draft/unmerged. PR #16's immediate base is correct (PR #14 head), but it is not independently mergeable until parent-first integration.
- Current PR #16 diff: 248 commits beyond base, 32 files, 4,399 additions, 72 deletions.
- Current exact branch HEAD `7914772358d2ee49c87374373bad5c589d0a2905` passed [workflow #43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349): 13 isolated suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 successful executions).
- Direct GitHub Actions are full-SHA pinned; no Node.js 20 or punycode deprecation warning appears in the verified logs.
- CI scope remains Python reference models only. No Rust, PostgreSQL, COSE, Trusted Egress, venue or live-execution evidence is implied. No PR was merged or retargeted.

### Final synchronized G1 baseline exact-head CI — 2026-11-14

- Exact branch HEAD `7914772358d2ee49c87374373bad5c589d0a2905` passed [workflow #43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349).
- Python 3.11, 3.12 and 3.13 each passed all 13 isolated suites / 239 tests; 717 successful executions total.
- All three logs show no test failures and no Node.js 20 / `punycode` deprecation warnings.
- Verification is limited to existing Python reference models; no Rust, CBOR/COSE, PostgreSQL, Trusted Egress, venue or live-safety implementation was exercised.

### Post-synchronization exact-head regression — 2026-11-14

- Branch HEAD `928d5fd261553676c3fad6a8e88b984a862af338` passed [workflow #43615282210](https://github.com/PandaGarry/NEXUS/actions/runs/43615282210).
- Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 successful executions).
- No test failures or Node.js 20 / `punycode` deprecation warnings. Evidence remains limited to Python reference models.


### Post-sync exact-head verification — 2026-11-14

- Normalized the final G1 checklist section order and verified exact HEAD `9e9035033da77d958601cb6b69128e13e2551a0d` with [workflow #43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737).
- All 13 isolated Python reference suites passed on Python 3.11/3.12/3.13: 239 tests per runtime, 717 executions total.
- No Node.js 20 or punycode deprecation warnings remain in the job logs.
- PR #16 remains a 265-commit / 32-file / 4,467-addition / 72-deletion Draft in the verified parent-first stack.
- No Rust runtime, production DB, signer, Trusted Egress, venue connection or live order path was introduced.

### Full stacked-PR ancestry and current exact-head CI — 2026-11-14

- Verified direct PR chain #1 → #2 → #3 → #4 → #5 → #6 → #7 → #9 → #10 → #11 → #12 → #13 → #14 → #16 by exact parent-head / child-base SHA equality. PR #8 is parallel from #7, not an ancestor of #16.
- All direct-chain PRs remain open/Draft/unmerged; #16 correctly targets #14's head.
- Exact PR #16 head `9e9035033da77d958601cb6b69128e13e2551a0d` passed [workflow #43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737): Python 3.11/3.12/3.13, 13 suites / 239 tests each, 717 successful executions.
- No failures or Node.js 20 / `punycode` deprecation warnings. This is Python reference-model CI only, not Rust, persistence, Trusted Egress, venue or live-safety evidence.

### CBOR / COSE library qualification — NX-RESEARCH-011 — 2026-11-14

- Added a standards- and source-grounded comparison of Rust `cbor2`, `cbor-core`, `coset`, `cose2` and Python `pycose`.
- Identified `cbor2` as a deterministic encoder/raw-value candidate but not a strict NEXUS ingress decoder alone.
- Rejected `cbor-core` as a drop-in codec due to draft profile, length-first ordering and unstable API.
- Identified `coset` 0.4.2 as the leading test-only COSE structure candidate for RFC 9864 alg=-19, with original protected-header preservation and custom crypto closures.
- Recorded that `cose2`'s bundled Ed25519 provider uses deprecated alg=-8; no signer, verifier or dependency was adopted.
- No Cargo workspace, package, key, parser or runtime was introduced. G0D/G1 qualification remains open.

### CBOR command-key profile refined — 2026-11-14

- Restricted command map keys to schema-defined ASCII text field names; non-ASCII, unknown and duplicate keys are rejected.
- Kept Unicode user text in values with strict UTF-8 handling and no implicit normalization.
- Updated NX-ADR-008, OD-08 and the living checklist. No parser or dependency was implemented.

### Exact-head CI after NX-RESEARCH-011 — 2026-11-14

- Branch HEAD `1bb2192e6746e0f86659f006ef204990adc81188` passed [workflow #43615753905](https://github.com/PandaGarry/NEXUS/actions/runs/43615753905).
- Python 3.11, 3.12 and 3.13 passed 13 isolated suites / 239 tests each (717 successful executions).
- No test failures or Node.js 20 / `punycode` deprecation warnings. Verification is limited to Python reference models.

### Final action-runtime and exact-head verification — 2026-11-14

- Exact branch HEAD `69657a0808b859b17ab94a6d3e008a2ae9671cc7` passed [workflow #43615820603](https://github.com/PandaGarry/NEXUS/actions/runs/43615820603): 13 suites / 239 tests on Python 3.11/3.12/3.13 (717 executions).
- No test failures or Node.js 20 / `punycode` deprecation warnings.
- Verified the exact pinned checkout v7.0.1 and setup-python v7.1.0 action manifests both use Node 24.
- Evidence remains limited to Python reference models and action runtime; no Rust, CBOR/COSE, PostgreSQL, Trusted Egress or live behavior was exercised.

### COSE pre-verification trust boundary tightened — 2026-11-14

- Token-supplied kid/alg/issuer/audience are explicitly untrusted until signature verification.
- Key lookup is local, bounded and registry-backed; remote key discovery from token fields is forbidden.
- Signed issuer/audience must match locally expected context after verification; ambiguity, stale generation and revocation fail closed.
- Verification material is public OKP/Ed25519 only (32-byte public key, no private d outside Risk); signatures must be 64 bytes.
- No signer/verifier or key provider was implemented or selected.

### COSE_Sign1 wire representation made unambiguous — 2026-11-14

- Pinned the envelope to untagged, embedded-payload COSE_Sign1 with exactly four array elements.
- Protected header is restricted to alg=-19 and bounded byte-string kid; unprotected map is empty.
- Capability payload is a single NEXUS deterministic-CBOR map; exact protected and payload bytes are preserved.
- Sig_structure uses RFC 9052 §9 deterministic encoding and fixed non-caller-controlled external AAD.
- No implementation or dependency approved; byte-exact vectors remain required.

### COSE pre-verification key-resolution boundary tightened — 2026-11-14

- Treat token-supplied kid, alg, issuer and audience as untrusted until signature verification.
- Prohibit token-directed remote key retrieval; candidate lookup is bounded to a local versioned registry and local expected issuer/audience/algorithm/purpose.
- Require signed claims to match local expected context after verification; require exactly one eligible key or fail closed.
- Restrict Execution to public OKP/Ed25519 (32-byte public key); private key material remains within Risk; require 64-byte signature.
- Added corresponding negative-test requirements. No verifier or key registry was implemented.

### Exact-head CI after COSE key-resolution hardening — 2026-11-14

- Exact branch HEAD `6fefd9a44ff2f272b6516265d10f41c46a13cf7a` passed [workflow #43615911362](https://github.com/PandaGarry/NEXUS/actions/runs/43615911362).
- Python 3.11/3.12/3.13 each passed 13 suites / 239 tests (717 successful executions); no failures or Node.js 20 / `punycode` warnings.
- Evidence is Python reference-model regression only, not COSE/Rust/persistence/egress/venue/live proof.

### Exact-head CI after COSE profile refinement — 2026-11-14

- Branch HEAD `88fcb30068507d85fb35802ca5d2195fd528c000` passed [workflow #43616054657](https://github.com/PandaGarry/NEXUS/actions/runs/43616054657).
- Python 3.11/3.12/3.13 each passed 13 suites / 239 tests (717 successful executions); no test failures or Node.js 20 / `punycode` warnings.
- This verifies only Python reference models, not COSE signing/verification, Rust, key registry, persistence, egress or live behavior.

### Exact COSE profile and stacked-PR audit — 2026-11-14

- Verified PR #16 exact-head workflow [#43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308): 13 Python reference suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 successful executions); all job logs free of failures and Node.js 20 / `punycode` warnings.
- Re-verified direct PR ancestry #1→#2→#3→#4→#5→#6→#7→#9→#10→#11→#12→#13→#14→#16 by exact SHA equality; #8 is parallel. Direct-chain PRs remain open/Draft/unmerged.
- PR #16 snapshot at verification: 33 changed files, 4,937 additions, 72 deletions and 322 commits including stacked history.
- Synchronized exact COSE_Sign1 wire profile and key-resolution trust requirements across ADR, research, owner decisions, status, roadmap and checklist.
- CI proves Python reference-model regression only; no Rust, CBOR/COSE runtime, PostgreSQL, Trusted Egress, venue or live behavior.

### COSE_Sign1 wire-profile exact-head CI — 2026-11-14

- Branch HEAD `8d2c2f404782b718f1a3a422bb0ce918bb6b922d` passed [workflow #43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308).
- Python 3.11/3.12/3.13 each passed 13 suites / 239 tests (717 successful executions); no test failures or Node.js 20 / `punycode` warnings.
- This is reference-model regression only; no COSE parser, signer, verifier, key registry or cross-language vectors were executed.

### Final exact-head CI after COSE wire-profile synchronization — 2026-11-14

- Branch HEAD `71afa64c00affed017c1f072600f4f0e4aaeccc6` passed [workflow #43616247630](https://github.com/PandaGarry/NEXUS/actions/runs/43616247630).
- Python 3.11/3.12/3.13 each passed 13 suites / 239 tests (717 successful executions); no failures or Node.js 20 / `punycode` warnings.
- Verification remains Python reference-model only; no COSE, Rust, PostgreSQL, Trusted Egress, venue or live path was exercised.

### Final synchronized PR #16 exact-head CI — 2026-11-14

- Exact branch HEAD `3af0453897545b77fee358b9902a6301f662232e` passed [workflow #43616348161](https://github.com/PandaGarry/NEXUS/actions/runs/43616348161).
- Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 successful executions); no test failures or Node.js 20 / `punycode` warnings.
- Evidence is limited to Python reference models. Rust, CBOR/COSE, PostgreSQL, Trusted Egress, venues and live execution remain untested.

### Risk reservation concurrency protocol clarified — 2026-11-14

- Added Risk-owned scope-state serialization point shared by capacity reservation and exposure-projection updates.
- Preserved Ledger journal ownership and routed Ledger/venue/external exposure facts through Risk's idempotent projection inbox; no cross-service writes to Risk state.
- Specified deterministic multi-scope processing, atomic reservation commit, stable idempotency, bounded whole-transaction retry for 40001/40P01 and fail-closed ambiguous commit behavior.
- Synchronized NX-ADR-008, NX-IF-002 and OD-09; added adversarial concurrency/recovery evidence gates.
- No database, schema, service or runtime was implemented.

### Field-level data lineage and projection governance — NX-ARCH-REVIEW-006 — 2026-11-14

- Added a source-grounded field inventory for NX-IF-001..005 and NX-SEC-001.
- Proposed data classifications and accountable owners for trade intent/command/approval, Risk scope/exposure/reservations, execution events/Ledger, evidence/recovery, halt/emergency and security assets.
- Defined future projection restrictions for Analytics, Portfolio, Notifications, Strategy, Demo, Learning and Billing.
- Identified the missing complete Ledger journal-leg schema and explicitly avoided inventing fields.
- Retention/legal basis and field classifications remain proposals; no projection API, database table, access policy or runtime was implemented.

### Risk projection/reservation concurrency acceptance plan synchronized — 2026-11-14

- Aligned NX-ADR-008 §5.3, NX-IF-002 §6.4/§11, NX-REF-EXEC-002 §4.5 and OD-09.
- Risk owns derived exposure projection and scope-state serialization; Ledger remains journal owner and emits facts through idempotent inbox/outbox handoff.
- Added all-scope deterministic ordering, atomic reservation, missing/stale evidence fail-closed and idempotency/ambiguous-commit rules.
- Added adversarial acceptance cases for projection/reservation races, duplicate/reordered events, serialization/deadlock retry and recovery.
- No PostgreSQL instance/schema/service implemented; G1 evaluation only.
- Clarified that absence of a visible idempotency row does not prove rollback while the original Risk transaction may still be in flight; only same-identity/digest retry is permitted, otherwise halt.

### Risk scope serialization and PostgreSQL concurrency — NX-ARCH-REVIEW-007 — 2026-11-14

- Added a source-grounded concurrency review of the Risk-owned scope-state serialization point.
- Required parent/account and child projection fan-out to update all affected scope rows atomically; added scope-config version serialization.
- Defined logical scope-state version metadata without selecting a physical schema.
- Clarified whole-transaction 40001/40P01 retry and non-generic 23505/23P01 handling.
- Added a PostgreSQL 18 concurrency/fault-injection matrix and performance proof requirements.
- Synchronized NX-ADR-008, NX-IF-002 and OD-09. No database, schema, migration or runtime was implemented.

### Exact-head CI after NX-ARCH-REVIEW-007 — 2026-11-14

- Exact branch HEAD `e7c5461ae7ccea4f29fc77461db91d44566aba36` passed [workflow #43616908979](https://github.com/PandaGarry/NEXUS/actions/runs/43616908979).
- Python 3.11/3.12/3.13 each passed 13 suites / 239 tests (717 successful executions); no failures or Node.js 20 / `punycode` warnings.
- This is reference-model regression only; no PostgreSQL concurrency harness or production database was exercised.

### Numeric-wire parser integer budget made runtime-independent — 2026-11-14

- Added a fixed 512-decimal-digit budget for numeric-wire integer fields, independent of caller input-size budget and Python interpreter configuration.
- Oversized coefficient, scale, numerator or denominator values now fail with NUMERIC.RESOURCE_LIMIT before integer conversion.
- Replaced interpreter-threshold regression with explicit 512-digit acceptance and 513-digit rejection tests for decimal and rational values.
- This is a Python reference-parser resource limit only; Rust parity and production numeric profile remain open.
### Risk root-scope guard and immutable valuation inputs — 2026-11-14

- Made the account/root scope-state record mandatory in every v1 reservation/projection transaction; recheck root scope_config_version after locking the full scope set.
- Bound Risk reservations and capabilities to exact immutable market/index/FX/fee/collateral input versions and freshness evidence.
- Kept market-data ticks out of the serialized scope-state write path; stale or policy-invalid valuation inputs block dispatch.
- Synchronized NX-ADR-008, NX-IF-002, NX-ARCH-REVIEW-007 and OD-09. No runtime or schema was implemented.

### Immutable valuation-input and dispatch race-control clarification — 2026-11-14

- Clarified that Risk exposure scope-state and market/index/FX/fee/collateral source snapshots have separate ownership and transaction boundaries.
- Risk binds reservations/approvals to exact immutable valuation-input version vectors and source evidence; no cross-domain distributed transaction is assumed.
- Trusted Egress must revalidate the bound vector against source-specific freshness and configured drift/admissibility policy before send. Newer source values do not silently mutate an issued approval.
- Inadmissible or unconfigured inputs fail closed and require a new Risk evaluation/reservation.
- Interface schema, race tests and numeric thresholds remain open; no runtime was added.

### PostgreSQL 18.7 G1 evaluation patch selected — 2026-11-14

- Selected PostgreSQL 18.7 as the exact G1 evaluation target after reviewing the November 12, 2026 official release and supported-version status.
- Recorded release caveats for index integrity/REINDEX, incremental backup chains, C-extension rebuilds, extension scripts and privilege-sensitive SQL paths.
- Added G1 constraints: fresh full backup for PITR qualification, no unreviewed extensions/C extensions, no dblink or untrusted replication subscriptions, and base-table-only authoritative writes.
- No PostgreSQL instance, schema, extension or production deployment was created or approved. Requalify the latest supported 18.x patch before any future deployment.

### Persisted valuation-evidence manifest required at Trusted Egress — 2026-11-14

- Defined immutable ValuationInputVector identity/version and binding across ExposureSnapshot, RiskReservation and RiskApprovalCapability.
- Trusted Egress reads the authoritative persisted Risk evidence manifest and consumed source-watermark/correction status before send.
- Prohibited source-service calls and replacement market/FX/fee/collateral fetches on the dispatch path.
- Missing/stale/incomplete manifest, watermark gaps or inadmissible freshness/drift evidence fail closed; newer values never silently rebind an approval.
- Ingestion/invalidation objectives and race tests remain open; no runtime implemented.

### Trusted Egress send-authorization linearization defined — 2026-11-14

- Added a short attempt-scoped final authorization transaction over persisted valuation manifest, reservation, halt, eligibility and dispatcher-fence versions.
- Committed single-use EgressBoundaryAuthorization is the send-authorization linearization point; the single-writer Egress process immediately initiates socket write.
- No source fetch/queue hop/unbounded async preparation is allowed after the final gate; no database transaction is held over network I/O.
- Post-gate updates are causally later; the attempt remains potentially sent and requires reconciliation. Crash/race runtime tests remain open.

### Risk approval and valuation-evidence contracts synchronized — 2026-11-14

- Aligned NX-IF-001 RiskEvaluationRequest/RiskDecision/RiskApprovalCapability with immutable valuation_input_vector_id/version from NX-IF-002.
- Aligned NX-IF-001 with exact COSE_Sign1 untagged embedded four-element profile, alg=-19, bounded kid and empty unprotected map.
- Required local-only bounded key resolution, exact signed byte preservation and rejection of token-directed remote key discovery.
- Required Trusted Egress to validate the signed valuation vector against the persisted Risk evidence manifest with no remote source fetch; missing/unverifiable evidence denies send.
- Added negative conformance vectors; no cryptographic or Egress runtime implemented.

### PostgreSQL 18.7 G1 evaluation qualification — NX-RESEARCH-012 — 2026-11-14

- Selected PostgreSQL 18.7 as the exact G1 evaluation patch only; no production database or deployment was selected.
- Recorded the official release's 52 security fixes, 140+ bug fixes, index/REINDEX caveats and warning not to trust pre-update incremental backup chains.
- Added G1 controls for fresh full backup/PITR, extension/C-extension exclusion, dblink/subscription exclusion, base-table privileges, no runtime DDL and RLS/view defense-in-depth.
- Updated the reference-model README's verified Python matrix to 13 suites / 239 tests per runtime (717 executions) at exact tested SHA c191cde.

### Exact PR #16 head reference CI passed — 2026-11-14

- Branch HEAD `7fb396df5f3e700adf0ad151c446e38930fdadb0` passed [workflow #43617605777](https://github.com/PandaGarry/NEXUS/actions/runs/43617605777).
- Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 executions total).
- Job logs contain no failures or Node.js 20 / `punycode` deprecation warnings.
- This verifies Python reference models only; no Rust, CBOR/COSE, PostgreSQL 18.7, Trusted Egress, venue or live path was exercised.

### CI evidence reference corrected — 2026-11-14

- Corrected the exact-head workflow reference for SHA `7fb396df5f3e700adf0ad151c446e38930fdadb0` to [#43617626344](https://github.com/PandaGarry/NEXUS/actions/runs/43617626344).
- Verified Python 3.11/3.12/3.13: 13 suites / 239 tests each (717 successful executions), no failures or Node.js 20 / `punycode` warnings.

### NX-IF-004 G1 profile and Trusted Egress ownership aligned — 2026-11-14

- RiskApprovalCapability now binds both StateEvidenceVector and ValuationInputVector.
- Final compatibility checking is assigned to Trusted Egress at the attempt-scoped send-authorization gate, not generic Execution.
- Canonical CBOR/SHA-256/COSE Ed25519 profile now references NX-ADR-008 / NX-IF-001; library, key custody and security acceptance remain open.
- Documentation only; no signer, verifier, key or dispatch runtime implemented.

### WP-D evidence-vector and Trusted Egress contract synchronized — 2026-11-14

- Distinguished StateEvidenceVector (NX-IF-004) from ValuationInputVector (NX-IF-002); RiskApprovalCapability binds both.
- Required Egress to validate the exact signed valuation vector against the persisted Risk evidence manifest and latest consumed watermark/correction state.
- Prohibited remote source calls or replacement valuation fetches on the dispatch path; missing/stale/unverifiable evidence denies send.
- Added cross-source coherence and RecoveryBarrier/approval separation acceptance cases. No implementation/runtime added.

### Halt / final Trusted Egress race semantics — 2026-11-14

- Reconciled halt-epoch propagation with the final EgressBoundaryAuthorization linearization point across NX-IF-005, NX-ADR-008, NX-ARCH-REVIEW-005 and NX-REF-EXEC-002.
- Halt-first denies the final gate; gate-first creates an in-flight attempt that cannot be retroactively revoked and must be tracked until socket initiation or positive sender fencing.
- Egress cannot acknowledge a new halt epoch while a paused pre-halt gate-authorized attempt could still resume and initiate a write.
- Clarified that full HALTED acknowledgement prevents new stale/queued send initiation but does not recall requests already initiated or guarantee no bytes after the wall-clock halt-request time.
- No runtime, transport fence or fault-injection test was implemented; evidence remains open.

### Halt / final Trusted Egress gate race contract clarified — 2026-11-14

- Required halt-epoch transition and final EgressBoundaryAuthorization to serialize on the same authoritative halt-state generation.
- Defined halt-wins (deny) and gate-wins (in-flight, retain reservation, reconcile) outcomes.
- Required Egress to track gate-committed attempts until socket initiation or positive sender fencing before acknowledging the newer halt epoch.
- Clarified that no stale/queued attempt may newly initiate after boundary acknowledgement, but bytes already sent cannot be recalled.
- Separated Risk Engine outage from halt-store outage: independent Control Plane can commit halt while store is available; uncertain store blocks Egress authorization and fully-enforced HALTED status.
- No runtime, halt store or external fence implemented; race/fault proof remains open.

### Halt / Egress race conformance cases expanded — 2026-11-14

- Added NX-IF-005 cases 36–42 for both linearization orders, paused Egress, missing external fence, halt-store outage, late venue acceptance and actual socket-boundary proof.
- No runtime tests or external fencing proof are claimed; these remain G1 implementation gates.

### Halt / final Egress gate linearization specified — 2026-11-14

- Serialized the halt-epoch transition and final EgressBoundaryAuthorization against the same authoritative halt-state generation.
- Defined gate-first attempts as in-flight and non-revocable; Egress must drain or positively fence them before acknowledging the new halt epoch.
- Clarified that HALTED acknowledgement prevents new stale/queued socket-write initiation after acknowledgement, not venue processing of bytes already sent.
- Added halt race crash points and IF-005 conformance cases. Actual network/process fencing remains unimplemented and unproven.

### Halt / Egress race acceptance matrix and CI evidence — 2026-11-14

- Expanded NX-IF-005 with race cases 36–42: halt-before-gate, gate-before-halt, paused Egress, unavailable control store, failed sender fence, delayed venue acceptance and instrumented socket-boundary proof.
- Aligned halt acceptance criteria with the final EgressBoundaryAuthorization linearization point.
- Distinguished Risk application outage (independent Control Plane can still commit halt) from authoritative halt-store outage (Egress denies final gate; no fully-enforced HALTED claim).
- Verified Python reference suites at SHA `73841573e4e02b34a0c0363bbbe21155828d0c08`, [workflow #43617906166](https://github.com/PandaGarry/NEXUS/actions/runs/43617906166): 13 suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 executions).
- This is documentation and reference-model CI only; no halt store, Egress runtime, socket instrumentation or external fence was implemented.

### Risk approval and venue signing authorities separated — 2026-11-14

- NX-SEC-001 now requires separate non-reused keys, workload identities and policies for RiskApprovalCapability signing and venue request signing/credentials.
- Risk signer alone holds Risk private key; Execution/Trusted Egress receive public verification material only.
- Trusted Egress alone holds venue credentials and owns the venue socket; EgressBoundaryAuthorization remains a separate one-use attempt control.
- No key, vault, signer or venue credential is implemented; key lifecycle and compromise tests remain open.

### Exact PR #16 head CI passed after halt / signing authority updates — 2026-11-14

- Branch head `dbfba513b86a79b8b6574a80c1beb136b28836c7` passed [workflow #43618114058](https://github.com/PandaGarry/NEXUS/actions/runs/43618114058).
- Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 executions total).
- All logs show no failures or Node.js 20 / `punycode` deprecation warnings.
- This is Python reference-model CI only; no signing keys, halt store, Egress, PostgreSQL, Rust or venue path was exercised.

### Test-only halt / final Egress gate reference oracle — 2026-11-14

- Added `HaltEgressGate` sequential state-machine oracle and 12 tests covering both logical commit orders, paused sender acknowledgement blocking, positive sender fencing, single-use attempt IDs, control-store outage and reconciliation after socket initiation.
- Linked the oracle to NX-IF-005 / NX-REF-EXEC-002 and documented its strict limitation: it does not prove database linearizability, durable state, real process/socket behavior or external network fencing.
- Exact-head CI for the expanded test matrix remains pending.

### Halt / final Egress gate oracle CI — 2026-11-14

- The test-only `HaltEgressGate` oracle and 11 new tests passed at SHA `e45ea01c6047e1f1207a6987a2cd05d7440853b1`, [workflow #43618215618](https://github.com/PandaGarry/NEXUS/actions/runs/43618215618).
- Python 3.11/3.12/3.13 each passed 250 tests (750 successful executions); the egress-fencing package is expected to run 25 tests/runtime.
- All logs were clean of test failures and Node.js 20 / `punycode` deprecation warnings.
- This is sequential reference-model evidence only; no durable halt store, database lock proof, socket, process fence or network enforcement was tested.

### HEGC logical authority and idempotent Egress grant contract — 2026-11-14

- Assigned sole logical write ownership of HaltState and EgressBoundaryAuthorization to the bounded Halt/Egress Gate Coordinator (HEGC), separate from Risk, Command Coordinator and venue-credential-owning Egress.
- HEGC has no venue credentials/socket or Risk signing key; Egress has no direct write access to control records.
- Defined least-privilege HEGC reads and control-schema-only writes.
- Made grant issuance idempotent on stable attempt ID; exact retries return the same grant, changed bindings conflict, and ambiguous responses are resolved by the same ID.
- No HEGC runtime, schema, role or database instance implemented.

### HEGC / Risk approval independent verification boundary hardened — 2026-11-14

- NX-SEC-001 classifies HEGC as a critical control-plane trust domain with no venue credentials/socket or Risk signing key.
- Trusted Egress must independently verify the RiskApprovalCapability signature and exact command/reservation/evidence/audience/expiry/single-use bindings; the HEGC grant cannot replace Risk approval.
- HEGC grant issuance is idempotent by attempt ID; changed bindings conflict and ambiguous responses resolve through the same ID.
- No HEGC runtime or production security proof exists.

### HEGC authority and halt-gate reference model hardened — 2026-11-14

- Selected HEGC as sole logical writer of halt and final Egress authorization records; no venue credentials, socket or Risk signing key.
- Restricted Egress to one-use attempt-scoped grants and removed direct control-state write authority.
- Added test-only model cases for pending halt/store recovery, in-flight attempts, sender fencing, repeated halt idempotency and signed-64-bit epoch exhaustion.
- Production HEGC, PostgreSQL schema/API, actual socket instrumentation and external fencing remain unimplemented.
