"""Append-only in-memory instrument specification registry reference.

TEST-ONLY: no persistence, concurrency, source authority or distributed ordering.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from instrument_spec import InstrumentSpec


class RegistryError(ValueError):
    """Base class for registry reference errors."""


class VersionConflict(RegistryError):
    """A version was reused with different content or moved backwards."""


class IdentityConflict(RegistryError):
    """A stable internal instrument ID was rebound to another venue identity."""


class EffectiveTimeRegression(RegistryError):
    """A new version has an earlier known effective time than its predecessor."""


class Registration(str, Enum):
    ADDED = "ADDED"
    ALREADY_PRESENT = "ALREADY_PRESENT"


class InstrumentSpecRegistry:
    __slots__ = ("_history",)
    """Append-only registry for immutable InstrumentSpec snapshots.

    This object is deliberately single-process and in-memory. The caller owns
    version assignment. A repeated identical version is idempotent; a repeated
    version with different content is rejected. New versions must increase.
    """

    def __init__(self) -> None:
        self._history: dict[str, tuple[InstrumentSpec, ...]] = {}

    def register(self, spec: InstrumentSpec) -> Registration:
        if not isinstance(spec, InstrumentSpec):
            raise RegistryError("spec must be an InstrumentSpec")
        history = self._history.get(spec.instrument_id, ())
        if not history:
            self._history[spec.instrument_id] = (spec,)
            return Registration.ADDED

        for existing in history:
            if spec.spec_version == existing.spec_version:
                if spec == existing:
                    return Registration.ALREADY_PRESENT
                raise VersionConflict("same spec_version has different snapshot content")

        latest = history[-1]
        if spec.spec_version < latest.spec_version:
            raise VersionConflict("spec_version must increase monotonically")

        if (spec.venue_id, spec.native_instrument_id, spec.market_type) != (
            latest.venue_id, latest.native_instrument_id, latest.market_type
        ):
            raise IdentityConflict(
                "instrument_id cannot be rebound to another venue/native instrument/market"
            )

        if (
            latest.effective_at_ms is not None
            and spec.effective_at_ms is not None
            and spec.effective_at_ms < latest.effective_at_ms
        ):
            raise EffectiveTimeRegression(
                "known effective_at_ms cannot move backwards across versions"
            )

        self._history[spec.instrument_id] = (*history, spec)
        return Registration.ADDED

    def get(
        self, instrument_id: str, spec_version: Optional[int] = None
    ) -> Optional[InstrumentSpec]:
        history = self._history.get(instrument_id, ())
        if spec_version is None:
            return history[-1] if history else None
        for snapshot in history:
            if snapshot.spec_version == spec_version:
                return snapshot
        return None

    def history(self, instrument_id: str) -> tuple[InstrumentSpec, ...]:
        return self._history.get(instrument_id, ())
