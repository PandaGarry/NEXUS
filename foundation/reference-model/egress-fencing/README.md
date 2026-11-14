# Egress authority handover reference model

**Status:** Test-only control-plane state-machine model; not an egress security boundary.

This package models the required ordering for an account-scoped authority handover:

`ACTIVE → HALTING → FENCING → FENCED → RECONCILING → READY_TO_GRANT → ACTIVE(new epoch)`

It checks that:
- takeover revokes old-epoch eligibility at the modeled control plane;
- a new authority cannot be granted before positive old-egress fence evidence;
- reconciliation cannot begin before fencing;
- a new authority cannot be granted before reconciliation evidence;
- unknown fencing outcomes fail closed;
- stale identities/epochs cannot regain dispatch eligibility through the model.

Run:

```bash
python -m unittest -v
```

## Critical limitations

The model is deliberately not capable of fencing a real process or network route. Its fence receipt is an opaque test string supplied by the caller; there is no trusted attestation verifier, cloud/host supervisor, firewall/proxy integration, credential revocation, network policy or distributed database.

Therefore:
- a passing test proves only the modeled transition ordering;
- it does not prove a stale process cannot use already-held credentials or an open socket;
- it does not prove a host has been terminated or an egress route revoked;
- it is not production code and must not be imported into a trading service.

Production qualification still requires NX-REF-EXEC-002's independently controlled egress fence, positive evidence, reconciliation and adversarial tests against the actual network boundary.
