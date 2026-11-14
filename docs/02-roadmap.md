# Дорожная карта

Статусы меняются только при наличии проверяемых свидетельств.

## Phase 0 — Foundation Audit (In Progress)
- [ ] Зафиксировать baseline commit и структуру Tradoor.
- [ ] Завершить аудит exchange adapters и capabilities matrix.
- [ ] Проверить ingestion, recorder, backfill, migrations и persistence.
- [ ] Проверить тесты, CI, dependency tree и лицензии.
- [ ] Проверить auth/session/security и построить threat model.
- [ ] Сравнить HFTBacktest, LEAN и ABIDES по fidelity, replay, latency и queue modeling.
- [ ] Сопоставить Order Flow формулы с поведенческими эталонами.
- [ ] Зафиксировать дефекты, неизвестные свойства и ограничения.

## Phase 1 — Core Architecture (Blocked)
- [ ] Утвердить NX-ADR-001 Unified Market Event Contract.
- [ ] Утвердить NX-ADR-004 Market Data Recovery State Machine.
- [ ] Утвердить NX-ADR-005 Instrument Specification & Exact Arithmetic.
- [ ] Утвердить NX-ARCH-001 целевую архитектуру и deployment topology.
- [ ] Определить transactional boundaries, durable outbox, event log и recovery.

## Phase 2 — Professional Analytics (Blocked)
- [ ] Спецификации и golden tests для Footprint, Delta/CVD, DOM, Tape, Profiles.
- [ ] Независимая проверка данных и нормализации.
- [ ] UI/UX benchmark и производительные сценарии.

## Phase 3 — Quant & Simulation (Blocked)
- [ ] Утвердить NX-ADR-003 и NX-ADR-006.
- [ ] Определить execution simulation levels L1/L2/L3.
- [ ] Утвердить out-of-sample и walk-forward protocols.
- [ ] Проверить latency, queue position, partial fills, slippage и adverse selection.

## Phase 4 — Risk & Execution (Blocked)
- [ ] Утвердить execution lifecycle и reconciliation.
- [ ] Утвердить независимый Risk Engine и threat model.
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
