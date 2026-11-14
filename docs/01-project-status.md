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


## Cross-contract pre-egress ordering clarification — 2026-11-14

## Reservation/dispatch review finding refresh — 2026-11-14

NX-ARCH-REVIEW-001 F-02 was stale in wording: it still described the reservation/command lifecycle as wholly unspecified, although NX-IF-001 §8.3, NX-IF-002 and NX-ADR-002 now publish the ordered design contract. F-02 is now explicitly marked **partially resolved at design level only**: durable reservation precedes capability issuance; single-use capability consumption is atomic with canonical command/outbox commit; ambiguous dispatch retains reservation. Owner acceptance, transaction/isolation choice, crash/replay/concurrency evidence, full reservation lifecycle proof and independently enforced egress fencing remain open. No runtime or distributed-safety guarantee is implied.


A targeted review found one ambiguous label in the IF-002 exposure lifecycle table: “marks command as dispatching / sends it” did not make the ordering between the durable attempt marker and network side effect explicit. The row now requires the dispatcher to commit the durable pre-egress marker before any network action. That marker moves exposure to `DISPATCH_OUTCOME_UNKNOWN` and is expressly not evidence that bytes were sent. The conservative reservation remains held until authoritative venue outcome and reconciliation. NX-ARCH-REVIEW-001 records the clarification. This aligns documentation only; production storage, transaction isolation, fencing and egress enforcement remain unimplemented and unverified.


## Transaction and egress crash analysis — 2026-11-14

Expanded NX-REF-EXEC-002 with a proposed implementation decomposition and minimum crash-point matrix. The design now separates (1) Risk-owned all-scope reservation commit, (2) Command Coordinator's atomic single-use capability consumption + canonical command/reservation-reference/outbox commit, (3) durable attempt marker, and (4) the credential-owning Egress send boundary. Risk and Command are ordered independent durable commits; no cross-service distributed ACID transaction is assumed. Reservations remain held through uncertain sends and until authoritative reconciliation.

The egress recommendation is one account-scoped credential-owning boundary; ordinary workers and adapters have no direct venue route. A takeover requires positive external revocation/fencing of the old egress path, not lease expiry or a local epoch check. Added crash cases for ambiguous commits, before/during/after socket write, venue acceptance, fill-to-Ledger handoff, halt epoch transfer and incomplete RecoveryBarrier.

**Status:** architecture/test-plan refinement only. G1 technical baselines for OD-08/09/10/12 are selected in NX-ADR-008; exact libraries/providers, production security, numeric thresholds, operator identity and deployment choices remain open. No runtime, production transaction, trusted fence or venue credential was added. The stale-egress race remains a blocker.


## Persistence and trusted-egress option analysis — 2026-11-14

NX-REF-EXEC-002 §4.5 now compares persistence and egress topologies. Candidate model: Risk and Command use separately owned local ACID transactions (all-scope reservation commit before capability issuance; atomic single-use consume + command/outbox at Command); Ledger remains independently atomic/idempotent. Candidate egress boundary is one account-scoped credential/socket-owning workload with workers denied direct venue routes and takeover gated on positive external fencing. A DB lease/local epoch is explicitly insufficient to stop a stale process already past its final check. G1 technical baselines for OD-08/09/10/12 are selected in NX-ADR-008. Documentation/design only; no provider, database, key, proxy, host or deployment is installed or production-selected, and no runtime implementation is claimed. Exact-head CI evidence is recorded in the current checklist.



### Exact-head CI verification after persistence/egress analysis — 2026-11-14

- Documentation analysis head verified: `3187a69e443157ac3e66b874b4dcbb29588ddc70`.
- GitHub Actions run [#43606550889](https://github.com/PandaGarry/NEXUS/actions/runs/43606550889) completed successfully on that exact head.
- Three jobs passed: Python 3.11, 3.12 and 3.13. Each executed 13 isolated reference-model suites with counts 11, 24, 13, 17, 12, 16, 18, 18, 32, 12, 15, 28 and 21 = 237 tests per runtime; 711 successful test executions total.
- This CI run verifies the existing Python reference-model suites at the exact documentation-analysis head. It does not test the newly documented transaction alternatives, database isolation, production egress topology, external host/network fencing, Rust, venue behavior or live safety.


## Open-source component qualification — 2026-11-14

NX-RESEARCH-010 published a candidate shortlist. PostgreSQL is the leading persistence candidate for G1 evaluation only; OpenTelemetry Collector is the preferred observability candidate; OpenBao is a secrets-management candidate pending deployment/security/license review; NATS JetStream is deferred unless measured asynchronous fan-out/replay needs justify it; Cilium is conditional on a Kubernetes decision; Temporal is deferred; NautilusTrader remains test-only and is not trusted execution authority. No external dependency or runtime module was added. G0D dependency governance and OD-09 persistence selection remain open.


## Modular product architecture — 2026-11-14

- Published [NX-ARCH-006](architecture/NX-ARCH-006-modular-product-boundaries-and-trust-isolation.md) as PROPOSED / DESIGN ONLY.
- Proposed a protected domain core with independently governed product modules behind versioned contracts and deny-by-default admission. The core remains sole authority for Risk, Ledger, durable execution state and trusted egress.
- Identity & Access, Demo and Learning/Wiki are separate bounded domains. Demo/live separation must be enforced by account identity, storage/ledger ownership, service permissions and egress—not by UI flags. Learning has no access to trading secrets or financial write paths.
- Initial direction: modular monolith / limited separate trust domains, not microservices per feature and not arbitrary in-process plugin loading.
- No runtime modules, packages, identity provider, database, public registration, third-party extension mechanism or deployment topology selected/installed. Exact branch-head workflow #43608583358 passed on `e15e47f9512bc07a1f6534a4f41b0d27d7d42578`: 13 suites / 237 tests each on Python 3.11, 3.12 and 3.13 (711 successful reference-model executions). This does not test module isolation, identity, DB, secrets or egress. Cross-review and owner/security decisions remain OPEN; G0D/G1 remain BLOCKED as applicable.


## Platform extensibility and entitlement foundation — 2026-11-14

- Published [NX-ARCH-007](architecture/NX-ARCH-007-platform-extensibility-and-entitlements.md) as PROPOSED / STRATEGIC DESIGN ONLY.
- Defined a future product-domain taxonomy covering Identity, Trading Core, Demo, Analytics/Research, Strategy Lab, Automation, Learning, Portfolio/Reporting, Collaboration, API/Integrations, Billing/Entitlements and Administration/Support.
- Separated product capability, commercial entitlement and security authorization. A subscription, successful payment, plan claim or feature flag cannot grant or bypass Risk, Ledger, venue eligibility, limits, halt or trusted egress.
- Defined stable feature identifiers, auditable entitlement grants, explicit subscription lifecycle, replay-safe billing webhook handling, quotas distinct from Risk limits, downgrade/data-retention principles and compatibility requirements.
- Public SaaS, multi-tenancy, teams, payment provider, plans/prices, public registration and commercial launch remain separate gated decisions. No payment integration, entitlement service, tenant runtime, module or product feature was implemented.
- NX-ARCH-007 is a design artifact only; cross-review, G0D/G1, owner/legal/security approvals remain OPEN.


## Module registry and admission governance — 2026-11-14

- Published [NX-ARCH-008](architecture/NX-ARCH-008-module-registry-admission-capability-governance.md) as PROPOSED / DESIGN ONLY.
- Defined immutable module and artifact identity, registry-controlled lifecycle states, module classes and trust tiers, plus the distinction between manifest declarations, capability definitions, workload grants and request-time authorization.
- Added a proposed data-access matrix for product domains, explicit exclusions for optional-module access to Risk/reservations/Ledger/direct venue egress, and requirements for contract compatibility, dependency governance, revocation, rollback and runtime isolation.
- Added 20 adversarial qualification scenarios with a requirement to inspect authoritative state and actual enforcement boundaries, not only mocked policy outcomes.
- No registry runtime, schema validator, signing/grant service, sandbox, module, dependency or deployment technology was implemented or selected. G0D/G1 and owner/security review remain BLOCKED/OPEN as applicable.


## Exact-head verification — NX-ARCH-008


### NX-ARCH-008 exact-head regression verification — 2026-11-14

- Exact branch HEAD `b1d3201a1fe1706909218943f5464eba43ea1041` passed GitHub Actions [#43611030968](https://github.com/PandaGarry/NEXUS/actions/runs/43611030968).
- All three jobs completed successfully: Python 3.11, 3.12 and 3.13; 13 isolated reference-model suites / 237 tests per runtime; 711 successful test executions total.
- This verifies the existing Python reference-model regression workflow at that exact documentation head. It does **not** test NX-ARCH-008's proposed registry, schema, identity, grant issuance, module isolation, secret handling, database permissions, network/egress enforcement, Rust, venue behavior or live-trading safety.
- The exact-head CI result is regression evidence only; NX-ARCH-008 remains PROPOSED / DESIGN ONLY and G0D/G1 remain open.


## Final synchronized documentation-head verification


### Final synchronized documentation-head verification — 2026-11-14

The synchronized documentation head `c5c00d37b26f365b79690a9f3297ab571d9ec6f2` passed exact-head GitHub Actions [#43611122433](https://github.com/PandaGarry/NEXUS/actions/runs/43611122433). Python 3.11, 3.12 and 3.13 jobs all completed successfully; each ran 13 isolated reference-model suites / 237 tests (711 successful executions total). This is existing Python reference-model regression evidence only. It does not test NX-ARCH-008's proposed registry, manifest, workload identity, grants, module runtime/isolation, secrets, database permissions, network/egress enforcement, Rust, venue behavior or live-trading safety. NX-ARCH-008 remains PROPOSED / DESIGN ONLY; G0D/G1 remain open.


## Module governance cross-review — 2026-11-14

- Published [NX-ARCH-REVIEW-002](architecture/NX-ARCH-REVIEW-002-module-governance-cross-review.md), cross-reviewing NX-ARCH-001/006/007/008, NX-SEC-001, NX-IF-001..005 and NX-OWNER-DECISIONS-001.
- No blocking design contradiction remains after two wording clarifications: gateway admission checks versus owning-service authorization; T4 protection tier versus separate protected workload identities/authorities.
- Retained findings F-03..F-08 as open: executable permission mapping, revocation propagation objectives, registry/signing/workload identity trust roots, actual DB/host/network isolation evidence, first G1 module/resource budgets and operator/support governance.
- Cross-review is design-level only. No owner decision or gate is closed; no module runtime, registry, security control or dependency is implemented. G0D/G1 remain open.


## Capability catalog and authorization contracts — 2026-11-14

- Published [NX-ARCH-009](architecture/NX-ARCH-009-capability-catalog-authorization-contracts.md), turning the broad module matrix into a proposed capability contract model.
- Defined stable capability IDs/versioning, owner and enforcement authority, typed resource scopes, data classifications, an initial 12-entry candidate catalog, and a module-to-capability/negative-test mapping.
- Explicitly excluded protected financial operations and Trusted Egress from optional-module grants; documented the request-time authorization sequence and separation from product entitlements.
- Added revocation/cache/outage requirements, audit/privacy constraints and 18 adversarial CAP scenarios.
- No executable schema, policy engine, grant issuer, active permission, module runtime or dependency was implemented. Cross-review, domain/security acceptance and G0D/G1 remain open.


## Capability catalog cross-review — 2026-11-14

- Published [NX-ARCH-REVIEW-003](architecture/NX-ARCH-REVIEW-003-capability-authorization-cross-review.md) for NX-ARCH-009.
- Narrowed billing subscription capability to intent submission only; entitlement-state writes remain exclusively with Billing after provider verification/reconciliation.
- Confirmed separation of capability definition, module declaration, workload grant, product entitlement, user authorization and resource-owner decision.
- Retained CAP-R-02..09 and added CAP-19..26 as future qualification requirements.
- Cross-review is design-level only. No candidate capability is approved or active; no schema, policy engine, grant issuer or runtime exists. G0D/G1 remain open.


## Capability-to-interface contract traceability — 2026-11-14

- Located and inspected the canonical NX-IF-001..005, NX-SEC-001 and NX-OWNER-DECISIONS-001 files on the active engineering branch.
- Published [NX-ARCH-REVIEW-004](architecture/NX-ARCH-REVIEW-004-capability-to-interface-contract-traceability.md), mapping all 12 proposed NX-ARCH-009 capabilities to existing contract evidence or an explicit missing-contract gap.
- Confirmed the IF contracts are protected execution, Risk, Ledger, recovery and emergency-control boundaries, not general module APIs or direct data-store grants.
- Recorded v1 account/subaccount scope constraints, missing product-domain contracts, cross-cutting contract requirements and a source-grounded but incomplete data inventory.
- Field-level classification/retention, domain-owner acceptance, revocation objectives and boundary-observed G1 evidence remain open. No runtime, permission, dependency or integration was added.


### NX-ARCH-REVIEW-004 exact-head regression evidence — 2026-11-14

Exact branch HEAD `f78fc7d006ea475cf596ee2bd8bd65b9a7d37afa` passed GitHub Actions [#43613212116](https://github.com/PandaGarry/NEXUS/actions/runs/43613212116). Python 3.11, 3.12 and 3.13 all succeeded: 13 isolated reference-model suites / 237 tests per runtime, 711 successful executions total. This is regression evidence for the existing Python reference models only; it does not execute the capability traceability review, product-domain APIs, authorization grants, module isolation, field-level data controls, Rust or venue integration. NX-ARCH-REVIEW-004 remains design-only; G0D/G1 and owner/security acceptance remain open.


## Revocation, freshness and outage objectives — 2026-11-14

- Published [NX-ARCH-REVIEW-005](architecture/NX-ARCH-REVIEW-005-revocation-freshness-outage-objectives.md) to turn NX-ARCH-008/009, NX-IF-004/005 and NX-SEC-001 requirements into measurable candidate profiles and an outage matrix.
- Kept authorization freshness, source-data freshness, halt/control propagation and RecoveryBarrier readiness as distinct concepts.
- Proposed conservative non-production authorization-cache/revocation/cancellation targets for discussion only; explicitly did not select global market/account/Ledger freshness thresholds or a halt deadline.
- OD-10 and OD-12 remain OPEN; all numeric objectives require owner/security/domain-owner approval and boundary-observed measurement. No policy engine, cache, revocation service, runtime or network fence was implemented.


### NX-ARCH-REVIEW-005 exact-head regression evidence — 2026-11-14

Exact branch HEAD `97a1819527bf6b1973793b12a084ef8cd0dee776` passed GitHub Actions [#43613493976](https://github.com/PandaGarry/NEXUS/actions/runs/43613493976): Python 3.11/3.12/3.13, 13 isolated reference-model suites / 237 tests per runtime (711 successful executions). This verifies existing Python reference-model regression only; it does not test proposed authorization cache/revocation objectives, outage behavior, source freshness, halt propagation, cancellation, actual process/DB/secret/network fencing, Rust or venue integration. Numeric targets in NX-ARCH-REVIEW-005 remain proposals; OD-10/12 and owner/security acceptance remain open.

## CI supply-chain hardening and PR integration graph — 2026-11-14

- CI workflow `.github/workflows/reference-model.yml` now pins `actions/checkout` v7.0.1 to `3d3c42e5aac5ba805825da76410c181273ba90b1` and `actions/setup-python` v7.1.0 to `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`.
- Exact action-upgrade HEAD `e35d81cb34aeae1c13e25def0320e8a4a4b649bb` passed [GitHub Actions #43614458632](https://github.com/PandaGarry/NEXUS/actions/runs/43614458632): Python 3.11/3.12/3.13, 13 isolated suites and 237 tests per runtime, 711 successful executions total.
- Job logs no longer report Node.js 20 deprecation or Node `punycode` deprecation warnings. Direct actions are SHA-pinned; transitive action dependency locking/inventory remains open.
- Verified stacked PR graph: #13 head `bb6400502640818fd5eba8a93eb3ae8dc54581d2` is #14 base; #14 head `ab6976933cb4de9b5320b73531034d02edc53907` is #16 base. The #16 base is intentional and must not be retargeted to the default branch or merged ahead of its parents.
- All three PRs remain Draft/open/unmerged. PR #16 remains 28 changed files / 3,730 additions / 55 deletions and 205 commits beyond PR #14's head. Its scope/reviewability needs a dependency-aware disposition; no automatic merge or stack rewrite was performed.
- Evidence boundary: this is Python reference-model CI, not Rust, production transaction isolation, external egress fencing, venue integration or live-safety evidence. G0D/G1 remain BLOCKED; live trading NOT AUTHORIZED.


## Numeric wire resource-boundary hardening — 2026-11-14

- Hardened the test-only numeric wire parser against short-encoded but extreme decimal scales and interpreter integer-string conversion ceilings.
- Added optional max_scale; default scale ceiling is the caller's max_chars budget. Oversized integer conversion failures map to stable NUMERIC.RESOURCE_LIMIT.
- Added regression coverage for decimal/rational oversized integers and scale-budget failures.
- Exact code/test HEAD b0fb99d4505ba5eb405788fee8ce447f28437479 passed [GitHub Actions #43614612130](https://github.com/PandaGarry/NEXUS/actions/runs/43614612130): 13 isolated suites / 239 tests per Python 3.11, 3.12 and 3.13; 717 successful executions total.
- This is reference-only hardening. No production numeric limits, normalized fixture schema/runner, Rust implementation or live execution path was added; G0D/G1 remain open.


## G1 technical baseline selected — 2026-11-14

- Published [NX-ADR-008](architecture/NX-ADR-008-g1-technical-baseline-storage-and-capability-signing.md) under the owner's expanded delegation to select the safest technical baseline for G1 design/qualification.
- Canonical command bytes: restricted RFC 8949 deterministic CBOR; SHA-256 domain-separated digest; COSE_Sign1 fully specified COSE Ed25519 algorithm (-19, RFC 9864) for RiskApprovalCapability. Exact libraries, key custody and security/jurisdictional review remain gated.
- Persistence: PostgreSQL 18 is the G1 evaluation target only. Initial topology is one primary, service-owned schemas/roles and separate Risk/Command/Ledger local ACID transactions. No distributed transaction, broker-as-source-of-truth or automatic failover.
- Freshness/recovery: source-specific EvidenceRequirementSet/FreshnessPolicy, watermarks/completeness, monotonic elapsed-time and fail-closed UNKNOWN; no global TTL. Numeric thresholds and RTO/RPO remain owner/source decisions.
- Emergency operations: single Owner, step-up resume after READY RecoveryBarrier, no automatic cancel-all/flatten or offline emergency order plan; break-glass containment only.
- These are G1 design/qualification choices, not production approval. No package, database, key, cloud, venue, credential or runtime was installed/selected for production. G0D/G1 evidence gates remain open; live trading NOT AUTHORIZED.

## COSE signing-profile standards correction — 2026-11-14

A standards cross-check of NX-ADR-008 found that RFC 9053's polymorphic COSE EdDSA identifier (-8) was superseded for fully specified algorithm use by RFC 9864 (October 2025). The G1 profile now specifies COSE Ed25519 algorithm identifier **-19**, with COSE key type OKP and Ed25519 curve. The deprecated polymorphic identifier (-8), Ed448, algorithm/key mismatch and substitution are rejected. Protected `kid` is only an integrity-protected lookup hint: it is not assumed unique or independently authoritative; key resolution is issuer/algorithm/purpose/status/generation-bound and fails closed on ambiguity. No cryptographic implementation or key custody provider is selected. Cross-language signature vectors and provider qualification remain open.


## Canonical CBOR ingress hardening requirement — 2026-11-14

NX-ADR-008 now explicitly requires strict deterministic-profile validation on received command bytes before object materialization: shortest-form arguments/lengths, definite lengths, RFC 8949 core bytewise-lexicographic map ordering, schema-defined text keys, duplicate/unknown-key rejection and no trailing bytes. This closes a protocol-specification ambiguity; it does not mean a parser exists. Library suitability must be demonstrated against raw-byte adversarial vectors before dependency selection.


## PR ancestry and current verification — 2026-11-14

- PR #16 is intentionally stacked on PR #14. Full direct ancestry verified by matching child base SHA to parent head SHA: #1 -> #2 -> #3 -> #4 -> #5 -> #6 -> #7 -> #9 -> #10 -> #11 -> #12 -> #13 -> #14 -> #16. PR #8 is a parallel branch, not an ancestor.
- Every PR in this direct ancestry is currently open, Draft and unmerged. PR #16 is therefore not independently mergeable; its base is correct and must not be retargeted to main. Parent-first integration is required; no merge or branch rewrite was performed.
- Current PR #16 diff: 248 commits beyond its immediate base, 32 files, 4,399 additions and 72 deletions. Scope/reviewability needs a deliberate disposition.
- Current exact branch HEAD `7914772358d2ee49c87374373bad5c589d0a2905` passed [workflow #43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349): 13 isolated Python reference suites, 239 tests each on 3.11/3.12/3.13 (717 executions). Node.js 20 and punycode deprecation warnings are absent.
- This CI is Python reference-model evidence only. Rust, PostgreSQL transactions, COSE signing, Trusted Egress fencing, venue adapters and live execution remain unimplemented/unverified. PR #16 remains Draft/open/unmerged.

## Final synchronized G1 baseline / standards exact-head verification — 2026-11-14

Final branch HEAD `7914772358d2ee49c87374373bad5c589d0a2905` passed GitHub Actions [#43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349). Python 3.11, 3.12 and 3.13 all succeeded; each executed 13 isolated reference-model suites / 239 tests (717 successful executions total). All three job logs are free of test failures and the previous Node.js 20 / `punycode` deprecation warnings. This verifies only the existing Python reference-model regression workflow. It does not validate the proposed CBOR/COSE protocol implementation, PostgreSQL transactions, Rust, actual process/host/network fencing, Trusted Egress, venue adapters or live trading. PR #16 remains Draft/open/unmerged; G0D/G1 implementation and boundary evidence remain open; live trading NOT AUTHORIZED.

## Post-synchronization exact-head regression — 2026-11-14

Branch HEAD `928d5fd261553676c3fad6a8e88b984a862af338` passed [GitHub Actions #43615282210](https://github.com/PandaGarry/NEXUS/actions/runs/43615282210): Python 3.11, 3.12 and 3.13 each passed 13 isolated suites / 239 tests (717 successful executions total). All three logs contain no failures or Node.js 20 / `punycode` deprecation warnings. This is Python reference-model regression only; no Rust, CBOR/COSE, PostgreSQL, actual egress fence, venue or live-safety implementation was exercised.


## Post-sync exact-head verification — 2026-11-14

- Current branch HEAD `9e9035033da77d958601cb6b69128e13e2551a0d` passed [GitHub Actions #43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737): 13 isolated Python reference suites, 239 tests each on Python 3.11/3.12/3.13 (717 successful executions).
- All three logs are free of Node.js 20 and punycode deprecation warnings.
- Current PR #16 snapshot: 265 commits, 32 files, 4,467 additions, 72 deletions; full parent ancestry remains open/Draft and PR #16 remains Draft.
- This is reference-model CI only; Rust, PostgreSQL, COSE, trusted egress, venue adapters and live trading are not verified.

## Full stacked-PR ancestry and current exact-head verification — 2026-11-14

GitHub metadata confirms the direct dependency chain by exact SHA equality: PR #1 → #2 → #3 → #4 → #5 → #6 → #7 → #9 → #10 → #11 → #12 → #13 → #14 → #16. PR #8 is a parallel branch from PR #7 and is not an ancestor of #16. All direct-chain PRs remain open, Draft and unmerged. PR #16 correctly targets PR #14's exact head; parent-first integration is mandatory.

Current PR #16 head `9e9035033da77d958601cb6b69128e13e2551a0d` passed [workflow #43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737): 13 isolated Python reference suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 successful executions). No test failures or Node.js 20 / `punycode` deprecation warnings. This is reference-model regression only; Rust, CBOR/COSE, PostgreSQL, Trusted Egress, external fencing, venue and live-safety behavior remain untested.

## CBOR / COSE library qualification — NX-RESEARCH-011

Published [NX-RESEARCH-011](research/NX-RESEARCH-011-cbor-cose-library-qualification.md). Rust `cbor2` 1.1.6 is a candidate for RFC 8949 core deterministic encoding and raw-byte preservation but does not provide the complete strict NEXUS ingress gate by itself. `cbor-core` 0.10.1 is not a drop-in protocol codec because it targets a draft profile, uses length-first ordering and has an unstable API. `coset` 0.4.2 is the leading COSE_Sign1 structure candidate for test-only evaluation (alg=-19 and original protected-header preservation), while `cose2`'s bundled Ed25519 provider uses deprecated alg=-8. Python `pycose` is not selected as a reference oracle. No dependency or runtime was added; exact strict-parser, cross-language vector, provenance, SBOM and fuzz qualification remain open G0D/G1 work.

## CBOR command-key profile refinement — 2026-11-14

NX-ADR-008 and OD-08 now restrict command map keys to schema-defined ASCII text field names. User-provided identifiers and Unicode text remain values, subject to strict UTF-8 and no implicit Unicode normalization. This reduces key-alias and schema ambiguity; it does not replace raw-byte deterministic validation. No parser implementation or dependency was added.

## Exact-head CI after CBOR / COSE qualification and OD-08 key-profile refinement — 2026-11-14

Branch HEAD `1bb2192e6746e0f86659f006ef204990adc81188` passed [GitHub Actions #43615753905](https://github.com/PandaGarry/NEXUS/actions/runs/43615753905): Python 3.11/3.12/3.13 each passed 13 isolated reference suites / 239 tests (717 successful executions total). No failures or Node.js 20 / `punycode` deprecation warnings. The run verifies Python reference models only; it does not execute CBOR/COSE candidates, the strict byte validator, Rust, PostgreSQL, Trusted Egress, external fencing, venues or live safety.

## Final CI action-runtime and serialization-research verification — 2026-11-14

Branch HEAD `69657a0808b859b17ab94a6d3e008a2ae9671cc7` passed [workflow #43615820603](https://github.com/PandaGarry/NEXUS/actions/runs/43615820603): Python 3.11/3.12/3.13 each passed 13 isolated reference suites / 239 tests (717 successful executions total). Job logs contain no failures or Node.js 20 / `punycode` deprecation warnings. The exact pinned `actions/checkout` v7.0.1 and `actions/setup-python` v7.1.0 manifests were fetched from their pinned commit SHAs and both declare Node 24. This verifies the Python reference models and direct action runtime only; it does not validate Rust, CBOR/COSE libraries, PostgreSQL, Trusted Egress, external fencing, venue adapters or live trading.

## COSE key-resolution trust boundary — 2026-11-14

NX-ADR-008 and NX-RESEARCH-011 now explicitly treat all token-supplied metadata—including protected `kid`/`alg` and payload issuer/audience—as untrusted until signature verification. Candidate lookup is bounded to a local versioned registry; token-directed remote key retrieval is forbidden. Local expected issuer/audience and key-purpose policy must be enforced, then signed claims checked against that context. Verification accepts only public OKP/Ed25519 (32-byte public key), rejects private key material outside Risk, requires a 64-byte signature and fails closed on ambiguous/stale/revoked key resolution. This is a protocol requirement, not an implemented verifier.

## COSE_Sign1 serialization profile — 2026-11-14

NX-ADR-008 and NX-RESEARCH-011 now define one exact wire representation: untagged embedded-payload four-element COSE_Sign1; protected header has only alg=-19 and bounded byte-string kid; unprotected map is empty; capability claims are a single NEXUS deterministic-CBOR payload. The verifier preserves exact protected-header and payload bytes, constructs Sig_structure using RFC 9052 §9 deterministic encoding and rejects detached/tagged/extra-header alternatives. This removes representation ambiguity from the design; no implementation has been selected or tested yet.

## COSE key-resolution boundary and exact-head verification — 2026-11-14

NX-ADR-008 and NX-RESEARCH-011 now require token-supplied `kid`, `alg`, issuer and audience to remain untrusted until signature verification. Candidate lookup is bounded to a local versioned registry; token-directed remote key retrieval is forbidden. Local expected issuer/audience/algorithm/purpose govern candidate selection, and signed claims must match that local context after verification. Only public OKP/Ed25519 verification material (32-byte public key) is exposed to Execution; private key material remains within Risk; signature length is 64 bytes. This is a design requirement, not an implemented verifier.

The exact branch HEAD `6fefd9a44ff2f272b6516265d10f41c46a13cf7a` passed [workflow #43615911362](https://github.com/PandaGarry/NEXUS/actions/runs/43615911362): Python 3.11/3.12/3.13 each passed 13 isolated reference suites / 239 tests (717 successful executions total). No test failures or Node.js 20 / `punycode` warnings. The run does not exercise COSE, Rust, PostgreSQL, Trusted Egress, venues or live trading.

## Exact-head CI after COSE protected-header and key-resolution refinement — 2026-11-14

Branch HEAD `88fcb30068507d85fb35802ca5d2195fd528c000` passed [workflow #43616054657](https://github.com/PandaGarry/NEXUS/actions/runs/43616054657): Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 successful executions). No test failures or Node.js 20 / `punycode` warnings. This remains Python reference-model CI only; it does not validate the proposed COSE protected-header parser, signer/verifier, key registry, Rust, PostgreSQL, egress fencing, venue behavior or live safety.

## Exact-head CI after COSE_Sign1 wire-profile specification — 2026-11-14

Branch HEAD `8d2c2f404782b718f1a3a422bb0ce918bb6b922d` passed [workflow #43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308): Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 successful executions total). No failures or Node.js 20 / `punycode` deprecation warnings. This is Python reference-model CI only; no COSE wire parser, signer, verifier, key registry or cross-language signature vector was executed.

## Exact COSE profile and current stacked-PR verification — 2026-11-14

- PR #16 current verified snapshot: `8d2c2f404782b718f1a3a422bb0ce918bb6b922d`, 33 changed files, 4,937 additions, 72 deletions and 322 commits in the stacked comparison (including parent history). It remains open/Draft/unmerged.
- Re-verified the direct chain by exact base/head SHA equality: #1 → #2 → #3 → #4 → #5 → #6 → #7 → #9 → #10 → #11 → #12 → #13 → #14 → #16. PR #8 is a parallel branch from #7, not an ancestor. Every PR in the direct chain is currently open, Draft and unmerged; PR #16's immediate base is PR #14's exact head.
- Exact-head workflow [#43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308) passed on Python 3.11/3.12/3.13: 13 isolated suites / 239 tests per runtime, 717 successful executions total. All three logs inspected; no failures or Node.js 20 / `punycode` warnings.
- COSE_Sign1 now has one exact application wire profile in NX-ADR-008: untagged, embedded payload, four-element array; protected alg=-19 and 1–64-byte kid only; empty unprotected map; deterministic-CBOR capability payload; exact protected/payload byte preservation; RFC 9052 §9 Sig_structure; fixed external AAD. Token metadata is untrusted until verification; key lookup is local and bounded.
- Evidence remains Python reference-model-only. No Rust, CBOR/COSE runtime, PostgreSQL, Trusted Egress, external fence, venue adapter or live trading behavior was exercised. G0D/G1 implementation and evidence gates remain open.

## Final exact-head CI after COSE wire-profile synchronization — 2026-11-14

Branch HEAD `71afa64c00affed017c1f072600f4f0e4aaeccc6` passed [workflow #43616247630](https://github.com/PandaGarry/NEXUS/actions/runs/43616247630): Python 3.11/3.12/3.13 each passed 13 isolated reference suites / 239 tests (717 successful executions total). No failures or Node.js 20 / `punycode` deprecation warnings. This is Python reference-model regression only; it does not execute the COSE wire profile, strict CBOR parser, Rust, PostgreSQL, Trusted Egress, venue adapters or live execution.

## Final synchronized PR #16 exact-head CI — 2026-11-14

Branch HEAD `3af0453897545b77fee358b9902a6301f662232e` passed [workflow #43616348161](https://github.com/PandaGarry/NEXUS/actions/runs/43616348161): Python 3.11/3.12/3.13 each passed 13 isolated suites / 239 tests (717 successful executions total). All three logs show no failures or Node.js 20 / `punycode` deprecation warnings. This is reference-model CI only; Rust, CBOR/COSE, PostgreSQL, Trusted Egress, venue adapters and live execution remain untested. PR #16 remains Draft/open/unmerged and stacked parent-first.

## Risk reservation concurrency design — 2026-11-14

NX-ADR-008 §5.3 now defines a Risk-owned scope-state record as the common serialization point for reservation commits and Risk's derived exposure-projection updates. Ledger remains journal owner and cannot write Risk-owned state directly; Risk consumes Ledger/venue/external exposure events through an idempotent inbox and updates projection, watermark and scope state in its own local transaction. Multi-scope reservations process all pre-provisioned scope rows in deterministic ID order and commit atomically. Stale/incomplete projections, missing scope rows and unresolved commit authority fail closed. Whole-transaction retry is bounded for SQLSTATE 40001/40P01; stable idempotency identity/digest handles ambiguous commits. NX-IF-002 §6.4 and OD-09 are synchronized.

This is a design protocol only. No PostgreSQL schema, service, transaction or concurrency test has been implemented. Exact patch/version, role grants, query/lock behavior, crash/recovery and adversarial concurrency evidence remain open.

## Field-level data lineage and projection governance — NX-ARCH-REVIEW-006

Published [NX-ARCH-REVIEW-006](architecture/NX-ARCH-REVIEW-006-field-level-data-lineage-and-projection-governance.md) after inspecting the actual fields in NX-IF-001..005 and NX-SEC-001. The review maps proposed classifications and source ownership for command/approval, exposure/reservation, execution/Ledger, evidence/recovery and halt/emergency objects. It defines restrictions for future Analytics/Portfolio/Notifications/Strategy/Demo/Learning/Billing projections and explicitly identifies that IF-003 does not yet enumerate the complete Ledger journal-leg schema. Field classifications, retention/legal basis and projection allowlists remain proposals requiring source-owner/security approval. No API, schema, grant, store or runtime was implemented.

## Risk reservation and exposure-projection serialization — 2026-11-14

The PostgreSQL G1 evaluation design is now consistent across NX-ADR-008 §5.3, NX-IF-002 §6.4/§11, NX-REF-EXEC-002 §4.5 and OD-09. Risk owns its derived exposure projection, source watermarks, scope-state version and reservation aggregates. Reservation commits and Risk projection updates update the same Risk-owned scope-state record; Ledger remains journal owner and cannot write Risk state directly. Risk consumes Ledger/venue/external facts via an idempotent inbox. Multi-scope account/child reservations update all pre-provisioned scope rows in deterministic ID order and commit atomically. Stale/incomplete source evidence, missing scope state or unresolved commit/primary authority fails closed.

The acceptance plan now explicitly covers projection/reservation races, duplicate/reordered events, 40001/40P01 full-transaction retries, idempotency conflicts, ambiguous commits and recovery. PostgreSQL 18 remains an evaluation target only; no schema, database instance or runtime is implemented.
Unknown Risk reservation commit handling now explicitly distinguishes a missing visible row from a proven rollback: if the original transaction may still be in flight, absence is not proof of rollback. A retry can use only the same stable request identity/digest so the unique constraint arbitrates; if primary authority or outcome remains uncertain, keep the scope HALTED.

## Risk scope serialization and PostgreSQL concurrency — NX-ARCH-REVIEW-007

Published [NX-ARCH-REVIEW-007](architecture/NX-ARCH-REVIEW-007-risk-scope-serialization-and-postgresql-concurrency.md) and synchronized its findings into NX-ADR-008 §5.3, NX-IF-002 §6.4 and OD-09. The G1 design now requires every projection event to update all affected parent/account and child scope-state rows atomically; scope hierarchy changes serialize and advance scope_config_version; the logical state row carries monotonic projection/reservation/source versions; and SQLSTATE 23505 is resolved only as a known idempotency collision, never blindly retried. PostgreSQL 18 SERIALIZABLE remains an evaluation baseline only. Concurrency, role separation, throughput, failover and old-primary fencing remain unproven; no database/schema/runtime was implemented.

## Exact-head CI after NX-ARCH-REVIEW-007 — 2026-11-14

Branch HEAD `e7c5461ae7ccea4f29fc77461db91d44566aba36` passed [workflow #43616908979](https://github.com/PandaGarry/NEXUS/actions/runs/43616908979): Python 3.11/3.12/3.13 each passed 13 isolated reference suites / 239 tests (717 successful executions). All three logs show no failures or Node.js 20 / `punycode` deprecation warnings. This is Python reference-model regression only; no PostgreSQL concurrency harness, database, Rust, CBOR/COSE, Trusted Egress, venue or live path was exercised.

## Numeric-wire parser resource determinism — 2026-11-14

The Python reference numeric-wire parser now enforces a fixed 512-decimal-digit limit for every integer field (decimal coefficient/scale and rational numerator/denominator), separately from the overall max_chars limit. Oversized values fail as NUMERIC.RESOURCE_LIMIT before interpreter integer conversion. Regression tests cover 512-digit acceptance and 513-digit rejection. This removes normal acceptance dependence on Python's configurable integer-string conversion threshold. The value is a reference parser resource budget only—not a production numeric profile, financial limit or Risk policy. Rust parity remains open.
## Risk scope root guard and valuation-input boundary — 2026-11-14

NX-ADR-008 §5.3, NX-IF-002 §6.4, NX-ARCH-REVIEW-007 and OD-09 now require the account/root scope-state record in every v1 reservation and projection transaction; after acquiring the complete lock set, the transaction rechecks the root scope_config_version and recomputes the scope set if it changed. Market/index/FX/fee/collateral inputs remain immutable versioned snapshots bound to the reservation and signed capability. Market-data ticks do not rewrite scope-state rows; stale or policy-invalid valuation inputs block dispatch. Trusted Egress validates the exact signed valuation_input_vector_id/version against the authoritative persisted Risk evidence manifest and MUST NOT fetch replacement market/FX/fee/collateral values or call source services on the dispatch path. If the manifest is unavailable or cannot prove the bound vector admissible, Egress denies send. This avoids turning each price tick into a serialized write while preserving the exact valuation basis used by Risk.

No market-data valuation service, schema or runtime was implemented; source freshness and dispatch-time invalidation still require conformance proof.

## Valuation-input consistency boundary — 2026-11-14

NX-ADR-008, NX-IF-002 and NX-ARCH-REVIEW-007 now distinguish Risk-owned economic exposure state from source-owned immutable market/index/FX/fee/collateral snapshots. The design does not assume these sources share PostgreSQL or a distributed transaction. Risk binds an exact version vector and source evidence to the reservation/approval; Trusted Egress must revalidate freshness and any configured drift/admissibility policy before send. A newer source version never silently mutates an existing approval; an inadmissible vector requires a new Risk evaluation/reservation. Interface schema, cross-source snapshot coherence and numeric thresholds remain open. No runtime is implemented.

## PostgreSQL 18.7 G1 patch-level qualification — 2026-11-14

Published [NX-RESEARCH-012](research/NX-RESEARCH-012-postgresql-18-7-g1-evaluation-qualification.md) after reviewing the official PostgreSQL Global Development Group announcement and 18.7 release notes. PostgreSQL 18.7 is selected as the exact G1 evaluation patch only; it was the latest supported 18.x minor on 2026-11-14. The release fixes 52 security vulnerabilities and more than 140 bugs, but its migration notes warn about affected index corruption and existing incremental backup chains. G1 therefore starts with a fresh full backup, no third-party/C extensions, no unreviewed extension scripts, no dblink/untrusted replication subscriptions and base-table-only authoritative writes. Exact package provenance, platform, backup/restore/PITR, schema-specific REINDEX review and concurrency proof remain open. No database is installed and production remains unselected.
