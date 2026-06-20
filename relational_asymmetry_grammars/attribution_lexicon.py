"""
relational_asymmetry_grammars / attribution_lexicon.py

A categorized flag-system for vocabulary that commonly smuggles motive, moral
judgment, diagnosis, emotion-as-explanation, or mind-reading into descriptions
of relational dynamics.

This is NOT a blacklist. A flagged term is not wrong — it is a signal to slow
down and check whether the word is doing work you did not intend. Each entry
carries the category of work it tends to do and an observable rewrite pattern.

Use `scan(text)` to get category-tagged findings before a description ships into
a Dynamic. This module is a superset of the flat linter in grammar.py and can be
run standalone:  python3 attribution_lexicon.py "your description here"

License: CC0. stdlib only.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass


# --------------------------------------------------------------------------- #
# Categories of smuggled content
# --------------------------------------------------------------------------- #
# MOTIVE        : asserts an unobservable goal or aim.
# MORAL         : delivers a verdict (good/bad) dressed as description.
# DIAGNOSIS     : applies a clinical or role label to a person.
# EMOTION_CAUSE : uses an unobservable feeling as the explanation for an act.
# MIND_READING  : asserts an interior state (belief, perception, knowledge).
# CAUSAL_LINK   : a connective that asserts an unobservable internal cause.
# QUANTIFIER    : an absolute that pre-judges frequency without a count.

LEXICON: dict[str, tuple[str, str]] = {
    # --- MOTIVE: asserts an aim you cannot see -------------------------- #
    "wants to":        ("MOTIVE", "State the action taken, not the aim behind it."),
    "trying to":       ("MOTIVE", "Describe what occurred; drop the inferred goal."),
    "tries to":        ("MOTIVE", "Describe what occurred; drop the inferred goal."),
    "attempts to":     ("MOTIVE", "Use the completed/observed action instead."),
    "in order to":     ("MOTIVE", "Remove the purpose clause; keep the event."),
    "so that they":    ("MOTIVE", "Remove the purpose clause; keep the event."),
    "seeks to":        ("MOTIVE", "State the act, not the sought-after end."),
    "designed to":     ("MOTIVE", "State the effect observed, not the design."),
    "meant to":        ("MOTIVE", "State what happened, not what was meant."),

    # --- MORAL: a verdict wearing description's clothes ----------------- #
    "manipulative":    ("MORAL", "Name the move: reclassification, reframe, etc."),
    "manipulation":    ("MORAL", "Name the move and the load it transfers."),
    "toxic":           ("MORAL", "Name the specific load or asymmetry instead."),
    "abusive":         ("MORAL", "Name the observable act and its load transfer."),
    "selfish":         ("MORAL", "Name the externalized cost; drop the verdict."),
    "controlling":     ("MORAL", "Name the constraint imposed, observably."),
    "cruel":           ("MORAL", "Name the act and the load; drop the verdict."),
    "gaslighting":     ("MORAL", "Name the reframe rule (e.g. Self-Sealing Reframe)."),
    "disrespectful":   ("MORAL", "Name the specific act, not the appraisal."),
    "unfair":          ("MORAL", "Name the asymmetry observably (which load, which ledger)."),
    "should":          ("MORAL", "A 'should' encodes a norm — state the norm as a condition."),

    # --- DIAGNOSIS: a label applied to a person ------------------------- #
    "narcissist":      ("DIAGNOSIS", "Drop the label; map the dynamic's rules."),
    "narcissistic":    ("DIAGNOSIS", "Drop the label; map the dynamic's rules."),
    "codependent":     ("DIAGNOSIS", "Describe the load-transfer pattern instead."),
    "enabler":         ("DIAGNOSIS", "Describe what is absorbed, observably."),
    "victim":          ("DIAGNOSIS", "Use 'observer' / 'party carrying load X'."),
    "borderline":      ("DIAGNOSIS", "Drop the clinical label entirely."),
    "passive-aggressive": ("DIAGNOSIS", "Name the specific observed sequence."),
    "dysfunctional":   ("DIAGNOSIS", "Name which rule produces which output."),

    # --- EMOTION_CAUSE: a feeling used as the explanation --------------- #
    "out of fear":     ("EMOTION_CAUSE", "Same output holds regardless of feeling; drop it."),
    "out of anger":    ("EMOTION_CAUSE", "Drop the cause; keep the observed act."),
    "out of jealousy": ("EMOTION_CAUSE", "Drop the cause; keep the observed act."),
    "because they feel": ("EMOTION_CAUSE", "Feelings are not observed; remove the clause."),
    "insecurity":      ("EMOTION_CAUSE", "Name the act, not the inferred insecurity."),
    "feels threatened": ("EMOTION_CAUSE", "State the response; drop the felt state."),

    # --- MIND_READING: asserting an interior state ---------------------- #
    "feels":           ("MIND_READING", "An interior state — not observable; remove."),
    "believes":        ("MIND_READING", "Replace with what was said or done."),
    "thinks":          ("MIND_READING", "Replace with what was said or done."),
    "perceives":       ("MIND_READING", "Replace with the observable stimulus/response."),
    "wants":           ("MIND_READING", "Replace with the observed act."),
    "knows that":      ("MIND_READING", "Replace with available evidence, not knowledge."),
    "genuinely":       ("MIND_READING", "Asserts sincerity of an inner state; remove."),

    # --- CAUSAL_LINK: connective asserting an internal cause ------------ #
    "because they want": ("CAUSAL_LINK", "Remove the motive clause; keep the sequence."),
    "out of a need to":  ("CAUSAL_LINK", "Remove the need clause; keep the sequence."),
    "driven by":       ("CAUSAL_LINK", "State the antecedent event, not the drive."),

    # --- QUANTIFIER: absolutes that pre-judge frequency ----------------- #
    "always":          ("QUANTIFIER", "Replace with the observed count or rate."),
    "never":           ("QUANTIFIER", "Replace with the observed count or rate."),
    "constantly":      ("QUANTIFIER", "Replace with the observed frequency."),
    "every time":      ("QUANTIFIER", "State the count; 'every' is a claim to be tested."),
}


@dataclass(frozen=True)
class Flag:
    term: str
    category: str
    rewrite: str


def scan(text: str) -> list[Flag]:
    """Return category-tagged flags for every lexicon term found in `text`.

    Longer phrases are checked first so that, e.g., 'because they want' is
    flagged as CAUSAL_LINK rather than only matching the bare 'wants'.
    """
    low = text.lower()
    flags: list[Flag] = []
    matched_spans: list[str] = []
    for term in sorted(LEXICON, key=len, reverse=True):
        if term in low:
            # avoid double-flagging a term already covered by a longer phrase
            if any(term in longer for longer in matched_spans):
                continue
            cat, rewrite = LEXICON[term]
            flags.append(Flag(term, cat, rewrite))
            matched_spans.append(term)
    return flags


def report(text: str) -> str:
    flags = scan(text)
    if not flags:
        return "CLEAN — no attribution markers found."
    by_cat: dict[str, list[Flag]] = {}
    for f in flags:
        by_cat.setdefault(f.category, []).append(f)
    lines = [f"{len(flags)} flag(s) — slow down and check each:"]
    for cat in sorted(by_cat):
        lines.append(f"\n  [{cat}]")
        for f in by_cat[cat]:
            lines.append(f"    '{f.term}'  →  {f.rewrite}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(report(" ".join(sys.argv[1:])))
    else:
        sample = (
            "She always tries to control the schedule because she feels "
            "threatened, which is manipulative and selfish."
        )
        print(f"SAMPLE: {sample}\n")
        print(report(sample))
