# NX-RESEARCH-005 — Russian Banking, Brokerage and Corporate-Structure Options

**Date:** 2026-11-14  
**Status:** PRELIMINARY — integration candidates identified; no bank, broker, company jurisdiction or legal structure selected  
**Scope:** Officially documented Russian bank APIs, domestic brokerage API evidence, and first-pass Russian tax/regulatory considerations for a Russian citizen residing in the Russian Federation. This is not legal, tax, sanctions or investment advice.  
**Related:** NX-RESEARCH-003, NX-RESEARCH-004, NX-ARCH-001, NX-OWNER-DECISIONS-001, ТЗ-NX-001, ТЗ-NX-004, ТЗ-NX-006.

## 1. Owner context and boundaries

The owner confirmed on 2026-11-14 that he is both a Russian citizen and currently resides in the Russian Federation. The owner asked NEXUS to consider domestic integrations, specifically Sberbank, Alfa-Bank and T-Bank, and asked whether the project could lawfully be structured through a foreign company.

This memo distinguishes four separate questions:
1. Bank-account data and treasury integration (balances, statements, transfers and payment status).
2. Brokerage integration for domestic exchange-traded instruments (quotes, orders, fills and positions).
3. Crypto-exchange access for the owner's own capital.
4. Corporate/IP structure for owning, developing, licensing or operating NEXUS.

No personal bank credentials, brokerage tokens, company registrations or account connections are authorized by this research.

## 2. Russian bank API evidence

### 2.1 Sberbank — Sber API / SberBusinessAPI / SberConnect

Official sources:
- Sber API overview: https://developers.sber.ru/docs/ru/sber-api/start/overview
- Statement API overview: https://developers.sber.ru/docs/ru/sber-api/specifications/statement/statement-overview
- Statement summary: https://developers.sber.ru/docs/ru/sber-api/specifications/statement/summary
- SberBusinessAPI documented capabilities: https://sberbusinessapi-documentation.github.io/
- SberConnect API: https://www.sberbank.ru/ru/legal/sberconnect_api

Observed facts:
- Sber API is positioned for companies and holdings to automate accounting and treasury processes. Available API sets and operations are fixed in the service agreement.
- Official statement methods include account statements, transaction details, daily summary, incremental statement retrieval and statement-file export.
- SberBusinessAPI documentation lists account discovery, account statements, RUB payment orders and foreign-currency payment orders, subject to product activation and contract.
- SberConnect describes payment instructions, payment-status retrieval, cancellation requests and account movement information in RUB and foreign currency.
- Sber's official developer documentation says API connection is arranged through the bank's business channel and a contractual setup process.

Interpretation:
- Sber is a strong candidate for a **business treasury/accounting connector**, subject to the owner's actual account type, bank approval, scopes, certificates and contract.
- Public evidence reviewed here does not establish a general consumer API for arbitrary personal retail accounts.
- Payment initiation must be a separately permissioned capability, not bundled with read-only statement access.

### 2.2 Alfa-Bank — Alfa API

Official sources:
- Alfa API business overview: https://alfabank.ru/sme/alfaapi/
- Developer portal: https://developers.alfabank.ru/
- Connection instructions: https://developers.alfabank.ru/products/alfa-api/documentation/articles/connection/connection

Observed facts:
- Alfa API documents account operations, statements, payment preparation, notifications/events and payment-status workflows for business use.
- Direct host-to-host integration is supported for the customer's own organization.
- B2B SaaS/partner integration may expose third-party company data only where the relevant company has consented to the bank's data transfer.
- The documented onboarding includes an information-technology interaction agreement and sandbox testing before production.
- The public product page describes statement and payment automation and bank-side integration controls.

Interpretation:
- Alfa is a strong candidate for a **business banking connector**, conditional on business account status, bank onboarding, contract and approved scopes.
- Public evidence reviewed does not establish a general personal-retail-account API or an API for autonomous trading through Alfa Investments.
- Alfa API access for a partner platform and access to the owner's own business account are different legal/technical integration modes.

### 2.3 T-Bank — T-API / T-Invest API

Official sources:
- T-API documentation: https://developer.tbank.ru/docs/api/t-api
- T-API business capabilities: https://developer.tbank.ru/tapi
- T-Invest API overview: https://www.tbank.ru/invest/open-api/
- T-Invest API start: https://developer.tbank.ru/invest/intro/intro
- T-Invest API FAQ: https://developer.tbank.ru/invest/intro/faq

Observed facts:
- T-API for business documents account statements, payment creation/status, invoices and other business workflows.
- T-Bank's official T-API onboarding documentation says direct business API use requires registration as an LLC or individual entrepreneur and access to T-Business; third-party customer data uses a partner integration.
- T-Invest API is a separate brokerage interface. It supports market and historical data, portfolio information, and submitting market, limit and stop orders; a sandbox is documented.
- T-Invest API onboarding requires a brokerage account and client identification.
- T-Invest API FAQ states it is provided to T-Invest clients without the right to redistribute data as a public service. Additional brokerage accounts are opened in the app, not through the API.
- T-Invest API is for exchange-traded instruments exposed by the broker; its existence does not establish cryptocurrency exchange or perpetual-swap access.

Interpretation:
- T-Bank offers two distinct candidate integrations:
  - **T-API:** business banking / treasury connector, subject to LLC/IP onboarding.
  - **T-Invest API:** potential domestic brokerage adapter for the owner's own brokerage account, subject to client eligibility, product availability, terms and data-use restrictions.
- The T-Invest API's non-redistribution condition is material: it may support the owner's private NEXUS terminal but must not be assumed to permit redistribution or a public multi-user data service.

## 3. Domestic brokerage scope

- T-Invest API has direct official evidence for algorithmic trading in supported exchange-traded instruments, including orders, quotes, historical data and sandbox.
- Sber's reviewed public sources confirm brokerage accounts and retail order workflows, but this research pass did not establish a supported public retail brokerage trading API suitable for NEXUS automation.
- Alfa's reviewed public sources confirm Alfa API for business banking and brokerage services, but this pass did not establish an official public retail brokerage execution API.
- Absence of evidence in this bounded pass is not proof that private, institutional, QUIK, partner or negotiated interfaces do not exist. Such interfaces require separate official confirmation.
- Domestic securities/futures trading is a different product family and regulatory/operational adapter from offshore crypto spot/perpetual trading. It should not be silently included in the v1 crypto execution venue count.

## 4. Russian crypto regulatory watch

Official source:
- Bank of Russia, “Regulation of cryptocurrency circulation in Russia”: https://www.cbr.ru/explan/cryptocurrency

Observed facts from the Bank of Russia's current FAQ as reviewed on 2026-11-14:
- The FAQ references Federal Law No. 282-FZ and explains that digital currencies and foreign digital instruments are distinct statutory categories; foreign stablecoins may fall into either category depending on issuance terms.
- The FAQ states that from 1 July 2027, Russian residents who are not persons organizing digital-currency circulation may conduct digital-currency transactions only through or with persons organizing such circulation, as defined by the law.
- The FAQ also describes restrictions taking effect from 1 September 2027 for certain non-qualified investors and digital-currency transfers, with instrument/admission conditions.
- These future dates mean the legal and venue landscape is changing; the law and implementing regulations must be rechecked before any live deployment and periodically thereafter.

Interpretation:
- NEXUS must not treat today's apparent technical access to a foreign exchange as a permanent legal permission.
- The product must maintain a versioned jurisdiction/regulatory capability register and block unsupported assumptions. Legal applicability to the owner's precise trading pattern requires qualified Russian legal advice.
- The legal treatment may differ by instrument classification, spot/perpetual/derivative structure, resident status, counterparty and transaction route.

## 5. Foreign-company option — first-pass assessment

A foreign company may be considered for legitimate purposes such as:
- owning software/IP and entering genuine software-development or licensing contracts;
- selling NEXUS as a software product in markets where the company is lawfully established and actually operates;
- contracting with vendors, employees or customers where the entity has real operational substance;
- holding a distinct business operation where banking, tax, accounting, governance and local law support it.

A foreign company must **not** be treated as a device that automatically changes the owner's personal exchange eligibility or removes Russian law, sanctions, tax reporting or beneficial-owner disclosure.

Relevant Russian tax sources:
- FNS, controlled foreign companies and controlling persons: https://www.nalog.gov.ru/rn77/taxation/cfcomp/conforcom/
- FNS, foreign company tax-residence rules and place of management: https://www.nalog.gov.ru/rn77/yul/interest/reg_yl/confirm_status/

Observed facts:
- FNS describes a CFC as a foreign organization not recognized as a Russian tax resident where a Russian tax-resident individual or organization is a controlling person.
- FNS describes participation thresholds including more than 25%, or more than 10% where the aggregate participation of Russian tax residents exceeds 50%, alongside a separate factual-control test.
- FNS states that a foreign organization whose place of management is in the Russian Federation may itself be treated as a Russian tax resident, subject to applicable treaty rules.
- The relevant analysis is not limited to the jurisdiction printed on the incorporation certificate; control, actual management, ownership, income rights and operating facts matter.

Preliminary implications:
- A company incorporated abroad but effectively owned and managed from Russia may trigger Russian CFC and/or corporate tax-residence questions.
- Incorporating abroad does not, by itself, establish access to a foreign exchange, foreign bank or a different exchange legal entity.
- Exchanges and banks may identify the ultimate beneficial owner, controllers, source of funds, actual residence, operating location and nature of business. Corporate KYC is not a substitute for personal eligibility.
- A foreign company may also create local substance, accounting, audit, reporting, tax, director, registered-office, banking and ongoing compliance costs.
- No jurisdiction can responsibly be recommended without comparing the actual business purpose, residence/tax position, ownership/control, banking access, venue eligibility, treaty position, sanctions exposure and operating substance.

## 6. NEXUS architecture implications

Proposed design direction — not yet an accepted architecture decision:

1. Add a **Bank & Treasury Integration** boundary separate from Crypto Exchange Execution.
2. Use explicit connector classes:
   - BankAccountReadConnector — balances, statements, transactions, account metadata.
   - BankPaymentConnector — payment preparation/submission/status, separately disabled and permissioned.
   - BrokerageMarketDataConnector — supported domestic exchange instruments and quotes.
   - BrokerageExecutionConnector — broker orders/fills/positions, separately certified.
3. Keep the canonical Ledger as the accounting authority; bank and broker connectors supply external evidence and reconciliation inputs, not direct mutable balances.
4. Preserve provenance, bank/broker transaction IDs, currencies, timestamps, statement periods, correction/reversal semantics and reconciliation status.
5. Separate personal-account access, business-account access and partner/B2B access. Never assume that one token or contract grants all three.
6. Apply least privilege: read-only scopes first; payment and trading permissions are separate, explicit capabilities with independent approval and audit.
7. Maintain a capability matrix per bank/broker, account type, legal entity, product, API scope, environment, data redistribution terms and supported recovery behavior.
8. Do not store bank credentials or brokerage tokens in the repository. Use isolated secret storage and explicit revocation procedures.

### Recommended scope sequencing

- **Phase 0 (now):** research/contract qualification only. No account connection or credential collection.
- **Read-only foundation:** one bank connector can be evaluated for statements and reconciliation, if an eligible account and approved API access exist.
- **Crypto v1:** retain the previously accepted one-crypto-venue / one-dedicated-account boundary. Domestic banks may be funding/treasury and accounting sources, not an implicit second crypto execution venue.
- **Later domestic markets track:** evaluate T-Invest API as a separate brokerage venue for Russian exchange instruments. Do not add it to v1 crypto scope without an explicit scope decision.
- **Payment initiation:** later, only after bank approval, transaction signing, payee controls, operator authorization and independent limits are designed.
- **Commercial NEXUS entity:** evaluate only after deciding whether NEXUS is private proprietary software, a product licensed to the owner, or a multi-user SaaS/platform.

## 7. Open qualification questions

### Banks / brokers
- Does the owner have personal accounts only, or also an LLC/IP and business settlement accounts?
- Which exact account type and API contract can each bank provide to this owner?
- Are statement APIs available for the owner's own personal accounts, or only business accounts/partner integrations?
- Does the bank permit use by a private personal terminal, a commercial SaaS, or both?
- For T-Invest API, which instrument classes, order types, account modes, market data rights, rate limits and sandbox features are available to the owner's account?
- Are official Sber/Alfa brokerage automation interfaces available under a direct customer agreement?

### Company / ownership
- Is the goal to own NEXUS IP, trade only the owner's capital, sell software subscriptions, or provide investment/trading services to third parties?
- Would the foreign entity have real management, personnel, operations and banking in its incorporation jurisdiction, or would all decisions and operations remain in Russia?
- What jurisdiction and tax-residence analysis is appropriate for the owner and any future entity?
- Which exchange/bank has confirmed in writing that the exact beneficial-owner, nationality, residence and business model are eligible?

## 8. Preliminary conclusion

- Sber API and Alfa API are documented candidates for business banking / treasury / statement integration, subject to contract and account-type qualification.
- T-API is a documented business banking candidate requiring LLC/IP onboarding; T-Invest API is the clearest currently evidenced domestic algorithmic brokerage API candidate, but only for supported exchange-traded instruments and subject to client terms and non-redistribution restrictions.
- This research pass does not establish public personal-retail account APIs for Sber/Alfa, nor a public Alfa/Sber retail brokerage execution API.
- A foreign company is a potentially legitimate business/IP structuring option, not an eligibility workaround. Russian CFC and place-of-management rules make superficial offshore incorporation particularly unsuitable as an assumption.
- No bank, broker, crypto venue, foreign jurisdiction or corporate structure is selected.
- No account, credential, payment, order, risk limit, live trading or production deployment is authorized.

**Conclusion:** Design NEXUS to support distinct bank, brokerage and crypto-exchange connectors, but qualify each against the exact account, API contract, legal entity, instrument and permitted use. Keep v1's accepted crypto scope intact while building a controlled domestic integration research track.
