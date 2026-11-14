# NX-RESEARCH-009 — Russia Jurisdiction, Product Classification & First-Venue Eligibility

**Status:** RESEARCH ONLY / LEGAL REVIEW REQUIRED / NO VENUE SELECTED  
**As-of date:** 2026-11-14  
**Owner context:** Individual owner is a Russian citizen residing in the Russian Federation; current accounts are personal retail bank accounts. Formal legal-residency status under the applicable statutory definition, broker qualification status and exact exchange KYC/contracting entity must still be evidenced.  
**Purpose:** Determine which market/product lanes can be investigated without assuming that a technically reachable API is legally or operationally eligible.

> This is an engineering research note, not a legal opinion, sanctions opinion, tax opinion or permission to trade. It separates primary-source facts from engineering interpretation and unresolved legal questions. No attempt to bypass venue restrictions, KYC, sanctions, Russian law or bank controls is contemplated.

## 1. Executive disposition

**Do not select a foreign exchange or enable live trading yet.** The Russian regulatory framework materially changes the first-venue decision. It is no longer sufficient to ask whether a venue's public country list includes Russia or whether its API accepts orders.

The investigation produces three distinct lanes:

1. **Russian regulated crypto-linked derivatives (MOEX / SPB Exchange through a broker):** real instruments and existing broker APIs are documented, but the current crypto-index products found are restricted to qualified investors. They are cash-settled financial instruments, not ownership of BTC/ETH and not equivalent to global USDT perpetuals.
2. **Russian regulated spot digital-currency access (a CBR-registered broker or crypto-exchange organization):** a domestic regulatory route is emerging. ООО «Т-ИНВЕСТ ЛАБ» has an active CBR record with the right to operate as an organization exchanging digital currencies from 2026-10-06, in addition to brokerage and depository permissions. A public crypto trading API and an order-book execution interface have **not** been evidenced.
3. **Foreign centralized venues (Bybit Global / OKX Global and others):** public technical/API documentation exists, but Russian-law eligibility, the exact contracting entity, account-specific KYC, product classification and the future Article 30 regime remain unresolved. These venues are research-only candidates, not approved live venues.

**Current conclusion:** the first live product cannot be chosen until (a) the owner's qualified-investor status is established, (b) the target product is classified (spot digital currency, foreign digital instrument, exchange-traded crypto-index future or another derivative), and (c) counsel confirms the applicable law for the owner, venue entity, software and funding/withdrawal flow.

## 2. Russian Federal Law No. 282-FZ — engineering-relevant facts

Primary legal text: [Federal Law No. 282-FZ of 2026-08-04, official publication](https://publication.pravo.gov.ru/document/0001202608040007). The Bank of Russia maintains the [cryptocurrency regulation FAQ](https://www.cbr.ru/explan/cryptocurrency/) and [crypto-market launch / registers page](https://www.cbr.ru/develop/cryptocurrency/).

### 2.1 Effective dates and resident route

- The law generally entered into force on **2026-09-01**.
- Part 1 of Article 30 enters into force on **2027-07-01**.
- Article 30(1), once effective, states that residents who are not persons organizing digital-currency circulation may transact in digital currencies only through or with persons organizing such circulation, subject to enumerated exceptions.
- The Bank of Russia's FAQ (answer 9, updated 2026-10-12) explains that from 2027-07-01 residents may transact only through the persons recognized under Chapter 4, including a licensed broker or a crypto-exchange organization included in the Bank of Russia register.
- The Bank of Russia FAQ (answer 10, updated 2026-10-12) says direct P2P transactions between individuals are not in the permitted list from 2027-07-01.
- Article 30(2) prohibits assisting residents in transactions that violate the law, including providing software for such transactions. The exact application to a privately developed, owner-operated tool, to particular foreign-venue products, and to transactions before/after 2027-07-01 is a **legal-review question**. NEXUS must not assume that private/self-use status creates an exemption.

**Engineering interpretation:** a foreign venue's global country list is not enough to qualify it for a Russian resident. For a live adapter, NEXUS needs a dated legal eligibility decision that addresses the actual product, contracting entity and transaction flow. A legal entity abroad, different IP address, different app store or account opened through another person is not an approved workaround and does not automatically change the owner's statutory residency or beneficial-owner analysis.

### 2.2 Retail qualification, testing and limits

Article 31 and Article 32 create separate conditions for qualified and non-qualified residents:
- A broker acquiring digital currency for a non-qualified resident must satisfy the testing, risk-warning, annual-limit and publicly-admitted-instrument conditions in Article 31(1).
- For a qualified resident, Article 31(2) still requires the relevant test and risk warning.
- Article 31(3) applies the corresponding rules to a crypto-exchange organization and other named intermediaries.
- The Bank of Russia's Directive No. 7441-U (2026-09-11), published 2026-11-06 after registration, defines the annual monetary-equivalent limit and the relevant eligible-asset / market criteria. The exact effective date and final operative values must be checked before implementation; this report intentionally does not hard-code a retail limit.
- A prior qualified-investor status may carry over for digital-currency transactions in the circumstances described in Bank of Russia FAQ answer 14 (updated 2026-10-26). The owner's status must be confirmed by the broker, not inferred from account balance or this report.

**Required evidence:** broker-issued qualified-investor status, product access flag and test status. For T-Invest API, the documented `GetInfo` response can expose qualified-investor status and types of instruments available after testing. Never infer eligibility from merely having a T-Bank personal bank account.

### 2.3 Stablecoins and self-custody

- Bank of Russia FAQ answers 3–4 (updated 2026-10-12) state that USDT may be classified as a foreign digital instrument, and that foreign stablecoins are subject to the same Federal Law No. 282-FZ requirements applicable to digital currencies, regardless of classification.
- Bank of Russia FAQ answer 11 (updated 2026-10-12) says a natural person may not transfer digital currency from a digital account to their own non-custodial wallet under Article 31(9). Article 31 contains limited exceptions and additional conditions for certain transfers; it is not a general permission for unrestricted self-custody withdrawals.
- Article 31(8)–(9) must be read together with the relevant Bank of Russia interpretations. A generic “withdraw to any wallet” feature cannot be assumed available to an RF resident.

**Engineering consequence:** NEXUS's existing no-custody / no-withdrawal design remains appropriate. Any future transfer, deposit, wallet or withdrawal feature needs its own legal and venue qualification; it must not be smuggled into a trading adapter.

### 2.4 Product classification is not optional

The law distinguishes digital currency from foreign digital instruments. The Bank of Russia FAQ says classification of a foreign stablecoin depends on its issuance conditions, while the same statutory requirements apply to its circulation.

The following must be classified separately:
- spot BTC/ETH;
- USDT or another stablecoin;
- a perpetual contract whose underlying is a crypto index but whose settlement is fiat;
- a contract whose settlement is USDT or another foreign digital instrument;
- a tokenized claim or other foreign digital instrument;
- a Russian exchange-traded derivative referencing a crypto index.

Do not infer that a crypto-index future is legally identical to spot crypto, or that a cash-settled derivative is automatically outside Law No. 282-FZ. Obtain a product-specific legal classification before live execution.

## 3. Domestic regulated candidates

### 3.1 ООО «Т-ИНВЕСТ ЛАБ»

The Bank of Russia's participant record shows:
- status: active;
- right to conduct the activity of an organization exchanging digital currencies from **2026-10-06**;
- brokerage license 045-14134-100000 from 2022-05-20;
- depository license 045-14135-000100 from 2022-05-20;
- dealer license 045-14087-010000 from 2020-06-17.

Source: [Bank of Russia participant record for ООО «Т-ИНВЕСТ ЛАБ»](https://www.cbr.ru/finorg/foinfo/?ogrn=1207700043198).

This is a meaningful domestic candidate because the owner already uses T-Bank personally. It does **not** establish:
- that the retail crypto service is publicly launched or available to this owner;
- that spot BTC/ETH/USDT can be traded through a public API;
- that the service exposes an order book, trades, depth, market-data history or streaming fills;
- that an API can submit/cancel/replace crypto orders;
- that the product is suitable for autonomous execution or high-frequency order-flow analysis.

The CBR registration is an operator qualification, not proof of a retail API or exchange-style order book. The statutory definition of an organization exchanging digital currencies includes systematic principal dealing off organized trading; it should not be treated as equivalent to a centralized limit-order-book venue.

### 3.2 T-Invest API and crypto-index “neoassets”

Official T-Invest API documentation describes:
- `Futures` / `FutureBy` instrument discovery;
- `api_trade_available_flag` to determine whether a specific instrument can be traded through the API;
- `for_qual_investor_flag` to identify instruments restricted to qualified investors;
- `GetInfo` to retrieve account information, qualified-investor status and types of instruments available after testing;
- order placement and order-state methods for supported exchange instruments.

Sources:
- [T-Invest API — instrument reference](https://developer.tbank.ru/invest/services/instruments/head-instruments)
- [T-Invest API — instrument FAQ and availability flags](https://developer.tbank.ru/invest/services/instruments/faq_instruments)
- [T-Invest API — trading robot examples and GetInfo](https://developer.tbank.ru/invest/intro/intro/cases)

A separate T-Invest FAQ says smart assets can be listed and portfolio/operations retrieved, but quotes, trading and positions for those smart assets are not supported by API. Do not confuse smart assets/DFA with exchange-traded crypto-index futures or neoassets; each instrument's actual API flags and product type must be inspected.

T-Invest's official T-Terminal communication states:
- SPB Exchange crypto-index neoassets include Bitcoin, Ethereum, Solana, Ripple and Tron references;
- quoted prices are USD-based while settlement is in RUB;
- these crypto-index neoassets are available **only to qualified investors**;
- they are derivatives, not ownership of the underlying crypto assets.

Source: [T-Terminal / T-Investments official product communication](https://www.tbank.ru/invest/social/profile/T-Terminal/).

**Disposition:** T-Invest is the highest-priority domestic API investigation, but its crypto product/API eligibility is UNQUALIFIED until actual instrument records and account flags are verified.

### 3.3 Moscow Exchange crypto-index futures

MOEX's official product material states that its crypto-index futures (including BTCUSDF, ETHUSDF, SOLUSDF, XRPUSDF and TRXUSDF perpetual-style daily contracts) are available only to qualified investors. Contracts are cash-settled in RUB while quoted using the relevant index value in USD.

Sources:
- [MOEX launch notice for perpetual crypto-index futures, 2026-09-16](https://www.moex.com/n104244)
- [MOEX crypto futures FAQ and eligibility](https://www.moex.com/fyuchersy-na-bitkoin-i-efir-vash-dostup-k-kripte-uzhe-sejchas)
- [MOEX perpetual futures product page](https://www.moex.com/ru/derivatives/perpetual-futures)

MOEX dated BTC index futures are also cash-settled. Example contract page: [BTC-12.26 / BTZ6](https://www.moex.com/ru/derivatives/futures-on-indices/btz6).

These are not spot BTC and not equivalent to USDT perpetuals on a global crypto exchange. Their RUB settlement, USD index quotation, contract multiplier, daily variation/settlement mechanics, fees, margin and trading schedule require a separate instrument model and venue-qualified financial formulas.

**Disposition:** DOMESTIC DERIVATIVE CANDIDATE / QUALIFIED-INVESTOR GATE / T-INVEST API CONFORMANCE REQUIRED.

### 3.4 SPB Exchange crypto-index neoassets

T-Invest's official communication says crypto-index neoassets are only for qualified investors. The public description reports USD-based quotation and RUB settlement, with a separate financing/rollover cost structure rather than assuming global exchange funding.

This is a distinct product from MOEX futures and from spot crypto. Exact underlying index, contract terms, rollover/financing formula, fees, market data depth, API trade flag, execution event model and trading hours remain to be qualified from official SPB and broker documentation.

**Disposition:** DOMESTIC DERIVATIVE CANDIDATE / QUALIFIED-INVESTOR GATE / API AND CONTRACT DETAILS BLOCKED.

## 4. Foreign venue screening — technical eligibility is not legal eligibility

| Venue / entity | Public-source finding as of 2026-11-14 | NEXUS disposition |
|---|---|---|
| Bybit Global | Global restricted-country material does not list the Russian Federation as a whole, but lists certain Russian-controlled territories; Bybit's KYC FAQ says territorial restrictions are tied to nationality. Bybit EU is a separate entity/product regime and lists Russia as restricted. General fiat service for Russian users is constrained to RUB; SWIFT USD/SEPA routes are unavailable. Public API supports granular trade permissions separate from withdrawal permissions. | TECHNICALLY PLAUSIBLE / ACCOUNT ENTITY AND KYC UNCONFIRMED / RUSSIAN-LAW REVIEW REQUIRED |
| OKX Global | Public risk disclosure specifically restricts certain fiat payment services for Russia; API agreement and terms require an eligible jurisdiction, verified account and product-specific compliance. No authoritative account-level confirmation of spot/derivatives API eligibility for this owner's RF residence has been obtained. | CONDITIONAL / NOT QUALIFIED |
| Kraken | Current global terms and eligibility materials explicitly restrict Russian Federation residents / relevant Russian jurisdiction. | REMOVE FROM RF V1 LIVE SHORTLIST |
| Coinbase | Public identity/residency materials require additional proof of residence for Russian nationals/residents applying in a supported jurisdiction. This does not establish eligibility for a person currently residing in the RF; no reliable positive confirmation has been obtained. | NOT QUALIFIED / LOW PRIORITY |
| Binance | Previous research on P2P and Russian account restrictions is not enough to establish current spot/derivatives API eligibility. A product-, entity- and account-specific official confirmation is missing. | NOT QUALIFIED |

Primary sources:
- [Bybit Global service-restricted countries](https://www.bybit.com/en/help-center/article/Service-Restricted-Countries)
- [Bybit individual KYC FAQ](https://www.bybit.com/ru-RU/help-center/article/Individual-KYC-FAQ)
- [Bybit EU service restrictions](https://www.bybit.eu/en-EU/help-center/article/Service-Restricted-Countries)
- [Bybit fiat-service country restrictions](https://www.bybit.com/en/help-center/article/List-of-Restricted-Issuing-Countries-for-Fiat-Service)
- [Bybit V5 API documentation](https://bybit-exchange.github.io/docs/v5/guide)
- [OKX risk and compliance disclosure](https://www.okx.com/en-us/help/risk-compliance-disclosure)
- [OKX API agreement](https://www.okx.com/help/api-agreement)
- [Kraken Global Terms](https://www.kraken.com/legal/global-terms)
- [Kraken Derivatives eligibility](https://support.kraken.com/articles/360023786632-kraken-derivatives-eligibility)
- [Coinbase proof-of-residency documents](https://help.coinbase.com/en/coinbase/managing-my-account/verify-my-identity/proof-of-residency-documents)

**Important:** absence of the Russian Federation from a public restricted-country list is not affirmative permission. Actual contracting entity, KYC nationality/residence, account opening date, product, sanctions screening, fiat rail and API permissions must all be confirmed by the venue. Never use VPN, false address, borrowed account or nominal foreign entity to defeat these checks.

## 5. Product and venue comparison

| Dimension | Global spot/perpetual venue | MOEX / SPB crypto-index derivatives | Domestic registered crypto-exchange organization |
|---|---|---|---|
| Underlying exposure | Actual digital currency or exchange-defined derivative | Crypto index reference; cash settlement in RUB | Actual digital currency in a regulated account/transaction model |
| Order book / DOM | Usually available, subject to venue API | Exchange order book exists; broker API depth and historical data need qualification | Not implied by registration; principal dealing may be off-order-book |
| API execution | Public APIs exist; owner eligibility unresolved | T-Invest API has generic futures methods; exact instrument flag/access unknown | No public crypto execution API confirmed |
| Qualified investor | Venue KYC and product rules | Current crypto-index futures/neoassets found are qualified-only | Non-qualified route may exist subject to testing, warnings, limits and admitted assets |
| Settlement | Often USDT/coin/other venue-defined | RUB, with USD-based index quotation for MOEX/SPB products | Product-specific; exact account and transfer rules required |
| Legal path for RF resident | Unresolved now; materially constrained by Article 30 from 2027-07-01 | Domestic regulated broker/exchange route, still product eligibility gated | Domestic CBR register route, product/API not yet proven |
| NEXUS v1 readiness | BLOCKED | BLOCKED pending qualification and API evidence | BLOCKED pending public product/API evidence |

No option currently satisfies all legal, product, account, API, market-data and execution-integrity gates.

## 6. Required NEXUS architecture control — Venue Eligibility Record

Before an adapter can enter LIVE-ELIGIBLE state, require an immutable, owner-approved `VenueEligibilityRecord` with at least:

- owner statutory residency status and evidence date (not citizenship alone);
- citizenship/nationality where the venue's KYC policy uses it;
- actual physical residence and account opening jurisdiction;
- venue legal entity and contracting terms version;
- venue region/product (Global/EU/other), exact instrument and settlement asset;
- product legal classification (spot digital currency, foreign digital instrument, exchange-traded derivative, other);
- applicable law and effective-date analysis, including Article 30/31/32 of 282-FZ;
- qualified-investor status, test completion and applicable limits;
- venue KYC outcome and written product/API eligibility confirmation;
- funding and withdrawal route, including custodial/non-custodial restrictions;
- API permission set, IP policy and explicit absence of withdrawal permission;
- market-data permissions, history/depth availability and redistribution constraints;
- legal review reference, reviewer, decision date, expiry/revalidation trigger.

Suggested adapter eligibility states:
- `RESEARCH_ONLY`
- `DATA_ONLY`
- `PAPER_ONLY`
- `LIVE_ELIGIBLE`
- `SUSPENDED`

Any missing, expired, contradictory or UNKNOWN mandatory evidence keeps the adapter out of LIVE-ELIGIBLE. This gate is not a substitute for Risk Engine and must not make automated legal interpretations from IP address or nationality alone.

## 7. Owner and external evidence still required

1. **Qualified-investor status:** obtain broker-confirmed status from T-Invest or the actual broker account. T-Invest API `GetInfo` can expose it; do not send access tokens to NEXUS source control or chat.
2. **T-Invest instrument discovery:** in the owner's authenticated account, query `GetFutures` and `FindInstrument` for official crypto-index/neoasset identifiers; record `api_trade_available_flag`, `for_qual_investor_flag`, `real_exchange`, `min_price_increment`, contract multiplier, settlement and margin metadata. No order should be submitted.
3. **T-Invest written confirmation:** ask whether the crypto-index neoassets are available through T-Invest API for this account, whether order book/trades/market depth/history are exposed, and whether order submit/cancel/replace and fill/account events are supported.
4. **T-Invest Lab written confirmation:** ask whether the regulated spot crypto service is live, which assets/account types are supported, whether a documented API exists, and whether actual order-book or quote-based principal dealing is offered.
5. **Legal opinion:** obtain product-specific advice on Articles 30, 31 and 32 of Law 282-FZ; Article 30(2) software-assistance scope; foreign venue access; self-use software; spot vs perpetual vs exchange-traded derivative classification; custody/withdrawal and funding.
6. **Foreign venue confirmation:** if a foreign venue remains under consideration, obtain written account-specific eligibility from the actual contracting entity for a Russian citizen/resident and the exact spot/derivative product/API.

No real API key, order, transfer, deposit or withdrawal is required for this qualification stage.

## 8. Immediate decisions and work sequence

| Item | Disposition |
|---|---|
| Select Bybit/OKX/Kraken/Coinbase/Binance | DEFERRED; no live selection |
| Treat Russian-regulated crypto-index futures as equivalent to global perps | REJECTED |
| Treat T-Invest Lab registration as proof of public crypto API | REJECTED |
| Enable MOEX/SPB crypto derivatives for a non-qualified owner | BLOCKED |
| Enable foreign live trading without legal review | BLOCKED |
| Build a venue eligibility record and adapter activation gate | RECOMMENDED DESIGN WORK |
| Continue venue-neutral data/analytics/reference-model work | ALLOWED |
| Continue paper/simulation work using clearly synthetic or lawfully sourced data | ALLOWED, subject to data licence |

### Next bounded work package: WP-VENUE-QUAL-001

1. Complete a T-Invest API capability and product-access assessment using official API contracts and the owner's account flags, without placing orders.
2. Compare MOEX dated BTC futures, MOEX perpetual crypto-index futures and SPB crypto-index neoassets as separate instrument types.
3. Determine whether the T-Invest Lab spot service has launched and whether it offers an API.
4. Draft NX-ADR-006 (Venue Eligibility & Jurisdictional Activation Gate) after this research is owner-reviewed.
5. Keep foreign venues research-only until counsel resolves the statutory path.

**Exit criteria:** a documented, evidence-backed candidate path with exact product, legal eligibility, account qualification, market-data/API support and instrument semantics. If none passes, record NO LIVE VENUE QUALIFIED and continue paper/research without forcing a selection.

## 9. Source update and maintenance

This report is the current jurisdiction/product eligibility baseline as of 2026-11-14. It supplements and supersedes earlier venue-shortlist conclusions where they conflict with Law No. 282-FZ or current official venue rules. Revalidate the CBR register, legislation, venue terms, API availability and broker product flags before any later decision; do not treat this snapshot as permanent.
