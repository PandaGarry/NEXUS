# NX-RESEARCH-009 — Russia Jurisdiction, Product Classification & First-Venue Eligibility

**Status:** RESEARCH ONLY / LEGAL REVIEW REQUIRED / NO VENUE SELECTED  
**As-of date:** 2026-11-14

This report assesses the Russian regulatory environment, domestic exchange candidates and foreign venue eligibility for NEXUS. It is an engineering research record, not legal, tax, sanctions or investment advice. It does not authorize trading.

## Executive disposition

Do not select a foreign venue or enable live trading yet. This report evaluates an RF-resident natural-person scenario. Statutory residency, nationality/KYC, account-specific eligibility, broker qualification and product eligibility are separate variables that must be evidenced independently. No personal identifiers, account details or address information are recorded in this public research artifact.

Three lanes remain distinct:

1. **Domestic exchange-traded crypto-index derivatives (MOEX / SPB through a broker):** real products exist, but the MOEX crypto-index futures and T-Invest/SPB crypto-index neoassets found are qualified-investor-only. They are cash-settled RUB products, not spot crypto and not equivalent to global USDT perpetuals.
2. **Domestic spot digital currency through a CBR-regulated intermediary:** ООО «Т-ИНВЕСТ ЛАБ» has an active CBR record and the right to operate as an organization exchanging digital currencies from 2026-10-06, in addition to broker and depository permissions. This does not establish a launched public service, order book or public crypto API.
3. **Foreign centralized venues:** Bybit Global and OKX Global remain technical research candidates only. Exact contracting entity, KYC, Russian-law eligibility, product classification, sanctions screening and future Article 30 restrictions are unresolved. Kraken is removed from the RF v1 shortlist; Coinbase eligibility for a current RF resident is not established.

No option currently passes every legal, account, product, API, market-data and execution-integrity gate.

## 1. Federal Law No. 282-FZ

Primary sources:
- [Official publication of Federal Law No. 282-FZ, 2026-08-04](https://publication.pravo.gov.ru/document/0001202608040007)
- [Bank of Russia Directive No. 7441-U, official PDF](https://www.cbr.ru/Queries/UniDbQuery/File/90134/8618)
- [Bank of Russia cryptocurrency regulation FAQ](https://www.cbr.ru/explan/cryptocurrency/)
- [Bank of Russia crypto-market launch and participant registers](https://www.cbr.ru/develop/cryptocurrency/)

Key provisions:
- The law generally entered into force on **2026-09-01**.
- Part 1 of Article 30 enters into force on **2027-07-01**.
- Once effective, Article 30(1) requires residents who are not persons organizing digital-currency circulation to transact only through or with persons organizing such circulation, subject to enumerated exceptions.
- Bank of Russia FAQ answer 9 (updated 2026-10-12) says that from 2027-07-01 residents may transact only through Chapter 4 participants, including a licensed broker or a crypto-exchange organization included in the Bank of Russia register.
- FAQ answer 10 says direct P2P transactions between individuals are not included in the permitted list from 2027-07-01.
- Article 30(2), already effective under the general commencement rule, prohibits assisting residents in transactions that violate the law, including providing software for such transactions. Its application to privately developed, owner-operated software and to specific foreign-venue products is unresolved and requires a qualified legal opinion. NEXUS must not assume that personal use creates an exemption.

Article 31 establishes conditions for residents acquiring digital currency through brokers and other named intermediaries:
- non-qualified residents: positive test, risk warning, annual limit and eligible instruments admitted to public organized trading;
- qualified residents: the applicable test and risk warning still apply;
- the corresponding rules also apply to crypto-exchange organizations in the cases specified by the law.
The Bank of Russia's Directive No. 7441-U (2026-09-11) was registered on 2026-10-30 and officially published on 2026-11-06. Clause 9 makes it effective 10 days after publication, i.e. **2026-11-17** (subject to no amendment or later official clarification).
- Clause 2 sets the annual acquisition-value limit for a non-qualified resident buying digital currencies through a broker at **RUB 300,000 per calendar year**. Clause 1 defines the total as the ruble sum of acquisition values through that broker during the calendar year, not merely the current open-position value. Repeated buy/re-entry activity can therefore consume the limit even when earlier positions have been sold.
- Clauses 3 and 8 include BTC, ETH and USDT (USDT as a foreign digital instrument) in the list that an organizer of trading may admit to public organized trading, subject to the stated criteria. This is permission to admit eligible assets, not proof that a particular exchange has already launched an instrument or API.
- Article 31(3) applies corresponding conditions to crypto-exchange organizations in specified cases. Do not assume without legal review that the broker-specific RUB 300,000 calculation applies identically to every principal-dealing crypto-exchange model.

Bank of Russia FAQ answer 14 (updated 2026-10-26) describes when a pre-existing qualified-investor recognition carries over to digital-currency transactions. The owner's status must be confirmed by the actual broker; it must not be inferred from account balances or this report.

### Stablecoins and wallet transfers

- Bank of Russia FAQ answers 3–4 state that USDT may be classified as a foreign digital instrument depending on issuance conditions, and that the same Federal Law No. 282-FZ requirements apply to foreign stablecoins.
- FAQ answer 11 states that a natural person may not transfer digital currency from a digital account to their own non-custodial wallet under Article 31(9). Article 31 has limited exceptions and additional conditions; there is no generic assumption of unrestricted self-custody withdrawals.
- No wallet, custody, transfer or withdrawal feature is authorized by this research.

**Product classification must be explicit:** spot BTC/ETH, USDT, a crypto-index future, a USDT-settled perpetual, and another foreign digital instrument are not automatically the same legal product. Obtain product-specific legal classification; do not infer that cash settlement automatically excludes a derivative from Law No. 282-FZ.

## 2. Domestic regulated candidates

### 2.1 ООО «Т-ИНВЕСТ ЛАБ»

The [Bank of Russia participant record](https://www.cbr.ru/finorg/foinfo/?ogrn=1207700043198) shows an active status and the right to operate as an organization exchanging digital currencies from 2026-10-06. It also lists:
- brokerage license 045-14134-100000 from 2022-05-20;
- depository license 045-14135-000100 from 2022-05-20;
- dealer license 045-14087-010000 from 2020-06-17.

This is a high-priority domestic investigation for the T-Bank route. It does not prove the crypto service is publicly available, that spot trading has a public API, or that the service exposes order book, depth, trades, streaming fills, order placement/cancellation or history.

**Additional due-diligence note:** the [CBR decisions record for T-Invest Lab](https://www.cbr.ru/finorg/foinfo/rbr/?inn=007743330386) lists orders dated 2026-09-28 and 2026-10-06 requiring suspension of order placement and trades on organized trading on behalf of certain individual clients under Federal Law No. 224-FZ. The published record describes client-specific measures; it is not an operator-wide suspension and does not state that the crypto-exchange activity right was withdrawn. This is not a disqualification finding, but the broker's compliance controls, scope of those measures and current status should be included in due diligence.

The statutory definition of an organization exchanging digital currencies includes principal dealing in its own name and account outside organized trading; CBR registration must not be mistaken for an exchange-style limit order book.

### 2.2 T-Invest API and crypto-index neoassets

Official T-Invest API docs:
- [Instrument reference](https://developer.tbank.ru/invest/services/instruments/head-instruments)
- [Instrument FAQ and API availability flags](https://developer.tbank.ru/invest/services/instruments/faq_instruments)
- [Trading robot examples / GetInfo](https://developer.tbank.ru/invest/intro/intro/cases)

The API documents:
- `Futures` / `FutureBy` instrument discovery;
- `api_trade_available_flag` for API trade availability;
- `for_qual_investor_flag` for qualified-investor restrictions;
- `GetInfo` for qualified-investor status and post-test instrument access;
- order placement and order-state methods for supported exchange instruments.

A separate T-Invest FAQ says smart assets/DFA can be listed and portfolio/operations retrieved, but quotes, trading and positions for those smart assets are not supported through the API. Do not conflate smart assets/DFA with SPB crypto-index futures/neoassets.

T-Invest's official [T-Terminal communication](https://www.tbank.ru/invest/social/profile/T-Terminal/) says crypto-index neoassets reference Bitcoin, Ethereum, Solana, Ripple and Tron, are quoted in USD and settled in RUB, and are available only to qualified investors. They are derivatives, not ownership of underlying crypto assets.

**Disposition:** highest-priority domestic API investigation, but exact crypto instrument access and market-data/execution support remain UNQUALIFIED until authenticated account flags and official product/API evidence are checked. No order is needed for this check.

### 2.3 Moscow Exchange crypto-index futures

MOEX official sources:
- [Perpetual crypto-index futures launch notice, 2026-09-16](https://www.moex.com/n104244)
- [Crypto futures FAQ and eligibility](https://www.moex.com/fyuchersy-na-bitkoin-i-efir-vash-dostup-k-kripte-uzhe-sejchas)
- [Perpetual futures page](https://www.moex.com/ru/derivatives/perpetual-futures)
- [BTC-12.26 contract](https://www.moex.com/ru/derivatives/futures-on-indices/btz6)

MOEX states that crypto-index futures (BTCUSDF, ETHUSDF, SOLUSDF, XRPUSDF and TRXUSDF) are available only to qualified investors. Contracts are quoted using USD index values and settled in RUB. Dated BTC index futures are also cash-settled.

These instruments require their own contract, index, RUB settlement, margin, clearing, fee, financing and trading-hours models. They are not spot BTC and not equivalent to a global USDT perpetual.

**Disposition:** domestic derivative candidate / qualified-investor gate / T-Invest API conformance required.

### 2.4 SPB Exchange crypto-index neoassets

T-Invest's official communication says crypto-index neoassets are only for qualified investors. They use USD-based quotations and RUB settlement, with a financing/rollover structure distinct from global perpetual funding. Exact contract, underlying index, market depth, history, fees, rollover and API trade flags remain to be qualified from SPB and broker documentation.

**Disposition:** domestic derivative candidate / qualified-investor gate / API and contract details blocked.

## 3. Foreign venue screening

| Venue / entity | Public-source finding as of 2026-11-14 | Disposition |
|---|---|---|
| Bybit Global | Its 2026-10-16 global restricted-country page does not list the Russian Federation as a whole, but includes certain Russian-controlled territories in Ukraine. Its KYC FAQ says territorial restrictions are based on nationality. Bybit EU is separate and explicitly excludes Russian nationals. General fiat service allows Russian users only RUB transactions; SEPA and USD SWIFT rails list Russia as restricted. | TECHNICALLY PLAUSIBLE / ACCOUNT ENTITY AND KYC UNCONFIRMED / RUSSIAN-LAW REVIEW REQUIRED |
| OKX Global | Its disclosure (last updated 2026-11-14) specifically lists Russia for fiat-payment-service restrictions, not as a blanket restricted location. Its API agreement requires a verified account and eligibility under applicable terms; product access is jurisdiction-specific. API/data use is limited to own internal purposes absent written authorization; market-data redistribution/commercialization is restricted. | CONDITIONAL / NOT QUALIFIED |
| Kraken | Its global Terms (last updated 2026-11-06) explicitly prohibit use by persons located in, controlled from or resident in Russia. | REMOVE FROM RF V1 LIVE SHORTLIST |
| Coinbase | Coinbase requires additional proof of residence for Russian nationals and/or people resident in Russia applying in another jurisdiction. This does not establish eligibility for someone currently resident in the RF. | NOT QUALIFIED / LOW PRIORITY |
| Binance | Prior P2P research is not enough to establish current spot/derivatives API eligibility for the owner's exact account and product. | NOT QUALIFIED |

Primary sources:
- [Bybit Global service restrictions](https://www.bybit.com/en/help-center/article/Service-Restricted-Countries)
- [Bybit individual KYC FAQ](https://www.bybit.com/ru-RU/help-center/article/Individual-KYC-FAQ/n)
- [Bybit EU service restrictions](https://www.bybit.eu/en-EU/help-center/article/Service-Restricted-Countries)
- [Bybit fiat-service restrictions](https://www.bybit.com/en/help-center/article/List-of-Restricted-Issuing-Countries-for-Fiat-Service)
- [Bybit V5 API](https://bybit-exchange.github.io/docs/v5/guide)
- [OKX risk/compliance disclosure](https://www.okx.com/en-us/help/risk-compliance-disclosure)
- [OKX API agreement](https://www.okx.com/help/okx-api-agreement)
- [OKX API documentation](https://www.okx.com/docs-v5/en/)
- [Kraken Global Terms](https://www.kraken.com/legal/global-terms)
- [Coinbase proof-of-residency requirements](https://help.coinbase.com/en/coinbase/managing-my-account/verify-my-identity/proof-of-residency-documents)

Absence from a public restricted-country list is not affirmative permission. Actual entity, KYC, product, sanctions screening, funding rails, withdrawal route and API permissions must be confirmed. VPN, false address, borrowed accounts or nominal foreign companies are not acceptable workarounds.

## 4. Required architecture control — Venue Eligibility Record

Before an adapter can enter `LIVE_ELIGIBLE`, require an immutable owner-approved `VenueEligibilityRecord` containing:
- statutory residency evidence and date (not citizenship alone);
- nationality where venue KYC uses it;
- physical residence and account opening jurisdiction;
- venue legal entity, region and terms version;
- exact product/instrument and settlement asset;
- legal classification: spot digital currency, foreign digital instrument, exchange-traded derivative or other;
- applicable Articles 30–32 and effective-date analysis;
- qualified-investor status, test completion and limits;
- venue KYC and written product/API eligibility confirmation;
- funding and withdrawal route, including custody restrictions;
- API permission set, IP policy and explicit absence of withdrawal permission;
- market-data permissions, depth/history and redistribution constraints;
- legal review reference, reviewer, decision date, expiry and revalidation trigger.

Suggested adapter states: `RESEARCH_ONLY`, `DATA_ONLY`, `PAPER_ONLY`, `LIVE_ELIGIBLE`, `SUSPENDED`. Missing, expired, contradictory or UNKNOWN mandatory evidence blocks live activation. This gate is separate from the Risk Engine and must not infer legal eligibility from IP address or nationality alone.

## 5. Required evidence and next work package

1. Confirm the owner's qualified-investor status directly with the actual broker. T-Invest `GetInfo` can expose it; no access token is to be sent in chat or committed to Git. If non-qualified, evaluate the RUB 300,000 annual cumulative acquisition cap from 2026-11-17 and whether it makes the intended autonomous turnover viable.
2. In the owner's authenticated T-Invest account, inspect `GetFutures` / `FindInstrument` for exact crypto-index/neoasset identifiers and record `api_trade_available_flag`, `for_qual_investor_flag`, `real_exchange`, tick, multiplier, settlement and margin fields. No order submission.
3. Obtain written T-Invest confirmation of API order, cancel/replace, order book, trades, depth, history and private fill/account-event support for these exact instruments.
4. Obtain written T-Invest Lab confirmation whether its spot service is live, supported assets/account types, public API availability and quote-based versus order-book execution.
5. Obtain a product-specific legal opinion on Articles 30–32, Article 30(2) software-assistance scope, foreign venue use, spot/perpetual/derivative classification, custody and funding.
6. If a foreign venue remains under consideration, obtain account-specific written confirmation from the actual contracting entity for a Russian citizen/resident and the exact product/API.

No real key, order, transfer, deposit or withdrawal is needed for this qualification stage.

## 6. Architecture follow-up

**NX-ADR-007 — Venue Eligibility & Jurisdictional Activation Gate** has been drafted as a PROPOSED architecture decision. **NX-REF-VENUE-001** adds a test-only deterministic evidence evaluator and 24 fail-closed conformance tests for scope, freshness, expiry, approval revision and suspended/revoked states. It does not interpret law or grant authorization. NX-ADR-006 remains reserved for the previously deferred strategy-validation/research-governance topic. Owner/legal acceptance and exact-head CI evidence remain open.

## 7. Disposition

- No venue selected.
- No API key connected.
- No live order, transfer, deposit or withdrawal.
- Domestic MOEX/SPB crypto-index derivatives blocked pending qualified-investor status and API evidence.
- T-Invest Lab spot/API route unqualified.
- Foreign venues research-only pending legal and account-specific eligibility.
- Venue-neutral data, analytics, simulation and reference-model work may continue.

This is the active jurisdiction/product eligibility baseline as of 2026-11-14. Revalidate laws, CBR registers, venue terms, product availability and API permissions before any later decision.
