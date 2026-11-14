# Changelog

Заметные изменения проекта фиксируются в обратном хронологическом порядке. Release notes пишутся понятным языком; инженерные детали остаются в ADR/PR.

## Unreleased

### Added
- NX-IF-001: proposed Canonical Trade Command & Risk Approval Contract defining TradeIntent separation, immutable command envelope, canonicalization/digest, signed scoped approval capability, one-time consumption, invalidation and negative conformance matrix; implementation and tests not started.
- NX-IF-002: proposed Exposure Snapshot & Risk Reservation Contract defining exclusive exposure buckets, source ownership, durable reservations, atomic multi-scope capacity checks, fencing, partial-fill transfer, unknown-outcome retention and recovery/conformance scenarios; implementation and tests not started.
- NX-IF-003: proposed Execution Event & Ledger Posting Contract defining canonical fill identity, durable Execution outbox/Ledger inbox, atomic balanced journal posting, fee/correction handling, replay and projection-watermark exposure handoff; implementation and tests not started.
- NX-IF-004: proposed State Evidence, Freshness & Recovery Barrier Contract defining source-specific evidence vectors, freshness policies, quarantine/recovery cases, scoped generation-fenced barriers and restart/reconciliation ordering; implementation and tests not started.
- NX-IF-005: proposed Emergency Operations, Halt & Risk-Reduction Authorization Contract defining monotonic scoped halt epochs, command-class authorization, bounded emergency plans, protective-order handling, operator governance and controlled resume; implementation and tests not started.
- NX-ARCH-REVIEW-001: proposed cross-specification review covering 12 interface and recovery findings, five bounded closure work packages and explicit design blockers; no implementation or runtime verification claimed.
- ТЗ-NX-006: proposed Portfolio & Financial Ledger requirements covering immutable journal events, exact accounting, balances/positions, P&L, fees/funding, reconciliation, snapshots and deterministic replay; implementation not started.
- ТЗ-NX-005: proposed Independent Risk Engine requirements covering deterministic pre-trade authorization, exact exposure calculation, hierarchical hard limits, concurrent risk reservations, signed payload-bound approvals, continuous monitoring and kill-switch governance; implementation not started.
- ТЗ-NX-004: proposed Autonomous Execution Engine requirements covering durable command/outbox, order lifecycle, ambiguous outcomes, private execution events, reconciliation, kill switch, credential isolation and adapter certification; implementation not started.
- ТЗ-NX-003: proposed Quant & Strategy Engine requirements covering immutable strategy artifacts, deterministic DecisionContext/TradeIntent contracts, research provenance, bias controls, simulation fidelity and promotion gates; implementation not started.
- ТЗ-NX-002: proposed requirements for Footprint, Delta/CVD, DOM, Tape, Volume Profile, TPO, quality, replay and golden tests; implementation not started.
- NX-ADR-001: proposed canonical market-event envelope, typed payload semantics, provenance, exact units, ordering and schema evolution; no implementation claimed.
- NX-ARCH-001: proposed logical architecture, trust boundaries, deployment baseline and critical command/data flows; no technology stack selected.
- NX-RESEARCH-001: initial evidence-based comparison of HFTBacktest, QuantConnect LEAN and ABIDES; no engine selected.
- NX-WP-001: рабочий регламент AI Project Lead с правилами исследования, evidence, контроля качества, согласований и Definition of Done.
- NX-OPS-001: ежедневный pulse, еженедельный deep review и событийный анализ внешних изменений.

### Added
- Создана базовая структура документации NEXUS TRADING.
- Зафиксированы устав проекта, текущий статус, roadmap и readiness gates.
- Добавлены реестры ADR, спецификаций, исследований и безопасности.

### Notes
- Это документационный baseline, не программный релиз.
- Прототипирование остаётся заблокированным до прохождения readiness gates.
