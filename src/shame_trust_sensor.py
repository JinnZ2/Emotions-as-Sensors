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
