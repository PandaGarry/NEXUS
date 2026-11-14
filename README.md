# NEXUS

**NEXUS TRADING** — профессиональная персональная криптоторговая платформа: Order Flow, количественные стратегии, автономное исполнение, независимое управление риском и Desktop + Web клиенты с единым backend.

> **Текущий статус:** Foundation Audit / Architecture Discovery. Прототипирование и подключение реальных торговых ключей не разрешены до прохождения readiness gates.

## Навигация
- [Устав проекта](docs/00-project-charter.md)
- [Текущий статус](docs/01-project-status.md)
- [Дорожная карта](docs/02-roadmap.md)
- [Архитектура и ADR](docs/architecture/README.md)
- [Технические спецификации](docs/specifications/README.md)
- [Исследования и аудит](docs/research/README.md)
- [Безопасность](docs/security/README.md)
- [Prototype Readiness Gates](docs/quality/readiness-gates.md)
- [Changelog](CHANGELOG.md)
- [Шаблон объявления об обновлении](.github/RELEASE_TEMPLATE.md)

## Инварианты
1. Безопасность капитала важнее автономности и удобства.
2. AI не обходит независимый Risk Engine и не владеет неограниченными биржевыми credentials.
3. Stale, invalid или unsynchronized market data блокируют риск-увеличивающие действия.
4. Тайм-аут отправки ордера не означает отказ; неизвестный результат требует reconciliation, а не слепого повтора.
5. Финансовая точность требует exact arithmetic и явных спецификаций инструментов.
6. Backtest не доказывает будущую доходность.
7. Любое изменение требует acceptance criteria, тестов, документации и evidence.
8. Непроверенные возможности и непроведённые тесты нельзя объявлять готовыми.

## Статусы
- **Proposed** — предложение.
- **Accepted** — решение принято, реализация может быть отдельной задачей.
- **In Progress** — выполняется.
- **Verified** — проверено указанным методом и evidence.
- **Blocked** — есть блокирующее условие.
- **Deprecated** — заменено или не рекомендуется.
