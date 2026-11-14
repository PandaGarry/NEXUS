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

## Research records
- [NX-RESEARCH-001 — Simulation systems landscape](NX-RESEARCH-001-simulation-landscape.md)
- [NX-RESEARCH-002 — Tradoor market-data adapter audit](NX-RESEARCH-002-market-data-adapter-audit.md)
- [NX-RESEARCH-003 — First-Venue Shortlist](NX-RESEARCH-003-first-venue-shortlist.md) — Coinbase/Kraken conditional comparison; no venue selected.
- [NX-RESEARCH-006 — Reference Platform Fit Assessment](NX-RESEARCH-006-reference-platform-fit-assessment.md) — NautilusTrader leading candidate, not selected; targeted source review only.
- [NX-RESEARCH-007 — NautilusTrader v2 Release Baseline Review](NX-RESEARCH-007-nautilus-v2-release-baseline.md) — v2.0.0rc9 is test-only; stable v2 and exact-source re-audit required.
- [NX-RESEARCH-008 — NautilusTrader RC9 Execution Boundary Audit](NX-RESEARCH-008-nautilus-rc9-execution-boundary-audit.md) — exact RC9 source confirms persistence-before-dispatch and non-bypassable Risk boundary gaps; no execution-core adoption.

## Evidence labels
- CONFIRMED — непосредственно подтверждено исходником или тестом.
- OBSERVED — обнаружено в просмотренной части, область проверки ограничена.
- CLAIMED — заявлено документацией, но независимо не подтверждено.
- UNKNOWN — доказательств недостаточно.
- NOT TESTED — runtime/CI/test не запускался в этой проверке.

- [NX-RESEARCH-009 — Russia Jurisdiction, Product Classification & First-Venue Eligibility](NX-RESEARCH-009-russia-jurisdiction-product-and-venue-eligibility.md) — Current 2026-11-14 baseline for Law 282-FZ, domestic regulated candidates, MOEX/SPB crypto derivatives and foreign venue eligibility; no live venue qualified.
- NX-RESEARCH-003 and NX-RESEARCH-004 remain historical research records; their venue eligibility conclusions must be read with NX-RESEARCH-009, which supersedes earlier shortlist conclusions for the owner's RF-resident scenario.

- [NX-RESEARCH-010 — Open-Source Component Qualification](NX-RESEARCH-010-open-source-component-qualification.md) — candidate shortlist for PostgreSQL, OpenTelemetry, OpenBao, NATS JetStream, Cilium and Temporal; no dependency adoption approved.

- [NX-RESEARCH-011 — CBOR / COSE Library Qualification](NX-RESEARCH-011-cbor-cose-library-qualification.md) — evaluates Rust CBOR/COSE candidates against RFC 8949 core deterministic encoding and RFC 9864 alg=-19; no library or runtime dependency approved.

- [NX-RESEARCH-012 — PostgreSQL 18.7 G1 Evaluation Qualification](NX-RESEARCH-012-postgresql-18-7-g1-evaluation-qualification.md) — selects 18.7 as the exact G1 test target and records the November 12, 2026 security/bugfix release caveats; no database or production deployment approved.

- [NX-RESEARCH-012 — PostgreSQL 18.7 G1 Evaluation Qualification](NX-RESEARCH-012-postgresql-18-7-g1-evaluation-qualification.md) — exact patch-level G1 target, release security/index/backup caveats, role and extension hardening; no database installed or production-approved.
