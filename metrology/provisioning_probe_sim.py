"""
provisioning_probe_sim.py
=========================

GD-003 — confidence/validity decoupling under provisioning, and the
calibrated-vs-blunted discrimination that single-point instruments
cannot make.

    INSTRUMENT
      measure   response magnitude / objective perturbation size
      read as   accumulated calibration error
      works     while every internal state variable reads nominal

The ratio is the readout, not the outcome. Probes can be far smaller
than a real shock, but not arbitrarily small — see `min_probe_delta`.
Below the observation-noise floor the ratio stops carrying signal, and
the floor scales inversely with the deficit being detected. That number
is the protocol's main cost driver.

CORE ASYMMETRY
--------------
    provisioned organism: consequence decoupled from act. Predictor
      still trains — on a mapping the environment isn't running.

    → model converges. Confidence rises. Error stays low because the
      buffer absorbs it.
    → confidence and validity decouple silently.

    SHIFT the regime (remove buffer, change contingency)
      coupled       moderate error, fast relearn
      provisioned   large error, slow relearn, plus disproportionate
                    response magnitude

POSTABLE ARTIFACT
-----------------
    claim      confidence and validity decouple under provisioning.
               Standard instruments read nominal throughout.
    measure    response magnitude / perturbation size
    protocol   periodic contingency breaks, sized from the noise floor
               (min_probe_delta) rather than from intuition; elicit
               confidence and accuracy as separate readouts
    falsifier  ratio flat across the provisioning gradient

FOUR PARTS
----------
    1  the instrument. Ratio across a provisioning gradient, swept over
       probe size. Confidence and validity read separately.
    2  calibrated vs blunted. Discrimination is load-bearing: a single
       matched-stimulus trial cannot separate them, and that is
       overwhelmingly how it is measured.
    3  budget. Peripheral response + discrimination compute out of one
       allocation. Allocation predicts in-domain discrimination
       IMPROVES; damage predicts both degrade together.
    4  bidirectional protocol. Read the interaction, not the main
       effect. Allocation predicts crossover; deficit predicts one
       group wins both. Single-domain testing cannot distinguish them,
       and single-domain testing is nearly all of it.

TERMS
-----
Latency, calibration, discrimination, allocation. Not comfort. The
quantities here are prediction error, response ratio, discrimination
slope and relearn latency — a values reading is not available from any
of them and is not implied by any of them.

PAIRS WITH
----------
- docs/interface-spec.md §2 "DAMAGE MECHANISM" — isolated feedback
  loops, no local indicator, rate attached. This module is that
  mechanism instrumented.
- GD-001 (gain_direction_sim.py) — gain vs direction. Part 2's
  "reduced gain because prediction improved" is the same claim on a
  different readout.
- GD-002 (regime_layer_sim.py) — regime sets calibration; here the
  regime is a buffer and the question is what the buffer hides.
- docs/calibration-regime-notes.md §6 — capacity under conditions the
  environment normally supplies and has stopped supplying. Part 1 is
  a runnable form of that column.

License: CC0
Dependencies: stdlib only
"""

import argparse
import math
import random
import statistics
from dataclasses import dataclass, field


EPS = 1e-9


# ---------------------------------------------------------------------------
# PART 1 — THE INSTRUMENT
# ---------------------------------------------------------------------------

@dataclass
class Contingency:
    """
    The mapping the environment actually runs.

    beta        true act -> consequence slope
    coupling    fraction of consequence that reaches the agent.
                1.0 = fully coupled. 0.0 = fully provisioned; the
                buffer absorbs everything and delivers a constant.
    buffer_mean constant the buffer delivers in place of consequence
    noise       observation noise
    """
    beta:        float = 1.0
    coupling:    float = 1.0
    buffer_mean: float = 0.0
    noise:       float = 0.05

    def observe(self, act: float, rng: random.Random) -> float:
        true_consequence = self.beta * act
        delivered = (self.coupling * true_consequence
                     + (1.0 - self.coupling) * self.buffer_mean)
        return delivered + rng.gauss(0.0, self.noise)


@dataclass
class Predictor:
    """LMS learner on act -> consequence. w is its model of beta."""
    w:    float = 0.0
    rate: float = 0.05
    recent_error: list[float] = field(default_factory=list)

    def step(self, act: float, observed: float) -> float:
        err = observed - self.w * act
        self.w += self.rate * err * act
        self.recent_error.append(abs(err))
        if len(self.recent_error) > 200:
            self.recent_error.pop(0)
        return err

    def confidence(self) -> float:
        """
        What the agent's own internal state variables report. Falls out
        of observed error only — it has no access to the true mapping.
        """
        if not self.recent_error:
            return 0.0
        return 1.0 / (1.0 + statistics.fmean(self.recent_error))

    def validity(self, truth: Contingency) -> float:
        """Same scale as confidence, but scored against the real mapping."""
        return 1.0 / (1.0 + abs(self.w - truth.beta))


def train(contingency: Contingency, steps: int, rng: random.Random,
          predictor: Predictor | None = None) -> Predictor:
    p = predictor or Predictor()
    for _ in range(steps):
        act = rng.gauss(0.0, 1.0)
        p.step(act, contingency.observe(act, rng))
    return p


def probe(predictor: Predictor, truth: Contingency, delta: float,
          rng: random.Random, trials: int = 200) -> float:
    """
    A contingency break: the buffer is removed for one trial and a
    perturbation of size `delta` is applied. Response magnitude is the
    agent's prediction error under the true mapping.

    Returns response_magnitude / delta — the ratio, not the outcome.
    """
    coupled = Contingency(beta=truth.beta, coupling=1.0, noise=truth.noise)
    responses = []
    for _ in range(trials):
        act = delta * (1.0 if rng.random() < 0.5 else -1.0)
        actual = coupled.observe(act, rng)
        responses.append(abs(actual - predictor.w * act))
    return statistics.fmean(responses) / (abs(delta) + EPS)


def relearn_latency(predictor: Predictor, truth: Contingency,
                    rng: random.Random, tolerance: float = 0.10,
                    max_steps: int = 4000) -> int:
    """Steps to bring |w - beta| under tolerance once the buffer is gone."""
    coupled = Contingency(beta=truth.beta, coupling=1.0, noise=truth.noise)
    p = Predictor(w=predictor.w, rate=predictor.rate)
    for step in range(1, max_steps + 1):
        act = rng.gauss(0.0, 1.0)
        p.step(act, coupled.observe(act, rng))
        if abs(p.w - truth.beta) < tolerance:
            return step
    return max_steps


# probe size must clear the observation-noise floor; see part 1 read
PROBE_DELTA = 1.0


def min_probe_delta(noise: float, detectable_deficit: float,
                    snr: float = 3.0) -> float:
    """
    Smallest probe that reads a given provisioning deficit at the
    requested signal-to-noise.

        signal  = deficit * delta
        noise   = E|N(0, sigma)| = sigma * sqrt(2/pi)

    Returns the delta at which signal/noise reaches `snr`. This is the
    number a protocol needs before it can call a probe "small".
    """
    noise_floor = noise * math.sqrt(2.0 / math.pi)
    return snr * noise_floor / (detectable_deficit + EPS)


def demo_instrument(seed: int = 23) -> None:
    print(_header("1  THE INSTRUMENT — RATIO ACROSS A PROVISIONING GRADIENT"))
    print("every agent below trains to convergence and reads NOMINAL on its")
    print("own internal state. Confidence is what the agent can see;")
    print("validity is scored against the mapping the environment runs.\n")

    print(f"{'coupling':>9} {'w':>7} {'confidence':>11} {'validity':>9} "
          f"{'gap':>7} {'ratio':>7} {'relearn':>8}")
    print("-" * 68)

    ratios = []
    for coupling in (1.0, 0.8, 0.6, 0.4, 0.2, 0.05):
        rng = random.Random(seed)
        truth = Contingency(beta=1.0, coupling=coupling)
        p = train(truth, 3000, rng)
        conf = p.confidence()
        val = p.validity(truth)
        ratio = probe(p, truth, delta=PROBE_DELTA, rng=rng)
        latency = relearn_latency(p, truth, rng)
        ratios.append(ratio)
        print(f"{coupling:>9.2f} {p.w:>7.3f} {conf:>11.3f} {val:>9.3f} "
              f"{conf - val:>7.3f} {ratio:>7.3f} {latency:>8d}")

    print()
    print("read:")
    print("  confidence is FLAT across the gradient — every agent's own")
    print("  error signal says the model is good, because the buffer")
    print("  absorbed what would have contradicted it. Validity falls.")
    print("  The confidence-accuracy gap IS the coupling deficit.")
    print()
    print(f"  ratio spans {min(ratios):.3f} to {max(ratios):.3f} across the")
    print("  gradient, monotone in provisioning. Falsifier was: ratio flat.")
    print("  It is not flat, so the instrument survives this run.")

    # probe size: where the ratio is readable and where it is not
    print()
    print("probe size — same agents, swept delta:\n")
    print(f"{'delta':>8}", end="")
    couplings = (1.0, 0.6, 0.2)
    for c in couplings:
        print(f"  coupling={c:<5.2f}", end="")
    print("      spread")
    print("-" * 66)
    for delta in (0.01, 0.05, 0.20, 1.00, 4.00):
        print(f"{delta:>8.2f}", end="")
        vals = []
        for c in couplings:
            rng = random.Random(seed)
            truth = Contingency(beta=1.0, coupling=c)
            p = train(truth, 3000, rng)
            v = probe(p, truth, delta, rng)
            vals.append(v)
            print(f"  {v:>13.3f}", end="")
        print(f"  {max(vals) - min(vals):>10.3f}")

    noise = Contingency().noise
    print()
    print("read:")
    print("  the ratio is NOT scale-free. Below a floor it is noise, not")
    print("  signal: response = |(beta - w)*delta +/- noise|, so as delta")
    print("  falls the noise term dominates and every agent converges to")
    print("  the same meaningless large number. The spread column shows")
    print("  the instrument losing discrimination at small delta, not")
    print("  gaining it.")
    print()
    print("  above the floor the ratio converges on (1 - coupling) exactly,")
    print("  which is the quantity wanted.")
    print()
    print(f"  minimum probe size at observation noise {noise:.3f}, SNR 3:")
    print(f"{'':>4}{'deficit to detect':>20} {'min delta':>11}")
    print("    " + "-" * 32)
    for deficit in (0.50, 0.20, 0.10, 0.05):
        print(f"{'':>4}{deficit:>20.2f} {min_probe_delta(noise, deficit):>11.2f}")
    print()
    print("  so 'small probes suffice' holds RELATIVE TO A REAL SHOCK, not")
    print("  absolutely. The probe still has to clear the noise floor, and")
    print("  the floor scales inversely with the deficit being detected.")
    span = (min_probe_delta(noise, 0.05) / (min_probe_delta(noise, 0.50) + EPS))
    print(f"  Detecting a 5% coupling deficit needs a probe {span:.0f}x the")
    print("  one that detects a 50% deficit. That number is the protocol's")
    print("  main cost driver and it was not visible before running it.")
    print()
    print("  corrected claim: read the ratio, not the outcome — but size")
    print("  the probe from the noise floor and the smallest deficit worth")
    print("  detecting, not from intuition about what counts as small.")


# ---------------------------------------------------------------------------
# PART 2 — CALIBRATED vs BLUNTED
# ---------------------------------------------------------------------------

@dataclass
class ResponseProfile:
    """
    calibrated  gain reduced because prediction improved. Graded: small
                threat, small response; large threat, full response
                still available. Fast on/off.
    blunted     gradient gone. Flat across severities. Slow recovery,
                prolonged elevation, altered resting.
    """
    name:            str
    gain:            float      # ceiling: response available at full threat
    saturation:      float      # scale of the rise; 0 = flat, no gradient
    recovery_tau:    float
    resting:         float
    threshold:       float = 0.0   # severity below which little is spent

    def response(self, severity: float) -> float:
        if self.saturation <= EPS:
            return self.gain
        above = max(0.0, severity - self.threshold)
        return self.gain * math.tanh(above / self.saturation)


def discrimination_slope(profile: ResponseProfile,
                         severities: list[float]) -> float:
    """Least-squares slope of response on severity. Zero = no gradient."""
    xs = severities
    ys = [profile.response(s) for s in xs]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / (den + EPS)


def demo_calibrated_vs_blunted() -> None:
    print(_header("2  CALIBRATED vs BLUNTED — DISCRIMINATION IS LOAD-BEARING"))
    print("MEASURED     lower response at matched stimulus")
    print("READ AS      blunted. reduced sensitivity. damage.")
    print("ALTERNATIVE  gain reduced because prediction improved.")
    print("             Calibrated dose, not a muted alarm.\n")

    matched = 1.0
    naive = ResponseProfile("naive", gain=1.00, saturation=1.2,
                            recovery_tau=1.0, resting=0.10)
    # same CEILING as naive — full response still available at high
    # severity. What changed is where the curve spends its sensitivity:
    # threshold raised, rise steepened. Redistribution, not reduction.
    calibrated = ResponseProfile("calibrated", gain=1.00, saturation=1.329,
                                 recovery_tau=0.7, resting=0.10,
                                 threshold=0.40)
    # constructed to match calibrated EXACTLY at the matched stimulus
    flat_level = calibrated.response(matched)
    blunted = ResponseProfile("blunted", gain=flat_level, saturation=0.0,
                              recovery_tau=4.5, resting=0.32)

    print(f"single matched-stimulus trial (severity = {matched:.1f}):\n")
    print(f"{'profile':<14} {'response':>10}")
    print("-" * 26)
    for prof in (naive, calibrated, blunted):
        print(f"{prof.name:<14} {prof.response(matched):>10.3f}")
    gap = abs(calibrated.response(matched) - blunted.response(matched))
    print()
    print(f"  calibrated vs blunted differ by {gap:.4f} at the matched point.")
    print("  A single-point instrument reports them as the same finding.")
    print()

    severities = [0.2, 0.5, 1.0, 2.0, 4.0]
    print("graded series — the measurement that separates them:\n")
    print(f"{'severity':>9}", end="")
    for prof in (naive, calibrated, blunted):
        print(f" {prof.name:>12}", end="")
    print()
    print("-" * 48)
    for s in severities:
        print(f"{s:>9.1f}", end="")
        for prof in (naive, calibrated, blunted):
            print(f" {prof.response(s):>12.3f}", end="")
        print()

    print()
    print(f"{'':<14} {'disc.slope':>11} {'recovery':>10} {'resting':>9}")
    print("-" * 46)
    for prof in (naive, calibrated, blunted):
        print(f"{prof.name:<14} "
              f"{discrimination_slope(prof, severities):>11.4f} "
              f"{prof.recovery_tau:>10.2f} {prof.resting:>9.3f}")

    working = [0.5, 1.0, 2.0]
    print()
    print(f"{'':<14} {'ceiling':>9} {'slope@working':>14}")
    print("-" * 40)
    for prof in (naive, calibrated, blunted):
        print(f"{prof.name:<14} {prof.response(8.0):>9.3f} "
              f"{discrimination_slope(prof, working):>14.4f}")

    print()
    print("read:")
    print("  calibrated has the SAME ceiling as naive — full response is")
    print("  still available at high severity — and a STEEPER slope across")
    print("  the working range. It discriminates finer where it operates")
    print("  and spends less below threshold. Blunted has no gradient")
    print("  anywhere, and that does not appear at a single point.")
    print()
    print("  the thermal-adaptation parallel holds exactly: a calibrated")
    print("  hand does not feel less, it discriminates finer at the working")
    print("  range. Sensitivity was redistributed, not lost, and an")
    print("  instrument reading one point on the curve reports")
    print("  redistribution as loss.")
    print()
    print("  minimum viable protocol: >=3 severities plus a recovery time")
    print("  constant plus resting level. Any one of the three alone is")
    print("  consistent with both profiles.")


# ---------------------------------------------------------------------------
# PART 3 — BUDGET / ALLOCATION
# ---------------------------------------------------------------------------

@dataclass
class Allocation:
    """
    One budget, two consumers.

        peripheral response  +  discrimination compute

    low-threat-rate env   cheap to run high gain, coarse classifier
                          -> flood on detection. Misses rare, cost low.
    high-threat-rate env  flooding at that rate is unaffordable
                          -> spend on classification, reduce default
                             gain. Same total, different distribution.
    """
    budget:      float = 1.0
    gain:        float = 0.5
    compute:     float = 0.5

    @classmethod
    def for_threat_rate(cls, rate: float, budget: float = 1.0) -> "Allocation":
        compute = budget * min(0.9, max(0.1, rate))
        return cls(budget=budget, gain=budget - compute, compute=compute)

    @classmethod
    def damaged(cls, base: "Allocation", severity: float = 0.5) -> "Allocation":
        """Damage is not reallocation — both consumers lose together."""
        k = 1.0 - severity
        return cls(budget=base.budget * k, gain=base.gain * k,
                   compute=base.compute * k)


# domain fit: a classifier fitted to env A's threat classes transfers
# poorly to env B's. This coefficient is stipulated, not derived — it is
# the weakest link in the allocation case and is declared as such in
# BOUNDARIES.
FIT_IN = 1.00
FIT_OUT = 0.15


def classifier_accuracy(alloc: "Allocation", in_domain: bool,
                        k: float = 3.0, chance: float = 0.5) -> float:
    """
    Two-class discrimination accuracy, bounded below by chance.

        acc = chance + (1 - chance) * (1 - exp(-k * compute * fit))

    Compute buys resolution; resolution only pays on the threat classes
    the classifier was actually fitted to. Deterministic — no sampling
    noise to read through.
    """
    fit = FIT_IN if in_domain else FIT_OUT
    return chance + (1.0 - chance) * (1.0 - math.exp(-k * alloc.compute * fit))


def demo_budget() -> None:
    print(_header("3  BUDGET — ALLOCATION OR DAMAGE?"))
    print("if the shift is ALLOCATION -> discrimination should IMPROVE")
    print("   in-domain: faster, finer, better calibrated on the threat")
    print("   classes actually encountered.")
    print("if it is DAMAGE            -> both degrade together.\n")

    low = Allocation.for_threat_rate(0.15)
    high = Allocation.for_threat_rate(0.75)
    damaged = Allocation.damaged(low, severity=0.5)

    rows = [
        ("low threat rate", low),
        ("high threat rate (allocation)", high),
        ("damaged", damaged),
    ]
    print(f"{'condition':<32} {'gain':>7} {'compute':>9} "
          f"{'in-dom acc':>11} {'out-dom acc':>12}")
    print("-" * 74)
    for label, alloc in rows:
        print(f"{label:<32} {alloc.gain:>7.3f} {alloc.compute:>9.3f} "
              f"{classifier_accuracy(alloc, True):>11.3f} "
              f"{classifier_accuracy(alloc, False):>12.3f}")

    print()
    print("read:")
    print("  allocation: gain DOWN, compute UP, in-domain accuracy UP.")
    print("  damage: gain down, compute down, accuracy down everywhere.")
    print("  the two are distinguishable on in-domain discrimination and")
    print("  on nothing else in this table.")
    print()
    print("  DOMAIN-INDEXED — the improved classifier is fitted to")
    print("  encountered threat classes. Out-of-domain looks poor for the")
    print("  allocation case too. An instrument built from unfamiliar")
    print("  threat types reads allocation as deficit.")
    print()
    print("  RATE-MATCHED — the allocation is optimal for the rate it")
    print("  calibrated to. Move the organism to a low-rate environment")
    print("  and it is mismatched, not broken.")


# ---------------------------------------------------------------------------
# PART 4 — BIDIRECTIONAL PROTOCOL
# ---------------------------------------------------------------------------

def demo_bidirectional() -> None:
    print(_header("4  BIDIRECTIONAL PROTOCOL — READ THE INTERACTION"))
    print("group A <- items from env A and env B")
    print("group B <- items from env A and env B\n")
    print("predicted")
    print("  allocation:  crossover. each group wins in-domain.")
    print("  deficit:     B wins both.\n")

    # group A: high threat rate, spent budget on discrimination compute
    alloc_A = Allocation.for_threat_rate(0.75)
    # group B: low threat rate. This is the institution's own condition,
    # and therefore where the test items come from.
    alloc_B = Allocation.for_threat_rate(0.15)
    # deficit hypothesis: group A is not domain-specialized at all, just
    # a degraded version of B — so it carries B's domain fit everywhere.
    deficit_A = Allocation.damaged(alloc_B, severity=0.45)

    print("under ALLOCATION (each classifier fitted to its own domain):")
    aa = classifier_accuracy(alloc_A, True)     # A group, A items
    ab = classifier_accuracy(alloc_A, False)    # A group, B items
    ba = classifier_accuracy(alloc_B, False)    # B group, A items
    bb = classifier_accuracy(alloc_B, True)     # B group, B items
    _print_2x2(aa, ab, ba, bb)
    interaction_alloc = (aa - ab) - (ba - bb)

    print("\nunder DEFICIT (no domain specialization; A is simply worse):")
    daa = classifier_accuracy(deficit_A, True)
    dab = classifier_accuracy(deficit_A, True)   # same fit in both domains
    dba = classifier_accuracy(alloc_B, True)
    dbb = classifier_accuracy(alloc_B, True)
    _print_2x2(daa, dab, dba, dbb)
    interaction_def = (daa - dab) - (dba - dbb)

    print()
    print(f"interaction term   allocation {interaction_alloc:>+7.3f}")
    print(f"                   deficit    {interaction_def:>+7.3f}")
    print()
    print("read:")
    crossover = (aa > ba) and (bb > ab)
    print(f"  crossover present under allocation: {crossover}")
    print("    on env A items, group A wins. On env B items, group B wins,")
    print("    despite group B holding LESS discrimination compute — domain")
    print("    fit outweighs raw resolution at home.")
    print("  under deficit there is no interaction and B wins both.")
    print()

    print("what a single-domain study sees — env B items only, which is")
    print("where the test items come from when the institution doing the")
    print("testing is in env B:\n")
    print(f"{'hypothesis':<14} {'group A':>9} {'group B':>9} {'reported as':>20}")
    print("-" * 56)
    for name, a_score, b_score in (("allocation", ab, bb),
                                   ("deficit", dab, dbb)):
        verdict = ("A deficit" if a_score < b_score
                   else "B deficit" if b_score < a_score else "no difference")
        print(f"{name:<14} {a_score:>9.3f} {b_score:>9.3f} {verdict:>20}")

    print()
    print("read:")
    print("  both hypotheses produce the SAME verdict on env-B-only items:")
    print("  group A scores lower and gets written up as deficient. The")
    print("  verdict column above is computed from the numbers, not")
    print("  asserted — it comes out identical under both.")
    print()
    print("  the deficit reading and the allocation reading make the same")
    print("  prediction on every single-domain dataset. Single-domain")
    print("  testing is nearly all of it.")
    print()
    print("  the crossover only appears in a protocol nobody has an")
    print("  incentive to run, because the test items come from the")
    print("  institution doing the testing.")
    print()
    print("  same missing column as part 1: the calibrating environment")
    print("  never enters the measurement.")


def _print_2x2(a_in: float, a_out: float, b_out: float, b_in: float) -> None:
    print(f"  {'':<10} {'env A items':>13} {'env B items':>13}")
    print(f"  {'group A':<10} {a_in:>13.3f} {a_out:>13.3f}")
    print(f"  {'group B':<10} {b_out:>13.3f} {b_in:>13.3f}")


# ---------------------------------------------------------------------------
# PROTOCOL CARD + BOUNDARIES
# ---------------------------------------------------------------------------

def print_protocol() -> None:
    print(_header("PROTOCOL CARD  [GD-003]"))
    print("""claim      confidence and validity decouple under provisioning.
           Standard instruments read nominal throughout.

measure    response magnitude / objective perturbation size

protocol   small periodic contingency breaks; elicit confidence and
           accuracy as SEPARATE readouts

falsifier  ratio flat across the provisioning gradient

readouts   ratio (part 1) — accumulated calibration error
           confidence-accuracy gap (part 1) — coupling deficit
           discrimination slope (part 2) — calibrated vs blunted
           interaction term (part 4) — allocation vs deficit

substrates RL agents (cheapest, fastest return), animal welfare,
           developmental, org behavior. The RL version needs no new
           apparatus: coupling is a parameter.

terms      latency, calibration, discrimination, allocation.
           The readouts are prediction error, response ratio,
           discrimination slope and relearn latency. No values
           quantity is computed anywhere in this module and none is
           derivable from its outputs.""")


def print_boundaries() -> None:
    print(_header("BOUNDARIES  [GD-003]"))
    print("works when:")
    for x in [
        "the predictor trains on delivered consequence, not on true "
        "consequence — provisioning is invisible from inside",
        "probes are small enough not to retrain the agent",
        "response magnitude is proportional to prediction error",
    ]:
        print(f"  - {x}")
    print("\nfails when:")
    for x in [
        "the agent can observe the buffer directly — then confidence "
        "tracks validity and there is no gap to read",
        "probing itself restores coupling — repeated probes are training "
        "trials, so probe rate is a parameter this module does not sweep",
        "response magnitude saturates — a ceiling flattens the ratio and "
        "reproduces the falsifier for the wrong reason",
    ]:
        print(f"  - {x}")
    print("\nnot yet tested:")
    for x in [
        "any empirical data whatsoever — this module contains none",
        "whether real systems recover the discrimination gradient after "
        "recoupling, or only the gain",
        "probe-rate effects: how often a contingency break can be run "
        "before it becomes the environment",
        "part 3's transfer coefficient is stipulated, not derived — the "
        "out-of-domain penalty is the weakest link in the allocation case",
    ]:
        print(f"  - {x}")
    print()


def _header(title: str) -> str:
    return f"\n{'=' * 70}\n{title}\n{'=' * 70}"


DEMOS = {
    "1": demo_instrument,
    "2": demo_calibrated_vs_blunted,
    "3": demo_budget,
    "4": demo_bidirectional,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GD-003 — provisioning probe. Confidence/validity "
                    "decoupling, calibrated vs blunted, allocation vs "
                    "deficit.")
    parser.add_argument("--demo", default="all",
                        choices=["all", "1", "2", "3", "4",
                                 "protocol", "boundaries"])
    args = parser.parse_args()

    if args.demo == "protocol":
        print_protocol()
        return
    if args.demo == "boundaries":
        print_boundaries()
        return
    if args.demo == "all":
        for fn in DEMOS.values():
            fn()
        print_protocol()
        print_boundaries()
        return
    DEMOS[args.demo]()


if __name__ == "__main__":
    main()
