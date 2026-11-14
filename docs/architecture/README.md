# Архитектура и ADR

Каждый ADR содержит статус, контекст, решение, альтернативы, последствия, риски, миграцию и acceptance criteria.

| ID | Название | Статус |
|---|---|---|
| [NX-ADR-001](NX-ADR-001-unified-market-event-contract.md) | Unified Market Event Contract | Proposed |
| [NX-ADR-002](NX-ADR-002-execution-integrity-reconciliation.md) | Execution Integrity & Reconciliation | Proposed |
| [NX-ADR-003](NX-ADR-003-simulation-fidelity-strategy-validation.md) | Simulation Fidelity & Strategy Validation | Proposed |
| [NX-ADR-004](NX-ADR-004-market-data-recovery-state-machine.md) | Market Data Recovery State Machine | Proposed |
| [NX-ADR-005](NX-ADR-005-instrument-specification-exact-arithmetic.md) | Instrument Specification & Exact Arithmetic | Proposed |
| NX-ADR-006 | Strategy Validation / Research Governance | Deferred — covered by NX-ADR-003 unless a distinct governance decision emerges |
| [NX-SEC-001](../security/NX-SEC-001-threat-model-credential-isolation.md) | Threat Model / Credential Isolation | Proposed |
| [NX-ARCH-001](NX-ARCH-001-target-architecture.md) | Target Architecture & Deployment Topology | Proposed |
| [NX-ARCH-003](NX-ARCH-003-domain-kernel-numeric-model.md) | Domain Kernel & Exact Numeric Model | Proposed |

## Architecture reviews and foundation design
- [NX-PROJECT-CHECKLIST-001 — Project Execution and Evidence Checklist](../quality/NX-PROJECT-CHECKLIST-001-execution-and-evidence.md) — Active living checklist with G0D D1–D8 status, engineering workstreams, evidence requirements and explicit non-authorizations.
- [NX-ARCH-REVIEW-001 — Cross-Specification Contract Review](NX-ARCH-REVIEW-001-cross-specification-contract-review.md) — Proposed; design findings and closure work packages.
- [NX-DOC-REVIEW-001 — Foundation Documentation Final Review](../quality/NX-DOC-REVIEW-001-foundation-documentation-final-review.md) — In progress; integration and G0 documentation blockers.

## Reference platform research
- [NX-RESEARCH-006 — Reference Platform Fit Assessment](../research/NX-RESEARCH-006-reference-platform-fit-assessment.md) — In progress; NautilusTrader is a leading candidate, not selected; NEXUS risk, durable outbox, ledger and recovery boundaries remain independently owned.

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
- [NX-REF-EXEC-002 — Dispatcher Authority Transfer and Egress Fencing](NX-REF-EXEC-002-dispatcher-authority-transfer-egress-fencing.md) — Proposed design for account-scoped authority transfer, independently enforced egress revocation, stale-state mutation rejection and fail-closed recovery.
