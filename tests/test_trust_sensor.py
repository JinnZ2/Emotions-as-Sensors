"""Tests for src/trust_sensor.py — pins the falsifiable claims C1..C5.

Each test name references the claim it exercises. If a test breaks and
the *behavior* is right, update the claim in CLAIM_TABLE; do not retune
the scorer to save the test (per the module's refutation protocol).
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from trust_sensor import (  # noqa: E402
    Breach,
    Commitment,
    Delivery,
    Resolution,
    TrustSensor,
    CLAIM_TABLE,
)


def _kept(cid, t, cost=1.0, stakes=1.0):
    return (
        Commitment(cid, "X", "s", issued_at=t, due_at=t + 1,
                   cost_to_keep=cost, stakes=stakes),
        Resolution(cid, observed_at=t + 1, delivery=Delivery.AS_STATED),
    )


def _absent(cid, t, breach=Breach.NONE, cost=1.0, stakes=1.0):
    return (
        Commitment(cid, "X", "s", issued_at=t, due_at=t + 1,
                   cost_to_keep=cost, stakes=stakes),
        Resolution(cid, observed_at=t + 1, delivery=Delivery.ABSENT, breach=breach),
    )


def test_empty_input_returns_no_read():
    out = TrustSensor().emit([])
    assert out["trajectory"] == []
    assert out["read"] is None


def test_C1_kept_promises_monotonically_drop_entropy():
    """C1: trust == reduced predictive surprise."""
    s = TrustSensor()
    traj = s.read([_kept(f"k{i}", i) for i in range(8)])
    entropies = [p.entropy_bits for p in traj]
    for a, b in zip(entropies, entropies[1:]):
        assert b <= a, f"entropy rose from {a} to {b} on all-kept stream"
    assert entropies[-1] < entropies[0]


def test_C2_ceiling_gates_on_cure_threshold():
    """C2: trust compounds — you can't buy high stakes without a cured base."""
    s = TrustSensor(cure_threshold=3.0)
    # one big-stakes kept promise: mass = 1 * 5 = 5 >= 3, cures immediately
    traj = s.read([_kept("k0", 0, cost=1.0, stakes=5.0)])
    assert traj[-1].ceiling == 5.0

    # by contrast: two small kept promises (mass 1 each) do NOT cure tier 5
    s2 = TrustSensor(cure_threshold=3.0)
    traj2 = s2.read([_kept(f"k{i}", i, cost=1.0, stakes=1.0) for i in range(2)])
    assert traj2[-1].ceiling == 0.0


def test_C3_high_cost_promise_moves_p_more_than_low_cost():
    """C3: cost-to-keep weights the information in a kept promise."""
    s_low = TrustSensor()
    s_high = TrustSensor()
    p_low = s_low.read([_kept("k0", 0, cost=0.1, stakes=1.0)])[-1].p_estimate
    p_high = s_high.read([_kept("k0", 0, cost=10.0, stakes=1.0)])[-1].p_estimate
    assert p_high > p_low


def test_C4_breach_channel_separable_from_delivery():
    """C4: renegotiated late delivery reads differently from absent-and-silent."""
    s_reneg = TrustSensor()
    s_absent = TrustSensor()

    reneg_pair = (
        Commitment("k0", "X", "s", 0, 1, cost_to_keep=2.0, stakes=1.0),
        Resolution("k0", 2, delivery=Delivery.LATE, breach=Breach.RENEGOTIATED),
    )
    absent_pair = _absent("k0", 0, breach=Breach.NONE, cost=2.0)

    p_reneg = s_reneg.read([reneg_pair])[-1].p_estimate
    p_absent = s_absent.read([absent_pair])[-1].p_estimate
    assert p_reneg > p_absent, "renegotiated-and-delivered must beat absent"


def test_C5_contested_response_raises_noise_floor():
    """C5: ledger contest raises an irreducible non-computability floor."""
    s = TrustSensor()
    pairs = [
        _kept("k0", 0),
        _kept("k1", 1),
        _absent("k2", 2, breach=Breach.CONTESTED, cost=3.0, stakes=4.0),
    ]
    out = s.emit(pairs)
    assert out["read"]["ledger_scoreable"] is False
    lo, hi = out["read"]["p_band"]
    assert hi - lo > 0, "contested ledger must return a band, not a point"
    # 1 contest / 3 events == 0.3333 noise floor
    assert out["trajectory"][-1].ledger_noise == pytest.approx(0.3333, abs=1e-3)


def test_C5_acknowledged_failure_keeps_ledger_scoreable():
    """Same delivery outcome (ABSENT), different breach channel: scoreable."""
    s = TrustSensor()
    pairs = [
        _kept("k0", 0),
        _kept("k1", 1),
        _absent("k2", 2, breach=Breach.ACKNOWLEDGED),
    ]
    out = s.emit(pairs)
    assert out["read"]["ledger_scoreable"] is True
    lo, hi = out["read"]["p_band"]
    assert lo == hi, "clean ledger must collapse the band to a point"


def test_trajectory_is_time_ordered_by_observed_at():
    """Input order must not matter — trajectory sorts on observed_at."""
    s = TrustSensor()
    scrambled = [_kept("k2", 2), _kept("k0", 0), _kept("k1", 1)]
    traj = s.read(scrambled)
    ts = [p.t for p in traj]
    assert ts == sorted(ts)


def test_claim_table_has_all_five():
    assert set(CLAIM_TABLE.keys()) == {"C1", "C2", "C3", "C4", "C5"}
    for cid, entry in CLAIM_TABLE.items():
        assert "claim" in entry and "refuted_if" in entry
