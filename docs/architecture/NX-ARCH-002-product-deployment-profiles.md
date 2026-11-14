# NX-ARCH-002 — Product & Deployment Profiles

**Status:** PROPOSED — owner review required  
**Version:** 0.1  
**Date:** 2026-11-14  
**Scope:** product-use profiles and deployment-stage boundaries for NEXUS. This document complements NX-ARCH-001; it does not change exchange eligibility, legal permissions, owner risk decisions or readiness gates.

## 1. Product direction

NEXUS v1 is developed first as a **closed personal-use product for one owner**. It is not initially a public exchange, broker, managed-account service, SaaS offering or multi-user commercial platform.

The first product objective is to build, verify and operate a professional personal trading and financial workstation. Commercial distribution, third-party accounts, customer onboarding, custody for others, public market-data redistribution and paid services are outside the initial scope.

This product scope does not create an exemption from applicable law, sanctions, KYC, exchange terms, API terms, banking agreements, data licenses or reporting obligations. A private deployment must use only accounts, products and API permissions for which the owner is eligible.

## 2. Profile model

Profiles describe intended deployment/use and permitted capabilities. They are not legal entities, exchange account types, or automatic authorization to trade.

| Profile | Purpose | Allowed baseline | Explicitly not granted |
|---|---|---|---|
| `PERSONAL_DEV` | Local engineering and research | Source work, unit tests, synthetic fixtures, offline replay | Live credentials, external order dispatch, production data writes |
| `PERSONAL_TEST` | Controlled verification | Historical data, public market feeds, read-only account integration where expressly permitted, paper, sandbox, fault injection | Real order placement, withdrawals, production capital |
| `PERSONAL_PRODUCTION` | Private single-owner operation after all gates | Owner-authorized account connectivity and autonomous operation within separately approved limits; monitoring, backup and recovery | Third-party users, customer funds, public service, unrestricted AI or signer authority |
| `COMMERCIAL` | Future separately approved product/business operation | Only capabilities explicitly approved after legal, licensing, security, operational and business review | Any inherited personal permission, account, credential or risk approval |

A deployment has exactly one active profile. Profile changes are explicit, versioned, audited and require a controlled deployment/review process. Downgrading a profile must revoke capabilities no longer permitted.

## 3. Personal-use scope and boundaries

### Included in the initial product

- One owner and one personal account context for the first release.
- Desktop and Web clients backed by one authoritative backend and state.
- Server-side market-data collection, analytics, strategy research and autonomous runtime.
- Personal bank/broker connectors only through officially supported and permitted access paths.
- Private portfolio and ledger views combining supported personal financial sources without conflating their legal or accounting semantics.
- Private operational monitoring and owner-only controls.

### Excluded from the initial product

- Public signup, multi-tenant customer isolation and third-party account onboarding.
- Managing or trading capital belonging to other people.
- Investment advice, brokerage, exchange, custody or asset-management services for others.
- Public redistribution of exchange/broker market data without explicit rights.
- Public APIs, paid subscriptions, customer SLAs and commercial support.
- Company formation solely as a presumed workaround for personal eligibility restrictions.

A future commercial profile requires a separate product and legal architecture review; it is not a toggle that makes the personal deployment public.

## 4. Capability gates are independent of profiles

A profile never bypasses the existing readiness gates.

- `PERSONAL_DEV`: development only; no live secrets or order dispatch.
- `PERSONAL_TEST`: read-only/paper/sandbox capabilities only after G1/G2 requirements and owner approvals are satisfied.
- `PERSONAL_PRODUCTION`: considered only after all applicable architecture, security, venue eligibility, account, reconciliation, recovery, operational and owner authorization gates are satisfied. Live trading remains a separate explicit authorization; the profile itself does not enable it.
- `COMMERCIAL`: requires a new legal/entity/jurisdiction, licensing, data-rights, security, privacy, customer-funds, operational-resilience and support assessment.

The following controls remain invariant in every profile:
- No withdrawal permission for exchange API credentials.
- No AI access to raw secrets, signer keys or direct private order dispatch.
- Every risk-increasing command requires current, payload-bound Risk Engine approval.
- Unknown, stale, incomplete or unreconciled state blocks risk-increasing activity.
- No blind retry after an ambiguous venue outcome.
- No production/live activation, risk-limit change or account connection without the required explicit owner authorization.

## 5. Legal and account eligibility boundary

Personal use is a product-scope decision, not a legal conclusion. Before connecting any venue, bank or broker, qualify the exact combination of:
- owner citizenship and actual residence;
- provider legal entity and applicable terms;
- account type and KYC status;
- product family and market type;
- API permission scope and automation rules;
- deposit/withdrawal and settlement rails;
- market-data license and redistribution conditions.

Foreign incorporation, a foreign hosting region, VPN use or a different UI profile must not be treated as changing the owner's actual citizenship/residence or satisfying provider eligibility. No false address, nominee, borrowed identity, third-party KYC or account-sharing workaround is permitted.

A future foreign company may be evaluated for legitimate IP ownership, contracting, hiring or international commercial activity. It does not automatically cure personal account restrictions or remove Russian tax, CFC, place-of-effective-management, reporting or sanctions questions. No jurisdiction or company structure is selected here.

## 6. Architecture consequences

- Keep the core domain model single-owner for v1; do not prematurely introduce tenant billing or customer administration.
- Retain strong internal identity, authorization, audit and secret isolation even for a single owner.
- Keep connectors capability-based and provider-neutral. A bank connector, domestic brokerage connector and crypto exchange connector remain separate boundaries.
- Separate read-only, paper, sandbox and live permissions at the adapter and credential layers; do not rely on UI hiding.
- Keep production deployment server-authoritative and independent of Desktop/Web client availability.
- Preserve data portability and clean separation of personal account data from any future commercial tenant/customer data.
- Do not select a hosting provider, country, legal entity or commercial jurisdiction in this document.

## 7. Transition criteria

### Personal development → personal test
- Architecture and contract gates authorize the relevant read-only/paper scope.
- Test fixtures, provenance, deterministic replay and failure scenarios are defined.
- Credentials, if any, are scoped to read-only and stored outside source control.
- No path from test runtime to live dispatch exists.

### Personal test → personal production consideration
- Venue/account eligibility is confirmed for the exact owner profile and product.
- Adapter capability and private-stream semantics are certified against evidence.
- Risk, execution, ledger, reconciliation, freshness, recovery and emergency-operation contracts pass their required conformance tests.
- Security review, secret isolation, backup/restore and incident runbooks are verified.
- Numeric risk policy and emergency authority are explicitly approved by the owner.
- A separate explicit live authorization is recorded. Without it, live remains disabled.

### Personal → commercial consideration
- A separate business case and jurisdiction comparison exists.
- Legal/tax advice and written provider eligibility are obtained for the proposed entity and beneficial owner.
- Data, software and upstream licenses permit the proposed distribution and service model.
- Multi-tenant isolation, privacy, security, customer support, incident response, availability and operational-resilience requirements are designed and tested.
- Commercial readiness is independently reviewed; personal production approval does not carry over.

## 8. Acceptance criteria for this profile proposal

- [ ] Owner confirms the single-owner personal-first product direction.
- [ ] NX-ARCH-001 links to this profile model without changing existing accepted v1 safety decisions.
- [ ] Roadmap distinguishes personal development, personal test, personal production consideration and future commercial assessment.
- [ ] No profile is treated as exchange/legal eligibility or live-trading authorization.
- [ ] Existing G0–G3 readiness gates and owner-controlled decisions remain intact.
- [ ] No company, country, venue, hosting provider or numeric risk limit is selected by implication.

## 9. Verification and limitations

This is a documentation proposal only. No runtime profile enforcement, feature flags, IAM policy, credential policy, account connection, exchange adapter, company formation or deployment change is implemented. No tests, security assessment or legal/tax opinion are claimed.

**Current project status remains: Prototype Readiness BLOCKED.**
