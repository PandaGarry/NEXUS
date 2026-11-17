# NEXUS — product evolution and activation triggers

**Last reviewed:** 2026-11-15  
**Current product direction:** personal-first, single-owner deployment. Commercial use is a separate product stage.

## 1. Product stages

### Stage A — Personal engineering and research

- One owner; no third-party accounts or assets.
- Public market data, historical research, offline replay, deterministic tests and paper/simulation.
- No private account credentials or live order dispatch by default.
- Venue-neutral domain direction with concrete provider-specific adapters.

### Stage B — Personal test operation

- Read-only account integrations only where expressly permitted.
- Sandbox/testnet and paper execution after adapter and security gates.
- Private credentials, if ever introduced, must be scoped, isolated, audited and excluded from source control.
- No live capital until explicit owner approval and all readiness gates pass.

### Stage C — Personal production consideration

- One verified eligible account/product path.
- Certified market-data, order lifecycle, reconciliation, risk, emergency and recovery behavior.
- Explicit live authorization remains separate from deployment profile.
- No third-party users or customer funds.

### Stage D — Commercial/public product (not in current scope)

This is a separate product and legal/security architecture. It must not inherit personal approvals or permissions.

## 2. Mandatory re-evaluation triggers

Any one of the following triggers a formal commercial-readiness work package before the corresponding capability is enabled:

1. First user other than the owner.
2. Any third-party API key, account, asset or money enters the system.
3. Multiple tenants share one database, runtime, queue, cache, event log or control plane.
4. An external service receives authority to issue, approve or dispatch commands.
5. NEXUS redistributes third-party market data, offers paid access, or provides hosted strategy execution to others.
6. Any custody, pooled capital, managed-account, advisory, brokerage or copy-trading-like service is contemplated.

## 3. Controls activated by the trigger

The scope of the review must include, as applicable:

- tenant identity and isolation at every data/control plane boundary;
- PostgreSQL RLS and database privilege separation (including HEGC or equivalent policy controls);
- signed, scoped, expiring and revocable capabilities;
- secret vaulting, per-tenant credential isolation, rotation and incident response;
- immutable audit trail and evidence provenance;
- privacy, data retention, deletion/export and breach response;
- market-data and software licensing / redistribution rights;
- exchange API terms and customer-key authorization model;
- jurisdiction-specific legal, licensing, tax and consumer-protection analysis by qualified counsel;
- support, service-level, incident and operational-resilience requirements;
- threat model, penetration testing and independent security review.

No single checklist item is an automatic implementation prescription; the design must match the actual commercial model and threat model.

## 4. Explicit boundaries

- A future commercial mode is not a UI toggle.
- A company, foreign server, VPN, nominee or third-party account does not automatically establish exchange eligibility or resolve legal obligations.
- No third-party assets or credentials are to be accepted before legal and security approval.
- The existence of multi-tenant architecture proposals in old Draft PRs does not mean NEXUS is a multi-tenant product today.
- Deferred controls should have named triggers and owners, not vague "later" labels.

## 5. Review questions

- Does the first external user change the data controller / processor or service-provider obligations?
- Does any third-party key permit the system to act on behalf of another person?
- Are tenants isolated at database, storage, queue, secrets, logs, caches and support tooling?
- Are upstream data rights compatible with redistribution and derived-data products?
- Do provider API terms permit the proposed automation and customer-key model?
- Which licenses, registrations or other legal requirements apply in the actual operating jurisdiction?
