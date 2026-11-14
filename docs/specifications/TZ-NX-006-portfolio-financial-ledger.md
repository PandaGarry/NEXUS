# ТЗ-NX-006 — Portfolio & Financial Ledger

**Status:** PROPOSED — owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** authoritative event-sourced accounting, portfolio state, balances, positions, cash flows, fees, funding and realized/unrealized P&L for NEXUS Crypto v1.  
**Dependencies:** NX-ADR-001, NX-ADR-002, NX-ADR-004, NX-ADR-005, NX-ARCH-001, NX-SEC-001, ТЗ-NX-001, ТЗ-NX-004, ТЗ-NX-005.  
**Implementation:** NOT STARTED.

## 1. Purpose

The Ledger is the authoritative internal record of account financial events and derived portfolio state. It answers, with traceable evidence: what assets and liabilities exist, what positions are open, how each balance changed, what fees/funding/realized P&L were booked, and how current equity and exposure are derived.

The Ledger is not an order router, strategy engine or risk policy engine. It records facts and produces deterministic projections. The Risk Engine consumes Ledger state but retains independent authorization authority. The Ledger never infers a fill from an order acknowledgement or invents a missing financial event.

## 2. Scope

In scope:
- immutable normalized account, execution, fee, funding, transfer and adjustment events;
- double-entry journal / balanced posting model where applicable;
- balances, liabilities, collateral, positions and portfolio projections;
- realized and unrealized P&L with explicit valuation basis;
- fee/funding/interest/settlement/insurance/liquidation and exchange cash-flow records;
- deposits, withdrawals and internal transfers as observed account movements (trading-only API permissions remain the default);
- reconciliation against venue balances, positions, executions and transaction history;
- exact arithmetic, currencies, contract specifications and valuation provenance;
- snapshots, replay, corrections, audit, reporting and Risk Engine interfaces.

Out of scope:
- exchange order placement, signing or withdrawals initiated by NEXUS;
- strategy P&L attribution as a substitute for account accounting;
- tax advice or jurisdiction-specific tax reporting;
- discretionary balance editing or silent historical mutation;
- live account connection as part of this specification.

## 3. Non-negotiable invariants

1. Every financial state change is traceable to immutable source evidence or an explicitly authorized internal adjustment.
2. An order acknowledgement never creates a fill; only authoritative execution evidence posts trade quantity and trade-related cash effects.
3. Duplicate venue events cannot duplicate postings. Corrections and busts are new linked events and compensating postings, never silent edits.
4. Exact decimal/fixed-point/integer arithmetic is authoritative; binary floating point is not used for canonical financial values.
5. Every amount has an explicit currency, sign convention, unit, source and event-time meaning.
6. Unknown is not zero. Missing balances, fees, funding, contract multipliers, FX rates or positions remain UNKNOWN until reconciled.
7. Ledger is the single accounting source of truth for NEXUS; caches and projections are rebuildable.
8. Venue snapshots are evidence for reconciliation, not permission to erase immutable journal history.
9. All projections are deterministic and reproducible from journal events, instrument specs and valuation inputs.
10. Risk Engine receives freshness and reconciliation state alongside financial values; stale projections cannot silently authorize new risk.
11. Transfers between accounts/venues are linked and must not be misreported as trading profit or loss.
12. No live trading or asset movement is authorized by this specification.

## 4. Accounting model and boundaries

Use an append-only journal with balanced postings for financial events where the event has accounting debit/credit semantics. Maintain operational subledgers for:
- cash and collateral by account/currency;
- open positions by instrument/side;
- realized P&L;
- unrealized valuation;
- trading fees, rebates and funding;
- interest, settlement and liquidation/insurance events;
- transfers and non-trading cash flows;
- suspense / unresolved reconciliation items.

Each source event is normalized once, assigned an immutable NEXUS event ID and linked to one or more journal transactions. A journal transaction contains balanced postings under a documented chart of accounts and a posting-rule version. The exact account taxonomy is an architecture/owner decision, but no posting may be unbalanced or silently discarded.

Positions are quantity/cost-basis subledger records, not cash balances. Unrealized P&L is a valuation projection, not a realized cash posting. Mark-to-market revaluation entries, if maintained for reporting, must be separated from realized exchange cash flows and clearly labeled as non-cash valuation entries.

## 5. Canonical financial event contract

Every normalized event contains:
- `nexus_financial_event_id` and schema version;
- venue, account/subaccount, market type and native instrument ID where applicable;
- event category and subtype;
- native transaction/order/execution identifiers;
- exact signed amount, currency and quantity/price units where relevant;
- event timestamp, venue timestamp unit, receive timestamp and processing timestamp;
- source channel/endpoint, connection generation and pagination cursor/watermark;
- raw payload hash and secure raw evidence reference;
- Instrument Specification version where applicable;
- correction/bust linkage and original event reference;
- normalization version, adapter version and confidence/quality state;
- reconciliation status and posting-rule version.

Canonical categories include:
- TRADE_FILL;
- TRADING_FEE / FEE_REBATE;
- FUNDING_PAYMENT / FUNDING_RECEIPT;
- REALIZED_PNL;
- INTEREST / BORROW_COST;
- SETTLEMENT;
- LIQUIDATION / INSURANCE_CLEAR / ADL;
- TRANSFER_IN / TRANSFER_OUT / INTERNAL_TRANSFER;
- COLLATERAL_CHANGE;
- BONUS / REWARD / REBATE;
- EXCHANGE_ADJUSTMENT;
- CORRECTION / BUST;
- UNKNOWN_FINANCIAL_EVENT.

Unknown or venue-specific types must be preserved as raw evidence and mapped to suspense/UNKNOWN until their accounting treatment is documented. Do not drop unfamiliar event categories.

## 6. Exact arithmetic, currency and instrument semantics

All canonical quantities use exact decimal or integer-scaled representation with explicit scale. Price, size, contract count, multiplier, fee, balance, margin and P&L retain sufficient precision for the venue and instrument. Rounding occurs only at explicit boundaries and records the rounding mode and discarded remainder where material.

Instrument calculations must use immutable NX-ADR-005 specification versions:
- linear contracts;
- inverse contracts;
- quanto contracts;
- spot assets and liabilities;
- contract multiplier/value currency;
- settlement and quote currencies;
- tick/lot precision and fee currency.

No generic formula is applied to all instruments. Every formula is versioned, unit-tested and backed by golden fixtures. Historical events retain the specification version active at event time; a later instrument metadata update cannot silently rewrite historical amounts.

FX conversion is a valuation operation, not mutation of the original currency amount. Preserve original amount and currency plus converted value, quote currency, rate source, rate timestamp, quality, haircut and conversion method. If FX is missing or stale, the converted portfolio total is UNKNOWN/INCOMPLETE, not a zero contribution.

## 7. Trade and position accounting

Each execution fill is an independent immutable event. For every fill record:
- venue execution ID and documented uniqueness scope;
- linked venue and NEXUS order IDs;
- account, instrument, side and position side/index;
- exact fill price, quantity, contract count and multiplier;
- fee amount and fee currency, liquidity role if supplied;
- venue trade time, receive time and source;
- instrument specification and posting-rule versions.

A fill updates position quantity and cost basis according to the instrument's contract model and position mode. Partial fills remain separate. Position close/reversal accounting must split closing quantity from newly opened opposite-side quantity where the venue uses net position semantics. Hedge-mode long and short legs remain distinct.

Position projection includes quantity, side, average entry/cost basis, mark price, unrealized P&L, realized P&L, fees, funding, margin references and source freshness. Venue position snapshots are compared to the projection; differences create reconciliation discrepancies rather than silently overwriting fills.

## 8. Fees, funding, settlement and realized P&L

Fees and rebates are separate financial events with exact currency and sign semantics. A positive/negative sign is normalized to a canonical convention and the original venue sign is preserved. Maker/taker classification is UNKNOWN when not supplied or reliably derivable.

Funding payments/receipts are recorded as cash events with:
- instrument and position reference;
- exact amount and settlement currency;
- funding rate and notional basis where supplied;
- settlement timestamp and venue transaction ID;
- original source semantics and normalized sign.

Realized P&L is recognized from authoritative close/settlement events or derived from fills under a documented instrument-specific method, then reconciled against venue account history. Do not double-count realized P&L when the exchange reports both trade-level close P&L and account cash-flow transaction. Posting rules define which source is primary and how duplicates/cross-references are resolved.

Liquidation, insurance, ADL, delivery and expiry settlement are distinct categories, not generic trading fees. Unknown components remain separate suspense entries until semantics are established.

## 9. Balances, equity and portfolio valuation

Maintain per account and currency:
- total balance;
- available balance;
- locked/reserved balance;
- collateral-eligible amount;
- liabilities/borrowed amount;
- unrealized P&L where venue reports it;
- margin balance/equity where applicable;
- venue-reported values and NEXUS-derived values separately.

Portfolio equity is a derived valuation with an explicit definition and timestamp. It must distinguish:
- cash/wallet balance;
- collateral-adjusted equity;
- margin equity including unrealized P&L;
- gross asset value;
- liabilities;
- restricted/non-collateral assets;
- unsettled transfers and suspense items.

Do not combine incompatible venue account modes into one number without an approved normalization and collateral policy. A portfolio total may be marked PARTIAL/UNKNOWN if any material account, currency or position cannot be valued reliably. Show coverage and missing components rather than a misleading precise total.

## 10. Event ingestion, idempotency and corrections

Ingestion supports private streams, REST history/snapshots and controlled operator evidence. Each source has a documented identity strategy:
- stable venue transaction/execution ID where guaranteed;
- venue/account/category-specific composite key only where documented and tested;
- raw payload hash as evidence, not a universal business identity.

Deduplication key scopes are explicit. Same ID across different accounts/categories must not collide. Events arriving late or out of order are retained with original event time and processing time. Replayed pages and overlapping history windows must be idempotent.

Corrections, fee adjustments, trade busts and exchange restatements create linked compensating journal transactions. Never delete or mutate the original event or posting. Rebuildable projections apply corrections in deterministic order while preserving full lineage.

## 11. Reconciliation

Reconciliation is continuous and event-triggered. Compare:
- venue wallet/account balances;
- open positions and position modes;
- executions and order cumulative quantities;
- fee, funding and transaction histories;
- internal transfers and settlement events;
- local journal balances and projections.

Triggers:
- startup and restore;
- private stream connect/reconnect or sequence gap;
- fill/fee/funding event arrival;
- ambiguous execution outcome;
- periodic checkpoint;
- venue account snapshot change;
- operator request;
- before releasing a risk or execution quarantine.

Use overlapping time windows, stable cursors and documented retention limits. Persist query parameters, cursor, response hash, retrieval timestamp, adapter version and reconciliation watermark. Empty results outside venue history retention do not prove absence of events.

Discrepancy states:
- MATCHED;
- PENDING_SOURCE_LAG;
- MISSING_LOCAL_EVENT;
- MISSING_VENUE_EVENT;
- AMOUNT_MISMATCH;
- POSITION_MISMATCH;
- BALANCE_MISMATCH;
- DUPLICATE_SUSPECTED;
- UNKNOWN_EVENT_TYPE;
- OUTSIDE_RETENTION;
- MANUAL_REVIEW_REQUIRED.

Material unresolved discrepancies mark affected account/currency/instrument projections DEGRADED or QUARANTINED and propagate a block to Risk Engine. No risk-increasing approval may rely on unreconciled financial state where policy requires a clean ledger.

## 12. Snapshots, replay and recovery

Journal is authoritative; snapshots are derived acceleration artifacts. Every snapshot records:
- journal watermark / last applied event sequence;
- schema, posting-rule and projection versions;
- instrument specification versions;
- valuation marks and FX inputs with timestamps;
- source reconciliation state;
- snapshot hash and creation time.

On restart, validate snapshot integrity and replay journal events after its watermark. If the journal has gaps, invalid hashes or missing dependencies, mark the projection unhealthy and block downstream risk use. Rebuild must be deterministic and produce the same projection hash for the same event and reference-data versions.

Backups must preserve journal, raw evidence references, idempotency keys, correction links, policy/posting versions and reconciliation state. Restore drills are mandatory before production readiness.

## 13. Ledger states and data quality

Per account/currency/instrument projection:
- INITIALIZING;
- SYNCING;
- RECONCILING;
- HEALTHY;
- DEGRADED;
- STALE;
- QUARANTINED;
- HALTED.

Data quality is orthogonal:
- VALID;
- PARTIAL;
- STALE;
- UNSYNCHRONIZED;
- INVALID;
- UNKNOWN.

A HEALTHY state requires complete required event ingestion, current account/position snapshots, no material unresolved discrepancy, valid instrument specs, consistent journal and fresh valuation inputs. Restart or reconnect returns to SYNCING/RECONCILING, not automatically HEALTHY.

## 14. Risk Engine interface

Ledger exposes versioned read models:
- `AccountFinancialState`;
- `PositionState`;
- `OpenOrderAndPendingExposure` (joined with Execution);
- `EquityAndCollateralState`;
- `RealizedAndUnrealizedPnL`;
- `LedgerHealthAndReconciliationState`.

Each response includes exact values, currencies, as-of time, journal watermark, source watermarks, quality, reconciliation state and projection version. Risk Engine must be able to reject a snapshot as stale or incomplete. Ledger does not return a bare number without provenance and status.

## 15. Reporting and performance attribution

Reports distinguish realized P&L, unrealized P&L, fees, funding, interest, transfers, rebates, adjustments and valuation/FX effects. Net performance must not treat deposits, withdrawals or internal transfers as profit. Strategy attribution is a separate analytical dimension linked to immutable strategy/intent IDs; unassigned/manual/external activity remains visible as unattributed.

Daily/session boundaries require an owner-approved timezone and cut-off policy. Reports must state whether values are cash-based, mark-to-market, gross or net of fees/funding, and which FX valuation time is used. Tax lots and jurisdiction-specific tax treatment are not part of v1.

## 16. Security, privacy and audit

- Service identities are least-privilege; Ledger has no exchange trading or withdrawal authority.
- Raw account payloads and identifiers are encrypted at rest and access-controlled.
- Logs redact API secrets, signatures and unnecessary personal/account data.
- Journal and audit history are append-only with tamper-evident hashes or equivalent integrity controls.
- Manual adjustments require strong operator authentication, reason, evidence, scoped permission and dual approval for configured high-impact cases.
- No ordinary service, AI agent or strategy may mutate journal history or create an unbacked balance.
- Retention, deletion and export policies must preserve financial audit obligations while minimizing sensitive data.

## 17. Observability

Metrics:
- event ingestion lag and gaps by venue/account/channel;
- duplicate, late, corrected and unknown event counts;
- journal posting failures and unbalanced transaction attempts;
- projection lag and replay duration;
- reconciliation drift and discrepancy age by category;
- stale/partial/unknown balance and position coverage;
- FX/mark freshness and valuation coverage;
- snapshot integrity and restore status;
- Risk Engine consumers receiving degraded state.

Every journal transaction must be traceable to source event, raw evidence, posting rule, instrument spec, actor/service, timestamps and correction lineage.

## 18. Testing strategy

Required tests:
- double-entry balance invariants and chart-of-accounts rules;
- exact decimal arithmetic, scale, rounding and currency conversions;
- golden tests for spot, linear, inverse and quanto contracts;
- partial fills, net-position close/reversal and hedge-mode legs;
- fees, rebates, funding signs, settlement and liquidation events;
- duplicate, reordered, late, missing and corrected events;
- venue-specific ID uniqueness and pagination overlaps;
- trade P&L vs account cash-flow double-count prevention;
- transfer neutrality and internal transfer linking;
- missing/unknown event categories and suspense handling;
- snapshot/replay deterministic hash equality;
- reconciliation mismatches and stale/retention boundaries;
- restart, crash, backup/restore and journal integrity;
- Risk Engine freshness/quality propagation;
- authorization, audit, redaction and tamper-evidence.

Testing ladder:
1. pure accounting and arithmetic unit/golden tests;
2. adapter fixture/contract tests;
3. deterministic historical replay;
4. fault-injected ingestion/reconciliation tests;
5. exchange sandbox/read-only account comparison where appropriate;
6. read-only shadow reconciliation;
7. production readiness and limited-live review only by separate owner approval.

## 19. Acceptance criteria

- [ ] Every financial state change has immutable source evidence or approved adjustment evidence.
- [ ] Journal transactions satisfy configured balancing invariants.
- [ ] Exact arithmetic and instrument-specific formulas are used throughout.
- [ ] Duplicate events cannot duplicate balances, fees, funding or P&L.
- [ ] Corrections and busts preserve original records and create compensating entries.
- [ ] Order acknowledgements never create fills.
- [ ] Fills, fees, funding and settlement are separately identifiable and correctly linked.
- [ ] Transfers are excluded from trading profit/loss.
- [ ] Unknown amounts, currencies, event types and FX rates remain UNKNOWN/suspense.
- [ ] Venue snapshots reconcile against local positions, balances and transaction history.
- [ ] Material discrepancies propagate degraded/quarantined status to Risk Engine.
- [ ] Snapshot/replay is deterministic and survives restart/restore.
- [ ] Reports distinguish cash, collateral equity, margin equity and valuation effects.
- [ ] Audit lineage reconstructs every posting and correction.
- [ ] Golden, contract, replay, reconciliation and fault-injection tests pass before production use.

## 20. Open owner decisions

1. Initial venues, account modes, spot/perpetual product coverage and subaccount scope.
2. Chart of accounts and journal database/event-store design, finalized in NX-ARCH-001.
3. Daily P&L boundary, timezone and treatment of transfers, fees, funding and rebates.
4. FX conversion providers, mark hierarchy, freshness and collateral haircuts.
5. Raw payload, journal and audit retention periods.
6. Policy for exchange-reported vs NEXUS-derived P&L when they differ.
7. Operator adjustment workflow and dual-approval thresholds.
8. Whether portfolio aggregation spans multiple venues/accounts in the first release.
9. Snapshot cadence, replay objectives and backup/restore targets.
10. Treatment of external/manual orders, positions and unassigned cash flows.

Until decided, unsupported account modes and valuation scopes remain explicitly PARTIAL/UNKNOWN and cannot be presented as fully reconciled.

## 21. Dependencies and implementation sequence

- NX-ADR-005 supplies immutable instrument specs and exact arithmetic.
- NX-ADR-001 supplies canonical event envelope, provenance and timestamps.
- NX-ADR-004 and ТЗ-NX-001 supply data quality, recovery and source watermarks.
- ТЗ-NX-004 supplies authoritative order/fill and private account event evidence.
- NX-ADR-002 supplies execution identity and reconciliation lifecycle.
- ТЗ-NX-005 consumes Ledger state for exposure/loss checks; Ledger does not approve risk.
- NX-SEC-001 and NX-ARCH-001 define storage, identity, access and recovery controls.

Implementation order: chart of accounts and posting rules → canonical financial event contract → exact instrument accounting and golden tests → immutable journal/idempotent ingestion → balance/position projections → fees/funding/settlement → reconciliation → snapshots/replay → Risk Engine read models → reporting and restore certification. Start with read-only import and replay; no live execution or asset movement is implied.

## 22. Evidence and references

Official venue documentation consulted on 2026-11-14; each adapter must pin API version, endpoint, account mode and retention behavior at implementation time:

- Binance USDⓈ-M Futures Get Income History — income categories include realized P&L, funding, commission and transfers; query windows and identifier semantics are endpoint-specific: https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Get-Income-History
- Binance USDⓈ-M Futures Account Trade List — fill-level trade history and pagination/ID semantics: https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api
- Bybit V5 Get Transaction Log — transaction records expose trade fees, funding, cash flow, balance changes, IDs and cursor pagination: https://bybit-exchange.github.io/docs/v5/account/transaction-log
- Bybit V5 Funding Account Transaction History — separate funding-account transaction history and cursor behavior: https://bybit-exchange.github.io/docs/v5/asset/fund-history
- OKX API v5 Get Bills — balance-changing account records, pagination and separate historical archive workflow: https://www.okx.com/docs-v5

Venue APIs expose different categories, sign conventions, retention windows, pagination and source identifiers. NEXUS must preserve raw native semantics and normalize through versioned adapter rules; no single endpoint is assumed to be a complete accounting ledger.

## 22A. Execution event ingestion and posting contract (WP-C)

The normative handoff is proposed in [NX-IF-003 — Execution Event & Ledger Posting Contract](../architecture/NX-IF-003-execution-event-ledger-posting-contract.md). Ledger MUST consume immutable normalized Execution events through a durable inbox and MUST atomically commit the inbox identity, payload digest, complete balanced journal transaction, source links and projection work/watermark. Re-delivery of the same identity and digest returns the existing outcome without a second posting; same identity with a different digest is quarantined. Acknowledgement MUST NOT precede durable commit or durable quarantine. Execution delivery status, Ledger journal commit, projection application and venue reconciliation remain distinct states.

Fills, fees/rebates and later fee adjustments are separately identifiable and linked; fee fields embedded in a fill and separately reported account transactions MUST be deduplicated to prevent double posting. Corrections/busts append compensating journal transactions referencing original postings; historical records are never edited or deleted. The journal transaction for one economic event is atomic across all required legs and rejects unknown currencies, unsupported instrument semantics and unbalanced postings.

## 23. Verification status

This is a requirements proposal only. No NEXUS journal, posting engine, portfolio ledger, reconciliation projector, accounting report or restore test has been implemented or tested. No exchange account has been connected. No live trading or asset movement is authorized.

**Prototype Readiness remains BLOCKED.**
