# NX-IF-003 — Execution Event & Ledger Posting Contract

**Date:** 2026-11-14  
**Status:** PROPOSED — normative interface draft; not accepted  
**Work package:** NX-ARCH-REVIEW-001 / WP-C  
**Applies to:** ТЗ-NX-004, ТЗ-NX-005, ТЗ-NX-006, NX-ADR-002, NX-ADR-005, NX-IF-002, NX-ARCH-001  
**Design baseline:** `docs/wp-b-exposure-reservations`, commit `7a44dccf33222f1487832bb6fee0b8b7cd492ce5`

## 1. Purpose and scope

Define the durable handoff from authoritative execution facts to financial accounting and derived portfolio state.

The contract separates four independently observable milestones:

1. an execution fact is received and authenticated from a venue/source;
2. Execution validates, normalizes, deduplicates and durably commits the fact;
3. Ledger consumes that committed fact and atomically commits its accounting journal transaction;
4. Ledger projections apply the posting and publish a projection watermark that Risk can consume.

These milestones MUST NOT be collapsed into a single generic "fill processed" status.

This contract defines:
- source authority and ownership boundaries;
- canonical execution-event identity and evidence;
- durable Execution outbox → Ledger inbox delivery;
- immutable, balanced and idempotent Ledger posting;
- partial fill, fee, correction and bust semantics;
- projection watermark and WP-B exposure transfer;
- replay, reconciliation, crash recovery and conformance requirements.

Out of scope:
- venue-specific REST/WebSocket payload schemas and authentication;
- final chart of accounts, accounting policy and tax treatment;
- choice of database, message broker, RPC, serialization or cryptographic algorithms;
- detailed instrument valuation/FX hierarchy;
- live trading authorization or permission to move assets.

## 2. Normative language and system invariants

The terms MUST, MUST NOT, SHOULD and MAY are normative.

1. **Execution owns execution facts.** It is authoritative for normalized venue order lifecycle, fills/executions, native execution identifiers, execution corrections/bust evidence and the raw source evidence it received.
2. **Ledger owns accounting facts.** It is authoritative for posted journal transactions, balances, position/cost-basis projections, realized P&L postings and accounting classifications.
3. A venue order acknowledgement MUST NOT create a fill, position quantity or trade journal posting.
4. One order MAY produce zero, one or many fills. Each fill is an independent economic execution fact; order ID is not a fill ID.
5. Execution event persistence and Ledger posting are separate durable commits. No distributed atomic transaction is assumed between the services.
6. Delivery from Execution to Ledger is at-least-once. Ledger effects MUST be idempotent; the system MUST NOT claim exactly-once transport or exactly-once behavior across a venue boundary.
7. An event MUST NOT be acknowledged as consumed until its inbox identity and complete balanced journal transaction are durably committed in one Ledger transaction.
8. A fill remains in WP-B `FILL_PENDING_LEDGER` until the matching Ledger posting and required position projection watermark are visible and reconciled.
9. Duplicate, late, reordered, corrected or busted events MUST NOT silently duplicate, erase or rewrite historical execution facts or journal postings.
10. Corrections MUST append linked compensating events/postings; original evidence and postings remain immutable.
11. Financial values MUST use exact decimal/fixed-point/integer representations under the immutable instrument and currency specifications. Binary floating-point MUST NOT be canonical for price, quantity, fee, balance, margin or P&L.
12. Unknown identity, currency, instrument specification, multiplier, fee sign, event ordering or accounting classification MUST remain UNKNOWN and be quarantined; it MUST NOT be guessed or coerced to zero.
13. A Ledger projection is not healthy merely because its database transaction committed. Required source watermarks, projection offsets and reconciliation state MUST also be satisfied.
14. Risk Engine remains the sole authority for exposure aggregation and authorization. Neither Execution nor Ledger may mint Risk approvals or release reservations by assumption.

## 3. Authority boundaries and lifecycle

### 3.1 Ownership matrix

| Fact/state | Authoritative owner | Contract boundary |
|---|---|---|
| Raw venue order/fill/fee payload and retrieval metadata | Adapter evidence store, retained by Execution or immutable evidence store | Preserve raw bytes/reference, digest, endpoint/channel, adapter version and retrieval context |
| Normalized order lifecycle and venue order identifiers | Execution | Does not imply financial posting |
| Normalized fill/execution fact and native execution identity | Execution | Immutable fact with correction lineage |
| Execution-to-Ledger delivery state | Execution outbox + Ledger inbox | Delivery metadata, not accounting truth |
| Journal transaction, debit/credit postings and posting-rule version | Ledger | Immutable accounting record |
| Balances, positions, cost basis and realized accounting projections | Ledger | Rebuildable projections derived from journal and versioned reference data |
| Risk reservation and ExposureSnapshot bucket | Risk Engine | Consumes Execution/Ledger source facts; does not rewrite them |
| Venue account/balance/position/fill reconciliation evidence | Venue adapter/reconciliation subsystem | Evidence compared with NEXUS facts; not permission to overwrite journal history |

Execution MUST NOT publish a Ledger balance as authoritative. Ledger MUST NOT infer a fill from order state, client intent, acknowledgement or an unverified UI event. Risk MUST NOT treat an Execution fill as a confirmed Ledger position before the Ledger posting/projection handoff is complete.

### 3.2 Distinct processing milestones

For each execution event, expose separate state/evidence for:

- `RECEIVED`: raw source message or reconciliation record accepted into the adapter boundary;
- `VALIDATION_PENDING`: schema, identity, instrument and source checks are in progress;
- `QUARANTINED`: material ambiguity or invalidity prevents normal processing;
- `NORMALIZED`: canonical event constructed with exact values and provenance;
- `EXECUTION_COMMITTED`: immutable event and deduplication identity durably committed by Execution;
- `LEDGER_DELIVERY_PENDING`: committed event is available in the durable outbox;
- `LEDGER_DELIVERED`: delivery attempt reached Ledger; this alone does not prove posting;
- `LEDGER_POSTING_COMMITTED`: Ledger inbox and journal transaction committed atomically;
- `PROJECTION_PENDING`: required position/balance read models have not applied the journal watermark;
- `PROJECTION_APPLIED`: relevant projections report the posting watermark;
- `RECONCILED`: applicable venue/account reconciliation evidence is complete through the required watermark;
- `RECONCILIATION_REQUIRED`: discrepancy, gap or unresolved dependency remains.

These are event-processing milestones, not a replacement for the separate order lifecycle in NX-ADR-002. Terminal order state and fill processing state MUST remain independently queryable.

## 4. Canonical ExecutionEvent v1

### 4.1 Required envelope

Every normalized execution fact sent to Ledger MUST carry:

| Field | Requirement |
|---|---|
| `schema_name`, `schema_version` | Explicit contract version; unknown major versions reject/quarantine |
| `event_id` | Immutable NEXUS event ID |
| `event_type` | TRADE_FILL, FEE, FEE_ADJUSTMENT, TRADE_CORRECTION, TRADE_BUST, or explicitly defined supported type |
| `execution_id` | Stable canonical identity for one economic execution; not the order ID |
| `venue`, `environment`, `account_id`, `subaccount_id` | Fully scoped identity; account namespace MUST be explicit |
| `market_type`, `native_instrument_id`, `internal_instrument_id` | Instrument identity |
| `instrument_spec_version` | Immutable NX-ADR-005 spec version used for exact interpretation |
| `venue_order_id`, `client_order_id` | Optional only where venue does not provide them; absence is explicit |
| `venue_execution_id`, `venue_trade_id` | Native IDs, preserved separately and with documented namespace |
| `side`, `position_side` | Explicit side semantics; UNKNOWN is not defaulted |
| `price`, `quantity`, `contract_count`, `multiplier` | Exact decimal strings or integer ticks/lots; fields applicable to the instrument model |
| `price_currency`, `quantity_unit`, `settlement_currency` | Explicit units/currencies |
| `fee_amount`, `fee_currency`, `fee_sign_convention`, `liquidity_role` | Fee may be absent only as explicitly UNKNOWN/not-yet-reported; maker/taker may be UNKNOWN |
| `exchange_event_time`, `received_at`, `processed_at` | Distinct timestamps with explicit clock/source semantics |
| `source_channel`, `source_sequence`, `source_cursor`, `connection_generation` | Source ordering evidence; absent sequence remains absent, never fabricated |
| `source_payload_digest`, `raw_evidence_ref`, `adapter_version` | Provenance and replay evidence |
| `correction_of`, `correction_version`, `effective_time` | Required for correction/bust events; original event remains linked |
| `strategy_lineage`, `command_id`, `risk_approval_id`, `reservation_id` | Optional lineage; external/manual events remain explicitly unattributed |
| `normalization_version`, `deduplication_scope`, `quality` | Reproducible adapter semantics and identity confidence |

A field may be inapplicable only where the instrument/event schema says so. Missing required values MUST be represented as UNKNOWN with a reason and cannot be used to post an unbounded financial effect.

### 4.2 Identity and deduplication

The canonical event identity MUST be scoped by at least venue, environment, account/subaccount, market type, instrument and the venue-documented native execution identifier namespace.

- Native order IDs and execution IDs MUST be stored separately.
- A venue execution ID that is only unique per symbol, day, account or endpoint MUST include that namespace.
- If the venue has no stable execution ID, an adapter MAY construct a versioned composite identity only from fields whose uniqueness semantics are documented and tested. The event MUST carry reduced identity confidence and the exact composite recipe/version.
- Price + quantity + timestamp alone MUST NOT be assumed unique.
- If two plausible records collide or cannot be distinguished, quarantine them; do not silently collapse them.
- The same economic execution discovered through WebSocket, REST history and account reconciliation MUST converge to one canonical execution lineage while retaining all source observations.
- Reuse of a canonical identity with different immutable economic fields is an identity conflict and MUST create a reconciliation case, not overwrite the original.

### 4.3 Corrections and ordering

A correction/bust is a new event with its own event ID, a reference to the original execution/event and an explicit correction version/reason/source evidence. It MUST NOT mutate the original fill.

The system MUST preserve both:
- **effective time** — when the economic event is stated to apply;
- **knowledge/record time** — when NEXUS received and committed the information.

Out-of-order corrections remain pending until their dependency is available or are quarantined under a bounded policy. A correction received before the original MUST NOT be applied as an unlinked free-standing negative fill. Reprocessing the same correction is idempotent.

Source sequence/cursor ordering is scoped to the venue stream and connection generation. A sequence gap or incomplete history window marks completeness UNKNOWN and is handled by the freshness/recovery contract (WP-D); event timestamps alone do not prove gap-free ordering.

## 5. Durable Execution outbox → Ledger inbox

### 5.1 Execution commit boundary

Execution MUST commit the following in one local durable transaction:
1. normalized immutable execution event;
2. canonical deduplication identity and identity-conflict outcome;
3. raw evidence reference/digest and source provenance;
4. correlation lineage to order/command where known;
5. durable outbox record for Ledger delivery;
6. local event sequence/commit watermark.

If the outbox is stored separately, the implementation MUST provide an equivalent atomic commit guarantee; a best-effort dual write is forbidden.

An event MUST NOT be published to Ledger before this transaction commits. If the process crashes after commit, the outbox worker MUST resume delivery after restart.

### 5.2 Delivery protocol

- Outbox delivery is at-least-once and retryable with bounded backoff and observability.
- Each delivery carries immutable `event_id`, `execution_id`, schema version, payload digest and source lineage.
- Ledger MUST persist an inbox receipt keyed by the canonical event identity and validate the payload digest.
- Re-delivery with the same identity and same digest returns the prior committed outcome without a second posting.
- Same identity with a different digest is an integrity conflict and MUST be quarantined.
- An acknowledgement is returned only after Ledger has committed either (a) the complete journal posting and inbox outcome, or (b) a durable quarantine/rejection outcome.
- Transient failures MUST leave the outbox pending. Permanent schema/identity/accounting failures MUST become visible quarantine outcomes, not disappear from the queue.
- Outbox delivery status MUST NOT be interpreted as Ledger posting status.

### 5.3 Ledger atomic posting boundary

For an accepted financial event, Ledger MUST commit in one database transaction:
1. unique inbox identity + payload digest;
2. journal transaction identity and posting-rule version;
3. every debit/credit leg required for that economic event;
4. balance invariant checks for the configured accounting model;
5. link from source event/execution ID to journal transaction;
6. projection work item or durable journal watermark from which projections can resume;
7. durable consumer outcome/acknowledgement state.

No partial journal batch may be visible. If any leg fails validation or the transaction is unbalanced, the entire posting transaction MUST roll back and the event MUST remain pending or enter durable quarantine. A retry after a successful commit MUST return the existing posting identity.

The journal MUST reject unknown currencies, unsupported account mappings, precision overflow, invalid sign conventions and missing required instrument semantics. It MUST NOT invent balancing legs to make an invalid event appear balanced. Suspense accounts MAY be used only under an explicitly approved posting policy with bounded exposure and a visible unresolved classification; they are not a generic sink for unknown values.

### 5.4 Delivery guarantee and semantics

The target is at-least-once event delivery with idempotent accounting effects and durable replay. It is not a claim of globally exactly-once processing. Correctness is established by immutable identities, atomic local transactions, idempotent consumers, watermarks and reconciliation evidence.

## 6. Accounting and instrument semantics

### 6.1 Fill and fee separation

A fill and its fee are related but distinct financial facts:
- A trade fill records executed quantity/price and updates the position/cost-basis subledger according to the versioned instrument/accounting model.
- A fee or rebate records a separate cash/asset liability effect in its actual fee currency, with exact sign and source semantics.
- A venue may include fee fields on a fill response or report fees in a separate account transaction. The adapter MUST normalize the source relationship and prevent both paths from posting the same fee twice.
- Fee-not-yet-reported is UNKNOWN/pending, not zero. A later fee event is posted independently and linked to the fill.
- Fee adjustments/rebates are new linked events. They do not mutate the original fee posting.
- Maker/taker role is only assigned when source evidence or a validated venue rule supports it.

### 6.2 Instrument model

Posting rules MUST be selected by immutable instrument spec and account/position mode, not by symbol-name heuristics.

The accounting model MUST explicitly handle supported cases:
- spot base/quote asset exchange;
- linear contracts with contract multiplier and settlement currency;
- inverse contracts where P&L and notional depend on the documented inverse formula;
- quanto or other contract models only after explicit formula/version certification;
- net-position and hedge-mode accounting, including split close/open quantity where a netting fill crosses through zero.

The event MUST preserve exact contract count, quantity unit, multiplier, price and relevant currencies. Missing contract value, multiplier, settlement currency, lot precision or position mode MUST block posting of affected economic effects and trigger quarantine/reconciliation. Do not use a fallback multiplier of 1 or assume all symbols are linear USDT contracts.

### 6.3 P&L boundaries

- Realized P&L is posted only under a versioned instrument-specific accounting rule and authoritative close/settlement evidence.
- Unrealized P&L is a valuation projection, not a realized cash posting.
- If a venue reports both trade-level realized P&L and a separate account cash-flow event, the posting policy MUST select the authoritative representation and cross-link the other as corroborating evidence; it MUST NOT double-count.
- Funding, borrow interest, liquidation fees, settlement, transfers and rebates are separate event classes with explicit source, currency, sign and posting rules. This contract does not define their complete schemas; unsupported classes remain outside the certified scope.
- FX translation and portfolio valuation are governed by a separate versioned valuation policy. An unknown FX rate MUST NOT be replaced with 1.

## 7. Corrections, busts and compensating journal transactions

1. Original Execution events and Ledger journal transactions are immutable.
2. A correction/bust creates a new execution event linked to the original identity and source evidence.
3. Ledger creates a compensating journal transaction referencing the original posting and correction event. It does not delete, edit or reuse the original posting ID.
4. A replacement/corrected economic value, if supported by source evidence, is posted as a separate linked transaction after the reversal/adjustment policy is validated.
5. Correction ordering is deterministic using correction lineage/version and explicit effective/knowledge times; ambiguous competing corrections are quarantined.
6. Replaying the original plus correction stream MUST produce the same journal/projection result and retain the full audit history.
7. A bust that changes position or exposure MUST trigger a new Ledger projection watermark and Risk ExposureSnapshot version; affected approvals/reservations are re-evaluated under WP-B.
8. A late correction after a reservation or exposure bucket was released MUST restore the relevant conservative exposure and trigger a reconciliation incident where required.

## 8. WP-B exposure transfer and Risk consumption

The following handoff is normative across NX-IF-002 and this contract:

| Stage | WP-B bucket/state | Release/transfer condition |
|---|---|---|
| Venue fill observed and committed by Execution | `FILL_PENDING_LEDGER` | Fill identity and exact quantity are durably committed in Execution |
| Ledger journal transaction committed, projection pending | `FILL_PENDING_LEDGER` | Do not move yet; journal commit alone may not make position read model available |
| Ledger position projection applied through matching journal watermark | Candidate `CONFIRMED_POSITION` | Matching fill lineage, exact instrument/account scope and projection watermark are visible |
| Reconciliation incomplete or source gap unresolved | `FILL_PENDING_LEDGER` or `UNKNOWN_EXPOSURE` | Retain conservative exposure and apply policy halt/block |
| Ledger posting corrected/busted | New exposure version from compensating evidence | Recompute; never erase prior bucket history |

Risk Engine MUST verify the event/execution lineage, journal transaction ID, Ledger projection version/watermark and required reconciliation quality before transferring the filled quantity. The transfer MUST be atomic within the Risk exposure snapshot update so the same quantity is neither omitted nor represented in both pending and confirmed buckets.

The unfilled order remainder remains in `WORKING_ORDER_REMAINDER` until authoritative final order/fill reconciliation proves it is no longer executable. Fee/margin reservations remain governed by WP-B and approved policy; posting a fill does not implicitly release all related reserves.

## 9. Reconciliation and completeness

Execution and Ledger reconciliation are continuous, scoped and evidence-bearing.

At minimum compare:
- venue execution history vs normalized Execution events;
- private stream sequence/cursor vs REST overlap windows and pagination completeness;
- venue fee/account transaction history vs fee journal postings;
- venue balances and positions vs Ledger journal-derived projections;
- venue order cumulative filled quantity vs sum of unique normalized fills;
- correction/bust history vs compensating journal transactions.

Every reconciliation run records account/instrument scope, query parameters, time window, cursor/page boundaries, source response digest, adapter version, retrieval time, source watermark, completeness status and discrepancies.

- A partial page, retention boundary, missing cursor, sequence gap or stale snapshot MUST NOT be treated as complete history.
- Discrepancies MUST be categorized and quarantined with an owner/action state.
- Repair MUST use newly ingested authoritative evidence and compensating events/postings; never rewrite historical journal rows to match a venue snapshot.
- External/manual fills are ingested as external execution facts, remain unattributed to a NEXUS strategy, and enter the same Ledger controls. If identity or completeness is unknown, quarantine and conservatively block the affected scope.
- Risk receives reconciliation quality/watermarks alongside financial projections; a stale or incomplete ledger blocks risk-increasing activity where policy requires completeness.

## 10. Crash, retry and fault behavior

| Failure point/scenario | Required behavior |
|---|---|
| Crash after raw receipt, before Execution commit | Re-fetch/replay source evidence; no event assumed committed |
| Crash after Execution event/outbox transaction | Outbox resumes; event is not lost |
| Crash after send, before Ledger response | Redeliver same immutable identity; Ledger inbox deduplicates |
| Ledger commits journal, crashes before ACK | Retry returns existing posting; no second journal transaction |
| Duplicate WebSocket + REST fill | One canonical execution; preserve both observations |
| Same ID, different economic payload | Integrity conflict; quarantine and halt affected scope as policy requires |
| Partial multi-leg journal failure | Entire journal transaction rolls back; no partial posting |
| Fee arrives after fill | Post fee separately when authoritative; pending fee state remains visible |
| Correction arrives before original | Hold/quarantine correction until original lineage is resolved |
| Duplicate/out-of-order corrections | Idempotent by correction identity/version; conflicts quarantined |
| Fill arrives after cancel acknowledgement | Preserve fill, reconcile final cumulative quantity; restore exposure if previously released |
| Missing sequence/history page | Mark source completeness UNKNOWN; reconcile overlap; do not mark healthy |
| Ledger projection lags journal | Keep WP-B bucket in FILL_PENDING_LEDGER |
| Restart with stale snapshot | Rebuild from journal watermark; no risk use until projection and reconciliation gates pass |
| Unknown multiplier/currency/fee sign | Quarantine; no guessed posting or zero substitution |
| Venue snapshot disagrees with journal | Preserve both truths; create discrepancy and compensating repair workflow |

## 11. Observability, audit and security

Record at minimum:
- event, execution, order, command, approval, reservation, journal transaction and correction IDs;
- venue/account/instrument scope and instrument spec version;
- raw evidence references/digests, source channel, adapter and normalization versions;
- exchange/receive/process/commit timestamps;
- source cursor/sequence, outbox attempt, inbox outcome and posting/projection watermarks;
- exact amounts, units, currencies, sign conventions and posting-rule version;
- deduplication/conflict/quarantine outcomes and reconciliation case;
- service identity, actor, reason code and immutable audit lineage.

Metrics include outbox age/retry count, inbox duplicate/conflict count, fill-to-posting lag, posting-to-projection lag, unposted fill quantity, pending fee age, correction backlog, journal imbalance rejects, reconciliation drift, source completeness, quarantine age and restore/replay divergence.

Execution and Ledger service identities MUST be least-privilege. Ledger has no exchange trading or withdrawal authority. AI and Strategy have no journal mutation authority. Raw evidence and journal integrity controls MUST be tamper-evident and access audited.

## 12. Conformance and acceptance criteria

The following tests are required before production use; none is claimed executed by this document.

1. One order with many partial fills creates one immutable execution record per unique fill and correct cumulative quantity.
2. The same fill from WebSocket, REST history and reconciliation creates one canonical execution lineage with all source observations retained.
3. Same native ID in different accounts/instruments does not collide; same scoped ID with different payload quarantines.
4. A venue without stable execution IDs uses only a documented, versioned composite identity; ambiguous collisions quarantine.
5. Execution event and outbox commit atomically; crash injection at every transaction boundary cannot lose a committed event.
6. Ledger inbox identity and all journal legs commit atomically; failed/unbalanced posting leaves no partial journal.
7. Duplicate delivery after Ledger commit but before acknowledgement produces no second posting.
8. Duplicate fee observations and separate fee endpoint events cannot double-post one economic fee.
9. Unknown fee currency/sign or missing fee evidence remains pending/UNKNOWN, not zero.
10. Spot, linear and inverse golden fixtures produce exact expected asset, liability, position and P&L effects under approved posting rules.
11. Unsupported quanto, margin mode or contract multiplier fails closed rather than using a guessed default.
12. Net-position crossing fills split closing and opening legs correctly; hedge-mode legs remain distinct.
13. Correction/bust produces compensating journal entries and deterministic replay while preserving original records.
14. Correction before original and conflicting correction versions are quarantined and recover deterministically.
15. Fill-to-Ledger projection watermark transfer moves exposure from FILL_PENDING_LEDGER to CONFIRMED_POSITION exactly once.
16. Ledger posting committed but projection delayed does not release pending exposure.
17. Late fill after cancel/release restores exposure and triggers required invalidation/halt.
18. Crash/restart at each outbox/inbox/posting/ack/projection boundary recovers without duplicate accounting effects.
19. Reconciliation detects missing fills, fees, cursor gaps, retention boundaries and position/balance discrepancies.
20. External/manual executions are accounted for without fabricated strategy attribution.
21. Same journal + event + spec + posting-rule versions replay to the same projection hash.
22. Audit lineage reconstructs source evidence → Execution event → Ledger posting → projection → Risk exposure transfer.

WP-C design exit criteria:
- ownership and state transitions are unambiguous across ТЗ-NX-004/005/006 and NX-IF-002;
- event identity, inbox/outbox and atomic posting semantics are defined;
- correction, fee and crash/replay behavior are specified;
- WP-B fill bucket handoff has an explicit Ledger watermark gate;
- all owner decisions and non-implemented evidence gaps are visible;
- cross-document review finds no contradictory authority or duplicate accounting path.

Passing this design review does not mean implementation, schema conformance, tests or runtime behavior are verified.

## 13. Owner decisions required

1. Initial venue/account-mode shortlist and whether initial certification is single venue/account.
2. Stable native execution-ID guarantees and fallback identity approval per selected venue.
3. Chart of accounts, journal schema, posting-rule versioning and balancing policy.
4. Fee/rebate timing, currency/sign normalization and fee-not-yet-reported handling.
5. Funding, borrow interest, liquidation, settlement, transfer and other account-event schemas/order.
6. Exact precision/rounding rules per currency, instrument and posting leg; treatment of residual dust.
7. Net vs hedge mode and supported spot/linear/inverse/quanto scope for first certification.
8. Correction/bust precedence, retention and effective-time restatement policy.
9. Transactional store/event log/inbox-outbox technology and recovery objectives.
10. Source sequence/cursor completeness and maximum lag/watermark requirements per venue/account mode.
11. External/manual execution policy and operator reconciliation authority.
12. Approved FX/valuation policy and which realized-P&L source is authoritative when venue reports multiple representations.

Until these decisions are approved, unsupported instruments, event types and account modes remain PARTIAL/UNKNOWN and cannot be marked reconciled or production-ready.

## 14. Dependencies and related contracts

- [NX-IF-001 — Canonical Trade Command & Risk Approval Contract](NX-IF-001-canonical-trade-command-risk-approval-contract.md): command identity and approval lineage.
- [NX-IF-002 — Exposure Snapshot & Risk Reservation Contract](NX-IF-002-exposure-snapshot-risk-reservation-contract.md): exclusive exposure buckets, fill-pending handoff, reservation lifecycle and recovery.
- [NX-ADR-002 — Execution Integrity & Reconciliation](NX-ADR-002-execution-integrity-reconciliation.md): durable command outbox, order/fill identity and ambiguous outcomes.
- [NX-ADR-005 — Instrument Specification & Exact Arithmetic](NX-ADR-005-instrument-specification-exact-arithmetic.md): exact values, contract models and immutable instrument versions.
- [ТЗ-NX-004 — Autonomous Execution Engine](../specifications/TZ-NX-004-autonomous-execution-engine.md): normalized private execution evidence and durable event outbox.
- [ТЗ-NX-005 — Independent Risk Engine](../specifications/TZ-NX-005-independent-risk-engine.md): exposure aggregation, reservation transfer and fail-closed policy.
- [ТЗ-NX-006 — Portfolio & Financial Ledger](../specifications/TZ-NX-006-portfolio-financial-ledger.md): immutable journal, balanced postings, positions and accounting projections.
- [NX-ARCH-001 — Target Architecture & Deployment Topology](NX-ARCH-001-target-architecture.md).
- [NX-ARCH-REVIEW-001 — Cross-Specification Contract Review](NX-ARCH-REVIEW-001-cross-specification-contract-review.md).

## 15. Verification limits

This is a proposed interface contract only. No NEXUS Execution event schema, outbox worker, Ledger inbox, journal posting engine, accounting projection, venue adapter, database transaction, conformance test, fault-injection test, reconciliation run or runtime behavior has been implemented or verified. No exchange account has been connected, no credentials or orders have been used, and no live trading or asset movement is authorized.
