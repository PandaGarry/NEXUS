# Текущий статус проекта

**Дата среза:** 2026-11-14  
**Общий статус:** BLOCKED — Prototype Readiness Gate не пройден  
**Текущая фаза:** Phase 0 — Foundation Audit

| Область | Статус | Комментарий |
|---|---|---|
| Цель и продуктовые границы | Accepted | Зафиксированы в Project Charter |
| Архитектурные принципы | Proposed / Partially accepted | Требуются финальные ADR |
| Tradoor audit | In Progress | Выполнен первый bounded source pass на SHA 39a1826; остаются instrument metadata, recovery, funding и private API |
| Exchange capabilities matrix | Incomplete | Trade/book/OI/liquidation первично просмотрены; per-channel matrix и UNKNOWN поля ещё не закрыты |
| Simulation fidelity | In Progress | Tradoor paper-модель недостаточна для реалистичного исполнения |
| Runtime verification | Not performed | CI/runtime тесты не считать пройденными |
| Security threat model | Not started | Блокер |
| Exact arithmetic / instrument specs | Not started | Блокер |
| Prototype readiness | BLOCKED | Не начинать прототипирование |

## Новые наблюдения по Tradoor (NX-RESEARCH-002)

- Аудит закреплён за Tradoor SHA `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`; последний проверенный commit был преимущественно переименованием Frost Script, без изменения просмотренных market-data файлов.
- Основной chart/trade market-data path идёт напрямую в браузер; Order Flow DOM/Tape hub принадлежит странице. Это не готовый автономный ingestion backend.
- В browser BookSync sequence continuity реально проверяется для Binance, OKX и Deribit; у ряда остальных incremental adapters sequence не передаётся в общий контракт.
- Server trade parser имеет отдельные event-time/coverage расхождения для Kraken Spot, Coinbase Spot и Lighter; browser parser в этих местах отличается. Детали и пути — в NX-RESEARCH-002.
- Open Interest recorder существует для восьми venue/market families, polling 15s, minute storage; arithmetic использует f64.
- Server liquidation collector охватывает 11 perpetual venues, с 24h retention.
- Funding-rate collection и private authenticated order execution остаются UNKNOWN в рамках текущего аудита.

## Ранее установленные наблюдения

- В crates/render/src/footprint.rs реализованы варианты Footprint, POC/Value Area и imbalance-related расчёты; независимая проверка формул требуется.
- В bins/server/src/training.rs paper execution-модель использует упрощённые fills; в рассмотренном коде финансовые значения используют f64.
- crates/venues содержит public market-data adapters; private authenticated order execution для каждой биржи не доказан.
- В рассмотренных частях limits.rs ограничения in-memory и не координируются между replicas.
- Лицензия Tradoor заявлена как AGPL-3.0-only; юридический анализ обязателен.

Это контрольная точка, а не отчёт о полном аудите. Выводы связывать с точным commit SHA, путями/строками, датой и методом. Непроверенное помечать UNKNOWN, а не PASS.
