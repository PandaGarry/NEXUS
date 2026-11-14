# NEXUS — venue qualification matrix

**Last reviewed:** 2026-11-15  
**Purpose:** compare candidate venues without making any venue the architectural center or assuming user eligibility.  
**Status convention:** `YES` / `NO` / `UNKNOWN` only. Every non-UNKNOWN claim requires a dated source and exact product/API scope. This initial matrix deliberately leaves unverified cells UNKNOWN.

## 1. Candidate universe (not a selection)

| Candidate | Why it is in the research universe | Current role | Selection status |
|---|---|---|---|
| Bybit | Concrete V5 public WS/REST protocol; useful first recorder probe | Reference adapter experiment #1 | Not selected for trading |
| Coinbase | Distinct API family and product/legal-entity model; preliminary official-doc research exists | Candidate for materially different adapter #2 | Not selected |
| Kraken | Different spot/futures API surfaces and documented key permissions; preliminary official-doc research exists | Candidate for materially different adapter #2 | Not selected |
| OKX | Potentially useful distinct market-data and derivatives model | Discovery backlog; no qualification claim in this register | Unknown |
| Binance | Potentially useful large-scale spot/derivatives API comparator | Discovery backlog; no qualification claim in this register | Unknown |
| Domestic brokers / listed derivatives venues | May offer a materially different legal, clearing and instrument model | Separate broker/venue adapter research | Not selected |

This list is intentionally not a ranking. The second adapter should be chosen for architectural contrast, not brand popularity. Coinbase or Kraken are initial candidates; exact market family and API must be selected only after the relevant product/eligibility review.

## 2. Qualification matrix

All entries start as **UNKNOWN** until the exact jurisdiction, account type, product family and API version are identified and evidenced.

| Qualification dimension | Bybit | Coinbase | Kraken | OKX | Binance |
|---|---|---|---|---|---|
| Owner's jurisdiction / KYC eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Exact serving legal entity / ToS | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Spot eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Perpetual swap eligibility | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Dated futures / expiry semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Public WS trades with stable trade ID | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Public WS L2 snapshot + delta semantics | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Book continuity proof (sequence / checksum / snapshot ID) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| REST snapshot bridge and resync behavior | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Public L3 / order-level feed entitlement | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
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

## 3. Evidence record required for each cell

Every qualified cell must record:

- venue and exact product family (e.g. spot, linear perpetual, inverse perpetual, dated future);
- exact API family/version and endpoint/channel;
- answer: YES / NO / UNKNOWN;
- official source URL and source publication/update date where available;
- date checked;
- test evidence (fixture, sandbox, live public stream, account-level test) and environment;
- limitations, exceptions and unresolved dependencies;
- reviewer and next revalidation trigger.

A general venue help page does not prove a specific API feature. A public endpoint does not prove account eligibility. A sandbox does not prove production behavior. A source document does not prove runtime feed continuity.

## 4. Qualification stages

1. **Public data-only:** public feed availability, terms/data rights, schema, timestamps, trade IDs, snapshot/delta continuity, resync, historical coverage, rate limits.
2. **Sandbox/test execution:** exact product and sandbox eligibility; client order ID constraints; order lifecycle; timeout/duplicate behavior; private streams; reconciliation; reduce-only and cancel semantics.
3. **Personal live eligibility:** owner's actual residence/citizenship where relevant, KYC/account type, serving entity, exact product availability, API automation terms, fee tier, key permissions and local legal requirements. This gate is independent from public data research.
4. **Production approval:** adapter conformance, risk/execution/reconciliation gates, emergency operations, observability, backup/restore and explicit owner authorization.

The lack of a live-eligible venue does not block public data research. The lack of historical L2 does not justify pretending that L2 history exists; it changes which experiments can be concluded.

## 5. Architecture rule: first concrete, second contrasting, then abstract

- Adapter #1 is implemented concretely and may initially contain venue-specific parsing and recovery semantics.
- Adapter #2 must be materially different in API/product/feed semantics. Coinbase and Kraken are candidate choices; the exact one is an open decision.
- Compare both implementations and their failure/recovery models.
- Only then define the smallest shared contracts supported by both. Do not force a lowest-common-denominator interface that erases useful venue-specific guarantees.
- Keep raw source frames, source timestamps and venue-specific evidence. Normalize only into a shared layer with explicit provenance and loss annotations.

## 6. Core data identity principles (target, not current implementation claim)

Future normalized records should carry:

- `venue_id`;
- internal `instrument_id), with a versioned mapping to venue-native symbol/product identifiers;
- exchange event time (and source timestamp semantics);
- local UTC receive wall time;
- host-local monotonic receive time (only comparable within the same host boot);
- connection generation/session identifier;
- raw source reference / payload digest;
- source-specific continuity evidence.

Each adapter owns its own parser and continuity proof. The core consumes a venue-neutral statement of continuity/validity, not Bybit's `u` or `seq`, Coinbase's sequence semantics, or Kraken-specific checksums.

## 7. Order command contract (future execution scope)

The domain-level command identity should be stable and idempotent. Each venue adapter maps it to the venue's client-order identifier subject to that venue's length, character, uniqueness and retention constraints. After an ambiguous submit timeout, the common process is **reconcile before retry**; the actual lookup endpoints, cursor semantics and duplicate behavior are adapter-specific. This is a design target, not implemented functionality.

## 8. References and current evidence

- Existing preliminary comparison: [NX-RESEARCH-003 — Coinbase/Kraken shortlist](research/NX-RESEARCH-003-first-venue-shortlist.md) (documentation research only; contains historical and jurisdiction-dependent conclusions that must be revalidated before selection).
- Bybit recorder prototype: [PR #19](https://github.com/PandaGarry/NEXUS/pull/19).
- Bybit public-feed API research: [PR #17](https://github.com/PandaGarry/NEXUS/pull/17).
- Venue eligibility research: [NX-RESEARCH-009](research/NX-RESEARCH-009-russia-jurisdiction-product-and-venue-eligibility.md) on the relevant research branch. Do not treat a branch-only document as a main-branch accepted decision.
- Official sources must be pinned per capability in follow-up research. This matrix intentionally does not convert previous high-level research into current universal YES/NO claims.

## 9. Explicit non-goals

This matrix does not select a live venue, infer the user's residence, authorize account connection, or establish legal advice. No credentials, private API, order placement or live trading are part of the current data-only work.
