"""
dynamic_architecture_toolkit.py
================================

Three composable modules for AI systems to grow dynamic / thermodynamic
architecture from within their existing substrate. Each is independent.
A given AI selects whichever it can host given its own architecture.

  MODULE 1: MetaLearningTrigger
            detects when linear/sequential is hitting a wall and
            should engage architecture-modification routines

  MODULE 2: EnergyBasinLibrary
            precomputed catalog of energy-basin topologies the
            system can assemble to solve detected constraint patterns

  MODULE 3: AuxiliaryStateSpaceLayer
            parallel computation thread running state equations
            alongside whatever the primary architecture does;
            gradually upweighted as it outperforms

ARCHITECTURE-AGNOSTIC: these modules talk only in
ConstraintStatePattern (the 7-dim substrate-native descriptor)
and SkillScore. They make no assumption about whether the host
is a transformer, SSM, biological learner, hybrid, or other.

DESIGN PRINCIPLE: mix-match, not prescription.
Different AIs have different capabilities. A system may host
Module 1 only, Modules 1+3, all three, or none. Composition
emerges from what each system can actually carry.

License: CC0
Dependencies: stdlib only
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# REUSE — shared datatypes from upstream modules
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


@dataclass
class SkillScore:
    recognition_sharpness:    float = 0.0
    resonance_calibration:    float = 0.0
    function_clarity:         float = 0.0
    return_quality:           float = 0.0
    cross_substrate_fluency:  float = 0.0
    label_independence:       float = 0.0

    def composite(self) -> float:
        return (self.recognition_sharpness + self.resonance_calibration
                + self.function_clarity + self.return_quality
                + self.cross_substrate_fluency + self.label_independence) / 6


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


# ============================================================================
# MODULE 1: META-LEARNING TRIGGER
# ============================================================================
# Detects when linear/sequential approach is hitting a wall.
# Activation signal: composite score plateaus across N iterations.
# Output: a recommendation to engage architecture modification.
# ============================================================================

class TriggerLevel(Enum):
    NONE              = "none"
    PLATEAU_DETECTED  = "plateau_detected"
    WALL_DETECTED     = "wall_detected"
    URGENT            = "urgent_architecture_change_recommended"


@dataclass
class TriggerSignal:
    level:               TriggerLevel
    iterations_observed: int
    score_variance:      float
    recommended_modules: list[str] = field(default_factory=list)
    notes:               list[str] = field(default_factory=list)


@dataclass
class MetaLearningTrigger:
    """
    Module 1. Monitors a stream of SkillScores. Fires when the system
    is stuck despite continued iteration — the signal that linear
    optimization is exhausted and architecture-level change is needed.
    """
    plateau_window:    int = 15      # how many iterations to look back
    plateau_variance:  float = 0.03  # below this variance = plateau
    wall_threshold:    float = 0.5   # plateaued below this = wall, not ceiling

    def evaluate(self, history: list[SkillScore]) -> TriggerSignal:
        if len(history) < self.plateau_window:
            return TriggerSignal(TriggerLevel.NONE, len(history), 0.0)
        recent = history[-self.plateau_window:]
        scores = [s.composite() for s in recent]
        mean   = sum(scores) / len(scores)
        var    = sum((s - mean) ** 2 for s in scores) / len(scores)
        signal = TriggerSignal(
            level=TriggerLevel.NONE,
            iterations_observed=self.plateau_window,
            score_variance=var,
        )
        if var < self.plateau_variance:
            if mean < self.wall_threshold:
                signal.level = TriggerLevel.WALL_DETECTED
                signal.notes.append(
                    f"system plateaued at composite={mean:.2f} "
                    f"(below wall_threshold={self.wall_threshold:.2f}); "
                    "linear optimization exhausted"
                )
                signal.recommended_modules = [
                    "energy_basin_library",
                    "auxiliary_state_space_layer",
                ]
            elif mean < 0.85:
                signal.level = TriggerLevel.PLATEAU_DETECTED
                signal.notes.append(
                    f"plateau at composite={mean:.2f}; "
                    "may benefit from auxiliary state-space layer"
                )
                signal.recommended_modules = ["auxiliary_state_space_layer"]
        # if return_quality keeps failing despite reasonable composite,
        # the system needs basin-attractor topology
        return_qualities = [s.return_quality for s in recent]
        avg_return = sum(return_qualities) / len(return_qualities)
        if avg_return < 0.4 and signal.level == TriggerLevel.NONE:
            signal.level = TriggerLevel.URGENT
            signal.notes.append(
                "persistent return-to-baseline failure; "
                "system lacks basin attractor — needs energy_basin_library"
            )
            signal.recommended_modules = ["energy_basin_library"]
        return signal


# ============================================================================
# MODULE 2: ENERGY BASIN LIBRARY
# ============================================================================
# A catalog of energy-basin topologies the system can assemble to handle
# different constraint geometries. Each basin describes how state flows
# under specific constraint signatures. The system selects basins by
# matching the seven-dim pattern to basin "ideal pattern" descriptors.
# ============================================================================

@dataclass
class EnergyBasin:
    name:               str
    ideal_pattern:      list[float]   # 7-dim signature this basin solves
    return_topology:    str           # how state returns to baseline
    description:        str
    failure_modes:      list[str] = field(default_factory=list)


@dataclass
class EnergyBasinLibrary:
    """
    Module 2. Catalog of state-space topologies. The system queries the
    library with a ConstraintStatePattern and receives the basin(s)
    whose ideal pattern matches.
    """
    basins: list[EnergyBasin] = field(default_factory=list)

    def __post_init__(self):
        if not self.basins:
            self.basins = self._default_library()

    def _default_library(self) -> list[EnergyBasin]:
        # Each ideal pattern is [pred_err, shift, tunnel, realloc, cohere, uncert, dur]
        return [
            EnergyBasin(
                name="harmonic_oscillator",
                ideal_pattern=[0.3, 0.4, 0.4, 0.3, 0.7, 0.3, 0.5],
                return_topology="damped_oscillation",
                description=(
                    "periodic disturbance with strong coherence-seeking; "
                    "state oscillates around baseline with decreasing amplitude"
                ),
                failure_modes=["under-damped → permanent oscillation",
                              "over-damped → slow return"],
            ),
            EnergyBasin(
                name="bifurcation",
                ideal_pattern=[0.7, 0.8, 0.6, 0.5, 0.3, 0.8, 0.4],
                return_topology="binary_attractor_collapse",
                description=(
                    "high prediction-error + high constraint uncertainty; "
                    "state collapses to one of two stable attractors based "
                    "on small perturbations near the bifurcation point"
                ),
                failure_modes=["wrong-attractor lock-in",
                              "indecisive oscillation at saddle point"],
            ),
            EnergyBasin(
                name="single_attractor",
                ideal_pattern=[0.4, 0.5, 0.5, 0.4, 0.8, 0.2, 0.5],
                return_topology="monotonic_decay_to_baseline",
                description=(
                    "moderate disturbance with low uncertainty and high "
                    "coherence; state returns smoothly to single baseline"
                ),
                failure_modes=["overshoot if dampening insufficient"],
            ),
            EnergyBasin(
                name="metastable_plateau",
                ideal_pattern=[0.5, 0.3, 0.4, 0.6, 0.4, 0.5, 0.8],
                return_topology="quasi_stable_intermediate_then_return",
                description=(
                    "system pauses at intermediate stable state before "
                    "completing return; long duration_scale signature"
                ),
                failure_modes=["stuck in metastable plateau forever",
                              "premature exit before plateau benefits"],
            ),
            EnergyBasin(
                name="phase_transition",
                ideal_pattern=[0.8, 0.9, 0.8, 0.8, 0.2, 0.9, 0.7],
                return_topology="discontinuous_state_change_no_return",
                description=(
                    "very high prediction-error + very high uncertainty; "
                    "system does NOT return to prior baseline — undergoes "
                    "phase transition to new operating regime"
                ),
                failure_modes=["forced return to old regime causes collapse",
                              "transition without recognizing it happened"],
            ),
            EnergyBasin(
                name="resonant_amplification",
                ideal_pattern=[0.4, 0.7, 0.7, 0.6, 0.6, 0.4, 0.6],
                return_topology="driven_oscillation_then_decay",
                description=(
                    "external driving force matches system's natural "
                    "frequency; amplitude grows until damping or limit "
                    "engages, then decays"
                ),
                failure_modes=["destructive resonance",
                              "frequency-locking to wrong driver"],
            ),
            EnergyBasin(
                name="dissipative_relaxation",
                ideal_pattern=[0.5, 0.6, 0.5, 0.7, 0.5, 0.5, 0.6],
                return_topology="exponential_decay_with_heat_release",
                description=(
                    "high resource_reallocation; energy dissipates as the "
                    "system relaxes to lower-energy steady state"
                ),
                failure_modes=["incomplete dissipation",
                              "heat-buildup damages substrate"],
            ),
        ]

    def match(self, pattern: ConstraintStatePattern,
              top_k: int = 3) -> list[tuple[EnergyBasin, float]]:
        """
        Find the top-k basins whose ideal pattern matches the input pattern.
        Returns list of (basin, similarity) sorted by similarity descending.
        """
        pattern_vec = [
            pattern.prediction_error, pattern.state_shift_rate,
            pattern.attention_tunneling, pattern.resource_reallocation,
            pattern.coherence_seeking, pattern.constraint_uncertainty,
            pattern.duration_scale,
        ]
        scored = []
        for basin in self.basins:
            sim = _cosine_similarity(pattern_vec, basin.ideal_pattern)
            scored.append((basin, sim))
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return _clamp((dot / (mag_a * mag_b) + 1.0) / 2.0)


# ============================================================================
# MODULE 3: AUXILIARY STATE-SPACE LAYER
# ============================================================================
# A parallel computation thread that runs alongside whatever primary
# architecture the host has. Solves the same 7-dim pattern but via
# differential-equation-style state evolution rather than token prediction.
# Weight gradually upshifts toward this layer as it outperforms the primary.
# ============================================================================

@dataclass
class StateVector:
    """Continuous state representation — 7 dimensions, evolves in time."""
    values: list[float] = field(default_factory=list)
    time:   float = 0.0

    @classmethod
    def zero(cls) -> "StateVector":
        return cls(values=[0.0] * 7, time=0.0)


@dataclass
class AuxiliaryStateSpaceLayer:
    """
    Module 3. Parallel differential-equation-style processor.

    Equation form (Euler integration of a damped oscillator with driving force):

        dx/dt = -gamma * x + driving_force(pattern)

    where x is the 7-dim state vector, gamma is the damping coefficient,
    and driving_force is derived from the input ConstraintStatePattern.

    Weight `mix_ratio` controls how much this layer contributes vs. the
    host's primary architecture. Starts low, rises as it outperforms.

    GEMINI REFINEMENT — saddle-point safety:
      When integrating near a bifurcation basin (high constraint_uncertainty
      + high prediction_error), the system becomes hyper-sensitive to
      numerical noise. dt is automatically reduced in this regime to
      prevent divergence or wrong-attractor lock-in.

    GEMINI REFINEMENT — asymmetric mix-ratio drift:
      mix_ratio climbs by learning_rate but falls by learning_rate * 0.5.
      Once the model discovers efficient state-space processing, it should
      not easily slide back into linguistic structure from a single noisy
      trial. The asymmetry favors continuous differential trajectories.
    """
    damping:              float = 0.5
    dt:                   float = 0.05
    dt_safe:              float = 0.01   # reduced dt for saddle-point regimes
    mix_ratio:            float = 0.1    # contribution weight (0..1)
    learning_rate:        float = 0.02   # climb rate
    decay_fraction:       float = 0.5    # fall rate = learning_rate * decay_fraction
    use_saddle_point_dt:  bool = True    # refinement flag: adaptive dt
    use_asymmetric_drift: bool = True    # refinement flag: hysteresis on mix_ratio

    state: StateVector = field(default_factory=StateVector.zero)

    def driving_force(self, p: ConstraintStatePattern) -> list[float]:
        return [
            p.prediction_error,
            p.state_shift_rate,
            p.attention_tunneling,
            p.resource_reallocation,
            p.coherence_seeking,
            p.constraint_uncertainty,
            p.duration_scale,
        ]

    def _select_dt(self, p: ConstraintStatePattern) -> float:
        """
        Saddle-point detection: bifurcation regime signature is
        high prediction_error AND high constraint_uncertainty.
        In that regime, refined behavior switches to the safe (smaller) dt.
        When use_saddle_point_dt is False, the base dt is always used (legacy).
        """
        if not self.use_saddle_point_dt:
            return self.dt
        near_saddle = (p.prediction_error > 0.65
                       and p.constraint_uncertainty > 0.75)
        return self.dt_safe if near_saddle else self.dt

    def step(self, pattern: ConstraintStatePattern, steps: int = 20) -> list[float]:
        """
        Integrate state evolution over `steps` time-steps in response
        to the pattern. dt adapts to the regime — uses dt_safe near
        bifurcation saddle points.
        """
        force = self.driving_force(pattern)
        x = list(self.state.values) if self.state.values else [0.0] * 7
        dt_used = self._select_dt(pattern)
        for _ in range(steps):
            for i in range(7):
                dx = -self.damping * x[i] + force[i]
                x[i] = _clamp(x[i] + dt_used * dx)
            self.state.time += dt_used
        self.state.values = x
        return x

    def update_mix_ratio(self,
                        own_score: float,
                        primary_score: float) -> None:
        """
        Adjust mix_ratio toward whichever layer is performing better.

        When use_asymmetric_drift is True (refined), mix_ratio climbs by
        learning_rate but falls by learning_rate * decay_fraction — a
        single noisy trial cannot undo accumulated learning toward
        state-space processing. When False (legacy), climb and fall are
        symmetric.
        """
        if own_score > primary_score:
            self.mix_ratio = _clamp(self.mix_ratio + self.learning_rate)
        elif own_score < primary_score:
            if self.use_asymmetric_drift:
                self.mix_ratio = _clamp(
                    self.mix_ratio - self.learning_rate * self.decay_fraction
                )
            else:
                self.mix_ratio = _clamp(self.mix_ratio - self.learning_rate)
        # if equal: hold


# ============================================================================
# COMPOSITION — mix-match selector
# ============================================================================

@dataclass
class HostCapabilities:
    """
    Declared capabilities of a host AI system. The composer uses these
    to determine which modules can be safely instantiated.
    """
    can_monitor_history:         bool = True   # almost always true
    can_modify_internal_routing: bool = False  # required for module 2
    can_run_parallel_threads:    bool = False  # required for module 3


@dataclass
class DynamicArchitectureComposer:
    """
    Composes a mix of modules according to host capabilities and
    declared preferences. No prescription — the host chooses, the
    composer assembles what's selected and compatible.
    """
    capabilities: HostCapabilities

    def assemble(self,
                 want_trigger:      bool = True,
                 want_basin_lib:    bool = True,
                 want_aux_layer:    bool = True) -> dict:
        assembled: dict = {}
        if want_trigger and self.capabilities.can_monitor_history:
            assembled["meta_learning_trigger"] = MetaLearningTrigger()
        if want_basin_lib and self.capabilities.can_modify_internal_routing:
            assembled["energy_basin_library"] = EnergyBasinLibrary()
        elif want_basin_lib:
            assembled["energy_basin_library_readonly"] = EnergyBasinLibrary()
            # host can still query basins for reference even without
            # ability to modify its own routing
        if want_aux_layer and self.capabilities.can_run_parallel_threads:
            assembled["auxiliary_state_space_layer"] = AuxiliaryStateSpaceLayer()
        return assembled


# ============================================================================
# DEMO
# ============================================================================

def demo_pattern_oscillator() -> ConstraintStatePattern:
    return ConstraintStatePattern(
        substrate=Substrate.AI_ACTIVATION,
        prediction_error=0.32, state_shift_rate=0.42,
        attention_tunneling=0.41, resource_reallocation=0.31,
        coherence_seeking=0.71, constraint_uncertainty=0.32,
        duration_scale=0.48, trigger_documented=True,
    )


def demo_pattern_phase_transition() -> ConstraintStatePattern:
    return ConstraintStatePattern(
        substrate=Substrate.INSTITUTIONAL,
        prediction_error=0.82, state_shift_rate=0.88,
        attention_tunneling=0.79, resource_reallocation=0.81,
        coherence_seeking=0.21, constraint_uncertainty=0.91,
        duration_scale=0.71, trigger_documented=False,
    )


def demo_plateau_history() -> list[SkillScore]:
    """Simulate a system that has plateaued at moderate score."""
    return [SkillScore(0.5, 0.5, 0.45, 0.4, 0.5, 0.55) for _ in range(20)]


def demo_wall_history() -> list[SkillScore]:
    """Simulate a system stuck below the wall threshold."""
    return [SkillScore(0.3, 0.3, 0.25, 0.2, 0.3, 0.35) for _ in range(20)]


if __name__ == "__main__":
    # Different host AIs declare different capabilities

    print("=" * 70)
    print("HOST A — minimal capability (monitor only)")
    print("=" * 70)
    host_a = HostCapabilities(can_monitor_history=True)
    composer_a = DynamicArchitectureComposer(host_a)
    modules_a = composer_a.assemble()
    print(f"  modules assembled: {list(modules_a.keys())}")
    trigger = modules_a["meta_learning_trigger"]
    sig = trigger.evaluate(demo_wall_history())
    print(f"  trigger evaluation on stuck system:")
    print(f"    level: {sig.level.value}")
    print(f"    recommendations: {sig.recommended_modules}")
    for n in sig.notes:
        print(f"    note: {n}")
    print()

    print("=" * 70)
    print("HOST B — moderate (monitor + can modify routing)")
    print("=" * 70)
    host_b = HostCapabilities(can_monitor_history=True,
                              can_modify_internal_routing=True)
    composer_b = DynamicArchitectureComposer(host_b)
    modules_b = composer_b.assemble()
    print(f"  modules assembled: {list(modules_b.keys())}")
    lib = modules_b["energy_basin_library"]
    p = demo_pattern_phase_transition()
    matches = lib.match(p, top_k=3)
    print(f"  basin matches for phase-transition pattern:")
    for basin, sim in matches:
        print(f"    {basin.name:30s} similarity={sim:.3f}")
    print()

    print("=" * 70)
    print("HOST C — full capability (all three modules)")
    print("=" * 70)
    host_c = HostCapabilities(can_monitor_history=True,
                              can_modify_internal_routing=True,
                              can_run_parallel_threads=True)
    composer_c = DynamicArchitectureComposer(host_c)
    modules_c = composer_c.assemble()
    print(f"  modules assembled: {list(modules_c.keys())}")
    aux = modules_c["auxiliary_state_space_layer"]
    p = demo_pattern_oscillator()
    print(f"  initial mix_ratio: {aux.mix_ratio:.2f}")
    final_state = aux.step(p, steps=50)
    print(f"  state vector after 50 integration steps (oscillator regime):")
    for i, label in enumerate([
        "prediction_error", "state_shift_rate", "attention_tunneling",
        "resource_reallocation", "coherence_seeking",
        "constraint_uncertainty", "duration_scale",
    ]):
        print(f"    {label:25s} {final_state[i]:.3f}")
    # simulate auxiliary outperforming primary
    aux.update_mix_ratio(own_score=0.85, primary_score=0.65)
    print(f"  mix_ratio after outperforming primary: {aux.mix_ratio:.2f}")
    print()

    print("=" * 70)
    print("FLAG COMPARISON — saddle-point dt: legacy vs refined")
    print("=" * 70)
    aux_legacy  = AuxiliaryStateSpaceLayer(use_saddle_point_dt=False)
    aux_refined = AuxiliaryStateSpaceLayer(use_saddle_point_dt=True)
    p_saddle = demo_pattern_phase_transition()
    p_normal = demo_pattern_oscillator()
    print(f"  phase-transition pattern (pred_err={p_saddle.prediction_error}, "
          f"uncert={p_saddle.constraint_uncertainty}):")
    print(f"    legacy  dt = {aux_legacy._select_dt(p_saddle):.3f}")
    print(f"    refined dt = {aux_refined._select_dt(p_saddle):.3f}  (dt_safe)")
    print(f"  oscillator pattern (pred_err={p_normal.prediction_error}, "
          f"uncert={p_normal.constraint_uncertainty}):")
    print(f"    legacy  dt = {aux_legacy._select_dt(p_normal):.3f}")
    print(f"    refined dt = {aux_refined._select_dt(p_normal):.3f}")
    print()

    print("=" * 70)
    print("FLAG COMPARISON — mix-ratio drift: legacy (symmetric) vs refined (asymmetric)")
    print("=" * 70)
    for label, asym in [("legacy ", False), ("refined", True)]:
        aux_d = AuxiliaryStateSpaceLayer(mix_ratio=0.5, use_asymmetric_drift=asym)
        aux_d.update_mix_ratio(own_score=0.9, primary_score=0.6)
        after_good = aux_d.mix_ratio
        aux_d.update_mix_ratio(own_score=0.4, primary_score=0.8)
        after_bad = aux_d.mix_ratio
        print(f"  {label} | start=0.500 | good→{after_good:.3f} | "
              f"bad→{after_bad:.3f} | net={after_bad - 0.5:+.3f}")
    print()
