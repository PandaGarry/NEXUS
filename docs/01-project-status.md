# Текущий статус проекта

**Дата среза:** 2026-11-14  
**Общий статус:** BLOCKED — Prototype Readiness Gate не пройден  
**Текущая фаза:** Phase 0 — Foundation Audit

| Область | Статус | Комментарий |
|---|---|---|
| Цель и продуктовые границы | Accepted | Зафиксированы в Project Charter |
| Архитектурные принципы | Proposed / Partially accepted | Требуются финальные ADR |
| Tradoor audit | In Progress | Исходники изучены выборочно; аудит не завершён |
| Exchange capabilities matrix | Incomplete | Проверить каждый адаптер и канал |
| Simulation fidelity | In Progress | Tradoor paper-модель недостаточна для реалистичного исполнения |
| Runtime verification | Not performed | CI/runtime тесты не считать пройденными |
| Security threat model | Not started | Блокер |
| Exact arithmetic / instrument specs | Not started | Блокер |
| Prototype readiness | BLOCKED | Не начинать прототипирование |

## Наблюдения по Tradoor
- Rust/WASM/WebGL2/SolidJS архитектура с отдельными crates для core, render, venues, store, ingest и server.
- В crates/render/src/footprint.rs реализованы варианты Footprint, POC/Value Area и imbalance-related расчёты; независимая проверка формул требуется.
- В web/src/lib/orderflow.ts часть DOM/Tape и book sync логики находится на browser side; автономная торговля не должна зависеть от вкладки.
- В bins/server/src/training.rs paper execution-модель использует упрощённые fills; в рассмотренном коде финансовые значения используют f64.
- crates/venues содержит public market-data adapters; private authenticated order execution для каждой биржи не доказан.
- В рассмотренных частях limits.rs ограничения in-memory и не координируются между replicas.
- Лицензия Tradoor заявлена как AGPL-3.0-only; юридический анализ обязателен.

Это контрольная точка, а не отчёт о полном аудите. Выводы связывать с точным commit SHA, путями/строками, датой и методом. Непроверенное помечать UNKNOWN, а не PASS.
