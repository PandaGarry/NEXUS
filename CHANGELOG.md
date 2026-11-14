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
- Updated historical venue research, architecture index, roadmap, project status and checklist. No venue selected, no live capability or production code added.
