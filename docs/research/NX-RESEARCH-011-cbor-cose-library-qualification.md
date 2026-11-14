# NX-RESEARCH-011 — CBOR / COSE Library Qualification

**Date:** 2026-11-14  
**Status:** RESEARCH ONLY — candidates and rejection criteria; no dependency approved or installed  
**Scope:** G1 deterministic command serialization, strict CBOR ingress and COSE_Sign1 Ed25519 (-19) capability signing  
**Related:** NX-ADR-008, NX-ARCH-005, NX-OWNER-DECISIONS-001 OD-08, NX-RESEARCH-010

## 1. Executive disposition

The wire protocol is selected in NX-ADR-008; implementation libraries are not.

- **CBOR encoder candidate:** Rust `cbor2` 1.1.6 is the strongest current candidate for RFC 8949 core deterministic encoding and exact raw-value preservation. It is not a strict ingress decoder by itself.
- **Strict CBOR ingress:** no reviewed crate is approved as a complete drop-in implementation of the NEXUS profile. A strict raw-byte validator must reject non-preferred encodings, duplicate/unknown keys, tags, floats, indefinite lengths, bad map ordering, invalid UTF-8, trailing bytes and resource exhaustion before typed deserialization. The validator may use a qualified low-level library, but it must inspect the original bytes and prove every rejection.
- **COSE structure candidate:** Rust `coset` 0.4.2 is the leading test-only candidate for COSE_Sign1 data structures. It exposes fully specified Ed25519 (-19), preserves the original protected-header byte string on parse, supports external AAD and custom signing/verifying closures, and reports duplicate map keys. Its underlying CBOR implementation and API maturity require a constrained profile and interoperability tests.
- **Alternative COSE candidate:** `cose2` 0.5.1 models RFC 9052 structures and has pluggable signer/verifier traits, but its built-in Ed25519 provider uses the deprecated polymorphic EdDSA identifier (-8). It is not usable as-is for OD-08; a custom signer/verifier bound to integer label -19 would be required.
- **Python COSE library:** `pycose` 1.1.0 is not selected as the independent conformance oracle. Its latest PyPI release is dated 2023-12-15, the published package has no provenance attestation, and its documentation still describes the older RFC 8152 generation.
- No Cargo workspace, package, signer, verifier, CBOR parser, key or runtime has been added.

## 2. Candidate matrix

| Candidate | Version / license / MSRV | Strengths | Blocking limitations | Disposition |
|---|---|---|---|---|
| Rust `cbor2` | 1.1.6 / MIT / Rust 1.89 | RFC 8949 core bytewise deterministic encoder; `RawValue` preserves exact encoded bytes; exact-one-item well-formedness and UTF-8 validation; bounded recursion; low-level header codec | Default decode intentionally accepts indefinite items, non-preferred spellings, tags and other well-formed but NEXUS-forbidden forms. `RawValue` proves well-formedness, not canonicality. No strict deterministic ingress mode was found in the reviewed public API | **Leading encoder / raw-byte candidate; not sufficient alone for ingress** |
| Rust `cbor-core` | 0.10.1 / MIT / Rust 1.88 | Strict default decoder; duplicate-key and non-shortest rejection; recursion, length and preallocation limits | Targets `draft-rundgren-cbor-core-25`, not an RFC-only stable profile; its map ordering is length-first. API explicitly not stable. Small single-maintainer project. Although text-only command keys may make its ordering equivalent for the restricted command map, this equivalence must be proven and does not qualify it for arbitrary COSE maps | **Do not adopt as the protocol codec; retain as comparison/test candidate only** |
| Rust `coset` | 0.4.2 / Apache-2.0 / Rust 1.81 | IANA `Algorithm::Ed25519 = -19`; `ProtectedHeader.original_data` preserves received protected bstr; COSE_Sign1 to-be-signed structure includes caller-supplied external AAD; signing/verifying is delegated through closures; duplicate map keys produce an error | Underlying `ciborium`; documentation still references RFC 8152 in places; project says API/code may change and is not an officially supported Google product. It does not provide key custody or crypto provider. Generic parser is not a substitute for NEXUS strict ingress validation | **Leading COSE structure candidate for isolated interoperability tests only** |
| Rust `cose2` | 0.5.1; exact license/MSRV/provenance not yet independently qualified | Explicit RFC 9052 / RFC 8392 data model; built on `cbor2`; signer/verifier traits; COSE header collision and critical-header checks; bounded `validate_cbor` with duplicate-key checks | Built-in Ed25519 provider explicitly uses polymorphic EdDSA (-8), which OD-08 rejects. `validate_cbor` is well-formedness/duplicate/limit validation, not by itself the complete NEXUS deterministic profile. Young release line; exact package provenance/license must be checked | **Alternative test candidate only; no built-in signer accepted** |
| Python `pycose` | 1.1.0 / BSD-3-Clause / Python >=3.7 | COSE message model and cryptography integration | PyPI latest release 2023-12-15; one maintainer; no release provenance attestation; published docs refer to RFC 8152; no demonstrated RFC 9864 alg=-19 conformance | **Do not use as NEXUS golden-vector oracle** |

## 3. Protocol-specific findings

### 3.1 CBOR command bytes

The command profile is narrower than general CBOR:

- one root item only; no trailing bytes or CBOR sequences;
- map keys are schema-defined ASCII text field names only; no arbitrary, compound or integer command-map keys;
- definite lengths and preferred shortest forms only;
- RFC 8949 §4.2.1 core deterministic ordering;
- no duplicate or unknown command keys;
- no tags, floats, NaN/Infinity, undefined or unassigned simple values;
- financial quantities remain exact strings or typed structures; no floating-point conversion;
- signed 64-bit bounds apply only to explicitly declared control metadata;
- explicit input, item-count, nesting, string, map, allocation and processing budgets.

Rust `cbor2` 1.1.6 documents that its canonical encoder emits shortest forms, definite lengths and RFC 8949 §4.2.1 bytewise-ordered keys. Its decoder is intentionally more liberal: it accepts indefinite items, segmented strings, half-width floats, leading-zero bignums and unknown tags in most positions. `RawValue` preserves the exact original bytes but guarantees only one well-formed item and valid UTF-8. Therefore:

1. `validate_slice` / `RawValue::new` alone are not an ingress security gate.
2. Decode-and-reencode comparison is acceptable only if the original bytes are preserved and all duplicate/unknown keys are detected before any map collapses them.
3. The preferred design is a byte-level profile validator that checks the original input before typed decode; its implementation must be small, bounded and exhaustively vector-tested.
4. Do not silently normalize or canonicalize attacker-supplied command bytes and then treat the normalized value as the originally approved command.

### 3.2 Map-ordering profile

RFC 8949 §4.2.1 sorts by bytewise lexicographic order of deterministic key encodings. RFC 8949 §4.2.3 retains the legacy length-first ordering for compatibility.

The NEXUS command schema restricts map keys to fixed ASCII text field names. For text-string keys, the deterministic encoded prefix includes the string length, so the two orderings may coincide; this must be proven with explicit vectors including lengths around 23/24, 255/256 and multibyte value strings. Do not generalize that equivalence to arbitrary CBOR keys or COSE maps. The selected protocol remains RFC 8949 §4.2.1, not a silent switch to the legacy profile.

### 3.3 COSE_Sign1 profile

The selected profile is RFC 9052 COSE_Sign1 with RFC 9864 fully specified COSE Ed25519 alg=-19.

- Protected header contains exactly the required algorithm and key identifier parameters; no algorithm or kid may be moved to the unprotected bucket.
- `kid` is an integrity-protected lookup hint, not an authentication factor or uniqueness guarantee.
- Key resolution is issuer-, audience-, algorithm-, purpose-, validity-, revocation- and registry-generation-bound; exactly one eligible key must resolve or verification fails closed.
- COSE key must be OKP / Ed25519 and must be bound to alg=-19; reject -8, -53, key/algorithm mismatch and algorithm substitution.
- External AAD is a fixed, versioned NEXUS domain separator; no caller-controlled or empty-context fallback.
- Verify the signature over the received protected-header bstr as received. Never reconstruct different protected-header bytes before signature verification.
- No unprotected header parameters are permitted in the initial NEXUS profile; reject protected/unprotected collisions and unknown critical parameters.
- Signature verification does not authorize a command: Risk approval, reservation, single-use consumption, halt epoch, eligibility and egress checks remain separate mandatory gates.

### 3.4 Candidate-specific constraints

**`coset`:** its `ProtectedHeader.original_data` is a useful property because signature verification can use the exact protected bstr received from the wire. Its IANA registry includes Ed25519=-19. The crate uses `ciborium` underneath; the NEXUS profile should restrict protected headers to the fixed small integer labels required by this profile and must run the independent raw-byte validator first. A dedicated test must prove byte-identical signing/verification across Rust and Python for alg=-19, kid, external AAD and the exact COSE_Sign1 array.

**`cose2`:** its generic `Signer` / `Verifier` trait can represent a custom algorithm label, but its bundled Ed25519 provider is explicitly for polymorphic EdDSA (-8). Do not enable that provider for NEXUS. If tested, implement a separate adapter returning integer label -19 and verify the exact emitted protected header and Sig_structure against RFC 9864 vectors.

**`cbor-core`:** strictness is attractive, but its current target is a draft profile and its ordering is length-first. Its use is not approved for NEXUS merely because a restricted text-key subset may happen to share the same order.

## 4. Required qualification vectors

Before any library is selected, create language-neutral vectors and require identical accept/reject results in Python and Rust.

### CBOR positive vectors
- empty and minimal command structures;
- all field names in the schema and all nesting levels;
- lengths at 0, 23, 24, 255, 256 and configured maximum;
- Unicode values including multibyte characters, combining marks and supplementary-plane code points;
- signed integer boundaries for permitted control metadata;
- byte-identical canonical encoder output and SHA-256 digest.

### CBOR negative vectors
- non-shortest integer and length encodings;
- indefinite-length byte/text strings, arrays and maps;
- unsorted keys under RFC 8949 §4.2.1 and legacy length-first order where they differ;
- duplicate keys at every nesting level;
- unknown fields, non-text keys and malformed key types;
- invalid UTF-8, unpaired Unicode representation attempts and prohibited normalization aliases;
- tags, floats, NaN, Infinity, undefined and unassigned simple values;
- truncated headers/bodies, oversized declared lengths, excessive nesting, too many map entries and trailing bytes.

### COSE positive / negative vectors
- COSE_Sign1 alg=-19, OKP/Ed25519, protected kid and fixed external AAD;
- verify using the exact received protected bstr;
- reject alg=-8, alg=-53, wrong kty/crv, key/algorithm mismatch and signature corruption;
- reject missing/unprotected alg, unprotected kid, duplicate/colliding labels and unknown critical headers;
- reject unknown issuer, wrong audience, wrong purpose, not-yet-valid/expired key, revoked key, stale registry generation and ambiguous kid;
- prove cross-language identical Sig_structure bytes and signature result.

## 5. Qualification gates and next actions

1. G0D: record immutable crate versions, source commit/tag, license, transitive SBOM, provenance, advisory status and reproducible build evidence.
2. G1: build a throwaway test harness (not a production dependency or runtime) to compare `cbor2` canonical output, strict-validator behavior and `coset` COSE_Sign1 behavior against the language-neutral vectors.
3. Review every panic/unwrap path reachable from untrusted input; fuzz CBOR and COSE parsers with bounded resources.
4. Verify MSRV against the future Rust toolchain policy; current candidates imply Rust 1.89 for cbor2 and 1.81 for coset.
5. Test key-provider abstraction with a non-exportable signing interface; software Ed25519 keys are test fixtures only, never a production custody decision.
6. Keep production integration blocked until G0D, OD-08 security review, key custody/recovery and owner-controlled legal/jurisdictional decisions are closed.

## 6. Source register

- RFC 8949 CBOR: https://www.rfc-editor.org/rfc/rfc8949.html
- RFC 9052 COSE structures: https://www.rfc-editor.org/rfc/rfc9052.html
- RFC 9053 COSE algorithms: https://www.rfc-editor.org/rfc/rfc9053.html
- RFC 9864 fully specified Ed25519 alg=-19: https://www.rfc-editor.org/rfc/rfc9864.html
- IANA COSE registry: https://www.iana.org/assignments/cose/cose.xhtml
- Rust cbor2 1.1.6: https://docs.rs/cbor2/1.1.6/cbor2/
- Rust cbor2 raw values: https://docs.rs/cbor2/1.1.6/cbor2/struct.RawValue.html
- Rust cbor2 validation: https://docs.rs/cbor2/1.1.6/cbor2/fn.validate_slice.html
- Rust cbor-core 0.10.1: https://docs.rs/cbor-core/0.10.1/cbor_core/
- Rust coset 0.4.2: https://docs.rs/coset/0.4.2/coset/
- coset protected header preservation: https://docs.rs/coset/0.4.2/coset/struct.ProtectedHeader.html
- Rust cose2 0.5.1: https://docs.rs/cose2/0.5.1/cose2/
- cose2 validation: https://docs.rs/cose2/0.5.1/cose2/fn.validate_cbor.html
- Python pycose: https://pypi.org/project/pycose/

Upstream releases and security posture change. Requalify exact pinned versions and full transitive dependency graph at adoption time. This research is not a legal opinion, security certification or production approval.
