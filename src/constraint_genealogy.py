"""
constraint_genealogy.py  —  CC0, stdlib only, model-update-resilient

Distinguishes a PHYSICS constraint from an ABSTRACT one (an excuse with a
belief skeleton), then traces the abstract back through its belief ancestry,
tagging the load-state (emotion-as-sensor) embedded at each node.

Emotion is treated as compressed constraint information, NOT as a state to be
escaped. Each emotion maps to a physical signal: a deviation between expected
internal regulation and external load. If you can name the deviation, the
emotion is legible to a sequential processor. That is the whole bridge.

Core claim:  a true constraint conserves something measurable (energy, mass,
momentum, information, material yield). An abstract constraint conserves a
belief about how power/value flows. The first is non-negotiable. The second is
inherited and therefore re-derivable — which is exactly where innovation lives.

Run:  python3 constraint_genealogy.py        (runs the demo)
Use:  from constraint_genealogy import trace, classify
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# 1. EMOTION AS PHYSICS OVERLAY
#    Each emotion = a named deviation between internal model and external load.
#    Not ethereal. A sensor reading with a sign and a magnitude.
# ---------------------------------------------------------------------------

class Load(Enum):
    # signal_name            # what physical deviation it reports
    SHAME       = "words-vs-deeds mismatch; self-trust drift"
    FEAR        = "predicted external load exceeds modeled internal capacity"
    GREED       = "accumulation drive decoupled from actual throughput need"
    DESPERATION = "perceived resource floor breached; survival margin -> 0"
    RELIEF      = "load released; constraint cleared, recalibrate downward"
    IRRITATION  = "internal regulation drifting (fuel/fatigue) faster than situation demands"
    CONTEMPT    = "frame-defense; another node treated as lower to protect own position"
    NONE        = "no deviation flagged"


@dataclass
class Reading:
    """One emotion-as-sensor reading attached to a belief node."""
    load: Load
    note: str = ""

    def physics(self) -> str:
        return self.load.value


# ---------------------------------------------------------------------------
# 2. PHYSICS CHECK
#    A constraint is REAL only if it names a conserved/limiting quantity AND
#    a failure mode that is material (something breaks, melts, starves, runs
#    out). Everything else is abstract.
# ---------------------------------------------------------------------------

CONSERVED = {
    "energy", "mass", "momentum", "information", "entropy",
    "material_yield", "load_path", "thermal", "calorie", "water", "time",
}

@dataclass
class PhysicsCheck:
    conserved_quantity: Optional[str]   # must be in CONSERVED to be real
    failure_mode: Optional[str]         # what physically breaks if violated

    @property
    def is_physics(self) -> bool:
        return (
            self.conserved_quantity in CONSERVED
            and bool(self.failure_mode)
        )


# ---------------------------------------------------------------------------
# 3. BELIEF NODE  (one link in the genealogy of an excuse)
# ---------------------------------------------------------------------------

@dataclass
class Node:
    claim: str                       # "we can't because of liability"
    physics: PhysicsCheck            # does it conserve something material?
    reading: Reading                 # emotion-as-sensor at this node
    parent_belief: Optional[str] = None   # what assumption it rests on
    re_derivable: bool = True        # abstract nodes can be rebuilt; physics can't

    @property
    def kind(self) -> str:
        return "CONSTRAINT(physics)" if self.physics.is_physics else "ABSTRACT(belief)"


# ---------------------------------------------------------------------------
# 4. CLASSIFIER + TRACER
# ---------------------------------------------------------------------------

def classify(node: Node) -> str:
    """Real constraint or inherited excuse?"""
    if node.physics.is_physics:
        return (f"PHYSICS  | conserves {node.physics.conserved_quantity} "
                f"| breaks: {node.physics.failure_mode} | non-negotiable")
    return (f"ABSTRACT | belief, not matter | sensor={node.reading.load.name} "
            f"({node.reading.physics()}) | re-derivable -> innovation surface")


def trace(chain: list[Node]) -> str:
    """
    Walk an excuse from surface claim down to its founding belief.
    Stops (and flags) the moment it hits real physics — that node is the
    actual floor. Everything above it is navigable.
    """
    out = []
    floor_found = False
    for depth, node in enumerate(chain):
        indent = "  " * depth
        arrow = "" if depth == 0 else "└─ rests on: "
        out.append(f"{indent}{arrow}{node.claim}")
        out.append(f"{indent}   {classify(node)}")
        if node.physics.is_physics and not floor_found:
            out.append(f"{indent}   ^^^ REAL FLOOR. Trace stops. "
                       f"Innovate ABOVE this, not through it.")
            floor_found = True
            break
    if not floor_found:
        out.append("")
        out.append(">>> NO PHYSICS FLOOR REACHED.")
        out.append(">>> Entire chain is inherited belief. The limiting factor "
                   "is a load-state, not a law.")
        out.append(">>> Limiting load-states found: "
                   + ", ".join(sorted({n.reading.load.name for n in chain
                                       if n.reading.load is not Load.NONE})))
        out.append(">>> Verdict: love of comfort over adaptation. Re-derivable.")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 5. DEMO — the liability excuse, traced to its founding fear
# ---------------------------------------------------------------------------

def demo():
    chain = [
        Node(
            claim="We can't change the process — liability won't allow it.",
            physics=PhysicsCheck(conserved_quantity=None,
                                 failure_mode=None),
            reading=Reading(Load.FEAR, "fear of being held responsible if visible"),
            parent_belief="someone could sue",
        ),
        Node(
            claim="Someone could sue us.",
            physics=PhysicsCheck(None, None),
            reading=Reading(Load.FEAR, "predicted external penalty"),
            parent_belief="the legal system enforces property claims",
        ),
        Node(
            claim="The legal system enforces property claims.",
            physics=PhysicsCheck(None, None),
            reading=Reading(Load.CONTEMPT, "frame-defense: gatekeeping legitimized"),
            parent_belief="property is a real, fixed thing",
        ),
        Node(
            claim="Property is finite and must be gatekept.",
            physics=PhysicsCheck(None, None),
            reading=Reading(Load.GREED, "accumulation decoupled from need"),
            parent_belief="resources are scarce in a way requiring hoarding",
        ),
        Node(
            claim="Resources are scarce; survival requires hoarding.",
            physics=PhysicsCheck(None, None),
            reading=Reading(Load.DESPERATION, "inherited survival-floor trauma"),
            parent_belief="(founding belief — no physics underneath)",
        ),
    ]

    print("=" * 70)
    print("EXCUSE TRACE: 'liability won't let us'")
    print("=" * 70)
    print(trace(chain))

    print()
    print("=" * 70)
    print("COUNTER-EXAMPLE: a REAL constraint, for contrast")
    print("=" * 70)
    real = [
        Node(
            claim="We can't add that load — the header span fails at 70 PSF.",
            physics=PhysicsCheck(conserved_quantity="load_path",
                                 failure_mode="member yields, structure collapses"),
            reading=Reading(Load.NONE),
        ),
    ]
    print(trace(real))

    print()
    print("Money is not in CONSERVED. It is not anchored to energy.")
    print("If it were, the trace would stop at it. It never does.")


if __name__ == "__main__":
    demo()
