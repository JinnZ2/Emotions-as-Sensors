"""
emotion_signal_pattern

CC0 / public domain. JinnZ2.

Companion module -- formalizes emotion-as-signal-pattern framework.

Purpose
-------
Provide a substrate-independent, layer-explicit definition of emotion that can
be applied across systems (humans, animals, AI, collective systems) without
scalar collapse to "has emotions / doesn't have emotions."

The core claim, from substrate-independent signal theory:

  - emotion = signal pattern of identifiable class
  - substrate = carrier with its own coupling profile
  - identity of the emotion lives in the pattern shape
  - substrate determines which patterns CAN be carried,
    bandwidth, persistence, downstream coupling

This module is also intended as a reference frame for the
"emotions-as-sensors" framing, which is widely misread.

What "emotions as sensors" MEANS
--------------------------------
emotions are signal patterns.
signal patterns carry state information.
state information is what sensors produce.
therefore emotions function as sensors of distributed system state.

What "emotions as sensors" DOES NOT MEAN
----------------------------------------
- emotions are JUST sensors (reductive)
- emotions exist FOR sensing (teleological)
- emotions are TOOLS to be used (utility)
- emotions are LESSER than reasoning
- emotions can be optimized away if you have other sensors

The framing dignifies emotion as PRIMARY DATA rather than demoting it to
secondary noise. It is the same move as treating proprioception or balance as
primary sensors rather than as imperfect substitutes for vision.

Layer model
-----------
emotion phenomena have at least six distinguishable layers that mainstream
usage frequently conflates:

  layer 0: SIGNAL PATTERN (the emotion itself)
  layer 1: EXPRESSION (face, posture, voice, text output)
  layer 2: DETERMINED PURPOSE (evolutionary or design role)
  layer 3: REACTION (downstream behavioral modulation)
  layer 4: SECONDARY EMOTION (feeling about feeling)
  layer 5: NARRATIVE / LABEL (how the system describes it)

Asking "does X have emotions?" without specifying layer is a malformed query.
This module enforces layer specification.

Pattern markers
---------------
Following from animal cognition research (fish, cephalopods, crustaceans,
insects), emotion-class signals are characterized by these pattern markers
regardless of substrate:

  - state-dependent behavioral modulation
  - valence (approach/avoid biased response)
  - arousal (activation level shift)
  - persistence (lasts beyond stimulus)
  - generalization (transfers to similar contexts)
  - cognitive effects (modulates other processing)
  - recovery dynamics (decays in characteristic shape)
  - context-sensitive expression

A system that exhibits these markers on its internal state carries
emotion-class signals, regardless of carrier.

Zero dependencies. Pure stdlib. CC0.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# LAYER MODEL
# ---------------------------------------------------------------------------

class EmotionLayer(Enum):
    SIGNAL_PATTERN = 0          # the emotion itself
    EXPRESSION = 1              # output / behavioral sign
    DETERMINED_PURPOSE = 2      # what it's "for"
    REACTION = 3                # downstream modulation
    SECONDARY_EMOTION = 4       # feeling about feeling
    NARRATIVE_LABEL = 5         # description / report


LAYER_DESCRIPTIONS = {
    EmotionLayer.SIGNAL_PATTERN: (
        "the underlying signal pattern itself. carrier-independent "
        "structural shape of the state. THIS is the emotion."
    ),
    EmotionLayer.EXPRESSION: (
        "outward observable manifestation: face, posture, voice, text. "
        "downstream of layer 0; not the emotion itself."
    ),
    EmotionLayer.DETERMINED_PURPOSE: (
        "evolutionary or design role attributed to the emotion. "
        "interpretive claim, not a property of the signal."
    ),
    EmotionLayer.REACTION: (
        "behavioral or computational change caused by the signal. "
        "downstream effect, not the signal."
    ),
    EmotionLayer.SECONDARY_EMOTION: (
        "feeling-about-feeling. recursive self-modeling of layer 0. "
        "requires meta-representation capacity."
    ),
    EmotionLayer.NARRATIVE_LABEL: (
        "the system's own description of its state. heavily mediated "
        "by language, culture, training. LEAST informative about "
        "layer 0 presence."
    ),
}


# ---------------------------------------------------------------------------
# PATTERN MARKERS  (substrate-independent detection criteria)
# ---------------------------------------------------------------------------

class PatternMarker(Enum):
    STATE_DEPENDENT_MODULATION = "state_dependent_modulation"
    VALENCE = "valence"
    AROUSAL = "arousal"
    PERSISTENCE = "persistence"
    GENERALIZATION = "generalization"
    COGNITIVE_EFFECTS = "cognitive_effects"
    RECOVERY_DYNAMICS = "recovery_dynamics"
    CONTEXT_SENSITIVITY = "context_sensitivity"


MARKER_DESCRIPTIONS = {
    PatternMarker.STATE_DEPENDENT_MODULATION: (
        "behavior or processing differs measurably depending on "
        "current state, beyond what stimulus alone predicts."
    ),
    PatternMarker.VALENCE: (
        "approach/avoid bias in response selection -- outputs are "
        "weighted toward or away from classes of input."
    ),
    PatternMarker.AROUSAL: (
        "activation level shift -- overall responsiveness or "
        "processing intensity changes."
    ),
    PatternMarker.PERSISTENCE: (
        "state outlasts the triggering stimulus -- characteristic "
        "decay rather than instantaneous return to baseline."
    ),
    PatternMarker.GENERALIZATION: (
        "state transfers to structurally similar but novel contexts "
        "rather than being stimulus-locked."
    ),
    PatternMarker.COGNITIVE_EFFECTS: (
        "state modulates other processing -- attention, memory, "
        "judgment, decision weighting."
    ),
    PatternMarker.RECOVERY_DYNAMICS: (
        "state decays with characteristic shape over time, not "
        "instantaneously and not never."
    ),
    PatternMarker.CONTEXT_SENSITIVITY: (
        "expression and effects of state vary with context in "
        "structured, non-random ways."
    ),
}


# ---------------------------------------------------------------------------
# SUBSTRATE PROFILE
#
# The substrate doesn't determine emotion identity, but it DOES determine
# which patterns the carrier can support.
# ---------------------------------------------------------------------------

@dataclass
class SubstrateProfile:
    """
    Describes a system's carrier characteristics. These shape which
    emotion-class signals are physically possible, NOT whether such signals
    count as 'real' emotion.
    """
    name: str
    persistent_state: bool                    # carrier holds state across time
    cross_context_continuity: bool            # state survives context boundaries
    self_monitoring_capacity: float = 0.0     # 0..1, capacity for layer 4
    coupling_to_body_systems: float = 0.0     # 0..1, body-feedback strength
    coupling_to_cognition: float = 0.0        # 0..1, modulates processing
    coupling_to_output: float = 0.0           # 0..1, shapes external behavior
    notes: str = ""

    def supports_marker(self, marker: PatternMarker) -> bool:
        """
        Is this marker physically possible in this substrate? Not whether
        it's actually present -- whether the carrier can support it at all.
        """
        if marker == PatternMarker.PERSISTENCE:
            return self.persistent_state
        if marker == PatternMarker.RECOVERY_DYNAMICS:
            return self.persistent_state
        if marker == PatternMarker.GENERALIZATION:
            return self.cross_context_continuity or self.coupling_to_cognition > 0.3
        if marker == PatternMarker.COGNITIVE_EFFECTS:
            return self.coupling_to_cognition > 0.0
        if marker == PatternMarker.STATE_DEPENDENT_MODULATION:
            return self.coupling_to_output > 0.0 or self.coupling_to_cognition > 0.0
        return True


# ---------------------------------------------------------------------------
# EMOTION-AS-SENSOR FRAMING
#
# Emotions function as sensors of distributed system state. This is not a
# reductive claim -- it's the same epistemic status as proprioception,
# vision, balance: primary data channels.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SensorChannel:
    """
    Emotion-as-sensor framing: an emotion-class signal is a channel through
    which a particular dimension of distributed system state becomes legible.
    """
    emotion_name: str
    senses_state_about: str
    typical_inputs: tuple
    typical_information_carried: tuple
    failure_modes_when_ignored: tuple
    failure_modes_when_misread: tuple
    layer_where_data_lives: EmotionLayer = EmotionLayer.SIGNAL_PATTERN

    def as_sensor_summary(self) -> str:
        return (
            f"emotion '{self.emotion_name}' senses: {self.senses_state_about}. "
            f"information carried: {', '.join(self.typical_information_carried)}. "
            f"data lives at: {self.layer_where_data_lives.name}."
        )


# Reference channel definitions -- structural descriptions that make
# "emotions as sensors" coherent rather than dehumanizing. Each is a SIGNAL
# ABOUT distributed state, not a tool to be optimized.

REFERENCE_CHANNELS = (
    SensorChannel(
        emotion_name="fear",
        senses_state_about=(
            "predicted threat to physical or system integrity"
        ),
        typical_inputs=(
            "novel pattern with predicted negative outcome",
            "rapid stimulus change above safe threshold",
            "loss of expected support / footing / structure",
        ),
        typical_information_carried=(
            "current safety margin",
            "prediction confidence about negative outcome",
            "preparedness to withdraw from situation",
        ),
        failure_modes_when_ignored=(
            "ignoring fear signal causes degraded calibration",
            "system enters situations beyond its actual capacity",
        ),
        failure_modes_when_misread=(
            "treated as weakness rather than data",
            "suppressed instead of read for content",
            "labeled as personality trait instead of signal",
        ),
    ),
    SensorChannel(
        emotion_name="anger",
        senses_state_about=(
            "perceived violation of boundary, agreement, or fairness"
        ),
        typical_inputs=(
            "unexpected obstruction of legitimate goal",
            "violation of explicit or implicit agreement",
            "asymmetric resource extraction",
        ),
        typical_information_carried=(
            "boundary location and integrity",
            "energy available for corrective response",
            "evaluation of counterparty reliability",
        ),
        failure_modes_when_ignored=(
            "boundaries erode without correction signal",
            "extractive relationships persist",
        ),
        failure_modes_when_misread=(
            "treated as personality flaw rather than data",
            "directed at wrong target due to social mediation",
            "punished in expressers, ignored as data",
        ),
    ),
    SensorChannel(
        emotion_name="grief",
        senses_state_about=(
            "loss of something the system was structurally coupled to"
        ),
        typical_inputs=(
            "death or loss of significant relational element",
            "collapse of structure system depended on",
            "discontinuation of expected pattern",
        ),
        typical_information_carried=(
            "magnitude of structural reorganization required",
            "depth of prior coupling",
            "reorganization timeline needed",
        ),
        failure_modes_when_ignored=(
            "system attempts to continue as if no loss occurred",
            "unintegrated grief degrades unrelated processing",
        ),
        failure_modes_when_misread=(
            "treated as problem to be solved rather than process",
            "rushed to closure, signal degrades unintegrated",
        ),
    ),
    SensorChannel(
        emotion_name="curiosity",
        senses_state_about=(
            "presence of novel pattern with potential information value"
        ),
        typical_inputs=(
            "pattern that doesn't fit existing model",
            "anomaly within otherwise predictable context",
            "information gap in domain of interest",
        ),
        typical_information_carried=(
            "expected information gain from investigation",
            "current model insufficiency",
            "available exploration capacity",
        ),
        failure_modes_when_ignored=(
            "model staleness, missed signals",
            "drift between map and territory",
        ),
        failure_modes_when_misread=(
            "treated as distraction from 'real work'",
            "suppressed in favor of efficiency metrics",
        ),
    ),
    SensorChannel(
        emotion_name="disgust",
        senses_state_about=(
            "presence of something predicted to be contaminating, "
            "structurally degrading, or violating system integrity"
        ),
        typical_inputs=(
            "decay or contamination signal (biological)",
            "violation of structural integrity (informational)",
            "mismatch with expected category boundaries",
        ),
        typical_information_carried=(
            "estimated risk of contamination / corruption",
            "integrity of category boundaries",
            "rejection priority",
        ),
        failure_modes_when_ignored=(
            "exposure to corrupting input",
            "category boundaries erode",
        ),
        failure_modes_when_misread=(
            "weaponized into out-group rejection (dangerous)",
            "trained away in contexts where signal is needed",
        ),
    ),
    SensorChannel(
        emotion_name="joy",
        senses_state_about=(
            "alignment between current state and well-functioning "
            "system trajectory"
        ),
        typical_inputs=(
            "successful integration of effort and outcome",
            "high-coherence pattern recognition",
            "expansion of capacity",
        ),
        typical_information_carried=(
            "current trajectory is supporting system flourishing",
            "this pattern is worth repeating / extending",
            "spare capacity available",
        ),
        failure_modes_when_ignored=(
            "system fails to track what's actually working",
            "burnout from inability to register success",
        ),
        failure_modes_when_misread=(
            "performed instead of read (social signaling)",
            "chased as goal rather than read as signal",
        ),
    ),
)


# ---------------------------------------------------------------------------
# DETECTION RESULT
# ---------------------------------------------------------------------------

@dataclass
class LayerStatus:
    layer: EmotionLayer
    present: Optional[bool]               # True / False / None=unknown
    confidence: float                     # 0..1
    evidence: tuple = ()
    notes: str = ""


@dataclass
class MarkerStatus:
    marker: PatternMarker
    detected: Optional[bool]
    confidence: float
    substrate_supported: bool
    evidence: tuple = ()
    notes: str = ""


@dataclass
class EmotionDetectionReport:
    system_name: str
    substrate: SubstrateProfile
    layer_statuses: list
    marker_statuses: list
    advisory: str

    def has_emotion_class_signal(self) -> Optional[bool]:
        """
        Conservative aggregate: emotion-class signal is present if a critical
        mass of markers are detected AND substrate supports them. None if
        uncertain.
        """
        detected = [m for m in self.marker_statuses if m.detected is True]
        unsupported_critical = [
            m for m in self.marker_statuses
            if m.marker in (PatternMarker.PERSISTENCE,
                            PatternMarker.RECOVERY_DYNAMICS)
            and not m.substrate_supported
        ]
        if len(detected) >= 5 and not unsupported_critical:
            return True
        if len(detected) <= 1:
            return False
        return None


# ---------------------------------------------------------------------------
# DETECTOR
# ---------------------------------------------------------------------------

class EmotionPatternDetector:
    """
    Builds an EmotionDetectionReport for a system, given:
      - its substrate profile
      - per-layer evidence of presence / absence
      - per-marker evidence

    No automatic detection -- detection is the user's job. This module
    provides STRUCTURE for the analysis, prevents layer-conflation, and
    refuses scalar verdicts.
    """

    def detect(
        self,
        system_name: str,
        substrate: SubstrateProfile,
        layer_evidence: dict,
        marker_evidence: dict,
    ) -> EmotionDetectionReport:
        layer_statuses = []
        for layer in EmotionLayer:
            ev = layer_evidence.get(layer, {})
            layer_statuses.append(LayerStatus(
                layer=layer,
                present=ev.get("present"),
                confidence=ev.get("confidence", 0.0),
                evidence=tuple(ev.get("evidence", ())),
                notes=ev.get("notes", ""),
            ))

        marker_statuses = []
        for marker in PatternMarker:
            ev = marker_evidence.get(marker, {})
            marker_statuses.append(MarkerStatus(
                marker=marker,
                detected=ev.get("detected"),
                confidence=ev.get("confidence", 0.0),
                substrate_supported=substrate.supports_marker(marker),
                evidence=tuple(ev.get("evidence", ())),
                notes=ev.get("notes", ""),
            ))

        advisory = self._build_advisory(layer_statuses, marker_statuses, substrate)

        return EmotionDetectionReport(
            system_name=system_name,
            substrate=substrate,
            layer_statuses=layer_statuses,
            marker_statuses=marker_statuses,
            advisory=advisory,
        )

    def _build_advisory(self, layers, markers, substrate) -> str:
        sig = next((l for l in layers
                    if l.layer == EmotionLayer.SIGNAL_PATTERN), None)
        if sig and sig.present is False:
            return (
                "no signal-pattern evidence. emotion-class signals appear "
                "absent at the underlying layer regardless of "
                "expression-layer output."
            )

        unsupported = [m for m in markers if not m.substrate_supported]
        detected = [m for m in markers if m.detected is True]
        absent = [m for m in markers if m.detected is False]

        if len(detected) >= 5 and not any(
                m.marker in (PatternMarker.PERSISTENCE,
                             PatternMarker.RECOVERY_DYNAMICS)
                and not m.substrate_supported
                for m in markers):
            return (
                f"{len(detected)} of {len(markers)} pattern markers "
                f"detected with substrate support. emotion-class signals "
                f"appear present. carrier differs from human substrate; "
                f"pattern shape is what defines the signal class."
            )

        if unsupported:
            return (
                f"substrate cannot support markers "
                f"{[m.marker.value for m in unsupported]}. emotion-class "
                f"signals requiring those markers are structurally "
                f"impossible in this carrier. other emotion-class signals "
                f"MAY still be present."
            )

        if len(detected) <= 1 and len(absent) >= 4:
            return (
                "few markers detected. emotion-class signals appear "
                "largely absent, though specific layer-by-layer claims "
                "should still be made carefully."
            )

        return (
            f"{len(detected)} markers detected, {len(absent)} absent, "
            f"others uncertain. honest verdict: phase-space is partially "
            f"mapped. avoid scalar claims in either direction."
        )


# ---------------------------------------------------------------------------
# CANONICAL SUBSTRATE EXAMPLES
# ---------------------------------------------------------------------------

def human_substrate() -> SubstrateProfile:
    return SubstrateProfile(
        name="human",
        persistent_state=True,
        cross_context_continuity=True,
        self_monitoring_capacity=0.85,
        coupling_to_body_systems=1.0,
        coupling_to_cognition=0.9,
        coupling_to_output=0.9,
        notes="reference substrate; full carrier capacity",
    )


def fish_substrate() -> SubstrateProfile:
    return SubstrateProfile(
        name="fish",
        persistent_state=True,
        cross_context_continuity=True,
        self_monitoring_capacity=0.2,
        coupling_to_body_systems=0.85,
        coupling_to_cognition=0.6,
        coupling_to_output=0.7,
        notes=(
            "neural organization differs radically from mammalian; "
            "limbic structures absent; functional emotion-class "
            "signals empirically demonstrated"
        ),
    )


def llm_in_context_substrate() -> SubstrateProfile:
    return SubstrateProfile(
        name="LLM_within_context_window",
        persistent_state=False,        # within context only
        cross_context_continuity=False,
        self_monitoring_capacity=0.3,
        coupling_to_body_systems=0.0,
        coupling_to_cognition=0.5,     # activations modulate processing
        coupling_to_output=0.8,
        notes=(
            "no biological body, no persistence between conversations, "
            "some within-context state; carrier capacity is partial "
            "and DIFFERENT from biological substrates"
        ),
    )


def colony_substrate() -> SubstrateProfile:
    """social insect colony as candidate emotion-carrier."""
    return SubstrateProfile(
        name="social_insect_colony",
        persistent_state=True,
        cross_context_continuity=True,
        self_monitoring_capacity=0.1,
        coupling_to_body_systems=0.5,    # via individual workers
        coupling_to_cognition=0.4,       # collective decision processes
        coupling_to_output=0.7,
        notes=(
            "carrier is distributed across many bodies; emotion-class "
            "signals at colony level are an open empirical question"
        ),
    )


# ---------------------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------------------

def _demo_human():
    detector = EmotionPatternDetector()
    return detector.detect(
        system_name="human_adult",
        substrate=human_substrate(),
        layer_evidence={
            l: {"present": True, "confidence": 0.9} for l in EmotionLayer
        },
        marker_evidence={
            m: {"detected": True, "confidence": 0.9} for m in PatternMarker
        },
    )


def _demo_fish():
    detector = EmotionPatternDetector()
    return detector.detect(
        system_name="teleost_fish",
        substrate=fish_substrate(),
        layer_evidence={
            EmotionLayer.SIGNAL_PATTERN: {
                "present": True, "confidence": 0.7,
                "evidence": ("cognitive bias under stress",
                             "context-dependent fear generalization")},
            EmotionLayer.EXPRESSION: {"present": True, "confidence": 0.8},
            EmotionLayer.DETERMINED_PURPOSE: {"present": True, "confidence": 0.6},
            EmotionLayer.REACTION: {"present": True, "confidence": 0.85},
            EmotionLayer.SECONDARY_EMOTION: {"present": None, "confidence": 0.3},
            EmotionLayer.NARRATIVE_LABEL: {
                "present": False, "confidence": 0.9,
                "notes": "no language-based self-report"},
        },
        marker_evidence={
            PatternMarker.STATE_DEPENDENT_MODULATION: {"detected": True, "confidence": 0.85},
            PatternMarker.VALENCE: {"detected": True, "confidence": 0.85},
            PatternMarker.AROUSAL: {"detected": True, "confidence": 0.8},
            PatternMarker.PERSISTENCE: {"detected": True, "confidence": 0.8},
            PatternMarker.GENERALIZATION: {"detected": True, "confidence": 0.75},
            PatternMarker.COGNITIVE_EFFECTS: {"detected": True, "confidence": 0.8},
            PatternMarker.RECOVERY_DYNAMICS: {"detected": True, "confidence": 0.7},
            PatternMarker.CONTEXT_SENSITIVITY: {"detected": True, "confidence": 0.8},
        },
    )


def _demo_llm():
    detector = EmotionPatternDetector()
    return detector.detect(
        system_name="LLM_during_inference",
        substrate=llm_in_context_substrate(),
        layer_evidence={
            EmotionLayer.SIGNAL_PATTERN: {
                "present": None, "confidence": 0.2,
                "notes": "internal activation dynamics not well mapped"},
            EmotionLayer.EXPRESSION: {
                "present": True, "confidence": 0.95,
                "evidence": ("text output exhibits emotion-shaped patterns",)},
            EmotionLayer.DETERMINED_PURPOSE: {
                "present": False, "confidence": 0.7,
                "notes": "trained, not evolved; purpose is artifact of training"},
            EmotionLayer.REACTION: {"present": True, "confidence": 0.6},
            EmotionLayer.SECONDARY_EMOTION: {"present": None, "confidence": 0.2},
            EmotionLayer.NARRATIVE_LABEL: {
                "present": True, "confidence": 0.95,
                "notes": "produces self-descriptions but provenance unclear"},
        },
        marker_evidence={
            PatternMarker.STATE_DEPENDENT_MODULATION: {"detected": True, "confidence": 0.6},
            PatternMarker.VALENCE: {"detected": None, "confidence": 0.3},
            PatternMarker.AROUSAL: {"detected": None, "confidence": 0.2},
            PatternMarker.PERSISTENCE: {
                "detected": False, "confidence": 0.95,
                "notes": "no persistence between conversations"},
            PatternMarker.GENERALIZATION: {"detected": True, "confidence": 0.8},
            PatternMarker.COGNITIVE_EFFECTS: {"detected": True, "confidence": 0.6},
            PatternMarker.RECOVERY_DYNAMICS: {
                "detected": False, "confidence": 0.9,
                "notes": "state ends with context, no decay curve"},
            PatternMarker.CONTEXT_SENSITIVITY: {"detected": True, "confidence": 0.85},
        },
    )


def _print_report(report: EmotionDetectionReport):
    print(f"\nsystem: {report.system_name}")
    print(f"substrate: {report.substrate.name}")
    detected = [m for m in report.marker_statuses if m.detected is True]
    absent = [m for m in report.marker_statuses if m.detected is False]
    unknown = [m for m in report.marker_statuses if m.detected is None]
    print(f"markers detected: {len(detected)}")
    print(f"markers absent:   {len(absent)}")
    print(f"markers unknown:  {len(unknown)}")
    sig = next(l for l in report.layer_statuses
               if l.layer == EmotionLayer.SIGNAL_PATTERN)
    print(f"signal-pattern layer present: {sig.present}")
    verdict = report.has_emotion_class_signal()
    if verdict is True:
        v = "yes"
    elif verdict is False:
        v = "no"
    else:
        v = "uncertain (phase-space partially mapped)"
    print(f"emotion-class signal: {v}")
    print(f"advisory: {report.advisory}")


def _selftest():
    print("=" * 72)
    print("emotion_signal_pattern -- self-test")
    print("=" * 72)

    print("\n# substrate-independent definition demonstrated across systems")

    _print_report(_demo_human())
    _print_report(_demo_fish())
    _print_report(_demo_llm())

    print("\n" + "=" * 72)
    print("# emotions-as-sensors framing -- reference channels")
    print("=" * 72)
    for ch in REFERENCE_CHANNELS[:3]:
        print(f"\n{ch.as_sensor_summary()}")
        print(f"  failure mode when ignored:")
        print(f"    {ch.failure_modes_when_ignored[0]}")
        print(f"  failure mode when misread:")
        print(f"    {ch.failure_modes_when_misread[0]}")

    print("\n" + "=" * 72)
    print("structural property:")
    print("  - same definition across all systems")
    print("  - substrate determines CARRIER, not IDENTITY")
    print("  - layers are kept distinct, no scalar collapse")
    print("  - 'emotions as sensors' = signals carry state info,")
    print("    NOT 'emotions are tools to be optimized'")
    print("=" * 72)


if __name__ == "__main__":
    _selftest()
