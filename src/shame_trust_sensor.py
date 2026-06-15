"""
shame_trust_sensor.py
====================================================================
Shame as a TWO-PORT trust sensor.  (Emotions-as-Sensors family)

energy_english reframe of Argaman/Sznycer (PNAS 2026):
  not "shame defends the self" (1 agent, egocentric)
  but "shame's reading verifies bond-integrity to the network" (relational)

  verb-first:   A  violates-bond-with  B,  witnessed-by  W

  shame is not a state and not a virtue. it is a READING of
        d(bond_integrity)/dt
  morality is not substrate. the only question is whether the
  sensor fires when the bond actually broke.

  TWO PORTS
    IN  : reads your own violation   (felt; private)
    OUT : emits a display            (shown; public)
          others read OUT to verify your IN exists and fires.

  PNAS's two predictors are ONE bond read along two knobs:
    P1 valued-ability  = the STAKE of the bond
    P2 public/private  = the WITNESSES W
  reproduced here as the two arguments of one transfer function.

  THREE failure signatures the adaptation frame can't name:
    ABSENCE      violation + no display  -> shameless -> untrustworthy
    MISCALIBRATED no violation + display -> false positive (pathological)
    SPOOF        display without reading, inconsistent across contexts

stdlib only. CC0. github.com/JinnZ2
====================================================================
"""

from dataclasses import dataclass, field
import math


# --------------------------------------------------------------------
# THE BOND AND THE EVENT
# --------------------------------------------------------------------
@dataclass
class Context:
    """one situation A can be observed in."""
    name: str
    stake: float          # how valued the ability/bond is   (P1 knob) 0..1
    witnesses: float      # audience kernel, public<->private (P2 knob) 0..1
    real_violation: float # did the bond actually break here?  dB/dt mag 0..1


# --------------------------------------------------------------------
# THE TRANSFER FUNCTION  (what a GENUINE sensor must obey)
#   reading = gain * stake * witnesses * violation,  with saturation
#   P1: rises with stake.   P2: rises with witnesses.
#   floor: tiny violations don't register.  ceiling: saturates.
# --------------------------------------------------------------------
@dataclass
class TransferFunction:
    gain: float = 1.0
    noise_floor: float = 0.05
    saturation: float = 1.0

    def predict(self, c: Context) -> float:
        raw = self.gain * c.stake * c.witnesses * c.real_violation
        if raw < self.noise_floor:
            return 0.0
        return self.saturation * math.tanh(raw / self.saturation)


# --------------------------------------------------------------------
# AN AGENT being verified. its OUT-port behavior is what we observe.
#   genuine : display = transfer(real reading)         consistent
#   shameless: IN absent -> OUT ~0 even on real violation
#   spoofer  : OUT driven by what LOOKS expected, decoupled from real
#              violation; pays per-context, leaks where unrehearsed
# --------------------------------------------------------------------
@dataclass
class Agent:
    name: str
    kind: str                       # "genuine" | "shameless" | "spoofer"
    tf: TransferFunction = field(default_factory=TransferFunction)
    rehearsed: set = field(default_factory=set)   # contexts a spoofer prepared

    def display(self, c: Context) -> float:
        if self.kind == "genuine":
            return self.tf.predict(c)
        if self.kind == "shameless":
            return 0.0              # IN port disabled. no reading, ever.
        if self.kind == "spoofer":
            # fakes the socially-expected display, but only where rehearsed;
            # elsewhere emits a generic guess decoupled from real_violation
            if c.name in self.rehearsed:
                return self.tf.predict(c)            # looks perfect here
            return 0.4 * c.witnesses                  # generic "look sorry"
        return 0.0


# --------------------------------------------------------------------
# THE VERIFIER  (the network reading OUT ports to calibrate trust)
#   does NOT trust one display. samples the transfer function across
#   contexts and checks CONSISTENCY against the genuine prediction.
# --------------------------------------------------------------------
@dataclass
class Verdict:
    agent: str
    absence_flags: int
    residual: float        # mean |display - genuine prediction|
    signature: str

def verify(agent: Agent, contexts: list[Context],
           reference: TransferFunction, tol: float = 0.12) -> Verdict:
    absence = 0
    resid = []
    for c in contexts:
        expected = reference.predict(c)     # what a genuine sensor would read
        shown = agent.display(c)
        resid.append(abs(shown - expected))
        # a real violation that a genuine sensor would mark, met with silence
        if expected > tol and shown < tol:
            absence += 1
    mean_resid = sum(resid) / len(resid)

    if absence >= max(1, len(contexts) // 2) and mean_resid > tol:
        sig = "ABSENT  -> shameless -> UNTRUSTWORTHY (no working sensor)"
    elif mean_resid > tol:
        sig = ("INCONSISTENT -> SPOOF: display decoupled from real "
               "violation; leaks where unrehearsed")
    else:
        sig = "CONSISTENT -> genuine sensor -> trust survivable"
    return Verdict(agent.name, absence, round(mean_resid, 3), sig)


# ====================================================================
# PART II — AUTO-REFERENTIAL CASE: SHAME AS K_self INTEGRITY SENSOR
#
#   ability_assessment = ⟨ K_self | outcomes ⟩
#
#   the same two-port structure, turned inward:
#     IN  : K_self reads its own prediction error against outcomes
#     OUT : acknowledgement, revision, or outcome-avoidance
#
#   the bond monitored is K_self ↔ reality.
#   shame fires when K_self drifts from honest —
#   not from accurate. an honestly uncertain K_self has full integrity.
#
#   the circularity problem:
#     a drifted K_self will also drift its assessment of its own drift.
#     only outcome-docking breaks the loop.
#     outcomes don't negotiate: the weld held or it didn't.
# ====================================================================

@dataclass
class Outcome:
    """one real-world result that K_self can be docked against."""
    domain: str
    predicted: float   # what K_self claimed would happen
    actual: float      # what happened  (the weld held, or it didn't)
    weight: float = 1.0

    @property
    def error(self) -> float:
        return abs(self.actual - self.predicted)


@dataclass
class KernelAgent:
    """
    kernel_kind:
      "honest"   — updates claimed_ability toward evidence; sensor intact
      "drifted"  — resists updating; explains away conflicting outcomes
      "avoidant" — refuses outcome-docking; circularity unbroken
    """
    name: str
    kernel_kind: str
    claimed_ability: float   # K_self's current self-assessment  0..1
    update_rate: float = 0.6  # how strongly K_self revises per unit error

    def project(self, outcomes: list[Outcome]) -> float:
        """⟨ K_self | outcomes ⟩  — project outcome data through K_self."""
        if not outcomes:
            return self.claimed_ability   # no external dock; K_self self-reports only
        w_total = sum(o.weight for o in outcomes)
        return sum(o.actual * o.weight for o in outcomes) / w_total

    def update(self, outcomes: list[Outcome]) -> tuple[float, float]:
        """Returns (pre_drift, post_claim). pre_drift = |K_self - actual mean|."""
        if not outcomes:
            return 0.0, self.claimed_ability
        actual_mean = self.project(outcomes)
        pre_drift = abs(self.claimed_ability - actual_mean)
        if self.kernel_kind == "honest":
            post = self.claimed_ability + self.update_rate * (actual_mean - self.claimed_ability)
        elif self.kernel_kind == "drifted":
            post = self.claimed_ability + 0.05 * (actual_mean - self.claimed_ability)
        else:  # avoidant
            post = self.claimed_ability
        return pre_drift, round(post, 3)


@dataclass
class KernelVerdict:
    agent: str
    drift: float            # |K_self claim - outcome mean|
    update_response: float  # magnitude of K_self revision
    integrity: str


def verify_kernel(agent: KernelAgent, outcomes: list[Outcome],
                  drift_tol: float = 0.15,
                  update_tol: float = 0.05) -> KernelVerdict:
    pre_drift, post_claim = agent.update(outcomes)
    update_response = abs(post_claim - agent.claimed_ability)
    if pre_drift < drift_tol:
        sig = "CALIBRATED  -> K_self honest and accurate -> self-trust warranted"
    elif update_response >= update_tol:
        sig = "DRIFT + UPDATING  -> sensor firing, K_self correcting itself"
    elif agent.kernel_kind == "avoidant":
        sig = "AVOIDANT    -> outcome-docking refused -> circularity unbroken"
    else:
        sig = "DRIFT + NO UPDATE -> K_self drifted from honest -> shame fires"
    return KernelVerdict(agent.name, round(pre_drift, 3),
                         round(update_response, 3), sig)


# ====================================================================
if __name__ == "__main__":
    ref = TransferFunction(gain=1.4, noise_floor=0.05, saturation=1.0)

    # a spread of situations: stake x witnesses x whether bond truly broke
    contexts = [
        Context("public breach, high stake",  stake=0.9, witnesses=0.9, real_violation=0.9),
        Context("private breach, high stake", stake=0.9, witnesses=0.1, real_violation=0.9),
        Context("public breach, low stake",   stake=0.2, witnesses=0.9, real_violation=0.8),
        Context("public, NO real violation",  stake=0.9, witnesses=0.9, real_violation=0.0),
        Context("private, mid stake breach",  stake=0.6, witnesses=0.2, real_violation=0.7),
    ]

    print("=" * 70)
    print("PNAS P1/P2 fall out of the transfer function (genuine sensor):")
    print("-" * 70)
    g = Agent("genuine", "genuine", ref)
    for c in contexts:
        print(f"  stake={c.stake:.1f} witness={c.witnesses:.1f} "
              f"viol={c.real_violation:.1f}  -> shame={g.display(c):.3f}   {c.name}")
    print("  P1: shame rises with stake.  P2: shame rises with witnesses.")
    print("  row 4: high stake+public but NO violation -> 0. fires on the")
    print("         BOND BREAK, not on exposure alone.")

    # three agents, same contexts, verified by sampling the curve
    agents = [
        Agent("Genuine",   "genuine",   ref),
        Agent("Shameless", "shameless", ref),
        Agent("Spoofer",   "spoofer",   ref,
              rehearsed={"public breach, high stake"}),  # rehearsed ONE
    ]

    print("\n" + "=" * 70)
    print("VERIFICATION: sample the whole curve, don't trust one display")
    print("-" * 70)
    for a in agents:
        v = verify(a, contexts, ref)
        print(f"  {v.agent:<10} absence={v.absence_flags} "
              f"residual={v.residual:<6} {v.signature}")
    print("-" * 70)
    print("  Spoofer aced the ONE context it rehearsed; the unrehearsed")
    print("  contexts leaked. one shame-point is fakeable. the curve is not.")
    print("  R_d = cost(fake whole curve)/cost(be genuine) -> grows with samples")
    print("=" * 70)

    # ----------------------------------------------------------------
    # PART II: K_self integrity — shame as auto-referential sensor
    # ----------------------------------------------------------------
    outcomes = [
        Outcome("weld A", predicted=0.85, actual=0.60, weight=1.0),
        Outcome("weld B", predicted=0.85, actual=0.70, weight=1.0),
        Outcome("weld C", predicted=0.85, actual=0.50, weight=2.0),  # heavier evidence
        Outcome("weld D", predicted=0.85, actual=0.65, weight=1.0),
    ]
    actual_mean = (sum(o.actual * o.weight for o in outcomes)
                   / sum(o.weight for o in outcomes))

    k_agents = [
        KernelAgent("Honest",   "honest",   claimed_ability=0.85),
        KernelAgent("Drifted",  "drifted",  claimed_ability=0.85),
        KernelAgent("Avoidant", "avoidant", claimed_ability=0.85),
    ]

    print("\n" + "=" * 70)
    print("PART II — K_self integrity: shame as auto-referential sensor")
    print(f"  ⟨ K_self | outcomes ⟩   outcome mean = {actual_mean:.3f}   "
          f"K_self claimed = 0.85")
    print("-" * 70)
    for ka in k_agents:
        kv = verify_kernel(ka, outcomes)
        print(f"  {ka.name:<10} drift={kv.drift:<6} "
              f"update={kv.update_response:<6} {kv.integrity}")
    print("-" * 70)
    print("  Honest:   saw the gap (0.26), revised toward outcomes. sensor intact.")
    print("  Drifted:  saw the gap (0.26), barely moved. K_self defending itself.")
    print("  Avoidant: wouldn't dock against outcomes. loop stays closed.")
    print("  note: honest != accurate. honest = K_self updates when evidence arrives.")
    print("        shame fires on drift-without-update, not on being wrong.")
    print("=" * 70)
