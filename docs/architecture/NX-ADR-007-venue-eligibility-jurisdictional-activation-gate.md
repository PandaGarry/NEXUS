# NX-ADR-007 — Venue Eligibility & Jurisdictional Activation Gate

**Status:** PROPOSED / NOT OWNER-ACCEPTED / NOT IMPLEMENTED  
**Date:** 2026-11-14  
**Related research:** [NX-RESEARCH-009 — Russia Jurisdiction, Product Classification & First-Venue Eligibility](../research/NX-RESEARCH-009-russia-jurisdiction-product-and-venue-eligibility.md)  
**Related contracts:** NX-IF-001..005, NX-SEC-001, NX-ADR-002, NX-ADR-004  
**Decision scope:** Eligibility to access a specific venue entity, account, product and instrument through NEXUS. This is separate from strategy approval, order risk approval and exchange API authentication.

## 1. Context

NEXUS is a private, owner-operated trading system. Its v1 venue has not been selected. Public API availability is not proof that a particular person may legally open or operate an account, access a product, use an API, fund the account or withdraw assets.

Eligibility depends on several independent and changeable dimensions:
- statutory residency and applicable law;
- nationality where venue KYC rules use it;
- physical residence and account-opening jurisdiction;
- exact venue legal entity and regional product;
- exact product/instrument and settlement asset;
- qualified-investor status, testing and account limits;
- KYC/AML/sanctions outcome;
- funding, custody and withdrawal restrictions;
- API permissions and market-data licence;
- effective dates of laws, regulations and venue terms.

NX-RESEARCH-009 documents the current Russian-law and venue-specific evidence. It identifies unresolved interpretation questions, including Article 30(2) of Federal Law No. 282-FZ, the 2027-07-01 Article 30(1) transition, stablecoin/derivative classification and the difference between domestic exchange-traded derivatives and global crypto perpetuals.

Without a dedicated gate, these facts tend to be scattered across configuration, connector code and operator assumptions. That creates a risk that a technically working adapter is treated as live-eligible without complete legal, account and product evidence.

## 2. Decision

Introduce a separate **Venue Eligibility Gate (VEG)** and a versioned, immutable **VenueEligibilityRecord**.

The gate is a prerequisite for enabling a venue adapter in a specific mode. It does not replace:
- Risk Engine authorization;
- Execution Engine command integrity;
- exchange-side KYC/account controls;
- security/credential controls;
- market-data licence checks;
- legal advice or a regulator's decision.

No adapter may enter `LIVE_ELIGIBLE` solely because an API endpoint works, a public country list omits a jurisdiction, a key can be created, or a user can log in.

The initial default for every venue/product/account is `RESEARCH_ONLY`. Unknown, missing, expired, contradictory or unreviewed mandatory evidence fails closed.

## 3. Eligibility record

A `VenueEligibilityRecord` is an immutable evidence snapshot with a monotonically increasing revision. It must bind to one exact owner account scope, one venue legal entity, one regional platform, one product family and a defined instrument scope.

Minimum fields:

| Field group | Required evidence |
|---|---|
| Identity / jurisdiction | Internal owner-profile reference; statutory residency basis and review date; citizenship/nationality only where relevant to KYC; actual residence jurisdiction; account-opening jurisdiction. Raw identity documents and addresses remain outside the public repository. |
| Venue entity | Legal entity name/identifier; platform region (Global/EU/other); applicable terms and API-agreement version; contracting entity and governing law. |
| Product scope | Product family (spot digital currency, foreign digital instrument, linear/inverse/quanto derivative, exchange-traded future, other); exact instrument IDs; base/quote/settlement assets; custody/settlement model. |
| Regulatory analysis | Applicable laws and effective dates; product classification; required local intermediary/register status; counsel review reference; unresolved assumptions and explicit scope. |
| Investor eligibility | Qualified/non-qualified status as confirmed by the broker/venue; tests and warnings completed; annual or product limits; evidence timestamp and account scope. |
| Venue KYC / compliance | KYC level/status; written product/API eligibility confirmation; sanctions-screening outcome reference and date; restrictions and expiry. Do not store raw screening data in public Git. |
| Funding / custody | Approved funding rail and account owner; permitted deposits/transfers; custody model; withdrawal destination classes and legal restrictions. |
| API / data rights | API product/version; exact permissions; IP allowlist requirement; explicit withdrawal permission status; market-data depth/history scope; data retention and redistribution rights. |
| Validity | Record revision; evidence source references; reviewer; owner approval; created/effective/expiry timestamps; revalidation triggers; superseded record reference. |

Public repository artifacts may contain schema, policy identifiers, source URLs and non-sensitive evidence references only. They MUST NOT contain identity documents, residential addresses, tax IDs, account numbers, KYC files, API credentials, sanctions-screening payloads or private legal correspondence.

## 4. Adapter activation states

Each exact venue/account/product scope has one state:

- `RESEARCH_ONLY` — public documentation and capability research only; no authenticated account access.
- `DATA_ONLY` — explicitly approved market-data access for the defined account/product and permitted data use; no order or account-mutating API permissions.
- `PAPER_ONLY` — simulation or sandbox only; no production order route. Data source must itself be lawfully accessible and licensed for this use.
- `LIVE_ELIGIBLE` — all mandatory legal, venue, account, product, API, security and owner gates passed for a tightly defined scope.
- `SUSPENDED` — previously eligible scope is frozen pending revalidation; no new live instructions.
- `REVOKED` — eligibility withdrawn; return to research requires a new record/revision and review.

A state applies only to its bound scope. Approval for spot does not imply approval for margin, futures, perpetuals, options, transfers or withdrawals. Approval for one venue entity or regional platform does not transfer to another entity under the same brand.

## 5. Live activation conditions

Transition to `LIVE_ELIGIBLE` requires all of the following evidence:

1. **Legal classification:** exact product and settlement model are classified under applicable law; any ambiguity that could change legality is resolved by qualified counsel.
2. **Jurisdiction:** statutory residency and relevant nationality/residence variables are established; effective laws and transition dates are analyzed.
3. **Venue entity:** the exact contracting entity and regional terms are identified; the venue confirms the account can use the exact product and API while meeting truthful KYC requirements.
4. **Investor access:** qualified/non-qualified status, tests, warnings, product restrictions and annual limits are confirmed by the broker/venue.
5. **Funding/custody:** funding source, beneficial ownership, custody and withdrawal constraints are documented; no prohibited or unsupported route is assumed.
6. **API rights:** exact API product, endpoints, key permissions, IP restrictions, market-data rights and history access are verified.
7. **Security:** credential vault, no-withdrawal key scope where supported, rotation/revocation, network egress controls and audit trail are approved.
8. **Execution/Risk:** NX-IF-001..005 and the independent Risk/Execution gates are separately satisfied.
9. **Owner approval:** owner explicitly approves the exact record revision and the limited activation scope.
10. **Validity:** evidence is current, not expired, and no revalidation trigger is active.

A missing item blocks live activation. The gate must return a machine-readable denial reason, not a generic Boolean.

## 6. Enforcement and command flow

- The venue adapter cannot self-assert its own eligibility.
- The Eligibility Gate is an independent control-plane authority, not an AI Orchestrator prompt or connector-local configuration flag.
- Every live command authorization must bind to the current eligibility record ID/revision and exact venue/account/product scope.
- The Execution Gateway must reject a command if the record is missing, stale, expired, suspended, revoked, mismatched or not in `LIVE_ELIGIBLE`.
- Eligibility evidence is checked independently from the Risk Engine approval. Both must pass; neither can override the other.
- A cached eligibility token must be cryptographically bound to scope, revision, expiry and audience. If its freshness cannot be proven, live execution fails closed.
- A change in legal rules, venue terms, KYC status, account region, residence, nationality where relevant, product, settlement asset, funding rail, sanctions status or API permission triggers revalidation and may automatically move the scope to `SUSPENDED`.
- No geolocation/IP inference, VPN detection, address substitution or nationality guess is sufficient to grant or revoke legal eligibility. Verified evidence and formal review control the decision.

### 6.1 Egress-bound eligibility fencing

A simple preflight read of the Eligibility Gate is insufficient because eligibility may be suspended after command authorization but before the network side effect.

The production design MUST:
- bind `eligibility_record_id`, revision, scope digest, monotonically increasing scope epoch and expiry to the canonical live command;
- verify the record at command admission and again at the final trusted egress boundary immediately before the external side effect;
- make the egress boundary the sole holder of live venue credentials; no strategy, AI, adapter worker or stale dispatcher may retain a direct path to the venue;
- serialize eligibility-epoch changes with dispatch so that a stale command cannot be sent after a suspension/revocation epoch has advanced;
- reject if the current record revision/epoch differs, the record is expired, or the trusted eligibility state is unavailable;
- preserve OUTCOME_UNKNOWN and reconcile if the external send may already have occurred; never assume a suspension cancels an accepted venue order.

A local cached flag, process lease or caller-side check is not a security boundary. This requirement reuses the same stale-worker/egress-fencing principle already identified in the execution reference work.

## 7. Suspensions and emergency operations

Suspension is not permission to continue trading under a different label.

When eligibility is suspended or revoked:
- no new risk-increasing order may be submitted;
- no order amend, cancel, reduce, close, cancel-all or flatten operation is automatically presumed lawful;
- the permitted emergency operation set must be explicitly established by legal review, venue rules and NX-IF-005;
- if no permitted action is evidenced, NEXUS must halt new commands and surface the outstanding orders/positions for operator handling;
- the gate must not silently transform a legal suspension into a risk-reduction authorization.

This avoids assuming that a cancel/close/flatten command is always legally permitted in every suspension scenario.

## 8. Alternatives considered

### A. Hard-code a venue allowlist in the adapter

Rejected. Eligibility changes independently of connector code and varies by entity, account, product, settlement and effective date. A static allowlist becomes stale and hides missing evidence.

### B. Infer eligibility from IP address, app store, country selector or successful KYC login

Rejected. IP is not statutory residency; account login is not proof of product/API permission or local-law compliance. KYC outcomes may be partial, conditional or product-specific.

### C. Let the AI Orchestrator decide whether trading is legally allowed

Rejected. Legal eligibility is a deterministic control-plane gate based on reviewed evidence. AI may summarize evidence or flag changes but cannot grant eligibility or bypass the gate.

### D. Treat Risk Engine approval as sufficient

Rejected. Risk controls exposure and trading constraints; it does not establish jurisdictional, contractual or regulatory permission.

### E. Disable all foreign venues permanently

Deferred. This may be the eventual outcome for a particular owner/product/legal scenario, but the gate should represent evidence-backed eligibility rather than hard-code an unreviewed global conclusion.

## 9. Consequences

**Positive**
- Venue selection becomes evidence-based and auditable.
- Legal/product changes can suspend only the affected scope.
- AI, adapters and Risk Engine cannot bypass the separate eligibility boundary.
- Personal-use and future commercial rights remain explicitly distinct.
- Sensitive KYC and identity records stay outside public Git.

**Costs**
- Additional control-plane schema, lifecycle, signatures, expiry and review process.
- Every venue/product/account combination requires a qualification dossier.
- Owner and legal reviewer must maintain evidence and approve revisions.
- Some technically available venues may remain disabled due to unresolved law or terms.

## 10. Open owner/legal decisions

- Which qualified legal reviewer will approve statutory residency, product classification and Article 30(2) software-assistance analysis?
- What evidence format and retention period will the reviewer require?
- Which emergency operations, if any, remain permitted after eligibility suspension?
- Who can approve, suspend and revoke an eligibility record?
- What revalidation cadence is appropriate for each venue and legal regime?
- How should broker-specific annual limits be reconciled across multiple accounts or intermediaries?
- What data and API rights are required for a future commercial NEXUS product?

No defaults are selected for these decisions.

## 11. Cross-document consistency review (2026-11-14)

Reviewed exact branch versions:
- NX-IF-001, blob `8324c9b1f9a221fbb505c89c008a4e99d77741c7`;
- NX-IF-002, blob `7205cefb1d9fe76283f089ca272199087fd4e9ec`;
- NX-IF-003, blob `62d93913d88f0c0af4eb5ad623160b9770acac76`;
- NX-IF-004, blob `abc4e5808c129d4556c1dfe622d18d6a8710b82c`;
- NX-IF-005, blob `648543cd89b196cd0ee1d78d9b81d73257364b1d`;
- NX-SEC-001, blob `06c5ee9d6c5ec0e5b7549e9d3cf0a5a872328e01`;
- NX-ADR-002, blob `7107feec894ab4f8e4bf4e210153551b3555b541`.

**Result: no blocking contradiction found.** The following integration points must be addressed before implementation:
- NX-IF-001 must carry an eligibility evidence reference separately from the Risk approval; Risk must not become the legal eligibility authority.
- NX-IF-002 exposure and reservation semantics remain independent of legal eligibility.
- NX-IF-003 ledger posting ownership is unchanged.
- NX-IF-004 should include eligibility evidence freshness/revalidation state where it affects system readiness.
- NX-IF-005 must define operation-specific permissions after eligibility suspension; no cancel/close/flatten permission is presumed.
- NX-SEC-001 requires the eligibility evidence vault and reviewer/operator access controls to protect identity and legal records.
- NX-ADR-002 / fenced egress must verify the current eligibility revision/epoch at the final side-effect boundary and prevent stale dispatchers from bypassing suspension.

This is a bounded consistency pass over the relevant authority, command, state, security and egress integration boundaries; it is not a full line-by-line conformance review, owner acceptance, legal opinion, conformance evidence or implementation verification.

## 12. Acceptance criteria for this ADR

- [x] Separate legal/venue eligibility from Risk Engine authorization and adapter capability.
- [x] Define immutable scope-bound eligibility record and evidence groups.
- [x] Define fail-closed activation states and required live evidence.
- [x] Define revision binding, freshness, expiry and revalidation triggers.
- [x] Explicitly avoid automated legal inference and identity data in public Git.
- [x] Define suspension behavior without assuming cancel/close/flatten is automatically permitted.
- [ ] Owner review and acceptance.
- [ ] Qualified legal review of applicable laws and product classification.
- [ ] Cross-review against NX-IF-001..005, NX-SEC-001 and NX-ADR-002.
- [ ] Conformance scenarios and tests for missing, stale, expired, mismatched, suspended and revoked records.
- [ ] Production identity/evidence storage, signing, authorization and operator role design.

**Disposition:** PROPOSED. Cross-document consistency review completed with no blocking contradiction; owner/legal review and conformance evidence remain open. No implementation, API key, order or live capability is authorized. G0/G1 remain blocked.
