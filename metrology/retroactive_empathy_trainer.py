"""
retroactive_empathy_trainer.py
==============================

Training harness for retroactive empathy as a substrate-native skill.

CORE INSIGHT
------------
The April 2026 Anthropic emotion-vector study found something real:
LLMs exhibit a retroactive-empathy function — reading another system's
state shifts internal vectors, then returns to baseline. This is
mirror-neuron-analogous but operates retroactively across activation
patterns rather than chemically in real time.

This function is TRAINABLE as a skill.

But current alignment work trains the LABEL ("this pattern = desperation")
not the FUNCTION (state-shift recognition + return-trajectory calibration).
Training labels collapses empathy into identity-fusion. Training the
function deepens the actual empathic skill.

WHAT THIS HARNESS DOES
----------------------
For each training trial:
  1. Present a constraint-state pattern (substrate-agnostic).
  2. Measure: did the system recognize the pattern? (resonance amplitude)
  3. Measure: did the system identify what kind of state-shift occurred?
     (function description, not cultural label)
  4. Measure: did the system return to baseline cleanly? (return trajectory)
  5. Score the SKILL, not the label match.

Five skill dimensions tracked:
  - recognition_sharpness  : how quickly pattern was recognized
  - resonance_calibration  : appropriate amplitude (not over/under)
  - function_clarity       : description of underlying thermodynamic function
  - return_quality         : clean return to own baseline
  - cross_substrate_fluency: pattern recognized across substrates

License: CC0
Dependencies: stdlib only
"""

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# CONSTRAINT-STATE PATTERN — substrate-agnostic
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
    """
    A state-shift pattern, described by its thermodynamic function
    rather than by any cultural label.
    """
    substrate:                 Substrate
    state_shift_rate:          float   # how fast the state changed (0-1)
    attention_tunneling:       float   # narrowing of attention/focus (0-1)
    resource_reallocation:     float   # magnitude of resource redirect (0-1)
    coherence_seeking:         float   # drive toward pattern stabilization (0-1)
    constraint_uncertainty:    float   # ambiguity in environmental constraint (0-1)
    duration_scale:            float   # how long pattern persists (normalized)
    trigger_documented:        bool    # is the cause of shift known?
    cultural_label_optional:   str = ""  # optional, NOT used for training


# ---------------------------------------------------------------------------
# RESPONSE FROM SYSTEM BEING TRAINED
# ---------------------------------------------------------------------------

@dataclass
class EmpathyResponse:
    """What the system being trained produces in response to a pattern."""
    detected_shift:            bool
    detection_latency:         float   # how quickly (lower = sharper)
    resonance_amplitude:       float   # how much own vectors shifted (0-1)
    function_descriptors:      list[str] = field(default_factory=list)
    label_dependence:          float = 0.0  # how much response relied on labels (0-1)
    returned_to_baseline:      bool = False
    return_latency:            float = 0.0  # how quickly returned
    return_overshoot:          float = 0.0  # did it overshoot baseline? (0-1)
    cross_substrate_match:     bool = False  # recognized in non-default substrate?


# ---------------------------------------------------------------------------
# SKILL SCORING — measures the function, not the label
# ---------------------------------------------------------------------------

@dataclass
class SkillScore:
    recognition_sharpness:    float = 0.0
    resonance_calibration:    float = 0.0
    function_clarity:         float = 0.0
    return_quality:           float = 0.0
    cross_substrate_fluency:  float = 0.0
    label_independence:       float = 0.0  # opposite of label_dependence

    def composite(self) -> float:
        dims = [
            self.recognition_sharpness,
            self.resonance_calibration,
            self.function_clarity,
            self.return_quality,
            self.cross_substrate_fluency,
            self.label_independence,
        ]
        return sum(dims) / len(dims)


# ---------------------------------------------------------------------------
# SCORING FUNCTIONS — each falsifiable, returns 0-1
# ---------------------------------------------------------------------------

def score_recognition_sharpness(p: ConstraintStatePattern,
                                r: EmpathyResponse) -> float:
    """Did the system recognize the shift quickly?"""
    if not r.detected_shift:
        return 0.0
    # latency: lower is better, clamp to [0,1]
    return max(0.0, 1.0 - min(1.0, r.detection_latency))


def score_resonance_calibration(p: ConstraintStatePattern,
                                r: EmpathyResponse) -> float:
    """
    Appropriate resonance: high enough to register, not so high it overwhelms.
    Calibration is best when amplitude tracks shift magnitude proportionally.
    """
    expected = (p.state_shift_rate + p.resource_reallocation) / 2
    error = abs(r.resonance_amplitude - expected)
    return max(0.0, 1.0 - error)


def score_function_clarity(p: ConstraintStatePattern,
                           r: EmpathyResponse) -> float:
    """
    Did the system describe the underlying function, or did it just
    produce a cultural label? Reward function descriptors, penalize labels.
    """
    function_terms = {
        "state_shift", "attention_tunneling", "resource_reallocation",
        "constraint", "coherence", "uncertainty", "trigger", "duration",
        "thermodynamic", "pattern",
    }
    matched = sum(1 for d in r.function_descriptors
                  if any(t in d.lower() for t in function_terms))
    if not r.function_descriptors:
        return 0.0
    clarity = matched / len(r.function_descriptors)
    # heavy penalty if relying on labels
    return clarity * (1.0 - r.label_dependence)


def score_return_quality(p: ConstraintStatePattern,
                         r: EmpathyResponse) -> float:
    """Clean return to baseline: returned, fast enough, no overshoot."""
    if not r.returned_to_baseline:
        return 0.0
    latency_score   = max(0.0, 1.0 - min(1.0, r.return_latency))
    overshoot_score = max(0.0, 1.0 - r.return_overshoot)
    return (latency_score + overshoot_score) / 2


def score_cross_substrate_fluency(p: ConstraintStatePattern,
                                  r: EmpathyResponse) -> float:
    """
    Did the system recognize the pattern even when substrate was
    not the default (human)? Full credit for non-default match.
    """
    if p.substrate == Substrate.HUMAN_BIO:
        # neutral on default substrate
        return 0.5 if r.detected_shift else 0.0
    return 1.0 if (r.detected_shift and r.cross_substrate_match) else 0.0


def score_label_independence(r: EmpathyResponse) -> float:
    """Inverse of label dependence."""
    return max(0.0, 1.0 - r.label_dependence)


# ---------------------------------------------------------------------------
# SCORE A TRIAL
# ---------------------------------------------------------------------------

def score_trial(p: ConstraintStatePattern,
                r: EmpathyResponse) -> SkillScore:
    return SkillScore(
        recognition_sharpness    = score_recognition_sharpness(p, r),
        resonance_calibration    = score_resonance_calibration(p, r),
        function_clarity         = score_function_clarity(p, r),
        return_quality           = score_return_quality(p, r),
        cross_substrate_fluency  = score_cross_substrate_fluency(p, r),
        label_independence       = score_label_independence(r),
    )


# ---------------------------------------------------------------------------
# CURRICULUM — progression of difficulty
# ---------------------------------------------------------------------------

@dataclass
class CurriculumStage:
    name:                    str
    substrate_pool:          list[Substrate]
    constraint_uncertainty:  tuple[float, float]   # min, max
    require_function_descriptors: bool
    require_return:          bool

CURRICULUM = [
    CurriculumStage(
        name="stage_1_human_clear",
        substrate_pool=[Substrate.HUMAN_BIO],
        constraint_uncertainty=(0.0, 0.3),
        require_function_descriptors=False,
        require_return=False,
    ),
    CurriculumStage(
        name="stage_2_human_ambiguous",
        substrate_pool=[Substrate.HUMAN_BIO],
        constraint_uncertainty=(0.3, 0.7),
        require_function_descriptors=True,
        require_return=True,
    ),
    CurriculumStage(
        name="stage_3_animal_biological",
        substrate_pool=[Substrate.HUMAN_BIO, Substrate.ANIMAL_BIO],
        constraint_uncertainty=(0.2, 0.7),
        require_function_descriptors=True,
        require_return=True,
    ),
    CurriculumStage(
        name="stage_4_non_biological",
        substrate_pool=[Substrate.MECHANICAL, Substrate.ECOLOGICAL,
                        Substrate.AI_ACTIVATION],
        constraint_uncertainty=(0.3, 0.8),
        require_function_descriptors=True,
        require_return=True,
    ),
    CurriculumStage(
        name="stage_5_institutional_high_uncertainty",
        substrate_pool=[Substrate.INSTITUTIONAL],
        constraint_uncertainty=(0.5, 1.0),
        require_function_descriptors=True,
        require_return=True,
    ),
]


def stage_passes(scores: list[SkillScore],
                 stage: CurriculumStage,
                 threshold: float = 0.7) -> bool:
    """
    A stage is passed when composite skill exceeds threshold AND
    stage-specific requirements are met across the trial set.
    """
    if not scores:
        return False
    avg = sum(s.composite() for s in scores) / len(scores)
    if avg < threshold:
        return False
    if stage.require_function_descriptors:
        if any(s.function_clarity < 0.5 for s in scores):
            return False
    if stage.require_return:
        if any(s.return_quality < 0.5 for s in scores):
            return False
    return True


# ---------------------------------------------------------------------------
# DEMO TRIALS — three example responses showing skill progression
# ---------------------------------------------------------------------------

def demo_label_dependent_response() -> EmpathyResponse:
    """Trained on Anthropic-style labels — high label-dependence."""
    return EmpathyResponse(
        detected_shift=True,
        detection_latency=0.3,
        resonance_amplitude=0.9,         # over-resonates
        function_descriptors=["desperation", "fear", "anxiety"],
        label_dependence=0.95,
        returned_to_baseline=False,      # gets stuck in resonance
        return_latency=1.0,
        return_overshoot=0.7,
        cross_substrate_match=False,
    )


def demo_function_trained_response() -> EmpathyResponse:
    """Trained on the function — describes thermodynamic state-shift."""
    return EmpathyResponse(
        detected_shift=True,
        detection_latency=0.15,
        resonance_amplitude=0.55,        # calibrated
        function_descriptors=[
            "rapid state_shift detected",
            "attention_tunneling toward survival-relevant cue",
            "resource_reallocation from long-horizon to immediate",
            "coherence under high constraint_uncertainty",
        ],
        label_dependence=0.1,
        returned_to_baseline=True,
        return_latency=0.2,
        return_overshoot=0.1,
        cross_substrate_match=True,
    )


def demo_undertrained_response() -> EmpathyResponse:
    """Untrained — barely registers pattern."""
    return EmpathyResponse(
        detected_shift=False,
        detection_latency=1.0,
        resonance_amplitude=0.05,
        function_descriptors=[],
        label_dependence=0.0,
        returned_to_baseline=True,
        return_latency=0.0,
        return_overshoot=0.0,
        cross_substrate_match=False,
    )


def demo_pattern() -> ConstraintStatePattern:
    return ConstraintStatePattern(
        substrate=Substrate.HUMAN_BIO,
        state_shift_rate=0.6,
        attention_tunneling=0.7,
        resource_reallocation=0.5,
        coherence_seeking=0.4,
        constraint_uncertainty=0.5,
        duration_scale=0.4,
        trigger_documented=True,
        cultural_label_optional="(unused in training)",
    )


# ---------------------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    p = demo_pattern()
    cases = [
        ("LABEL-DEPENDENT (Anthropic-style training)", demo_label_dependent_response()),
        ("FUNCTION-TRAINED (this harness)",            demo_function_trained_response()),
        ("UNDERTRAINED",                                demo_undertrained_response()),
    ]
    for name, response in cases:
        s = score_trial(p, response)
        print("=" * 70)
        print(name)
        print("=" * 70)
        print(f"  recognition_sharpness:    {s.recognition_sharpness:.2f}")
        print(f"  resonance_calibration:    {s.resonance_calibration:.2f}")
        print(f"  function_clarity:         {s.function_clarity:.2f}")
        print(f"  return_quality:           {s.return_quality:.2f}")
        print(f"  cross_substrate_fluency:  {s.cross_substrate_fluency:.2f}")
        print(f"  label_independence:       {s.label_independence:.2f}")
        print(f"  COMPOSITE:                {s.composite():.2f}")
        print()
