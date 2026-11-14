# NX-REF-DOMAIN-009 — Operation-Specific Financial Rounding & Valuation Contract

**Status:** PROPOSED DESIGN CONTRACT / NOT OWNER-ACCEPTED  
**Scope:** Financial operation semantics across Instrument, Risk, Execution, Portfolio and Ledger.  
**Authority:** None. This document does not select a venue, approve a production policy, authorize order validation or permit live trading.  
**Baseline:** PR #11 head `64a36fa9a8d9626488025430a9a8776844ed5a93`; stacked branch `foundation/financial-operation-contract-v0`.

## 1. Purpose and non-goals

NEXUS already has test-only exact decimal/rational primitives, dimensional value types and version-pinned instrument-unit reference models. Those primitives deliberately do not decide how a financial operation rounds, values, settles or posts.

This contract defines the decision surface and fail-closed boundaries for each operation. It separates:

1. venue-independent mathematical invariants;
2. venue/product/account-specific semantics that must be qualified from authoritative documentation and observed API contracts;
3. owner-controlled accounting and risk policies;
4. display-only approximations, which must never become authoritative ledger or authorization inputs.

It does **not** select a venue/product, account mode, inventory accounting method, collateral valuation policy, FX source, fee tier, leverage, numeric limits, rounding mode or production numeric profile. It does not implement a production calculator.

## 2. Normative language and evidence classes

- **MUST / MUST NOT** — invariant required for any conforming NEXUS implementation.
- **SHOULD** — default engineering requirement; deviation requires a recorded rationale and tests.
- **BLOCKED** — no safe generic policy can be selected from current evidence.
- **VENUE-QUALIFIED** — requires exact venue + product + account mode + instrument + effective time evidence.
- **OWNER-DECISION** — requires explicit owner/accounting/risk policy approval.
- **TEST-ONLY** — reference examples or models; no production authority.

Evidence classes:
- **E1 Official specification:** current official venue/API/contract documentation for the exact product and account mode.
- **E2 Authoritative account evidence:** authenticated account configuration, fee schedule, risk tier, instrument metadata or exchange-issued execution/ledger event.
- **E3 Conformance evidence:** captured sanitized fixtures and deterministic tests against E1/E2 semantics, including version/effective-time provenance.
- **E4 Independent mathematical oracle:** hand-derived or separately implemented exact examples; not a substitute for E1/E2.

A search result, generic help page, symbol name, third-party SDK or another venue's rule is not sufficient to mark a venue-specific item qualified.

## 3. Global financial correctness invariants

### 3.1 Exactness and dimensions

1. Authoritative prices, quantities, contract counts, rates, fees, funding, balances, collateral, margin, notional and P&L MUST use exact decimal or exact rational representations with explicit dimensions and units.
2. Binary floating point MUST NOT be authoritative for validation, reservations, approvals, fills, journal postings, balances, exposure or reconciliation.
3. Every intermediate MUST retain its dimension. A scalar without unit, instrument identity and relevant spec version is not a financial value.
4. No implicit asset conversion, FX conversion, contract conversion, settlement conversion or rounding is permitted.
5. Rational results MUST remain rational until a specifically authorized operation boundary requires quantization. A repeating rational MUST NOT be silently truncated to decimal.
6. Every calculation MUST bind to immutable input evidence: instrument spec version, price source/type, fee schedule/rate source, risk tier, account mode, timestamps and source identifiers as applicable.

### 3.2 Rounding and quantization

1. A rounding mode MUST be selected per operation and per output field; there is no global financial rounding default.
2. A rounding decision MUST identify: input value, target unit/scale or step, rounding mode, rounding purpose, sign behavior, policy version, and the point in the calculation at which rounding occurs.
3. Intermediate values MUST NOT be rounded merely to fit a display scale or storage column.
4. Rounding MUST occur only at a documented boundary: exchange order parameter construction, exchange-defined fee/funding settlement, owner-approved accounting posting, or presentation.
5. The order of operations is part of the contract. Algebraically equivalent rearrangements are not presumed equivalent after rounding.
6. Every rounded result MUST be revalidated against all applicable instrument and account constraints.
7. If required precision, mode, source or policy is unknown, the operation MUST fail closed or remain explicitly non-authoritative. It MUST NOT invent a default.
8. Presentation rounding MUST be isolated from the authoritative value and MUST never feed back into calculations.

### 3.3 Provenance and replay

Each financial result MUST carry or be reproducibly linked to:
- calculation/version identifier;
- operation and input dimensions;
- exact input values and source event IDs;
- instrument identity and immutable spec version, where applicable;
- price type/source and source timestamp, where applicable;
- fee/funding/risk schedule version and effective interval, where applicable;
- rounding policy ID/version and every quantization step;
- exact pre-rounded and final values;
- calculation status: AUTHORITATIVE, ESTIMATE, DISPLAY_ONLY, UNKNOWN or REJECTED.

A replay using the same immutable inputs and policy versions MUST produce the same exact result.

## 4. Operation matrix

| Operation | NEXUS-neutral invariant | Required authoritative source | Rounding boundary | Current disposition |
|---|---|---|---|---|
| Price tick normalization | Candidate price must satisfy the exact instrument tick rule; no silent mutation | Versioned instrument spec and order-side/price-band rules | Explicit order-construction policy only; otherwise reject | PARTIAL — validator exists, directional policy BLOCKED |
| Quantity/lot normalization | Candidate quantity must satisfy exact quantity unit, step, min/max and contract semantics | Versioned instrument spec and quantity-unit mapping | Explicit order-construction policy only; otherwise reject | PARTIAL — reference validation exists, venue mappings BLOCKED |
| Minimum notional | Use product-specific notional definition and price source | Instrument rules + venue market-order/reference-price rule | No rounding to force acceptance; evaluate exact required notional | BLOCKED for market/derivative semantics |
| Trading fees | Preserve actual fee amount and fee asset from execution/account event | Fill/commission event and effective fee schedule | Exchange's actual charged amount is ledger fact; estimates separately qualified | BLOCKED |
| Funding | Preserve actual funding cashflow, sign, asset and event time | Funding settlement/account event; published rate is estimate/input only | Exchange settlement precision and timing | BLOCKED |
| Realized P&L | Match closed quantity to position lots using an explicit position/accounting model | Fills, position mode, settlement rules and owner accounting policy | No rounding in matching/intermediates; venue settlement or approved journal boundary | BLOCKED |
| Unrealized P&L | A valuation estimate must identify mark/last/index/other price basis | Explicit price source and product valuation formula | No ledger rounding; display-only rounding isolated | BLOCKED |
| Initial/maintenance margin | Apply exact product and risk-tier rules, account mode and portfolio offsets | Venue risk brackets/account configuration | Venue-defined margin precision; NEXUS reservation uses conservative approved policy | BLOCKED |
| Liquidation | Distinguish venue trigger/estimated price from NEXUS risk estimate | Venue formula, mark-price rules, maintenance tiers, fees and account mode | No generic rounding; venue tick/trigger rules only after qualification | BLOCKED |
| FX/collateral valuation | No implicit conversion; conversion is a separately sourced valuation edge | Approved pair, source, timestamp, direction, haircut and fallback policy | Explicit haircut/rounding at approved valuation boundary | BLOCKED |
| Ledger posting/reconciliation | Balanced immutable journal; idempotent source-event identity; corrections are compensating events | Canonical execution/account events and approved chart/posting rules | Journal unit precision and rounding accounts are owner-approved | PARTIAL — NX-IF-003 design only |

The matrix is a work register, not a statement that the listed policies are implemented.

## 5. Operation contracts

### 5.1 Tick and lot normalization

**Known mathematical invariant:** price tick and quantity step are exact divisibility constraints against a specific immutable instrument specification. The existing reference validator can reject values that do not satisfy the supplied tick/step and min/max constraints.

**Important distinction:** validation is not normalization. NEXUS MUST NOT silently round an invalid price or quantity and submit the altered order.

If a strategy or order-construction component requests normalization, it must provide an explicit intent:
- price objective (preserve passive limit, avoid crossing, aggressive execution, or another named objective);
- side and order type;
- quantity objective (do not exceed requested exposure, meet a target exposure, or another named objective);
- allowed deviation bound and policy version.

The normalization function must return both the proposed value and a structured explanation of the adjustment. It must then re-run tick/step, min/max, minimum-notional, price-band, order-type and risk checks. If no unique safe result exists, reject.

**Not selected:** floor/ceiling/nearest mode for buy/sell prices or quantities; tie-breaking; market-order reference price; price-band-dependent tick schedules; quote-quantity spot semantics; contract-specific size multipliers.

### 5.2 Minimum notional and market-order reference values

For a limit order, a simple base-amount × price calculation may be dimensionally valid only after the instrument model proves the quantity unit and price dimensions match.

For market orders, a venue may apply a weighted-average or other reference price rather than a submitted limit price. Derivatives may define contract value independently of spot base quantity. NEXUS MUST use the exact venue/product rule and its reference window/source; it MUST NOT assume last trade, mark price or order-book midpoint.

A candidate that cannot be evaluated with complete current metadata is REJECTED for automated execution.

### 5.3 Trading fees

Separate the following concepts:
- **estimated fee/reserve:** pre-trade estimate used to reserve capacity;
- **actual execution fee:** immutable amount/asset reported by the venue for a fill or account event;
- **fee adjustment/rebate:** separate event with its own identity and provenance;
- **displayed fee estimate:** non-authoritative UI value.

The actual fee event is the ledger source of truth when the venue provides it. NEXUS MUST NOT overwrite actual fee with a recomputed estimate. If the venue does not provide a fee on the fill, the fee remains pending/unknown until authoritative account evidence or a qualified deterministic rule resolves it.

Fee schedule qualification must include maker/taker classification, account tier, instrument/product, discount token or rebate rules, fee currency, fee basis (filled notional/contract value/other), minimums, caps, effective interval, and rounding/precision behavior.

**Blocked:** fee rates, fee asset selection, maker/taker determination for each execution path, rebate treatment, fee rounding mode, fee event correction semantics and whether a venue's fee amount is per-fill or aggregated.

### 5.4 Funding

Funding is a cashflow, not a price adjustment and not an unrealized P&L component by default.

NEXUS must distinguish:
- predicted funding rate;
- published/settled funding rate;
- estimated funding amount;
- actual funding debit/credit event.

The actual account funding event is the ledger fact. An estimated funding calculation must bind to the exact product formula, position value basis, mark/reference price, funding timestamp, sign convention, settlement currency, eligibility/cutoff rules and rate version.

Funding estimation MUST NOT be booked as realized cashflow before the authoritative settlement event. A missing or delayed event remains pending and must be reconciled.

**Blocked:** rate formula, clamp/cap/floor, interval, position snapshot cutoff, mark-price basis, sign convention, settlement asset, precision, rounding, partial-position treatment and account-specific exceptions.

### 5.5 Realized P&L

Realized P&L is not a single universal number. NEXUS must keep separate projections:
- gross position P&L from matched position changes;
- trading fees;
- funding cashflows;
- other position-related cashflows/adjustments;
- net realized trading result;
- accounting realized result under the approved inventory/position policy.

The position matching method (for example average-entry, FIFO or another venue/account model) MUST be explicit and versioned. Position mode (one-way/hedge), close/reduce semantics, partial fills, flips, fees allocated to opening/closing lots, settlement asset and contract type affect the result.

The venue's displayed P&L is a reconciliation input, not automatically NEXUS's accounting policy. NEXUS must preserve the raw venue event and explain any projection difference.

**Blocked:** position-lot matching, average-entry recomputation, fee allocation, funding allocation, partial-close allocation, inverse/quanto realized P&L, settlement conversion and treatment of manual/external position changes.

### 5.6 Unrealized P&L

Every unrealized P&L value must declare its valuation basis:
- last traded price;
- mark price;
- index price;
- bid/ask or executable liquidation estimate;
- another explicitly defined source.

These bases are not interchangeable. A UI may show multiple named estimates, but Risk and liquidation logic must consume only the price basis mandated by the qualified product/account rules.

The result is an estimate until realized by a fill or authoritative settlement/account event. Leverage does not change gross position P&L mathematics; it changes margin requirements and therefore ratios such as return on margin.

**Blocked:** default display basis, risk valuation basis per product, stale-price policy, price source priority, mark/index construction, inverse/quanto formula qualification, settlement conversion and presentation policy.

### 5.7 Initial margin, maintenance margin and collateral

Margin is a venue/account risk rule, not merely notional divided by leverage. A complete qualification must capture:
- isolated/cross/portfolio margin mode;
- position and order risk tiers/brackets;
- maintenance margin rates and deductions;
- initial margin and leverage constraints;
- open-order margin treatment;
- fee-to-close and funding buffers, if applicable;
- portfolio offsets and eligible collateral;
- collateral conversion prices, haircuts and concentration limits;
- risk-limit transitions and account-specific overrides.

NEXUS must distinguish venue-reported margin from its own conservative reservation estimate. Unknown tier, missing collateral haircut, incomplete portfolio exposure or stale account state MUST block risk-increasing commands.

**Blocked:** every numeric margin formula, tier selection, cross-position offset, collateral eligibility, haircut, fee reserve, risk-limit boundary, precision and rounding policy.

### 5.8 Liquidation

Liquidation price is a product/account-specific risk output, not a universal function of entry price and leverage.

A qualified model must identify:
- trigger price source (typically a specifically defined mark/index construction, not assumed last trade);
- isolated/cross/portfolio account mode;
- maintenance margin tier and deductions;
- position direction, quantity and contract type;
- collateral balance and valuation/haircut;
- open orders, fees, funding and other liabilities;
- tier transitions, partial liquidation, auto-deleveraging and insurance mechanisms;
- price/quantity tick behavior and venue trigger semantics.

NEXUS must label its own output as an estimate and compare it with venue-reported liquidation/position risk fields. It MUST NOT use an unqualified generic formula to authorize exposure.

**Blocked:** all venue liquidation formulas, trigger rules, tier mechanics, partial liquidation, bankruptcy-price relation, fee/funding buffers and rounding.

### 5.9 FX and collateral conversion

FX conversion is a directed, timestamped valuation operation, not an implicit arithmetic convenience.

Every conversion requires:
- source asset and target asset;
- pair and direction;
- exact rate and price-source identity;
- source timestamp and maximum permitted age;
- bid/ask/mid/mark choice and conversion side;
- haircut or spread policy;
- fallback/source-switch policy;
- conversion graph/path and prohibition of cycles;
- rounding/precision boundary and policy version.

No stablecoin is assumed to be exactly equal to fiat USD. No asset is assumed to be worth its ticker nominal value. If a required conversion path is unavailable, stale or ambiguous, collateral valuation and any risk-increasing authorization fail closed.

**Blocked:** approved FX sources, conversion direction, stablecoin/fiat treatment, haircuts, source hierarchy, stale thresholds, fallback and accounting gain/loss treatment.

### 5.10 Ledger posting and reconciliation

The ledger records facts and approved accounting transformations; it must not silently replace facts with estimates.

Required separation:
1. immutable raw venue event;
2. canonical normalized event with provenance;
3. exact calculation result and policy version;
4. balanced journal transaction;
5. derived balances/positions/P&L projections;
6. reconciliation result and unresolved discrepancy.

Execution fill, fee and funding events require stable source identity and idempotent posting. Corrections/busts must create compensating/reversal entries; historical journal rows are not rewritten. Posting must be atomic: either the complete balanced journal transaction and inbox identity commit, or neither does.

A fill may remain in FILL_PENDING_LEDGER until its required journal posting is durable and the projection watermark advances. Risk must not double-count or release exposure merely because an event was received.

The accounting policy must specify chart of accounts, asset precision, realized/unrealized classification, inventory/position matching, fee/funding accounts, transfers, conversions, rounding accounts, correction policy and reconciliation tolerances. No tolerance may conceal a missing or duplicated event.

**Current dependency:** NX-IF-003 remains PROPOSED. This document adds financial-operation requirements; it does not accept or implement the ledger contract.

## 6. Calculation pipeline and rounding-point discipline

A conforming calculation pipeline should follow this order, with operation-specific exceptions only when official venue semantics require them:

1. Validate source identity, freshness, completeness and effective-time applicability.
2. Resolve immutable instrument/product/account configuration and versions.
3. Parse exact scalar values and attach dimensions.
4. Validate units and contract semantics before arithmetic.
5. Calculate exact intermediate values (decimal/rational); do not round.
6. Apply the explicitly qualified operation formula and ordering.
7. At a documented external boundary only, apply the operation-specific quantization rule.
8. Revalidate all downstream constraints using the quantized submitted/posting value.
9. Persist exact inputs, pre-rounded value, quantized value, policy version and provenance.
10. Reconcile against authoritative venue/account evidence.

This is a recommended common skeleton, not permission to reorder a venue formula. If official semantics prescribe a different sequence, encode that sequence exactly and add a counterexample test proving why it differs.

## 7. Required conformance fixture format

Every operation fixture must include at minimum:

- fixture ID and schema version;
- venue/product/account mode or explicit `VENUE_NEUTRAL_MATH`;
- instrument identity and spec version, where relevant;
- exact inputs with dimensions;
- source event IDs and timestamps;
- formula identifier/version;
- operation ordering;
- intermediate exact values;
- rounding mode, scale/step and rounding point, or explicit `NONE`;
- exact expected output and output unit;
- expected status (AUTHORITATIVE / ESTIMATE / DISPLAY_ONLY / REJECTED / UNKNOWN);
- negative variants: missing metadata, wrong unit, stale source, unknown tier, unsupported contract type, boundary and sign/tie cases.

Golden vectors must be independently hand-derived or checked against a separate exact rational oracle. Tests must cover positive and negative values, exact ties, repeating rationals, boundary values, partial fills, corrections, missing/late events and replay determinism where applicable.

## 8. Venue qualification dossier

No venue is qualified by this document. Before a venue/product can be enabled, the dossier must contain:

1. official instrument metadata and version/effective-time behavior;
2. tick bands, lot/quantity semantics, min/max and min-notional rules;
3. contract multiplier, denomination, settlement and inverse/linear/quanto semantics;
4. fee schedule, tier/discount rules and actual fee event examples;
5. funding formula, interval, cutoff, settlement asset and actual funding event examples;
6. mark/index price methodology and timestamp/freshness behavior;
7. initial/maintenance margin tiers, deductions, collateral haircuts and account-mode behavior;
8. liquidation/partial-liquidation/ADL rules;
9. FX/collateral valuation source and fallback policy;
10. private API event identity, replay/correction and reconciliation semantics;
11. sanitized captured fixtures plus exact conformance tests for all applicable operations;
12. legal/account eligibility for the owner's nationality, residence, entity and product.

If an item is not applicable, the venue must explicitly say so or provide authoritative evidence. Missing data remains UNKNOWN, never zero or inferred.

## 9. Current research evidence and its limits

The following official documentation demonstrates why one generic policy is unsafe. It is comparative evidence only and does not select or qualify any venue:

- Binance Spot filters distinguish price tick, lot step, min/max quantity and minimum notional; market-order notional may use a prior-trade average rather than a submitted price: https://github.com/binance/binance-spot-api-docs/blob/master/filters.md
- OKX instrument metadata distinguishes tick size, lot size, min size, spot base-currency quantity and derivative contract count; linear and inverse contracts have different settlement and P&L denomination: https://www.okx.com/docs-v5/en/
- Bybit's linear and inverse P&L documentation uses different dimensional formulas and settlement assets; its examples also distinguish unrealized position P&L from fees/funding included in realized/closed P&L: https://www.bybit.com/en/help-center/article/Profit-Loss-calculations-USDT-Contract and https://www.bybit.com/en/help-center/article/Profit-Loss-calculations-Inverse-Contracts
- Bybit funding documentation describes product-specific position-value bases for linear and inverse contracts: https://www.bybit.com/en/help-center/article/Funding-fee-calculation
- Bybit order-cost documentation distinguishes estimated initial margin and estimated opening/closing fees from fees actually charged on execution: https://www.bybit.com/en/help-center/article/Order-Cost-USDT-Contract

These sources are not a complete current venue dossier. Their rules must not be copied to another venue or assumed to apply to every account/product.

## 10. Acceptance criteria for this design package

This package can move from PROPOSED to owner-review-ready only when:

- [x] Financial operations and their separate policy boundaries are enumerated.
- [x] Global exactness, dimensions, provenance and no-implicit-rounding invariants are explicit.
- [x] Estimated values are separated from authoritative venue/account facts.
- [x] Venue-specific and owner-controlled unknowns are explicitly BLOCKED.
- [x] Required venue qualification dossier and fixture schema are defined.
- [x] Cross-document consistency review completed against NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006.
- [ ] Owner review of accounting and valuation policy boundaries completed.
- [ ] Exact venue/product/account selection and legal eligibility completed before venue-specific rules are populated.

This is not an implementation gate and does not pass G0/G1.

## 11. Next bounded work package

**WP-FIN-ROUND-001 — Contract consistency and independent math fixtures**

1. Review this contract against NX-ADR-005, NX-IF-003, ТЗ-NX-005 and ТЗ-NX-006; record contradictions only.
2. Create venue-neutral mathematical fixtures only where the formula is truly universal (dimensional multiplication, rational reciprocal identity, sign conventions as explicitly parameterized).
3. Keep venue-dependent fee, funding, margin, liquidation, valuation and accounting examples BLOCKED until a product/account is selected and qualified.
4. Do not add generic production rounding defaults or numeric limits.
5. Publish a finite disposition: ACCEPTED DESIGN / OWNER DECISION REQUIRED / VENUE QUALIFICATION REQUIRED / DEFERRED.

No production calculator, Risk Engine, Ledger or live execution work is authorized by this package.


### 10.1 Cross-document consistency review (2026-11-14)

Reviewed the exact current branch versions of:
- NX-ADR-005, blob `e66701d9ffadbf93343988b7976913e83abe834a`;
- NX-IF-003, blob `62d93913d88f0c0af4eb5ad623160b9770acac76`;
- ТЗ-NX-005, blob `d34ffa9cd703e9b6d351e3df129d9feabe093462`;
- ТЗ-NX-006, blob `53de605aa5c391920f35b928ee848c402b5d5114`.

**Result: no blocking contradiction found in the reviewed financial-operation boundaries.**
- NX-ADR-005 requires exact instrument semantics and operation-specific rounding; this contract makes the per-operation decision and qualification boundary explicit.
- ТЗ-NX-005 requires exact exposure/margin calculations, explicit cross-currency source/quality/haircut and fail-closed behavior; this contract preserves Risk as a consumer of qualified valuation inputs and does not claim margin/liquidation formulas.
- ТЗ-NX-006 requires exact values, explicit rounding boundaries, immutable source evidence and UNKNOWN for missing/stale FX; this contract adds the missing operation-level rounding/provenance and estimate-versus-fact distinctions.
- NX-IF-003 separates fill, fee, funding and P&L effects and requires atomic journal posting/corrections; this contract does not change that ownership and explicitly leaves posting rules and owner accounting decisions open.

**Residual design gaps remain intentionally open:** position/inventory matching, fee and funding settlement details, venue/product/account formulas, valuation source hierarchy, collateral haircuts, journal precision/rounding accounts, and numeric production limits. This review does not accept any of those policies or pass G0/G1.
