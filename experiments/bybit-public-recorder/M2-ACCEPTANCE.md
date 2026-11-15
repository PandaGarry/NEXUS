# Bybit M2 acceptance checklist — live REST snapshot + delta synchronization

**Status:** `IN_PROGRESS` — acceptance criteria remain incomplete  
**Plan date:** 2026-11-15  
**Target:** 2026-11-28  
**Scope:** public market data only; Bybit V5 linear BTCUSDT; no credentials, private endpoints, account access or orders.

This checklist is a release gate, not a claim that M2 is implemented. Every checked item must link to a commit, CI run, fixture, raw journal or reproducible report.

## Terms and data-use gate (must pass before further live captures or raw-data publication)

- [ ] Review the current [Bybit API Terms & Conditions](https://www.bybit.com/en/help-center/article/API-Terms?category=ae1012f19fad1c184e) (support page last updated 2026-10-20) and the linked [API agreement PDF](https://www.bybit.com/common-static/compliance/legal/BYBIT/df1923006718fbba8ba70d7d762b9866.pdf).
- [ ] By **2026-11-18**, send Bybit a written clarification request covering Sections 2.3 and 7.2 (API-key identity/verification) for unauthenticated public market-data endpoints; whether §5.1 permits personal internal development/testing/research capture, local retention and offline replay; whether §6.5's anti-replication/competition restriction applies to a private single-owner tool; and the scope of §§6.6, 6.7 and 6.9 for non-commercial internal research and derived data. Save the support ticket/reference and exact text of the request in the private project evidence log; do not include credentials or raw market data.
- [ ] By **2026-11-24**, record Bybit's written response or explicitly record that no response was received. If unanswered or ambiguous, keep the live-capture gate `BLOCKED`; do not infer permission from endpoint reachability or silence. This external decision must not block synthetic fixtures, offline replay, parser work or documentation.
- [ ] Keep all public-feed checks strictly as development/conformance tests. Section 6.5 restricts replication/competition; §6.6 prohibits using the API or Service Data to monitor availability/performance/functionality for benchmarking purposes; do not publish uptime or latency benchmarks from these runs.
- [ ] Do not repackage/resell API or Service Data (Section 6.7) or commercially exploit the APIs (Section 6.9). Any future commercial/public NEXUS use requires separate review/permission.
- [ ] Keep raw exchange frames private; do not commit or redistribute them until retention, derived-data and redistribution rights are explicitly reviewed.
- [ ] Automated live smoke is gated by repository variable `NEXUS_BYBIT_PUBLIC_DATA_TERMS_APPROVED=true`; leave it unset until the owner records the terms decision and confirms that the exact intended activity is permitted. A missed 2026-11-24 response deadline does not auto-approve data use.


## Implementation progress (2026-11-15)

- [x] Added a public REST full-depth snapshot client and response validator in `src/nexus_bybit_recorder/snapshot.py`.
- [x] Extended the journal to store timestamped REST response bodies and metadata before parsing.
- [x] Added `BookSynchronizer` with bounded buffering, exact watermark bridge, `u=1` reset handling, gap invalidation and disconnect invalidation.
- [x] Integrated REST snapshot acquisition and live synchronization into the public recorder CLI; the live CLI journals book-state transitions.
- [x] Added unit tests for REST response validation, synchronization, reset/gap behavior, exhaustive record classification and a mocked end-to-end live loop (WS frames → REST snapshot → `LIVE_VALID` → replay).
- [x] Parser-hardening CI passed on Python 3.11/3.12/3.13: [run 43646661506](https://github.com/PandaGarry/NEXUS/actions/runs/43646661506), testing code commit `54b0a510b254f91f1e06346a3b6ce61e13f41999`; all three matrix jobs passed, 37 tests per runtime. The three new tests for malformed level shape, non-integer sequence values and boolean sequence values passed. The live-public-smoke job was correctly skipped by the terms gate. Workflow path filters now include M2 acceptance/milestone docs so subsequent checklist changes also trigger CI.
- [ ] Integrated 10-minute live run [43642980172](https://github.com/PandaGarry/NEXUS/actions/runs/43642980172) was cancelled by subsequent code updates before the capture step completed. Future automated live smoke is skipped unless `NEXUS_BYBIT_PUBLIC_DATA_TERMS_APPROVED=true` is set after the terms gate is cleared. A deterministic mocked live-loop integration test now passes, but it is not exchange-live evidence. Hosted-runner latency remains out of scope.
- [x] Added `replay_book()` and a deterministic fixture that reconstructs the same watermark from raw REST/WS journal events and compares it with a recorded `LIVE_VALID` marker.
- [ ] Replay evidence from the integrated live archive must pass the workflow gate; the unit fixture alone is insufficient.
- [ ] Fault-injection and reconnect evidence remain outstanding; M2 is not accepted.
- [x] Live cross-sequence regression, malformed root-frame rejection, post-snapshot `seq` regression and same-snapshot-`seq`/different-`u` handling are tested on all supported Python runtimes; [CI 43680047302](https://github.com/PandaGarry/NEXUS/actions/runs/43680047302) passed all 41 tests on Python 3.11/3.12/3.13 after the latest documentation/terms-gate changes.
- [x] Strict delta parser hardening: `u`/`seq` reject booleans and non-integers; malformed level shapes and non-string price/quantity fields fail closed. Evidence: commits [`ce773e1`](https://github.com/PandaGarry/NEXUS/commit/ce773e190404ec33b2b6d2b09195fd7e8faf697c) and [`54b0a51`](https://github.com/PandaGarry/NEXUS/commit/54b0a510b254f91f1e06346a3b6ce61e13f41999); all 37 tests passed on Python 3.11/3.12/3.13 in run 43646661506.
- [x] Latest runtime hardening (commit [`37e6c68`](https://github.com/PandaGarry/NEXUS/commit/37e6c6807ded23f971715b1301155aa57b0b5ffe)) invalidates immediately on a live cross-sequence regression and safely rejects non-object WS roots; two regression tests were added. [CI run 43679738573](https://github.com/PandaGarry/NEXUS/actions/runs/43679738573) passed all 39 tests on Python 3.11/3.12/3.13 at branch head `b4eda7cd5fe49b5a8370ef84985981f9725de5ca`. Protocol-edge [CI run 43679930904](https://github.com/PandaGarry/NEXUS/actions/runs/43679930904) passed all 41 tests on Python 3.11/3.12/3.13 at code head `bdf5d27e0adaf835f7725ea509d6adca55a1f0f6`. Subsequent terms/documentation changes were rechecked by [CI run 43680047302](https://github.com/PandaGarry/NEXUS/actions/runs/43680047302), which again passed all 41 tests on all three runtimes. live smoke was skipped by the terms gate.


- [x] Independent Arena review findings were reconciled against the implementation branch. C1 (live sequence regression) was already fixed and covered by an immediate-invalidation regression test; C2 (missing b/a) now fails closed in buffering and live states; C3 (u=1 with empty REST sides) now returns NO_BOOK, never LIVE_VALID.
- [x] High-risk ingress handling: malformed/non-object WS frames and unexpected orderbook topics/symbols invalidate the generation and force reconnect. Synthetic live-loop tests cover malformed JSON and wrong-symbol orderbook frames.
- [x] Conflicting duplicate update IDs are detected by canonical payload digest in both live application and buffered snapshot bridging; exact duplicates remain deterministic. Conflicting and identical duplicate tests are included.
- [x] Snapshot bridge ResyncRequired preserves the latest buffered delta and immediately requests another snapshot. A targeted mocked regression test covers this path.
- [x] Replay now journals each orderbook transition with generation, symbol, watermark and book fingerprint; replay checks validity, watermarks and fingerprints. A tampered-delta test proves a changed payload is detected. Snapshot-fetch and validation failures are journaled as invalidation transitions.
- [x] Latest synthetic/unit CI at exact code head 2eb442a45c2931e8fd69429f760c4b1ee80ed703, run 43681007605, completed successfully. The Python 3.11/3.12/3.13 test matrix passed. Live-public-smoke remained skipped by the terms gate.
- [ ] These tests remain synthetic/mocked evidence. No live synchronized-book, real reconnect/reset/gap, or exchange-session replay evidence has been accepted.

- [x] Numeric price identity is canonicalized with exact Decimal semantics. Numerically equivalent wire strings map to one price key; duplicate numeric price levels in snapshots or deltas are rejected rather than silently overwriting each other.
- [x] Snapshot HTTP concurrency is bounded process-wide: cancelling an asyncio task no longer permits repeated orphaned to_thread requests to accumulate; overlapping requests fail fast while the prior blocking request still owns the single-flight slot.
- [x] Reconnect backoff no longer resets on WebSocket handshake success. It is reset only after a connection remains open for at least 30 seconds; shorter successful opens retain the accumulated exponential delay. Regression tests cover short-lived opens and the stability threshold. Implementation commits: `b753ee3` (runtime) and `b303c5c` (tests); CI run [#43682834296](https://github.com/PandaGarry/NEXUS/actions/runs/43682834296) was in progress when this checklist was updated. Arena must independently review the end-to-end reconnect behavior and jitter/cap/rate-window coverage before this item is treated as independently verified.
- [x] Exact runtime code head [bed5667](https://github.com/PandaGarry/NEXUS/commit/bed5667e2d68e76ff694a731a9c5ea9a458d775f) passed the Python 3.11/3.12/3.13 matrix in [CI 43681248092](https://github.com/PandaGarry/NEXUS/actions/runs/43681248092). Live-public-smoke remained skipped by the terms gate.
- [x] Latest PR head [`38dfbf2`](https://github.com/PandaGarry/NEXUS/commit/38dfbf274cf09f92ba40c841be0f64d24437e53d) passed the Python 3.11/3.12/3.13 unit-test matrix in [CI run 43682906493](https://github.com/PandaGarry/NEXUS/actions/runs/43682906493) (run #192); all three unit-test jobs succeeded. `live-public-smoke` was skipped by the terms gate. This verifies the current PR head's unit CI, not M2 live acceptance.
- [x] Checklist-only PR head [`33166f3`](https://github.com/PandaGarry/NEXUS/commit/33166f383c84b5453d63ee9fcf699a550539cd91) was also exercised by [CI run 43684811816](https://github.com/PandaGarry/NEXUS/actions/runs/43684811816) (run #194): Python 3.11/3.12/3.13 unit-test jobs all succeeded; live-public-smoke was skipped by the terms gate. This does not add live M2 evidence.
- [ ] Define and persist seeded-depth semantics before M2 acceptance: LIVE_VALID means sequence-consistent from the exact REST seed, not a globally complete book. Record seed depth per side and explicitly state RPI exclusion; Bybit REST full-depth is bounded to 10,000 levels per side.

## 0. Evidence and accounting

- [x] Re-opened and independently classified the original 10-minute artifact on 2026-11-15: 8,149 trade-topic, 2,998 orderbook-topic, 29 pong replies and 1 subscription acknowledgement; all 11,177 records reconcile and all raw SHA-256 checks passed.
- [ ] Preserve a user-controlled private copy of the artifact before its 2026-11-28 expiry; the inspection copy in the current working session is not a durable user-controlled archive.
- [x] Reconcile exactly 11,177 journal records with mutually exclusive categories: 8,149 `publicTrade`, 2,998 `orderbook.full`, 29 pong replies (`op=ping`, `ret_msg=pong`), 1 subscription acknowledgement, 0 malformed/non-JSON and 0 other. Categories sum exactly to 11,177.
- [x] Independent offline audit of artifact #10: ZIP SHA-256 matches GitHub artifact digest; all 11,177 per-frame raw SHA-256 values verify. All 2,998 orderbook deltas have `u` values 1440743–1443740 with no gaps, strictly increasing `seq` (846263141163–846270590664), no repeated/conflicting `u`, no missing/non-array `b/a`, and no numeric duplicate prices within either side. One connection generation; no REST snapshot or initial book state, therefore this is stream-segment integrity only, not M2/live-book acceptance.
- [ ] Independent Arena reproduces the artifact audit and checks additional invariants/mutations without publishing raw frames.
- [x] Disabled future raw-capture artifact uploads from the public Actions workflow in commit `54f2c15`; the live job validates its capture in-place and no longer uploads `evidence/`. This does **not** remove or retroactively privatize existing artifact #10 (ID `14131465205`), which remains available until deleted or expired.
- [ ] Keep the original artifact private until Bybit data terms and redistribution rights have been reviewed. Do not commit raw exchange data to the public repository by default.
- [ ] Add synthetic/minimal protocol fixtures to the repository only where licensing and terms permit; fixtures must be clearly labelled synthetic if synthetic.
- [ ] Record the Actions runner region as an environment fact only. Do not use hosted-runner wall/monotonic timing as a production latency benchmark.

## 1. REST snapshot acquisition

- [ ] Use the documented public endpoint `GET /v5/market/full_orderbook?category=linear&symbol=BTCUSDT` (not the top-of-book endpoint).
- [ ] Validate HTTP status, JSON shape, `retCode == 0`, `result.s`, `result.u`, `result.seq`, both sides and decimal levels.
- [ ] Journal the exact REST response body before parsing, with request URL (no secrets), HTTP status, local UTC wall time, monotonic receive time and connection generation.
- [ ] Bound HTTP timeout, response bytes, retries and snapshot request rate. Never silently accept an error body as a snapshot.
- [ ] Preserve explicit metadata that RPI orders are excluded.

## 2. Snapshot / buffered-delta bridge

- [ ] Subscribe to `orderbook.full.BTCUSDT` first and buffer raw deltas before requesting the REST snapshot.
- [ ] Validate every buffered event is a full-depth `type=delta` for the expected symbol.
- [ ] While buffering, require consecutive `u` within a connection generation; on discontinuity, discard the buffer and restart synchronization.
- [ ] If `seq` decreases, discard that delta as specified by Bybit; never sort events to hide wire-order problems.
- [ ] If snapshot `seq` is less than the first usable buffered delta `seq`, fetch a newer snapshot.
- [ ] Discard buffered deltas with `seq` lower than the snapshot `seq`.
- [ ] Require a buffered delta with both `seq` and `u` exactly equal to the snapshot watermark. If same `seq` has a different `u`, retry snapshot; do not guess.
- [ ] Initialize from the REST snapshot, then apply only deltas after the exact matching watermark in original receive order.
- [ ] Bound the delta buffer. Overflow invalidates synchronization and starts a clean resync.
- [ ] Do not expose a book to downstream consumers until the complete bridge succeeds.

## 3. Runtime continuity and fail-closed behavior

- [ ] For live updates, ignore stale `u` values below the local watermark.
- [ ] On `u` gap (`u > local_u + 1`), invalidate and resynchronize.
- [ ] On `u=1`, invalidate immediately and restart the documented snapshot synchronization procedure.
- [ ] On disconnect, reconnect, connection-generation change, malformed JSON/event, wrong symbol/topic, invalid decimal, crossed/locked book or buffer overflow, mark the book invalid.
- [ ] A reconnect must never inherit a `LIVE_VALID` book from the previous connection.
- [ ] Verify reconnect backoff across repeated short-lived successful socket opens followed by immediate disconnects/invalid frames. Backoff must not reset merely because the handshake succeeded; bound attempts per time window and test jitter/cap behavior to avoid venue connection storms.
- [ ] No strategy or analytics consumer may read a book while invalid or synchronizing.
- [ ] If snapshot acquisition repeatedly fails or cannot catch up, remain unavailable; never fall back to a stale book.

## 4. Replay and deterministic tests

- [ ] Journal WS frames and REST snapshot responses in one append-only, checksum-verified event journal with explicit record kinds.
- [ ] Replay must reconstruct the same valid/invalid state transitions and final book fingerprint from the recorded ordered events.
- [ ] Test exact watermark match; snapshot older than first delta; same `seq` / different `u`; `seq` decrease; `u` gap; `u=1` reset; duplicate/stale delta; malformed response; nonzero `retCode`; invalid levels; crossed book; buffer overflow; disconnect/reconnect; REST timeout.
- [ ] Include at least one fixture based on a legally retainable, redacted/synthetic protocol example and document its provenance.
- [ ] Assert no book is marked valid before exact snapshot alignment and all post-watermark deltas are applied.

## 5. Live evidence

- [ ] Capture a real public session with REST snapshot + WS deltas and a valid synchronized book.
- [ ] Record snapshot `u/seq`, matching delta `u/seq`, applied delta count, resync count, invalidation reason and final watermark.
- [ ] Demonstrate a controlled disconnect/reconnect or observed reconnect and prove the book becomes invalid then valid only after a new bridge.
- [ ] Demonstrate an injected `u=1` reset and an injected `u` gap; both must force resync.
- [ ] Keep hosted-runner timing out of latency claims. Any latency study requires a controlled, geographically relevant host, synchronized wall clock and monotonic elapsed-time measurements.

## 6. Acceptance decision

M2 is accepted only when all required sections above are complete, unit tests pass on Python 3.11/3.12/3.13, live evidence is archived with a reproducible replay, and the evidence register links the exact commit and CI run. Any uncompleted item remains explicitly open; target dates are not silently moved.

## 6A. Independent protocol cross-check and live comparison gate

**Protocol review checked 2026-11-15 against the official Bybit V5 documentation:**

- The `orderbook.full.{symbol}` stream is delta-only; there is no initial WS snapshot.
- `u` is consecutive within a session; a gap invalidates the local book, and `u=1` is a reinitialization signal.
- `seq` is monotonically increasing but explicitly **not guaranteed to be consecutive**. Never require `seq + 1`.
- During snapshot bridging, discard deltas with `seq` below the snapshot; if `seq` matches but `u` differs, retry the snapshot; initialize only when both values match. Apply remaining deltas in original receive order.
- Therefore exact equality of both snapshot/delta `seq` and `u` at the bridge point is the documented rule; the concern is not equality itself, but incorrectly treating `seq` as a consecutive counter or accepting a later unmatched event.

Official source: [Bybit full-depth orderbook synchronization procedure](https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob).

**Additional acceptance evidence required before M2 can be accepted:**

- [ ] Independent reviewer verifies the implementation line-by-line against the official procedure above, including `u` continuity, non-consecutive `seq`, reset handling, stale-event discard and exact bridge pair. Record reviewer, commit and findings.
- [ ] Add/confirm protocol-derived fixtures that explicitly demonstrate non-consecutive increasing `seq` is accepted, `u` gap is rejected, same `seq` with different `u` causes snapshot retry, and a `seq` decrease is discarded.
- [ ] On a real permitted session, run an independent REST-vs-WS reconciliation while the WS stream is already being journaled continuously. Record the REST request-start and response-receive wall/monotonic times, snapshot `seq/u`, and the current local-book `seq/u` at both times.
- [ ] Because the REST snapshot may be ahead of the local book when its response arrives, do **not** compare it immediately with the older local state. Continue buffering WS deltas, validate continuity, and advance/replay the local state through the delta whose `seq` and `u` exactly match the REST snapshot watermark. `seq` is monotonic but not consecutive; `u` is consecutive within a generation.
- [ ] At the exact REST watermark, compare the independently reconstructed local book with the REST snapshot over the top-N levels available in both. Use exact Decimal price/quantity comparisons; no arbitrary percentage tolerance. Record missing/extra levels, ordering, crossed/locked state and exact differences.
- [ ] Then apply all deltas after the REST watermark to both the snapshot-seeded book and the independently reconstructed book in original receive order. Compare their fingerprints at a later common watermark. This explicitly accounts for market changes during the REST request/response window.
- [ ] If the matching `seq/u` event is absent, continuity breaks, the buffer overflows, or the two reconstructions disagree, classify the check as INCONCLUSIVE/FAILED, invalidate and resynchronize; never explain unexplained differences away as timing noise.
- [ ] Report the full delta window (count and first/last `seq/u`), both comparison watermarks, top-N depth, exact decimal method and all differences. Do not compare states at different watermarks as if simultaneous.
- [ ] Preserve the raw evidence privately if terms permit, otherwise preserve a legally permitted redacted/synthetic reproduction and a reproducible report. Do not publish raw frames without rights review.

## Official protocol references checked 2026-11-15

- Bybit full-depth WebSocket and synchronization procedure: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob
- Bybit full-depth REST snapshot: https://bybit-exchange.github.io/docs/v5/market/full-ob


## Independent Arena audit A — remediation follow-up (2026-11-15)

Arena's report against `38dfbf2` identified three additional ingress/replay defects and clarified the retry cap. Remediation is implemented in the current branch; CI evidence for the resulting head is pending.

- [x] **Decimal resource bounds:** price and quantity strings are length-limited; coefficient precision and exponent are bounded before fixed-point canonicalization. `Decimal.normalize()` was removed from price-key construction to avoid context-sensitive overflow. Extreme `1e1000000` and `1e-1000000` deltas now fail closed through `BookSynchronizer.on_delta()` without an exception escaping.
- [x] **Duration enforcement:** the WebSocket frame iterator is bounded by the remaining monotonic deadline; reconnect backoff and rate-window waits are also clipped to the remaining duration. A silent connected socket stops when `--duration` expires; normal disconnect and cancellation paths still run.
- [x] **Strict JSON:** shared `strict_json_loads()` rejects duplicate object keys recursively. Live WS ingress, REST snapshot validation, journal-envelope parsing and replay all use the same policy. Duplicate-key frames invalidate the generation; duplicate-key journal envelopes fail integrity validation.
- [x] **Reconnect policy clarified:** after 8 attempts in a rolling 60-second window, the recorder waits until the oldest attempt expires and a slot becomes available; it does not terminate. The wait checks the recording deadline before another connection attempt.
- [x] **Strict reconnect delay cap:** jitter is included inside the 30-second maximum; total delay cannot exceed 30.0 seconds.
- [ ] **Verification pending:** exact current PR head must pass Python 3.11/3.12/3.13 unit CI. Add full lifecycle fault-injection coverage for repeated short-lived handshakes, stable reset, exceptions before handshake, rate-window exhaustion/release and cancellation. Unit helper tests do not replace this integration evidence.
- [ ] **M2 acceptance remains open:** no permitted synchronized live REST/WS session, controlled reconnect/reset/gap session, or permitted real-session replay has been accepted. These code fixes do not change the terms gate or authorize a new capture.
