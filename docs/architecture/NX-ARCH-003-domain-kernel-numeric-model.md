# NX-ARCH-003 — Domain Kernel & Exact Numeric Model

**Status:** PROPOSED — owner/architecture review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** Venue-neutral pure domain primitives and exact numeric semantics required by market data, instrument rules, risk, execution and ledger.  
**Related:** NX-ADR-001, NX-ADR-005, NX-IF-001..004, ТЗ-NX-001, ТЗ-NX-004, ТЗ-NX-005, ТЗ-NX-006, NX-DOC-REVIEW-001.

## 1. Purpose

NEXUS requires a small, deterministic domain kernel that preserves exact values and explicit units across all subsystems. It must not inherit UI formatting, exchange wire formats, database representations or strategy-specific assumptions.

This document defines a first conformance slice. It does not select the final production language, database, serialization format or numeric library.

## 2. Core numeric representation

A finite base-10 value is represented mathematically as:

`value = coefficient × 10^{-scale}`

The canonical domain representation must preserve the exact value, not a binary floating-point approximation.

Requirements:

- coefficient is a signed integer;
- scale is a non-negative integer;
- zero has one canonical representation;
- trailing decimal zeros are removed from canonical form without changing value;
- parsing accepts an explicitly defined decimal grammar and rejects exponent notation unless a separate wire adapter explicitly expands it without loss;
- serialization uses a canonical decimal string or an equivalently lossless integer/scale encoding;
- binary floating point is prohibited as the authoritative representation for price, quantity, fee, balance, margin, notional and P&L;
- overflow must be explicit and fail closed in bounded production representations.

The Python reference oracle in `foundation/reference-model` uses arbitrary-precision integers to establish mathematical expectations. It is not a production runtime component and does not define production bounds.

## 3. Supported first-slice operations

The first conformance slice covers:

1. strict decimal parsing and canonical formatting;
2. exact equality and ordering;
3. exact addition and subtraction;
4. exact multiplication;
5. exact rescaling/quantization only when no information is discarded;
6. positive-step divisibility for tick/lot validation;
7. exact rational division with reduced numerator/denominator;
8. exact finite-decimal conversion where the reduced denominator contains only factors 2 and 5;
9. explicit-scale quantization only when a caller supplies a named rounding mode.

General decimal division and rounding were excluded from the initial scalar slice. NX-REF-DOMAIN-005 now adds an isolated test-only exact-rational division oracle and explicit quantization modes. This does not approve a rounding mode for any financial operation. Square roots and transcendental functions remain open. NX-REF-DOMAIN-007 adds a test-only bounded admission context with caller-supplied limits and preflight checks; it does not select production limits or prove resource safety. NX-REF-DOMAIN-008 adds versioned scalar wire encodings; cross-language conformance and event/command integration remain open. No implicit rounding is permitted.

## 4. Units and dimensional safety

A numeric scalar is not automatically a price, quantity, currency amount or contract count. Domain wrappers must carry explicit semantic types and units.

Minimum future typed wrappers:

- Price + quote currency + instrument identity/spec version;
- Quantity + base/contract unit + instrument identity/spec version;
- Money + currency;
- Rate + declared denominator/time basis;
- Multiplier/contract value + settlement semantics;
- Timestamp with explicit clock source/precision;
- TickSize and QuantityStep as positive validated increments.

Operations between incompatible units must be rejected at the type/domain boundary. NX-REF-DOMAIN-003 adds test-only AssetAmount, Money, Price, Notional and instrument-scoped ContractCount wrappers. NX-REF-DOMAIN-004 adds a spec-version-pinned quantity-unit mapping. These remain reference models, not production domain integration.

## 5. Instrument-rule validation

A candidate price/quantity is valid only when:
- the instrument specification is known, current and versioned;
- the tick/lot step is known and positive;
- exact divisibility is satisfied;
- min/max quantity, min notional, price bounds and contract semantics are independently checked;
- unknown metadata is never replaced by zero, one or a guessed default.

Rounding to a venue step is a separate policy decision. A helper that silently rounds an invalid order value is prohibited.

## 6. Reference-oracle boundary

The Python implementation is deliberately dependency-free and uses arbitrary-precision integer coefficients. Its role is to produce an independent expected result for future production-language implementations. The suite also includes 1,000 deterministic seeded property cases cross-checked against Python's independent rational `fractions.Fraction` representation; this strengthens the mathematical oracle but is not fuzzing or production-runtime evidence.

It is not:
- an exchange adapter;
- a trading engine;
- a financial ledger;
- a production numeric type;
- a performance implementation;
- evidence of Rust/WASM or backend conformance.

Production implementation must match the golden vectors and add bounded-overflow, serialization, fuzz/property and cross-language tests. NX-REF-DOMAIN-007/008 now provide initial test-only bounded-admission and scalar-wire references; production profiles, implementation and cross-language evidence remain open.

## 7. Acceptance criteria for this slice

- [x] Decimal grammar and canonicalization are implemented and covered by reference tests.
- [x] No float conversion occurs in the reference path (source inspection; exact arithmetic CI).
- [x] Add/subtract/multiply/compare are exact (golden vectors and 1,000 rational-oracle property cases).
- [x] Exact quantization rejects any operation that would discard non-zero digits.
- [x] Tick/lot divisibility rejects non-positive steps.
- [x] Negative, zero, large magnitude and high-scale values have test coverage.
- [x] Division/rounding are not exposed as accidental defaults.
- [x] Golden vectors are language-neutral and reusable by production implementations (v1.0.0, 15 cases).
- [x] Deterministic property checks compare 1,000 generated cases against an independent rational representation.
- [ ] Fuzz/property coverage with broader input generation and cross-language conformance.
- [x] Test-only bounded numeric context rejects configured scale, coefficient, rational and intermediate-growth excess before arithmetic expansion.
- [x] Test-only canonical scalar decimal/rational wire encodings reject non-canonical representations and require input-size budgets.
- [ ] Production numeric bounds and overflow behavior are decided before live financial calculations.
- [ ] Unit-bearing Price/Quantity/Money types are separately specified before order/risk/ledger integration.

## 8. Open decisions

- Production implementation language and shared backend/client boundary.
- Production bounded numeric type and maximum coefficient/scale (test-only limits are caller-supplied fixtures, not production values).
- Production overflow and checked-operation policy for every financial calculation.
- Cross-language adoption and integration of canonical scalar wire encoding into typed events/commands.
- Explicit rounding modes and per-operation ownership (venue normalization, fees, P&L, display only).
- Currency and contract dimensional model.
- Whether inverse/quanto instruments are deferred from the first supported product family.

## 9. Verification status

The reference oracle is a conformance aid only. It does not establish production readiness. The first-slice scalar acceptance criteria above are verified at reference-model level; production bounds, units, fuzzing and cross-language conformance remain open.

GitHub Actions run [#43590395882](https://github.com/PandaGarry/NEXUS/actions/runs/43590395882) passed exact PR HEAD `3fb21aa53c9d6c72afcf6761493388f417fcb56b`: 11 exact-decimal tests (including 1,000 deterministic rational-oracle property cases) and 21 gateway tests on Python 3.11, 3.12 and 3.13.

**Status remains PROPOSED.**


## 10. Bounded numeric and scalar wire reference extensions

NX-REF-DOMAIN-007 provides an explicit BoundedNumericContext. All NumericLimits are mandatory; there is no global default. It preflights input length, scale alignment, multiplication growth, division expansion, rational bounds and quantization growth. Division uses conservative pre-reduction checks and may reject some reducible quotients. These are reference semantics only; production limits remain unselected.

NX-REF-DOMAIN-008 defines nxd1 decimal and nxr1 rational scalar encodings. Parsers require max_chars and reject non-canonical or unreduced values. These encodings carry no currency, instrument, provenance, timestamp, command identity or signature semantics.


Latest bounded numeric/wire evidence: PR run [#43595199511](https://github.com/PandaGarry/NEXUS/actions/runs/43595199511) passed exact PR HEAD `fddd03f59baa159d8ed345691221c2446b0f60e3` on Python 3.11–3.13; ten isolated suites, 172 tests per runtime / 516 matrix executions. This remains reference-only and does not select production limits.


Latest exact PR-head verification: run [#43595449902](https://github.com/PandaGarry/NEXUS/actions/runs/43595449902) passed commit `6200bae99e9b7ce865487a40312d0074c0e2a276` on Python 3.11–3.13. Ten suites, 172 tests per runtime / 516 matrix executions. Production limits and resource-safety proof remain open.
