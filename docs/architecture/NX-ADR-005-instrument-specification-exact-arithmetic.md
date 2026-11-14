# NX-ADR-005 — Instrument Specification & Exact Arithmetic

**Status:** PROPOSED — requires owner review  
**Date:** 2026-11-14  
**Scope:** Canonical instrument identity, versioned trading rules, contract/settlement semantics, and exact numeric representation across market data, strategy, risk, execution and ledger.  
**Evidence baseline:** Tradoor `tradoor-terminal/tradoor` commit `39a1826816f973ff46c15a848ad1cbe3be7b1dc8`; see NX-RESEARCH-002. This ADR defines NEXUS requirements; it does not claim Tradoor already meets them.

## Context

A symbol and price decimal count are not a trading specification. Spot assets, linear contracts, inverse contracts, quanto contracts, options and venue-specific perpetuals can share similar symbols while having different quantity units, multipliers, settlement currencies, precision and P&L formulas.

The source audit found that Tradoor's shared `Product` model stores market identity, base/quote, kind, optional native symbol, `price_decimals` and display statistics. It does not store authoritative lot/quantity filters, min notional, contract multiplier, settlement, linear/inverse semantics or margin tiers. Venue parsers often extract only price precision. Order Flow conversion helpers cover selected venues and contain fallback assumptions. The Hyperliquid parser currently derives `price_decimals` from `szDecimals` (size precision), a semantic mismatch that must be fixed before that model is reused.

Financial correctness cannot rely on binary floating-point as the canonical representation. Floating-point remains acceptable for visualization or explicitly approximate analytics, never as the single source of truth for order validation, balances, fees, margin or P&L.

## Decision

NEXUS will own a versioned Instrument Specification Registry. Venue adapters populate it from authoritative venue metadata; an instrument is not tradable until the required fields are present, validated, fresh and approved.

### Canonical identity

An instrument key is immutable and unambiguous:

`venue_id + market_type + native_instrument_id`

A separate stable internal `instrument_id` maps to that key. Canonical symbols are display aliases only and must never be used as the sole primary key. Spot, linear perpetual, inverse perpetual and other contract families are distinct instruments even when their visible base/quote symbols match.

### Required specification fields

| Group | Required fields |
|---|---|
| Identity | internal instrument ID, venue, market type, native ID/symbol, base, quote, settlement asset, status |
| Price | exact tick size, price precision/scale, allowed price bounds/bands, price reference rules |
| Quantity | exact quantity step/lot size, quantity precision/scale, min/max quantity, quantity unit |
| Notional | min/max notional and calculation currency/rule |
| Contract | contract type, linear/inverse/quanto, contract value, multiplier, multiplier unit, base/quote conversion rule |
| Settlement | settlement currency, collateral currencies, settlement schedule, funding interval/rules where applicable |
| Trading rules | supported order types, time-in-force, reduce-only/close semantics, position mode constraints |
| Risk | leverage tiers, initial/maintenance margin brackets, max position/notional, price bands |
| Provenance | source endpoint/document, raw payload hash/reference, fetched_at, effective_at if supplied, adapter version, schema version |
| Lifecycle | ACTIVE / SUSPENDED / DELISTING / DELISTED / UNKNOWN, validation state, expiry if applicable |

Fields not applicable to a market are explicitly NOT_APPLICABLE with a reason. Missing fields are UNKNOWN, never zero or a guessed default.

### Versioning and freshness

- Every metadata refresh produces an immutable specification version with effective/fetched timestamps and raw source evidence.
- Orders and financial events reference the exact spec version used for validation and calculation.
- A spec change that alters tick, lot, multiplier, settlement, margin or contract semantics invalidates cached validation and triggers controlled revalidation.
- Stale or incomplete specs block new risk-increasing orders. Existing positions remain visible and are reconciled; emergency reduce-only actions follow a separate safe policy.
- Delisted or suspended instruments cannot accept new risk-increasing orders.
- The system must retain historical spec versions for replay, backtests, audit and reconciliation.

### Exact arithmetic

Canonical price and quantity are represented as integer ticks/lots where the venue rules allow it, or as arbitrary-precision decimal/fixed-point values with explicit scale. Currency amounts and P&L use exact decimal arithmetic with documented rounding rules.

Normative rules:
- No binary float as the canonical value for price, quantity, fee, balance, margin, funding or P&L.
- Preserve the original venue decimal string/raw numeric representation before parsing.
- Convert price to integer ticks only after validating exact divisibility by tick size.
- Convert quantity to integer lots only after validating exact divisibility by lot step.
- Reject values that cannot be represented exactly at the current spec version; never silently round a risk-increasing order.
- Rounding direction is field- and operation-specific and documented (e.g. price rounding must not accidentally increase risk; fee rounding must follow venue rules).
- Each monetary value carries currency and scale; cross-currency conversion uses a timestamped, source-attributed FX/mark reference.
- Multiplication/division order and intermediate precision are specified for contract notional, inverse P&L, fees, funding and margin.
- Display formatting is separate from canonical storage and may use floating-point only after conversion from the exact value.

### Contract models

At minimum, the engine must explicitly support or reject:
- Spot base-quantity and quote-quantity order semantics.
- Linear contracts: contract quantity × contract multiplier → base exposure/notional according to venue rules.
- Inverse contracts: quote-denominated contract value and price-dependent base exposure/P&L.
- Quanto contracts: multiplier and settlement conversion in a third currency.
- Venue-specific coin multipliers and denomination conventions.

Unsupported contract models are non-tradable; no fallback multiplier of 1 is allowed for execution or risk.

### Instrument metadata ingestion

Each adapter must implement:
1. Fetch instrument catalogue and all pagination.
2. Fetch trading filters/rules and margin/position metadata separately where endpoints differ.
3. Parse decimal strings without converting through `f64`.
4. Validate schema, status, units, consistency and required fields.
5. Preserve raw payload and source endpoint.
6. Emit a new immutable spec version only when the canonical spec changes.
7. Alert on unknown schema fields, missing required fields, implausible changes or stale metadata.
8. Reconcile metadata before enabling strategy startup or order dispatch.

Public market-data catalogue endpoints are not assumed to contain all private/account-specific risk constraints.

## Consequences

- Instrument metadata becomes a first-class domain model and dependency for risk/execution.
- Some symbols remain chartable but non-tradable until complete rules are available.
- Decimal/fixed-point arithmetic increases implementation and testing effort.
- Historical backtests become reproducible against the exact metadata version.
- Adapters require per-venue golden fixtures and authoritative documentation.

## Alternatives considered

1. **Reuse Tradoor Product:** rejected; it is a discovery/display catalogue, not a full trading spec.
2. **Use decimal counts only:** rejected; decimal counts do not encode increments, bounds, units or contract multipliers.
3. **Use f64 and round at order send:** rejected; precision loss can occur before rounding and creates inconsistent risk calculations.
4. **Assume multiplier 1 when absent:** rejected; can misstate exposure and P&L by orders of magnitude.
5. **Infer contract size from market trades/candles:** rejected for execution; observed trade ratios are not authoritative instrument rules.

## Acceptance criteria

1. Every tradable instrument has a complete, fresh, versioned specification.
2. Spot, linear, inverse and quanto contracts are distinguished explicitly.
3. Price tick and quantity lot are independently represented and validated.
4. Exact decimal strings survive ingestion without f64 conversion.
5. Off-tick/off-lot values are rejected or rounded only under an explicit, tested policy.
6. Min/max quantity, min notional, price bounds and contract multiplier are enforced by Risk/Execution.
7. Fee, funding, notional, margin, realized/unrealized P&L calculations have deterministic golden tests using exact arithmetic.
8. Historical order/fill/ledger events retain the spec version used at the time.
9. Metadata refresh handles pagination, stale data, schema changes, delisting and temporary venue outages.
10. Missing multiplier, settlement currency, tick or lot data cannot silently default to 1/0 or be considered tradable.
11. A Hyperliquid fixture demonstrates that size precision is not assigned to price precision.
12. No live trading is enabled solely because public symbol discovery succeeds.

## Open decisions for owner review

- Which exact decimal/fixed-point implementation and maximum scale should be standardized across Rust/backend and client display?
- Which venue/market families are required for the initial release?
- What metadata freshness thresholds apply to tick/lot rules versus margin tiers?
- Which inverse/quanto products are in initial scope, or should they be deferred until the first linear/spot release?
