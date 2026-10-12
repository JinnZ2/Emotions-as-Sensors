"""
relational_asymmetry_grammars / dynamics.py

The first three dynamics, mapped in the stripped format. Work in progress.
Each is admissible only if it passes Dynamic.validate() (has a falsifier,
carries no attribution markers). Run this file to validate all three and to
see a worked example of the falsification harness on a cycle log.

License: CC0. stdlib only.
"""

from __future__ import annotations

from grammar import (
    Cycle, CycleLog, Dynamic, Falsifier, Load, LoadKind, ResetClass, Rule,
    run_falsification,
)


# --------------------------------------------------------------------------- #
# Dynamic 1 — Recruited Justification
# --------------------------------------------------------------------------- #
RECRUITED_JUSTIFICATION = Dynamic(
    name="Recruited Justification",
    observable_signature=(
        "A stated reason for an outcome fails when the same reason is applied "
        "to a structurally parallel case."
    ),
    loads=[
        Load(
            "parallel-scrutiny labor",
            LoadKind.DISCRETE,
            "The observer carries the work of testing the stated reason against "
            "parallel cases; this work is not performed by the other party.",
        ),
    ],
    rules=[
        Rule(
            "R1",
            antecedent="An outcome is fixed.",
            consequent="A reason is supplied after the outcome.",
            note="Order is observable: the reason appears in defense of an "
                 "already-fixed outcome.",
        ),
        Rule(
            "R2",
            antecedent="The supplied reason is applied to a parallel case.",
            consequent="The reason does not hold in the parallel case.",
            note="The reason is not stable across cases; it does not carry load.",
        ),
    ],
    falsifiers=[
        Falsifier(
            "F1",
            condition="The stated reason holds consistently across all "
                      "structurally parallel cases tested.",
            channel="parallel-case",
        ),
    ],
)


# --------------------------------------------------------------------------- #
# Dynamic 2 — Self-Sealing Reframe
# --------------------------------------------------------------------------- #
SELF_SEALING_REFRAME = Dynamic(
    name="Self-Sealing Reframe",
    observable_signature=(
        "Naming a pattern is responded to by reclassifying the act of naming "
        "as hostility; any following response is read as confirmation of the "
        "hostility."
    ),
    loads=[
        Load(
            "burden-of-proof transfer",
            LoadKind.DISCRETE,
            "The observer carries the burden of disproving an ascribed hostility "
            "that was never asserted by the observer.",
        ),
        Load(
            "reframe-absorption",
            LoadKind.CONTINUOUS,
            "The observer holds the reframe over time; the content of the "
            "original observation remains unexamined for the duration.",
        ),
    ],
    rules=[
        Rule(
            "R1",
            antecedent="A pattern is named.",
            consequent="The naming is reclassified as hostility.",
            note="Topic shifts from the content named to the act of naming.",
        ),
        Rule(
            "R2",
            antecedent="Any response is given to the reclassification.",
            consequent="The response is read as confirming the hostility.",
            note="Escalation, clarification, and silence are read identically.",
        ),
        Rule(
            "R3",
            antecedent="The premise is stated.",
            consequent="The premise is consistent with every possible response.",
            note="Zero information content: a premise compatible with all "
                 "outcomes distinguishes none.",
        ),
    ],
    falsifiers=[
        Falsifier(
            "F1",
            condition="A counter-observation is ever evaluated on its content "
                      "rather than reclassified as hostility.",
            channel="content-evaluation",
        ),
    ],
)


# --------------------------------------------------------------------------- #
# Dynamic 3 — Threshold Veto / Accretion
# --------------------------------------------------------------------------- #
THRESHOLD_VETO = Dynamic(
    name="Threshold Veto / Accretion",
    observable_signature=(
        "An accommodation baseline is treated as non-revertible; a restoration "
        "of the prior baseline is reclassified as offense; the threshold marker "
        "is non-decreasing across cycles."
    ),
    loads=[
        Load(
            "standard-holding",
            LoadKind.DISCRETE,
            "The observer holds the suspended standard without raising it, "
            "because raising it is reclassified as offense.",
        ),
        Load(
            "silent-hold integral",
            LoadKind.CONTINUOUS,
            "The accumulated standard-holding is sustained over time; its "
            "magnitude scales with active prohibitions multiplied by duration "
            "held, and is the dominant accumulating cost.",
        ),
    ],
    rules=[
        Rule(
            "R1",
            antecedent="A reset occurs.",
            consequent="The accommodation baseline does not revert.",
            note="Decay coefficient is zero across resets.",
        ),
        Rule(
            "R2",
            antecedent="A restoration of the prior baseline is attempted.",
            consequent="The attempt is reclassified as offense.",
            note="The only path back to reciprocity is pre-coded as a violation.",
        ),
        Rule(
            "R3",
            antecedent="A reset occurs.",
            consequent="The active load set is the union of all prior loads.",
            note="The post-reset equilibrium is a stacked configuration, not a "
                 "neutral baseline.",
        ),
    ],
    falsifiers=[
        Falsifier(
            "F1",
            condition="The threshold marker decays across any no-initiative "
                      "interval.",
            channel="decay",
        ),
        Falsifier(
            "F2",
            condition="The threshold marker rises across an interval in which "
                      "the observer took no initiative.",
            channel="autonomous",
        ),
    ],
)


ALL_DYNAMICS = [
    RECRUITED_JUSTIFICATION,
    SELF_SEALING_REFRAME,
    THRESHOLD_VETO,
]


# --------------------------------------------------------------------------- #
# Demo
# --------------------------------------------------------------------------- #
def _demo() -> None:
    print("=" * 68)
    print("ADMISSIBILITY CHECK (each dynamic must pass its own constraint)")
    print("=" * 68)
    for d in ALL_DYNAMICS:
        problems = d.validate()
        status = "ADMISSIBLE" if not problems else "INADMISSIBLE"
        print(f"\n[{status}] {d.name}")
        for p in problems:
            print(f"    - {p}")

    print()
    print("=" * 68)
    print("WORKED EXAMPLE: falsification harness on a cycle log")
    print("=" * 68)
    print(
        "\nFour cycles reconstructed from memory. Reset class is UNKNOWN for\n"
        "the cycles that cannot be cleanly separated, and no clean\n"
        "no-initiative interval exists in the archive. This is the honest\n"
        "state of the instrument: under-determined, not confirmed.\n"
    )

    log = CycleLog(cycles=[
        Cycle(1, "—", ResetClass.UNKNOWN, "baseline suspended", 1.0, True),
        Cycle(2, "restoration attempt", ResetClass.UNKNOWN,
              "baseline suspended + naming prohibited", 2.0, True),
        Cycle(3, "restoration attempt", ResetClass.UNKNOWN,
              "+ standard-raising prohibited", 3.0, True),
        Cycle(4, "restoration attempt", ResetClass.UNKNOWN,
              "+ silent-hold required", 4.0, True),
    ])

    for f in run_falsification(log):
        print(f"  CLAIM : {f.claim}")
        print(f"  VERDICT: {f.verdict.value.upper()}")
        print(f"  BASIS : {f.basis}")
        print()


if __name__ == "__main__":
    _demo()
