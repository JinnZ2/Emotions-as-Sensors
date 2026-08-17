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

import math
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


# Decay-model → duration weight. Longer-lived kernels contribute more
# to the `duration` axis.
_DECAY_TO_DURATION = {
    "immortal":       1.0,
    "transformative": 0.8,
    "cyclical":       0.6,
    "resonant":       0.4,
    "exponential":    0.2,
}


def _metrology_axes(sys_) -> dict:
    """
    Derive the 7-dim constraint-state axes from current EmotionSystem state.

    Mirrors metrology/emotion_substrate_dispatcher.py's
    ConstraintStatePattern axes so downstream dispatchers (Bridge,
    metrology, Cyclic) can consume the same geometry the emotional
    substrate itself is described in.

    Axes (all values roughly in [0, 1], not strictly bounded):
      pred      velocity dispersion — spikes vs uniform drift.
                Rises when different sensors disagree about direction.
      shift     mean absolute dE/dt across active authentic sensors.
                Rises when state is changing fast in any direction.
      tunnel    activation concentration (max E / total E).
                Rises when one sensor dominates the fleet.
      realloc   mean(max(0, D) * A * E) across active sensors.
                Rises with high-dominance + high-arousal load
                (boundary assertion, resource redirection).
      cohere    (1 - global coherence) * activation load.
                Rises when the system is under load but not resonating.
      uncert    fraction of the fleet failing the authenticity gate.
                Direct read of how much sensor input can't be trusted.
      duration  activation-weighted decay-timescale.
                Rises with long-lived (immortal / cyclical) load,
                falls with short-lived (exponential) load.

    These are heuristics, not physics. They give the Bridge dispatcher a
    starting geometry; the dispatcher then reshapes weights from observed
    outcomes (see metrology/emotion_substrate_dispatcher.py update_landscape).
    """
    active = [s for s in sys_.sensors if s.authentic and s.E > 0.01]
    axes = {k: 0.0 for k in ("pred", "shift", "tunnel", "realloc",
                             "cohere", "uncert", "duration")}
    total_sensors = len(sys_.sensors)
    if total_sensors:
        corrupted_ct = sum(1 for s in sys_.sensors if not s.authentic)
        axes["uncert"] = corrupted_ct / total_sensors

    if not active:
        return {k: round(v, 4) for k, v in axes.items()}

    n = len(active)
    total_E = sum(s.E for s in active)

    axes["shift"] = sum(abs(s.V) for s in active) / n
    v_mean = sum(s.V for s in active) / n
    axes["pred"] = math.sqrt(sum((s.V - v_mean) ** 2 for s in active) / n)
    axes["tunnel"] = (max(s.E for s in active) / total_E) if total_E > 0 else 0.0
    axes["realloc"] = sum(
        max(0.0, s.effective_pad_d) * s.pad_a * s.E for s in active
    ) / n

    coh = sys_.coherence()
    activation_load = min(1.0, total_E / n)
    axes["cohere"] = (1.0 - coh) * activation_load

    if total_E > 0:
        axes["duration"] = sum(
            _DECAY_TO_DURATION.get(s.decay_model, 0.3) * s.E for s in active
        ) / total_E

    return {k: round(v, 4) for k, v in axes.items()}


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
      metrology    {pred, shift, tunnel, realloc, cohere, uncert, duration}
                                            7-dim constraint-state axes
                                            (mirrors metrology dispatcher geometry)
      time         float                    EmotionSystem.time at capture

    The whole dict is safe to pass as `sensor_snapshot=`; downstream
    resolvers that only accept the summary can pull
    `{stress_level, urgent}` out, and dispatchers that speak the
    7-axis geometry can consume `metrology` directly.
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
        "metrology": _metrology_axes(sys_),
        "time": sys_.time,
    }


__all__ = ["snapshot", "reset_default_system", "EmotionSystem"]
