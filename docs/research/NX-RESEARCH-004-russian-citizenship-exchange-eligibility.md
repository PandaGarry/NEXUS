# NX-RESEARCH-004 — Exchange Eligibility for Russian Citizens

**Date:** 2026-11-14  
**Status:** PRELIMINARY — no venue qualified or selected  
**Scope:** Publicly documented nationality, residence, territorial, fiat and product restrictions relevant to an individual Russian citizen; this is not a legal opinion or an account-specific eligibility determination.  
**Related:** NX-RESEARCH-003, NX-OWNER-DECISIONS-001 (OD-02, OD-03, OD-07), NX-ARCH-001, ТЗ-NX-004.

## 1. Owner context

The owner confirmed Russian citizenship on 2026-11-14 and indicated that Russia is the currently available operating/residence scenario, while lawful remote account opening in another territory would be a plus.

The owner's current tax residence, actual country of residence, any additional citizenship/residence permits, and sanctions status have not been confirmed. Do not infer them from IP or approximate location metadata.

## 2. Findings

### 2.1 Bybit

Official sources:
- Service Restricted Countries, last updated 2026-10-16: https://www.bybit.com/en/help-center/article/Service-Restricted-Countries
- Individual KYC FAQ, last updated 2026-08-20: https://www.bybit.com/ru-RU/help-center/article/Individual-KYC-FAQ/n
- Restricted issuing countries for fiat services, last updated 2026-07-27: https://www.bybit.com/en/help-center/article/List-of-Restricted-Issuing-Countries-for-Fiat-Service/

Observed facts:
- Bybit's current general excluded-jurisdiction list does not name the Russian Federation as a whole. It does name specified Ukrainian territories, including Crimea/Sevastopol and non-government-controlled areas of Donetsk, Luhansk, Kherson and Zaporizhzhia.
- The same restricted-country notice says users must notify Bybit if they become resident in an excluded jurisdiction and warns that false representations about location/residence may lead to account termination and liquidation of open positions.
- Bybit's Individual KYC FAQ explicitly states that territorial restrictions are determined based on the user's nationality, not current place of residence.
- The KYC FAQ says identity documents must be issued by the country of citizenship and proof of address is a separate requirement for Advanced KYC.
- Bybit's fiat-service restriction table lists the Russian Federation for general fiat services with a qualification that Russian users can only make RUB transactions. It separately lists Russia among restricted countries for USD SWIFT and other fiat rails.

Interpretation:
- The absence of the Russian Federation from the general excluded-jurisdiction list is not sufficient to establish that a Russian citizen is eligible for all Bybit services.
- The nationality-based KYC statement makes nationality a controlling qualification variable. The public material retrieved does not unambiguously resolve the exact eligibility of a Russian citizen for the relevant account entity, spot, derivatives and API trading.
- Fiat access is separately constrained; it must not be conflated with crypto deposits/withdrawals or derivatives eligibility.
- Bybit remains **UNQUALIFIED / CONDITIONAL**, not a selected venue, until Bybit Support provides written account-specific clarification and all applicable terms are checked.

Required written questions to Bybit:
1. Can an individual with Russian citizenship complete Standard and Advanced KYC using a valid Russian passport and genuine proof of current residence in the Russian Federation?
2. If yes, which legal entity and terms govern that account?
3. Are spot, USDT perpetuals, inverse contracts, margin and API trading available to that verified customer?
4. Are there additional restrictions based on sanctions screening, beneficial ownership, source of funds, banks, counterparties or payment rails?
5. Are crypto deposits and withdrawals available independently of restricted fiat rails?
6. Can the customer maintain and use the account while physically residing in Russia, and what events require re-verification or service termination?

### 2.2 OKX

Official sources:
- Risk & Compliance Disclosure, last updated 2026-11-14: https://www.okx.com/help/risk-compliance-disclosure
- API documentation: https://www.okx.com/docs-v5

Observed facts:
- OKX's current disclosure lists a set of Restricted Locations, but the Russian Federation is not in that list.
- The same disclosure says OKX may restrict services in Russia specifically regarding fiat payment services.
- The disclosure separately lists product-specific regional restrictions for other jurisdictions, demonstrating that geographic availability can vary by product.
- OKX API documentation describes REST and WebSocket interfaces, API key permission separation (Read, Trade, Withdraw), and IP binding recommendations.

Interpretation:
- The disclosure supports only a limited statement: Russia is specifically identified for possible fiat-service restrictions; it does not establish a blanket prohibition on all OKX services for Russian citizens or residents.
- The retrieved public disclosure does not settle nationality-based KYC eligibility, derivatives access, legal entity, crypto deposit/withdrawal access, or account continuity for a Russian citizen residing in Russia.
- OKX remains **UNQUALIFIED / CONDITIONAL** pending written support confirmation and product-specific terms review.

Required written questions to OKX:
1. Can a Russian citizen whose genuine current residence is in Russia complete individual KYC?
2. Which OKX legal entity and terms would govern that account?
3. Are spot, margin, perpetual swaps/futures and API trading available to that customer?
4. Are crypto deposits and withdrawals available, and which fiat rails are restricted?
5. Do any restrictions depend on nationality, residence, source of funds, bank, sanctions screening or counterparty?
6. What happens if the customer later relocates to another country and provides genuine new proof of residence?

## 3. Remote account opening in another jurisdiction

A foreign account is a viable alternative only where the owner genuinely qualifies under the destination jurisdiction's law and the venue's terms.

Acceptable evidence may include a real residence permit/status and genuine proof of residential address, where accepted by the venue. A company, nominee, borrowed address, false residence declaration, VPN/geolocation masking or third-party KYC must not be used to simulate eligibility.

A change of residence does not automatically remove nationality-based restrictions or sanctions obligations. Before relying on a foreign venue entity, confirm the customer's eligibility in writing with that entity and review local law, tax reporting, funding rails and withdrawal access.

## 4. Preliminary comparison

| Venue | Russian citizen residing in Russia | Fiat | API | Current disposition |
|---|---|---|---|---|
| Bybit | Public KYC policy makes nationality a controlling factor; exact Russian-citizen eligibility unresolved | General fiat list limits Russian users to RUB; USD SWIFT restricted | Documented API exists; eligibility for this customer unresolved | UNQUALIFIED / CONDITIONAL |
| OKX | Public disclosure does not establish a blanket platform ban, but individual KYC eligibility remains unresolved | Russia specifically restricted for fiat services | Documented REST/WebSocket API exists; eligibility for this customer unresolved | UNQUALIFIED / CONDITIONAL |

## 5. NEXUS decision and implementation impact

- No exchange is selected by this research.
- OD-03 remains OPEN.
- Do not hard-code Bybit or OKX as the v1 venue.
- Keep the exchange adapter and instrument capability model venue-neutral.
- Do not create live credentials or connect an account during Phase 0.
- Venue qualification requires written support evidence for the exact nationality/residence combination, product family, API permissions, deposit/withdrawal route, legal entity and account mode.
- A venue that allows registration but does not confirm durable account servicing is not qualified for autonomous execution.

## 6. Evidence limitations

This memo summarizes public official material available on 2026-11-14. It does not constitute legal advice, a sanctions-screening result, a KYC pre-approval, or a guarantee of future service. Exchange policies and regional entities may change. Public API documentation proves interface documentation exists, not that a particular customer is eligible to use it.

**Conclusion:** Bybit and OKX remain research candidates only. Neither is qualified for NEXUS v1 until the exact Russian-citizen / genuine-residence scenario is confirmed in writing and product-specific capabilities are verified.
