# NX-REF-DOMAIN-003 — Dimensional Financial Types Reference Model

**Status:** TEST-ONLY REFERENCE / PROPOSED DOMAIN CONTRACT  
**Scope:** Immutable, exact-decimal financial values.  
**Authority:** None. This model cannot authorize, validate or submit an order.

## 1. Purpose

Prevent dimensionally invalid arithmetic from entering later Risk, Execution and Ledger work. A raw decimal does not identify whether it represents BTC, USD, a price, a contract count or a quote notional.

## 2. Types

| Type | Meaning | Required unit |
|---|---|---|
| `AssetAmount` | Amount of a named asset; suitable for spot base quantity | Asset code |
| `Money` | Cash/accounting amount | Currency/asset code |
| `Price` | Quote units per one base unit | Base asset + quote asset |
| `Notional` | Calculated quote-denominated value | Quote asset |
| `ContractCount` | Number of contracts, not underlying asset | Instrument ID |

All numeric fields use `ExactDecimal`. No float conversion, implicit FX, implicit asset conversion or implicit contract conversion exists. Money and Notional remain distinct even when their unit code matches.

## 3. Supported operations

- Add/subtract `AssetAmount` only when asset codes match.
- Add/subtract `Money` only when currency codes match.
- Add/subtract `Notional` only when quote-asset codes match.
- Compare same-type amounts only when both dimension and unit match.
- `Price.notional_for(AssetAmount)` is supported only when the amount's asset matches the price base asset; result is a quote-denominated `Notional`.
- `ContractCount` is instrument-scoped and has no conversion to `AssetAmount`.

Signed amount values are permitted for position deltas and accounting corrections. Positive order constraints belong to order validation, not these general ledger-capable value types.

## 4. Explicitly unsupported

No FX conversion, currency metadata registry, token contract identity, precision bounds, division/reciprocal, rounding, fee conversion, funding, collateral valuation, margin, leverage, P&L, linear/inverse/quanto contract formulas, settlement conversion or accounting journal policy is implemented. No contract multiplier is inferred from `InstrumentSpec`.

The current `InstrumentSpec.quantity_unit` remains an opaque identifier. Mapping it to these domain types requires a separately versioned, venue-qualified instrument-unit contract. This reference slice does not silently infer that mapping.

## 5. Verification

Dedicated tests cover exact notional multiplication, base-asset mismatch, contract-count rejection, positive price, same-unit arithmetic, cross-unit rejection, Money/Notional separation, canonical unit codes and signed deltas. The test suite is added to the Python 3.11–3.13 reference-model workflow.

## 6. Exit boundary

This slice is complete only as a test-only reference model after exact-head CI passes. Production domain types, bounded numeric representation, cross-language conformance and integration with Risk/Ledger remain blocked.
