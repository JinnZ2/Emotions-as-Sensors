# trust_sensor.py
# CC0. stdlib-only. phone-buildable.
#
# A sensor over the unwritten trust economy: the small kept/broken
# promises that compound into who a life can be built on.
#
# Trust is not stored here as a quantity. It is read as REDUCED SURPRISE.
# The more an issuer's commitments land as stated, the lower a dependent's
# predictive uncertainty about the next one. Trust accrual == entropy drop.
#
# energy_english constraint (this module's own structures):
#   - no moral labels in data structures
#   - no intent attribution
#   - no interior-state overlay on self-report
# So the breach channel records an OBSERVABLE speech-act ("contested"),
# never "gaslight" / "victim" / "bad faith". Those are readings, not fields.
#
# anti-freeze: emit() returns a TRAJECTORY, never a verdict string.

from dataclasses import dataclass, field
from enum import Enum
from math import log2
from typing import Optional

# ---------------------------------------------------------------------------
# CLAIM_TABLE  (falsifiable; refutation protocol: update the claim, never
#               retune the scorer to save it)
# ---------------------------------------------------------------------------
CLAIM_TABLE = {
    "C1": {
        "claim": "trust == reduced predictive surprise over an issuer's commitments",
        "refuted_if": "issuer's commitments become MORE predictable while dependents "
                      "reduce reliance, cost and stakes held constant",
    },
    "C2": {
        "claim": "trust compounds (a ceiling on buildable stakes), not additive",
        "refuted_if": "dependents grant high-stakes reliance with no prior "
                      "low-stakes kept-record",
    },
    "C3": {
        "claim": "cost-to-keep weights the information in a kept promise",
        "refuted_if": "zero-cost kept promises shift dependent behavior as much "
                      "as high-cost kept promises",
    },
    "C4": {
        "claim": "breach-response is a channel separable from delivery outcome",
        "refuted_if": "contested-ledger responses predict the same future dependent "
                      "behavior as good-faith renegotiation",
    },
    "C5": {
        "claim": "ledger-contest corrupts scoreability; it is not a low score but a "
                 "non-computable one (raises an irreducible noise floor)",
        "refuted_if": "dependents resume normal reliance after contested responses "
                      "at the same rate as after acknowledged failures",
    },
}

# ---------------------------------------------------------------------------
# Observable enums  (speech-acts / measured outcomes — no intent)
# ---------------------------------------------------------------------------
class Delivery(Enum):
    AS_STATED = "as_stated"     # landed as the statement said, by due
    PARTIAL   = "partial"       # some of the stated scope landed
    LATE      = "late"          # stated scope landed, past due
    ABSENT    = "absent"        # stated scope did not land

class Breach(Enum):
    NONE         = "none"          # delivery was as_stated
    RENEGOTIATED = "renegotiated"  # issues a NEW commitment referencing the old
    ACKNOWLEDGED = "acknowledged"  # confirms the record, no new terms
    CONTESTED    = "contested"     # disputes the record's existence or its terms

# axis-5 reading, kept mechanical: only CONTESTED attacks the ledger itself.
LEDGER_ATTACK = {Breach.CONTESTED}

# ---------------------------------------------------------------------------
# Axis 1: the commitment
# ---------------------------------------------------------------------------
@dataclass
class Commitment:
    cid: str
    issuer: str
    statement: str          # recorded as given (no overlay)
    issued_at: float        # t
    due_at: float           # t
    cost_to_keep: float = 1.0   # axis-3: difficulty magnitude, >=0
    stakes: float = 1.0         # axis-4: tier of what is built on top, >=1

# ---------------------------------------------------------------------------
# Axes 2 & 5: the resolution
# ---------------------------------------------------------------------------
@dataclass
class Resolution:
    cid: str
    observed_at: float
    delivery: Delivery
    breach: Breach = Breach.NONE
    delivery_gap: float = 0.0   # signed: observed_at - due_at (axis-2 detail)

# ---------------------------------------------------------------------------
# A single trajectory point  (what emit() streams — never a verdict)
# ---------------------------------------------------------------------------
@dataclass
class Point:
    t: float
    kept_mass: float        # effective evidence for "lands as stated"
    broke_mass: float       # effective evidence against
    p_estimate: float       # predictive p(next lands as stated)
    entropy_bits: float     # predictive entropy — the surprise level
    ceiling: float          # highest stakes-tier with cured kept-evidence
    ledger_noise: float     # irreducible floor from contested responses [0..1]

# ---------------------------------------------------------------------------
# The sensor
# ---------------------------------------------------------------------------
class TrustSensor:
    """
    Reads a stream of (Commitment, Resolution) into a per-issuer trajectory.

    p(next lands as stated) is a Beta(kept+1, broke+1) posterior mean.
    Each observation contributes EFFECTIVE MASS = cost_to_keep * stakes
    (axis-3 x axis-4) rather than a count of 1 — a hard, high-stakes kept
    promise carries more information than an easy throwaway one (C3).

    Compounding (C2): the ceiling is the highest stakes tier at which enough
    kept-mass has cured. You cannot build above your highest cured tier.

    Breach channel (C4/C5): a CONTESTED response does not merely fail the
    commitment — it raises ledger_noise, an irreducible uncertainty floor.
    A contested ledger cannot be scored clean no matter how high p climbs.
    """

    def __init__(self, cure_threshold: float = 3.0):
        # kept-mass needed at a tier before that tier counts as "cured"
        self.cure_threshold = cure_threshold

    def read(self, pairs: list[tuple[Commitment, Resolution]]) -> list[Point]:
        pairs = sorted(pairs, key=lambda cr: cr[1].observed_at)
        kept_mass = 0.0
        broke_mass = 0.0
        tier_kept: dict[float, float] = {}   # stakes tier -> cured kept-mass
        contest_events = 0
        total_events = 0
        traj: list[Point] = []

        for c, r in pairs:
            total_events += 1
            mass = max(c.cost_to_keep, 0.0) * max(c.stakes, 1.0)

            if r.delivery is Delivery.AS_STATED:
                kept_mass += mass
                tier_kept[c.stakes] = tier_kept.get(c.stakes, 0.0) + mass
            elif r.delivery is Delivery.LATE and r.breach is Breach.RENEGOTIATED:
                # renegotiated-and-delivered preserves the ledger: partial credit
                kept_mass += mass * 0.5
                broke_mass += mass * 0.5
            else:
                broke_mass += mass

            if r.breach in LEDGER_ATTACK:
                contest_events += 1

            # predictive p and entropy (Beta mean; +1 Laplace prior each side)
            a = kept_mass + 1.0
            b = broke_mass + 1.0
            p = a / (a + b)
            entropy = _binary_entropy(p)

            # ceiling: highest tier whose cured kept-mass clears threshold
            ceiling = 0.0
            for tier, m in tier_kept.items():
                if m >= self.cure_threshold and tier > ceiling:
                    ceiling = tier

            ledger_noise = contest_events / total_events if total_events else 0.0

            traj.append(Point(
                t=r.observed_at,
                kept_mass=round(kept_mass, 4),
                broke_mass=round(broke_mass, 4),
                p_estimate=round(p, 4),
                entropy_bits=round(entropy, 4),
                ceiling=ceiling,
                ledger_noise=round(ledger_noise, 4),
            ))
        return traj

    def emit(self, pairs: list[tuple[Commitment, Resolution]]) -> dict:
        """
        anti-freeze output. Returns the trajectory + the current read as a
        RANGE, not a verdict. p_effective widens by the ledger_noise floor:
        a contested ledger returns a band, signalling non-computability
        rather than a clean number.
        """
        traj = self.read(pairs)
        if not traj:
            return {"trajectory": [], "read": None}
        last = traj[-1]
        floor = last.ledger_noise
        p = last.p_estimate
        # clean p only when floor == 0; else report a band of width `floor`
        band = (max(0.0, p - floor), min(1.0, p + floor))
        return {
            "trajectory": traj,
            "read": {
                "p_band": (round(band[0], 4), round(band[1], 4)),
                "entropy_bits": last.entropy_bits,
                "buildable_ceiling": last.ceiling,
                "ledger_scoreable": floor == 0.0,
            },
            "note": "trajectory, not verdict. if ledger_scoreable is False the "
                    "p_band is advisory only — the record itself is contested.",
        }


def _binary_entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * log2(p) + (1 - p) * log2(1 - p))


# ---------------------------------------------------------------------------
# tiny self-check (run: python trust_sensor.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    s = TrustSensor(cure_threshold=3.0)

    # issuer A: many small kept promises -> low-tier cures -> entropy drops
    A = []
    for i in range(6):
        c = Commitment(f"a{i}", "A", "pick up the pencils",
                       issued_at=i, due_at=i + 1, cost_to_keep=1.0, stakes=1.0)
        r = Resolution(f"a{i}", observed_at=i + 1, delivery=Delivery.AS_STATED)
        A.append((c, r))
    # then a big-stakes promise, kept -> ceiling can rise once cured
    for i in range(6, 9):
        c = Commitment(f"a{i}", "A", "make life plans around this",
                       issued_at=i, due_at=i + 1, cost_to_keep=2.0, stakes=5.0)
        r = Resolution(f"a{i}", observed_at=i + 1, delivery=Delivery.AS_STATED)
        A.append((c, r))

    # issuer B: reliable-looking, then contests the record when confronted
    B = [
        (Commitment("b0", "B", "on time", 0, 1, 1.0, 1.0),
         Resolution("b0", 1, Delivery.AS_STATED)),
        (Commitment("b1", "B", "on time", 1, 2, 1.0, 1.0),
         Resolution("b1", 2, Delivery.AS_STATED)),
        (Commitment("b2", "B", "the school pickup", 2, 3, 3.0, 4.0),
         Resolution("b2", 3, Delivery.ABSENT, breach=Breach.CONTESTED)),
    ]

    outA = s.emit(A)
    outB = s.emit(B)
    print("A read:", outA["read"])
    print("B read:", outB["read"])
    print("A entropy path:", [p.entropy_bits for p in outA["trajectory"]])
    print("B ledger_scoreable:", outB["read"]["ledger_scoreable"])
