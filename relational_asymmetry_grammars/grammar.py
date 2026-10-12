"""
relational_asymmetry_grammars / grammar.py

A stdlib-only engine for mapping unhealthy relational dynamics as GRAMMARS:
observable generative rules that produce recurring asymmetric load transfer,
stated WITHOUT attribution of motive, intent, emotion, or diagnosis.

Core constraint
---------------
A dynamic is described only by what is OBSERVABLE: the events, the rule that
relates them, the load that results, and the conditions under which the model
would be FALSE. No interior states. The same output (load accretion, asymmetry)
can be produced from fear, joy, habit, or anything else; the generator's
internal state is not measured and not required. Only the structure is.

Falsification doctrine
----------------------
Every dynamic ships with at least one condition under which it returns FALSE.
A model that predicts every outcome has zero information content and is itself
an instance of the self-sealing defect it is meant to detect. The harness can
return SUPPORTED, FALSIFIED, or UNDER_DETERMINED. UNDER_DETERMINED is a result,
not a failure.

License: CC0. stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# --------------------------------------------------------------------------- #
# Attribution linter
# --------------------------------------------------------------------------- #
# The constraint is enforced as code: descriptions are scanned for mentalistic
# / motive / diagnostic vocabulary. This is a warning tool, not a hard fail —
# but the framework's own content is expected to pass it (dogfooding).

ATTRIBUTION_MARKERS = (
    "wants", "want to", "wanting", "desires", "desire to",
    "intends", "intend to", "intention", "intentional", "intentionally",
    "tries to", "trying to", "attempts to",
    "in order to", "so that they", "so they can",
    "feels", "feeling", "emotion", "motivated by", "motive",
    "deliberately", "consciously", "on purpose", "purposely",
    "manipulat",          # manipulative / manipulation
    "malicious", "cruel on purpose", "narcissist", "abuser",
    "because they feel", "because they want",
)


def scan_for_attribution(text: str) -> list[str]:
    """Return the list of attribution markers found in `text` (lowercased match).

    A non-empty return means the description has smuggled motive/intent/emotion
    in and should be rewritten in observable terms.
    """
    low = text.lower()
    return [m for m in ATTRIBUTION_MARKERS if m in low]


# --------------------------------------------------------------------------- #
# Primitives
# --------------------------------------------------------------------------- #
class LoadKind(Enum):
    DISCRETE = "discrete"        # a one-shot prohibition / offloaded task (+1, step)
    CONTINUOUS = "continuous"    # a load held over time; cost scales with duration


@dataclass(frozen=True)
class Load:
    """A measurable prohibition or offloaded task that lands on one party."""
    name: str
    kind: LoadKind
    description: str

    def attribution_findings(self) -> list[str]:
        return scan_for_attribution(self.description)


@dataclass(frozen=True)
class Rule:
    """A generative rule of the grammar. Antecedent and consequent are both
    stated as OBSERVABLE events, never as inferred states."""
    rule_id: str
    antecedent: str
    consequent: str
    note: str = ""

    def attribution_findings(self) -> list[str]:
        return scan_for_attribution(
            " ".join([self.antecedent, self.consequent, self.note])
        )


@dataclass(frozen=True)
class Falsifier:
    """A condition under which the dynamic returns FALSE. Without at least one
    of these, a dynamic is not admissible."""
    falsifier_id: str
    condition: str           # observable condition that, if met, falsifies
    channel: str             # e.g. 'autonomous', 'decay', 'documentation'


@dataclass
class Dynamic:
    name: str
    observable_signature: str
    loads: list[Load] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    falsifiers: list[Falsifier] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Structural admissibility check. Returns a list of problems;
        empty list means admissible."""
        problems: list[str] = []
        if not self.falsifiers:
            problems.append(
                f"{self.name}: no falsifier — model is unfalsifiable, inadmissible."
            )
        attrib = scan_for_attribution(self.observable_signature)
        if attrib:
            problems.append(
                f"{self.name}: signature contains attribution markers {attrib}."
            )
        for r in self.rules:
            if r.attribution_findings():
                problems.append(
                    f"{self.name}/{r.rule_id}: rule contains attribution "
                    f"markers {r.attribution_findings()}."
                )
        for l in self.loads:
            if l.attribution_findings():
                problems.append(
                    f"{self.name}/{l.name}: load contains attribution "
                    f"markers {l.attribution_findings()}."
                )
        return problems


# --------------------------------------------------------------------------- #
# Cycles and the load ledger
# --------------------------------------------------------------------------- #
class ResetClass(Enum):
    RESPONSE_CONTINGENT = "response_contingent"   # trigger was the observer's action
    AUTONOMOUS = "autonomous"                     # time- or external-stress-keyed
    UNKNOWN = "unknown"                           # not yet separable


@dataclass
class Cycle:
    """One observed iteration. Every field is something you can log at the time;
    nothing here is inferred."""
    index: int
    reset_event: str                              # what immediately preceded re-arming
    reset_class: ResetClass
    restored_state: str                           # which configuration recurred
    threshold_marker: Optional[float]             # accommodation baseline this cycle
    initiative_in_interval: bool                  # did the observer take initiative
                                                  # in the interval preceding this reset?


@dataclass
class CycleLog:
    cycles: list[Cycle] = field(default_factory=list)

    # ---- drift ---------------------------------------------------------- #
    def threshold_series(self) -> list[tuple[int, float]]:
        return [
            (c.index, c.threshold_marker)
            for c in sorted(self.cycles, key=lambda x: x.index)
            if c.threshold_marker is not None
        ]

    def drift(self) -> Optional[float]:
        """Mean Δthreshold / Δcycle over the marked series, or None if < 2 marks."""
        s = self.threshold_series()
        if len(s) < 2:
            return None
        deltas = [
            (s[i + 1][1] - s[i][1]) / (s[i + 1][0] - s[i][0])
            for i in range(len(s) - 1)
        ]
        return sum(deltas) / len(deltas)

    def is_monotonic_nondecreasing(self) -> Optional[bool]:
        s = self.threshold_series()
        if len(s) < 2:
            return None
        return all(s[i + 1][1] >= s[i][1] for i in range(len(s) - 1))

    # ---- reset-class summary ------------------------------------------- #
    def response_contingent_fraction(self) -> Optional[float]:
        classed = [c for c in self.cycles if c.reset_class is not ResetClass.UNKNOWN]
        if not classed:
            return None
        rc = sum(
            1 for c in classed
            if c.reset_class is ResetClass.RESPONSE_CONTINGENT
        )
        return rc / len(classed)


# --------------------------------------------------------------------------- #
# Verdicts and the falsification harness
# --------------------------------------------------------------------------- #
class Verdict(Enum):
    SUPPORTED = "supported"
    FALSIFIED = "falsified"
    UNDER_DETERMINED = "under_determined"


@dataclass
class Finding:
    claim: str
    verdict: Verdict
    basis: str


def run_falsification(log: CycleLog) -> list[Finding]:
    """Apply the standing falsification channels to a cycle log.

    Returns a list of Findings. Nothing here CONFIRMS by accumulation of
    supporting cases; a finding can only be SUPPORTED in the weak sense of
    'not yet falsified, given enough data to test', and is otherwise
    UNDER_DETERMINED.
    """
    findings: list[Finding] = []

    # --- Channel 1: response-contingency -------------------------------- #
    # Falsified if the threshold ever RISES across an interval in which the
    # observer took NO initiative (autonomous accretion -> 'necessary' clause
    # of the response-contingent rule is false).
    autonomous_rise = False
    prev: Optional[Cycle] = None
    for c in sorted(log.cycles, key=lambda x: x.index):
        if (
            prev is not None
            and not c.initiative_in_interval
            and c.threshold_marker is not None
            and prev.threshold_marker is not None
            and c.threshold_marker > prev.threshold_marker
        ):
            autonomous_rise = True
        prev = c

    rcf = log.response_contingent_fraction()
    have_no_initiative_interval = any(
        not c.initiative_in_interval for c in log.cycles
    )
    if autonomous_rise:
        findings.append(Finding(
            "Reset is response-contingent (keyed to observer initiative).",
            Verdict.FALSIFIED,
            "Threshold rose across a no-initiative interval: an autonomous "
            "driver exists. Restraint by the observer would not stop accretion.",
        ))
    elif not have_no_initiative_interval:
        findings.append(Finding(
            "Reset is response-contingent (keyed to observer initiative).",
            Verdict.UNDER_DETERMINED,
            "No clean no-initiative interval is logged. The response-contingent "
            "reading cannot be separated from the data. Run a prospective "
            "no-initiative window with the threshold marked at both ends.",
        ))
    else:
        findings.append(Finding(
            "Reset is response-contingent (keyed to observer initiative).",
            Verdict.SUPPORTED,
            f"No autonomous rise observed across logged no-initiative "
            f"interval(s); response-contingent fraction = {rcf}. Weakly "
            "supported, not confirmed.",
        ))

    # --- Channel 2: accretion / non-decay ------------------------------- #
    mono = log.is_monotonic_nondecreasing()
    if mono is None:
        findings.append(Finding(
            "Accommodation threshold accretes (non-decreasing).",
            Verdict.UNDER_DETERMINED,
            "Fewer than two marked threshold points; cannot compute drift.",
        ))
    elif mono is False:
        findings.append(Finding(
            "Accommodation threshold accretes (non-decreasing).",
            Verdict.FALSIFIED,
            "Threshold marker decays at least once across the series. The "
            "accretion model does not hold for this case.",
        ))
    else:
        d = log.drift()
        findings.append(Finding(
            "Accommodation threshold accretes (non-decreasing).",
            Verdict.SUPPORTED,
            f"Threshold series non-decreasing; mean drift = {d:.3f} "
            "load-units/cycle. Weakly supported.",
        ))

    return findings
