# Дорожная карта

Статусы меняются только при наличии проверяемых свидетельств.

## Phase 0 — Foundation Audit (In Progress)

**Operational checklist:** [NX-PROJECT-CHECKLIST-001](quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md). It is the current source for D1–D8 package status and ordered engineering work.

### Foundation close-out track (active)
- [ ] Complete NX-DOC-REVIEW-001 packages D1–D8 or explicitly defer each behind a named gate.
- [x] Add test-only egress authority handover state-machine model; actual network/host fencing remains BLOCKED.
- [x] Add exact-decimal reference oracle and unit tests (11/11; reference-only evidence).
- [x] Publish language-neutral golden vectors v1.0.0 (15 cases); Python oracle passes all vectors.
- [x] Add deterministic exact-arithmetic property checks: 1,000 seeded cases cross-checked against independent `fractions.Fraction` arithmetic.
- [ ] Add broader fuzz coverage and cross-language conformance.
- [ ] Approve production numeric bounds, overflow behavior, typed units and rounding ownership before financial runtime implementation.
- [ ] Establish implementation workspace, pinned toolchain, dependency policy and reproducible CI before production-language kernel work.
- [ ] Зафиксировать baseline commit и структуру Tradoor.
- [ ] Завершить аудит exchange adapters и capabilities matrix. (Initial Tradoor source pass recorded in NX-RESEARCH-002; private/funding and full instrument rules remain UNKNOWN.)
- [ ] Проверить ingestion, recorder, backfill, migrations и persistence.
- [ ] Проверить тесты, CI, dependency tree и лицензии.
- [x] Подготовить initial threat model (NX-SEC-001, PROPOSED).
- [ ] Провести deployment-specific review и security verification.
- [ ] Сравнить HFTBacktest, LEAN и ABIDES по fidelity, replay, latency и queue modeling.
- [ ] Сопоставить Order Flow формулы с поведенческими эталонами.
- [ ] Зафиксировать дефекты, неизвестные свойства и ограничения.

- [x] Prepare bounded first-venue candidate review (NX-RESEARCH-003): Coinbase and Kraken remain conditional candidates; no selection until jurisdiction/product eligibility and exact API capability are verified.

## Phase 1 — Core Architecture (Blocked)

- [x] Define proposed personal-first product/deployment profile model (NX-ARCH-002): single-owner closed personal use first; future commercial operation requires a separate legal/security/product review. Owner approval and runtime enforcement remain open.

- [x] Publish bounded WP-A..WP-E interface design drafts (NX-IF-001..005).
- [x] Consolidate critical owner decisions and readiness dependencies in NX-OWNER-DECISIONS-001.
- [x] Accept bounded v1 scope: one venue + dedicated account/subaccount; account/subaccount risk boundary; server-side autonomous runtime; shared Desktop+Web backend (OD-01/04/15, owner-directed 2026-11-14).
- [ ] Select first venue and product/account mode after confirming legal/account eligibility and completing official capability review (OD-02/03).
- [ ] Obtain remaining G0 owner decisions before freezing the architecture baseline.
- [ ] Obtain G1/G2 decisions and conformance evidence before read-only/paper and sandbox/shadow gates respectively.
- [ ] Obtain all G3 risk/security/emergency approvals before any limited-live consideration.
- [ ] Утвердить NX-ADR-001 Unified Market Event Contract. (Draft published; owner review and schema conformance design review required.)
- [ ] Утвердить NX-ADR-002 Execution Integrity & Reconciliation. (ADR drafted; owner review required.)
- [ ] Утвердить NX-ADR-003 Simulation Fidelity & Strategy Validation. (ADR drafted; owner review required.)
- [ ] Утвердить NX-ADR-004 Market Data Recovery State Machine.
- [ ] Утвердить NX-ADR-005 Instrument Specification & Exact Arithmetic.
- [ ] Утвердить NX-ARCH-001 целевую архитектуру и deployment topology. (Draft published; owner review required.)
- [ ] Закрыть NX-ARCH-REVIEW-001 WP-A..WP-E: canonical command/approval, exposure/reservations, Execution↔Ledger handoff, freshness/recovery, emergency operations. WP-A..WP-E design drafts now exist; acceptance and owner review remain open.
  - [x] WP-A design draft: NX-IF-001 published and readback verified.
  - [ ] WP-A acceptance: owner/security decisions, canonicalization/digest selection, cross-language golden vectors and conformance tests.
  - [x] WP-B design draft: NX-IF-002 published; exclusive buckets, reservation lifecycle, atomic concurrency and failure matrix specified.
  - [ ] WP-B acceptance: owner decisions, persistence/transaction design, schema conformance, concurrency and fault-injection evidence.
  - [x] WP-C design draft: NX-IF-003 published; execution ownership, canonical fill identity, durable outbox/inbox, atomic Ledger posting, corrections and projection watermark handoff specified.
  - [ ] WP-C acceptance: owner accounting decisions, transaction/store selection, schema conformance, golden accounting fixtures, replay and fault-injection evidence.
  - [x] WP-D design draft: NX-IF-004 published; StateEvidenceVector, source-specific freshness/quality, quarantine, RecoveryCase and scoped RecoveryBarrier/restart ordering specified.
  - [ ] WP-D acceptance: owner freshness thresholds and venue/account scope, durable persistence and operator policy decisions, schema conformance, restart/replay/reconciliation and fault-injection evidence.
  - [x] WP-E design draft: NX-IF-005 published; monotonic scoped HaltState, command-class authorization, protective-order semantics, bounded emergency plans, operator governance and controlled resume specified.
  - [ ] WP-E acceptance: owner role/dual-control/emergency-policy decisions, venue/account-mode capability certification, halt propagation, race, fault-injection and adapter conformance evidence.
- [ ] Определить transactional boundaries, durable outbox, event log и recovery.
- [ ] Согласовать EvidenceRequirementSet/FreshnessPolicy thresholds и recovery objectives с владельцем до любой реализации.
- [ ] Выполнить end-to-end contract review и зафиксировать owner decisions до выбора реализации. Consolidated register: NX-OWNER-DECISIONS-001 (OD-01..OD-15).

## Phase 2 — Professional Analytics (Blocked)
- [ ] Утвердить ТЗ-NX-002 Professional Order Flow. (Draft published; formula decisions and owner review required.)
- [ ] Подготовить независимые golden datasets и тесты для Footprint, Delta/CVD, DOM, Tape, Profiles.
- [ ] Независимая проверка данных и нормализации.
- [ ] UI/UX benchmark и производительные сценарии.

## Phase 3 — Quant & Simulation (Blocked)
- [ ] Утвердить ТЗ-NX-003 Quant & Strategy Engine. (Draft published; owner review and strategy-runtime decisions required.)
- [x] Publish NX-ADR-003 simulation and strategy-validation protocol (PROPOSED; owner review remains open).
- [ ] NX-ADR-006 explicitly deferred: NX-ADR-003 already covers the current strategy-validation governance scope; reopen only if a distinct architectural decision is identified.
- [ ] Определить execution simulation levels L1/L2/L3.
- [ ] Утвердить out-of-sample, purge/embargo и walk-forward protocols.
- [ ] Проверить latency, queue position, partial fills, slippage и adverse selection.

## Phase 4 — Risk & Execution (Blocked)
- [ ] Утвердить ТЗ-NX-004 Autonomous Execution Engine. (Draft published; venue shortlist, kill-switch playbook and persistence decisions require owner review.)
- [ ] Утвердить ТЗ-NX-005 Independent Risk Engine. (Draft published; owner limits, policy scopes, kill-switch governance and risk input contracts require owner review.)
- [ ] Утвердить NX-ADR-002 Execution Integrity & Reconciliation.
- [ ] Утвердить независимый Risk Engine и NX-SEC-001 threat model.
- [ ] Проверить kill switch, limits, secrets, audit и disaster recovery.
- [ ] Допускать read-only/paper только после прохождения архитектурных gates.

## Phase 5 — Portfolio & Accounting (Blocked)
- [ ] Утвердить ТЗ-NX-006 Portfolio & Financial Ledger. (Draft published; chart of accounts, posting rules, P&L boundaries, FX/valuation policy and retention require owner review.)
- [ ] Зафиксировать immutable journal, event identity, correction/bust and idempotency semantics.
- [ ] Подготовить golden accounting fixtures для spot, linear, inverse и quanto.
- [ ] Проверить fees, funding, settlement, transfers, reconciliation и deterministic replay.
- [ ] Согласовать Ledger read models and freshness contract с Risk Engine.

## Phase 6 — Autonomous Intelligence (Blocked)
- [ ] Определить права и ограничения AI Orchestrator.
- [ ] Проверить policy enforcement и полный audit trail.
- [ ] Исключить прямой обход AI компонента Risk Engine.

## Phase 7 — Desktop + Web Production (Blocked)
- [ ] Progress through PERSONAL_DEV → PERSONAL_TEST → PERSONAL_PRODUCTION only via explicit readiness gates; PERSONAL_PRODUCTION does not itself authorize live trading.
- [ ] Defer COMMERCIAL profile, multi-tenancy and third-party users to a separately approved business/legal/security work package.
- [ ] Выбрать desktop shell по benchmark.
- [ ] Проверить единое состояние, offline/reconnect и multi-device behavior.
- [ ] Подготовить production observability, backups и deployment runbooks.

Live trading требует отдельного формального допуска, ограниченного rollout и подтверждённой эксплуатационной готовности.

## Правило завершения Foundation Audit (anti-infinite-audit)

Phase 0 не означает исследовать все существующие проекты и все возможные функции. Аудит закрывается по фиксированным work packages, когда для каждого критического контура:
- известны применимые требования NEXUS;
- проверены выбранные исходники/документы/тесты по заранее определённому scope;
- зафиксированы capabilities и UNKNOWN;
- оценены критические риски и mitigation;
- принято решение: reuse / adapt / replace / build / defer;
- созданы ADR/spec и acceptance criteria;
- отсутствуют открытые вопросы, способные изменить фундаментальную архитектуру, либо они явно вынесены в owner decision.

### Очерёдность закрытия Phase 0
1. **Market data & exchange adapters:** capabilities matrix по приоритетным биржам и критическим потокам; отдельный список неподдержанных/неподтверждённых возможностей.
2. **Execution & recovery:** lifecycle, idempotency, unknown outcome, reconciliation, restart recovery и failure modes.
3. **Financial correctness:** instrument specs, exact arithmetic, fees, funding, margin и ledger invariants.
4. **Simulation & research:** сопоставление HFTBacktest/LEAN/ABIDES; выбрать минимально достаточную модель симуляции и зафиксировать limitations.
5. **Security & supply chain:** threat model, credentials, auth, dependencies, licenses, CI and backup/recovery.
6. **Analytics correctness:** формулы, aggregation semantics, golden datasets и independent checks для ключевых Order Flow функций.
7. **Architecture synthesis:** NX-ARCH-001, NX-ARCH-REVIEW-001, service boundaries, deployment, persistence, observability и final readiness review.

Каждый work package имеет ограниченный scope и exit criteria. Новые интересные направления помещаются в backlog, но не блокируют текущий этап, если не затрагивают безопасность, финансовую корректность или выбранную архитектуру.

### Обязательный выход Phase 0
- утверждаемые NX-ADR-001..006 и NX-SEC-001;
- NX-ARCH-001 и NX-ARCH-REVIEW-001;
- шесть ТЗ с контрактами и acceptance criteria;
- exchange capabilities matrix;
- risk register и dependency/license inventory;
- test/evidence matrix;
- implementation sequence и estimate ranges;
- финальный readiness report с PASS/BLOCKED и ссылками на evidence.

Только после owner review и прохождения всех критических gates разрешается начать безопасный read-only/paper prototype. Live trading требует отдельного допуска.

- Domain kernel: explicit, version-pinned instrument quantity-unit semantics (NX-REF-DOMAIN-004) added as test-only reference; venue mappings and derivative risk/P&L formulas remain future qualification work.

- Domain kernel: exact rational division and explicit quantization reference (NX-REF-DOMAIN-005) added; financial-operation-specific rounding policies remain a separate decision.

- Inverse contracts: exact rational base exposure reference added; venue-specific contract semantics, P&L, margin and rounding policy remain open.

- Domain kernel: NX-REF-DOMAIN-007 adds a test-only bounded numeric context with mandatory caller-supplied budgets; production limits remain unselected.
- Domain kernel: NX-REF-DOMAIN-008 adds canonical scalar decimal/rational wire formats; cross-language and typed event/command integration remain open.

### Financial-operation correctness increment

- [x] Publish NX-REF-DOMAIN-009 proposed operation-specific rounding and valuation contract; define universal exactness invariants, policy boundaries, provenance and venue qualification dossier.
- [ ] Cross-review financial-operation contract against NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006.
- [ ] Obtain owner decisions for position matching, fee/funding accounting, FX/collateral valuation and journal rounding.
- [ ] Qualify exact venue/product/account and capture authoritative fee, funding, margin, liquidation and price-source fixtures.
- [ ] Add independent mathematical golden fixtures only after each formula's universality or venue-specific authority is established.

No production financial calculator or execution/risk/ledger implementation is authorized by this documentation increment.

### Venue-neutral financial math fixtures

- [x] Publish NX-REF-DOMAIN-010 and language-neutral exact vectors for explicitly dimensioned spot, linear, inverse and partial-fill arithmetic.
- [x] Add independent rational-oracle checks and negative dimension/identity tests.
- [x] Add the fixture suite to Python 3.11–3.13 CI.
- [ ] Verify exact PR-head CI; then freeze this bounded fixture package.
- [ ] Keep fee/funding/P&L/margin/liquidation/FX/accounting fixtures blocked until authoritative venue/account or owner policies exist.

This package validates mathematical identities only; it does not pass financial readiness gates.
