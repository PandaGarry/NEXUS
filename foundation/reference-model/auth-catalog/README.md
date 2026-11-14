# Authorization-catalog manifest reference model

**Status:** TEST-ONLY LOGICAL VALIDATION MODEL — NOT A WIRE CODEC OR PRODUCTION CONTROL

Run from this directory:

```bash
python -m unittest -v
```

## Scope

- Exact v1 logical field set; reject unknown/missing fields.
- Context, timestamp, digest-shape and monotonic sequence/predecessor checks.
- Explicit bounded scope; reject wildcard scope, duplicate entries, unknown object classes and duplicate semantic object identities.
- Deny-rule shape and unique rule identifiers.
- Fail-closed admission preconditions for external signature verification, independent approval and revocation-state availability.

## Explicit non-goals

This slice does **not** implement deterministic CBOR, canonical byte validation, SHA-256 computation, COSE_Sign1, Ed25519, key lookup, trust-root/revocation services, approval identity, PostgreSQL catalog extraction, effective privilege analysis, immutable audit, deployment readiness, continuous drift detection or session/process/network fencing.

The `signature_verified`, `approval_verified` and `revocation_state_available` arguments are test seams representing results from future independent components. They are not cryptographic evidence. The candidate digest is supplied by the caller and is not recomputed here.

This model validates a logical object before wire serialization. It must not be used to parse or authorize attacker-supplied CBOR bytes. The selected wire profile remains the one in NX-ADR-008 and NX-RESEARCH-011; a separate raw-byte validator and cross-language golden vectors are mandatory.

No production manifest is generated or accepted by this reference slice. No database, credentials, keys, venue connectivity or trading capability are involved.


## CI evidence

Python workflow [#43633125568](https://github.com/PandaGarry/NEXUS/actions/runs/43633125568) passed exact code/test HEAD `c80d781ce7c9f2b4a015fa79f8e2c403709439d7` on Python 3.11, 3.12 and 3.13: 23 tests per runtime. The complete workflow ran 287 tests per runtime. PostgreSQL HEGC workflow [#43633125536](https://github.com/PandaGarry/NEXUS/actions/runs/43633125536) passed 12/12. These runs establish reference-model/fixture CI only.
