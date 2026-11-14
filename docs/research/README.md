# Исследования и аудит

Каждый аудит должен содержать дату, точный repository URL, commit SHA/tag, проверенные пути и диапазоны строк, метод проверки, выводы, ограничения и confidence. README и marketing claims не являются доказательством runtime behavior.

## Исследуемые проекты
- Tradoor — возможная база графиков/визуализации и отдельных analytics компонентов.
- ATAS Indicators — behavioral benchmark для Order Flow.
- NautilusTrader — паттерны Data/Risk/Execution/Portfolio и reconciliation.
- Hummingbot — connector lifecycle, Decimal, rate limiting и user streams.
- Cryptofeed — нормализация и raw stream capture.
- CCXT — широта биржевых API.
- Freqtrade / Jesse / VectorBT — research и backtesting patterns.
- TradingView Lightweight Charts — charting benchmark.
- HFTBacktest / QuantConnect LEAN / ABIDES — simulation и research systems; требуется углублённый аудит.

## Evidence labels
- CONFIRMED — непосредственно подтверждено исходником или тестом.
- OBSERVED — обнаружено в просмотренной части, область проверки ограничена.
- CLAIMED — заявлено документацией, но независимо не подтверждено.
- UNKNOWN — доказательств недостаточно.
- NOT TESTED — runtime/CI/test не запускался в этой проверке.
