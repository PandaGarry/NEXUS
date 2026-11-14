# Changelog

Заметные изменения проекта фиксируются в обратном хронологическом порядке. Release notes пишутся понятным языком; инженерные детали остаются в ADR/PR.

## Unreleased

### Added — Exact-decimal property verification
- Added 1,000 deterministic seeded property cases cross-checked against Python's independent rational `fractions.Fraction` representation for add/subtract/multiply/compare, canonical round-trip, step divisibility and exact quantization. This is reference-oracle evidence only; exact-head CI is pending.


### Updated — Execution control and evidence baseline
- Added [NX-PROJECT-CHECKLIST-001](docs/quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md), a living register for G0D D1–D8, engineering workstreams, ordered priorities, evidence rules and non-authorizations.
- Updated current verification evidence: GitHub Actions run [#43589753391](https://github.com/PandaGarry/NEXUS/actions/runs/43589753391) passed exact PR HEAD `b761f9249064f881cef994dfe8724b66034ebe02` with 10 exact-decimal and 21 gateway tests on Python 3.11–3.13.
- Explicitly deferred NX-ADR-006 because current strategy-validation governance is already covered by NX-ADR-003; reopen only if a distinct decision is identified.
- Corrected owner-decision status: OD-01/04 accepted, OD-15 partially accepted; no other owner decisions are inferred.


### Added
- NX-ARCH-002: proposed personal-first product/deployment profiles defining single-owner closed use, PERSONAL_DEV/PERSONAL_TEST/PERSONAL_PRODUCTION and separately gated future COMMERCIAL scope; no runtime enforcement or live authorization claimed.
- NX-IF-001: proposed Canonical Trade Command & Risk Approval Contract defining TradeIntent separation, immutable command envelope, canonicalization/digest, signed scoped approval capability, one-time consumption, invalidation and negative conformance matrix; implementation and tests not started.
- NX-IF-002: proposed Exposure Snapshot & Risk Reservation Contract defining exclusive exposure buckets, source ownership, durable reservations, atomic multi-scope capacity checks, fencing, partial-fill transfer, unknown-outcome retention and recovery/conformance scenarios; implementation and tests not started.
- NX-IF-003: proposed Execution Event & Ledger Posting Contract defining canonical fill identity, durable Execution outbox/Ledger inbox, atomic balanced journal posting, fee/correction handling, replay and projection-watermark exposure handoff; implementation and tests not started.
- NX-IF-004: proposed State Evidence, Freshness & Recovery Barrier Contract defining source-specific evidence vectors, freshness policies, quarantine/recovery cases, scoped generation-fenced barriers and restart/reconciliation ordering; implementation and tests not started.
- NX-IF-005: proposed Emergency Operations, Halt & Risk-Reduction Authorization Contract defining monotonic scoped halt epochs, command-class authorization, bounded emergency plans, protective-order handling, operator governance and controlled resume; implementation and tests not started.
- NX-OWNER-DECISIONS-001: proposed owner decision register consolidating OD-01..OD-15 across G0–G3; OD-01/04 accepted and OD-15 partially accepted by explicit owner direction, all other decisions remain open/deferred.
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

### Added — Project foundation
- Создана базовая структура документации NEXUS TRADING.
- Зафиксированы устав проекта, текущий статус, roadmap и readiness gates.
- Добавлены реестры ADR, спецификаций, исследований и безопасности.

### Added — Foundation documentation review and domain reference slice
- NX-DOC-REVIEW-001: bounded final documentation review with PR integration findings, cross-document corrections, G0 close-out packages and finite exit criteria.
- NX-ARCH-003: proposed venue-neutral exact numeric domain-kernel contract; production language, numeric bounds and rounding policy remain open.
- Added a dependency-free Python exact-decimal reference oracle plus language-neutral golden vectors v1.0.0 (15 cases) and 10 unit tests for parsing, canonicalization, exact arithmetic, comparison, quantization and tick/lot divisibility. Local tests passed; this is not production runtime evidence.
- Corrected NX-ARCH-001 stale reference to NX-ADR-001 and added a separate G0D documentation-baseline gate. No prototype/live permission is granted.

### Added — Reference platform fit assessment
- NX-RESEARCH-006: evidence-backed first assessment of NautilusTrader against NEXUS execution, risk, persistence, reconciliation, numeric and simulation contracts. NautilusTrader remains a leading candidate, not selected; no dependency integration or live use authorized.
- Project status distinguishes isolated execution of the 10 exact-decimal reference tests from unavailable GitHub Actions evidence and absent production runtime.

### Added — NautilusTrader v2 release baseline review
- NX-RESEARCH-007: pinned v2.0.0rc9 tag/commit, verified its pre-release status and compared it with the previously inspected develop snapshot (diverged histories: 77 ahead / 72 behind).
- Recorded RC9 precision conversion, SBE compatibility, at-least-once Redis retry and modify/cancel-denied semantics as mandatory NEXUS conformance topics.
- NautilusTrader remains a leading candidate, not selected; RC9 is test-only and not approved for production use.

### Added — NautilusTrader RC9 execution boundary audit
- NX-RESEARCH-008: exact v2.0.0rc9 source audit confirms asynchronous best-effort persistence before transport, non-universal RiskEngine routing and process-local dispatched-order markers absent after restart.
- NautilusTrader is not approved as NEXUS execution authority. NEXUS-owned durable outbox, non-bypassable Risk gateway, ledger and recovery barrier remain mandatory.

### Added — Dispatcher authority transfer and egress fencing
- NX-REF-EXEC-002 proposes an account-scoped authority-transfer protocol: freeze, advance epoch, positively fence old egress, quarantine ambiguous attempts, reconcile venue evidence, then grant new egress capability. Lease expiry alone is explicitly not a fence. Design only; no production mechanism implemented.

### Added — Command gateway reference conformance slice
- NX-REF-EXEC-001 and `foundation/reference-model/execution-gateway/`: a narrow Python/SQLite test model for payload-bound CREATE authorization, one-time approval/reservation consumption, durable-before-dispatch state, and conservative unknown-outcome recovery.
- Added 21 deterministic fault and negative-path tests, including two independent SQLite-connection race tests and an explicit split-brain counterexample showing a stale worker can still send after recovery. A local state-CAS guard now rejects its late ACK as an authoritative transition and records it as a stale venue observation, preserving OUTCOME_UNKNOWN. Egress fencing remains unresolved; this is not a safety pass. The model is explicitly test-only; no production signer, database, multi-process fencing, Risk calculation, ledger or venue integration is claimed.
- Added GitHub Actions conformance workflow for the exact-decimal and command-gateway reference suites on Python 3.11, 3.12 and 3.13. Run #43588971888 passed on exact HEAD `d22d417da0d11dab5b9bb79298edd379eab46867`; both suites passed on all three runtimes (10 + 20 tests per runtime at that historical revision). The two-connection concurrency cases exercise local SQLite transaction serialization only, not distributed leases/fencing. A later adversarial counterexample reproduces stale-worker egress after recovery. A follow-up state-CAS guard prevents stale ACK overwrite and records late responses as observations; its code revision passed CI on Python 3.11–3.13. This remains reference-model evidence only.
