# Дорожная карта

Статусы меняются только при наличии проверяемых свидетельств.

## Phase 0 — Foundation Audit (In Progress)
- [ ] Зафиксировать baseline commit и структуру Tradoor.
- [ ] Завершить аудит exchange adapters и capabilities matrix. (Initial Tradoor source pass recorded in NX-RESEARCH-002; private/funding and full instrument rules remain UNKNOWN.)
- [ ] Проверить ingestion, recorder, backfill, migrations и persistence.
- [ ] Проверить тесты, CI, dependency tree и лицензии.
- [x] Подготовить initial threat model (NX-SEC-001, PROPOSED).
- [ ] Провести deployment-specific review и security verification.
- [ ] Сравнить HFTBacktest, LEAN и ABIDES по fidelity, replay, latency и queue modeling.
- [ ] Сопоставить Order Flow формулы с поведенческими эталонами.
- [ ] Зафиксировать дефекты, неизвестные свойства и ограничения.

## Phase 1 — Core Architecture (Blocked)
- [ ] Утвердить NX-ADR-001 Unified Market Event Contract. (Draft published; owner review and schema conformance design review required.)
- [ ] Утвердить NX-ADR-002 Execution Integrity & Reconciliation. (ADR drafted; owner review required.)
- [ ] Утвердить NX-ADR-003 Simulation Fidelity & Strategy Validation. (ADR drafted; owner review required.)
- [ ] Утвердить NX-ADR-004 Market Data Recovery State Machine.
- [ ] Утвердить NX-ADR-005 Instrument Specification & Exact Arithmetic.
- [ ] Утвердить NX-ARCH-001 целевую архитектуру и deployment topology. (Draft published; owner review required.)
- [ ] Определить transactional boundaries, durable outbox, event log и recovery.

## Phase 2 — Professional Analytics (Blocked)
- [ ] Утвердить ТЗ-NX-002 Professional Order Flow. (Draft published; formula decisions and owner review required.)\n- [ ] Подготовить независимые golden datasets и тесты для Footprint, Delta/CVD, DOM, Tape, Profiles.
- [ ] Независимая проверка данных и нормализации.
- [ ] UI/UX benchmark и производительные сценарии.

## Phase 3 — Quant & Simulation (Blocked)
- [ ] Утвердить NX-ADR-003 и NX-ADR-006.
- [ ] Определить execution simulation levels L1/L2/L3.
- [ ] Утвердить out-of-sample и walk-forward protocols.
- [ ] Проверить latency, queue position, partial fills, slippage и adverse selection.

## Phase 4 — Risk & Execution (Blocked)
- [ ] Утвердить NX-ADR-002 Execution Integrity & Reconciliation.
- [ ] Утвердить независимый Risk Engine и NX-SEC-001 threat model.
- [ ] Проверить kill switch, limits, secrets, audit и disaster recovery.
- [ ] Допускать read-only/paper только после прохождения архитектурных gates.

## Phase 5 — Autonomous Intelligence (Blocked)
- [ ] Определить права и ограничения AI Orchestrator.
- [ ] Проверить policy enforcement и полный audit trail.
- [ ] Исключить прямой обход AI компонента Risk Engine.

## Phase 6 — Desktop + Web Production (Blocked)
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
7. **Architecture synthesis:** NX-ARCH-001, service boundaries, deployment, persistence, observability и final readiness review.

Каждый work package имеет ограниченный scope и exit criteria. Новые интересные направления помещаются в backlog, но не блокируют текущий этап, если не затрагивают безопасность, финансовую корректность или выбранную архитектуру.

### Обязательный выход Phase 0
- утверждаемые NX-ADR-001..006 и NX-SEC-001;
- NX-ARCH-001;
- шесть ТЗ с контрактами и acceptance criteria;
- exchange capabilities matrix;
- risk register и dependency/license inventory;
- test/evidence matrix;
- implementation sequence и estimate ranges;
- финальный readiness report с PASS/BLOCKED и ссылками на evidence.

Только после owner review и прохождения всех критических gates разрешается начать безопасный read-only/paper prototype. Live trading требует отдельного допуска.
