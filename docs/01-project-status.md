# Текущий статус проекта

**Дата среза:** 2026-11-14  
**Общий статус:** BLOCKED — Prototype Readiness Gate не пройден; bounded v1 scope decisions OD-01/04 accepted  
**Текущая фаза:** Phase 0 — Foundation Audit / Architecture Synthesis

| Область | Статус | Комментарий |
|---|---|---|
| Цель и продуктовые границы | Accepted / personal-first proposal | NEXUS v1 proposed as closed single-owner personal product; no public users or commercial service in initial scope. NX-ARCH-002 is proposed and requires owner review |
| Архитектурные принципы | Proposed / Partially accepted | Требуются финальные ADR |
| Tradoor audit | In Progress | Source pass обновлён до HEAD 6ab3877; funding/private execution capability audit добавлен в NX-RESEARCH-002. Полная per-venue сертификация, instrument metadata и runtime verification остаются открыты |
| Exchange capabilities matrix | Incomplete | Trade/book/OI/liquidation первично просмотрены; per-channel matrix и UNKNOWN поля ещё не закрыты |
| Simulation fidelity | In Progress | Tradoor paper-модель недостаточна для реалистичного исполнения |
| Runtime verification | Partial / reference-only | GitHub Actions run [#43591592168](https://github.com/PandaGarry/NEXUS/actions/runs/43591592168) passed exact PR HEAD `2128771d6de67636f3b86dc40e137049c6e41fbd`: 11 exact-decimal, 24 gateway and 13 egress-handover tests on Python 3.11, 3.12 and 3.13 (144 test executions across the matrix; 1,000 seeded rational-oracle cases run inside each exact-decimal suite). Reference-only; no production runtime, real egress fencing or exchange-adapter verification claimed |
| Security threat model | Drafted / Proposed | NX-SEC-001 сохранён; owner review, deployment-specific analysis и security verification не выполнены |
| Exact arithmetic / instrument specs | ADR proposed / implementation not started | NX-ADR-005 drafted; требует owner review и последующих golden tests. Блокер реализации сохраняется |
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
