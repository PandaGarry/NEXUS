# NX-REF-DOMAIN-008 — Canonical Numeric Wire Encoding v1

**Status:** TEST-ONLY REFERENCE / PROPOSED WIRE CONTRACT  
**Authority:** None. This is a scalar numeric encoding, not the final NEXUS event/API schema.

## 1. Scope

The reference defines deterministic textual encodings for exact scalar decimals and reduced rationals. It avoids JSON numbers and binary floating-point parsing for authoritative financial values.

## 2. Decimal encoding

Grammar: nxd1:<coefficient>:<scale>

- coefficient is a canonical signed base-10 integer string: 0, a positive integer without leading zeros, or a negative integer without leading zeros.
- scale is a canonical non-negative integer string without leading zeros (except 0).
- zero is exactly nxd1:0:0.
- coefficient/scale must already be normalized: non-zero coefficients have no trailing decimal zero while scale is positive.

Examples: nxd1:12345:2 represents 123.45; nxd1:-1:8 represents -0.00000001.

## 3. Rational encoding

Grammar: nxr1:<numerator>:<denominator>

- numerator uses the same canonical signed integer grammar;
- denominator is a canonical positive integer;
- numerator/denominator must be reduced by GCD;
- zero is exactly nxr1:0:1.

Example: nxr1:1:300 represents exactly 1/300.

## 4. Parser requirements

Parsers require a caller-supplied positive max_chars and reject oversized input before splitting or integer conversion. BoundedNumericContext uses the separate max_wire_chars budget for encoded input and output; raw decimal literals use max_input_chars. They reject unsupported versions, extra/missing fields, non-canonical integer forms, negative/zero denominators, non-reduced rationals and non-normalized decimal coefficient/scale pairs.

BoundedNumericContext integrates these parsers with its mandatory max_input_chars, coefficient, scale and rational digit budgets.

## 5. Versioning and limitations

- nxd1 and nxr1 are independent scalar wire versions.
- Any grammar, normalization or semantic change requires a new version; readers must not reinterpret v1 under changed rules.
- The encoding does not include currency, asset, instrument ID, instrument-spec version, quantity kind, timestamp, source, rounding policy or provenance. Those belong in separately versioned typed domain/event contracts.
- It does not define database storage, signatures, hashing, command canonicalization, API compatibility or message framing.
- Canonical text is not by itself authentication or authorization evidence.

## 6. Verification

Round-trip and negative tests plus language-neutral vectors in numeric-wire-golden-v1.json (version 1.0.0) cover decimal/rational values, values beyond JavaScript's safe integer range, version mismatch, malformed shape, leading zeros, explicit plus, negative zero, invalid denominator, unreduced fractions, non-normalized decimal values and mandatory input-size budgets. CI runs Python 3.11–3.13. Cross-language vectors and signature/canonical-command integration remain open.


**CI evidence:** PR run [#43595199511](https://github.com/PandaGarry/NEXUS/actions/runs/43595199511) passed exact PR HEAD `fddd03f59baa159d8ed345691221c2446b0f60e3` on Python 3.11–3.13. The numeric wire suite ran 11 tests per runtime; the complete matrix ran 172 tests per runtime / 516 test executions. This is reference-only; cross-language adoption remains open.
