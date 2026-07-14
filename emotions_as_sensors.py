"""
emotions_as_sensors — public snapshot adapter.

Exposes emotion sensor state as a flat-ish dict for downstream consumers
(orchestrators, chemistry resolvers, dispatcher inputs). The contract:

    import emotions_as_sensors
    sensors = emotions_as_sensors.snapshot()
    optics = orchestrator.process(voice_query, sensor_snapshot=sensors)

    ctx = scr.Query(
        feedstock='black_beans', target_property='lubricant',
        emotional_signals={'stress_level': sensors['stress_level'],
                           'urgent':       sensors['urgent']},
    )
    result = resolver.navigate(ctx)   # long-dwell branches scored down

The snapshot pulls from a lazy module-level EmotionSystem loaded from
./sensors/. For tests or multi-system setups, pass one in explicitly:

    emotions_as_sensors.snapshot(system=my_system)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
_SENSORS_DIR = _ROOT / "sensors"

if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from emotion_core import EmotionSystem  # noqa: E402

_default_system: Optional[EmotionSystem] = None


def _get_default_system() -> EmotionSystem:
    global _default_system
    if _default_system is None:
        _default_system = EmotionSystem(str(_SENSORS_DIR))
    return _default_system


def reset_default_system() -> None:
    """Drop the cached module-level EmotionSystem. Next snapshot() reloads."""
    global _default_system
    _default_system = None


def _classify_stress(p: float, a: float) -> str:
    """
    Downstream stress summary derived from aggregated PAD.

    high    negative pleasure, high arousal   (fear / anger / despair)
    medium  negative pleasure, moderate arousal (worry / tension)
    low     otherwise (neutral or positive-valence)
    """
    if p < 0 and a > 0.5:
        return "high"
    if p < 0 and a > 0.2:
        return "medium"
    return "low"


def _is_urgent(a: float) -> bool:
    """Urgency reads off the arousal axis regardless of valence."""
    return a > 0.6


def snapshot(system: Optional[EmotionSystem] = None) -> dict:
    """
    Full sensor-state snapshot for downstream consumers.

    Returns a dict with:
      pad          {P, A, D}                aggregated PAD, authentic sensors only
      octa         {state, label, phi_coherence}   system octahedral state
      coherence    float in [0, 1]          global resonance-graph coherence
      activations  {name: E}                per-sensor E for authentic active sensors
      corrupted    [name, ...]              sensors failing the authenticity gate
      stress_level 'low' | 'medium' | 'high'   derived from PAD
      urgent       bool                     derived from PAD arousal
      time         float                    EmotionSystem.time at capture

    The whole dict is safe to pass as `sensor_snapshot=`; downstream
    resolvers that only accept the summary can pull
    `{stress_level, urgent}` out.
    """
    sys_ = system if system is not None else _get_default_system()

    octa = sys_.system_octa_state()
    p = octa["pad"]["P"]
    a = octa["pad"]["A"]

    activations: dict = {}
    corrupted: list = []
    for s in sys_.sensors:
        if not s.authentic:
            corrupted.append(s.name)
            continue
        if s.E > 0.01:
            activations[s.name] = round(s.E, 4)

    return {
        "pad": octa["pad"],
        "octa": {
            "state": octa["state"],
            "label": octa["label"],
            "phi_coherence": octa["phi_coherence"],
        },
        "coherence": round(sys_.coherence(), 4),
        "activations": activations,
        "corrupted": corrupted,
        "stress_level": _classify_stress(p, a),
        "urgent": _is_urgent(a),
        "time": sys_.time,
    }


__all__ = ["snapshot", "reset_default_system", "EmotionSystem"]
