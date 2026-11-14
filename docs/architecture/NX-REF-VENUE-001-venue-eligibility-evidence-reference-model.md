# NX-REF-VENUE-001 — Venue Eligibility Evidence Reference Model

**Status:** TEST-ONLY REFERENCE / NOT PRODUCTION AUTHORIZATION  
**Date:** 2026-11-14  
**Parent decision:** [NX-ADR-007](NX-ADR-007-venue-eligibility-jurisdictional-activation-gate.md)

## Purpose and boundary

This package is a small deterministic reference evaluator for evidence completeness, scope binding, freshness and explicit owner approval. It is intended to make a subset of NX-ADR-007's fail-closed rules executable and testable.

It does **not**:
- interpret Federal Law No. 282-FZ or any other law;
- determine whether a venue, person, account or product is legally eligible;
- authenticate a reviewer or validate professional qualifications;
- verify signatures, KYC, sanctions results, venue statements or source documents;
- establish a trusted clock, persistent record store, distributed concurrency or revocation propagation;
- protect credentials or enforce a network egress boundary;
- grant trading permission or replace Risk, Execution, Security or legal review.

A passing reference test means only that this evaluator follows its explicit synthetic policy and fixture inputs.

## Model

The 'venue_eligibility.py' module defines:
- 'ActivationMode': RESEARCH_ONLY, DATA_ONLY, PAPER_ONLY, LIVE_ELIGIBLE, SUSPENDED, REVOKED;
- 'EvidenceStatus': CONFIRMED, UNKNOWN, REJECTED;
- immutable 'EvidenceItem' with key, status, exact scope digest, observation time, optional expiry, source reference and reviewer reference;
- immutable 'VenueEligibilityRecord' with exact scope digest, revision, state, validity interval, evidence tuple and owner-approved revision;
- immutable 'EligibilityPolicy' with mandatory evidence keys, reviewer-required keys, per-key maximum age and explicit owner-approval requirement;
- 'evaluate_eligibility', which returns a machine-readable decision and denial reason.

The policy is passed explicitly and has no permissive defaults. This avoids hiding legal or operational assumptions in a generic model default.

## Deterministic rules covered

1. Missing record denies.
2. Suspended and revoked records deny regardless of otherwise complete evidence.
3. Requested mode must exactly match the record mode; no implicit privilege inheritance between DATA_ONLY, PAPER_ONLY and LIVE_ELIGIBLE.
4. Record and every required evidence item bind to the exact expected scope digest.
5. UNKNOWN, REJECTED or missing evidence denies.
6. Record/evidence timestamps cannot be in the future relative to the supplied clock.
7. Expiry is exclusive: expires_at_ms <= now_ms is expired.
8. Maximum-age boundaries are inclusive: evidence is stale only when now_ms - observed_at_ms > max_age_ms.
9. Reviewer-required evidence must contain a reviewer reference. The reference is opaque and is not authenticated by this model.
10. Owner approval must bind to the exact record revision.
11. Duplicate evidence keys are rejected at record construction.
12. No implicit evidence policy, age limit or owner-approval setting exists.

## Test coverage

'test_venue_eligibility.py' contains 24 deterministic tests:
- complete exact-scope evidence;
- missing record/evidence;
- record and evidence scope mismatch;
- UNKNOWN and REJECTED evidence;
- record and evidence expiry boundaries;
- stale evidence and maximum-age equality;
- future record/evidence timestamps;
- missing reviewer reference;
- owner approval revision mismatch;
- SUSPENDED and REVOKED overrides;
- no DATA_ONLY/PAPER_ONLY/LIVE_ELIGIBLE privilege inheritance;
- RESEARCH_ONLY is not an execution mode;
- duplicate evidence keys;
- explicit policy construction;
- independent record/evidence expiry;
- invalid clock input.

The reference CI workflow runs this suite on Python 3.11, 3.12 and 3.13. CI evidence must be tied to the exact PR head SHA before reporting a pass.

## Known limitations and production requirements

- scope_digest is an opaque string in this model. Production must define canonical scope serialization, collision-resistant digesting and schema versioning.
- Evidence source/reviewer references are not dereferenced, authenticated or signed.
- The caller supplies now_ms; production needs a trusted time source, clock-skew policy and monotonicity strategy.
- In-memory immutable dataclasses do not provide persistence, append-only history, transactional revision updates or multi-writer concurrency.
- This evaluator does not model approval signatures, role separation, dual control, approval revocation or record supersession.
- No state transition protocol, durable event, cache invalidation, epoch fencing or egress enforcement is implemented.
- The policy is injected by the caller; no legally reviewed Russia-specific or venue-specific policy profile is included.
- Evidence validity and age limits are synthetic test inputs, not recommendations or selected production values.

Production implementation requires a separate design for canonical scope, authenticated evidence, signature and key management, trusted time, durable revision store, atomic epoch changes, reviewer/owner roles, revocation propagation and final egress enforcement. The egress boundary must remain the sole holder of live venue credentials.

**Disposition:** reference-only. It cannot be used to enable DATA_ONLY, PAPER_ONLY or live trading.
