# NX-REF-DOMAIN-001 — Instrument Specification Reference Model

**Status:** TEST-ONLY reference slice; schema and semantics PROPOSED  
**Version:** 0.1  
**Date:** 2026-11-14  
**Related:** NX-ADR-005, NX-ARCH-003, NX-IF-001, NX-IF-002, ТЗ-NX-001, ТЗ-NX-004, ТЗ-NX-005, ТЗ-NX-006.

## 1. Purpose and boundary

This slice turns a narrow part of NX-ADR-005 into executable, venue-neutral conformance examples: immutable instrument metadata, explicit unknown/not-applicable handling, exact tick and quantity increments, quantity bounds and minimum notional.

It is not a production registry, venue adapter, risk engine or execution authorization. The reference model uses the existing arbitrary-precision Python decimal oracle. Production language, bounded numeric representation, wire schema and persistence remain unselected.

## 2. Implemented model

`foundation/reference-model/instrument_spec.py` defines an immutable `InstrumentSpec` snapshot with:

- immutable internal ID plus venue / market / native instrument identity;
- base, quote and settlement assets;
- explicit SPOT / LINEAR / INVERSE / QUANTO / UNKNOWN contract type;
- explicit lifecycle status;
- monotonically assigned snapshot version (ordering authority is not implemented);
- exact positive tick size, quantity step and minimum quantity;
- optional maximum quantity and minimum notional;
- explicit minimum-notional applicability: REQUIRED / NOT_APPLICABLE / UNKNOWN;
- optional contract multiplier, required for derivative contract types;
- quantity unit, source identifier, raw payload SHA-256 and fetch/effective timestamps.

The fixture `instrument-spec-fixture-v1.json` is synthetic. It is not an exchange response and must not be represented as official venue evidence.

## 3. Validation behavior

The reference validator:

1. rejects malformed identity/provenance fields and invalid version/timestamps;
2. rejects non-positive tick, quantity step, minimum quantity and supplied optional positive constraints;
3. rejects inconsistent maximum/minimum quantity;
4. rejects missing required minimum notional and ambiguous UNKNOWN applicability;
5. requires a multiplier for derivative contract types and rejects one on SPOT;
6. blocks non-ACTIVE lifecycle state and UNKNOWN contract type;
7. blocks all derivative models (LINEAR / INVERSE / QUANTO) because their notional/exposure formulas are not implemented; blocks spot quote-quantity semantics because this slice only defines base-quantity checks;
8. validates positive order price/quantity, exact tick/lot divisibility, min/max quantity and price × base-quantity minimum notional without binary floating point.

`NOT_APPLICABLE` is an explicit declaration, not an inferred absence. A missing field cannot silently become zero, one or a guessed default.

## 4. Acceptance evidence

The dedicated test suite covers valid exact order values, off-tick and off-step rejection, minimum/maximum quantity, minimum notional, explicit UNKNOWN vs NOT_APPLICABLE, suspended/unknown instruments, unsupported inverse contracts, multiplier requirements, invalid provenance and non-positive order values.

GitHub Actions must execute this suite on Python 3.11, 3.12 and 3.13 at the exact branch HEAD before this slice can be marked verified. Test count and run URL are recorded only after the run completes.

## 5. Deliberate exclusions

- official venue fixtures, API pagination, adapter parsing and schema evolution;
- freshness thresholds, source authority, raw payload storage and hash verification;
- registry persistence, effective-time conflict resolution and version monotonicity;
- spot base-vs-quote order quantity semantics;
- contract notional/exposure, inverse/quanto P&L, fees, funding, margin and leverage;
- price bands, supported order types, time-in-force and position mode;
- account risk, reservations, approval, signing or execution;
- production numeric bounds, Rust/backend/client conformance and fuzzing.

The check `price × quantity` is only a narrow demonstration for the fixture's base-quantity spot-like semantics. It is not a universal notional formula for derivatives or quote-quantity spot orders.

## 6. Required next work

- Define a typed notional rule and quantity-denomination model before extending order validation.
- Add authoritative, version-pinned venue fixtures only after exact product/account/jurisdiction qualification.
- Specify metadata freshness, effective-time ordering, source precedence and change-impact policy.
- Add canonical serialization and cross-language golden vectors.
- Keep inverse/quanto non-tradable until reviewed formulas and independent golden tests exist.

**Disposition:** useful executable reference slice; NX-ADR-005 remains PROPOSED and no production instrument is thereby approved.
