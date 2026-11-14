# NX-REF-DOMAIN-010 — Venue-Neutral Financial Math Golden Fixtures

**Status:** TEST-ONLY REFERENCE FIXTURES  
**Authority:** Non-authorizing. These fixtures do not qualify a venue, define a production financial policy or permit order/risk/ledger decisions.  
**Parent design:** NX-REF-DOMAIN-009  
**Scope:** Exact dimensional identities only, with synthetic instrument metadata.

## 1. Purpose

Provide independently hand-derived, language-neutral examples for mathematical relationships that remain valid once their dimensions and instrument-unit semantics have already been explicitly established.

This package deliberately does not implement or specify:
- exchange tick/lot normalization or rounding direction;
- fees, rebates, funding or settlement;
- realized/unrealized P&L or inventory matching;
- minimum-notional venue rules;
- margin, liquidation, leverage or collateral;
- FX conversion;
- journal/accounting policy.

## 2. Golden vector set

The machine-readable vectors are in [financial-math-golden-v1.json](../../foundation/reference-model/financial-math-golden-v1.json), schema version 1.0.0.

| Fixture | Exact relationship | Expected result |
|---|---|---|
| spot-notional-001 | BTC quantity × USDT per BTC | 8125.03125 USDT |
| linear-contract-notional-001 | contracts × BTC/contract × USDT/BTC | 0.012 BTC; 780.003 USDT |
| inverse-contract-exposure-001 | contracts × USD/contract ÷ USD/BTC | 10000 USD; 40000/260001 BTC |
| partial-fill-weighted-average-001 | sum(fill quantity × fill price) ÷ sum(fill quantity) | 8125.085 USDT; 0.125 BTC; 65000.68 USDT/BTC |

All values are exact. No rounding is performed. The inverse result remains a rational number because its base-10 expansion is non-terminating.

## 3. Interpretation boundaries

### Spot notional

For an explicitly dimensioned base-asset amount and quote-per-base price:

`Notional_{quote} = Quantity_{base} \times Price_{quote/base}`

The fixture validates dimensional multiplication only. It does not determine whether a venue's minimum-notional rule uses this value or another reference-price convention.

### Linear contract exposure and notional

For an explicitly qualified multiplier expressed as base-asset units per contract:

`Exposure_{base} = ContractCount \times Multiplier_{base/contract}`

`Notional_{quote} = Exposure_{base} \times Price_{quote/base}`

The fixture does not qualify any venue's contract multiplier or order-size convention.

### Inverse contract exposure

For this explicitly declared synthetic convention:

`QuoteNotional = ContractCount \times QuoteUnitsPerContract`

`BaseExposure = QuoteNotional / Price_{quote/base}`

The exact result is `40000/260001 BTC`; it must not be silently truncated or rounded to a decimal. This fixture does not define inverse P&L, realized P&L, margin, settlement events or any venue's contract semantics.

### Partial-fill weighted average

For a set of fills with quantities in the same base unit and prices in the same quote/base unit:

`TotalQuoteValue = Σ(quantity_i × price_i)`

`WeightedAveragePrice = TotalQuoteValue / Σ(quantity_i)`

This is an arithmetic identity, not a promise that a venue reports its average price using this exact aggregation scope. It excludes fees, funding, rebates, inventory matching and P&L.

## 4. Independent verification

The Python test suite uses the existing test-only exact decimal/domain/instrument-unit references and checks selected results independently with Python's standard-library `fractions.Fraction`. The hand-derived JSON values are the cross-language expected outputs; Python is not the production authority.

Run from `foundation/reference-model`:

```bash
python -m unittest -v test_financial_math_fixtures.py
```

The suite includes positive vectors and negative dimensional/instrument-identity cases. CI runs it separately on Python 3.11, 3.12 and 3.13.

## 5. Explicit exclusions and disposition

- **ACCEPTED AS MATHEMATICS ONLY:** dimensional multiplication for the explicitly declared spot/linear/inverse models; exact weighted-average identity over a supplied fill set.
- **NOT QUALIFIED:** venue contract mappings, official multipliers, average-price reporting scope, tick/lot behavior, fees, funding, P&L, margin, liquidation, FX and accounting.
- **OWNER DECISION REQUIRED:** position/inventory accounting, treatment and allocation of fees/funding, valuation hierarchy, journal policy and rounding ownership.
- **DEFERRED:** production implementation, cross-language Rust/WASM conformance, bounded resource profile and any live execution integration.

These fixtures are not financial-operation conformance evidence and do not pass G0/G1. Existing readiness gates remain unchanged.
