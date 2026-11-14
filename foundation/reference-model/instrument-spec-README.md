# Instrument Specification Reference Model

**Status:** Test-only conformance aid; not production code.

## Run

From this directory:

```bash
python -m unittest -v test_instrument_spec.py
```

The test module imports the existing `nexus_decimal.py` oracle from the same directory.

## Scope

- immutable, versioned instrument metadata snapshot;
- explicit market, contract and lifecycle enums;
- exact tick-size and quantity-step validation;
- minimum/maximum quantity and minimum notional checks;
- provenance identifier, raw-payload SHA-256, fetch time and optional effective time;
- explicit `REQUIRED`, `NOT_APPLICABLE` and `UNKNOWN` applicability for minimum notional;
- fail-closed handling for unknown status/contract semantics and unsupported inverse/quanto calculations.

The JSON fixture is synthetic and is only a schema/conformance example.

## Explicit limitations

- no venue adapter, HTTP client, pagination or official venue fixture;
- no raw payload persistence or cryptographic authenticity verification;
- no freshness policy or immutable registry/database;
- no contract notional/exposure/P&L calculation;
- no margin/leverage tiers, price bands, fee/funding, account risk or order authorization;
- no spot quote-quantity semantics;
- no inverse/quanto order validation;
- no production bounds, Rust/backend/client conformance or live trading.

This validator checks a narrow subset of instrument rules. Passing it does not authorize an order or establish that an instrument is tradable in a production system.
