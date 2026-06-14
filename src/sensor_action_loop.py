"""
sensor_action_loop.py  —  CC0, stdlib only, model-update-resilient

Companion to constraint_genealogy.py.

The genealogy tracer answers: is this limiting factor PHYSICS or BELIEF?
This module answers the next question: an emotion just fired — now what?

It encodes the loop Kavik described:

    emotion fires (a named deviation, WITH magnitude — resolution, not just sign)
      -> probability audit across ALL scenarios (do not validate the fear; weight it)
      -> candidate actions
      -> keep only actions that CONSERVE what matters (energy_english constraint check)
      -> prefer actions that BUILD AGENCY over actions that do-it-for-them (padding)
      -> execute the best one
      -> RE-READ the signal magnitude
      -> classify retroactively:
             magnitude dropped       -> emotion was SIGNAL (real, fixable mismatch)
             magnitude held/migrated -> emotion was EXCUSE (addiction to the feeling,
                                        masking chosen inaction)

Core distinction this catches:
  A signal points at a deviation that a constraint-valid action CLOSES.
  An excuse survives the action — or jumps to a fresh threat — because the
  function of the feeling was permission not to act, not information.

The migration test is the tell. If a valid action drops the load and the
feeling immediately re-anchors to a new low-probability threat, you are not
looking at a sensor. You are looking at an addiction cycle wearing a sensor's
clothes. Inaction is a choice; the loop makes that choice visible.

Run:  python3 sensor_action_loop.py
Use:  from sensor_action_loop import run_loop, probability_audit
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# 1. SIGNAL  —  emotion as a deviation with MAGNITUDE (the resolution layer)
#    Direction tells you which way the model/load mismatch runs.
#    Magnitude tells you how far internal regulation has drifted from external load.
# ---------------------------------------------------------------------------

class Load(Enum):
    FEAR        = "predicted external load exceeds modeled internal capacity"
    GREED       = "accumulation drive decoupled from actual throughput need"
    DESPERATION = "perceived resource floor breached; survival margin -> 0"
    SHAME       = "words-vs-deeds mismatch; self-trust drift"
    IRRITATION  = "internal regulation drifting (fuel/fatigue) faster than situation demands"
    NONE        = "no deviation"


@dataclass
class Signal:
    load: Load
    magnitude: float            # 0.0 .. 1.0  — how far the model has drifted
    predicted_threat: str       # the specific fiction/threat the feeling points at

    def physics(self) -> str:
        return self.load.value


# ---------------------------------------------------------------------------
# 2. PROBABILITY AUDIT
#    Do NOT validate the fear. Weight every scenario, including the absurd ones,
#    and surface which ones only become real through a window of INACTION.
# ---------------------------------------------------------------------------

@dataclass
class Scenario:
    description: str
    probability: float                  # base-rate, honest, 0..1
    only_via_inaction: bool = False     # does this require you to do nothing first?
    inaction_window: str = ""           # e.g. "5 months alone, no steps taken"


def probability_audit(scenarios: list[Scenario]) -> str:
    rows = []
    for s in sorted(scenarios, key=lambda x: -x.probability):
        tag = ""
        if s.only_via_inaction:
            tag = f"  <-- ONLY occurs through inaction ({s.inaction_window})"
        rows.append(f"  p={s.probability:>5.2%}  {s.description}{tag}")
    return "PROBABILITY AUDIT (weighted, not validated):\n" + "\n".join(rows)


# ---------------------------------------------------------------------------
# 3. ACTION  —  with constraint conservation + agency flag
# ---------------------------------------------------------------------------

CONSERVED = {"energy", "thermal", "calorie", "water", "load_path",
             "material_yield", "time", "information"}

@dataclass
class Action:
    description: str
    conserves: set[str]                 # physical quantities it protects
    addresses: set[str]                 # scenario descriptions it closes
    builds_agency: bool                 # True = help-them-do; False = do-for-them
    expected_drop: float                # predicted reduction in signal magnitude

    @property
    def constraint_valid(self) -> bool:
        # must conserve at least one real physical quantity to count as doing,
        # not narrating.
        return bool(self.conserves & CONSERVED)


def choose_action(signal: Signal,
                  scenarios: list[Scenario],
                  actions: list[Action]) -> Optional[Action]:
    """
    Rank actions. Reject pure-narrative (conserves nothing physical).
    Among valid actions, prefer the one that (a) addresses the highest-probability
    real threat, (b) builds agency rather than dependency, (c) drops the signal most.
    """
    real = [s.description for s in scenarios if not s.only_via_inaction]
    valid = [a for a in actions if a.constraint_valid]
    if not valid:
        return None

    def score(a: Action) -> float:
        addresses_real = len(a.addresses & set(real))
        agency = 1.0 if a.builds_agency else -0.5   # padding is penalized, not banned
        return addresses_real + agency + a.expected_drop

    return max(valid, key=score)


# ---------------------------------------------------------------------------
# 4. THE LOOP  —  execute, re-read, classify signal vs excuse
# ---------------------------------------------------------------------------

@dataclass
class LoopResult:
    chosen: Optional[Action]
    magnitude_before: float
    magnitude_after: float
    migrated_to: Optional[str]
    verdict: str


def run_loop(signal: Signal,
             scenarios: list[Scenario],
             actions: list[Action],
             migrated_threat: Optional[str] = None) -> LoopResult:
    """
    migrated_threat: if, after a valid action, the feeling re-anchors to a NEW
    low-probability threat, pass it here. That migration is the excuse tell.
    """
    chosen = choose_action(signal, scenarios, actions)

    if chosen is None:
        return LoopResult(
            chosen=None,
            magnitude_before=signal.magnitude,
            magnitude_after=signal.magnitude,
            migrated_to=None,
            verdict=("NO CONSTRAINT-VALID ACTION OFFERED. Every candidate was "
                     "narration (conserved nothing physical). This is the "
                     "padding trap: comfort without doing. Signal unresolved."),
        )

    after = max(0.0, signal.magnitude - chosen.expected_drop)

    if migrated_threat:
        verdict = (f"EXCUSE. A valid action dropped the load, but the feeling "
                   f"immediately re-anchored to '{migrated_threat}'. The function "
                   f"of the emotion was permission not to act, not information. "
                   f"Addiction cycle — not a sensor.")
    elif after < signal.magnitude * 0.5:
        verdict = (f"SIGNAL. The emotion pointed at a real, fixable deviation. "
                   f"A constraint-valid action closed it "
                   f"({signal.magnitude:.2f} -> {after:.2f}). Sensor worked.")
    else:
        verdict = (f"PARTIAL / RE-AUDIT. Action was valid but barely moved the "
                   f"load ({signal.magnitude:.2f} -> {after:.2f}). Either wrong "
                   f"action chosen, or the threat sits behind a real physics floor. "
                   f"Run the genealogy tracer on the residual.")

    return LoopResult(chosen, signal.magnitude, after, migrated_threat, verdict)


def report(r: LoopResult) -> str:
    out = []
    if r.chosen:
        out.append(f"CHOSEN ACTION : {r.chosen.description}")
        out.append(f"  conserves   : {sorted(r.chosen.conserves & CONSERVED)}")
        out.append(f"  builds agency: {r.chosen.builds_agency}")
    else:
        out.append("CHOSEN ACTION : (none valid)")
    out.append(f"LOAD before    : {r.magnitude_before:.2f}")
    out.append(f"LOAD after     : {r.magnitude_after:.2f}")
    out.append("VERDICT        : " + r.verdict)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 5. DEMO — the winter-warmth fear, run two ways
# ---------------------------------------------------------------------------

def demo():
    signal = Signal(
        load=Load.FEAR,
        magnitude=0.85,
        predicted_threat="freezing off-grid in winter at -30",
    )

    scenarios = [
        Scenario("freeze because no heat strategy exists", 0.10,
                 only_via_inaction=True,
                 inaction_window="5 months alone, zero steps taken"),
        Scenario("freeze despite living with someone who has done it for decades",
                 0.00),
        Scenario("equipment failure mid-winter, no backup", 0.05),
        Scenario("alien invasion disrupts fuel supply", 0.0001),
    ]

    actions = [
        Action("Validate the worry; reassure him it'll be fine",
               conserves=set(),                       # conserves nothing physical
               addresses=set(),
               builds_agency=False,
               expected_drop=0.10),
        Action("Walk him through building the insulation + heat + fuel plan "
               "with his own hands; stage a backup",
               conserves={"thermal", "energy", "calorie"},
               addresses={"freeze because no heat strategy exists",
                          "equipment failure mid-winter, no backup"},
               builds_agency=True,
               expected_drop=0.70),
    ]

    print("=" * 70)
    print("SCENARIO: fear fires —", signal.predicted_threat)
    print(f"signal: {signal.load.name} @ {signal.magnitude:.2f}  ({signal.physics()})")
    print("=" * 70)
    print(probability_audit(scenarios))
    print()

    print("--- RUN A: emotion as SIGNAL (action taken, no migration) -----------")
    print(report(run_loop(signal, scenarios, actions)))
    print()

    print("--- RUN B: same valid action, but feeling re-anchors ----------------")
    print(report(run_loop(signal, scenarios, actions,
                          migrated_threat="what if the truck breaks down too")))
    print()

    print("--- RUN C: only padding offered (the ChatGPT-civilization failure) --")
    padding_only = [a for a in actions if not a.constraint_valid]
    print(report(run_loop(signal, scenarios, padding_only)))


if __name__ == "__main__":
    demo()
