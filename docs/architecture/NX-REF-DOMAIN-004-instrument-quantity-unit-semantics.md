# NX-REF-DOMAIN-004 — Instrument Quantity Unit Semantics Reference Model

**Status:** TEST-ONLY REFERENCE / PROPOSED DOMAIN CONTRACT  
**Authority:** None. Does not authorize, validate or submit orders.

## 1. Problem

`InstrumentSpec.quantity_unit` is intentionally opaque. Treating its string as a base asset or a contract count would silently invent financial meaning. A separate, explicit mapping is required and must be pinned to one immutable `InstrumentSpec` version.

## 2. Explicit mapping

`InstrumentUnitModel` binds:
- internal instrument ID and exact spec version;
- venue and native instrument identity;
- market and contract type;
- base, quote and settlement assets;
- the original opaque quantity-unit identifier;
- quantity kind: `ASSET_AMOUNT` or `CONTRACT_COUNT`;
- multiplier dimension and exact multiplier value.

The mapping constructor requires the caller to state quantity kind and multiplier dimension. It never infers either from the opaque venue string. `validate_against` rejects a different spec version, identity, asset tuple, quantity-unit token or multiplier.

## 3. Supported models

### Spot

Quantity is explicitly a base-asset amount. The quantity-unit identifier must equal the declared base asset. Quote-quantity spot semantics are not guessed and remain blocked.

### Linear contracts

Quantity is an instrument-scoped contract count. Contract multiplier means base-asset units per contract. Base exposure is exact multiplication; quote notional is then calculated using a Price whose base and quote assets match the spec.

### Inverse contracts

Quantity is an instrument-scoped contract count. Contract multiplier means quote-asset units per contract. Quote notional is exact multiplication and does not require a price.

Inverse base exposure is deliberately blocked: it requires division by price plus an explicit precision/rounding policy. The current ExactDecimal reference oracle has no division operation.

## 4. Explicitly unsupported

QUANTO is rejected. It requires a separately defined three-currency model that specifies payoff currency, multiplier dimensions, settlement asset and valuation/FX conversion rules. No generic scalar multiplier is accepted as a substitute.

Also unsupported: inverse base exposure, margin, collateral, leverage, fees, funding, P&L, settlement conversion, risk limits, order validation and production registry persistence. The model does not establish that any real venue's multiplier semantics match these illustrative fixtures.

## 5. Verification

The dedicated suite covers spot base-unit binding, linear base exposure and notional, inverse quote notional, exact spec-version binding, multiplier-dimension mismatch, cross-instrument rejection, explicit QUANTO rejection and inverse division-policy blocking. The suite runs independently in the Python 3.11–3.13 reference workflow.

## 6. Exit boundary

This is a test-only semantic reference. Venue-specific mappings require official instrument documentation and captured metadata fixtures, independently reviewed before use. No real instrument is qualified by synthetic fixtures.
