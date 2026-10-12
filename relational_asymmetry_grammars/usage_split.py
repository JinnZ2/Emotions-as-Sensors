"""
relational_asymmetry_grammars / usage_split.py

The same word can be used two different ways:

  (A) OBSERVABLE-EFFECT usage  — the word names an act, effect, or pattern.
                                 Clean. Usable. Stays falsifiable.
  (B) ATTRIBUTIVE usage        — the word labels the PERSON as a trait, nature,
                                 motive, or diagnosis. Smuggles the unobservable.

"Manipulation occurred" (an effect) is not "she is manipulative" (a trait).
"Narcissistic behavior" (a pattern) does not require "he is a narcissist" (an
identity). The constraint is not on the word — it is on whether the word is
pinned to an act or pinned to a person.

Three tiers
-----------
  SPLITTABLE   : has a clean observable usage AND an attributive usage. Keep the
                 observable form; flag the attributive form.
  REPLACE_ONLY : functions only as a verdict; no clean observable usage exists.
                 Replace the word entirely with the named load/asymmetry.
  SENSITIVE    : an observable category exists, but the usable form requires
                 naming the SPECIFIC act, never the label on the person.

Where possible, a `decomposition` field gives the strongest observable form —
usually a mapping to a rule in DYNAMICS.md. Pattern-naming is acceptable
shorthand; decomposition to the rule is stronger.

License: CC0. stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Tier(Enum):
    SPLITTABLE = "splittable"
    REPLACE_ONLY = "replace_only"
    SENSITIVE = "sensitive"


@dataclass(frozen=True)
class UsageSplit:
    term: str
    tier: Tier
    observable_usage: str      # how the word names an act/effect/pattern (clean)
    attributive_usage: str     # how the word labels the person (flagged)
    clean_example: str
    flagged_example: str
    decomposition: str         # strongest observable form (often a rule mapping)


SPLITS: tuple[UsageSplit, ...] = (
    UsageSplit(
        term="manipulation / manipulative",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a noun naming an effect: information is selectively presented or "
            "reframed so that the available choices are narrowed."
        ),
        attributive_usage=(
            "As an adjective on the person: asserts a stable trait and an aim "
            "('she is manipulative') — neither observed."
        ),
        clean_example=(
            "The choice was framed so that one option carried a pre-coded "
            "penalty; this is a manipulation of the option set."
        ),
        flagged_example="She is manipulative.",
        decomposition=(
            "Map to Self-Sealing Reframe (R1) or to a pre-coding rule: name the "
            "specific reframe and the load it transfers."
        ),
    ),
    UsageSplit(
        term="narcissistic / narcissist",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a pattern-category on behavior: a recurring sequence in which "
            "one party's account is treated as the only admissible account."
        ),
        attributive_usage=(
            "As an identity on the person ('he is a narcissist'): a clinical "
            "label applied to a whole person from outside a diagnosis."
        ),
        clean_example=(
            "The behavior fits the narcissistic pattern: competing accounts were "
            "reclassified as attacks rather than evaluated."
        ),
        flagged_example="He is a narcissist.",
        decomposition=(
            "Drop the category if you can; name the rule (e.g. competing account "
            "-> reclassified as hostility) and the burden-of-proof transfer."
        ),
    ),
    UsageSplit(
        term="controlling / control",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a named constraint: a specific limit is imposed on a degree of "
            "freedom (schedule, contact, spending)."
        ),
        attributive_usage=(
            "As a trait on the person ('he is controlling'): a disposition "
            "asserted across all situations."
        ),
        clean_example=(
            "A constraint was imposed on the schedule: alternatives proposed by "
            "the other party were reclassified as conflict."
        ),
        flagged_example="He is so controlling.",
        decomposition=(
            "Name which degree of freedom was constrained and which load the "
            "constraint transferred."
        ),
    ),
    UsageSplit(
        term="gaslighting",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a named reframe pattern: a stated observation is met by "
            "asserting the observation did not occur or proves a fault in the "
            "observer."
        ),
        attributive_usage=(
            "As a role on the person ('he is a gaslighter'): an identity rather "
            "than a described sequence."
        ),
        clean_example=(
            "The observation was reclassified as the observer's instability "
            "rather than evaluated — the Self-Sealing Reframe pattern."
        ),
        flagged_example="He is a gaslighter.",
        decomposition="Map directly to Self-Sealing Reframe (R1, R2).",
    ),
    UsageSplit(
        term="defensive / defensiveness",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a named response: an observation is met by shifting the topic "
            "from its content to the character of the one naming it."
        ),
        attributive_usage=(
            "As a trait ('she is so defensive'): a disposition asserted, and a "
            "verdict implied."
        ),
        clean_example=(
            "The response did not address the content; it reclassified the act "
            "of naming as an attack (a defensive reframe)."
        ),
        flagged_example="She's always so defensive.",
        decomposition="Map to Self-Sealing Reframe (R1).",
    ),
    UsageSplit(
        term="dismissive",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a named response: an observation is not evaluated on its content "
            "before being set aside."
        ),
        attributive_usage=(
            "As a trait ('he is dismissive'): a disposition asserted across "
            "situations."
        ),
        clean_example="The observation was set aside without its content being addressed.",
        flagged_example="He is dismissive.",
        decomposition="Name the specific observation and that its content went unaddressed.",
    ),
    UsageSplit(
        term="passive-aggressive",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a named sequence: a grievance is expressed through an indirect "
            "act rather than stated directly."
        ),
        attributive_usage=(
            "As a trait label on the person, asserting a stable disposition."
        ),
        clean_example=(
            "The grievance was expressed through a delayed task rather than "
            "stated, leaving the other party to infer it."
        ),
        flagged_example="He's passive-aggressive.",
        decomposition="Name the indirect act and the inference load it transfers.",
    ),
    UsageSplit(
        term="withdrawal / avoidant",
        tier=Tier.SPLITTABLE,
        observable_usage=(
            "As a named act: contact or engagement is reduced following a "
            "specific event."
        ),
        attributive_usage=(
            "As an attachment-style label ('he is avoidant'): a diagnosis "
            "applied to the person."
        ),
        clean_example="Engagement dropped after the standard was raised.",
        flagged_example="He's just avoidant.",
        decomposition="Name the antecedent event and the observed reduction; drop the style label.",
    ),
    UsageSplit(
        term="abuse / abusive",
        tier=Tier.SENSITIVE,
        observable_usage=(
            "As a category of act: a specific harmful act is named and located. "
            "The usable form is the named act, never the label on the person."
        ),
        attributive_usage=(
            "As an identity ('he is abusive'): a whole-person label that "
            "replaces the specific act with a verdict."
        ),
        clean_example="On [date], [specific act] occurred; it transferred [load].",
        flagged_example="He is abusive.",
        decomposition=(
            "Name the specific act, the date, and the load. Do not compress to "
            "the label. (Safety note: naming acts observably is also what makes "
            "a record usable by others later.)"
        ),
    ),
    UsageSplit(
        term="toxic",
        tier=Tier.REPLACE_ONLY,
        observable_usage="(none) — the word delivers a verdict, not an observation.",
        attributive_usage="Applied to a person or relationship as a global appraisal.",
        clean_example="(replace) The exchange transferred load X to one ledger and none to the other.",
        flagged_example="The relationship is toxic.",
        decomposition="Replace entirely: name the load, the asymmetry, the ledger.",
    ),
    UsageSplit(
        term="selfish",
        tier=Tier.REPLACE_ONLY,
        observable_usage="(none) — asserts an interior orientation and ranks it.",
        attributive_usage="A trait-plus-verdict applied to the person.",
        clean_example="(replace) The cost was externalized: it landed on one party and not the other.",
        flagged_example="She's selfish.",
        decomposition="Replace with the externalized-cost description.",
    ),
    UsageSplit(
        term="unfair",
        tier=Tier.REPLACE_ONLY,
        observable_usage="(none) — a verdict about a norm that is left unstated.",
        attributive_usage="Applied to an outcome or person as a judgment.",
        clean_example="(replace) Load L falls on party A each cycle and on party B in none.",
        flagged_example="It's unfair.",
        decomposition="State the asymmetry as counts per ledger; surface the norm as a condition.",
    ),
)


SPLIT_INDEX: dict[str, UsageSplit] = {s.term: s for s in SPLITS}


def show(term_substring: str = "") -> str:
    """Print the usage split for terms whose name contains `term_substring`
    (case-insensitive). Empty string shows all."""
    q = term_substring.lower()
    hits = [s for s in SPLITS if q in s.term.lower()]
    if not hits:
        return f"No usage split found for '{term_substring}'."
    blocks = []
    for s in hits:
        blocks.append(
            f"{s.term}   [{s.tier.value}]\n"
            f"  OBSERVABLE : {s.observable_usage}\n"
            f"  ATTRIBUTIVE: {s.attributive_usage}\n"
            f"  clean      : {s.clean_example}\n"
            f"  flagged    : {s.flagged_example}\n"
            f"  strongest  : {s.decomposition}"
        )
    return "\n\n".join(blocks)


if __name__ == "__main__":
    import sys
    print(show(sys.argv[1] if len(sys.argv) > 1 else ""))
