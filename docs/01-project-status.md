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
| Runtime verification | Partial / limited | 10 reference-model unit tests and 10,000 randomized exact-arithmetic checks passed in an isolated local directory using exact fetched files; PR #10 has no returned GitHub Actions runs; no production runtime/CI PASS claimed |
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


- **WP-C — Execution ↔ Ledger:** NX-IF-003 создан как PROPOSED design draft. Определены source ownership, canonical fill identity, durable Execution outbox/Ledger inbox, atomic balanced journal posting, fee/correction semantics, projection watermark и WP-B FILL_PENDING_LEDGER handoff. Owner decisions, implementation choices and conformance evidence remain open; no implementation or tests claimed.
- **WP-D — Freshness & Recovery:** NX-IF-004 создан как PROPOSED design draft. Определены StateEvidenceVector, source-specific freshness/quality/reconciliation dimensions, versioned EvidenceRequirementSet/FreshnessPolicy, RecoveryCase/quarantine, scoped generation-fenced RecoveryBarrier и dependency-aware restart/reconciliation ordering. Owner thresholds, venue/account scope, persistence and operator decisions remain open; no implementation or tests claimed.
- **WP-E — Emergency Operations:** NX-IF-005 создан как PROPOSED design draft. Определены monotonic scoped HaltState/epochs, explicit CREATE/AMEND/CANCEL/CLOSE/REDUCE_ONLY/CANCEL_ALL/FLATTEN classification, bounded EmergencyActionPlan, protective-order handling, operator step-up/dual-control and gated resume. Venue capability certification, role assignments and emergency-policy decisions remain open; no implementation or tests claimed.

- [NX-RESEARCH-003 — First-Venue Shortlist](research/NX-RESEARCH-003-first-venue-shortlist.md) — Coinbase/Kraken conditional comparison; exact venue/product selection remains open pending legal/account eligibility and API capability qualification.

## Новые архитектурные артефакты (PROPOSED)

- [NX-ARCH-002 — Product & Deployment Profiles](architecture/NX-ARCH-002-product-deployment-profiles.md) — personal-first single-owner scope; PERSONAL_DEV / PERSONAL_TEST / PERSONAL_PRODUCTION and separately gated future COMMERCIAL profile. Design only; no runtime enforcement or live authorization.

- [NX-ADR-001 — Unified Market Event Contract](architecture/NX-ADR-001-unified-market-event-contract.md) — canonical event envelope, typed payload semantics, exact units, timestamps, provenance, ordering and schema evolution. Design only; no implementation or conformance tests.
- [NX-ARCH-001 — Target Architecture & Deployment Topology](architecture/NX-ARCH-001-target-architecture.md) — logical boundaries, trust model, command/data flows, deployment baseline and owner decisions. Design only; no implementation or runtime verification.
- [NX-ARCH-REVIEW-001 — Cross-Specification Contract Review](architecture/NX-ARCH-REVIEW-001-cross-specification-contract-review.md) — bounded review of cross-service contracts; 12 findings, five closure work packages, interface readiness BLOCKED.
- [NX-IF-001 — Canonical Trade Command & Risk Approval Contract](architecture/NX-IF-001-canonical-trade-command-risk-approval-contract.md) — WP-A proposed contract for TradeIntent → CanonicalTradeCommand → RiskApprovalCapability; implementation and conformance tests NOT STARTED.
- [NX-IF-002 — Exposure Snapshot & Risk Reservation Contract](architecture/NX-IF-002-exposure-snapshot-risk-reservation-contract.md) — WP-B proposed contract for exclusive exposure buckets, source authority, durable atomic reservations, fencing, partial-fill handoff and recovery; implementation and conformance tests NOT STARTED.
- [NX-IF-003 — Execution Event & Ledger Posting Contract](architecture/NX-IF-003-execution-event-ledger-posting-contract.md) — WP-C proposed contract for canonical fill identity, durable outbox/inbox, atomic journal posting, corrections and projection-watermark exposure handoff; implementation and conformance tests NOT STARTED.
- [NX-IF-004 — State Evidence, Freshness & Recovery Barrier Contract](architecture/NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md) — WP-D proposed contract for source evidence vectors, freshness policies, recovery cases/quarantine and scoped restart/reconciliation barriers; implementation and conformance tests NOT STARTED.
- [NX-IF-005 — Emergency Operations, Halt & Risk-Reduction Authorization Contract](architecture/NX-IF-005-emergency-operations-halt-risk-reduction-contract.md) — WP-E proposed contract for monotonic halt epochs, command-class authorization, bounded emergency plans, protective-order handling and controlled resume; implementation and conformance tests NOT STARTED.
- [NX-OWNER-DECISIONS-001 — Critical Owner Decision Register](architecture/NX-OWNER-DECISIONS-001-critical-owner-decision-register.md) — OD-01 and OD-04 accepted under owner delegation; OD-15 partially accepted from prior product decisions; remaining OD items open/deferred by G0–G3.
- [NX-ADR-002 — Execution Integrity & Reconciliation](architecture/NX-ADR-002-execution-integrity-reconciliation.md)
- [NX-ADR-003 — Simulation Fidelity & Strategy Validation](architecture/NX-ADR-003-simulation-fidelity-strategy-validation.md)
- [NX-ADR-004 — Market Data Recovery State Machine](architecture/NX-ADR-004-market-data-recovery-state-machine.md)
- [NX-ADR-005 — Instrument Specification & Exact Arithmetic](architecture/NX-ADR-005-instrument-specification-exact-arithmetic.md)
- [ТЗ-NX-001 — Market Data Infrastructure](specifications/TZ-NX-001-market-data-infrastructure.md)
- [ТЗ-NX-002 — Professional Order Flow](specifications/TZ-NX-002-professional-order-flow.md) — функциональные требования и критерии корректности; implementation NOT STARTED
- [ТЗ-NX-003 — Quant & Strategy Engine](specifications/TZ-NX-003-quant-strategy-engine.md) — strategy artifacts, DecisionContext/TradeIntent, research governance, simulation fidelity and promotion gates; implementation NOT STARTED
- [ТЗ-NX-004 — Autonomous Execution Engine](specifications/TZ-NX-004-autonomous-execution-engine.md) — durable command/outbox, order lifecycle, ambiguity handling, private events, reconciliation, kill switch and credential isolation; implementation NOT STARTED
- [ТЗ-NX-005 — Independent Risk Engine](specifications/TZ-NX-005-independent-risk-engine.md) — deterministic pre-trade authorization, exposure and limit evaluation, reservations, signed approvals, continuous monitoring and halt controls; implementation NOT STARTED
- [ТЗ-NX-006 — Portfolio & Financial Ledger](specifications/TZ-NX-006-portfolio-financial-ledger.md) — immutable journal, exact accounting, positions, balances, P&L, fees/funding, reconciliation, snapshots and deterministic replay; implementation NOT STARTED
- [NX-SEC-001 — Threat Model & Credential Isolation](security/NX-SEC-001-threat-model-credential-isolation.md)

Эти документы сохранены и повторно прочитаны из GitHub; они не утверждены владельцем и не являются реализацией.

## Новые наблюдения по Tradoor (NX-RESEARCH-002)

- Исходный market-data source pass закреплён за Tradoor SHA `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`; funding/private-execution follow-up выполнен на HEAD `6ab38775f8f95a2b0237d8663a15405fa00465c6`. Это разные ревизии и разные scopes.
- Основной chart/trade market-data path идёт напрямую в браузер; Order Flow DOM/Tape hub принадлежит странице. Это не готовый автономный ingestion backend.
- В browser BookSync sequence continuity реально проверяется для Binance, OKX и Deribit; у ряда остальных incremental adapters sequence не передаётся в общий контракт.
- Server trade parser имеет отдельные event-time/coverage расхождения для Kraken Spot, Coinbase Spot и Lighter; browser parser в этих местах отличается. Детали и пути — в NX-RESEARCH-002.
- Open Interest recorder существует для восьми venue/market families, polling 15s, minute storage; arithmetic использует f64.
- Общая Tradoor Product-модель не содержит authoritative lot step/minQty/minNotional/contract multiplier/settlement/margin rules; Binance parser извлекает tick decimals, но не переносит LOT_SIZE в общий каталог. Contract-size conversion в Order Flow выборочная и имеет fallback 1.0. Не использовать для live order validation.
- Поправка по Hyperliquid: `6 - szDecimals` корректно отражает один из лимитов максимальных десятичных знаков цены perpetual по официальной документации; это не подтверждённый дефект. Но `Product.price_decimals` не описывает также ограничение в 5 значащих цифр и независимый size step. См. NX-RESEARCH-002.
- Подготовлены NX-ADR-001, NX-ADR-002, NX-ADR-003, NX-ADR-004, NX-ADR-005 и NX-SEC-001 со статусом PROPOSED; все требуют owner review и не являются принятыми решениями.
- Server liquidation collector охватывает 11 perpetual venues, с 24h retention.
- По четырём приоритетным venue APIs подтверждены публичные funding capabilities; исторические/interval semantics для OKX и Hyperliquid остаются частично UNKNOWN. В Tradoor funding collector и private authenticated execution в проверенных путях NOT OBSERVED; это не доказывает отсутствие кода во всех ветках.

## Ранее установленные наблюдения

- В crates/render/src/footprint.rs реализованы варианты Footprint, POC/Value Area и imbalance-related расчёты; независимая проверка формул требуется.
- В bins/server/src/training.rs paper execution-модель использует упрощённые fills; в рассмотренном коде финансовые значения используют f64.
- crates/venues содержит public market-data adapters; private authenticated order execution для каждой биржи не доказан.
- В рассмотренных частях limits.rs ограничения in-memory и не координируются между replicas.
- Лицензия Tradoor заявлена как AGPL-3.0-only; юридический анализ обязателен.

Это контрольная точка, а не отчёт о полном аудите. Выводы связывать с точным commit SHA, путями/строками, датой и методом. Непроверенное помечать UNKNOWN, а не PASS.


## Foundation documentation review and first conformance slice (2026-11-14)

- NX-DOC-REVIEW-001 added as a bounded close-out review. Documentation baseline remains NOT FROZEN; G0D is BLOCKED.
- Corrected the stale NX-ARCH-001 statement: NX-ADR-001 exists as PROPOSED and still requires owner review/conformance evidence.
- PR #1–#9 remain open Draft PRs and unmerged at this status snapshot. PR #8 and #9 are sibling branches; #9 does not include #8.
- Repository branch `docs/personal-product-profile` contains documentation only; no NEXUS root source workspace/build system was found. This is consistent with the current discovery phase.
- NX-ARCH-003 defines the first exact-decimal conformance slice without prematurely selecting production language, bounds or rounding policy.
- Added a dependency-free Python exact-decimal reference oracle and language-neutral golden vectors v1.0.0 (15 vectors). Local verification: `python -m unittest -v`, 10 tests passed against the checked-in reference-model content. This is reference-model evidence only, not production runtime or Rust/WASM verification.
- Prototype Readiness remains BLOCKED. No exchange account connection, credentials, orders, live trading, production deployment or risk-limit changes occurred.


## Reference-platform fit assessment (2026-11-14)

- NX-RESEARCH-006 added as an evidence-backed first fit assessment. NautilusTrader is a leading candidate for selected runtime reuse, not a selected full-stack foundation.
- Documented gaps against NEXUS: asynchronous cache persistence does not establish durable-before-dispatch; the built-in RiskEngine is not the independent NEXUS authorization boundary; bounded 128-bit/16-decimal and 64-bit/9-decimal modes (plus optional 18-decimal DeFi precision) require feature/domain-fit proof; v2 transition adds API migration risk; scoped deduplication/reconciliation do not replace the NEXUS ledger and recovery contracts.
- Recommended next work is a bounded source audit and conformance spike. No dependency, fork, live adapter or production integration is approved.
- The 10-test result applies to the exact reference-model files fetched from GitHub and executed in an isolated local directory. PR #10 HEAD returned no GitHub Actions workflow runs; no CI PASS is claimed.
