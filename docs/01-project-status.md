# Текущий статус проекта

**Дата среза:** 2026-11-14  
**Общий статус:** BLOCKED — Prototype Readiness Gate не пройден  
**Текущая фаза:** Phase 0 — Foundation Audit

| Область | Статус | Комментарий |
|---|---|---|
| Цель и продуктовые границы | Accepted | Зафиксированы в Project Charter |
| Архитектурные принципы | Proposed / Partially accepted | Требуются финальные ADR |
| Tradoor audit | In Progress | Source pass обновлён до HEAD 6ab3877; funding/private execution capability audit добавлен в NX-RESEARCH-002. Полная per-venue сертификация, instrument metadata и runtime verification остаются открыты |
| Exchange capabilities matrix | Incomplete | Trade/book/OI/liquidation первично просмотрены; per-channel matrix и UNKNOWN поля ещё не закрыты |
| Simulation fidelity | In Progress | Tradoor paper-модель недостаточна для реалистичного исполнения |
| Runtime verification | Not performed | CI/runtime тесты не считать пройденными |
| Security threat model | Not started | Блокер |
| Exact arithmetic / instrument specs | ADR proposed / implementation not started | NX-ADR-005 drafted; требует owner review и последующих golden tests. Блокер реализации сохраняется |
| Prototype readiness | BLOCKED | Не начинать прототипирование |

## Новые архитектурные артефакты (PROPOSED)

- [NX-ADR-002 — Execution Integrity & Reconciliation](architecture/NX-ADR-002-execution-integrity-reconciliation.md)\n- [NX-ADR-003 — Simulation Fidelity & Strategy Validation](architecture/NX-ADR-003-simulation-fidelity-strategy-validation.md)\n- [NX-ADR-004 — Market Data Recovery State Machine](architecture/NX-ADR-004-market-data-recovery-state-machine.md)
- [NX-ADR-005 — Instrument Specification & Exact Arithmetic](architecture/NX-ADR-005-instrument-specification-exact-arithmetic.md)
- [ТЗ-NX-001 — Market Data Infrastructure](specifications/TZ-NX-001-market-data-infrastructure.md)

Эти документы сохранены и повторно прочитаны из GitHub; они не утверждены владельцем и не являются реализацией.

## Новые наблюдения по Tradoor (NX-RESEARCH-002)

- Аудит закреплён за Tradoor SHA `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`; последний проверенный commit был преимущественно переименованием Frost Script, без изменения просмотренных market-data файлов.
- Основной chart/trade market-data path идёт напрямую в браузер; Order Flow DOM/Tape hub принадлежит странице. Это не готовый автономный ingestion backend.
- В browser BookSync sequence continuity реально проверяется для Binance, OKX и Deribit; у ряда остальных incremental adapters sequence не передаётся в общий контракт.
- Server trade parser имеет отдельные event-time/coverage расхождения для Kraken Spot, Coinbase Spot и Lighter; browser parser в этих местах отличается. Детали и пути — в NX-RESEARCH-002.
- Open Interest recorder существует для восьми venue/market families, polling 15s, minute storage; arithmetic использует f64.
- Общая Tradoor Product-модель не содержит authoritative lot step/minQty/minNotional/contract multiplier/settlement/margin rules; Binance parser извлекает tick decimals, но не переносит LOT_SIZE в общий каталог. Contract-size conversion в Order Flow выборочная и имеет fallback 1.0. Не использовать для live order validation.
- Поправка по Hyperliquid: `6 - szDecimals` корректно отражает один из лимитов максимальных десятичных знаков цены perpetual по официальной документации; это не подтверждённый дефект. Но `Product.price_decimals` не описывает также ограничение в 5 значащих цифр и независимый size step. См. NX-RESEARCH-002.
- Подготовлены NX-ADR-004 и NX-ADR-005 со статусом PROPOSED; они требуют owner review и не являются принятыми решениями.
- Server liquidation collector охватывает 11 perpetual venues, с 24h retention.
- По четырём приоритетным venue APIs подтверждены публичные funding capabilities; исторические/interval semantics для OKX и Hyperliquid остаются частично UNKNOWN. В Tradoor funding collector и private authenticated execution в проверенных путях NOT OBSERVED; это не доказывает отсутствие кода во всех ветках.

## Ранее установленные наблюдения

- В crates/render/src/footprint.rs реализованы варианты Footprint, POC/Value Area и imbalance-related расчёты; независимая проверка формул требуется.
- В bins/server/src/training.rs paper execution-модель использует упрощённые fills; в рассмотренном коде финансовые значения используют f64.
- crates/venues содержит public market-data adapters; private authenticated order execution для каждой биржи не доказан.
- В рассмотренных частях limits.rs ограничения in-memory и не координируются между replicas.
- Лицензия Tradoor заявлена как AGPL-3.0-only; юридический анализ обязателен.

Это контрольная точка, а не отчёт о полном аудите. Выводы связывать с точным commit SHA, путями/строками, датой и методом. Непроверенное помечать UNKNOWN, а не PASS.


## Следующие архитектурные артефакты (PROPOSED)

- [NX-ADR-002 — Execution Integrity & Reconciliation](architecture/NX-ADR-002-execution-integrity-reconciliation.md): durable outbox, immutable command identity, asynchronous order lifecycle, unknown outcomes, fill deduplication and reconciliation.
- [NX-ADR-003 — Simulation Fidelity & Strategy Validation](architecture/NX-ADR-003-simulation-fidelity-strategy-validation.md): explicit simulation modes/fidelity levels, execution assumptions, cost/funding model and leakage-resistant validation.

Оба ADR сохранены в рабочей ветке и требуют owner review. Они не являются реализацией. NX-RESEARCH-002 дополнен bounded funding/private-execution audit на Tradoor HEAD `6ab3877`; официальные API capabilities отделены от Tradoor application integration. No private execution implementation, live account test or runtime certification is claimed.
