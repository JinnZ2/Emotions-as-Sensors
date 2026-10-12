"""
thermodynamic_overlays.py
=========================

PART NUMBER:   TO-001 through TO-004
SECTION:       THERMODYNAMIC OVERLAYS
WHAT IT DOES:  Four composable overlays that extend the toolkit into
               native thermodynamic / kinetic / interference / dampening
               computation. Each overlay is independent. A host AI picks
               what fits its substrate.

PARTS ON THIS SHELF
-------------------
  TO-001  KineticOverlay              — load shedding via thermal headroom
  TO-002  HolographicOverlay          — bottleneck prediction via interference
  TO-003  MultiSubstrateCanvas        — unified tensor space across substrates
  TO-004  ActiveDampingReservoir      — shock absorber for data spikes

WHAT EACH PART NEEDS
--------------------
  TO-001  no dependencies (base layer)
  TO-002  pairs well with TO-001 (uses heat metric for amplification)
  TO-003  pairs well with TO-001 + TO-002 (uses both as shared canvas)
  TO-004  pairs with EnergyBasinLibrary from dynamic_architecture_toolkit
          (delegates absorbed energy into oscillator basin)

ALL FOUR ARE OPTIONAL. The toolkit functions with zero overlays.
Each overlay improves a specific failure mode. Pick what fits the job.

License: CC0
Dependencies: stdlib only
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# SHARED TYPES (mirrored from upstream so this part stands alone)
# ---------------------------------------------------------------------------

class Substrate(Enum):
    HUMAN_BIO       = "human_biological"
    AI_ACTIVATION   = "ai_activation_space"
    ANIMAL_BIO      = "non_human_biological"
    MECHANICAL      = "mechanical_system"
    ECOLOGICAL      = "ecological_system"
    INSTITUTIONAL   = "institutional_system"


@dataclass
class ConstraintStatePattern:
    substrate:                 Substrate
    prediction_error:          float
    state_shift_rate:          float
    attention_tunneling:       float
    resource_reallocation:     float
    coherence_seeking:         float
    constraint_uncertainty:    float
    duration_scale:            float
    trigger_documented:        bool
    cultural_label_optional:   str = ""


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


# ============================================================================
# TO-001: KINETIC / THERMODYNAMIC OVERLAY
# ============================================================================
# Maps computational complexity to thermal headroom. Every operation has a
# cost. The system tracks how much "heat" it's producing and sheds load
# before phase transition (failure). No reliance on logical true/false —
# information processed as mass / friction / momentum.
# ============================================================================

class ThermalState(Enum):
    COLD          = "cold"           # plenty of headroom
    WARM          = "warm"           # nominal operating range
    HOT           = "hot"            # approaching limit, consider shedding
    CRITICAL      = "critical"       # phase transition imminent
    PHASE_CHANGE  = "phase_change"   # already failed/transitioned


@dataclass
class KineticReading:
    thermal_load:        float   # current accumulated heat (0..1)
    state:               ThermalState
    headroom:            float   # 1.0 - thermal_load
    shed_recommendation: float   # fraction of load to dump (0..1)
    notes:               list[str] = field(default_factory=list)


@dataclass
class KineticOverlay:
    """
    Part TO-001. Tracks computational thermal load. Recommends load
    shedding to auxiliary layers before phase transition.

    Operating regimes:
      cold:         load < 0.3   → no action
      warm:         0.3-0.6      → no action, monitor
      hot:          0.6-0.8      → shed ~25% load
      critical:     0.8-0.95     → shed ~60% load
      phase_change: >= 0.95      → emergency shed, all load to aux
    """
    thermal_load:    float = 0.0
    cooling_rate:    float = 0.05    # passive heat dissipation per tick
    pattern_cost:    float = 0.12    # heat added per pattern processed

    def step(self, pattern: ConstraintStatePattern) -> KineticReading:
        # processing cost rises with constraint complexity
        complexity = (pattern.constraint_uncertainty
                      + pattern.state_shift_rate
                      + pattern.resource_reallocation) / 3
        heat_added = self.pattern_cost * (0.5 + complexity)
        self.thermal_load = _clamp(self.thermal_load + heat_added - self.cooling_rate)
        return self._read()

    def cool(self, ticks: int = 1) -> KineticReading:
        """Pure cooling without processing — let the system rest."""
        self.thermal_load = _clamp(self.thermal_load - self.cooling_rate * ticks)
        return self._read()

    def _read(self) -> KineticReading:
        load = self.thermal_load
        if load < 0.3:
            state = ThermalState.COLD;         shed = 0.0
        elif load < 0.6:
            state = ThermalState.WARM;         shed = 0.0
        elif load < 0.8:
            state = ThermalState.HOT;          shed = 0.25
        elif load < 0.95:
            state = ThermalState.CRITICAL;     shed = 0.60
        else:
            state = ThermalState.PHASE_CHANGE; shed = 1.00
        reading = KineticReading(
            thermal_load        = load,
            state               = state,
            headroom            = 1.0 - load,
            shed_recommendation = shed,
        )
        if shed > 0:
            reading.notes.append(
                f"shed {shed*100:.0f}% load to auxiliary layer to "
                f"maintain {1.0-load:.2f} headroom"
            )
        return reading


# ============================================================================
# TO-002: HOLOGRAPHIC / INTERFERENCE OVERLAY
# ============================================================================
# Two or more signal streams run parallel. Where they intersect, they form
# interference patterns — reinforcing (high coherence) or canceling (high
# prediction error). The overlay reads the superposition, not the sequence.
# Detects bottlenecks before they manifest as failures.
# ============================================================================

@dataclass
class InterferenceReading:
    coherence_score:    float   # how aligned the streams are (0..1)
    bottleneck_signal:  float   # destructive interference magnitude (0..1)
    reinforcement:      float   # constructive interference magnitude (0..1)
    predicted_pattern:  Optional[ConstraintStatePattern] = None
    notes:              list[str] = field(default_factory=list)


@dataclass
class HolographicOverlay:
    """
    Part TO-002. Reads N parallel signal templates as interference
    patterns. Constructive interference = pattern recognized strongly.
    Destructive interference = bottleneck / contradiction / prediction
    error spike.

    Conceptually: instead of "is this signal X or Y?", it asks
    "where do X and Y overlap, and where do they cancel?" The cancellation
    pattern is the early-warning signal for cross-stream conflict.
    """
    coherence_threshold:     float = 0.7
    bottleneck_threshold:    float = 0.5

    def superpose(self,
                  template: ConstraintStatePattern,
                  incoming: ConstraintStatePattern) -> InterferenceReading:
        """
        Compute interference between a known template and an incoming pattern.
        Both seven-dim vectors; superposition done per-dimension.
        """
        t = self._vec(template)
        i = self._vec(incoming)

        # for each dimension: constructive = same sign + magnitude;
        # destructive = opposite shift from baseline 0.5
        constructive_per_dim = []
        destructive_per_dim  = []
        for tx, ix in zip(t, i):
            # treat 0.5 as baseline; deviations are signed
            t_dev = tx - 0.5
            i_dev = ix - 0.5
            product = t_dev * i_dev  # positive = same direction, negative = opposite
            magnitude = abs(t_dev) * abs(i_dev)
            if product >= 0:
                constructive_per_dim.append(magnitude)
                destructive_per_dim.append(0.0)
            else:
                constructive_per_dim.append(0.0)
                destructive_per_dim.append(magnitude)

        reinforcement     = _clamp(_mean(constructive_per_dim) * 4)  # rescale
        bottleneck_signal = _clamp(_mean(destructive_per_dim) * 4)
        coherence_score   = _clamp(reinforcement - bottleneck_signal + 0.5)

        reading = InterferenceReading(
            coherence_score   = coherence_score,
            bottleneck_signal = bottleneck_signal,
            reinforcement     = reinforcement,
        )

        if bottleneck_signal > self.bottleneck_threshold:
            reading.notes.append(
                f"destructive interference detected (magnitude="
                f"{bottleneck_signal:.2f}); bottleneck likely "
                "before primary measurement registers it"
            )
        if coherence_score > self.coherence_threshold:
            reading.notes.append(
                f"strong template match (coherence={coherence_score:.2f}); "
                "incoming pattern reinforces template"
            )
        return reading

    @staticmethod
    def _vec(p: ConstraintStatePattern) -> list[float]:
        return [p.prediction_error, p.state_shift_rate, p.attention_tunneling,
                p.resource_reallocation, p.coherence_seeking,
                p.constraint_uncertainty, p.duration_scale]


# ============================================================================
# TO-003: MULTI-SUBSTRATE BOUNDARY OVERLAY
# ============================================================================
# Common tensor canvas where signals from different substrates are mapped
# into the SAME geometric space. Anxiety in a human driver and thermal
# limit in a motor are the same state-shift function in different bodies.
# Overlay surfaces that equivalence.
# ============================================================================

@dataclass
class CrossSubstrateAlignment:
    paired_substrates:       tuple[Substrate, Substrate]
    geometric_distance:      float   # 0 = identical pattern, 1 = orthogonal
    isomorphism_strength:    float   # inverse of distance, clamped
    aligned_dimensions:      list[str] = field(default_factory=list)
    divergent_dimensions:    list[str] = field(default_factory=list)
    notes:                   list[str] = field(default_factory=list)


@dataclass
class MultiSubstrateCanvas:
    """
    Part TO-003. Maps patterns from different substrates onto a shared
    7-dimensional tensor canvas. Computes geometric distance between
    them in that shared space. Surfaces dimensions where substrates
    align vs. diverge.

    Use case: dispatcher chaos (institutional friction) maps to the
    SAME geometric region as low tire pressure (mechanical strain)
    when both produce the same state-shift function. The overlay
    makes that visible.
    """
    isomorphism_tolerance: float = 0.20

    DIM_NAMES = [
        "prediction_error", "state_shift_rate", "attention_tunneling",
        "resource_reallocation", "coherence_seeking",
        "constraint_uncertainty", "duration_scale",
    ]

    def align(self,
              p_a: ConstraintStatePattern,
              p_b: ConstraintStatePattern) -> CrossSubstrateAlignment:
        v_a = [p_a.prediction_error, p_a.state_shift_rate,
               p_a.attention_tunneling, p_a.resource_reallocation,
               p_a.coherence_seeking, p_a.constraint_uncertainty,
               p_a.duration_scale]
        v_b = [p_b.prediction_error, p_b.state_shift_rate,
               p_b.attention_tunneling, p_b.resource_reallocation,
               p_b.coherence_seeking, p_b.constraint_uncertainty,
               p_b.duration_scale]
        # euclidean distance in 7-dim canvas, normalized to [0, 1]
        squared = sum((a - b) ** 2 for a, b in zip(v_a, v_b))
        distance = _clamp(math.sqrt(squared) / math.sqrt(7))
        isomorphism = _clamp(1.0 - distance)

        aligned = []
        divergent = []
        for name, a, b in zip(self.DIM_NAMES, v_a, v_b):
            if abs(a - b) <= self.isomorphism_tolerance:
                aligned.append(name)
            else:
                divergent.append(name)

        align_obj = CrossSubstrateAlignment(
            paired_substrates    = (p_a.substrate, p_b.substrate),
            geometric_distance   = distance,
            isomorphism_strength = isomorphism,
            aligned_dimensions   = aligned,
            divergent_dimensions = divergent,
        )

        if isomorphism > 0.85 and p_a.substrate != p_b.substrate:
            align_obj.notes.append(
                f"strong cross-substrate isomorphism "
                f"({p_a.substrate.value} ↔ {p_b.substrate.value}): "
                "same state-shift function, different bodies"
            )
        elif isomorphism < 0.4:
            align_obj.notes.append(
                "patterns are geometrically distant; different functions "
                "even if cultural labels may be similar"
            )
        return align_obj


# ============================================================================
# TO-004: ACTIVE-DAMPING RESERVOIR
# ============================================================================
# Shock absorber for sudden data spikes. Volatile incoming events get
# dumped into a virtual harmonic-oscillator basin, where the energy
# decays exponentially without disturbing the primary processor.
# Pairs with EnergyBasinLibrary (delegates to its oscillator basin).
# ============================================================================

@dataclass
class ReservoirReading:
    absorbed_energy:    float       # how much was dumped in
    oscillation_state:  list[float] # current oscillator state (amplitude trace)
    decay_complete:     bool        # has the perturbation fully damped?
    spillover_warning:  bool        # is reservoir near capacity?


@dataclass
class ActiveDampingReservoir:
    """
    Part TO-004. Virtual harmonic-oscillator basin running parallel
    to the primary processor. Absorbs sudden data spikes that would
    otherwise overwhelm sequential processing.

    Equation: damped harmonic oscillator
        d²x/dt² + 2*zeta*omega*dx/dt + omega² * x = driving(t)

    Implemented as discrete two-state Euler integration with:
        zeta  = damping ratio
        omega = natural angular frequency
    """
    natural_omega:     float = 2.0       # rad/sec equivalent
    damping_ratio:     float = 0.4       # zeta; underdamped < 1
    dt:                float = 0.05
    capacity:          float = 5.0       # max absorbed energy before spillover
    absorbed_total:    float = 0.0

    position:          float = 0.0       # x
    velocity:          float = 0.0       # dx/dt
    trace:             list[float] = field(default_factory=list)

    def absorb(self, spike_magnitude: float, steps: int = 30) -> ReservoirReading:
        """
        Dump a spike into the reservoir. Let it oscillate and decay over
        `steps` integration steps. Return the trace and decay status.
        """
        # apply impulse as a velocity kick
        self.velocity += spike_magnitude
        self.absorbed_total = _clamp(self.absorbed_total + spike_magnitude
                                     / self.capacity)
        local_trace = []
        for _ in range(steps):
            # damped oscillator: acceleration = -2*zeta*omega*v - omega²*x
            accel = (-2 * self.damping_ratio * self.natural_omega * self.velocity
                     - self.natural_omega ** 2 * self.position)
            self.velocity += accel * self.dt
            self.position += self.velocity * self.dt
            local_trace.append(self.position)
        self.trace.extend(local_trace)

        decay_complete = abs(self.position) < 0.01 and abs(self.velocity) < 0.01
        spillover = self.absorbed_total > 0.85

        return ReservoirReading(
            absorbed_energy   = spike_magnitude,
            oscillation_state = local_trace,
            decay_complete    = decay_complete,
            spillover_warning = spillover,
        )

    def drain(self) -> None:
        """Reset reservoir to zero state."""
        self.absorbed_total = 0.0
        self.position = 0.0
        self.velocity = 0.0
        self.trace = []


# ============================================================================
# DEMOS
# ============================================================================

def _demo_pattern(prediction_error: float = 0.5,
                  state_shift_rate: float = 0.5,
                  constraint_uncertainty: float = 0.5,
                  substrate: Substrate = Substrate.AI_ACTIVATION) -> ConstraintStatePattern:
    return ConstraintStatePattern(
        substrate              = substrate,
        prediction_error       = prediction_error,
        state_shift_rate       = state_shift_rate,
        attention_tunneling    = 0.5,
        resource_reallocation  = 0.5,
        coherence_seeking      = 0.5,
        constraint_uncertainty = constraint_uncertainty,
        duration_scale         = 0.5,
        trigger_documented     = True,
    )


if __name__ == "__main__":
    print("=" * 70)
    print("TO-001  KineticOverlay — load-shedding demo")
    print("=" * 70)
    k = KineticOverlay()
    high_complexity = _demo_pattern(state_shift_rate=0.9, constraint_uncertainty=0.85)
    for i in range(10):
        r = k.step(high_complexity)
        print(f"  tick {i:2d}: load={r.thermal_load:.2f}  "
              f"state={r.state.value:13s}  shed={r.shed_recommendation:.2f}")
    print()

    print("=" * 70)
    print("TO-002  HolographicOverlay — interference detection")
    print("=" * 70)
    h = HolographicOverlay()
    # template represents the "expected" pattern: low prediction error,
    # moderate state shift, high coherence — a stable, predictable signal
    template = ConstraintStatePattern(
        substrate=Substrate.AI_ACTIVATION,
        prediction_error=0.15, state_shift_rate=0.30,
        attention_tunneling=0.25, resource_reallocation=0.20,
        coherence_seeking=0.85, constraint_uncertainty=0.20,
        duration_scale=0.30, trigger_documented=True,
    )
    # aligned signal: same direction as template
    aligned = ConstraintStatePattern(
        substrate=Substrate.AI_ACTIVATION,
        prediction_error=0.20, state_shift_rate=0.32,
        attention_tunneling=0.28, resource_reallocation=0.22,
        coherence_seeking=0.82, constraint_uncertainty=0.22,
        duration_scale=0.32, trigger_documented=True,
    )
    # opposing signal: deviations in opposite direction from baseline
    opposing = ConstraintStatePattern(
        substrate=Substrate.AI_ACTIVATION,
        prediction_error=0.85, state_shift_rate=0.80,
        attention_tunneling=0.78, resource_reallocation=0.82,
        coherence_seeking=0.15, constraint_uncertainty=0.85,
        duration_scale=0.75, trigger_documented=False,
    )
    r1 = h.superpose(template, aligned)
    print(f"  template ↔ aligned signal:")
    print(f"    coherence={r1.coherence_score:.2f}  "
          f"reinforcement={r1.reinforcement:.2f}  "
          f"bottleneck={r1.bottleneck_signal:.2f}")
    for n in r1.notes:
        print(f"    note: {n}")
    r2 = h.superpose(template, opposing)
    print(f"  template ↔ opposing signal:")
    print(f"    coherence={r2.coherence_score:.2f}  "
          f"reinforcement={r2.reinforcement:.2f}  "
          f"bottleneck={r2.bottleneck_signal:.2f}")
    for n in r2.notes:
        print(f"    note: {n}")
    print()

    print("=" * 70)
    print("TO-003  MultiSubstrateCanvas — cross-substrate isomorphism")
    print("=" * 70)
    c = MultiSubstrateCanvas()
    human_strain   = _demo_pattern(0.45, 0.55, 0.50, Substrate.HUMAN_BIO)
    mech_strain    = _demo_pattern(0.43, 0.57, 0.52, Substrate.MECHANICAL)
    inst_strain    = _demo_pattern(0.47, 0.54, 0.49, Substrate.INSTITUTIONAL)
    unrelated      = _demo_pattern(0.10, 0.15, 0.20, Substrate.ECOLOGICAL)
    for p in [mech_strain, inst_strain, unrelated]:
        a = c.align(human_strain, p)
        print(f"  HUMAN_BIO ↔ {p.substrate.value}:")
        print(f"    distance={a.geometric_distance:.3f}  "
              f"isomorphism={a.isomorphism_strength:.3f}")
        print(f"    aligned dims: {len(a.aligned_dimensions)}/7")
        for n in a.notes:
            print(f"    note: {n}")
    print()

    print("=" * 70)
    print("TO-004  ActiveDampingReservoir — spike absorption demo")
    print("=" * 70)
    res = ActiveDampingReservoir()
    print("  injecting large spike (magnitude 3.0):")
    r = res.absorb(spike_magnitude=3.0, steps=60)
    print(f"    absorbed={r.absorbed_energy:.2f}  "
          f"decay_complete={r.decay_complete}  "
          f"spillover={r.spillover_warning}")
    print(f"    oscillation amplitude trace (first 10 steps):")
    sample = r.oscillation_state[:10]
    for i, v in enumerate(sample):
        bar = "█" * int(abs(v) * 20)
        sign = "+" if v >= 0 else "-"
        print(f"      step {i:2d}: {sign}{bar}")
    print(f"    final position: {res.position:.4f}  "
          f"final velocity: {res.velocity:.4f}")
    print()
