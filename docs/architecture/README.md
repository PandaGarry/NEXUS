# Архитектура и ADR

Каждый ADR содержит статус, контекст, решение, альтернативы, последствия, риски, миграцию и acceptance criteria.

| ID | Название | Статус |
|---|---|---|
| [NX-ADR-001](NX-ADR-001-unified-market-event-contract.md) | Unified Market Event Contract | Proposed |
| [NX-ADR-002](NX-ADR-002-execution-integrity-reconciliation.md) | Execution Integrity & Reconciliation | Proposed — reservation-before-approval and single-use approval/outbox commit ordering harmonized with NX-IF-001/002 |
| [NX-ADR-003](NX-ADR-003-simulation-fidelity-strategy-validation.md) | Simulation Fidelity & Strategy Validation | Proposed |
| [NX-ADR-004](NX-ADR-004-market-data-recovery-state-machine.md) | Market Data Recovery State Machine | Proposed |
| [NX-ADR-005](NX-ADR-005-instrument-specification-exact-arithmetic.md) | Instrument Specification & Exact Arithmetic | Proposed |
| NX-ADR-006 | Strategy Validation / Research Governance | Deferred — covered by NX-ADR-003 unless a distinct governance decision emerges |
| [NX-ADR-007](NX-ADR-007-venue-eligibility-jurisdictional-activation-gate.md) | Venue Eligibility & Jurisdictional Activation Gate | Proposed — cross-document review complete; owner/legal review and conformance evidence required |
| [NX-REF-VENUE-001](NX-REF-VENUE-001-venue-eligibility-evidence-reference-model.md) | Venue Eligibility Evidence Reference Model | Test-only reference; no production authorization |
| [NX-REF-VENUE-002](NX-REF-VENUE-002-eligibility-egress-fencing-reference-model.md) | Eligibility Egress Fencing Reference Model | Test-only single-process race model; no production fencing |
| [NX-SEC-001](../security/NX-SEC-001-threat-model-credential-isolation.md) | Threat Model / Credential Isolation | Proposed |
| [NX-ARCH-001](NX-ARCH-001-target-architecture.md) | Target Architecture & Deployment Topology | Proposed |
| [NX-ARCH-003](NX-ARCH-003-domain-kernel-numeric-model.md) | Domain Kernel & Exact Numeric Model | Proposed |
| [NX-ARCH-006](NX-ARCH-006-modular-product-boundaries-and-trust-isolation.md) | Modular Product Boundaries, Extension Contracts & Trust Isolation | Proposed — design only; no runtime module or public registration approved |\n| [NX-ARCH-007](NX-ARCH-007-platform-extensibility-and-entitlements.md) | Platform Extensibility, Product Capabilities & Entitlement Model | Proposed — strategic design only; no commercial or entitlement runtime approved |\n| [NX-ARCH-008](NX-ARCH-008-module-registry-admission-capability-governance.md) | Module Registry, Admission & Capability Governance | Proposed — design only; no executable registry, module runtime or grants approved |

## Architecture reviews and foundation design
- [NX-PROJECT-CHECKLIST-001 — Project Execution and Evidence Checklist](../quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md) — Active living checklist with G0D D1–D8 status, engineering workstreams, evidence requirements and explicit non-authorizations.
- [NX-ARCH-REVIEW-001 — Cross-Specification Contract Review](NX-ARCH-REVIEW-001-cross-specification-contract-review.md) — Proposed; design findings and closure work packages.
- [NX-DOC-REVIEW-001 — Foundation Documentation Final Review](../quality/NX-DOC-REVIEW-001-foundation-documentation-final-review.md) — In progress; integration and G0 documentation blockers.

## Reference platform research
- [NX-RESEARCH-006 — Reference Platform Fit Assessment](../research/NX-RESEARCH-006-reference-platform-fit-assessment.md) — In progress; NautilusTrader is a leading candidate, not selected; NEXUS risk, durable outbox, ledger and recovery boundaries remain independently owned.

## Executable reference slices
- [NX-REF-DOMAIN-001 — Instrument Specification Reference Model](NX-REF-DOMAIN-001-instrument-specification-reference-model.md) — Test-only immutable metadata snapshot and exact tick/lot/minimum-rule validator; not a production registry or order authority.
- [NX-REF-DOMAIN-002 — Instrument Registry Reference Model](NX-REF-DOMAIN-002-instrument-registry-reference-model.md) — Test-only append-only in-memory history, version conflict detection and effective-time ordering; no persistence or distributed authority.

## Interface contracts
- [NX-IF-001 — Canonical Trade Command & Risk Approval Contract](NX-IF-001-canonical-trade-command-risk-approval-contract.md) — Proposed; WP-A design artifact, not accepted or implemented.
- [NX-IF-002 — Exposure Snapshot & Risk Reservation Contract](NX-IF-002-exposure-snapshot-risk-reservation-contract.md) — Proposed; WP-B design artifact, not accepted or implemented.
- [NX-IF-003 — Execution Event & Ledger Posting Contract](NX-IF-003-execution-event-ledger-posting-contract.md) — Proposed; WP-C design artifact for canonical fills, durable inbox/outbox, atomic journal posting, corrections and projection watermark handoff; not accepted or implemented.
- [NX-IF-004 — State Evidence, Freshness & Recovery Barrier Contract](NX-IF-004-state-evidence-freshness-recovery-barrier-contract.md) — Proposed; WP-D design artifact for per-source evidence vectors, freshness policy, quarantine, scoped recovery cases and restart/reconciliation barriers; not accepted or implemented.
- [NX-IF-005 — Emergency Operations, Halt & Risk-Reduction Authorization Contract](NX-IF-005-emergency-operations-halt-risk-reduction-contract.md) — Proposed; WP-E design artifact for monotonic scoped halts, operation-class authorization, bounded emergency plans, protective-order handling and controlled resume; not accepted or implemented.
- [NX-ARCH-REVIEW-001 — Cross-Specification Contract Review](NX-ARCH-REVIEW-001-cross-specification-contract-review.md) — Proposed; WP-A..WP-E design drafts published; owner decisions and conformance evidence remain open.
- [NX-OWNER-DECISIONS-001 — Critical Owner Decision Register](NX-OWNER-DECISIONS-001-critical-owner-decision-register.md) — Proposed register; OD-01/04 accepted, OD-15 partially accepted; remaining decisions open/deferred by gate.

ADR, подготовленные в обсуждении, не считаются опубликованными или принятыми до появления полного документа в репозитории и review. Interface contracts также требуют owner/security review и conformance evidence.

- [NX-REF-EXEC-001 — Command Gateway Reference Conformance Slice](NX-REF-EXEC-001-command-gateway-reference-conformance.md) — Experimental Python/SQLite reference model; includes explicit stale-worker split-brain counterexample; fake adapter only; not production implementation.
- [NX-REF-EXEC-002 — Dispatcher Authority Transfer and Egress Fencing](NX-REF-EXEC-002-dispatcher-authority-transfer-egress-fencing.md) — Proposed design with recommended Risk/Command/Egress transaction decomposition, takeover fencing protocol and crash-point fault-injection matrix; no production database, network fence or credential boundary is selected or implemented.

- [NX-REF-DOMAIN-003 — Dimensional Financial Types Reference Model](NX-REF-DOMAIN-003-dimensional-financial-types-reference-model.md) — test-only exact-decimal value types; production integration remains blocked.

- [NX-REF-DOMAIN-004 — Instrument Quantity Unit Semantics](NX-REF-DOMAIN-004-instrument-quantity-unit-semantics.md) — explicit version-pinned unit mapping for spot, linear and conventional inverse contracts; inverse base exposure is represented exactly by NX-REF-DOMAIN-006; QUANTO remains unsupported.

- [NX-REF-DOMAIN-005 — Exact Rational Division & Explicit Quantization](NX-REF-DOMAIN-005-exact-rational-division-and-quantization.md) — reduced rational intermediate results and explicit rounding modes; test-only.

- [NX-REF-DOMAIN-006 — Inverse Contract Rational Exposure](NX-REF-DOMAIN-006-inverse-contract-rational-exposure.md) — inverse quote notional divided by price yields an exact rational base exposure; no implicit rounding.

- [NX-REF-DOMAIN-007 — Bounded Exact Numeric Context](NX-REF-DOMAIN-007-bounded-exact-numeric-context.md) — test-only caller-configured limits and preflight checks; no production profile selected.
- [NX-REF-DOMAIN-008 — Canonical Numeric Wire Encoding v1](NX-REF-DOMAIN-008-canonical-numeric-wire-encoding.md) — versioned scalar decimal/rational encodings with strict canonical parsing.

- [NX-REF-DOMAIN-009 — Operation-Specific Financial Rounding & Valuation Contract](NX-REF-DOMAIN-009-operation-specific-financial-rounding-valuation-contract.md) — Proposed design contract; enumerates rounding/valuation boundaries for tick/lot, fees, funding, P&L, margin, liquidation, FX and Ledger; venue/owner qualification remains blocked.

- [NX-REF-DOMAIN-010 — Venue-Neutral Financial Math Golden Fixtures](NX-REF-DOMAIN-010-venue-neutral-financial-math-golden-fixtures.md) — Test-only hand-derived dimensional identities for spot, explicitly mapped linear/inverse contract arithmetic and partial-fill weighted-average math; non-authorizing and not venue/account qualification.

- [NX-ARCH-004 — Rust Execution & Cross-Language Conformance Boundary](NX-ARCH-004-rust-execution-cross-language-conformance.md) — Proposed; defines candidate Rust domain/execution boundaries, adapter trust limits and egress requirements. Documentation only; no Rust workspace or production implementation.
- [NX-ARCH-005 — Language-Neutral Conformance Fixture & Runner Contract](NX-ARCH-005-language-neutral-conformance-fixture-and-runner.md) — Proposed; defines a common fixture envelope, stable rejection classes, deterministic runner protocol, versioning and CI evidence. No runner or Rust implementation added.


**2026-11-14 review note:** NX-ARCH-REVIEW-001 records the clarification that the IF-002 durable pre-egress attempt marker precedes any network side effect and is not evidence of transmission. See the review note and current IF-002 lifecycle table for the aligned wording.


### Persistence and egress decision analysis (2026-11-14)

See [NX-REF-EXEC-002 §4.5](NX-REF-EXEC-002-dispatcher-authority-transfer-egress-fencing.md) for the proposed option matrix. Current candidate: Risk reservation and Command acceptance use separate service-owned local ACID transactions; no distributed transaction is assumed. A single account-scoped Egress Authority owns credentials and the actual venue socket; workers have no direct venue route. Authority takeover requires positive external fencing of the previous workload/host, not lease expiry. OD-08/09/10/12 remain open; no provider or concrete mechanism has been selected.


### Modular product boundaries proposal (2026-11-14)

See [NX-ARCH-006](NX-ARCH-006-modular-product-boundaries-and-trust-isolation.md). The proposal defines bounded product domains, versioned contracts, deny-by-default module admission, workload identities, least-privilege capabilities, hard Demo/live separation, and a low-privilege Learning/Wiki domain. Modular monolith / limited trust-domain separation is preferred initially; arbitrary in-process plugin loading is not approved. Design only; no technology or deployment topology selected.

### Platform extensibility and commercial entitlements (2026-11-14)

See [NX-ARCH-007](NX-ARCH-007-platform-extensibility-and-entitlements.md). Defines the future product-domain portfolio, stable feature identifiers, entitlement lifecycle, quota model, contract compatibility, multi-tenancy readiness gates and the strict separation between product availability, commercial entitlement and security authorization. No plans, prices, payment provider, public SaaS or tenant runtime are selected.
\n\n### Module registry and admission governance (2026-11-14)\n\nSee [NX-ARCH-008](NX-ARCH-008-module-registry-admission-capability-governance.md). Defines immutable module/artifact identity, registry-controlled lifecycle, trust tiers, manifest declarations versus independently issued grants, request-time authorization, proposed data-access matrix, dependency/contract rules, revocation and 20 adversarial qualification scenarios. Design only; no executable registry, permission service, sandbox or runtime is selected or implemented.\n