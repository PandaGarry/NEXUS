# NX-RESEARCH-007 — NautilusTrader v2 Release Baseline Review

**Status:** CONFIRMED RELEASE-CHANNEL REVIEW — NOT AN ADOPTION DECISION  
**Review date:** 2026-11-14  
**NEXUS baseline:** PR #10, branch `foundation/domain-kernel-reference-v0`  
**Scope:** Identify whether a reproducible NautilusTrader v2 baseline is suitable for a NEXUS compatibility prototype.  
**Decision class:** Research evidence only; no dependency approval, license opinion, or production authorization.

## 1. Executive result

The latest official v2 release observed on 2026-11-14 is **v2.0.0rc9**, published 2026-11-10. It is explicitly a **pre-release**. The upstream README says v2 release-candidate wheels are intended for community testing and are not recommended for production environments controlling real capital. Plain stable installation still resolves to the v1 line until v2.0.0 final; v2 requires opting into pre-releases.

Therefore:

- v2.0.0rc9 is a reproducible candidate for isolated compatibility experiments only.
- It is not an acceptable production dependency baseline for NEXUS.
- The previously inspected `develop` snapshot `97ecbafd6621241a2222ef5a31cf887c6d96d950` is not interchangeable with rc9.
- Do not build NEXUS production execution around a moving `develop` branch or a release candidate.
- Keep NautilusTrader as the leading runtime candidate, but defer selection until a stable v2 release (or a separately justified and frozen source fork) exists and passes NEXUS conformance gates.

## 2. Immutable release identity

- Release tag: `v2.0.0rc9`
- Release date: 2026-11-10
- Tag object: `280573e0ec4b0c2a8159bc4a4f733a10e478d290`
- Peeled commit: `da6b57aefdd62b44f675e434ffcfefca7f4025dd`
- Release page: https://github.com/nautechsystems/nautilus_trader/releases/tag/v2.0.0rc9
- Tag API object: https://api.github.com/repos/nautechsystems/nautilus_trader/git/ref/tags/v2.0.0rc9
- Upstream installation / release-channel guidance: https://github.com/nautechsystems/nautilus_trader

The tag is immutable as a release identity. The tag object reports its own signature as unverified/unsigned; the release page separately reports the underlying commit as GitHub-verified. These are distinct attestations and must not be conflated. Release artifacts include SHA-256 manifests and Sigstore/in-toto provenance material; any future binary experiment must verify the exact artifact checksum and provenance, not merely trust a package version string.

## 3. RC9 changes relevant to NEXUS

The official release notes contain several changes that directly affect our integration contract:

1. **Numeric construction and decoding:** raw `Price` and `Quantity` construction/decoding reject digits beyond configured precision; `Price.from_decimal` and `Quantity.from_decimal` round excess decimal places using half-even. NEXUS must not allow an upstream convenience constructor to silently transform an authoritative order price or quantity. The adapter boundary must validate exact divisibility against the NEXUS instrument specification before conversion, and reject any lossy conversion.
2. **Serialization precision:** SBE requires matching precision modes and rejects version 0. All producers/consumers must use a compatible precision configuration and serialization version. This needs explicit cross-process and persistence round-trip tests.
3. **At-least-once messaging:** Redis message retries changed to at-least-once delivery; consumers must deduplicate. NEXUS must assume duplicate delivery, persist inbox identity, and make side effects idempotent. This is aligned with our model but is not an exactly-once guarantee.
4. **Execution lifecycle:** local modify/cancel refusals now emit denied events and require handling the corresponding callbacks. Command state mapping must include denied outcomes; they must not be mistaken for venue acknowledgement or successful cancellation.
5. **Connection errors:** data/execution engine connection methods now return `Result`; startup orchestration must propagate failures and must not mark a service healthy on an ignored error.
6. **Adapter churn:** RC9 includes broad adapter changes, including Bybit execution/reconciliation and Coinbase book recovery. This demonstrates active development, not completed NEXUS venue qualification.

These are release-note observations. They are not a complete code audit or proof that every adapter path behaves correctly.

## 4. RC9 versus the previously inspected develop snapshot

A GitHub compare was run from rc9 commit `da6b57aefdd62b44f675e434ffcfefca7f4025dd` to the previously inspected develop snapshot `97ecbafd6621241a2222ef5a31cf887c6d96d950`.

GitHub reported:

- status: `diverged`;
- develop snapshot: 77 commits ahead of rc9;
- develop snapshot: 72 commits behind rc9;
- merge base: `a8786259f83c9787293adc456444bfd38c361df6`.

This is a diverged history, not a simple forward update. Consequently, source findings previously recorded against the develop snapshot (including cache persistence and command-routing observations) must not be automatically attributed to rc9. R6-C must inspect the exact selected tag/source snapshot independently.

Compare endpoint: https://api.github.com/repos/nautechsystems/nautilus_trader/compare/da6b57aefdd62b44f675e434ffcfefca7f4025dd...97ecbafd6621241a2222ef5a31cf887c6d96d950

## 5. Revised NEXUS disposition

| Candidate baseline | Permitted use in NEXUS | Disposition |
|---|---|---|
| v2.0.0rc9 | Isolated build/API/conformance experiment; no real credentials or live capital | TEST-ONLY CANDIDATE |
| `develop` at `97ecbafd...` | Source evidence and targeted audit only | MOVING / DIVERGED SNAPSHOT |
| Stable v2.0.0+ | Re-evaluate after immutable release, artifact verification, license/dependency inventory and NEXUS conformance | NOT YET AVAILABLE AT REVIEW |
| v1.231.0 | Historical API reference only; legacy v1 maintenance path is restricted after v2 cutover | NOT A NEW INTEGRATION BASELINE |

NautilusTrader remains **LEADING CANDIDATE — NOT SELECTED**. No production use, dependency addition, fork, or live integration is approved.

## 6. Required R6 gates (updated)

| Gate | Required evidence | Exit condition |
|---|---|---|
| R6-A1 — Stable baseline | Stable v2 release, immutable tag/commit, artifact checksums and provenance, Rust/Python toolchain pins | Reproducible, non-RC source and binary identity |
| R6-A2 — Release delta | Compare stable release to rc9 and to the previously inspected develop snapshot; inspect breaking changes and migration notes | No unreviewed API/behavior assumptions |
| R6-B — Numeric compatibility | Exact tests for excess precision, half-even conversion, overflow, instrument tick/lot divisibility and SBE mode compatibility | NEXUS rejects lossy conversion before upstream construction |
| R6-C — Risk and durable dispatch | Re-audit every submit/modify/cancel/cancel-all/close route on the exact stable source | Payload-bound NEXUS authorization is non-bypassable; durable outbox commits before every external side effect |
| R6-D — Recovery | At-least-once duplicate delivery, restart, ambiguous timeout, late/duplicate fills, denied modify/cancel and reconciliation fault tests | NEXUS inbox/outbox and state transitions preserve invariants |
| R6-G — License and dependency governance | Exact release license, crate and transitive dependency inventory, artifact provenance, deployment model review | Explicit legal and architecture decision |

**Stop condition unchanged:** if a non-bypassable NEXUS risk + durable dispatch boundary cannot be proven without an invasive fork, reject NautilusTrader as the execution core and retain it as a reference.

## 7. Primary evidence

- Release v2.0.0rc9 and release notes: https://github.com/nautechsystems/nautilus_trader/releases/tag/v2.0.0rc9
- Upstream README and explicit pre-release warning: https://github.com/nautechsystems/nautilus_trader
- v2 migration guide: https://github.com/nautechsystems/nautilus_trader/blob/develop/MIGRATION_V2.md
- v2 Rust API stability note: https://nautilustrader.io/docs/latest/concepts/rust/

## 8. Limitations

This is a release-channel and release-note review plus GitHub commit/tag metadata comparison. No RC9 wheel was installed or executed; no Rust workspace was built; no adapter was connected; no live or sandbox account was used; no full source diff was audited; no license opinion was obtained. All such items remain NOT TESTED / UNKNOWN.
