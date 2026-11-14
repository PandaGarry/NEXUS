import unittest

from instrument_registry import (
    EffectiveTimeRegression, IdentityConflict, InstrumentSpecRegistry,
    Registration, VersionConflict,
)
from test_instrument_spec import dec, spec


class InstrumentSpecRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = InstrumentSpecRegistry()

    def test_registers_first_snapshot_and_returns_latest(self):
        first = spec()
        self.assertEqual(self.registry.register(first), Registration.ADDED)
        self.assertEqual(self.registry.get(first.instrument_id), first)
        self.assertEqual(self.registry.history(first.instrument_id), (first,))

    def test_newer_version_appends_without_mutating_history(self):
        first = spec()
        second = spec(spec_version=2, tick_size=dec("0.01"))
        self.registry.register(first)
        self.registry.register(second)
        self.assertEqual(self.registry.get(first.instrument_id, 1), first)
        self.assertEqual(self.registry.get(first.instrument_id, 2), second)
        self.assertEqual(self.registry.get(first.instrument_id), second)
        self.assertEqual(self.registry.history(first.instrument_id), (first, second))

    def test_identical_latest_version_is_idempotent(self):
        value = spec()
        self.registry.register(value)
        self.assertEqual(self.registry.register(value), Registration.ALREADY_PRESENT)

    def test_identical_historical_version_replay_is_idempotent(self):
        first = spec()
        second = spec(spec_version=2)
        self.registry.register(first)
        self.registry.register(second)
        self.assertEqual(self.registry.register(first), Registration.ALREADY_PRESENT)

    def test_same_version_with_different_content_is_rejected(self):
        first = spec()
        self.registry.register(first)
        changed = spec(tick_size=spec().quantity_step)
        with self.assertRaises(VersionConflict):
            self.registry.register(changed)

    def test_version_regression_is_rejected(self):
        self.registry.register(spec(spec_version=3))
        with self.assertRaisesRegex(VersionConflict, "increase"):
            self.registry.register(spec(spec_version=2))

    def test_internal_id_cannot_be_rebound_to_another_venue_identity(self):
        self.registry.register(spec())
        with self.assertRaises(IdentityConflict):
            self.registry.register(spec(spec_version=2, native_instrument_id="BTC-USDC"))

    def test_known_effective_time_cannot_regress(self):
        self.registry.register(spec(effective_at_ms=2000))
        with self.assertRaises(EffectiveTimeRegression):
            self.registry.register(spec(spec_version=2, effective_at_ms=1999))

    def test_unknown_effective_time_is_not_invented(self):
        first = spec(effective_at_ms=2000)
        second = spec(spec_version=2, effective_at_ms=None)
        self.registry.register(first)
        self.assertEqual(self.registry.register(second), Registration.ADDED)

    def test_effective_time_regression_is_detected_across_unknown_intermediate(self):
        self.registry.register(spec(effective_at_ms=2000))
        self.registry.register(spec(spec_version=2, effective_at_ms=None))
        with self.assertRaises(EffectiveTimeRegression):
            self.registry.register(spec(spec_version=3, effective_at_ms=1999))

    def test_instruments_have_independent_histories(self):
        first = spec()
        other = spec(instrument_id="nexus:demo:ETH-USDT", native_instrument_id="ETH-USDT",
                     base_asset="ETH", quantity_unit="ETH")
        self.registry.register(first)
        self.registry.register(other)
        self.assertEqual(self.registry.get(first.instrument_id), first)
        self.assertEqual(self.registry.get(other.instrument_id), other)
        self.assertEqual(len(self.registry.history(first.instrument_id)), 1)
        self.assertEqual(len(self.registry.history(other.instrument_id)), 1)

    def test_unknown_version_returns_none(self):
        self.registry.register(spec())
        self.assertIsNone(self.registry.get("nexus:demo:BTC-USDT", 99))
        self.assertIsNone(self.registry.get("nexus:demo:MISSING"))


if __name__ == "__main__":
    unittest.main()
