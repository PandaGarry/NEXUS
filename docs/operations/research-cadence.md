# Research & Review Cadence

**ID:** NX-OPS-001  
**Статус:** Proposed  
**Дата:** 2026-11-14

## Ритм
- Каждый рабочий сеанс: синхронизация с GitHub, проверка статуса, связанных ADR, backlog и открытых PR.
- Ежедневный pulse: новые upstream commits/releases, биржевые API changes, security advisories и breaking changes по приоритетным источникам.
- Еженедельный deep review: architecture, risks, roadmap, gates, evidence и устаревшие решения.
- Событийный review: немедленная проверка критических security/API/licensing изменений.

## Источники первого приоритета
1. Репозитории и releases: Tradoor, ATAS Indicators, NautilusTrader, Hummingbot, Cryptofeed, CCXT.
2. Execution/simulation: HFTBacktest, QuantConnect LEAN, ABIDES.
3. Официальные API docs/status/changelogs используемых криптобирж.
4. Официальные security advisories и dependency databases.
5. Исследования и инженерные обсуждения — как дополнительные сигналы, не как единственное доказательство.

## Фильтр сигнала
Сохранять находку, если она меняет архитектурное решение, risk register, compatibility, security, acceptance criteria, performance target или roadmap. Иначе кратко отмечать как reviewed/no material change без создания лишней документации.

## Выход каждого цикла
- новые подтверждённые изменения;
- влияние на NEXUS;
- затронутые ADR/specs/tasks;
- рекомендуемое действие;
- evidence и дата следующей проверки.

## Ограничения
Мониторинг не равен непрерывному наблюдению в реальном времени. Если scheduled automation или рабочий запуск не состоялся, нельзя утверждать, что проверка проведена. Upstream change не считается автоматически принятым решением NEXUS.
