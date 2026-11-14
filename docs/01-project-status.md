# Текущий статус проекта

**Дата среза:** 2026-11-14  
**Общий статус:** BLOCKED — Prototype Readiness Gate не пройден; bounded v1 scope decisions OD-01/04 accepted  
**Текущая фаза:** Phase 0 — Foundation Audit / Architecture Synthesis; bounded instrument-spec reference implementation in a stacked Draft PR

| Область | Статус | Комментарий |
|---|---|---|
| Цель и продуктовые границы | Accepted / personal-first proposal | NEXUS v1 proposed as closed single-owner personal product; no public users or commercial service in initial scope. NX-ARCH-002 is proposed and requires owner review |
| Архитектурные принципы | Proposed / Partially accepted | Требуются финальные ADR |
| Tradoor audit | In Progress | Source pass обновлён до HEAD 6ab3877; funding/private execution capability audit добавлен в NX-RESEARCH-002. Полная per-venue сертификация, instrument metadata и runtime verification остаются открыты |
| Exchange capabilities matrix | Incomplete | Trade/book/OI/liquidation первично просмотрены; per-channel matrix и UNKNOWN поля ещё не закрыты |
| Simulation fidelity | In Progress | Tradoor paper-модель недостаточна для реалистичного исполнения |
| Runtime verification | Partial / reference-only | GitHub Actions run [#43593302985](https://github.com/PandaGarry/NEXUS/actions/runs/43593302985) passed code/workflow HEAD `5a1369435dd9024191f193df70651f1c00a36c6e`: six isolated suites (11 exact-decimal, 24 gateway, 13 egress-handover, 17 instrument-specification, 12 instrument-registry and 16 dimensional-type tests) on Python 3.11, 3.12 and 3.13 (93 tests per runtime; 279 matrix executions; 1,000 seeded rational-oracle cases inside each exact-decimal suite). Reference-only; no production runtime, real egress fencing or exchange-adapter verification claimed |
| Security threat model | Drafted / Proposed | NX-SEC-001 сохранён; owner review, deployment-specific analysis и security verification не выполнены |
| Dimensional financial types | Reference slice added / exact-head CI pending (16 dedicated tests) | NX-REF-DOMAIN-003 introduces exact-decimal AssetAmount, Money, Price, Notional and ContractCount with explicit unit checks; 16 tests pass in run #43593302985 on Python 3.11–3.13; production integration, contract formulas and numeric bounds remain open |
| Exact arithmetic / instrument specs | ADR proposed / reference slices verified | NX-ADR-005 remains PROPOSED. NX-REF-DOMAIN-001 validates immutable snapshots and exact tick/lot/minimum rules (17 tests); NX-REF-DOMAIN-002 adds append-only in-memory history, idempotent replay, version/identity conflicts and effective-time ordering (12 tests). Combined reference CI run [#43592862627](https://github.com/PandaGarry/NEXUS/actions/runs/43592862627) passed on Python 3.11–3.13 at branch HEAD `7654c67774f3b6131b498a57c5de6b6621f6513f`; no persistence, source precedence, official venue fixtures, derivative formulas or production authority | NX-ADR-005 drafted; requires owner review and full registry/venue contract decisions. Implementation readiness remains blocked |
| Unified market event contract | PROPOSED | NX-ADR-001 опубликован; owner review и conformance design review требуются |
| Professional Order Flow specification | PROPOSED | ТЗ-NX-002 опубликовано; формулы, golden datasets и реализация не проверялись |
| Quant & Strategy Engine specification | PROPOSED | ТЗ-NX-003 опубликовано; research protocol, runtime, feature registry и стратегии не реализованы/не проверены |
| Autonomous Execution Engine specification | PROPOSED | ТЗ-NX-004 опубликовано; private adapters, durable outbox, reconciliation, vault/signer и runtime tests не реализованы/не проверены |
| Independent Risk Engine specification | PROPOSED | ТЗ-NX-005 опубликовано; policy registry, exposure calculator, approval signer, reservations, kill-switch controller и conformance tests не реализованы/не проверены |
| Portfolio & Financial Ledger specification | PROPOSED | ТЗ-NX-006 опубликовано; journal, posting engine, accounting projections, reconciliation, replay and restore tests не реализованы/не проверены |
| Cross-specification interfaces | BLOCKED | NX-ARCH-REVIEW-001 выявил 12 design gaps. WP-A NX-IF-001, WP-B NX-IF-002, WP-C NX-IF-003, WP-D NX-IF-004 и WP-E NX-IF-005 опубликованы как PROPOSED design drafts; owner/security/accounting/operations review, open decisions and conformance evidence remain outstanding |
| Target architecture | PROPOSED / bounded scope decisions accepted | NX-ARCH-001 remains proposed; owner-directed v1 scope accepted: one venue + dedicated account/subaccount, account-level risk boundary, server-side autonomous runtime, shared Desktop+Web backend. Venue/product/account-mode and production deployment decisions remain open |
| Prototype readiness | BLOCKED | Не начинать прототипирование |

## Current cross-work-package notes

- **WP-C — Execution ↔ Ledger:** NX-IF-003 создан как PROPOSED design draft. Определены source ownership, canonical fill identity, durable Execution outbox/Ledger inbox, atomic balanced journal posting, fee/correction semantics, projection watermark и WP-B FILL_PENDING_LEDGER handoff. Owner decisions, implementation choices and conformance evidence remain open; no implementation or tests claimed.
- **WP-D — Freshness & Recovery:** NX-IF-004 создан как PROPOSED design draft. Определены StateEvidenceVector, source-specific freshness/quality/reconciliation dimensions, versioned EvidenceRequirementSet/FreshnessPolicy, RecoveryCase/quarantine, scoped generation-fenced RecoveryBarrier и dependency-aware restart/reconciliation ordering. Owner thresholds, venue/account scope, persistence and operator decisions remain open; no implementation or tests claimed.
- **WP-E — Emergency Operations:** NX-IF-005 создан как PROPOSED design draft. Определены monotonic scoped HaltState/epochs, explicit CREATE/AMEND/CANCEL/CLOSE/REDUCE_ONLY/CANCEL_ALL/FLATTEN classification, bounded EmergencyActionPlan, protective-order handling, operator step-up/dual-control and gated resume. Venue capability certification, role assignments and emergency-policy decisions remain open; no implementation or tests claimed.

## Research and architecture records

- [NX-RESEARCH-003 — First-Venue Shortlist](research/NX-RESEARCH-003-first-venue-shortlist.md) — Coinbase/Kraken conditional comparison; exact venue/product selection remains open pending legal/account eligibility and API capability qualification.
- [NX-RESEARCH-006 — Reference Platform Fit Assessment](research/NX-RESEARCH-006-reference-platform-fit-assessment.md) — NautilusTrader is a leading candidate for selected runtime reuse, not selected.
- [NX-RESEARCH-007 — NautilusTrader v2 Release Baseline Review](research/NX-RESEARCH-007-nautilus-v2-release-baseline.md) — v2.0.0rc9 is pre-release and test-only; no production baseline selected.
- [NX-RESEARCH-008 — NautilusTrader RC9 Execution Boundary Audit](research/NX-RESEARCH-008-nautilus-rc9-execution-boundary-audit.md) — exact RC9 source confirms no durable-before-dispatch guarantee, bypassable RiskEngine routes and process-local dispatch markers; NautilusTrader cannot be NEXUS's execution authority without a NEXUS-owned gateway/outbox.

## Architecture artifacts (PROPOSED)

- NX-ARCH-002 — Product & Deployment Profiles; personal-first single-owner scope; no runtime enforcement or live authorization.
- NX-ADR-001 — Unified Market Event Contract; no implementation or conformance tests.
- NX-ARCH-001 — Target Architecture & Deployment Topology; no implementation or runtime verification.
- NX-ARCH-REVIEW-001 — Cross-Specification Contract Review; 12 findings, five closure work packages, interface readiness BLOCKED.
- NX-IF-001..005 — proposed contracts for authorization, reservations, ledger handoff, recovery barriers and emergency operations; implementation and conformance tests NOT STARTED.
- NX-OWNER-DECISIONS-001 — OD-01 and OD-04 accepted under owner delegation; OD-15 partially accepted; remaining decisions open/deferred.
- NX-ADR-002..005 — proposed execution, simulation, market recovery and instrument/exact-arithmetic contracts.
- ТЗ-NX-001..006 — proposed market data, order flow, quant, execution, risk and ledger specifications; implementation NOT STARTED.
- NX-SEC-001 — threat model and credential isolation; owner review and security verification not completed.

## Tradoor research notes

- Source pass pinned to Tradoor SHA `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`; funding/private-execution follow-up performed on HEAD `6ab38775f8f95a2b0237d8663a15405fa00465c6`.
- Main chart/trade market-data path is browser-side; Order Flow DOM/Tape hub is page-owned. Not a ready autonomous ingestion backend.
- Browser BookSync sequence continuity is checked for Binance, OKX and Deribit; some other incremental adapters do not pass sequence through the common contract.
- Server trade parser has event-time/coverage differences for Kraken Spot, Coinbase Spot and Lighter.
- Open Interest recorder covers eight venue/market families, polling 15s, minute storage; arithmetic uses f64.
- Common Tradoor Product model lacks authoritative lot step/minQty/minNotional/contract multiplier/settlement/margin rules; do not use for live order validation.
- Hyperliquid price decimal limit does not capture the full five-significant-figure rule or independent size step.
- Server liquidation collector covers 11 perpetual venues with 24h retention.
- Tradoor paper execution uses simplified fills and f64 financial values; public market-data adapters do not prove private authenticated execution.
- Tradoor license is declared AGPL-3.0-only; legal review required.

## Foundation documentation review and reference slice (2026-11-14)

- [NX-PROJECT-CHECKLIST-001](quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md) added as the living execution/evidence register. G0D remains BLOCKED; D1–D8 statuses and ordered next actions are explicit.

- NX-DOC-REVIEW-001 added as bounded close-out review. Documentation baseline remains NOT FROZEN; G0D is BLOCKED.
- PR #1–#9 were recorded as Draft/unmerged in the prior snapshot; PR #8 and #9 are sibling branches, and #9 does not include #8.
- Repository branch `docs/personal-product-profile` contains documentation only; no NEXUS root source workspace/build system was found in that discovery pass.
- NX-ARCH-003 defines the first exact-decimal conformance slice without selecting production language, bounds or rounding policy.
- Added a dependency-free Python exact-decimal reference oracle and language-neutral golden vectors v1.0.0 (15 vectors). Local verification: 10 tests passed against exact checked-in reference-model files. This is reference-model evidence only, not production runtime or Rust/WASM verification.
- Prototype Readiness remains BLOCKED. No exchange account connection, credentials, orders, live trading, production deployment or risk-limit changes occurred.

## Reference-platform fit assessment (2026-11-14)

- NX-RESEARCH-006 added as an evidence-backed first fit assessment. NautilusTrader is a leading candidate for selected runtime reuse, not a selected full-stack foundation.
- NX-RESEARCH-007 pins v2.0.0rc9 (commit `da6b57aefdd62b44f675e434ffcfefca7f4025dd`) as a test-only release candidate. It is not a production baseline.
- The previously inspected develop snapshot `97ecbafd6621241a2222ef5a31cf887c6d96d950` diverges from rc9 (77 commits ahead / 72 behind); source findings must not be transferred between snapshots without re-audit.
- NX-RESEARCH-008 inspects the exact RC9 execution/risk paths. RC9 documentation and source confirm asynchronous best-effort persistence before dispatch, submit/modify/cancel/query route branches that do not enforce a single universal RiskEngine gate, and process-local dispatched-order state absent after restart.
- NautilusTrader may remain a test-only candidate for replay and selected capabilities, but it is not approved as NEXUS execution authority. NEXUS must own durable outbox, non-bypassable Risk gateway, ledger and recovery barrier.
- 10 reference-model tests and 10,000 randomized arithmetic comparisons were run against exact fetched files in an isolated local directory. At that earlier review point, PR #10 had no returned GitHub Actions runs; subsequent exact-HEAD CI evidence is recorded below.


## Command gateway reference slice (2026-11-14)

- NX-REF-EXEC-002 proposes account-scoped authority epochs, credential/network isolation, independently enforced old-egress fencing, stale-epoch state-mutation rejection and a fail-closed takeover sequence. A 13-test Python control-plane state-machine model now checks takeover ordering and fail-closed transitions; it passed the three-version CI matrix in run #43590804814. Its caller-supplied fence receipt is not a trusted attestation and it does not fence real network access.
- NX-REF-EXEC-001 and `foundation/reference-model/execution-gateway/` add a test-only Python/SQLite model for CREATE command authorization, payload-bound approval, active reservation consumption, durable local outbox persistence, dispatch marker, and conservative ambiguous-outcome recovery.
- The suite contains 23 deterministic tests. GitHub Actions run [#43590804814](https://github.com/PandaGarry/NEXUS/actions/runs/43590804814) passed exact branch HEAD `a7ee5426077005a6135e9f1b6f1c4044cc41d459`: 11 exact-decimal, 21 gateway and 13 egress-handover state-machine tests on each of Python 3.11, 3.12 and 3.13 (135 test executions across the matrix). This is reference-model evidence only; the egress state machine does not revoke real network access. Three independent-connection tests cover local SQLite races only, including serialized recovery claims. A new adversarial counterexample proves a stale worker can resume after recovery and still send through an unfenced adapter. Conditional state transitions now reject late ACK, stale pre-send rejection and adapter-error updates after recovery, preserving OUTCOME_UNKNOWN and recording stale evidence. The egress race remains a known unsafe behavior; a real fenced egress authority is required before production.
- Scope is intentionally narrow: fake adapter only; no production signer, production database, fenced egress authority, cross-host leases/fencing, complete Risk calculation, ledger posting, venue reconciliation, or real exchange integration.
- The current exact PR HEAD is verified by GitHub Actions run #43591389103; no claim of local container rerun is made.
- Prototype Readiness remains BLOCKED. The reference model grants no live permission and does not change any owner risk limits.


## Latest gateway state-transition hardening (2026-11-14)

- Adversarial review found that late ACK handling already used a conditional state transition, but the second pre-send rejection path and adapter-exception path still performed unconditional updates. A stale worker could therefore overwrite a recovered command state through those paths.
- Added conditional updates requiring the command to remain DISPATCHING at the expected halt epoch. If recovery has superseded the worker, the stale path records a dispatch observation and leaves the authoritative state unchanged.
- Added two deterministic tests: recovery during the final pre-send guard and recovery during a simulated ambiguous adapter timeout.
- GitHub Actions run [#43591389103](https://github.com/PandaGarry/NEXUS/actions/runs/43591389103) passed exact PR HEAD `f2dc357e9c65f0c2e108e670c4211bb36ff1a162`: 11 decimal, 23 gateway and 13 egress-handover tests on each of Python 3.11, 3.12 and 3.13.
- This hardens authoritative state transitions only. The known stale-worker network-send counterexample remains reproducible; independently enforced egress fencing is still BLOCKED.


## Recovery transaction serialization (2026-11-14)

- A further race review found that restart recovery selected DISPATCHING rows and updated them without one transaction. A concurrent late response could commit between the scan and update, allowing recovery to overwrite a newer state.
- Recovery now acquires a SQLite write transaction before scanning, then conditionally transitions only rows still in DISPATCHING. The transaction gives the reference model a clear local serialization point; it is not a distributed lease or host fence.
- Added a two-connection/two-worker test proving that only one recovery worker claims a DISPATCHING command.
- GitHub Actions run [#43591524490](https://github.com/PandaGarry/NEXUS/actions/runs/43591524490) passed exact PR HEAD `4f836d0f9d1a43161927331c05e6cc19bb12072b`: 11 decimal, 24 gateway and 13 egress-handover tests on Python 3.11–3.13.
- The stale-worker network-send counterexample remains intentionally reproducible. Real egress fencing remains BLOCKED.

### Latest domain-kernel work

NX-REF-DOMAIN-004 adds a test-only, explicit mapping between instrument specifications and quantity dimensions. Spot, linear and inverse reference semantics are supported; QUANTO and inverse base exposure remain blocked. Dedicated 16-test suite passed in GitHub Actions run #43593795698 on exact HEAD `ba8df9def72bff82625669bc236430bb8d21592d` across Python 3.11–3.13 (109 tests per runtime / 327 matrix executions). No venue is qualified by synthetic fixtures.

### Exact division reference increment

NX-REF-DOMAIN-005 adds reduced rational division, exact terminating-decimal conversion and explicitly selected quantization modes. The dedicated 18-test suite and 1,000 deterministic rational property cases passed GitHub Actions run #43594118145 on exact PR HEAD `a46b49a2cbb7a5960ce483f93a736a3fbc945554` across Python 3.11–3.13 (127 tests per runtime / 381 matrix executions). No production or operation-specific rounding policy is approved.

### Inverse contract exposure increment

NX-REF-DOMAIN-006 adds a rational base-exposure result for the conventional inverse model, preserving exactness without implicit rounding. Synthetic tests passed PR CI run #43594275808 on current PR HEAD `a47085efd19826d9fea6edcaf2245dd689a288e8` across Python 3.11–3.13 (129 tests per runtime / 387 matrix executions). Venue-specific qualification remains pending.


### Bounded numeric and canonical wire increment

NX-REF-DOMAIN-007 adds a separate caller-configured bounded reference context with preflight checks; the arbitrary-precision oracle remains unchanged. NX-REF-DOMAIN-008 adds strict versioned scalar decimal/rational wire formats. PR CI run #43595449902 passed exact PR HEAD `6200bae99e9b7ce865487a40312d0074c0e2a276` on Python 3.11–3.13 (172 tests per runtime / 516 executions). Production numeric limits, fixed-width representation, resource-safety proof and cross-language integration remain open.

## Financial-operation contract increment (2026-11-14)

- NX-REF-DOMAIN-009 published on the stacked Draft branch as a PROPOSED design contract for operation-specific rounding and valuation.
- Enumerates tick/lot normalization, minimum notional, trading fees, funding, realized/unrealized P&L, initial/maintenance margin, liquidation, FX/collateral conversion and Ledger posting/reconciliation.
- Establishes global exactness/dimensionality/provenance invariants, separates estimates from authoritative account facts, defines explicit rounding boundaries and a venue-qualification dossier.
- Official Binance Spot, OKX and Bybit documentation is used only to demonstrate venue/product differences; no venue is selected or qualified.
- All venue/account formulas and owner accounting policies remain BLOCKED/OWNER-DECISION as applicable. No calculator, Risk/Ledger implementation, venue adapter, credentials, orders or live capability was added.
- Prototype readiness remains BLOCKED; live trading remains NOT AUTHORIZED.

## Venue-neutral financial math fixture increment (2026-11-14)

- NX-REF-DOMAIN-010 and `financial-math-golden-v1.json` add synthetic, non-authorizing exact vectors for spot notional, explicitly mapped linear contract exposure/notional, inverse rational base exposure and partial-fill weighted-average arithmetic.
- New test suite checks selected outputs independently with standard-library `fractions.Fraction`; non-terminating inverse exposure remains rational and exact decimal conversion fails closed.
- CI run [#43596710483](https://github.com/PandaGarry/NEXUS/actions/runs/43596710483) passed exact code/test commit `9d0bf48c3ddc66facf408d60b1c64beb971eebb6`: 179 tests on each of Python 3.11, 3.12 and 3.13; all three jobs successful.
- This is mathematical reference evidence only. It does not qualify venue multipliers, reporting scope, fees, funding, P&L, margin, liquidation, FX or accounting. G0/G1 and live-trading restrictions are unchanged.

- Expanded fixture verification: 650 deterministic seeded property cases (spot exact product, partial-fill permutation/partition invariance, inverse contract-value identity). GitHub Actions run [#43596851904](https://github.com/PandaGarry/NEXUS/actions/runs/43596851904) passed exact code/test commit `0f0b44e927aacf67d6f7a5678b160b3e3c6088e0`: 182 tests per runtime across Python 3.11, 3.12 and 3.13. This remains bounded test-only evidence, not formal verification or production/venue qualification.

## Russia jurisdiction and first-venue qualification update (2026-11-14)

- Published NX-RESEARCH-009 as the current RF-resident jurisdiction/product eligibility baseline.
- Law No. 282-FZ entered into force 2026-09-01; Article 30(1)'s resident-intermediary rule enters 2027-07-01. Article 30(2) includes a prohibition on assisting unlawful transactions, including software; its application to private owner-operated NEXUS requires legal review.
- Bank of Russia FAQ confirms from 2027-07-01 residents transact through Chapter 4 participants, including licensed brokers or CBR-registered crypto-exchange organizations; direct P2P between individuals is not included.
- CBR record confirms ООО «Т-ИНВЕСТ ЛАБ» has an active right to operate as an organization exchanging digital currencies from 2026-10-06 and holds broker/depository permissions. This does not establish a public crypto API.
- MOEX crypto-index futures and SPB/T-Invest crypto-index neoassets found are qualified-investor-only; both are cash-settled RUB products, not spot crypto/global USDT perps.
- Foreign venues remain research-only; Kraken removed from RF v1 shortlist, Coinbase/Bybit/OKX not qualified for the owner's exact account/product/legal route.
- No venue selected, no API keys connected, no live orders or transfers. A proposed jurisdictional eligibility record is required before any adapter can be LIVE-ELIGIBLE.
- Directive 7441-U was registered 2026-10-30, published 2026-11-06 and enters into force 2026-11-17. It sets a RUB 300,000 annual cumulative acquisition-value cap for non-qualified residents purchasing through a broker and lists BTC, ETH and USDT as assets that may be admitted to organized trading subject to criteria. The exact applicability of the broker cap to a principal-dealing crypto-exchange organization must be legally confirmed; active buy/re-entry turnover can consume the broker cap.

- Drafted NX-ADR-007 Venue Eligibility & Jurisdictional Activation Gate as PROPOSED: immutable scope-bound evidence record, fail-closed adapter states, independent Risk/Execution authorization, and eligibility-epoch fencing at the trusted egress boundary. Cross-document consistency review against NX-IF-001..005, NX-SEC-001 and NX-ADR-002 found no blocking contradiction. Owner/legal acceptance, production identity/evidence storage, signatures and conformance tests remain open.

- Added NX-REF-VENUE-001 test-only venue eligibility reference model: explicit policy inputs, immutable evidence records, exact scope binding, freshness/expiry checks, reviewer references and owner-approval revision binding. Added 24 deterministic fail-closed tests and a Python 3.11/3.12/3.13 CI step. The suite is not production authorization; exact-head CI is pending.

- Exact-head CI completed for venue eligibility reference model at PR #14 SHA `8c7eed6ac781a40c81652da08ff3207f4d46bc6d`, run 43598444584: 210 tests passed on each of Python 3.11, 3.12 and 3.13 (630 executions total). The 28 venue eligibility tests passed on all three runtimes. This verifies only the test reference model; production eligibility enforcement remains unimplemented.

- Added NX-REF-VENUE-002, a test-only single-process eligibility egress-fencing model. It serializes dispatch with suspension, binds command to exact record/revision/scope/epoch/expiry, consumes command IDs, and preserves OUTCOME_UNKNOWN without blind retry. 21 tests cover stale epoch, scope/revision mismatch, expiry, ambiguous send, concurrent dispatch/suspend ordering and revision-bound reactivation. CI run 43599182263 at SHA `a7a369ca9e5683208fbcd43a3fd1de0a8f8c47f1`: 231 tests passed on each Python 3.11/3.12/3.13 (693 executions). This remains a single-process reference, not production fencing.

## Rust execution and cross-language conformance update (2026-11-14)

- Created engineering branch `engineering/rust-execution-domain-conformance-v0` from exact PR #14 head `ab6976933cb4de9b5320b73531034d02edc53907`.
- Published [NX-ARCH-004](architecture/NX-ARCH-004-rust-execution-cross-language-conformance.md) as PROPOSED. It defines candidate Rust domain/execution boundaries, NEXUS-owned command/Risk/egress authority, adapter outcome classes, numeric constraints, language-neutral fixture rules and adversarial failure scenarios.
- Created GitHub Issue #15 to track implementation and acceptance evidence.
- No Rust source, Cargo workspace, production numeric profile, signer, persistent execution service, trusted egress or venue adapter was added.
- Python reference models remain test-only oracles. No cross-language conformance is claimed.
- NautilusTrader remains unselected; any reuse requires exact-version authority-boundary and adapter conformance review.
- Prototype readiness remains BLOCKED. No venue/account selected, no credentials connected and live trading NOT AUTHORIZED.


## Execution ordering cross-contract review update (2026-11-14)

- Corrected NX-ADR-002 to make the durable reservation-before-approval sequence explicit, consistent with NX-IF-002 §6.1 and NX-IF-001 §8.3.
- Defined two ordered durability boundaries: Risk commits all required `PRE_DISPATCH_RESERVATION` scopes before issuing `RiskApprovalCapability`; Command Coordinator atomically consumes the single-use capability while committing the canonical command, reservation reference and outbox record.
- Clarified the pre-egress dispatch-attempt marker and conservative move to `DISPATCH_OUTCOME_UNKNOWN`. A crash after the marker but before the socket write remains potentially sent until authoritative reconciliation; this intentionally over-approximates uncertainty to prevent reservation release.
- Cross-reviewed NX-ARCH-004 against NX-IF-001..005, NX-ARCH-003, NX-ADR-002/005/007 and NX-SEC-001. No remaining blocking authority-order contradiction was found in the reviewed documentation path.
- This closes a documentation sequencing gap only. No production transaction, dispatcher, trusted egress fence, Rust source, venue adapter or runtime test was added. Prototype readiness remains BLOCKED; live trading NOT AUTHORIZED.


## Language-neutral conformance infrastructure update (2026-11-14)

- Audited existing fixture families: exact decimal, rational division, numeric wire, financial math and instrument specification. Their top-level envelopes and invalid-case representations differ; the current CI runs Python unittest modules directly rather than a common cross-language runner.
- Published NX-ARCH-005 as PROPOSED, defining a common fixture envelope, VALUE/REJECT outcome union, stable rejection-class families, strict type/unit comparison, versioning, migration and evidence requirements.
- Verified the complete tracked branch tree contains no Cargo manifest/lockfile, Rust toolchain pin, Rust source tree or Rust runner. Rust implementation remains blocked pending G0D/G1 and owner-approved toolchain/dependency policy.
- Existing v1 fixtures were not changed; no normalized schema, validator, Python runner, Rust runner or cross-language conformance was implemented.

- Added a per-file migration assessment to NX-ARCH-005: decimal/rational suites are mostly structural; numeric-wire invalid cases require reference-derived stable rejection classes; financial-math values require strict unit preservation; instrument-spec fixture needs a separately specified validation operation and expected outcome. No legacy file was modified.

- NX-ARCH-005 includes an initial operation registry for decimal, rational, numeric-wire and dimensional-math suites. The numeric-wire reference parser now has catch-compatible typed error subclasses with stable machine-readable classes for malformed shape, unsupported version, non-canonical encoding and resource-limit failures. This improves reference conformance only; it is not production parser qualification.

- NX-ARCH-005 now specifies strict fixture ingestion: UTF-8-only decoding, duplicate-key and non-standard constant rejection, no JSON floating-point tokens, bounded integer control fields, raw-byte SHA-256 identity, and explicit parser resource limits. These are proposed requirements; no validator/runner exists yet.

- Exact-head reference-model workflow [#43602394909](https://github.com/PandaGarry/NEXUS/actions/runs/43602394909) passed `e126f67b5779969ad3cffb67cfbb505760668518`: 13 isolated suites / 232 tests on Python 3.11, 3.12 and 3.13 (696 successful executions), including the numeric-wire stable error-class tests. This is reference-model CI only; no normalized fixture validator/runner, Rust or production execution evidence is implied.

## NX-ARCH-005 cross-review update — 2026-11-14

A focused contract-to-code audit corrected the strict-JSON example in NX-ARCH-005 and narrowed claims around operation coverage. Decimal/rational and numeric-wire operation mappings are tied to the actual reference-model APIs; financial-math labels without callable reference implementations and the instrument-spec snapshot remain deferred migration targets. Non-numeric rejection mappings remain review-gated and must not be inferred from exception messages. No executable schema/runner or Rust implementation exists; owner review and G0D/G1 gates remain in force.

## Financial/numeric audit correction — 2026-11-14

Correction to the preceding NX-ARCH-005 cross-review: linear and inverse financial reference paths are present and tested in `instrument_units.py` / `test_financial_math_fixtures.py`; only reusable partial-fill aggregation remains an extraction follow-up because its current implementation is inline in the test. The exact decimal oracle is arbitrary precision, while `BoundedNumericContext` applies mandatory explicit synthetic limits. API misuse is distinct from mathematical inexactness. NX-ARCH-005 now records the corrected mapping and remains PROPOSED.


## Partial-fill aggregation reference extraction — 2026-11-14

Extracted the previously inline weighted-average calculation into `foundation/reference-model/financial_aggregation.py` as `aggregate_partial_fills`. The callable returns typed base quantity and quote notional plus an exact rational average; it rejects empty input and relies on domain wrappers for base/quote dimension safety. Golden-vector and seeded permutation/partition tests now exercise the named callable, with additional empty/mismatch/non-terminating cases. This remains a test-only arithmetic oracle: no venue fill admissibility, fees, funding, P&L, accounting, rounding, production runtime or normalized fixture runner is implied. NX-ARCH-005 owner approval remains required before normalized schema/runner work.

The aggregation boundary was further tested for a non-empty signed fill set with zero aggregate quantity: it raises the existing typed `DivisionByZero`. Empty input remains a separate `ValueError` input-contract failure. This keeps mathematical division-by-zero distinct from malformed operation input.


## Reference exception mapping audit — 2026-11-14

NX-ARCH-005 now contains an operation-by-operation audit of typed exceptions across decimal parsing/quantization/division, bounded numeric operations, dimensional price/instrument conversions and partial-fill aggregation. Candidate mappings are distinguished from malformed API input and unresolved domain errors; exception-message parsing is explicitly prohibited. In particular, a repeating rational conversion is mathematically valid even when exact finite-decimal conversion is not, and zero aggregate fill quantity is a typed division-by-zero outcome distinct from empty/malformed input. This remains proposed design evidence only; owner acceptance of the rejection taxonomy is still required before schema/runner implementation.

A small API-boundary defect found during the exception audit was corrected: `ExactDecimal.is_multiple_of` now explicitly rejects a non-`ExactDecimal` step with `TypeError` rather than leaking an incidental `AttributeError`. The existing `InvalidStep` path for non-positive decimal steps is unchanged and separately tested.
