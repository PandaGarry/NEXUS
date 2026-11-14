# Дорожная карта

Статусы меняются только при наличии проверяемых свидетельств.

## Phase 0 — Foundation Audit (In Progress)

**Operational checklist:** [NX-PROJECT-CHECKLIST-001](quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md). It is the current source for D1–D8 package status and ordered engineering work.

### Foundation close-out track (active)
- [ ] Complete NX-DOC-REVIEW-001 packages D1–D8 or explicitly defer each behind a named gate.
- [x] Add test-only egress authority handover state-machine model; actual network/host fencing remains BLOCKED.
- [x] Add exact-decimal reference oracle and unit tests (11/11; reference-only evidence).
- [x] Publish language-neutral golden vectors v1.0.0 (15 cases); Python oracle passes all vectors.
- [x] Add deterministic exact-arithmetic property checks: 1,000 seeded cases cross-checked against independent `fractions.Fraction` arithmetic.
- [ ] Add broader fuzz coverage and cross-language conformance.
- [ ] Approve production numeric bounds, overflow behavior, typed units and rounding ownership before financial runtime implementation.
- [ ] Establish implementation workspace, pinned toolchain, dependency policy and reproducible CI before production-language kernel work.
- [ ] Зафиксировать baseline commit и структуру Tradoor.
- [ ] Завершить аудит exchange adapters и capabilities matrix. (Initial Tradoor source pass recorded in NX-RESEARCH-002; private/funding and full instrument rules remain UNKNOWN.)
- [ ] Проверить ingestion, recorder, backfill, migrations и persistence.
- [ ] Проверить тесты, CI, dependency tree и лицензии.
- [x] Подготовить initial threat model (NX-SEC-001, PROPOSED).
- [ ] Провести deployment-specific review и security verification.
- [ ] Сравнить HFTBacktest, LEAN и ABIDES по fidelity, replay, latency и queue modeling.
- [ ] Сопоставить Order Flow формулы с поведенческими эталонами.
- [ ] Зафиксировать дефекты, неизвестные свойства и ограничения.

- [x] Prepare bounded first-venue candidate review (NX-RESEARCH-003): Coinbase and Kraken remain conditional candidates; no selection until jurisdiction/product eligibility and exact API capability are verified.

## Phase 1 — Core Architecture (Blocked)

- [x] Define proposed personal-first product/deployment profile model (NX-ARCH-002): single-owner closed personal use first; future commercial operation requires a separate legal/security/product review. Owner approval and runtime enforcement remain open.

- [x] Publish bounded WP-A..WP-E interface design drafts (NX-IF-001..005).
- [x] Consolidate critical owner decisions and readiness dependencies in NX-OWNER-DECISIONS-001.
- [x] Accept bounded v1 scope: one venue + dedicated account/subaccount; account/subaccount risk boundary; server-side autonomous runtime; shared Desktop+Web backend (OD-01/04/15, owner-directed 2026-11-14).
- [ ] Select first venue and product/account mode after confirming legal/account eligibility and completing official capability review (OD-02/03).
- [ ] Obtain remaining G0 owner decisions before freezing the architecture baseline.
- [ ] Obtain G1/G2 decisions and conformance evidence before read-only/paper and sandbox/shadow gates respectively.
- [ ] Obtain all G3 risk/security/emergency approvals before any limited-live consideration.
- [ ] Утвердить NX-ADR-001 Unified Market Event Contract. (Draft published; owner review and schema conformance design review required.)
- [ ] Утвердить NX-ADR-002 Execution Integrity & Reconciliation. (ADR drafted; owner review required.)
- [ ] Утвердить NX-ADR-003 Simulation Fidelity & Strategy Validation. (ADR drafted; owner review required.)
- [ ] Утвердить NX-ADR-004 Market Data Recovery State Machine.
- [ ] Утвердить NX-ADR-005 Instrument Specification & Exact Arithmetic.
- [ ] Утвердить NX-ARCH-001 целевую архитектуру и deployment topology. (Draft published; owner review required.)
- [ ] Закрыть NX-ARCH-REVIEW-001 WP-A..WP-E: canonical command/approval, exposure/reservations, Execution↔Ledger handoff, freshness/recovery, emergency operations. WP-A..WP-E design drafts now exist; acceptance and owner review remain open.
  - [x] WP-A design draft: NX-IF-001 published and readback verified.
  - [ ] WP-A acceptance: owner/security decisions, canonicalization/digest selection, cross-language golden vectors and conformance tests.
  - [x] WP-B design draft: NX-IF-002 published; exclusive buckets, reservation lifecycle, atomic concurrency and failure matrix specified.
  - [ ] WP-B acceptance: owner decisions, persistence/transaction design, schema conformance, concurrency and fault-injection evidence.
  - [x] WP-C design draft: NX-IF-003 published; execution ownership, canonical fill identity, durable outbox/inbox, atomic Ledger posting, corrections and projection watermark handoff specified.
  - [ ] WP-C acceptance: owner accounting decisions, transaction/store selection, schema conformance, golden accounting fixtures, replay and fault-injection evidence.
  - [x] WP-D design draft: NX-IF-004 published; StateEvidenceVector, source-specific freshness/quality, quarantine, RecoveryCase and scoped RecoveryBarrier/restart ordering specified.
  - [ ] WP-D acceptance: owner freshness thresholds and venue/account scope, durable persistence and operator policy decisions, schema conformance, restart/replay/reconciliation and fault-injection evidence.
  - [x] WP-E design draft: NX-IF-005 published; monotonic scoped HaltState, command-class authorization, protective-order semantics, bounded emergency plans, operator governance and controlled resume specified.
  - [ ] WP-E acceptance: owner role/dual-control/emergency-policy decisions, venue/account-mode capability certification, halt propagation, race, fault-injection and adapter conformance evidence.
- [ ] Определить transactional boundaries, durable outbox, event log и recovery.
- [ ] Согласовать EvidenceRequirementSet/FreshnessPolicy thresholds и recovery objectives с владельцем до любой реализации.
- [ ] Выполнить end-to-end contract review и зафиксировать owner decisions до выбора реализации. Consolidated register: NX-OWNER-DECISIONS-001 (OD-01..OD-15).

## Phase 2 — Professional Analytics (Blocked)
- [ ] Утвердить ТЗ-NX-002 Professional Order Flow. (Draft published; formula decisions and owner review required.)
- [ ] Подготовить независимые golden datasets и тесты для Footprint, Delta/CVD, DOM, Tape, Profiles.
- [ ] Независимая проверка данных и нормализации.
- [ ] UI/UX benchmark и производительные сценарии.

## Phase 3 — Quant & Simulation (Blocked)
- [ ] Утвердить ТЗ-NX-003 Quant & Strategy Engine. (Draft published; owner review and strategy-runtime decisions required.)
- [x] Publish NX-ADR-003 simulation and strategy-validation protocol (PROPOSED; owner review remains open).
- [ ] NX-ADR-006 explicitly deferred: NX-ADR-003 already covers the current strategy-validation governance scope; reopen only if a distinct architectural decision is identified.
- [ ] Определить execution simulation levels L1/L2/L3.
- [ ] Утвердить out-of-sample, purge/embargo и walk-forward protocols.
- [ ] Проверить latency, queue position, partial fills, slippage и adverse selection.

## Phase 4 — Risk & Execution (Blocked)
- [ ] Утвердить ТЗ-NX-004 Autonomous Execution Engine. (Draft published; venue shortlist, kill-switch playbook and persistence decisions require owner review.)
- [ ] Утвердить ТЗ-NX-005 Independent Risk Engine. (Draft published; owner limits, policy scopes, kill-switch governance and risk input contracts require owner review.)
- [ ] Утвердить NX-ADR-002 Execution Integrity & Reconciliation.
- [ ] Утвердить независимый Risk Engine и NX-SEC-001 threat model.
- [ ] Проверить kill switch, limits, secrets, audit и disaster recovery.
- [ ] Допускать read-only/paper только после прохождения архитектурных gates.

## Phase 5 — Portfolio & Accounting (Blocked)
- [ ] Утвердить ТЗ-NX-006 Portfolio & Financial Ledger. (Draft published; chart of accounts, posting rules, P&L boundaries, FX/valuation policy and retention require owner review.)
- [ ] Зафиксировать immutable journal, event identity, correction/bust and idempotency semantics.
- [ ] Подготовить golden accounting fixtures для spot, linear, inverse и quanto.
- [ ] Проверить fees, funding, settlement, transfers, reconciliation и deterministic replay.
- [ ] Согласовать Ledger read models and freshness contract с Risk Engine.

## Phase 6 — Autonomous Intelligence (Blocked)
- [ ] Определить права и ограничения AI Orchestrator.
- [ ] Проверить policy enforcement и полный audit trail.
- [ ] Исключить прямой обход AI компонента Risk Engine.

## Phase 7 — Desktop + Web Production (Blocked)
- [ ] Progress through PERSONAL_DEV → PERSONAL_TEST → PERSONAL_PRODUCTION only via explicit readiness gates; PERSONAL_PRODUCTION does not itself authorize live trading.
- [ ] Defer COMMERCIAL profile, multi-tenancy and third-party users to a separately approved business/legal/security work package.
- [ ] Выбрать desktop shell по benchmark.
- [ ] Проверить единое состояние, offline/reconnect и multi-device behavior.
- [ ] Подготовить production observability, backups и deployment runbooks.

Live trading требует отдельного формального допуска, ограниченного rollout и подтверждённой эксплуатационной готовности.

## Правило завершения Foundation Audit (anti-infinite-audit)

Phase 0 не означает исследовать все существующие проекты и все возможные функции. Аудит закрывается по фиксированным work packages, когда для каждого критического контура:
- известны применимые требования NEXUS;
- проверены выбранные исходники/документы/тесты по заранее определённому scope;
- зафиксированы capabilities и UNKNOWN;
- оценены критические риски и mitigation;
- принято решение: reuse / adapt / replace / build / defer;
- созданы ADR/spec и acceptance criteria;
- отсутствуют открытые вопросы, способные изменить фундаментальную архитектуру, либо они явно вынесены в owner decision.

### Очерёдность закрытия Phase 0
1. **Market data & exchange adapters:** capabilities matrix по приоритетным биржам и критическим потокам; отдельный список неподдержанных/неподтверждённых возможностей.
2. **Execution & recovery:** lifecycle, idempotency, unknown outcome, reconciliation, restart recovery и failure modes.
3. **Financial correctness:** instrument specs, exact arithmetic, fees, funding, margin и ledger invariants.
4. **Simulation & research:** сопоставление HFTBacktest/LEAN/ABIDES; выбрать минимально достаточную модель симуляции и зафиксировать limitations.
5. **Security & supply chain:** threat model, credentials, auth, dependencies, licenses, CI and backup/recovery.
6. **Analytics correctness:** формулы, aggregation semantics, golden datasets и independent checks для ключевых Order Flow функций.
7. **Architecture synthesis:** NX-ARCH-001, NX-ARCH-REVIEW-001, service boundaries, deployment, persistence, observability и final readiness review.

Каждый work package имеет ограниченный scope и exit criteria. Новые интересные направления помещаются в backlog, но не блокируют текущий этап, если не затрагивают безопасность, финансовую корректность или выбранную архитектуру.

### Обязательный выход Phase 0
- утверждаемые NX-ADR-001..006 и NX-SEC-001;
- NX-ARCH-001 и NX-ARCH-REVIEW-001;
- шесть ТЗ с контрактами и acceptance criteria;
- exchange capabilities matrix;
- risk register и dependency/license inventory;
- test/evidence matrix;
- implementation sequence и estimate ranges;
- финальный readiness report с PASS/BLOCKED и ссылками на evidence.

Только после owner review и прохождения всех критических gates разрешается начать безопасный read-only/paper prototype. Live trading требует отдельного допуска.

- Domain kernel: explicit, version-pinned instrument quantity-unit semantics (NX-REF-DOMAIN-004) added as test-only reference; venue mappings and derivative risk/P&L formulas remain future qualification work.

- Domain kernel: exact rational division and explicit quantization reference (NX-REF-DOMAIN-005) added; financial-operation-specific rounding policies remain a separate decision.

- Inverse contracts: exact rational base exposure reference added; venue-specific contract semantics, P&L, margin and rounding policy remain open.

- Domain kernel: NX-REF-DOMAIN-007 adds a test-only bounded numeric context with mandatory caller-supplied budgets; production limits remain unselected.
- Domain kernel: NX-REF-DOMAIN-008 adds canonical scalar decimal/rational wire formats; cross-language and typed event/command integration remain open.

### Financial-operation correctness increment

- [x] Publish NX-REF-DOMAIN-009 proposed operation-specific rounding and valuation contract; define universal exactness invariants, policy boundaries, provenance and venue qualification dossier.
- [x] Cross-review financial-operation contract against NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006; no blocking contradiction found, with owner/venue gaps retained.
- [ ] Obtain owner decisions for position matching, fee/funding accounting, FX/collateral valuation and journal rounding.
- [ ] Qualify exact venue/product/account and capture authoritative fee, funding, margin, liquidation and price-source fixtures.
- [x] Add bounded venue-neutral mathematical golden fixtures only for explicitly dimensioned identities; venue-specific financial-operation fixtures remain blocked pending authoritative evidence.

No production financial calculator or execution/risk/ledger implementation is authorized by this documentation increment.

### Venue-neutral financial math fixtures

- [x] Publish NX-REF-DOMAIN-010 and language-neutral exact vectors for explicitly dimensioned spot, linear, inverse and partial-fill arithmetic.
- [x] Add independent rational-oracle checks and negative dimension/identity tests.
- [x] Add the fixture suite to Python 3.11–3.13 CI.
- [x] Verify exact code/test commit CI: 179 tests per runtime passed on Python 3.11, 3.12 and 3.13; freeze this bounded fixture package as test-only reference evidence.
- [ ] Keep fee/funding/P&L/margin/liquidation/FX/accounting fixtures blocked until authoritative venue/account or owner policies exist.

This package validates mathematical identities only; it does not pass financial readiness gates.

- [x] Cross-review NX-REF-DOMAIN-009 against NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006; no blocking contradiction found, with owner/venue gaps retained.
- [x] Add venue-neutral exact dimensional math fixtures for spot, explicitly mapped linear/inverse contracts and partial-fill weighted-average arithmetic; initial Python 3.11–3.13 CI passed.
- [x] Verify final exact PR head and freeze the bounded mathematical fixture package (182 tests per runtime; see NX-REF-DOMAIN-010).
- [ ] Obtain owner decisions and venue qualification before authoring fee/funding/P&L/margin/liquidation/FX/accounting golden vectors.

### Russia jurisdiction and first-venue qualification gate

- [x] Publish NX-RESEARCH-009 with current Law 282-FZ, Bank of Russia guidance, domestic crypto-exchange registry, MOEX/SPB product eligibility and foreign-venue screening.
- [x] Pin Bank of Russia Directive 7441-U: effective 2026-11-17; non-qualified broker acquisition cap RUB 300,000/year; BTC, ETH and USDT may be admitted to organized trading subject to criteria. This does not establish that a specific product/API is live.
- [x] Mark earlier Coinbase/Kraken and Russian-citizenship shortlist memos as historical/superseded for live venue selection.
- [ ] Confirm owner qualified-investor status directly with the actual broker.
- [ ] Verify T-Invest API instrument access flags and streaming/order/fill support for exact crypto-index futures/neoassets; no orders.
- [ ] Obtain written T-Invest Lab confirmation of live spot crypto service, product terms and API availability.
- [ ] Obtain product-specific legal advice on Articles 30–32 of Law 282-FZ and Article 30(2) software-assistance scope.
- [x] Draft NX-ADR-007 Venue Eligibility & Jurisdictional Activation Gate; owner/legal acceptance and conformance evidence remain open.
- [ ] Keep all foreign venues RESEARCH_ONLY until legal, KYC, product and API eligibility are evidenced.

First-venue selection remains BLOCKED; no live trading is authorized.

- [x] Add test-only venue eligibility evidence evaluator and 24 deterministic fail-closed scenarios; exact-head CI verification pending.
- [ ] Verify the venue eligibility reference suite passes on Python 3.11, 3.12 and 3.13 at the exact PR head.
- [ ] Keep NX-ADR-007 PROPOSED until owner and qualified legal review are complete.

- [x] Verify venue eligibility reference suite and complete reference matrix: 210 tests/runtime on Python 3.11/3.12/3.13; 630 successful executions at PR #14 SHA `8c7eed6ac781a40c81652da08ff3207f4d46bc6d` (run 43598444584).

- [x] Add test-only eligibility egress fencing reference and 21 concurrency/ordering tests; CI passed 231 tests/runtime on Python 3.11/3.12/3.13 (693 executions) at SHA `a7a369ca9e5683208fbcd43a3fd1de0a8f8c47f1`, run 43599182263.
- [ ] Design and verify production cross-process egress fencing, durable dispatch state, bounded network timeouts and crash recovery.

## Phase 1/4 engineering increment — Rust and conformance boundary

- [x] Publish NX-ARCH-004 as a proposed design for Rust domain/execution boundaries and cross-language conformance.
- [x] Create dedicated engineering branch `engineering/rust-execution-domain-conformance-v0` from the reviewed PR #14 head `ab6976933cb4de9b5320b73531034d02edc53907`.
- [x] Define adapter trust boundaries, NEXUS-owned authorization/egress, OUTCOME_UNKNOWN handling and the Rust/Python golden-fixture contract.
- [ ] Owner/architecture review of RUST-01..06.
- [x] Cross-review NX-ARCH-004 against NX-IF-001..005, NX-ARCH-003, NX-ADR-002/005/007 and NX-SEC-001; harmonize ADR-002 reservation/approval/dispatch ordering.
- [ ] Approve toolchain and implementation workspace under G0D/G1 before production-language implementation.
- [ ] Implement Rust domain slice and differential conformance harness.
- [ ] Prove distributed/host-level egress fencing; single-process reference tests are insufficient.

**Current status:** design draft only. No Rust runtime or production implementation has been added. Prototype readiness remains BLOCKED and live trading remains NOT AUTHORIZED.

- [x] Harmonize NX-ADR-002 with NX-IF-001/002: durable reservation precedes capability issuance; single-use capability consumption is atomic with command/outbox commit; pre-egress attempt marker preserves conservative `DISPATCH_OUTCOME_UNKNOWN` exposure.
- [ ] Owner/architecture/security acceptance of the harmonized design; implementation gates remain unchanged.


## Conformance infrastructure — fixture contract

- [x] Audit existing golden fixture formats and confirm they are not yet normalized under one schema.
- [x] Publish NX-ARCH-005 with proposed fixture envelope, stable rejection classes, comparison rules, version policy and runner evidence protocol.
- [x] Classify legacy fixture migration paths and identify where rejection classes or expected behavior require reference-derived review.
- [x] Specify initial operation identifiers, typed result forms and reference exception mapping; resolve numeric-wire's catch-all error limitation with typed subclasses and stable error classes.
- [ ] Review and approve operation registry and stable error mappings before schema/runner implementation.
- [x] Define strict JSON ingestion and fixture identity requirements, including duplicate-key rejection and raw-byte SHA-256 evidence.
- [ ] Owner review and approval of fixture contract and error taxonomy.
- [ ] Migrate legacy fixture suites through explicit, tested converters; preserve v1 files unchanged.
- [ ] Implement deterministic Python runner and machine-readable report.
- [ ] Implement Rust adapter/differential runner only after G0D/G1 and toolchain/workspace approval.

**Current blocker:** repository tree contains no Cargo manifest, Rust toolchain pin, Rust source or Rust runner. No implementation readiness is inferred.

## Conformance contract review refinement — 2026-11-14

Before implementing a machine-readable fixture schema or runner, close the NX-ARCH-005 owner-review gate with an operation-by-operation executable-surface map. Decimal/rational and numeric-wire mappings are grounded in current reference APIs; financial fixture operations without callable oracles and instrument-spec validation remain deferred. Review stable rejection mappings for bounded numeric and dimensional-domain exceptions explicitly. The example envelope is now strict-JSON valid. Schema/runner and Rust work remain gated; no production readiness is implied.

## Reference operation coverage correction — 2026-11-14

The financial operation audit has been corrected: spot, linear and inverse paths have executable reference coverage; inverse exposure remains rational. Extract the currently inline partial-fill weighted-average algorithm into a named pure reference operation before registering it as a reusable normalized operation. Separately map the arbitrary-precision oracle and explicit bounded numeric wrapper; do not treat synthetic `NumericLimits` as a production profile. Invalid operation parameters must not be misclassified as mathematical rejection outcomes.


## Financial reference operation extraction — 2026-11-14

- [x] Extract partial-fill weighted-average arithmetic into a named pure reference callable with typed quantity/notional outputs and exact rational average.
- [x] Move golden-vector and seeded permutation/partition tests to the extracted callable; add empty-input, dimension-mismatch and repeating-rational cases.
- [ ] Register the operation in normalized fixture suites only after owner review of NX-ARCH-005 and approval of schema/runner implementation.

No venue fill policy, fees, funding, P&L, accounting or rounding semantics are introduced. Reference-only; production readiness unchanged.


## Operation-specific rejection mapping audit — 2026-11-14

- [x] Inspect current typed exception surfaces for exact decimal, rational, bounded numeric, dimensional domain, instrument-unit and partial-fill aggregation operations.
- [x] Separate mathematical/domain failures from malformed API input and record candidate stable mappings in NX-ARCH-005.
- [x] Identify unresolved invalid-domain-value and identity-mismatch cases instead of forcing them into an inaccurate class.
- [ ] Owner review and approval of the rejection taxonomy and operation registry.
- [ ] Implement adapters/schema/runner only after approval.

No production mapping or normalized wire contract is approved by this audit.


- [x] Close the reference API type-check gap in `ExactDecimal.is_multiple_of`; malformed step types now produce explicit `TypeError` and have a regression test. No numeric semantics changed.


## Pre-egress boundary wording closure — 2026-11-14

- [x] Make the IF-002 attempt-marker-before-network ordering explicit and align it with ADR-002.
- [x] State that `DISPATCH_OUTCOME_UNKNOWN` is entered before the external side effect and does not assert that bytes were sent.
- [ ] Prove durable commit ordering, stale-worker fencing and final trusted-egress validation in the selected implementation.
- [ ] Fault-inject crashes before marker, after marker/before socket write, during write, after venue acceptance/before response, and after response/before persistence.

Documentation ambiguity closed; implementation proof remains a separate gate.


## Transaction and egress failure semantics refinement — 2026-11-14

- [x] Define the logical Risk reservation transaction separately from the Command Coordinator transaction.
- [x] Require atomic single-use capability consumption with command + reservation reference + outbox commit.
- [x] Define Egress as the sole credential/socket owner and exclude direct venue egress from workers/adapters.
- [x] Add crash-point matrix covering ambiguous commit, attempt marker, socket write, acceptance, fills/Ledger, takeover and recovery evidence.
- [ ] Resolve OD-08 capability serialization/signing and key custody with security review.
- [ ] Resolve OD-09 database, isolation, durable journal and multi-scope reservation mechanism.
- [ ] Resolve OD-10 freshness/recovery and failover objectives; OD-12 operator/incident authority.
- [ ] Implement and fault-inject the selected actual egress fence; prove old path cannot send after takeover under partition/restart.

This refinement is proposed design only. It does not close G0/G1, select a technology provider or authorize production execution. The design intentionally avoids a distributed transaction between Risk and Command; each boundary owns its local durable commit and recovery protocol.


### Persistence and egress topology decision analysis — 2026-11-14

The active architecture track now compares database transaction models and Trusted Egress deployment choices in NX-REF-EXEC-002 §4.5. The candidate baseline separates Risk's atomic all-scope reservation commit from Command's atomic single-use capability-consume + command/outbox commit; no distributed ACID transaction is assumed. Egress must own the actual venue socket and credentials, while workers have no direct venue route. Takeover requires positive external fencing of the old process/host/network identity; DB lease expiry is not proof. G1 technical baselines for OD-08/09/10/12 are selected in NX-ADR-008; exact libraries/providers, security review, numeric thresholds, deployment and production acceptance remain open. This is design-only and does not authorize implementation/live operation.



### Exact-head CI verification after persistence/egress analysis — 2026-11-14

- Documentation analysis head verified: `3187a69e443157ac3e66b874b4dcbb29588ddc70`.
- GitHub Actions run [#43606550889](https://github.com/PandaGarry/NEXUS/actions/runs/43606550889) completed successfully on that exact head.
- Three jobs passed: Python 3.11, 3.12 and 3.13. Each executed 13 isolated reference-model suites with counts 11, 24, 13, 17, 12, 16, 18, 18, 32, 12, 15, 28 and 21 = 237 tests per runtime; 711 successful test executions total.
- This CI run verifies the existing Python reference-model suites at the exact documentation-analysis head. It does not test the newly documented transaction alternatives, database isolation, production egress topology, external host/network fencing, Rust, venue behavior or live safety.


### Open-source component qualification — 2026-11-14

- [x] Publish NX-RESEARCH-010 with candidate matrix and module authority exclusions.
- [ ] Define G0D dependency governance: immutable pins, license/transitive review, SBOM, provenance, vulnerability scanning and reproducible builds.
- [ ] Evaluate PostgreSQL on exact pinned version against Risk reservations, Command outbox, Ledger journal and recovery invariants before OD-09 selection.
- [ ] Define OpenTelemetry instrumentation/redaction contract before deploying a collector.
- [ ] Compare OpenBao with managed KMS/HSM only after Egress/deployment threat model is stable.
- [ ] Revisit NATS, Cilium and Temporal only when workload/deployment requirements justify them.

No module adoption or runtime integration is implied by this research increment.


## Modular product boundaries and security isolation (design track)

- [x] Publish NX-ARCH-006 proposal for bounded contexts, module contracts, deny-by-default admission, workload identity, capability grants and independent lifecycle.
- [x] Define Identity & Access, Demo and Learning/Wiki as separate product domains with distinct permissions and data ownership.
- [x] Define mandatory Demo/live invariants: separate ledger/account namespace, simulator-only route, no live credentials/egress, server-side enforcement and adversarial isolation tests.
- [ ] Cross-review against NX-ARCH-001..005, NX-SEC-001, NX-IF-001..005 and owner decisions.
- [ ] Complete module inventory, data classification, capability matrix and G0D/D4/D6 threat-to-test mapping.
- [ ] Select modular-monolith vs separately deployed trust domains only after deployment/threat review; decide storage isolation under OD-09.
- [ ] Implement one safe module prototype only after G0D/G1 approval and explicit authorization; public registration and live capability remain separately gated.

Publication is design progress, not implementation or security certification.


**NX-ARCH-006 verification note (2026-11-14):** the documentation increment's exact branch head `e15e47f9512bc07a1f6534a4f41b0d27d7d42578` passed workflow [#43608583358](https://github.com/PandaGarry/NEXUS/actions/runs/43608583358): 237 existing Python reference-model tests on each of Python 3.11/3.12/3.13 (711 executions). This is regression evidence only; no module runtime, identity, storage isolation, secret boundary or network-egress behavior is tested. Subsequent documentation-only synchronization commits are not covered by that exact-head run.


## Long-term product platform extensibility (design track)

- [x] Publish NX-ARCH-007 candidate product-domain taxonomy and stable extension principles.
- [x] Define three independent planes: product capability, commercial entitlement and security authorization.
- [x] Define entitlement records/lifecycle, replay-safe payment event ingestion, quota separation, downgrade behavior and versioned module compatibility.
- [ ] Cross-review NX-ARCH-007 against the protected-core and module-boundary architecture and owner decisions.
- [ ] Draft controlled module catalog and feature registry schemas, ownership/data-classification fields and compatibility policy.
- [ ] Build adversarial test plans for forged entitlements, replay/out-of-order webhooks, revocation, quota bypass, module failure and billing outage.
- [ ] Preserve critical-path independence: no billing/payment or non-critical product service in Risk/dispatch/egress synchronous flow.
- [ ] Only after explicit owner/legal/security approval consider public registration, payment integration, subscriptions, teams, multi-tenancy or commercial launch.

These are architectural readiness items, not commitments to ship all listed product domains.


## Module registry and admission governance (design track)

- [x] Publish NX-ARCH-008 with immutable module/artifact identity, registry record, lifecycle, trust tiers and manifest requirements.
- [x] Separate capability catalog, module declaration, workload grant, commercial entitlement and request-time domain authorization.
- [x] Define proposed module/data permission matrix, protected-core exclusions, contract/dependency policy, revocation and rollback requirements.
- [x] Define 20 adversarial module qualification scenarios and G0D/G1 exit criteria.
- [ ] Cross-review NX-ARCH-008 with NX-ARCH-001..007, NX-SEC-001, NX-IF-001..005 and owner decisions.
- [ ] Convert the proposed record into a versioned canonical schema only after ownership, signing/provenance and policy decisions are reviewed.
- [ ] Specify and test actual workload identity, storage/secret isolation, network/egress enforcement and revocation propagation before selecting a runtime.
- [ ] Select one low-risk first-party read-model module for a non-production G1 prototype only after G0D approval.

No executable registry, plugin loader, module runtime, third-party code execution or new dependency is approved by this design increment.


### NX-ARCH-008 regression verification


### NX-ARCH-008 exact-head regression verification — 2026-11-14

- Exact branch HEAD `b1d3201a1fe1706909218943f5464eba43ea1041` passed GitHub Actions [#43611030968](https://github.com/PandaGarry/NEXUS/actions/runs/43611030968).
- All three jobs completed successfully: Python 3.11, 3.12 and 3.13; 13 isolated reference-model suites / 237 tests per runtime; 711 successful test executions total.
- This verifies the existing Python reference-model regression workflow at that exact documentation head. It does **not** test NX-ARCH-008's proposed registry, schema, identity, grant issuance, module isolation, secret handling, database permissions, network/egress enforcement, Rust, venue behavior or live-trading safety.
- The exact-head CI result is regression evidence only; NX-ARCH-008 remains PROPOSED / DESIGN ONLY and G0D/G1 remain open.


### Final synchronized documentation-head verification


### Final synchronized documentation-head verification — 2026-11-14

The synchronized documentation head `c5c00d37b26f365b79690a9f3297ab571d9ec6f2` passed exact-head GitHub Actions [#43611122433](https://github.com/PandaGarry/NEXUS/actions/runs/43611122433). Python 3.11, 3.12 and 3.13 jobs all completed successfully; each ran 13 isolated reference-model suites / 237 tests (711 successful executions total). This is existing Python reference-model regression evidence only. It does not test NX-ARCH-008's proposed registry, manifest, workload identity, grants, module runtime/isolation, secrets, database permissions, network/egress enforcement, Rust, venue behavior or live-trading safety. NX-ARCH-008 remains PROPOSED / DESIGN ONLY; G0D/G1 remain open.


## Module governance cross-review

- [x] Complete NX-ARCH-REVIEW-002 across target architecture, modular boundaries, entitlements, module registry, threat model, interface contracts and owner decisions.
- [x] Resolve gateway/domain-authorization wording ambiguity and T4 trust-tier interpretation.
- [x] Record remaining F-03..F-08 implementation and owner-decision blockers.
- [ ] Close permission-to-contract mapping, revocation objectives, trust-root decisions, boundary enforcement, first-module scope and operator governance with evidence.
- [ ] Keep G0D/G1 blocked until their specific exit criteria are satisfied.

Cross-review completion is not architecture acceptance or security verification.


## Capability catalog and authorization contracts

- [x] Publish NX-ARCH-009 with capability record requirements, stable identifiers/versioning and single owner/enforcement authority.
- [x] Define scope grammar, data classification, candidate catalog and permission-to-owner/negative-test mapping.
- [x] Separate workload grants, commercial entitlements, user authorization and owning-service request decisions.
- [x] Define revocation, audit, privacy and CAP-01..18 adversarial qualification requirements.
- [ ] Complete cross-review against architecture, security and interface contracts.
- [ ] Obtain domain-owner/security acceptance and resolve field-level classification/retention and revocation objectives.
- [ ] Implement a strict validator and policy enforcement only after G0D acceptance; prove boundaries in G1.

No active grants or runtime authorization policy are created by the design artifact.


## Capability authorization cross-review

- [x] Complete NX-ARCH-REVIEW-003 and correct billing capability semantics.
- [x] Extend adversarial qualification scenarios CAP-19..26.
- [x] Record remaining findings CAP-R-02..09 and gate dependencies.
- [ ] Approve capability IDs, owners, contracts, scopes, data classes and negative tests.
- [ ] Close canonical resource binding, projection lineage, revocation, audit and billing-outage evidence before G0D/G1.
- [ ] Preserve no-billing-dependency invariant on Risk/command/dispatch/Trusted Egress.

Review completion is not implementation acceptance.


## Capability-to-interface contract traceability

- [x] Complete NX-ARCH-REVIEW-004 mapping all candidate capabilities against NX-IF-001..005 and NX-SEC-001.
- [x] Identify missing contracts for Market Data, Identity, Demo, Strategy, Analytics/Portfolio, Learning, Notifications and Billing rather than inventing endpoints.
- [x] Preserve protected domain ownership and v1 single-account scope.
- [ ] Obtain domain-owner/security acceptance and author missing product-domain contracts before schema/API/grant implementation.
- [ ] Complete field-level data classification, lineage, minimization and retention decisions.
- [ ] Define measurable revocation/cache/outage objectives and collect boundary-observed isolation evidence before G1.

Traceability completion is not capability approval or implementation readiness.


### Traceability review regression evidence

- NX-ARCH-REVIEW-004 exact review HEAD `f78fc7d006ea475cf596ee2bd8bd65b9a7d37afa` passed [workflow #43613212116](https://github.com/PandaGarry/NEXUS/actions/runs/43613212116): Python 3.11/3.12/3.13, 13 reference-model suites / 237 tests per runtime (711 successful executions).
- Evidence is limited to existing Python reference models; it does not validate capability grants, new domain contracts, module isolation, data-classification controls, Rust or venue integration.
- Evidence is recorded for the tested SHA only; subsequent documentation synchronization commits are not represented as an exact-head CI pass.


## Revocation, freshness and control-plane outage objectives

- [x] Publish NX-ARCH-REVIEW-005 with candidate authorization cache/revocation profiles, in-flight cancellation and outage matrix.
- [x] Separate authorization freshness from source evidence freshness, halt propagation and RecoveryBarrier readiness.
- [x] Preserve source-specific freshness and explicit fail-closed behavior; no global TTL or venue threshold inferred.
- [ ] Obtain owner/security approval of cache and revocation objectives; candidate numbers are not accepted SLOs.
- [ ] Obtain source-owner/OD-10 approval for data freshness, completeness, retention, clock uncertainty, retry budgets and RTO/RPO.
- [ ] Obtain OD-12 approval for halt deadline, operator roles, dual control and stale-egress containment.
- [ ] Prove cancellation, revocation and external fencing under process pause, partition and stale-worker fault injection.

Review publication does not establish implementation readiness or production guarantees.


### NX-ARCH-REVIEW-005 exact-head regression evidence

- Exact review HEAD `97a1819527bf6b1973793b12a084ef8cd0dee776` passed [workflow #43613493976](https://github.com/PandaGarry/NEXUS/actions/runs/43613493976): 13 Python reference-model suites / 237 tests each on 3.11, 3.12 and 3.13 (711 executions).
- This is regression-only evidence; it does not validate proposed cache/revocation SLOs, outage semantics, source freshness thresholds, halt propagation, process/DB/secret/network fencing, Rust or venues.
- Numeric objectives remain unaccepted proposals; OD-10/12 remain open.

## CI supply-chain and stacked-PR integration

- [x] Replace deprecated Node 20 action runtimes with current Node 24-compatible releases.
- [x] Pin direct GitHub Actions dependencies to verified full commit SHAs.
- [x] Verify the action-upgrade exact HEAD on Python 3.11/3.12/3.13 (13 suites, 237 tests per runtime; 711 executions).
- [x] Confirm PR #13 -> #14 -> #16 is a correctly based stacked dependency chain.
- [ ] Inventory and lock transitive action dependencies; add automated update/advisory monitoring.
- [ ] Reconcile PR #16 scope against its original title and split only genuinely independent review units.
- [ ] Integrate the stack in parent-first order after bounded review; retain Draft until review and required approval are complete.

The current CI result proves only the checked-in Python reference suites. It does not close G0D/G1 or authorize Rust production code, database selection, trusted egress, venue connectivity or live execution.


## Numeric wire parser resource boundary

- [x] Bound decimal wire scale independently from encoded syntax; default to the explicit input character budget and permit a stricter caller-supplied maximum.
- [x] Convert interpreter integer digit-budget failures into stable resource-limit outcomes.
- [x] Add decimal/rational adversarial regressions and verify 239 tests per Python runtime on the exact code/test HEAD.
- [ ] Add language-neutral fixture cases for scale and integer resource limits after NX-ARCH-005 profile semantics are accepted.
- [ ] Implement the normalized parser/runner and Rust differential conformance only after G0D/G1 readiness gates.

This hardening is confined to the Python reference oracle; it does not define production numeric limits.


## G1 technical baseline qualification

- [x] Select deterministic command encoding (RFC 8949 restricted deterministic CBOR), SHA-256 domain-separated digest and COSE_Sign1 fully specified COSE Ed25519 algorithm (-19, RFC 9864) capability-signing baseline.
- [x] Select PostgreSQL 18 as the G1 persistence evaluation target with separate local Risk/Command/Ledger transactions and no automatic failover.
- [x] Select source-specific freshness/recovery policy and fail-closed unknown handling; no global TTL.
- [x] Select single-owner halt/resume and conservative emergency-operation defaults; no automatic cancel-all/flatten or offline emergency orders.
- [ ] Qualify exact implementation libraries, versions, licenses, provenance and Python/Rust golden vectors.
- [ ] Qualify non-exportable key custody, rotation, revocation and jurisdictional/security compatibility.
- [ ] Prove PostgreSQL isolation/concurrency, crash/unknown-commit handling, backup/restore/PITR and old-primary fencing.
- [ ] Obtain numeric source freshness, retention, clock and RTO/RPO decisions from the accountable owner/domain.
- [ ] Prove Trusted Egress fencing at the actual network boundary before any live-readiness consideration.

Selection establishes a G1 design direction only. It does not authorize dependency installation, production deployment, real credentials or live trading.

## COSE Ed25519 interoperability gate

- [x] Replace deprecated polymorphic COSE EdDSA (-8) with fully specified COSE Ed25519 (-19) per RFC 9864.
- [x] Require OKP / Ed25519 key type/curve and reject algorithm/key mismatch, Ed448 and substitution.
- [x] Treat kid as a non-authoritative lookup hint; bind key resolution to issuer, algorithm, purpose, status and registry generation.
- [ ] Qualify library/provider support and cross-language COSE_Sign1 vectors, including rejection cases, before signer/verifier implementation.

## Canonical CBOR parser qualification

- [x] Specify RFC 8949 core deterministic map ordering and reject legacy length-first ordering.
- [x] Require raw-byte canonicality validation before CBOR object materialization.
- [x] Restrict command map keys to schema-defined text names; reject duplicate/unknown keys and trailing bytes.
- [ ] Build adversarial byte vectors for non-shortest encodings, indefinite lengths, unsorted maps, duplicate keys, invalid UTF-8 and resource exhaustion.
- [ ] Qualify Python and Rust decoders for raw-input visibility and identical rejection behavior before selecting dependencies.


## Parent-first PR integration gate

- [x] Verify the full direct PR ancestry #1 -> #2 -> #3 -> #4 -> #5 -> #6 -> #7 -> #9 -> #10 -> #11 -> #12 -> #13 -> #14 -> #16 by exact base/head SHA equality; PR #8 is parallel.
- [x] Confirm PR #16's immediate base is correctly the PR #14 head.
- [x] Verify current exact branch HEAD 7914772358d2ee49c87374373bad5c589d0a2905 on Python 3.11/3.12/3.13: 13 suites, 239 tests per runtime, 717 executions.
- [ ] Complete parent PR reviews and integrate strictly parent-first after each review gate.
- [ ] Reassess PR #16's 32-file scope and 248-commit history; split only demonstrably independent review units.

No PR merge, base retarget, force-push or branch rewrite is authorized by this checklist update. PR #16 remains Draft until the dependency stack is reviewable and the required owner approval is obtained.

## Final synchronized G1 baseline exact-head CI

- [x] Exact branch HEAD `7914772358d2ee49c87374373bad5c589d0a2905` passed workflow [#43615176349](https://github.com/PandaGarry/NEXUS/actions/runs/43615176349).
- [x] Python 3.11/3.12/3.13 each passed 13 suites / 239 tests; 717 successful executions total.
- [x] Confirm no test failures or Node.js 20 / `punycode` deprecation warnings.
- [ ] Build and run the proposed CBOR/COSE cross-language conformance suite only after exact libraries and schemas are reviewed; current CI is Python reference-only.
- [ ] Prove database, crash/recovery, external egress fencing and venue behavior independently; no production readiness is implied.

## Post-synchronization exact-head regression

- [x] Verify `928d5fd261553676c3fad6a8e88b984a862af338` on workflow [#43615282210](https://github.com/PandaGarry/NEXUS/actions/runs/43615282210).
- [x] Pass 13 suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 total).
- [ ] Continue to treat Python-only success as reference-oracle evidence, not cross-language, persistence, egress or live-readiness proof.


## Post-sync verification record

- [x] Exact normalized HEAD `9e9035033da77d958601cb6b69128e13e2551a0d` passed workflow [#43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737): 13 suites / 239 tests on each Python 3.11/3.12/3.13 runtime (717 executions).
- [x] No Node.js 20 or punycode deprecation warnings in the three job logs.
- [ ] Rust/DB/COSE/Egress/venue conformance remain separate future gates; this matrix does not cover them.

## Stacked integration chain and exact-head regression

- [x] Verify direct PR chain #1→#2→#3→#4→#5→#6→#7→#9→#10→#11→#12→#13→#14→#16 by exact base/head SHA equality.
- [x] Identify #8 as a parallel branch from #7, not a dependency of #16.
- [x] Confirm PR #16 correctly targets PR #14's head and all chain PRs remain Draft/open/unmerged.
- [x] Verify `9e9035033da77d958601cb6b69128e13e2551a0d` on [workflow #43615373737](https://github.com/PandaGarry/NEXUS/actions/runs/43615373737): 13 suites / 239 tests on Python 3.11/3.12/3.13 (717 executions).
- [ ] Integrate only parent-first after bounded review; PR #16 remains Draft.
- [ ] Keep the CI result scoped to Python reference models; it does not close Rust, database, egress or venue gates.

## CBOR / COSE library qualification — NX-RESEARCH-011

- [x] Compare Rust CBOR encoder/decoder and COSE structure candidates against the selected wire profile.
- [x] Record cbor2's canonical-encoder strengths and strict-ingress limitation.
- [x] Record cbor-core's draft/profile and unstable-API mismatch.
- [x] Record coset's alg=-19/original-protected-bytes/custom-crypto strengths and its maturity/dependency caveats.
- [x] Reject the cose2 built-in Ed25519 provider because it uses deprecated alg=-8; any future test requires a custom -19 signer/verifier.
- [ ] Build strict byte-level validator and cross-language positive/negative vectors.
- [ ] Complete exact-version provenance, license, SBOM, vulnerability, fuzz and resource-boundary review before any dependency adoption.

## CBOR command-key profile refinement

- [x] Restrict command map keys to fixed schema-defined ASCII names only.
- [x] Keep Unicode user text in values, with strict UTF-8 and no implicit normalization.
- [ ] Add negative vectors for non-ASCII keys, Unicode normalization lookalikes, duplicate keys and unknown field names in both language implementations.

## Exact-head CI after NX-RESEARCH-011

- [x] Branch HEAD `1bb2192e6746e0f86659f006ef204990adc81188` passed [workflow #43615753905](https://github.com/PandaGarry/NEXUS/actions/runs/43615753905).
- [x] Python 3.11/3.12/3.13 each passed 13 suites / 239 tests (717 successful executions).
- [x] No test failures or Node.js 20 / `punycode` deprecation warnings.
- [ ] Continue strict CBOR, COSE and dependency qualification separately; this workflow remains Python reference-only.

## Final action-runtime and exact-head regression

- [x] Verify exact HEAD `69657a0808b859b17ab94a6d3e008a2ae9671cc7` on workflow [#43615820603](https://github.com/PandaGarry/NEXUS/actions/runs/43615820603).
- [x] Pass 13 suites / 239 tests on each of Python 3.11, 3.12 and 3.13 (717 executions).
- [x] Confirm no test failures or Node.js 20 / `punycode` warnings.
- [x] Verify both direct pinned GitHub Actions manifests declare Node 24 at their exact pinned commit SHAs.
- [ ] Keep CI claims limited to Python reference models; CBOR/COSE, Rust, persistence, egress and venue qualification remain separate gates.

## COSE key-resolution conformance

- [x] Specify local-only bounded key lookup; token-supplied kid/issuer/audience are hints, never authority before signature verification.
- [x] Bind signed issuer/audience to local expected context after verification; forbid token-directed remote key retrieval.
- [x] Restrict verifier input to public Ed25519 key material and exact key/signature lengths.
- [ ] Add cross-language positive and adversarial COSE vectors for lookup ambiguity, remote key URL, claim mismatch, stale/revoked registry generation and private-key leakage.
- [ ] Qualify library behavior for protected-header byte preservation, duplicate headers and strict failure semantics.

## COSE_Sign1 exact-wire conformance

- [x] Define untagged four-element embedded-payload profile with alg=-19 and protected kid only.
- [x] Define empty unprotected map, canonical payload bstr and exact protected-header preservation.
- [x] Require RFC 9052 §9 deterministic Sig_structure and fixed external AAD.
- [ ] Add byte-exact cross-language signing/verifying vectors and negative profile tests.
- [ ] Prove parser behavior for duplicate labels, protected/unprotected collisions, detached payload, tags and extra parameters.

## COSE pre-verification key-resolution gate

- [x] Treat protected kid/alg and token issuer/audience as untrusted until verification succeeds.
- [x] Prohibit token-directed remote key retrieval; use a bounded local versioned registry.
- [x] Bind candidate lookup to locally expected issuer/audience/algorithm/purpose and check signed claims against that context after verification.
- [x] Require public OKP/Ed25519 key material only at Execution; keep private d material inside Risk; require 32-byte public key and 64-byte signature.
- [ ] Add cross-language vectors for wrong issuer/audience, key URL injection, ambiguous kid, stale/revoked key, malformed key/signature and private key exposure.
- [ ] Implement only after OD-08 security review and G0D/G1 dependency qualification.

## Exact-head CI after COSE key-resolution hardening

- [x] Verify `6fefd9a44ff2f272b6516265d10f41c46a13cf7a` on [workflow #43615911362](https://github.com/PandaGarry/NEXUS/actions/runs/43615911362).
- [x] Pass 13 suites / 239 tests on Python 3.11, 3.12 and 3.13 (717 executions).
- [ ] Keep this Python-only evidence separate from COSE/Rust/persistence/egress/venue qualification.

## Exact-head regression after COSE profile refinement

- [x] Verify `88fcb30068507d85fb35802ca5d2195fd528c000` on [workflow #43616054657](https://github.com/PandaGarry/NEXUS/actions/runs/43616054657).
- [x] Pass 13 suites / 239 tests on each Python 3.11/3.12/3.13 runtime (717 executions).
- [ ] Add and execute the actual cross-language COSE profile tests; current Python CI does not validate signature or key-registry behavior.

## COSE wire-profile exact-head regression

- [x] Verify `8d2c2f404782b718f1a3a422bb0ce918bb6b922d` on [workflow #43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308).
- [x] Pass 13 suites / 239 tests on each Python 3.11/3.12/3.13 runtime (717 executions).
- [ ] Keep COSE wire conformance, signer/verifier and key-registry tests as separate G0D/OD-08 implementation gates.

## Current COSE profile and stacked-PR verification

- [x] Freeze exact COSE_Sign1 application wire profile in NX-ADR-008 and NX-RESEARCH-011.
- [x] Verify PR #16 exact-head Python reference CI [#43616141308](https://github.com/PandaGarry/NEXUS/actions/runs/43616141308): 13 suites / 239 tests per Python 3.11/3.12/3.13 (717 executions).
- [x] Re-verify PR #1→#2→#3→#4→#5→#6→#7→#9→#10→#11→#12→#13→#14→#16 exact SHA ancestry; PR #8 is parallel.
- [x] Confirm direct-chain PRs remain open/Draft/unmerged; retain parent-first integration.
- [ ] Add byte-exact cross-language COSE vectors and strict profile rejection tests.
- [ ] Qualify exact crate versions, licenses, provenance, SBOM, advisories, fuzz behavior and key custody.
- [ ] Do not interpret Python reference CI as Rust, CBOR/COSE, PostgreSQL, Trusted Egress or live-safety evidence.

## Final exact-head regression after COSE wire-profile synchronization

- [x] Verify `71afa64c00affed017c1f072600f4f0e4aaeccc6` on [workflow #43616247630](https://github.com/PandaGarry/NEXUS/actions/runs/43616247630).
- [x] Pass 13 isolated suites / 239 tests on Python 3.11, 3.12 and 3.13 (717 executions).
- [x] Confirm no test failures or Node.js 20 / `punycode` warnings.
- [ ] Keep CBOR/COSE, Rust, persistence, egress and venue verification as independent implementation gates.

## Final synchronized PR #16 exact-head regression

- [x] Verify `3af0453897545b77fee358b9902a6301f662232e` on [workflow #43616348161](https://github.com/PandaGarry/NEXUS/actions/runs/43616348161).
- [x] Pass 13 suites / 239 tests on Python 3.11, 3.12 and 3.13 (717 executions).
- [x] Confirm no test failures or Node.js 20 / `punycode` deprecation warnings.
- [ ] Continue Rust, CBOR/COSE, persistence, egress and venue conformance as independent gates.

## PostgreSQL Risk reservation serialization conformance

- [x] Define shared Risk-owned scope-state serialization point for reservations and exposure projection updates.
- [x] Keep Ledger journal authority separate; Risk consumes Ledger/venue facts through idempotent inbox/projection transactions.
- [x] Specify deterministic multi-scope ordering, all-or-nothing reservation commit, stable idempotency and bounded full-transaction retries.
- [x] Specify fail-closed behavior for stale/incomplete evidence, missing scope state and ambiguous commit/primary authority.
- [ ] Implement a disposable G1 test harness only after G0D/OD-08/OD-09 acceptance; do not add production schema/runtime yet.
- [ ] Prove concurrent reservation and projection-update races, duplicate delivery, idempotency collisions, serialization/deadlock retry and ambiguous commit on the exact PostgreSQL patch.
- [ ] Prove service-role boundaries and recovery/backup/PITR plus old-primary fencing before any failover decision.

## Field-level data lineage and projection governance

- [x] Complete NX-ARCH-REVIEW-006 source-grounded inventory of fields in NX-IF-001..005 and NX-SEC-001.
- [x] Propose classification and owner boundaries for sensitive command, risk, execution, ledger, evidence, recovery and halt data.
- [x] Define future projection constraints for Analytics, Portfolio, Notifications, Strategy, Demo, Learning and Billing.
- [x] Identify missing Ledger journal-leg schema and prohibit inventing fields.
- [ ] Obtain source-owner/security acceptance for field-level classification and allowed projections.
- [ ] Author Ledger journal and Analytics/Portfolio projection contracts.
- [ ] Approve retention/deletion/legal basis, audit custody and declassification rules.
- [ ] Prove row/field isolation and source-lineage behavior with boundary-observed negative tests.

## Risk projection / reservation concurrency proof

- [x] Align ADR-008, IF-002, REF-EXEC-002 and OD-09 on the Risk-owned scope-state serialization point.
- [x] Require idempotent Risk projection ingestion for Ledger/venue/external exposure updates; no cross-service writes to Risk state.
- [x] Require deterministic all-scope ordering, atomic account/child reservations and fail-closed missing/stale source evidence.
- [x] Add negative/concurrency tests for projection/reservation races, duplicate/reordered events, idempotency collisions, 40001/40P01, ambiguous commit and missing scope state.
- [ ] Execute on exact PostgreSQL 18 patch with service-role separation, fault injection and observed lock/retry behavior.
- [ ] Prove backup/restore/PITR, old-primary fencing and recovery before any failover selection.
- [ ] Keep PostgreSQL as G1 evaluation target only until proof and security/operational review complete.
- [ ] Prove a lost response while the original transaction remains in flight cannot create a second reservation; same-identity/digest retry is arbitrated by the unique constraint, and unresolved outcome keeps the scope HALTED.

## Risk scope serialization and PostgreSQL concurrency — NX-ARCH-REVIEW-007

- [x] Refine common Risk-owned scope-state serialization for reservation and projection updates.
- [x] Require atomic updates to every affected parent/account and child scope row.
- [x] Version and serialize scope hierarchy/configuration changes.
- [x] Specify logical state-version fields and precise 40001/40P01/23505 behavior.
- [x] Define concurrency/fault-injection matrix and exact PostgreSQL 18 evidence sources.
- [ ] Implement exact-version concurrency tests, role separation and failure injection.
- [ ] Benchmark scope contention/fan-out without weakening atomicity.
- [ ] Prove source watermark completeness, failover, backup/restore and external fencing before G1.

## Exact-head regression after NX-ARCH-REVIEW-007

- [x] Verify `e7c5461ae7ccea4f29fc77461db91d44566aba36` on [workflow #43616908979](https://github.com/PandaGarry/NEXUS/actions/runs/43616908979).
- [x] Pass 13 suites / 239 tests on Python 3.11, 3.12 and 3.13 (717 executions).
- [ ] Keep PostgreSQL concurrency, transaction isolation, failover and egress-fencing evidence separate from Python reference CI.

## Numeric-wire cross-runtime resource parity

- [x] Fix the Python reference parser's integer digit budget at 512 digits, independent of interpreter defaults.
- [x] Cover the 512/513 digit boundary for decimal and rational wire encodings.
- [ ] Encode the same 512-digit acceptance / 513-digit rejection boundary in language-neutral vectors.
- [ ] Require Rust implementation to return the same stable NUMERIC.RESOURCE_LIMIT class.
- [ ] Reassess the bound only as part of an explicit production numeric profile; do not treat it as a trading or financial limit.
## Risk root-scope configuration guard and valuation snapshots

- [x] Include account/root scope-state in every v1 reservation/projection transaction and recheck root scope_config_version after locking all scopes.
- [x] Bind reservation/capability to immutable market/index/FX/fee/collateral input versions and source freshness evidence.
- [x] Keep market-data ticks out of the serialized scope-state write path; stale or invalid valuation snapshots block dispatch.
- [ ] Add concurrency tests for scope membership change racing reservation and for valuation-input changes between reservation and dispatch.
- [ ] Prove exact version-vector lineage, source freshness and dispatch-time invalidation in the G1 harness.

## Valuation-input snapshot race qualification

- [x] Define immutable source-owned valuation snapshots and version-vector binding.
- [x] Keep per-tick market-data updates outside the Risk scope-state serialization write path.
- [x] Require dispatch-time Trusted Egress revalidation and fail-closed behavior on stale/unconfigured/drift-invalid inputs.
- [ ] Specify the source-owner snapshot-vector contract and cross-source coherence evidence.
- [ ] Add reservation/approval/dispatch race tests for changed, stale, missing and contradictory valuation inputs.
- [ ] Select no numeric thresholds until source/domain evidence and owner policy exist.

## PostgreSQL 18.7 G1 patch qualification

- [x] Select PostgreSQL 18.7 as the exact G1 evaluation patch, based on current supported-release status.
- [x] Review official release notes and record index/REINDEX, incremental-backup, C-extension and privilege/extension caveats.
- [ ] Pin and verify package checksum/image digest, provenance, platform and configuration.
- [ ] Run fresh-full-backup restore/PITR, crash recovery and index integrity checks.
- [ ] Run transaction/concurrency and role-separation tests on the exact patch.
- [ ] Requalify latest supported 18.x minor before any deployment decision; 18.7 is not a permanent production pin.

## Persisted valuation evidence manifest at Trusted Egress

- [x] Define immutable ValuationInputVector and bind its exact ID/version through ExposureSnapshot, RiskReservation and RiskApprovalCapability.
- [x] Require Trusted Egress to read persisted Risk evidence manifest and consumed source watermark/correction status.
- [x] Keep source service calls and replacement market/FX/fee/collateral fetches off the dispatch path.
- [x] Deny send when manifest is missing, stale, incomplete, has watermark gaps or cannot prove admissibility.
- [ ] Define ingestion lag/correction invalidation objective and measurement.
- [ ] Add race/fault tests for source updates and corrections between approval and send.

## Trusted Egress authorization linearization

- [x] Define a single-use attempt-bound EgressBoundaryAuthorization over manifest/reservation/halt/eligibility/fence versions.
- [x] Define final-gate commit as the send-authorization linearization point.
- [x] Require immediate socket-write initiation and no DB transaction across network I/O.
- [ ] Test update-before-gate vs update-after-gate ordering for valuation correction, halt and venue eligibility.
- [ ] Inject crash after final authorization commit but before socket write; recover as potentially sent and reconcile.
- [ ] Inject crash during/after socket write; verify no blind retry and inspect actual instrumented egress boundary.

## Risk approval / COSE / valuation-manifest conformance

- [x] Synchronize NX-IF-001 with exact COSE_Sign1 profile and immutable valuation_input_vector_id/version.
- [x] Require local bounded key resolution; reject token-directed remote key discovery and ambiguous candidates.
- [x] Require persisted Risk evidence-manifest validation at Egress with no remote source calls.
- [ ] Run cross-language COSE positive/negative byte vectors after G0D readiness.
- [ ] Test manifest missing/stale/gap/correction/revocation and source-update races between approval and dispatch.
- [ ] Prove private-key isolation and Egress no-fetch behavior at instrumented process/network boundaries.

## PostgreSQL 18.7 G1 patch qualification

- [x] Select 18.7 as the exact G1 evaluation patch, not a production deployment version.
- [x] Review official release notes for security fixes, index-corruption/REINDEX and incremental-backup caveats.
- [x] Require fresh full backup as the G1 backup/PITR base; do not trust pre-18.7 incremental backup chains.
- [x] Prohibit extensions, C extensions, dblink and replication subscriptions in the initial G1 harness.
- [x] Require base-table service roles; RLS/updatable views are not sole authorization boundaries; runtime has no DDL/extension/superuser/replication privileges.
- [ ] Pin exact vendor package/image digest, build provenance, host platform and configuration.
- [ ] Review each 18.7 REINDEX item against actual schema/indexes and prove restore/PITR.
- [ ] Requalify the newest supported 18.x patch before any later deployment decision.

## Exact-head CI after G1 architecture qualification

- [x] Verify PR #16 HEAD `7fb396df5f3e700adf0ad151c446e38930fdadb0` on workflow #43617605777.
- [x] Pass 13 suites / 239 tests on Python 3.11–3.13 (717 successful executions).
- [x] Inspect logs for failures and deprecated Node.js runtime warnings; none found.
- [ ] Maintain separate proof gates for Rust, CBOR/COSE, PostgreSQL 18.7, Trusted Egress, fencing and venue behavior.

## PostgreSQL 18.7 / valuation-vector exact-head CI reference

- [x] Correctly record tested SHA `7fb396df5f3e700adf0ad151c446e38930fdadb0` and workflow [#43617626344](https://github.com/PandaGarry/NEXUS/actions/runs/43617626344).
- [x] Confirm 13 suites / 239 tests per Python runtime (717 executions).
- [ ] Keep database, valuation-manifest and egress tests separate from Python reference regression.

## NX-IF-004 cross-contract conformance

- [x] Bind RiskApprovalCapability to both StateEvidenceVector and ValuationInputVector.
- [x] Assign final evidence compatibility check to Trusted Egress's attempt-scoped send gate.
- [x] Reference NX-ADR-008's selected G1 CBOR/SHA-256/COSE Ed25519 profile.
- [ ] Add tests for dual evidence-vector invalidation and egress ordering.
- [ ] Qualify cryptographic libraries and key custody independently before implementation.

## WP-D valuation evidence and dispatch compatibility

- [x] Separate StateEvidenceVector from ValuationInputVector and bind both into RiskApprovalCapability.
- [x] Require persisted Risk evidence-manifest validation of the exact signed valuation vector at Trusted Egress.
- [x] Prohibit remote source calls and valuation substitution on the dispatch path; fail closed on missing/unverifiable manifest.
- [ ] Prove immutable source snapshots, cross-source vector coherence, watermark/correction continuity and source-specific freshness.
- [ ] Instrument Trusted Egress and network policy to prove no market/FX/fee/collateral fetch occurs at send time.
- [ ] Test market-data tick changes, source corrections/revocations and stale manifests between approval and dispatch.

## Halt / final-egress linearization proof

- [x] Define one serialization point shared by authoritative halt-epoch changes and final EgressBoundaryAuthorization.
- [x] Specify halt-first and gate-first outcomes, including paused-process semantics.
- [x] Require Egress drain/fence proof before acknowledging a newer halt epoch.
- [ ] Fault-inject halt-first, gate-first, process pause after gate, crash, partition, sender fence and halt acknowledgement.
- [ ] Verify no stale sender can initiate a socket write after full halt acknowledgement at the instrumented transport boundary.
- [ ] Confirm whether the stronger no-socket-initiation-after-halt-commit requirement is required; do not claim it from DB ordering alone.

## Halt / final Egress gate ordering

- [x] Serialize halt epoch transition and final EgressBoundaryAuthorization on the same authoritative halt-state generation.
- [x] Define halt-wins and gate-wins outcomes, including retained reservation and reconciliation.
- [x] Require drain or positive sender fencing before acknowledging a newer halt epoch.
- [x] Distinguish Risk application outage from authoritative halt-store outage; Egress denies if final gate cannot commit.
- [ ] Fault-inject paused Egress, halt/gate races, crash after gate commit, control-store loss and host/network fencing failure.
- [ ] Prove the guarantee at the instrumented socket boundary; do not overclaim wall-clock no-bytes-after-halt.

## Halt / Egress adversarial conformance cases

- [x] Add IF-005 cases 36–42 for halt/gate ordering, paused process, fence outage, halt-store outage, late venue acceptance and socket-boundary proof.
- [ ] Implement test harness for halt-before-gate and gate-before-halt with durable state inspection.
- [ ] Pause Egress after gate commit; prove no halt acknowledgement until socket initiation or positive sender fencing.
- [ ] Inject control-store outage and verify final gate denies.
- [ ] Verify late venue acceptance of a pre-acknowledgement initiated request remains reconciled.
- [ ] Prove no stale/queued socket initiation after halt acknowledgement using actual instrumented egress boundary.

## Halt / final Egress authorization linearization

- [x] Serialize halt-epoch and final EgressBoundaryAuthorization commits against the same authoritative halt-state record/generation.
- [x] Define gate-first attempts as in-flight and non-revocable; retain reservation and reconcile.
- [x] Block HALTED acknowledgement while a paused gate-committed sender could still initiate a socket write.
- [x] Add crash/conformance cases for halt-first, gate-first, pause-before-write, unavailable control store, positive fence failure and late venue acceptance.
- [ ] Test both transaction lock orders and actual socket initiation at the real Egress boundary.
- [ ] Prove external process/host/network fencing and post-ack no-new-send property under pause, partition and crash.

## Halt / Egress race evidence

- [x] Add explicit race matrix cases 36–42 to NX-IF-005.
- [x] Align acceptance criteria with the final egress authorization linearization point and distinguish Risk outage from halt-store outage.
- [x] Verify code/test HEAD `f1c0bd0576bd42058ca2482706533248bcf6069b` on workflow #43618694545: 255 tests/runtime, 765 executions; 24 egress-fencing tests including 16 HaltEgressGate cases.
- [ ] Re-run CI after any further final documentation/code synchronization.
- [ ] Implement only after G0D/G1 gates: instrumented halt/Egress race tests, actual socket boundary, external process/host/network fencing and recovery evidence.

## Signing authority separation

- [x] Separate Risk approval signing key authority from venue request-signing/credential authority.
- [x] Require distinct keys, workload identities and policies; prohibit key reuse.
- [x] Keep Risk private key out of Execution/Trusted Egress; keep venue secrets out of Risk signer.
- [ ] Prove negative access paths and compromised-workload containment.
- [ ] Qualify key custody, HSM/KMS, rotation, revocation and recovery before implementation.

## Exact-head CI after halt / signing authority clarification

- [x] Verify PR #16 HEAD `dbfba513b86a79b8b6574a80c1beb136b28836c7` on workflow #43618114058.
- [x] Pass 13 suites / 239 tests on Python 3.11–3.13 (717 successful executions).
- [x] Inspect logs for failures and deprecated Node.js runtime warnings; none found.
- [ ] Continue separate implementation gates for signing, halt store, egress fencing, PostgreSQL 18.7 and Rust conformance.

## Halt / final Egress reference oracle

- [x] Add test-only sequential state-machine model for halt/gate commit ordering.
- [x] Cover halt-first, gate-first, paused process, positive sender fence, control-store outage and post-send reconciliation.
- [x] Verify 11 new tests on Python 3.11/3.12/3.13 at exact PR HEAD (250 tests/runtime, 750 total; workflow #43618215618).
- [ ] Replace model assumptions with actual PostgreSQL shared-row/conditional-update proof and instrumented socket-boundary fault injection.
- [ ] Prove external process/host/network fencing independently of the old Egress workload.

## HEGC logical authority and grant idempotency

- [x] Assign HaltState / EgressBoundaryAuthorization sole-write ownership to HEGC, separate from Risk, Command and credential-owning Egress.
- [x] Keep HEGC free of venue credentials/socket and Risk signing key; restrict Egress from direct control-record writes.
- [x] Define least-privilege HEGC access to source records and control-owned schema.
- [x] Define idempotent grant issuance/recovery by stable attempt ID.
- [ ] Implement durable schema/unique constraints and exact retry/changed-binding behavior.
- [ ] Test ambiguous grant response, HEGC restart, paused Egress, duplicate attempts and sender fencing.
- [ ] Prove no untrusted workload can write HEGC control records or mint grants.

## HEGC trust-boundary qualification

- [x] Classify HEGC as critical control-plane authority with no Risk private key or venue credentials/socket.
- [x] Require Egress to independently verify RiskApprovalCapability and exact command/reservation/evidence bindings in addition to the HEGC grant.
- [ ] Test compromised HEGC cannot mint Risk approvals, bypass missing/invalid Risk signature, access venue credentials or open a venue socket.
- [ ] Test compromised Egress cannot write HaltState or mint grants; test no other workload can write HEGC control schema.
- [ ] Complete independent security review of HEGC identity, service role, audit, recovery and software supply chain.

## HEGC control authority and halt-gate conformance

- [x] Define HEGC as sole writer of HaltState/EgressBoundaryAuthorization; no venue credentials, socket or Risk signing key.
- [x] Restrict Egress to one-use HEGC grants; no direct control-state writes.
- [x] Specify one-active-instance PostgreSQL 18.7 evaluation topology and fail-closed outage.
- [x] Add reference-model tests for pending halt, in-flight grant, store recovery, sender fence, repeated request and epoch exhaustion.
- [ ] Implement disposable HEGC/DB test harness only after G0D/OD-12 acceptance.
- [ ] Prove actual socket boundary reporting, role separation, grant replay prevention and positive process/host/network fencing.
- [ ] Prove halt acknowledgement cannot precede resolution/isolation of every gate-committed attempt.

## Sender-fence outcome preservation

- [x] Treat positive sender fencing as prevention of future writes only.
- [x] Keep an attempt OUTCOME_UNKNOWN and reservation held when no trusted socket-initiation report exists.
- [x] Prohibit DEFINITELY_NOT_SENT classification or reservation release from fence evidence alone.
- [x] Verify the expanded 16-test HaltEgressGate oracle on Python 3.11/3.12/3.13 (included in 29 egress-fencing tests; 255 total tests/runtime, 765 executions; workflow #43618694545).
- [ ] Prove initiation reports, external fence attestation and venue reconciliation at the real Egress boundary.


## Sender-fence semantic correction and exact-head reference CI

- [x] Preserve OUTCOME_UNKNOWN after a positive sender fence when no trusted socket-initiation evidence exists; retain reservation and reconciliation obligation.
- [x] Extend the HaltEgressGate oracle to 16 cases, including pending-halt/store recovery, repeated halt idempotency and epoch exhaustion.
- [x] Pass exact code/test HEAD `f1c0bd0576bd42058ca2482706533248bcf6069b` on workflow #43618694545: 13 suites / 255 tests on each of Python 3.11, 3.12 and 3.13.
- [ ] Prove the same properties with real PostgreSQL concurrency, independent process/host/network fencing and instrumented socket initiation.

- [x] Verify halt/Egress gate reference-model code SHA `f1c0bd0576bd42058ca2482706533248bcf6069b` on workflow [#43618694545](https://github.com/PandaGarry/NEXUS/actions/runs/43618694545): 255 tests on each of Python 3.11/3.12/3.13 (765 executions).
- [ ] Replace sequential oracle assumptions with actual concurrent PostgreSQL/HEGC tests and instrumented socket/network boundary evidence.

## HEGC / halt-gate current reference verification

- [x] Verify SHA `9b88eabb80e44510e29013fe02315c354c4b488b` on workflow #43618875958.
- [x] Pass 257 tests per Python 3.11/3.12/3.13 runtime (771 executions); egress-fencing package 31 tests / 18 HaltEgressGate cases.
- [x] Inspect all three logs for failures and deprecated action runtimes; none found.
- [ ] Re-run exact-head CI after the signed-64-bit epoch-exhaustion grant-denial guard.
- [ ] Prove the HEGC SERIALIZABLE read/write protocol with all gate-critical writers and actual socket-boundary fencing.

## HaltEgressGate 18-case hardening and code/test CI

- [x] Fix duplicate halt requests during store outage so an already committed HALTING/HALTED epoch is not downgraded.
- [x] Assert sender-fenced attempts retain reservations and remain OUTCOME_UNKNOWN without trusted socket-initiation evidence.
- [x] Add two regressions for duplicate halt requests during store outage (HALTING and HALTED).
- [x] Pass exact code/test HEAD `2e94edd73f8933f0d510eed940452316ec5b8832` on workflow #43618796109: 257 tests/runtime on Python 3.11/3.12/3.13 (771 executions).
- [x] Verify 31 egress-fencing tests (13 authority-handover + 18 HaltEgressGate).
- [ ] Re-run CI after final documentation synchronization; current PR head is docs-only beyond the tested code/test SHA.
- [ ] Prove the same semantics with real PostgreSQL concurrent transactions, HEGC grant persistence, instrumented sockets and independently verified sender fencing.

- [x] Specify durable `ConsumeEgressGrant` transition and single-use GATE_COMMITTED → GRANT_CONSUMED state.
- [x] Deny send on lost/indeterminate consume response; no new attempt or second permit.
- [x] Require reservation retention, sender fencing and reconciliation when consume committed but socket initiation is unconfirmed.
- [ ] Prove grant replay prevention and lost-response semantics against the real HEGC/PostgreSQL transaction boundary.


## HEGC one-use grant consumption and commit-order proof

- [x] Add explicit GATE_COMMITTED → GRANT_CONSUMED → SOCKET_INITIATED test-only state transitions; only positive consume permits one socket attempt.
- [x] Cover lost consume response, repeated consumption, consume-store outage, sender fencing and reconciliation without blind resend.
- [x] Historical code/test HEAD 9d618131ac9951e23c589491b2fb1039f6dc1d86 passed workflow #43619080626: 13 suites / 260 tests on Python 3.11–3.13 (780 executions); egress-fencing 34 tests / 21 HaltEgressGate cases.
- [ ] Prove PostgreSQL SERIALIZABLE participation plus an enforced common per-scope generation/guard that provides the required commit-order property; SSI alone is not treated as strict serializability.
- [ ] Prove idempotent durable grant status resolution, process incarnation fencing, socket-initiation evidence and recovery against a real PostgreSQL 18.7 harness.


## Duplicate-halt cause preservation and latest reference CI

- [x] Preserve the initiating halt reason for the full active halt episode; duplicate requests are idempotent and do not overwrite the cause.
- [x] Test duplicate halt requests during HALTING and HALT_PENDING.
- [x] Pass exact code/test HEAD fedc4879fee5ed97f03dea094c3d5f3fb6aaf7c8 on workflow #43619194630: 13 suites / 262 tests on each of Python 3.11, 3.12 and 3.13 (786 executions).
- [x] Confirm egress-fencing package 36 tests / 23 HaltEgressGate cases.
- [ ] Prove the common per-scope commit-order guard, HEGC grant status recovery and actual process/socket fencing with PostgreSQL 18.7 integration tests.

## PostgreSQL SSI / HEGC commit-order barrier

- [x] Record that SSI serialization order is not necessarily commit order for overlapping transactions.
- [x] Separate Risk aggregate guard from HEGC gate-validation guard.
- [x] Require guard acquisition as first SQL statement before protected reads/writes; hold through commit and retry stale snapshots.
- [x] Record least-privilege coordination function candidate; no direct-DML/advisory-lock bypass.
- [ ] Prove writer-first and HEGC-first order on PostgreSQL 18.7 using multiple concurrent connections.
- [ ] Test every invalidating writer, stale-snapshot retry, process pause/crash, ambiguous commit and multi-scope ordering.
- [ ] Verify database privileges prevent any unguarded source mutation.

## HEGC guard entrypoint enforcement

- [x] Record that a guard function alone cannot enforce call ordering if callers can pre-read protected state.
- [x] Require a single HEGC transaction entrypoint or a DB-enforced first-statement transaction API.
- [x] Restrict all invalidating source writers to guarded procedures; revoke direct DML/advisory-lock bypass.
- [ ] Test caller pre-read, direct DML bypass, search_path spoofing, overload/temp-object attacks and function privilege escalation.
- [ ] Prove guard wait/retry and commit ordering on PostgreSQL 18.7.


## Idempotent HEGC grant issuance and binding-conflict conformance

- [x] Add a stable binding digest to each test-only attempt grant.
- [x] Exact same attempt ID + epoch + digest returns the original persisted attempt object, including after the halt epoch advances; no new grant is minted.
- [x] Changed digest or changed epoch for the same attempt ID is a hard conflict.
- [x] Pass exact code/test HEAD c2350f7807587e0428b760890f6fdba09ba60f60 on workflow #43619636403: 13 suites / 263 tests on Python 3.11–3.13 (789 executions); egress-fencing 37 tests / 24 HaltEgressGate cases.
- [ ] Prove canonical digest construction includes every authorization binding and authenticated Egress workload/process identity.
- [ ] Prove durable database uniqueness, ambiguous commit lookup and same-attempt retry under concurrent HEGC requests.
- [ ] Prove first-statement guard entrypoint and per-scope commit-order semantics against PostgreSQL 18.7.


## HEGC grant idempotency and database-enforced guard entrypoint

- [x] Bind attempt ID to immutable authorization digest in the reference oracle.
- [x] Exact retry returns the original attempt record even after halt epoch advances; changed digest or epoch conflicts without replacement grant.
- [x] Pass exact code/test HEAD `c2350f7807587e0428b760890f6fdba09ba60f60` on workflow #43619636403: 13 suites / 263 tests per Python 3.11–3.13 runtime (789 executions), egress-fencing 37 tests / HaltEgressGate 24.
- [x] Separate internal scope-guard helper from HEGC gate transaction entrypoint; service role must not have direct source SELECT or guard/grant DML.
- [x] Record SECURITY DEFINER identity constraints: dedicated authenticated session_user, no shared login/SET ROLE spoofing, explicit scope authorization.
- [ ] Prove the first-operation guard acquisition, complete scope-set derivation, entrypoint privilege closure, all guarded source writers, stale-snapshot retry and both commit orders on PostgreSQL 18.7.
