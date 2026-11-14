# NEXUS — venue qualification matrix

**Last reviewed:** 2026-11-15  
**Purpose:** compare candidate venues without making any venue the architectural center or assuming user eligibility.  
**Status convention:** YES / NO / UNKNOWN. Every non-UNKNOWN claim is scoped to an exact API/product and backed by a dated source. A documented public feed does not prove account eligibility or production readiness.

## 1. Candidate universe (not a live-venue ranking)

| Candidate | Why it is in the research universe | Current role | Selection status |
|---|---|---|---|
| Bybit | Concrete V5 full-depth public stream and linear derivatives market; first live raw capture succeeded | Reference adapter experiment #1 | Not selected for trading |
| Kraken Spot WebSocket v2 | Spot L2 stream sends a WS snapshot and updates with CRC32 checksum; materially contrasts with Bybit full-depth delta-only + REST snapshot model | **Recommended technical adapter #2 candidate** | Public protocol research only; not selected for trading |
| Coinbase Advanced Trade | Distinct API/product family and useful comparator; do not conflate with Coinbase Exchange API | Alternative technical adapter #2 candidate | Not selected |
| OKX | Potentially useful distinct market-data and derivatives model | Discovery backlog; no qualification claim here | Unknown |
| Binance | Potentially useful large-scale spot/derivatives API comparator | Discovery backlog; no qualification claim here | Unknown |
| Domestic brokers / listed derivatives venues | May offer a materially different legal, clearing and instrument model | Separate broker/venue adapter research | Not selected |

**Why Kraken Spot is the current technical recommendation for adapter #2:** Bybit's full-depth channel is delta-only and requires a REST snapshot plus u/seq alignment. Kraken Spot WebSocket v2 book documents an initial snapshot followed by updates and a CRC32 checksum over the top 10 bid/ask levels; its trade channel has a per-book trade identifier and RFC3339 timestamp. This gives us a meaningful contrast in market type (spot vs linear perpetual), initialization and continuity evidence. This is a technical test choice only, not a live-trading recommendation or eligibility finding.

Coinbase remains a valid alternative if a source-backed review identifies a stronger protocol contrast or materially better test conditions.

## 2. Evidence-backed public-data snapshot (checked 2026-11-15)

| Public-data capability | Bybit V5 linear | Kraken Spot WS v2 | Coinbase Advanced Trade |
|---|---|---|---|
| Public trades channel documented | YES | YES | UNKNOWN in this snapshot |
| Trade ID documented | YES — execution ID i | YES — trade_id, unique per book | UNKNOWN |
| Trade event timestamp documented | YES | YES — RFC3339 | UNKNOWN |
| L2 book documented | YES — full depth | YES — aggregated L2 | UNKNOWN in this snapshot |
| WS initial book snapshot | NO — full-depth stream is delta-only | YES — snapshot can be requested and defaults true | UNKNOWN |
| WS incremental updates | YES — delta-only | YES — update messages | UNKNOWN |
| Continuity evidence documented | YES — update ID u and cross sequence seq | YES — CRC32 checksum for top 10 bids/asks | UNKNOWN |
| REST snapshot required for initial book | YES | NO for documented WS snapshot flow | UNKNOWN |
| Public L3 / order-level feed entitlement | UNKNOWN | UNKNOWN for Spot; separate FIX examples show Futures L3 | UNKNOWN |
| Live public smoke evidence in NEXUS | YES — 10-minute capture/replay | NO | NO |

### Bybit V5 linear evidence

- Full-depth WS topic orderbook.full.{symbol} is explicitly delta-only; no initial snapshot is sent. A REST full-depth snapshot must be obtained and aligned with buffered deltas.
- u is consecutive within a session and resets to 1 on reinitialization; seq is monotonic but not necessarily consecutive.
- Full-depth stream excludes RPI orders.
- NEXUS run #10 captured 8,149 public trade messages and 2,998 full-depth delta messages over approximately 10 minutes. One connection generation was observed; this does not prove reconnect recovery or valid book reconstruction.

Official source: https://bybit-exchange.github.io/docs/v5/websocket/public/full-ob  
Trade channel: https://bybit-exchange.github.io/docs/v5/websocket/public/trade

### Kraken Spot WebSocket v2 evidence

- book is aggregated L2, with supported depths 10, 25, 100, 500 and 1,000.
- A snapshot is sent on subscription by default; it includes CRC32 checksum for top 10 bids and asks.
- Updates include the same checksum; multiple updates to the same price level in one message must be processed sequentially.
- trade events include taker side, quantity, price, per-book trade_id and RFC3339 timestamp; a message may batch multiple trades.
- This is L2, not proof of Spot L3/order-level access.

Official sources:
- Book L2: https://docs.kraken.com/api/docs/websocket-v2/book
- Trades: https://docs.kraken.com/api/docs/websocket-v2/trade

## 3. Full qualification matrix

The following remain UNKNOWN until exact jurisdiction, account type, product family and API version are identified and evidenced.

| Qualification dimension | Bybit | Coinbase | Kraken | OKX | Binance |
|---|---|---|---|---|---|
| Owner's jurisdiction / KYC eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Exact serving legal entity / ToS | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Spot eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Perpetual swap eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Dated futures / expiry semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Historical trade archive coverage / start date | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Historical L2 archive coverage | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Private order/fill/account streams | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| REST reconciliation for unknown order outcome | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Client order ID constraints / idempotency semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Timeout / duplicate-submit behavior | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Rate limits and recovery limits | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Sandbox / testnet availability and differences | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Cancel-on-disconnect behavior | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Reduce-only semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| API key permission separation / no-withdrawal scope | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| IP allowlisting | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Fees / funding / settlement specification | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Market-data license / redistribution restrictions | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Specification change / deprecation policy | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

## 4. Evidence record required for each cell

Every qualified cell must record:
- venue and exact product family (spot, linear perpetual, inverse perpetual, dated future, etc.);
- exact API family/version and endpoint/channel;
- answer: YES / NO / UNKNOWN;
- official source URL and source publication/update date where available;
- date checked;
- test evidence (fixture, sandbox, live public stream, account-level test) and environment;
- limitations, exceptions and unresolved dependencies;
- reviewer and next revalidation trigger.

A general venue help page does not prove a specific API feature. A public endpoint does not prove account eligibility. A sandbox does not prove production behavior. A source document does not prove runtime feed continuity.

## 5. Qualification stages

1. **Public data-only:** public feed availability, terms/data rights, schema, timestamps, trade IDs, snapshot/delta continuity, resync, historical coverage and rate limits.
2. **Sandbox/test execution:** exact product and sandbox eligibility; client order ID constraints; order lifecycle; timeout/duplicate behavior; private streams; reconciliation; reduce-only and cancel semantics.
3. **Personal live eligibility:** owner's actual residence/citizenship where relevant, KYC/account type, serving entity, exact product availability, API automation terms, fee tier, key permissions and local legal requirements. This gate is independent from public data research.
4. **Production approval:** adapter conformance, risk/execution/reconciliation gates, emergency operations, observability, backup/restore and explicit owner authorization.

The lack of a live-eligible venue does not block public data research. The lack of historical L2 does not justify pretending that L2 history exists; it changes which experiments can be concluded.

## 6. Architecture rule: first concrete, second contrasting, then abstract

- Adapter #1 is implemented concretely and may initially contain venue-specific parsing and recovery semantics.
- Adapter #2 candidate is Kraken Spot WS v2, subject to a bounded protocol/terms review. Coinbase Advanced Trade remains the alternative.
- Compare both implementations and their failure/recovery models.
- Only then define the smallest shared contracts supported by both. Do not force a lowest-common-denominator interface that erases useful venue-specific guarantees.
- Keep raw source frames, source timestamps and venue-specific evidence. Normalize only into a shared layer with explicit provenance and loss annotations.

## 7. Core data identity principles (target, not current implementation claim)

Future normalized records should carry:
- venue_id;
- internal instrument_id, with a versioned mapping to venue-native symbol/product identifiers;
- exchange event time (and source timestamp semantics);
- local UTC receive wall time;
- host-local monotonic receive time (only comparable within the same host boot);
- connection generation/session identifier;
- raw source reference / payload digest;
- source-specific continuity evidence.

Each adapter owns its own parser and continuity proof. The core consumes a venue-neutral statement of continuity/validity, not Bybit's u or seq, Coinbase's sequence semantics, or Kraken's checksum as if they were interchangeable.

## 8. Order command contract (future execution scope)

The domain-level command identity should be stable and idempotent. Each venue adapter maps it to the venue's client-order identifier subject to that venue's length, character, uniqueness and retention constraints. After an ambiguous submit timeout, the common process is **reconcile before retry**; the actual lookup endpoints, cursor semantics and duplicate behavior are adapter-specific. This is a design target, not implemented functionality.

## 9. References and current evidence

- Existing preliminary comparison: [NX-RESEARCH-003 — Coinbase/Kraken shortlist](research/NX-RESEARCH-003-first-venue-shortlist.md) (documentation research only; contains historical and jurisdiction-dependent conclusions that must be revalidated before selection).
- Bybit recorder prototype: [PR #19](https://github.com/PandaGarry/NEXUS/pull/19).
- Bybit public-feed API research: [PR #17](https://github.com/PandaGarry/NEXUS/pull/17).
- Second adapter qualification issue: [Issue #21](https://github.com/PandaGarry/NEXUS/issues/21).
- Venue eligibility research: [NX-RESEARCH-009](research/NX-RESEARCH-009-russia-jurisdiction-product-and-venue-eligibility.md) on the relevant research branch. Do not treat a branch-only document as a main-branch accepted decision.

## 10. Explicit non-goals

This matrix does not select a live venue, infer the user's residence, authorize account connection, or establish legal advice. No credentials, private API, order placement or live trading are part of the current data-only work.
