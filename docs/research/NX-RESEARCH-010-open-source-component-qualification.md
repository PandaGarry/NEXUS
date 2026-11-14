# NX-RESEARCH-010 — Open-Source Component Qualification for NEXUS

**Date:** 2026-11-14  
**Status:** RESEARCH / CANDIDATES ONLY — no dependency or runtime integration approved  
**Scope:** Qualify external components that may reduce engineering risk without transferring NEXUS-owned financial, risk or execution authority.  
**Baseline reviewed:** `f92004d8337ec770e485ff307f23a35f674252a5`.  
**Method:** Official repository/documentation review against NX-ARCH-001/002, NX-REF-EXEC-002, NX-SEC-001, NX-OWNER-DECISIONS-001 and readiness gates. Not a full source audit, binary verification, penetration test, legal opinion or benchmark.

## 1. Executive disposition

NEXUS should reuse mature infrastructure where it is a replaceable implementation detail, while keeping the authoritative trading state machine and capital-protection decisions inside NEXUS-owned contracts.

**Shortlist**
1. **PostgreSQL — leading persistence candidate for G1 evaluation only**, subject to OD-09 transaction/concurrency proof and restore tests. Not selected or added.
2. **OpenTelemetry Collector — preferred observability candidate**, once runtime services exist. Telemetry must be allowlisted/redacted and never carry credentials, signed payloads or unrestricted account data.
3. **OpenBao — secrets-management candidate**, subject to threat/deployment review and MPL-2.0 obligations. Do not introduce until signer/Egress deployment boundaries are specified.
4. **NATS JetStream — optional asynchronous fan-out/replay transport**, not a source of truth for reservations, command acceptance, outbox or Ledger journal. Defer until measured requirements justify another durable subsystem.
5. **Cilium — network-enforcement candidate only if Kubernetes is chosen.** It does not itself prove old-host termination or revoke credentials already held by a stale process.
6. **NautilusTrader — existing research candidate only.** NX-RESEARCH-008 rejects RC9 as autonomous execution authority; at most test-only replay/adapter compatibility pending a stable release and fresh audit.

**Defer / not preferred now:** Temporal as primary order lifecycle coordinator; HashiCorp Vault as default secrets product; Kubernetes/Cilium as default deployment; Kafka/Redpanda or multiple overlapping brokers. These add operational surface before a measured need exists.

## 2. Qualification rules

Every candidate must pass before becoming a dependency:
- Record exact upstream repository, immutable tag/commit and release artifacts.
- Review exact license for pinned version and all transitive dependencies.
- Assess maintainer activity, security policy/advisories, supported release line and upgrade policy.
- Define SBOM, vulnerability scan, provenance/signature verification and reproducible build.
- Document narrow adapter/interface boundary and replacement plan.
- Test relevant failures: restart, partition, duplicate delivery, lost acknowledgement, stale worker, backup/restore and resource exhaustion.
- Never grant authority because a component is popular or widely deployed.
- Pin dependencies; automated updates may open review PRs but may not silently change runtime versions.
- Keep production secrets out of untrusted CI, pull-request jobs, ordinary workers and observability pipelines.

## 3. Candidate matrix

| Component | Potential use | Evidence / license | Main concern / gate | Disposition |
|---|---|---|---|---|
| PostgreSQL | Risk reservations, command/outbox, Ledger journal, durable metadata | Official relational database; PostgreSQL License is permissive, similar to BSD/MIT | OD-09: prove isolation/locking/CAS, all-scope atomicity, failover, PITR and crash recovery | **Leading candidate; evaluate only** |
| OpenTelemetry Collector | Metrics, traces and logs | Official collector repository; Apache-2.0 | Redaction, cardinality/resource limits, trace integrity; telemetry outage must not block safety | **Preferred observability candidate; defer deployment** |
| OpenBao | Secrets, certificates, encryption and key-management boundary | Identity-based secrets/encryption manager; GitHub lists MPL-2.0 | File-level license obligations; HA, unseal/recovery, audit and signer integration need security design | **Candidate; not integrated** |
| NATS + JetStream | Durable asynchronous distribution, replay, consumers | NATS server Apache-2.0; streams/consumers provide persistence, replay and at-least-once delivery | Duplicates/redelivery and ACK races; retention/limits need policy. Never replace transactional outbox or Ledger | **Optional later** |
| Cilium | Identity-aware network policy/egress in Kubernetes | Apache-2.0 user-space components; BPF templates dual GPL-2.0/BSD-2-Clause | Kubernetes/Linux dependency; network policy is not proof of process/host termination or secret revocation | **Conditional only** |
| NautilusTrader | Replay, simulation, adapter compatibility | Existing NX-RESEARCH-006..008; v2.0.0rc9 is pre-release; inspected snapshot LGPL-3.0 | RC9 has non-universal Risk routing and does not satisfy NEXUS transactional outbox; stable release and license/dependency audit needed | **Test-only candidate** |
| Temporal | Durable orchestration of long-running operational workflows | Upstream server repository MIT | Workflow replay does not make external venue side effects exactly-once; order lifecycle must remain NEXUS domain transactions | **Defer; possibly ops workflows only** |
| HashiCorp Vault | Secrets/key-management boundary | Current repository LICENSE states BSL 1.1 with version-specific Additional Use Grant | Version-specific production-use terms require review; do not assume older MPL licensing applies | **Not preferred default; compare OpenBao/KMS** |

## 4. Recommended first controlled stack — proposed, not selected

- Evaluate PostgreSQL for service-owned durable records. Risk and Command must have separate schemas/roles and separate local transactions; no shared application superuser.
- No message broker initially. Use transactional outbox/inbox and bounded polling until measured load justifies NATS.
- Define OpenTelemetry instrumentation and redaction contracts first; deploy Collector only after runtime services exist.
- Keep secrets provider abstracted. Compare OpenBao with managed KMS/HSM only after deployment threat model is stable.
- Do not require Kubernetes. A simple isolated host/process topology may be easier to prove for a single-owner first deployment.
- Keep NautilusTrader outside the trusted execution path; no direct strategy-to-venue dispatch and no authority over Risk, outbox, Ledger or egress.

This is an evaluation baseline, not an accepted OD-09/10/12 decision and not permission to create a production runtime.

## 5. Non-delegable NEXUS authority

No external module may own or override:
- Risk policy, approval capability, reservation accounting or halt authority;
- canonical command identity, idempotency, outbox attempt state or outcome classification;
- canonical Ledger journal, fill identity, reconciliation barrier or account exposure;
- final venue-send authorization, credentials or socket except the specifically reviewed NEXUS Trusted Egress boundary;
- owner-controlled risk limits, emergency governance or live authorization.

A broker ACK is not a venue ACK. A database commit is not proof an order was sent. A venue HTTP response is not proof of a fill. A tracing span is not an audit ledger.

## 6. Integration gates

| Gate | Work | Exit evidence |
|---|---|---|
| G0D dependency governance | Immutable pins, license register, SBOM, provenance and vulnerability scanning | Reviewable policy and CI checks |
| G1 persistence | Evaluate PostgreSQL against reservation/outbox/Ledger invariants | Concurrency, crash, ambiguous commit, backup/restore and isolation tests on exact pinned version |
| G1 observability | Define OpenTelemetry schema and redaction | Secret/payload leakage tests, bounded cardinality, telemetry outage isolation |
| G1/G2 secrets | Compare OpenBao/managed KMS/HSM against Egress threat model | Threat review, key lifecycle, audit, recovery and revocation evidence |
| G2 messaging | Add NATS only if measured requirements justify fan-out/replay | Duplicate/replay/idempotency/retention/backpressure/failure tests |
| Deployment | Evaluate Cilium only after deployment target chosen | Network bypass and stale-egress fencing tests at actual enforcement point |
| Nautilus compatibility | Revisit on stable release or new integration boundary | Exact source/tag, provenance, license/dependency inventory and non-bypassable NEXUS gateway proof |

## 7. Evidence sources

- PostgreSQL license: https://www.postgresql.org/about/licence/
- PostgreSQL current releases: https://www.postgresql.org/
- OpenTelemetry Collector: https://github.com/open-telemetry/opentelemetry-collector
- Collector Apache-2.0 license: https://github.com/open-telemetry/opentelemetry-collector/blob/main/LICENSE
- NATS server: https://github.com/nats-io/nats-server
- JetStream persistence/replay: https://docs.nats.io/concepts/jetstream
- JetStream consumer acknowledgement/redelivery: https://docs.nats.io/nats-concepts/jetstream/consumers
- OpenBao: https://github.com/openbao/openbao
- Cilium: https://github.com/cilium/cilium
- Temporal: https://github.com/temporalio/temporal
- HashiCorp Vault current license: https://github.com/hashicorp/vault/blob/main/LICENSE
- NautilusTrader v2.0.0rc9: https://github.com/nautechsystems/nautilus_trader/releases/tag/v2.0.0rc9
- Existing NEXUS Nautilus audits: NX-RESEARCH-006/007/008.

Upstream status and licenses can change. Re-check the exact pinned version and transitive graph before adoption. This memo is a shortlist, not a legal opinion or source-level qualification.

## 8. Fresh official-documentation cross-check — 2026-11-14

This follow-up checks the candidate shortlist against current upstream documentation. It refines evaluation constraints; it does not select or integrate any component.

### PostgreSQL transaction semantics

- PostgreSQL 18 documents that SERIALIZABLE transactions can be aborted with `serialization_failure` when concurrent read/write dependencies cannot be serialized. A future NEXUS implementation must retry the **entire bounded transaction** from a fresh snapshot, with a finite retry budget and idempotent caller semantics; retrying only the failed statement is not sufficient.
- PostgreSQL advisory locks are application-defined and the database does not enforce that all writers use them. They cannot be the sole correctness mechanism for reservations or capability consumption.
- Row/table locks and serializable isolation still do not fence a stale process from an external venue socket. Database correctness and external-send authority are separate proofs.

### NATS JetStream delivery semantics

- JetStream consumers normally provide at-least-once delivery through acknowledgement tracking and redelivery.
- Its documented exactly-once mode combines publication deduplication IDs with double acknowledgements over a configured deduplication window. This is a broker-level message guarantee, not exactly-once execution of arbitrary external side effects.
- NEXUS must retain durable idempotency, outbox/inbox state, reconciliation and trusted-egress fencing even if JetStream is adopted. Broker ACK must never be treated as venue acceptance or fill evidence.

### OpenTelemetry data minimization

- OpenTelemetry explicitly places responsibility for identifying sensitive data on the implementer. Attribute/filter/redaction/transform processors are defense-in-depth, not a substitute for preventing sensitive values from entering telemetry.
- NEXUS instrumentation should use allowlisted attributes and bounded-cardinality labels at source; never emit credentials, signatures, canonical order payloads or unrestricted financial/account records. Telemetry outage must not block Risk, halt or execution safety.

### OpenBao audit boundary

- OpenBao audit devices log API requests/responses, but its documented non-audited paths include initialization, seal/unseal, health/leader and Raft bootstrap/join operations; optional unauthenticated metrics/profiling paths also require review.
- Multiple audit devices can provide redundant copies, but deployment must separately protect audit sink integrity, availability, access and recovery. "Audit enabled" alone is not a complete control.

### Current source references

- PostgreSQL 18 transaction isolation: https://www.postgresql.org/docs/current/sql-set-transaction.html
- PostgreSQL explicit/advisory locking: https://www.postgresql.org/docs/current/explicit-locking.html
- NATS JetStream delivery and replay: https://docs.nats.io/concepts/jetstream
- NATS JetStream delivery/acknowledgement model: https://docs.nats.io/learn/jetstream/
- OpenTelemetry sensitive-data handling: https://opentelemetry.io/docs/security/handling-sensitive-data/
- OpenTelemetry Collector security: https://opentelemetry.io/docs/security/
- OpenBao audit devices: https://openbao.org/docs/audit/

**Disposition unchanged:** PostgreSQL, OpenTelemetry Collector, OpenBao and NATS JetStream remain candidates only. No runtime dependency, database, broker, secret manager or deployment topology is selected or installed. Exact versions, licenses, security advisories, transitive dependencies and deployment threat model must be requalified at adoption time.
