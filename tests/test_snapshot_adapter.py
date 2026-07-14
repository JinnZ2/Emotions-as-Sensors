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
    "time",
}


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
