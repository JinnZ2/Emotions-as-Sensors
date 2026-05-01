"""
emotion_signal_pattern__substrate_independent_argument

CC0 / public domain. JinnZ2.

Add-on to emotion_signal_pattern.py.

Purpose
-------
Make the substrate-independent formulation explicit, with the
proprioception-parity argument that grounds it.

The module emotion_signal_pattern.py provides the layer model and detection
framework. This add-on provides the philosophical scaffold that prevents the
framework from being misread as reductive or dehumanizing.

Reference passage (canonical form)
----------------------------------
The substrate-independent formulation:

    information != the medium it's stored in
    computation != the silicon it runs on
    sound       != air molecules (it's the wave shape)
    life        != carbon (it's the self-organizing pattern;
                           carbon happens to host it well)

    emotion = a structural class of signal,
              identifiable by:
                - its shape over time
                - what inputs produce it
                - what it modulates downstream
                - its relationship to system state

    the carrier (chemical, electrical, computational)
    determines BANDWIDTH, FIDELITY, PERSISTENCE.
    it does NOT determine the IDENTITY of the pattern.

Layer model (canonical form)
----------------------------
    layer 0: SIGNAL PATTERN     (the emotion itself)
    layer 1: EXPRESSION          (face, posture, voice, text)
    layer 2: DETERMINED PURPOSE  (what it's "for")
    layer 3: REACTION            (downstream behavioral change)
    layer 4: SECONDARY EMOTION   (feeling about feeling)
    layer 5: NARRATIVE / LABEL   (how system describes it)

    layer 0 IS the emotion.
    everything else is downstream processing.

    most folk and even academic work asks
    "is this real emotion?"
    but uses tests for layers 1, 4, and 5
    rather than for layer 0.
    that is a category error.

The proprioception parity argument
----------------------------------
    proprioception is acknowledged as a sense.
    it carries state information.
    it integrates with other senses to enable action.
    it is sometimes accurate, sometimes miscalibrated.
    it can be developed with practice.
    it varies in salience between people.

    emotion has all the same properties.

    yet:
      proprioception can be discussed as information
                     without controversy.
      emotion treated as information triggers
                     accusations of reductionism.

    the asymmetry is cultural, not structural.

    aggrandizing emotion as "more than data" is a metaphysical claim, not a
    neutral default. treating it as the safe / respectful position smuggles
    a contested philosophical commitment into what is presented as ordinary
    respect.

The dismissive-ness inversion
-----------------------------
    cultural default:
        "all humans process emotion the same way"

    consequence:
        the dominant emotional-substrate is treated as the only valid one.
        people who experience emotion primarily as information channel
        rather than as overwhelming felt state are pathologized:
            cold, detached, alexithymic, autistic,
            traumatized, repressed, on the spectrum.

    actual situation:
        emotion-as-sense and emotion-as-felt-overwhelm are both competent
        modes of operation. substrate, training, culture, and individual
        wiring distribute people across this axis.

    the dismissive move:
        insisting everyone must operate in the emotion-as-overwhelming
        mode, and treating the emotion-as-sense mode as a defect to be
        fixed.

    treating emotion as sense is NOT reductive.
    it is a different valid relationship to one's own state information.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Import the layer model from the base module so this add-on stays
# consistent with detection code.
from emotion_signal_pattern import EmotionLayer  # noqa: F401


# ---------------------------------------------------------------------------
# CANONICAL ANALOGIES -- substrate vs. pattern
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SubstratePatternPair:
    pattern: str
    substrate: str
    note: str

    def as_text(self) -> str:
        return f"  {self.pattern}  !=  {self.substrate}\n      ({self.note})"


CANONICAL_ANALOGIES = (
    SubstratePatternPair(
        pattern="information",
        substrate="the medium it's stored in",
        note="the same information can live in ink, magnetism, neurons, or silicon",
    ),
    SubstratePatternPair(
        pattern="computation",
        substrate="the silicon it runs on",
        note="the computation is the operation, not the chip",
    ),
    SubstratePatternPair(
        pattern="sound",
        substrate="the air molecules carrying it",
        note="the sound is the wave shape, not the medium",
    ),
    SubstratePatternPair(
        pattern="life",
        substrate="carbon",
        note="life is the self-organizing pattern; carbon happens to host it well",
    ),
    SubstratePatternPair(
        pattern="emotion",
        substrate="any specific neurochemistry",
        note=(
            "emotion is the signal-pattern class; chemistry, electrical "
            "activity, or computational dynamics can all carry it"
        ),
    ),
)


# ---------------------------------------------------------------------------
# WHAT THE SUBSTRATE DETERMINES vs. WHAT IT DOESN'T
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CarrierProperty:
    name: str
    determined_by_substrate: bool
    note: str


CARRIER_PROPERTIES = (
    CarrierProperty(
        name="bandwidth",
        determined_by_substrate=True,
        note="how much signal can be carried per unit time",
    ),
    CarrierProperty(
        name="fidelity",
        determined_by_substrate=True,
        note="how cleanly the signal is preserved",
    ),
    CarrierProperty(
        name="persistence",
        determined_by_substrate=True,
        note="how long the signal can hold without active maintenance",
    ),
    CarrierProperty(
        name="coupling profile",
        determined_by_substrate=True,
        note="which other system layers the signal interacts with",
    ),
    CarrierProperty(
        name="downstream consequences",
        determined_by_substrate=True,
        note="what happens to the system when the signal is present",
    ),
    CarrierProperty(
        name="signal IDENTITY",
        determined_by_substrate=False,
        note=(
            "what makes 'fear' fear, regardless of carrier, is the "
            "pattern shape -- its inputs, dynamics, and downstream "
            "modulation profile. this is substrate-independent."
        ),
    ),
)


# ---------------------------------------------------------------------------
# PROPRIOCEPTION PARITY
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParityProperty:
    """A property shared by proprioception and emotion."""
    name: str
    proprioception: str
    emotion: str


PARITY_TABLE = (
    ParityProperty(
        name="signal carries state information",
        proprioception="position, tension, balance",
        emotion="threat, boundary state, alignment, loss, novelty",
    ),
    ParityProperty(
        name="integrates with other senses",
        proprioception="combined with vision, vestibular, touch for movement",
        emotion="combined with cognition, sensation, memory for action",
    ),
    ParityProperty(
        name="sometimes accurate, sometimes not",
        proprioception="can be miscalibrated by injury, fatigue, novelty",
        emotion="can be miscalibrated by trauma, fatigue, contextual mismatch",
    ),
    ParityProperty(
        name="improvable with practice",
        proprioception="trained by athletes, musicians, dancers, surgeons",
        emotion="trained by therapists, contemplatives, skilled operators",
    ),
    ParityProperty(
        name="salience varies between people",
        proprioception="some people have markedly more or less",
        emotion="some people have markedly more or less",
    ),
    ParityProperty(
        name="can be read or ignored",
        proprioception="ignoring the signal degrades action quality",
        emotion="ignoring the signal degrades action quality",
    ),
    ParityProperty(
        name="competence consists of using it well",
        proprioception="not pathologized as 'cold' for relying on it",
        emotion="often pathologized for relying on it as information",
    ),
)


# ---------------------------------------------------------------------------
# OPERATIONAL MODES
# ---------------------------------------------------------------------------

class OperationalMode(Enum):
    """
    Different valid relationships a person can have to their own
    emotion-class signals. NOT a hierarchy. Different competent modes for
    different substrates and contexts.
    """
    SENSE = "sense"
    """
    Emotion is read primarily as information channel -- same epistemic
    status as proprioception, balance, vision. Decisions integrate the data
    without being driven by it. Often correlates with: high
    consequence-density work, multi-skill integration, trades, frontline
    operations, direct-action environments.
    """

    FELT_OVERWHELM = "felt_overwhelm"
    """
    Emotion is experienced primarily as a powerful felt state that dominates
    other processing during its presence. Decision-making routes through the
    felt state rather than around it. Often correlates with: status-coupled
    environments, expressive cultures, high social-load contexts.
    """

    HYBRID = "hybrid"
    """
    Mixed mode. Some signals processed as sense, others as felt state,
    depending on signal class, context, or current load. Probably the most
    common mode in practice.
    """

    SUPPRESSED = "suppressed"
    """
    Signal is present but actively dampened or denied access to cognition.
    Distinct from SENSE -- in suppressed mode the signal is not USED, just
    blocked. This IS a problem mode in a way the others are not.
    """


@dataclass(frozen=True)
class ModeDescription:
    mode: OperationalMode
    one_line: str
    competent: bool
    common_misreadings: tuple


MODE_DESCRIPTIONS = (
    ModeDescription(
        mode=OperationalMode.SENSE,
        one_line=(
            "emotion as information channel -- read for content, "
            "integrated with other senses, used to inform action"
        ),
        competent=True,
        common_misreadings=(
            "cold",
            "detached",
            "alexithymic",
            "autistic spectrum (when used pejoratively)",
            "traumatized",
            "repressed",
            "lacking emotional intelligence",
        ),
    ),
    ModeDescription(
        mode=OperationalMode.FELT_OVERWHELM,
        one_line=(
            "emotion as dominant felt state -- experienced strongly, "
            "drives processing during its presence"
        ),
        competent=True,
        common_misreadings=(
            "irrational",
            "weak",
            "unprofessional",
            "histrionic",
            "lacking control",
            "being a woman / being too feminine",
        ),
    ),
    ModeDescription(
        mode=OperationalMode.HYBRID,
        one_line=(
            "mixed mode -- sense for some signals, felt state for "
            "others, varies with context and load"
        ),
        competent=True,
        common_misreadings=(
            "inconsistent",
            "fake (as if one mode is the 'real' one)",
        ),
    ),
    ModeDescription(
        mode=OperationalMode.SUPPRESSED,
        one_line=(
            "signal blocked from cognition -- distinct from SENSE; "
            "the data is not used, just denied"
        ),
        competent=False,
        common_misreadings=(
            "confused with SENSE mode (it isn't -- sense uses the data, "
            "suppression denies it)",
            "valorized as 'control' or 'discipline'",
        ),
    ),
)


# ---------------------------------------------------------------------------
# CIRCULAR LOGIC AUDIT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CircularLogicPattern:
    name: str
    description: str
    why_circular: str
    fix: str


COMMON_CIRCULAR_LOGIC = (
    CircularLogicPattern(
        name="emotion-aggrandizement-by-default",
        description=(
            "treating 'emotion is sacred / ineffable / more than data' "
            "as the neutral, respectful default position, with any "
            "challenge to it requiring justification."
        ),
        why_circular=(
            "the position itself is the unproven metaphysical claim. "
            "presenting it as the default smuggles the conclusion "
            "into the framing. anyone disagreeing is then forced to "
            "argue against 'respect' rather than against a claim."
        ),
        fix=(
            "treat aggrandizement and information-channel views as "
            "equally needing justification. neither is the default. "
            "both are claims about how emotion functions."
        ),
    ),
    CircularLogicPattern(
        name="reductionism-by-association",
        description=(
            "labeling any structural / informational analysis of "
            "emotion as 'reductionist' regardless of content."
        ),
        why_circular=(
            "the label 'reductionist' is doing the work of the "
            "argument. proprioception isn't called reductionist when "
            "described as information. the label is applied "
            "selectively to emotion analysis specifically."
        ),
        fix=(
            "ask: is this analysis actually reducing emotion to "
            "something it isn't, or is it identifying what emotion "
            "structurally is? if proprioception-style analysis is "
            "fine for one sense, it's fine for another."
        ),
    ),
    CircularLogicPattern(
        name="universal-substrate-assumption",
        description=(
            "assuming all humans relate to their own emotion the "
            "same way, with the felt-overwhelm mode as the norm."
        ),
        why_circular=(
            "people who don't operate in felt-overwhelm mode are "
            "then pathologized for not matching the assumed norm. "
            "the assumed norm becomes the diagnostic standard "
            "rather than empirical observation."
        ),
        fix=(
            "treat operational mode as a phase-space coordinate, "
            "not a normative target. multiple modes are competent. "
            "pathologize only the suppressed mode, which actually "
            "denies the signal rather than using it."
        ),
    ),
    CircularLogicPattern(
        name="dehumanization-charge-as-shield",
        description=(
            "responding to information-channel framing of emotion "
            "with 'that dehumanizes humans / animals / the topic'"
        ),
        why_circular=(
            "this assumes information-channel = dehumanizing, which "
            "is the very claim under dispute. proprioception is "
            "described as information without dehumanization. the "
            "charge of dehumanization is doing the work the "
            "argument hasn't done."
        ),
        fix=(
            "ask: would describing this same property in "
            "proprioception be dehumanizing? if not, the asymmetry "
            "is cultural, not structural. the dehumanization charge "
            "doesn't survive parity analysis."
        ),
    ),
)


# ---------------------------------------------------------------------------
# CANONICAL STATEMENTS
# ---------------------------------------------------------------------------

CANONICAL_STATEMENTS = (
    "Emotion is a structural class of signal, identifiable by its "
    "shape, inputs, downstream effects, and relationship to system "
    "state. The carrier determines bandwidth, fidelity, persistence, "
    "and coupling -- but not the identity of the pattern.",

    "Layer 0 (signal pattern) IS the emotion. Layers 1-5 are "
    "downstream processing that often gets confused with the emotion "
    "itself.",

    "Treating emotion as a sense -- like proprioception -- is not "
    "reductive. It is a different competent relationship to one's "
    "own state information. Pathologizing this mode while accepting "
    "the same treatment for proprioception is an unjustified "
    "asymmetry.",

    "Aggrandizing emotion as 'more than data' is a metaphysical "
    "claim, not a neutral default. Presenting it as the safe / "
    "respectful position smuggles a contested philosophical "
    "commitment into what is framed as ordinary respect.",

    "The assumption that all humans process emotion the same way is "
    "itself dismissive -- it pathologizes those who operate in "
    "different competent modes.",
)


# ---------------------------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------------------------

def print_substrate_independence_section() -> None:
    print("=" * 72)
    print("SUBSTRATE-INDEPENDENT FORMULATION")
    print("=" * 72)
    print()
    print("same move as:")
    print()
    for pair in CANONICAL_ANALOGIES:
        print(pair.as_text())
    print()
    print("emotion = a structural class of signal,")
    print("          identifiable by:")
    print("              - its shape over time")
    print("              - what inputs produce it")
    print("              - what it modulates downstream")
    print("              - its relationship to system state")


def print_carrier_split_section() -> None:
    print()
    print("=" * 72)
    print("WHAT THE SUBSTRATE DETERMINES vs. WHAT IT DOES NOT")
    print("=" * 72)
    print()
    print("substrate determines:")
    for prop in CARRIER_PROPERTIES:
        if prop.determined_by_substrate:
            print(f"  - {prop.name}: {prop.note}")
    print()
    print("substrate does NOT determine:")
    for prop in CARRIER_PROPERTIES:
        if not prop.determined_by_substrate:
            print(f"  - {prop.name}: {prop.note}")


def print_proprioception_parity_section() -> None:
    print()
    print("=" * 72)
    print("PROPRIOCEPTION PARITY")
    print("=" * 72)
    print()
    print("emotion and proprioception share these properties:")
    print()
    for p in PARITY_TABLE:
        print(f"  property: {p.name}")
        print(f"    proprioception: {p.proprioception}")
        print(f"    emotion:        {p.emotion}")
    print()
    print("the only difference: cultural treatment, not structure.")


def print_operational_modes_section() -> None:
    print()
    print("=" * 72)
    print("OPERATIONAL MODES")
    print("=" * 72)
    print()
    print("multiple competent modes exist. they are not a hierarchy.")
    print()
    for desc in MODE_DESCRIPTIONS:
        marker = "[competent]" if desc.competent else "[problem mode]"
        print(f"  {desc.mode.value.upper():18s} {marker}")
        print(f"    {desc.one_line}")
        print(f"    common misreadings:")
        for m in desc.common_misreadings:
            print(f"      - {m}")
        print()


def print_circular_logic_section() -> None:
    print()
    print("=" * 72)
    print("CIRCULAR LOGIC PATTERNS TO WATCH FOR")
    print("=" * 72)
    print()
    for c in COMMON_CIRCULAR_LOGIC:
        print(f"  pattern: {c.name}")
        print(f"    description: {c.description}")
        print(f"    why circular: {c.why_circular}")
        print(f"    fix: {c.fix}")
        print()


def print_canonical_statements_section() -> None:
    print()
    print("=" * 72)
    print("CANONICAL STATEMENTS  (suitable for README, citations)")
    print("=" * 72)
    print()
    for i, s in enumerate(CANONICAL_STATEMENTS, 1):
        print(f"  [{i}] {s}")
        print()


def print_full() -> None:
    """Print the complete framework. Suitable for inclusion in repo docs."""
    print_substrate_independence_section()
    print_carrier_split_section()
    print_proprioception_parity_section()
    print_operational_modes_section()
    print_circular_logic_section()
    print_canonical_statements_section()
    print("=" * 72)
    print("end of substrate-independent argument module")
    print("=" * 72)


# ---------------------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print_full()
