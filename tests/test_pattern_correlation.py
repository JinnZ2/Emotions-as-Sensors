"""Tests for the Non-Local Pattern Correlation Sensor selection protocol.

The sensor (sensors/non-local-pattern-correlation.json) replaces the older
"morphic resonance" label. Instead of a single causal mechanism, it offers
a menu of grounded exploration techniques. The investigator selects the
technique whose scope matches the question.

These tests exercise the protocol encoded in the sensor JSON:

  1. Selecting an inappropriate-scale technique for a given correlation
     type produces a warning.
  2. The U(t) routing (field_correlation_observation) only fires after all
     established techniques have been checked and failed.
  3. Parallel-technique convergence is supported — multiple techniques
     can report on the same signal.
"""

from __future__ import annotations

import json
import pathlib
import warnings

import pytest

SENSOR_PATH = (
    pathlib.Path(__file__).parent.parent
    / "sensors"
    / "non-local-pattern-correlation.json"
)

UTOFT_TECHNIQUE = "field_correlation_observation"


@pytest.fixture(scope="module")
def sensor() -> dict:
    return json.loads(SENSOR_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def scale_map(sensor: dict) -> dict[str, list[str]]:
    return sensor["scale_to_technique"]


@pytest.fixture(scope="module")
def technique_names(sensor: dict) -> set[str]:
    return {t["name"] for t in sensor["exploration_techniques"]}


def select_techniques(
    scale: str,
    scale_map: dict[str, list[str]],
) -> list[str]:
    """Return the techniques whose scope matches the given scale.

    Emits a warning if the caller passes a scale the protocol doesn't
    recognize and falls back to the U(t) route.
    """
    if scale not in scale_map:
        warnings.warn(
            f"scale {scale!r} is not in the selection protocol; "
            f"falling back to {UTOFT_TECHNIQUE}",
            UserWarning,
            stacklevel=2,
        )
        return [UTOFT_TECHNIQUE]
    return list(scale_map[scale])


def warn_if_mismatched(
    scale: str,
    technique: str,
    scale_map: dict[str, list[str]],
) -> None:
    """Warn when a technique is applied at a scale it isn't scoped for."""
    appropriate = set()
    for techniques in scale_map.values():
        appropriate.update(techniques)
    if technique not in appropriate:
        warnings.warn(
            f"technique {technique!r} is not registered in the "
            f"selection protocol",
            UserWarning,
            stacklevel=2,
        )
        return
    if technique not in scale_map.get(scale, []):
        warnings.warn(
            f"technique {technique!r} is inappropriate for scale "
            f"{scale!r}; expected one of "
            f"{scale_map.get(scale, [])}",
            UserWarning,
            stacklevel=2,
        )


def route_with_fallback(
    scale: str,
    scale_map: dict[str, list[str]],
    technique_results: dict[str, bool],
) -> list[str]:
    """Run techniques for the scale, falling back to U(t) only if all fail.

    technique_results maps technique name to whether it produced a fit.
    Returns the techniques that fired (in order). If none of the
    established techniques fit, U(t) is appended last.
    """
    selected = select_techniques(scale, scale_map)
    fired = [t for t in selected if technique_results.get(t, False)]
    if fired:
        return fired
    if all(not technique_results.get(t, False) for t in selected):
        if UTOFT_TECHNIQUE not in selected:
            return selected + [UTOFT_TECHNIQUE]
        return selected
    return fired


# ---------------------------------------------------------------------------
# (1) Inappropriate-scale technique selection produces a warning
# ---------------------------------------------------------------------------


def test_inappropriate_scale_technique_warns(scale_map: dict) -> None:
    with pytest.warns(UserWarning, match="inappropriate for scale"):
        warn_if_mismatched(
            scale="landscape",
            technique="gene_expression_dynamics",
            scale_map=scale_map,
        )


def test_unknown_scale_falls_back_to_utoft_with_warning(
    scale_map: dict,
) -> None:
    with pytest.warns(UserWarning, match="not in the selection protocol"):
        result = select_techniques("not_a_real_scale", scale_map)
    assert result == [UTOFT_TECHNIQUE]


def test_appropriate_scale_technique_does_not_warn(
    scale_map: dict,
) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        warn_if_mismatched(
            scale="generational",
            technique="epigenetic_inheritance",
            scale_map=scale_map,
        )


# ---------------------------------------------------------------------------
# (2) U(t) routing only fires after all techniques have been checked and
#     failed
# ---------------------------------------------------------------------------


def test_utoft_does_not_fire_when_a_technique_fits(scale_map: dict) -> None:
    fired = route_with_fallback(
        scale="generational",
        scale_map=scale_map,
        technique_results={
            "epigenetic_inheritance": True,
            "mitochondrial_signaling": False,
        },
    )
    assert UTOFT_TECHNIQUE not in fired
    assert "epigenetic_inheritance" in fired


def test_utoft_fires_only_when_all_established_techniques_fail(
    scale_map: dict,
) -> None:
    fired = route_with_fallback(
        scale="generational",
        scale_map=scale_map,
        technique_results={
            "epigenetic_inheritance": False,
            "mitochondrial_signaling": False,
        },
    )
    assert fired[-1] == UTOFT_TECHNIQUE


def test_utoft_is_the_documented_unestablished_route(
    scale_map: dict,
) -> None:
    assert scale_map["unestablished_reproducible"] == [UTOFT_TECHNIQUE]


# ---------------------------------------------------------------------------
# (3) Parallel-technique convergence is supported
# ---------------------------------------------------------------------------


def test_generational_scale_supports_parallel_techniques(
    scale_map: dict,
) -> None:
    techniques = scale_map["generational"]
    assert len(techniques) >= 2, (
        "generational scale should expose multiple techniques so "
        "convergence can be checked"
    )


def test_cellular_scale_supports_parallel_techniques(
    scale_map: dict,
) -> None:
    techniques = scale_map["cellular"]
    assert len(techniques) >= 2


def test_parallel_techniques_can_both_report_on_one_signal(
    scale_map: dict,
) -> None:
    fired = route_with_fallback(
        scale="generational",
        scale_map=scale_map,
        technique_results={
            "epigenetic_inheritance": True,
            "mitochondrial_signaling": True,
        },
    )
    assert "epigenetic_inheritance" in fired
    assert "mitochondrial_signaling" in fired
    assert UTOFT_TECHNIQUE not in fired


# ---------------------------------------------------------------------------
# Sanity: the JSON's structural invariants the protocol depends on
# ---------------------------------------------------------------------------


def test_every_scale_maps_to_known_techniques(
    scale_map: dict,
    technique_names: set[str],
) -> None:
    for scale, techniques in scale_map.items():
        unknown = [t for t in techniques if t not in technique_names]
        assert not unknown, (
            f"scale {scale!r} references unknown techniques: {unknown}"
        )


def test_utoft_technique_is_defined(technique_names: set[str]) -> None:
    assert UTOFT_TECHNIQUE in technique_names


def test_sensor_supersedes_morphic_resonance(sensor: dict) -> None:
    assert sensor.get("supersedes") == "morphic_resonance"
