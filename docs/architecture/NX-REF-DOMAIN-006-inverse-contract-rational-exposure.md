# NX-REF-DOMAIN-006 — Inverse Contract Base Exposure as Exact Rational

**Status:** TEST-ONLY REFERENCE / PROPOSED DOMAIN CONTRACT  
**Authority:** None. Not an order validator, risk calculation or production valuation service.

## 1. Scope and formula

This slice covers only a conventional inverse contract whose contract multiplier is a fixed quote-asset amount per contract and whose settlement asset is the base asset.

For contract count (N), quote value per contract (M_q), and price (P_{q/b}) (quote units per base unit):

[
Q_b = \frac{N \times M_q}{P_{q/b}}
]

The result is generally a rational number and may not have a finite base-10 representation.

## 2. Exact result type

`InstrumentUnitModel.inverse_base_exposure` returns `RationalAssetAmount`, carrying:
- the declared base asset code;
- a reduced `ExactRational` amount.

No decimal scale or rounding mode is selected. For example, one 100 USD inverse contract at 30,000 USD/BTC yields exactly 1/300 BTC, not an approximated decimal.

## 3. Explicit conversion boundary

- `to_asset_amount_exact()` succeeds only when the rational has a terminating base-10 representation.
- `quantize(scale, rounding)` requires a caller-supplied scale and explicit `RoundingMode`.
- Neither method chooses an exchange, risk or accounting rounding policy.
- The inverse model rejects a settlement asset different from the base asset.

## 4. Preconditions and exclusions

The explicit unit mapping must be pinned to the exact `InstrumentSpec` version. Contract count must belong to that instrument. Price base/quote assets must exactly match the specification. The contract multiplier is interpreted as quote-asset units per contract.

This is not a universal formula for every product labelled inverse. Venue-specific contract definitions must be qualified from official instrument documentation. quanto, quanto-style multipliers, coin-margined variants with nonstandard multipliers, fee/funding P&L, realized/unrealized P&L, margin, collateral and liquidation remain outside this slice.

## 5. Verification

Synthetic tests cover exact 1/300 BTC exposure, terminating 1/200 BTC exposure, explicit HALF_EVEN quantization, mismatched price dimensions, cross-instrument contract rejection and base-settlement precondition. The suite runs in the Python 3.11–3.13 reference workflow.

## 6. Exit boundary

No production use until venue-specific official specifications and captured fixtures are reviewed, operation-specific rounding is approved, and the same formulas pass independent cross-language golden vectors and property tests.
