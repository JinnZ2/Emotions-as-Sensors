"""Tests for the emotions_as_sensors.snapshot() public adapter.

The adapter is the contract downstream consumers (Bridge orchestrator,
chemistry resolver) call to read emotion sensor state. These tests pin:

  1. Documented key set is stable.
  2. Zero-state maps to stress='low', urgent=False.
  3. High-arousal negative-valence PAD maps to stress='high', urgent=True.
  4. Custom system can be injected (no reliance on the module-level singleton).
  5. Corrupted sensors are surfaced separately and excluded from activations.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import emotions_as_sensors as eas
from emotion_core import EmotionSystem


EXPECTED_KEYS = {
    "pad",
    "octa",
    "coherence",
    "activations",
    "corrupted",
    "stress_level",
    "urgent",
    "metrology",
    "time",
}

METROLOGY_AXES = {"pred", "shift", "tunnel", "realloc",
                  "cohere", "uncert", "duration"}


@pytest.fixture
def fresh_system():
    """A freshly loaded EmotionSystem — no cross-test state bleed."""
    return EmotionSystem(str(_ROOT / "sensors"))


def test_snapshot_returns_documented_keys(fresh_system):
    snap = eas.snapshot(system=fresh_system)
    assert set(snap.keys()) == EXPECTED_KEYS


def test_zero_state_is_calm(fresh_system):
    snap = eas.snapshot(system=fresh_system)
    assert snap["stress_level"] == "low"
    assert snap["urgent"] is False
    assert snap["activations"] == {}
    assert snap["pad"] == {"P": 0.0, "A": 0.0, "D": 0.0}


def test_stressed_pad_maps_to_high_and_urgent(fresh_system):
    # Drive a negative-valence, high-arousal sensor to E=0.9.
    driven = None
    for s in fresh_system.sensors:
        if s.pad_p < -0.3 and s.pad_a > 0.5:
            s.E = 0.9
            driven = s.name
            break
    assert driven is not None, "expected a fear/anger-shaped sensor in fleet"

    snap = eas.snapshot(system=fresh_system)
    assert snap["pad"]["P"] < 0
    assert snap["pad"]["A"] > 0.5
    assert snap["stress_level"] == "high"
    assert snap["urgent"] is True
    assert driven in snap["activations"]


def test_worried_but_not_urgent(fresh_system):
    # Negative-valence, moderate arousal → medium stress, not urgent.
    driven = None
    for s in fresh_system.sensors:
        if s.pad_p < -0.3 and 0.2 < s.pad_a < 0.5:
            s.E = 0.6
            driven = s.name
            break
    if driven is None:
        pytest.skip("no medium-arousal negative-valence sensor available")

    snap = eas.snapshot(system=fresh_system)
    assert snap["stress_level"] == "medium"
    assert snap["urgent"] is False


def test_corrupted_sensor_surfaces_separately(fresh_system):
    if not fresh_system.sensors:
        pytest.skip("no sensors loaded")
    s = fresh_system.sensors[0]
    s.E = 0.5
    s.authentic = False

    snap = eas.snapshot(system=fresh_system)
    assert s.name in snap["corrupted"]
    assert s.name not in snap["activations"]


def test_default_singleton_reload():
    """reset_default_system() forces a fresh load on next snapshot()."""
    first = eas._get_default_system()
    eas.reset_default_system()
    second = eas._get_default_system()
    assert first is not second


def test_metrology_axes_present_and_named(fresh_system):
    """metrology sub-key exposes exactly the 7 constraint-state axes."""
    snap = eas.snapshot(system=fresh_system)
    assert set(snap["metrology"].keys()) == METROLOGY_AXES


def test_metrology_zero_state(fresh_system):
    snap = eas.snapshot(system=fresh_system)
    assert all(v == 0.0 for v in snap["metrology"].values())


def test_metrology_tunnel_reflects_concentration(fresh_system):
    """One dominant sensor → tunnel near 1.0."""
    if not fresh_system.sensors:
        pytest.skip("no sensors loaded")
    fresh_system.sensors[0].E = 0.8
    snap = eas.snapshot(system=fresh_system)
    assert snap["metrology"]["tunnel"] > 0.9


def test_metrology_uncert_reflects_corruption_fraction(fresh_system):
    """uncert = fraction of the fleet failing the authenticity gate."""
    total = len(fresh_system.sensors)
    if total == 0:
        pytest.skip("no sensors loaded")
    # Corrupt roughly half the fleet.
    to_corrupt = max(1, total // 2)
    for s in fresh_system.sensors[:to_corrupt]:
        s.authentic = False

    snap = eas.snapshot(system=fresh_system)
    expected = round(to_corrupt / total, 4)
    assert snap["metrology"]["uncert"] == pytest.approx(expected, abs=1e-3)


def test_metrology_duration_rises_with_longlived_sensors(fresh_system):
    """Immortal-decay activation pushes duration higher than exponential."""
    immortal = next(
        (s for s in fresh_system.sensors if s.decay_model == "immortal"), None
    )
    exponential = next(
        (s for s in fresh_system.sensors if s.decay_model == "exponential"), None
    )
    if immortal is None or exponential is None:
        pytest.skip("need both immortal and exponential sensors in fleet")

    exponential.E = 0.8
    snap_short = eas.snapshot(system=fresh_system)
    exponential.E = 0.0
    immortal.E = 0.8
    snap_long = eas.snapshot(system=fresh_system)

    assert snap_long["metrology"]["duration"] > snap_short["metrology"]["duration"]
