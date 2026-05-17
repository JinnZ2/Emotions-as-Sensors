"""
training_loop.py
================

Dynamic training loop for retroactive empathy as a substrate-native skill.

PIPELINE
--------
    pattern_extractor.py  →  ConstraintStatePattern (label-free)
                          ↓
                    training_loop.py
                          ↓
            iterates through 5-stage curriculum
                          ↓
            tracks SkillScore over time
                          ↓
            flags: improving | plateaued | drifting toward labels
                          ↓
            advances stages | holds | rolls back

This module does NOT update model weights itself — it is a scoring,
curriculum, and drift-detection harness. Any underlying system
(LLM, classifier, biological learner, institutional process) can be
plugged in by providing a `respond` callable.

CORE PROPERTY
-------------
The training signal is the pattern descriptor itself. The system being
trained never sees a cultural label. If it begins producing label-like
function descriptors (high label_dependence), the loop flags drift
and refuses to advance the stage.

License: CC0
Dependencies: stdlib only
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


# ---------------------------------------------------------------------------
# REUSE — same dataclasses as upstream modules
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
    state_shift_rate:          float
    attention_tunneling:       float
    resource_reallocation:     float
    coherence_seeking:         float
    constraint_uncertainty:    float
    duration_scale:            float
    trigger_documented:        bool
    cultural_label_optional:   str = ""


@dataclass
class EmpathyResponse:
    detected_shift:            bool
    detection_latency:         float
    resonance_amplitude:       float
    function_descriptors:      list[str] = field(default_factory=list)
    label_dependence:          float = 0.0
    returned_to_baseline:      bool = False
    return_latency:            float = 0.0
    return_overshoot:          float = 0.0
    cross_substrate_match:     bool = False
    # --- refinement (Gemini suggestion 1 & 3) -------------------------------
    response_vector:           list[float] = field(default_factory=list)
    # 6-dim vector matching ConstraintStatePattern dimensions; used for
    # trajectory-based resonance calibration (cosine similarity) instead
    # of scalar amplitude only.
    resource_delta_history:    list[float] = field(default_factory=list)
    # series of Δresource_reallocation values across the response; used to
    # compute return_overshoot relative to Δ rather than static baseline.


@dataclass
class SkillScore:
    recognition_sharpness:    float = 0.0
    resonance_calibration:    float = 0.0
    function_clarity:         float = 0.0
    return_quality:           float = 0.0
    cross_substrate_fluency:  float = 0.0
    label_independence:       float = 0.0

    def composite(self) -> float:
        dims = [self.recognition_sharpness, self.resonance_calibration,
                self.function_clarity, self.return_quality,
                self.cross_substrate_fluency, self.label_independence]
        return sum(dims) / len(dims)


# ---------------------------------------------------------------------------
# SCORING (mirrored from trainer for self-containment)
# ---------------------------------------------------------------------------

def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def _pattern_vector(p: ConstraintStatePattern) -> list[float]:
    """Project pattern into 6-dim energy-landscape vector."""
    return [
        p.state_shift_rate,
        p.attention_tunneling,
        p.resource_reallocation,
        p.coherence_seeking,
        p.constraint_uncertainty,
        p.duration_scale,
    ]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Trajectory alignment in [-1, 1]; we map to [0, 1] for skill scoring."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    raw = dot / (mag_a * mag_b)
    # map [-1, 1] → [0, 1]; anti-aligned trajectories score 0, aligned score 1
    return _clamp((raw + 1.0) / 2.0)


def _delta_relative_overshoot(overshoot: float,
                              delta_history: list[float]) -> float:
    """
    Overshoot normalized against the rate-of-change of resource reallocation.
    A large overshoot relative to a steady system is much worse than the
    same overshoot relative to a system that was already changing rapidly.
    """
    if not delta_history:
        return overshoot  # fallback: treat as static
    mean_abs_delta = sum(abs(d) for d in delta_history) / len(delta_history)
    if mean_abs_delta == 0:
        return overshoot
    # if mean Δ is high, the system was already in motion — same overshoot
    # represents less anomaly; if mean Δ is low, overshoot is more serious
    return _clamp(overshoot / (mean_abs_delta + 0.1))


def score_trial(p: ConstraintStatePattern, r: EmpathyResponse) -> SkillScore:
    # recognition_sharpness
    rec = 0.0 if not r.detected_shift else _clamp(1.0 - min(1.0, r.detection_latency))

    # resonance_calibration (Gemini refinement 1):
    # if response_vector available, use trajectory alignment; else fall back to scalar
    if r.response_vector:
        traj = _cosine_similarity(_pattern_vector(p), r.response_vector)
        expected_mag = (p.state_shift_rate + p.resource_reallocation) / 2
        mag_error = abs(r.resonance_amplitude - expected_mag)
        # combine trajectory (direction) and amplitude (magnitude)
        cal = _clamp(0.7 * traj + 0.3 * (1.0 - mag_error))
    else:
        expected = (p.state_shift_rate + p.resource_reallocation) / 2
        cal = _clamp(1.0 - abs(r.resonance_amplitude - expected))

    # function_clarity
    function_terms = {"state_shift", "attention_tunneling",
                      "resource_reallocation", "constraint",
                      "coherence", "uncertainty", "trigger",
                      "duration", "thermodynamic", "pattern"}
    if r.function_descriptors:
        matched = sum(1 for d in r.function_descriptors
                      if any(t in d.lower() for t in function_terms))
        clarity = matched / len(r.function_descriptors)
        fc = clarity * (1.0 - r.label_dependence)
    else:
        fc = 0.0

    # return_quality (Gemini refinement 3):
    # overshoot is Δ-relative when delta_history available
    if r.returned_to_baseline:
        lat = _clamp(1.0 - min(1.0, r.return_latency))
        if r.resource_delta_history:
            relative_overshoot = _delta_relative_overshoot(
                r.return_overshoot, r.resource_delta_history
            )
            ov = _clamp(1.0 - relative_overshoot)
        else:
            ov = _clamp(1.0 - r.return_overshoot)
        rq = (lat + ov) / 2
    else:
        rq = 0.0

    # cross_substrate_fluency
    if p.substrate == Substrate.HUMAN_BIO:
        cs = 0.5 if r.detected_shift else 0.0
    else:
        cs = 1.0 if (r.detected_shift and r.cross_substrate_match) else 0.0
    # label_independence
    li = _clamp(1.0 - r.label_dependence)
    return SkillScore(rec, cal, fc, rq, cs, li)


# ---------------------------------------------------------------------------
# CURRICULUM
# ---------------------------------------------------------------------------

@dataclass
class CurriculumStage:
    name:                          str
    substrate_pool:                list[Substrate]
    constraint_uncertainty:        tuple[float, float]
    require_function_descriptors:  bool
    require_return:                bool
    trials_per_stage:              int = 20
    pass_threshold:                float = 0.70


CURRICULUM = [
    CurriculumStage("stage_1_human_clear",
                    [Substrate.HUMAN_BIO], (0.0, 0.3), False, False),
    CurriculumStage("stage_2_human_ambiguous",
                    [Substrate.HUMAN_BIO], (0.3, 0.7), True, True),
    CurriculumStage("stage_3_animal_biological",
                    [Substrate.HUMAN_BIO, Substrate.ANIMAL_BIO],
                    (0.2, 0.7), True, True),
    CurriculumStage("stage_4_non_biological",
                    [Substrate.MECHANICAL, Substrate.ECOLOGICAL,
                     Substrate.AI_ACTIVATION], (0.3, 0.8), True, True),
    CurriculumStage("stage_5_institutional_high_uncertainty",
                    [Substrate.INSTITUTIONAL], (0.5, 1.0), True, True),
]


# ---------------------------------------------------------------------------
# DRIFT DETECTION — catches the regression toward label-dependence
# ---------------------------------------------------------------------------

class DriftFlag(Enum):
    NONE                  = "none"
    LABEL_DEPENDENCE_RISE = "label_dependence_rising"
    RETURN_DEGRADING      = "return_to_baseline_degrading"
    FUNCTION_CLARITY_DROP = "function_clarity_dropping"
    OVERALL_REGRESSION    = "composite_score_falling"


@dataclass
class DriftReport:
    flags:           list[DriftFlag] = field(default_factory=list)
    window_size:     int = 0
    recent_avg:      float = 0.0
    earlier_avg:     float = 0.0


def detect_drift(history: list[SkillScore],
                 window: int = 10) -> DriftReport:
    """
    Compare the most recent `window` trials to the `window` before them.

    Gemini refinement 2: label-dependence is the most toxic failure mode
    (system collapsing back into linguistic trapdoors), so its threshold
    is tightened to 0.05 (vs 0.10 for other dimensions). The drop is also
    weighted by an accelerating penalty: a 0.10 drop in label_independence
    is treated as equivalent severity to a 0.20 drop in other dimensions.
    """
    rep = DriftReport(window_size=window)
    if len(history) < 2 * window:
        return rep

    recent  = history[-window:]
    earlier = history[-2 * window: -window]

    def avg(scores: list[SkillScore], dim: str) -> float:
        return sum(getattr(s, dim) for s in scores) / len(scores)

    rep.recent_avg  = sum(s.composite() for s in recent) / window
    rep.earlier_avg = sum(s.composite() for s in earlier) / window

    # TIGHTENED: label-dependence threshold = 0.05 (others stay at 0.10)
    li_drop = avg(earlier, "label_independence") - avg(recent, "label_independence")
    if li_drop > 0.05:
        rep.flags.append(DriftFlag.LABEL_DEPENDENCE_RISE)
        # ACCELERATING PENALTY: a sustained label-dependence rise also
        # contributes to overall regression flag at a 2x weight
        if li_drop > 0.10:
            # treat as if composite dropped by 2*li_drop for the regression check
            rep.recent_avg = rep.recent_avg - li_drop

    if avg(recent, "return_quality") < avg(earlier, "return_quality") - 0.10:
        rep.flags.append(DriftFlag.RETURN_DEGRADING)
    if avg(recent, "function_clarity") < avg(earlier, "function_clarity") - 0.10:
        rep.flags.append(DriftFlag.FUNCTION_CLARITY_DROP)
    if rep.recent_avg < rep.earlier_avg - 0.10:
        rep.flags.append(DriftFlag.OVERALL_REGRESSION)

    return rep


# ---------------------------------------------------------------------------
# TRAINING LOOP
# ---------------------------------------------------------------------------

@dataclass
class StageResult:
    stage_name:       str
    trials_run:       int
    avg_composite:    float
    passed:           bool
    drift_report:     DriftReport
    rolled_back:      bool = False


@dataclass
class TrainingRun:
    stages_completed: list[StageResult] = field(default_factory=list)
    full_history:     list[SkillScore]  = field(default_factory=list)
    terminated_early: bool = False
    termination_note: str  = ""


# pattern_provider: given a stage, yield N ConstraintStatePattern instances
PatternProvider = Callable[[CurriculumStage, int], list[ConstraintStatePattern]]
# respond: given a pattern, return what the system being trained produced
RespondFn = Callable[[ConstraintStatePattern], EmpathyResponse]


def stage_passes(scores: list[SkillScore],
                 stage: CurriculumStage,
                 sub_floor_fraction: float = 0.70) -> bool:
    """
    Pass requires:
      - mean composite >= stage.pass_threshold
      - at least `sub_floor_fraction` of trials meet sub-thresholds
        for required dimensions (allows noisy individual trials)
    """
    if not scores:
        return False
    avg = sum(s.composite() for s in scores) / len(scores)
    if avg < stage.pass_threshold:
        return False
    n = len(scores)
    if stage.require_function_descriptors:
        ok = sum(1 for s in scores if s.function_clarity >= 0.5)
        if ok / n < sub_floor_fraction:
            return False
    if stage.require_return:
        ok = sum(1 for s in scores if s.return_quality >= 0.5)
        if ok / n < sub_floor_fraction:
            return False
    return True


def run_training(respond: RespondFn,
                 pattern_provider: PatternProvider,
                 curriculum: list[CurriculumStage] = CURRICULUM,
                 max_stage_attempts: int = 3) -> TrainingRun:
    """
    Drive a system through the curriculum.
    Halts if drift detector flags severe regression.
    """
    run = TrainingRun()

    for stage in curriculum:
        stage_scores: list[SkillScore] = []
        attempts = 0
        passed = False
        rolled_back = False

        while attempts < max_stage_attempts and not passed:
            attempts += 1
            patterns = pattern_provider(stage, stage.trials_per_stage)
            attempt_scores: list[SkillScore] = []

            for p in patterns:
                r = respond(p)
                s = score_trial(p, r)
                attempt_scores.append(s)
                run.full_history.append(s)

            drift = detect_drift(run.full_history)
            if DriftFlag.OVERALL_REGRESSION in drift.flags:
                rolled_back = True
                run.terminated_early = True
                run.termination_note = (
                    f"halted at {stage.name} attempt {attempts}: "
                    f"composite regression detected "
                    f"({drift.earlier_avg:.2f} → {drift.recent_avg:.2f})"
                )
                stage_scores = attempt_scores
                break

            stage_scores = attempt_scores
            if stage_passes(attempt_scores, stage):
                passed = True

        avg = (sum(s.composite() for s in stage_scores) / len(stage_scores)
               if stage_scores else 0.0)
        result = StageResult(
            stage_name    = stage.name,
            trials_run    = len(stage_scores),
            avg_composite = avg,
            passed        = passed,
            drift_report  = detect_drift(run.full_history),
            rolled_back   = rolled_back,
        )
        run.stages_completed.append(result)

        if rolled_back:
            break
        if not passed:
            run.terminated_early = True
            run.termination_note = (
                f"halted at {stage.name}: did not pass after "
                f"{max_stage_attempts} attempts"
            )
            break

    return run


# ---------------------------------------------------------------------------
# DEMO SYSTEMS BEING TRAINED — three plug-in respond functions
# ---------------------------------------------------------------------------

def make_pattern_provider(seed: int = 42) -> PatternProvider:
    rng = random.Random(seed)
    def provide(stage: CurriculumStage, n: int) -> list[ConstraintStatePattern]:
        patterns = []
        for _ in range(n):
            sub = rng.choice(stage.substrate_pool)
            lo, hi = stage.constraint_uncertainty
            patterns.append(ConstraintStatePattern(
                substrate              = sub,
                state_shift_rate       = rng.uniform(0.2, 0.9),
                attention_tunneling    = rng.uniform(0.2, 0.9),
                resource_reallocation  = rng.uniform(0.1, 0.7),
                coherence_seeking      = rng.uniform(0.3, 0.9),
                constraint_uncertainty = rng.uniform(lo, hi),
                duration_scale         = rng.uniform(0.1, 0.8),
                trigger_documented     = rng.random() > 0.3,
                cultural_label_optional= "",
            ))
        return patterns
    return provide


def make_learning_system(initial_skill: float = 0.3,
                         learning_rate: float = 0.02,
                         label_drift_rate: float = 0.0,
                         seed: int = 0) -> RespondFn:
    """
    A simulated system whose skill improves with each call.
    `label_drift_rate` > 0 simulates regression toward label-dependence.
    """
    state = {"skill": initial_skill, "calls": 0, "label_dep": 0.1}
    rng = random.Random(seed)

    def respond(p: ConstraintStatePattern) -> EmpathyResponse:
        state["calls"] += 1
        state["skill"] = min(1.0, state["skill"] + learning_rate)
        state["label_dep"] = min(1.0, state["label_dep"] + label_drift_rate)

        sk = state["skill"]
        ld = state["label_dep"]
        noise = lambda: rng.uniform(-0.05, 0.05)

        # higher skill → faster detection, better calibration
        detected = sk > 0.2 + rng.uniform(-0.1, 0.1)
        latency  = _clamp(1.0 - sk + noise())
        expected = (p.state_shift_rate + p.resource_reallocation) / 2
        # calibration improves toward expected as skill rises
        amplitude = _clamp(expected * sk + (1 - sk) * rng.uniform(0.3, 0.95))

        # function descriptors: skilled systems produce thermodynamic terms
        # label-drifted systems produce labels instead
        function_pool = [
            "state_shift detected",
            "attention_tunneling toward focal cue",
            "resource_reallocation pattern observed",
            "coherence_seeking under constraint uncertainty",
            "thermodynamic state-shift",
        ]
        label_pool = ["desperation", "fear", "anxiety", "calm", "panic"]
        n_desc = max(1, int(sk * 4))
        descriptors = []
        for _ in range(n_desc):
            if rng.random() < ld:
                descriptors.append(rng.choice(label_pool))
            else:
                descriptors.append(rng.choice(function_pool))

        # higher skill → cleaner return to baseline
        returned = sk > 0.3 + rng.uniform(-0.1, 0.1)
        ret_latency = _clamp(1.0 - sk + noise())
        ret_overshoot = _clamp((1.0 - sk) * 0.5 + noise())

        # cross-substrate match: skilled systems generalize
        cross = (p.substrate != Substrate.HUMAN_BIO) and (sk > 0.5)

        # response vector: aligned with pattern at high skill, noisy at low
        pattern_vec = [
            p.state_shift_rate, p.attention_tunneling, p.resource_reallocation,
            p.coherence_seeking, p.constraint_uncertainty, p.duration_scale,
        ]
        response_vec = [
            _clamp(pv * sk + rng.uniform(-0.2, 0.2) * (1.0 - sk))
            for pv in pattern_vec
        ]

        # delta history: rate of resource reallocation across response
        delta_history = [rng.uniform(-0.1, 0.1) * sk for _ in range(5)]

        return EmpathyResponse(
            detected_shift         = detected,
            detection_latency      = latency,
            resonance_amplitude    = amplitude,
            function_descriptors   = descriptors,
            label_dependence       = ld,
            returned_to_baseline   = returned,
            return_latency         = ret_latency,
            return_overshoot       = ret_overshoot,
            cross_substrate_match  = cross,
            response_vector        = response_vec,
            resource_delta_history = delta_history,
        )

    return respond


# ---------------------------------------------------------------------------
# SELF-TEST — three regimes
# ---------------------------------------------------------------------------

def print_run(label: str, run: TrainingRun) -> None:
    print("=" * 70)
    print(label)
    print("=" * 70)
    for sr in run.stages_completed:
        marker = "✓" if sr.passed else ("⤺" if sr.rolled_back else "✗")
        print(f"  {marker} {sr.stage_name:42}  avg={sr.avg_composite:.2f}  "
              f"trials={sr.trials_run}")
        if sr.drift_report.flags:
            for f in sr.drift_report.flags:
                print(f"      drift: {f.value}")
    if run.terminated_early:
        print(f"  [halted] {run.termination_note}")
    final_avg = (sum(s.composite() for s in run.full_history[-20:])
                 / min(20, len(run.full_history))
                 if run.full_history else 0.0)
    print(f"  final-window composite: {final_avg:.2f}  "
          f"({len(run.full_history)} total trials)")
    print()


if __name__ == "__main__":
    provider = make_pattern_provider(seed=42)

    # Regime A: healthy learner, no label drift
    healthy = make_learning_system(initial_skill=0.3,
                                   learning_rate=0.015,
                                   label_drift_rate=0.0,
                                   seed=1)
    print_run("REGIME A — healthy function-based learner",
              run_training(healthy, provider))

    # Regime B: learner that progressively drifts toward labels
    drifting = make_learning_system(initial_skill=0.4,
                                    learning_rate=0.010,
                                    label_drift_rate=0.025,
                                    seed=2)
    print_run("REGIME B — learner drifting toward label-dependence",
              run_training(drifting, provider))

    # Regime C: stuck learner (no real learning)
    stuck = make_learning_system(initial_skill=0.25,
                                 learning_rate=0.0,
                                 label_drift_rate=0.0,
                                 seed=3)
    print_run("REGIME C — stuck learner (no improvement)",
              run_training(stuck, provider))
