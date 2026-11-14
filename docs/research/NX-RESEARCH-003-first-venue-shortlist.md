# NX-RESEARCH-003 — First-Venue Shortlist: Conditional Capability and Eligibility Review

**Date:** 2026-11-14  
**Status:** Preliminary research memo — no venue selected  
**Scope:** Bounded comparison of Coinbase and Kraken as candidate first venues for NEXUS v1; public official documentation only  
**Related:** NX-OWNER-DECISIONS-001 (OD-01..03), NX-ADR-001/002/004/005, NX-IF-001..005, ТЗ-NX-001/004/005/006  
**Decision boundary:** This memo does not establish the user's legal residence, account eligibility, preferred product, fee tier or actual account capabilities.

## 1. Executive result

The v1 architecture scope is now fixed to one venue and one dedicated account/subaccount. The exact venue and market family are not yet selected.

A responsible selection cannot be made from market-data features alone. It must be conditional on:
1. the user's actual legal residence and the legal entity serving the account;
2. product eligibility (spot, perpetual, perpetual-style dated future or standard future);
3. availability of a dedicated account/subaccount and API key permission scoping;
4. public/private stream semantics, recovery, order lifecycle and historical account-data coverage;
5. order-book depth required by NEXUS (L2 versus order-level L3);
6. fees, liquidity, rate limits, support and operational reliability for the intended instruments.

**Preliminary shortlist:** Coinbase and Kraken remain candidates, but for different product/market-data reasons. No winner is declared. Binance, Bybit and OKX are not shortlisted for a US-resident first account without a separately verified eligible legal/account route; this memo does not assume that the user is US-resident.

## 2. Candidate evidence matrix

| Capability | Coinbase | Kraken | NEXUS implication |
|---|---|---|---|
| Spot market data | Advanced Trade WebSocket documents ticker, ticker batch, level2, and authenticated user channel; Coinbase Exchange API separately documents heartbeat, level2, matches, full and user channels | Spot public REST PreTrade returns aggregated top-10 book levels and per-level order count; PostTrade exposes trade history with timestamp cursor | Both have useful public market-data surfaces; exact channel recovery, depth and continuity must be tested |
| Order-level L3 evidence | The sources reviewed here do not establish public order-by-order L3 for the selected Coinbase retail API | Kraken FIX documentation distinguishes Spot L2 and Futures L3 examples; it includes order IDs and queue timestamps for L3. Spot L3 access is not established by this evidence | Do not advertise L3 support based on a generic exchange label; verify exact product, feed and access entitlement |
| Private execution/account data | Coinbase Exchange API documents authenticated order cancellation and order/user event feeds; Advanced Trade has its own API surface and must not be conflated with Exchange API | Kraken API key permission documentation separates funds query, open/closed order query, order create/modify, cancel/close and ledger query permissions | Build per-product adapter contracts; never assume APIs across Coinbase product families are interchangeable |
| Key permission separation | API permission model must be verified against the exact selected API and account | Kraken documents distinct permissions for query funds, query orders/trades, modify trades, close trades, ledger query and withdrawals | Trading key must omit withdrawal/deposit/transfer capabilities wherever the venue supports that separation |
| Derivatives and eligibility | US Derivatives are offered through Coinbase Financial Markets to eligible US/Canada/EEA users; US product is cash-margined. Global derivatives are separately restricted to supported regions outside the US. US perpetual-style futures are not interchangeable with non-US perpetual swaps | Kraken states non-US Kraken Derivatives and Kraken Derivatives US are separate offerings. Its eligibility page describes different product availability and geographic restrictions; newer product material may describe additional US crypto products, so exact current product/API eligibility must be confirmed directly | Product/legal entity is a first-class adapter capability; never infer perpetual availability from a venue brand name |
| Dedicated strategy isolation | Advanced Trade portfolios support separate trading environments and portfolio-scoped API keys | Subaccounts are a candidate account-isolation model; exact availability and limits for the intended personal/business account must be verified | OD-01 requires a dedicated account/subaccount, not merely strategy labels inside one shared key |
| Historical/reconciliation evidence | Exact retention and cursor guarantees for all required order/fill/ledger events remain to be tested | Kraken futures docs expose paginated position-event history; spot history coverage and account-specific retention still need review | Historical endpoint availability does not prove complete recovery; retention windows and cursor semantics must be tested |

## 3. Candidate-specific assessment

### 3.1 Coinbase

**Strengths evidenced**
- Advanced Trade WebSocket exposes market-data channels including level2 and ticker; the authenticated user channel is documented.
- Coinbase Exchange API documents authenticated order cancellation and user/full order event feeds.
- Coinbase Advanced Trade supports multiple portfolios, with dedicated API keys scoped to portfolios.
- Coinbase US derivatives are provided through a regulated US entity for eligible customers; the US derivatives product is cash-margined.

**Constraints / unresolved**
- Coinbase Exchange API and Advanced Trade API are distinct surfaces. Capabilities, auth, IDs, event semantics and rate limits must be reviewed for the one actually selected.
- US derivatives are not the same product as a non-US perpetual swap; Coinbase's US perpetual-style futures are cash-margined derivatives with their own contract terms.
- Global derivatives are restricted to supported regions outside the US.
- The sources reviewed establish L2, not order-level L3, for the selected retail-facing API.
- Eligibility, account portfolio availability, API access and exact product terms require account-specific confirmation.

**Preliminary fit:** strong candidate for a US-eligible spot-first integration or regulated US futures evaluation, depending on the intended product; not yet established as an L3 order-flow venue.

### 3.2 Kraken

**Strengths evidenced**
- Spot public API provides aggregated order-book levels and trade-history cursoring.
- Kraken API key permissions are explicitly separated for funds query, order/trade query, modify, cancel/close and ledger query.
- FIX documentation describes order IDs and queue-entry timestamps for L3 market-data messages in its L3 example.
- Kraken's futures API documentation exposes position-event history and analytics categories including open interest, aggressor differential, CVD, liquidation volume and funding.

**Constraints / unresolved**
- The reviewed FIX document labels its examples Spot L2 and Futures L3; it does not prove retail Spot L3 entitlement.
- Kraken Derivatives and Kraken Derivatives US are separate product/legal paths. Eligibility pages and newer product material need reconciliation against the exact account, state/country and API product before selection.
- Futures order, fill, funding and position history semantics must be reviewed against the exact product and API version.
- Dedicated subaccount availability, API key scoping and history retention for the intended account type require confirmation.

**Preliminary fit:** strong candidate for deeper microstructure/futures research and granular key permissions; actual v1 fit depends on the user's eligible product path and whether required L3 feed access is available.

## 4. Current recommendation

Do not select a venue yet. Carry Coinbase and Kraken into a short, evidence-driven qualification pass, then select exactly one.

Selection order:
1. legal eligibility and exact product availability for the user's actual account jurisdiction;
2. dedicated account/subaccount and API permission model;
3. exact market family and instrument contract model;
4. market-data feed depth, sequence/recovery and historical coverage;
5. private order/fill/account events and reconciliation completeness;
6. liquidity, fees, rate limits and operational support;
7. venue-specific emergency command semantics.

If only L2 is available for the selected account, NEXUS may still support a valid L2-based Order Flow feature set, but it must not claim order-level queue reconstruction or L3 analytics. If a US product is a dated/perpetual-style future rather than a true perpetual swap, funding, expiry and settlement semantics must be modeled distinctly.

## 5. Bounded next research task and exit criteria

Next task: exact official-doc/API capability matrix for Coinbase Advanced Trade versus Kraken Spot and the relevant Kraken derivatives entity, after the legal jurisdiction and product family are known.

Exit criteria:
- one candidate has documented account eligibility for the user's actual jurisdiction;
- one precise API product/version is selected (not a mix of similarly named APIs);
- market data, private order/fill, balances/positions, instrument rules, fees/funding, history and emergency capabilities are source-pinned;
- unknowns and unavailable capabilities are explicit;
- no material unresolved capability gap changes the NEXUS v1 architecture;
- recommendation names one venue and one dedicated account/subaccount configuration, with reasons and caveats.

No account connection, credential handling, order placement, legal advice or live trading is part of this research.

## 6. Official sources reviewed

- Coinbase, **Advanced Trade WebSocket feeds**: https://help.coinbase.com/en/developer-platform/websocket-feeds/advanced-trade
- Coinbase, **Exchange WebSocket feeds**: https://help.coinbase.com/en/developer-platform/websocket-feeds/exchange
- Coinbase, **Cancel an order (Exchange API)**: https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/orders/cancel-an-order
- Coinbase, **Advanced Trade Portfolios**: https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/guides/portfolios
- Coinbase, **Get started with US Derivatives**: https://help.coinbase.com/en/coinbase/derivatives/us-derivatives-intro
- Coinbase, **Get started with Global Derivatives**: https://help.coinbase.com/en/coinbase/derivatives/global-derivatives-get-started
- Kraken, **Pre-Trade Data (Spot REST order book)**: https://docs.kraken.com/api/docs/rest-api/get-pre-trade
- Kraken, **Post-Trade Data (Spot trade history)**: https://docs.kraken.com/api/docs/rest-api/get-post-trade
- Kraken, **FIX Market Data Snapshot Full Refresh**: https://docs.kraken.com/api/docs/fix-api/mdsfr-fix
- Kraken, **Get API Key Info / permissions**: https://docs.kraken.com/api/docs/rest-api/get-api-key-info
- Kraken, **Get position update events (Futures)**: https://docs.kraken.com/api/docs/futures-api/history/get-position-events
- Kraken, **Derivatives eligibility requirements**: https://support.kraken.com/articles/360023786632-kraken-derivatives-eligibility
- Kraken, **Derivatives US product/compliance overview**: https://www.kraken.com/learn/futures-trading-us-futures-compliance

## 7. Limitations

This is a documentation review, not an API experiment or legal opinion. Web pages may change; account-specific eligibility, API entitlements, current rate limits, feed availability, data retention and actual runtime behavior remain unverified. No source code, tests, builds, benchmarks, credentials, exchange connections or orders were used.
