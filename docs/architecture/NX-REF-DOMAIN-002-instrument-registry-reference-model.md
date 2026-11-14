# NX-REF-DOMAIN-002 — Instrument Registry Reference Model

**Status:** TEST-ONLY reference slice; registry semantics PROPOSED  
**Version:** 0.1  
**Related:** NX-REF-DOMAIN-001, NX-ADR-005, NX-ARCH-003, NX-IF-001, NX-IF-002.

## 1. Purpose and boundary

NX-REF-DOMAIN-001 validates one immutable instrument-specification snapshot. This companion slice defines a deliberately narrow append-only in-memory history around those snapshots. Its purpose is to make version replay, conflicts, identity continuity and effective-time ordering executable.

It is not a production registry, persistence layer, venue-source authority or distributed concurrency protocol. Version numbers are assigned by the caller; this model does not decide who is entitled to assign them.

## 2. Registry behavior

`foundation/reference-model/instrument_registry.py` provides:

- `register(spec)`: append a new immutable snapshot;
- `get(instrument_id)`: return the latest registered snapshot;
- `get(instrument_id, version)`: return an exact historical snapshot;
- `history(instrument_id)`: return the immutable tuple of snapshots in registration order.

Registration rules:

1. First snapshot for an internal instrument ID is accepted.
2. A byte-for-byte/equality-identical replay of any already registered version is idempotent.
3. Reusing a version with different snapshot content is rejected.
4. A new version must be numerically greater than the latest registered version. Gaps are allowed; contiguity is not assumed.
5. A stable internal ID cannot be rebound to a different venue ID, native instrument ID or market type. A genuinely different venue identity requires a distinct internal ID in this reference model.
6. When both the incoming and most recent known effective timestamps are present, effective time cannot move backwards. Unknown timestamps remain unknown and do not erase the last known timestamp used for this comparison.
7. Fetch timestamps are provenance, not ordering authority; this model does not require them to be monotonic.

## 3. Verification

The registry suite covers first registration, latest/historical lookup, immutable append behavior, identical replay of latest and historical versions, same-version content conflict, version regression, identity rebinding, effective-time regression, unknown effective time, regression across an unknown intermediate snapshot, independent instruments and missing lookups.

CI must pass the suite on Python 3.11, 3.12 and 3.13 at the exact branch HEAD before the slice is marked verified.

## 4. Deliberate exclusions and unresolved decisions

- Durable storage, transactions, uniqueness constraints and concurrent writers.
- Cross-process/distributed version assignment and fencing.
- Venue source precedence, signatures, payload authenticity and trust levels.
- Effective-time conflict resolution when two sources disagree.
- Retroactive corrections, tombstones, delisted instrument retention and alias/symbol migration.
- Freshness thresholds, cache invalidation and order-time snapshot pinning.
- Historical event linkage to the exact spec version.
- Canonical wire serialization and cross-language conformance.
- Production schema, migrations, backups and recovery.

The stable-ID identity rule is a conservative reference invariant, not yet a final owner-approved identity policy. Real venue symbol migrations and contract rollovers require a separately specified identity/alias model.

**Disposition:** useful executable reference for append-only history semantics. NX-ADR-005 remains PROPOSED; no production registry or instrument orderability is approved.
