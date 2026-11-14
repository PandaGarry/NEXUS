# NX-ARCH-005 — Language-Neutral Conformance Fixture & Runner Contract

**Status:** PROPOSED — architecture/owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Work item:** GitHub Issue #15  
**Related:** NX-ARCH-003/004, NX-IF-001..005, NX-ADR-002/005/007, NX-REF-DOMAIN-001..010, NX-SEC-001.

## 1. Purpose and boundary

Define one language-neutral contract for deterministic conformance cases and the evidence protocol used to compare independent implementations.

The immediate target is future Python-reference/Rust-domain comparison. This document does not implement a runner, choose a JSON Schema validator, select a serialization crate, approve production numeric limits, or authorize a Rust workspace. Existing v1 fixture files remain valid historical artifacts and are not silently reinterpreted.

A fixture is an executable specification of one bounded behavior. It is not venue evidence, a trading authorization, a production policy or proof that an entire subsystem is correct.

## 2. Repository audit — current baseline

The current reference-model tree contains these language-neutral fixture families:

| File | Current shape | Scope / limitation |
|---|---|---|
| `golden-vectors-v1.json` | `version`, `representation`, `cases[{id,op,...}]` | Exact scalar decimal operations; expected comparison values include integers. |
| `division-golden-vectors-v1.json` | `version`, `representation`, `cases[{id,op,...}]` | Reduced rational division and explicit quantization. |
| `numeric-wire-golden-v1.json` | `version`, `wire_versions`, `cases[{id,kind,wire,...}]` | Canonical decimal/rational wire parse and rejection examples. |
| `financial-math-golden-v1.json` | `schema_version`, `suite`, `authority`, `rounding`, `provenance`, `cases[{id,operation,inputs,expected}]` | Synthetic dimensional arithmetic only. |
| `instrument-spec-fixture-v1.json` | `schema_version`, `fixture_notice`, `instrument` | One synthetic instrument metadata snapshot, not an operation/case suite. |

The files are deliberately not rewritten by this proposal. Their envelopes differ, invalid cases are represented differently, and there is no common stable rejection-class contract. Current CI executes Python test modules directly; it does not run a shared cross-language protocol.

The complete tracked repository tree at the audited branch head contains no `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, Rust source tree or Rust runner. Therefore Rust execution and Rust/Python differential conformance are not presently available. This is an observed repository-state blocker, not a reason to create an unreviewed workspace.

## 2.1 Legacy fixture migration assessment

The first migration pass must preserve the original v1 bytes and derive each new expected outcome from the existing reference implementation/tests, not from a mechanical guess.

| Legacy file | Proposed mapping | Migration class | Required review before conversion |
|---|---|---|---|
| `golden-vectors-v1.json` | Root `version` -> suite version; `representation` -> suite description/provenance; each `id/op` -> `id/operation`; operands -> `input`; `expected` -> VALUE outcome. | Mostly structural | Define stable operation names and preserve integer compare outputs as integers; add no inferred error cases. |
| `division-golden-vectors-v1.json` | Same case mapping; numerator/denominator and rounding fields remain exact strings/enums in `input`; expected rational or decimal is a typed VALUE. | Mostly structural | Confirm each operation's denominator/sign/rounding semantics and stable operation identifiers. |
| `numeric-wire-golden-v1.json` | `kind` selects decimal/rational parser operation; expected coefficient/scale or numerator/denominator becomes typed VALUE; invalid kinds become REJECT. | Semantic annotation required | Existing invalid cases do not declare stable rejection classes. Run the Python oracle, inspect its parser contract, then assign and review each class; do not infer from case ID or kind alone. |
| `financial-math-golden-v1.json` | Existing `schema_version/suite/authority/rounding/provenance` map directly to suite metadata; `operation/inputs/expected` map directly to case fields. | Near-direct | Preserve all units, instrument identities, rational fields and non-authorizing authority marker. Do not widen scope into fees, funding or venue formulas. |
| `instrument-spec-fixture-v1.json` | Treat `instrument` as an input object to a future explicit `instrument_spec.validate` case. | New expected behavior required | The file is a snapshot, not a test case: expected accept/reject outcome, validation operation and rejection classes must be derived from the current instrument-spec contract/tests. No automatic expected result is assumed. |

Migration order should begin with the scalar decimal and rational suites, then numeric-wire rejection annotation, then financial-math typed-value preservation. Instrument-spec conversion is last because it requires an explicit operation and expected outcome. Existing direct Python unit tests remain the baseline during migration; a converter must be one-way, deterministic and covered by its own tests.

## 3. Proposed fixture envelope v1

New cross-language suites SHOULD use a common top-level envelope. The canonical fixture contract identifier is `nexus.conformance.fixture`; the contract version is independent from the suite's semantic version.

Illustrative shape:

```json
{
  "fixture_contract": "nexus.conformance.fixture",
  "fixture_contract_version": "1.0.0",
  "suite": {
    "id": "nexus.numeric.scalar",
    "version": "1.0.0",
    "domain": "EXACT_NUMERIC",
    "authority": "TEST_ONLY_NON_AUTHORIZING"
  },
  "provenance": {
    "class": "SYNTHETIC_HAND_DERIVED",
    "source_refs": ["NX-ARCH-003", "NX-REF-DOMAIN-008"]
  },
  "cases": [
    {
      "id": "decimal-add-001",
      "operation": "decimal.add",
      "input": {
        "a": "0.1",
        "b": "0.02"
      },
      "expect": {
        "outcome": "VALUE",
        "value": "0.12"
      }
    },
    {
      "id": "decimal-invalid-001",
      "operation": "decimal.parse",
      "input": {
        "text": "1e3"
      },
      "expect": {
        "outcome": "REJECT",
        "error_class": "NUMERIC.INVALID_SYNTAX"
      }
    }
  ]
}
```

This is an illustrative contract, not a published JSON Schema or accepted wire standard.

### 3.1 Required envelope fields

- `fixture_contract`: fixed identifier.
- `fixture_contract_version`: semantic version of the envelope and runner-visible semantics.
- `suite.id`: stable namespace, unique within the repository.
- `suite.version`: semantic version of the suite's expected behavior.
- `suite.domain`: bounded domain namespace such as `EXACT_NUMERIC`, `DIMENSIONAL_MATH`, `INSTRUMENT_SPEC` or `EXECUTION_STATE`.
- `suite.authority`: must be explicitly non-authorizing for synthetic/reference suites.
- `suite.numeric_profile_id`: required whenever a case is bounded by numeric/resource limits; it names a reviewed test profile, never an implicit production default. Omit it for explicitly unbounded mathematical-oracle suites; do not use a magic `UNBOUNDED` profile identifier.
- `provenance.class`: e.g. `SYNTHETIC_HAND_DERIVED`, `REFERENCE_MODEL_DERIVED` or a separately reviewed source class.
- `provenance.source_refs`: stable repository document or evidence identifiers.
- `cases`: non-empty ordered array of uniquely identified cases.

### 3.2 Case contract

Every case has exactly:
- `id`: stable, unique within the suite version;
- `operation`: namespaced operation identifier;
- `input`: operation-specific JSON object;
- `expect`: one tagged outcome.

A successful outcome is `{"outcome":"VALUE","value":...}`. A rejected outcome is `{"outcome":"REJECT","error_class":"NAMESPACE.STABLE_CLASS"}`. The two forms are mutually exclusive. An expected rejection MUST NOT depend on exception names, human-readable messages, debug strings or stack traces.

Expected values may be strings, booleans, integers for non-financial enumerated results, arrays or typed objects. Financial scalar values MUST be encoded as canonical decimal strings or explicit rational numerator/denominator strings; JSON floating-point numbers are prohibited. Units and identity-bearing dimensions must be present in expected typed values, not inferred by the runner.

### 3.3 Stable rejection classes

The initial proposed class families are:

- `SCHEMA.INVALID`, `SCHEMA.UNSUPPORTED_VERSION`, `SCHEMA.MISSING_REQUIRED_FIELD`;
- `NUMERIC.INVALID_SYNTAX`, `NUMERIC.INVALID_WIRE`, `NUMERIC.UNSUPPORTED_WIRE_VERSION`, `NUMERIC.NON_CANONICAL`, `NUMERIC.DIVISION_BY_ZERO`, `NUMERIC.INEXACT_RESULT`, `NUMERIC.INVALID_STEP`, `NUMERIC.OVERFLOW`, `NUMERIC.RESOURCE_LIMIT`;
- `DOMAIN.UNIT_MISMATCH`, `DOMAIN.IDENTITY_MISMATCH`, `DOMAIN.UNSUPPORTED_OPERATION`;
- `INSTRUMENT.UNKNOWN_SPEC`, `INSTRUMENT.INVALID_RULE`, `INSTRUMENT.STALE_VERSION`;
- `STATE.INVALID_TRANSITION`, `STATE.STALE_EPOCH`, `STATE.DUPLICATE_IDENTITY`.

This is a starting catalogue. Each operation suite must declare the subset it can emit. A new implementation-specific failure must be mapped to a stable class or treated as a harness failure; it must not invent a success result or silently coerce the input.

### 3.4 Initial operation registry and migration contract

The following stable operation identifiers are proposed for the first normalized suites. They name mathematical/domain behavior, not Python function names. Each implementation maps these identifiers to its own code without sharing implementation internals.

| Suite domain | Operation ID | Canonical input | VALUE result | Rejection classes initially in scope |
|---|---|---|---|---|
| EXACT_NUMERIC | `decimal.parse` | `{"text":"..."}` | Canonical decimal string | `NUMERIC.INVALID_SYNTAX` |
| EXACT_NUMERIC | `decimal.add`, `decimal.subtract`, `decimal.multiply` | `{"a":"...","b":"..."}` | Canonical decimal string | No expected rejection in current golden set |
| EXACT_NUMERIC | `decimal.compare` | `{"a":"...","b":"..."}` | Integer exactly `-1`, `0` or `1` | No expected rejection in current golden set |
| EXACT_NUMERIC | `decimal.quantize_exact` | `{"value":"...","scale":N}` | Canonical decimal string | `NUMERIC.INEXACT_RESULT`, invalid scale maps to schema/domain validation pending explicit contract |
| EXACT_NUMERIC | `decimal.multiple_of` | `{"value":"...","step":"..."}` | Boolean | `NUMERIC.INVALID_STEP` |
| EXACT_NUMERIC | `rational.divide_exact` | `{"a":"...","b":"..."}` decimal operands | Reduced rational object `{"numerator":"...","denominator":"..."}` | `NUMERIC.DIVISION_BY_ZERO` |
| EXACT_NUMERIC | `rational.to_decimal_exact` | Reduced rational object | Canonical decimal string | `NUMERIC.INEXACT_RESULT` |
| EXACT_NUMERIC | `rational.quantize` | Reduced rational object plus explicit non-negative scale and explicit rounding enum | Canonical decimal string | `NUMERIC.INEXACT_RESULT` for UNNECESSARY mode |
| EXACT_NUMERIC | `numeric_wire.parse_decimal` | `{"wire":"...","max_chars":N}` | Typed decimal object `{"coefficient":"...","scale":N}` | `NUMERIC.INVALID_WIRE`, `NUMERIC.UNSUPPORTED_WIRE_VERSION`, `NUMERIC.NON_CANONICAL`, `NUMERIC.RESOURCE_LIMIT` |
| EXACT_NUMERIC | `numeric_wire.parse_rational` | `{"wire":"...","max_chars":N}` | Typed rational object `{"numerator":"...","denominator":"..."}` | `NUMERIC.INVALID_WIRE`, `NUMERIC.UNSUPPORTED_WIRE_VERSION`, `NUMERIC.NON_CANONICAL`, `NUMERIC.RESOURCE_LIMIT` |
| DIMENSIONAL_MATH | `financial.spot_notional`, `financial.linear_contract_notional`, `financial.inverse_contract_base_exposure`, `financial.partial_fill_aggregation_math` | Existing typed `inputs` object, migrated without dropping units/identity | Existing typed `expected` object, migrated without dropping units/identity | `DOMAIN.UNIT_MISMATCH`, `DOMAIN.IDENTITY_MISMATCH` only where explicit negative cases are added |
| INSTRUMENT_SPEC | `instrument_spec.validate_limit_order` | Full instrument snapshot plus price/quantity | Explicit `{"outcome":"VALUE","value":{"valid":true}}` | Deferred until a dedicated fixture specifies invalid cases and exact stable rejection mapping |

For `rational.divide_exact`, the current legacy vector takes decimal operands `a` and `b`; the normalized suite must preserve that public semantic input shape as `{"a":"...","b":"..."}` and return the reduced rational. The numerator/denominator form is for operations whose input is already a rational. These forms MUST NOT be conflated.

The first migration should not add synthetic rejection cases just to populate a taxonomy. A rejection class enters a suite only when a legacy case or a separately reviewed negative vector proves that behavior.

#### Reference-model exception mapping and remaining gaps

The exact-decimal oracle exposes typed exceptions (`InvalidDecimal`, `InexactQuantization`, `InvalidStep`, `DivisionByZero`, `InexactDivision`). The numeric-wire reference slice now also exposes typed subclasses with stable `error_class` values for malformed shape, unsupported wire version, non-canonical encoding and resource-budget exhaustion. All subclasses remain catch-compatible with the existing `NumericWireError` base class, preserving callers that depend on the old API.

The normalized adapter MUST read the stable machine-readable class; it MUST NOT parse exception messages. The mapping is covered by a dedicated test in `test_numeric_wire.py`. This is reference-model evidence only and does not establish a production wire parser.

The instrument-spec fixture remains a snapshot, not an executable test case. Although the current reference model has exception subclasses, the fixture contains no expected behavior. Do not mark it migrated until dedicated cases and a reviewed mapping from exception classes to stable rejection classes exist.

#### Cross-review: operation registry versus executable reference surface

The initial registry is a proposed normalization target, not a claim that every listed operation currently has an executable adapter:

- `decimal.*` and `rational.*` operations map to methods on `ExactDecimal` / `ExactRational` in `nexus_decimal.py`. `rational.divide_exact` specifically accepts two decimal operands and returns a reduced rational.
- `numeric_wire.parse_decimal` and `numeric_wire.parse_rational` map to `parse_decimal(encoded, max_chars=...)` and `parse_rational(encoded, max_chars=...)`. The normalized `wire` field is adapter input; the reference function's parameter is named `encoded`. The adapter must pass the profile-bounded `max_chars` explicitly.
- `financial.spot_notional` is exercised through `Price.notional_for(AssetAmount)` in `test_financial_math_fixtures.py`.
- `financial.linear_contract_notional` is backed by `InstrumentUnitModel.linear_base_exposure(ContractCount)` and `InstrumentUnitModel.linear_notional(ContractCount, Price)` in `instrument_units.py`; its vector test verifies base exposure and quote notional.
- `financial.inverse_contract_base_exposure` is backed by `InstrumentUnitModel.inverse_quote_notional(ContractCount)` and `InstrumentUnitModel.inverse_base_exposure(ContractCount, Price)`, returning exact rational asset exposure without implicit decimal rounding.
- `financial.partial_fill_aggregation_math` is backed by `aggregate_partial_fills` in `financial_aggregation.py`, returning typed total base quantity, quote notional and an exact rational weighted-average price. The callable is exercised by the golden-vector and seeded permutation/partition-invariance tests.
- The financial fixture therefore has executable reference coverage for spot, linear, inverse and partial-fill aggregation paths. The aggregator defines arithmetic over supplied typed inputs only; it does not establish venue fill admissibility, fees, funding, P&L, accounting or rounding policy.
- `instrument_spec.validate_limit_order` likewise remains deferred; the current instrument snapshot does not itself establish an executable operation contract.

The exception mapping is also intentionally incomplete outside numeric-wire parsing. `InvalidDecimal` is a candidate for `NUMERIC.INVALID_SYNTAX`; `InexactQuantization` and `InexactDivision` are candidates for `NUMERIC.INEXACT_RESULT`; `DivisionByZero` and `InvalidStep` map directly to their named numeric classes. `NumericLimitExceeded` from `bounded_numeric.py` must be mapped to `NUMERIC.RESOURCE_LIMIT` by a reviewed adapter. Domain exceptions such as `DimensionMismatch` require operation/context-aware mapping; do not infer `UNIT_MISMATCH` versus `IDENTITY_MISMATCH` from exception text. No machine-readable mapping should be declared until each operation's negative cases and adapter behavior are reviewed.

## 4. Canonical comparison rules

The runner comparison is semantic but deliberately strict:

1. Object member order is irrelevant; array order is significant unless the operation contract explicitly declares a set.
2. Strings compare byte-for-byte after UTF-8 decoding. No numeric coercion, exponent expansion, locale parsing or implicit Unicode normalization is permitted.
3. JSON integer, string, boolean and null types remain distinct. In particular, booleans are not integers.
4. Financial decimals and rationals compare as canonical strings/typed objects, not host-language floating-point values.
5. Missing fields are not equivalent to null, zero, empty string or empty array.
6. Unknown fields are rejected for contract version 1; the machine-readable schema should use closed objects (`additionalProperties: false`) at every envelope level. Extension fields require an explicit contract-version change, not ad hoc tolerance.
7. A rejection matches only when the normalized `error_class` matches. Human-readable messages are diagnostic only and are not conformance outputs.
8. The runner must not normalize away unit, currency, instrument, spec-version, sign, denominator or scale information.

## 4.1 Strict JSON ingestion and fixture identity

A language-neutral fixture contract is not portable if runtimes silently parse ambiguous JSON differently. The future validator/runner MUST apply the same strict ingestion rules before schema validation or case execution:

1. Decode bytes as UTF-8 strictly. Reject invalid UTF-8 and a UTF-8 BOM; do not fall back to a platform code page.
2. Reject duplicate object member names at every nesting level. A parser's default "first wins" or "last wins" behavior is not acceptable.
3. Reject non-standard numeric constants such as `NaN`, `Infinity` and `-Infinity`.
4. Reject JSON floating-point number tokens throughout the fixture contract. Control/count/scale fields use JSON integers only where the schema explicitly declares them; financial/domain quantities, coefficients, numerators, denominators, prices and other exact values use canonical strings or typed objects. No implementation may parse a JSON float and convert it back to a string.
5. JSON integer tokens are limited to the signed 64-bit range for cross-runtime control metadata. Larger exact integers MUST be decimal strings. Booleans remain booleans and MUST NOT be accepted as integers.
6. Reject unpaired Unicode surrogate code points. Do not apply Unicode normalization to strings or object keys; compare their decoded scalar values exactly.
7. Reject comments, trailing commas and other non-JSON extensions.
8. Apply explicit runner limits for raw fixture byte length, nesting depth, number of cases, object members and string length before unbounded execution. These are runner safety limits, not hidden numeric semantics. A limit profile must be named and recorded in evidence; no default production profile is implied.

The raw fixture SHA-256 is calculated over the exact original byte sequence before decoding. The runner report records both the raw-byte hash and the parsed contract/suite versions. It MUST NOT hash a reserialized JSON document, because whitespace, key order and serializer choices would change the evidence identity. Case array order is preserved; object member order is not semantically significant.

A validator test suite must include duplicate keys at root/suite/case/input/expect levels, invalid UTF-8, BOM, floats, non-finite constants, booleans in integer fields, out-of-range integers, unpaired surrogates, excessive nesting and each configured resource limit. The same adversarial corpus must be executed by every language implementation before claiming cross-language fixture compatibility.

## 5. Runner protocol

A language implementation exposes the same logical operation set through a thin test adapter. The adapter must not become a production API or import the other language's implementation.

Proposed runner responsibilities:

1. Validate the suite envelope, contract version, unique case IDs and operation availability before executing any case.
2. Execute cases in declared order with no network, wall-clock, randomness or external service dependency unless a suite explicitly models a deterministic injected source.
3. Emit one normalized result per case: case ID, actual outcome, actual value or stable error class, and optional diagnostic metadata excluded from comparison.
4. Compare each result against `expect`; fail closed on missing, extra, duplicate or unexecuted cases.
5. Produce a machine-readable report with suite ID/version, fixture SHA-256, source commit, implementation name/version, toolchain/runtime, platform, numeric profile ID, case totals, pass/fail counts and per-case mismatch identifiers.
6. Return distinct process statuses: `0` all cases passed; `1` conformance mismatch; `2` invalid fixture/unsupported contract; `3` runner or implementation failure. Exact CLI flags and report schema remain OPEN for implementation review.

The Python oracle and future Rust implementation must each execute the same fixture bytes independently. A wrapper may orchestrate both processes, but must not translate expected values differently per language.

## 6. Versioning and change control

- Envelope major version changes when parsing, comparison, outcome tagging or required-field semantics change incompatibly.
- Suite major version changes when existing case meaning or expected outcomes change incompatibly.
- Suite minor version may add cases without changing existing case meaning.
- Suite patch version is limited to non-semantic metadata/provenance corrections.
- Case IDs are never reused for different behavior.
- Existing v1 files remain frozen compatibility inputs. Migration creates a new normalized suite version or an explicit, tested one-way converter; silent in-place reinterpretation is prohibited.
- Fixture changes require review of the domain contract, independent expected-value derivation and CI evidence.
- Production policy fixtures must be kept separate from synthetic math fixtures and require owner/legal/venue qualification as applicable.

## 7. Test layers

The conformance program has separate layers; passing one does not imply passing another:

1. **Golden examples:** fixed hand-derived values and rejection classes.
2. **Differential tests:** Python and Rust execute identical normalized fixtures and produce identical results.
3. **Property tests:** deterministic generated inputs check algebraic invariants and compare against an independent oracle such as rational arithmetic.
4. **Adversarial parsing:** malformed, non-canonical, oversized, deeply nested and ambiguous inputs reject within explicit budgets.
5. **Bounded-resource tests:** every case names an explicit test profile; scale, coefficient, rational growth, allocation and input-size limits are tested before expensive work.
6. **Dimensional tests:** incompatible currencies/assets/instruments/spec versions reject; units never disappear during arithmetic.
7. **State-machine tests:** replay, duplicate identity, crash/recovery, concurrency and fencing are separate protocol suites, not folded into numeric arithmetic.

Property-test seeds, generator versions and generated-case counts are part of the evidence report. Randomness must be deterministic and reproducible.

## 8. CI and evidence requirements

A future CI job may claim cross-language conformance only when it records:
- exact repository commit SHA;
- exact fixture paths and SHA-256 hashes;
- envelope and suite versions;
- Python runtime and Rust toolchain versions;
- dependency lockfile and build profile;
- OS/architecture;
- numeric profile identifiers;
- deterministic property seeds and counts;
- per-suite/per-language totals and normalized rejection-class results.

A Python-only pass verifies only the Python reference implementation. A Rust-only pass verifies only the Rust adapter. Cross-language conformance requires both implementations to pass the same fixture bytes in the same evidence run.

## 9. Adoption plan and gates

1. **Owner review:** accept/revise the envelope, stable error taxonomy, version policy and evidence requirements.
2. **Legacy inventory:** map every existing v1 fixture field and case to the proposed envelope without changing v1 files; identify semantic gaps and ambiguous expectations.
3. **Schema validation:** publish a machine-readable schema and validator after choosing a dependency policy; validate all migrated suites.
4. **Python runner:** add a thin runner around existing reference operations; preserve current isolated unit tests.
5. **Rust readiness:** only after G0D/G1 approval, create a pinned Rust toolchain/workspace and dependency policy.
6. **Rust adapter:** implement the same operation identifiers and normalized result contract.
7. **Differential CI:** run Python and Rust against identical fixture hashes; add bounded/adversarial/property layers.
8. **Promotion:** treat successful reference conformance as a prerequisite, not proof of production integration, venue semantics, performance, security or live readiness.

## 10. Acceptance criteria

- [ ] Owner/architecture review accepts the envelope, outcome union, stable error taxonomy and version policy.
- [ ] Legacy fixture inventory and migration mapping are complete; v1 files remain unchanged.
- [ ] A machine-readable schema and validator reject malformed/ambiguous fixture suites.
- [ ] Python runner executes all migrated suites and emits deterministic reports.
- [ ] Rust adapter executes the same fixture bytes after G0D/G1 approval.
- [ ] Differential CI proves identical values, units and rejection classes.
- [ ] Bounded-resource, adversarial parsing, dimensional and deterministic property tests are included.
- [ ] CI evidence pins exact commit, fixture hashes, toolchain, dependency lock and test profile.
- [ ] Documentation, checklist, roadmap, status and changelog are updated.

## 11. Current disposition

**PROPOSED DESIGN ONLY.** Existing Python fixture files and direct unittest workflows remain unchanged. No normalized schema, runner, Rust source, Cargo workspace, production numeric profile or cross-language result is added by this document.

Prototype readiness remains BLOCKED. Live trading remains NOT AUTHORIZED.

#### Financial operation audit correction

A second pass inspected `test_financial_math_fixtures.py` and `instrument_units.py` directly and corrected the preceding audit: the spot, linear-contract and inverse-contract paths do have executable reference coverage. In particular, linear notional is calculated by `InstrumentUnitModel.linear_notional`, and inverse exposure remains a reduced `ExactRational` through `inverse_base_exposure`; it must not be coerced to a decimal unless an explicit exact-conversion or rounding contract permits it. The partial-fill weighted-average calculation is present and tested, including deterministic permutation/partition invariance properties, but is currently written inline in the test module rather than exposed as a named reusable oracle operation. The earlier statement that linear/inverse implementations were absent was incorrect and is superseded by this correction. The operation registry should map the three implemented operations to their real call paths and keep only partial-fill extraction as a code-structure follow-up.

#### Numeric API boundary and bounded-context mapping

The exact oracle and bounded wrapper are separate contracts:

- `ExactDecimal.parse`, arithmetic, `quantize_exact`, `ExactDecimal.divide_exact`, `ExactRational.to_decimal_exact` and `ExactRational.quantize` are arbitrary-precision mathematical reference operations. They do not impose production digit, scale or intermediate-growth limits.
- `BoundedNumericContext` in `bounded_numeric.py` wraps the oracle with an explicit caller-supplied `NumericLimits` profile. Its limits are mandatory and include independent input/wire character budgets, coefficient/rational digit budgets, scale, intermediate digit and power-of-ten exponent budgets. No implicit or production profile exists.
- The wrapper's `NumericLimitExceeded` is the typed signal for configured budget exhaustion and is a candidate adapter mapping to `NUMERIC.RESOURCE_LIMIT`; the adapter must match the exception type, not its message. `numeric_wire` subclasses already expose `error_class` directly. The two paths must not be conflated: raw wire parser `max_chars` and bounded-context `max_wire_chars` are separately enforced layers.
- API misuse/invalid parameters must be distinguished from operation-domain rejection. For example, negative, boolean or non-integer quantization scale currently raises `ValueError`/type validation before mathematical execution; the fixture schema/adapter must reject such malformed input as a schema/contract failure, not relabel it `NUMERIC.INEXACT_RESULT`. A valid non-negative scale that cannot represent the exact value is the inexact-result case.
- `decimal.quantize_exact` and `rational.quantize` must preserve these separate paths. The rational operation additionally requires an explicit supported `RoundingMode`; invalid/missing mode is malformed operation input, not a rounding outcome.

The reference oracle's arbitrary precision is intentional. The bounded wrapper is a test-only model of explicit limits, not a production numeric profile. Future production profiles must be separately approved and must not be copied from synthetic test values.


#### Partial-fill aggregation extraction update — 2026-11-14

The inline weighted-average arithmetic has been extracted to the test-only callable `aggregate_partial_fills` in `foundation/reference-model/financial_aggregation.py`. Its result preserves typed `AssetAmount` and `Notional` dimensions and an `ExactRational` weighted-average price. Empty input is rejected; incompatible base or quote dimensions fail through the existing domain types; non-terminating averages remain rational. Signed quantities are not prohibited by this arithmetic helper, so it must not be treated as a venue fill validator. Golden-vector and deterministic permutation/partition tests now call the named function. This closes the code-structure extraction follow-up only; normalized fixture registration remains owner-review gated.
