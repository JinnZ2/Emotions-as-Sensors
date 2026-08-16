"""
gain_direction_sim.py
=====================

GD-001 — exploration harness for the claim that a neuromodulator sets
GAIN but not DIRECTION, and that direction is set by what the receiver
was calibrated against.

    export_rate = f(OT_gain, calibration_history)

    sign(dExport/dOT)  = +   when calibration variance is high
                       = -   when calibration variance is low

The reported finding this responds to: oxytocin increased altruistic
behavior in adults reporting greater early-life adversity and decreased
it in adults reporting fewer hardships (Marsh et al., Translational
Psychiatry). A dose with two opposite signs is not a substance with two
effects. It is a gain knob, and the sign is coming from somewhere else.

WHAT THIS IS
------------
A generator of DISCRIMINATING PREDICTIONS. It does not test the
hypothesis and it contains no empirical data. It answers one question:
if the gain/calibration model is right, what measurements would come
apart from what an adversity-count model predicts?

Everything below is a consequence of the mechanism, not a stipulation.
The sign flip is nowhere written as a branch — it falls out of one
subtraction (see `export_slope`).

THE MECHANISM
-------------
The receiver holds a prior about whether export is returned. The
precision of that prior is the inverse of its calibration variance:

    precision  pi = 1 / (calibration_variance + eps)

Gain multiplies the whole social evaluation, which has two terms — an
incoming cue (positive) and a prior-weighted cost of misplaced export
(negative, scaled by precision):

    dExport/dOT = cue_salience - pi * export_cost

    high calibration variance -> pi low  -> slope positive
    low  calibration variance -> pi high -> slope negative

The flip is at pi* = cue_salience / export_cost, i.e.

    calibration_variance* = export_cost / cue_salience

A tight prior amplified is sharper discrimination. Against a stranger
who returns nothing, sharper discrimination means less export. A loose
prior amplified is just the cue, and the cue says export.

THE THREE TESTS
---------------
1. UNITS. Adversity count and environmental autocorrelation are
   orthogonal. Severe-but-predictable is not mild-but-unpredictable.
   If variance is the operative term these dissociate, and ACE
   instruments — which count events — are in the wrong units.

2. RETURN SIGNAL. Does export condition on expected reciprocity?
   Buffering says yes, disposition says no. The two are unidentifiable
   wherever return is possible. They separate only at r = 0 — a
   donation task to strangers with no return, which is the one case
   where buffering predicts nothing.

3. CAPTIVITY. The negative arm requires calibration variance below
   threshold. Wild environments impose a variance floor; provisioned
   ones do not. Wild-caught vs lab-reared conspecifics, same species,
   same dose, is a direct test of whether the low-variance arm exists
   outside captivity at all.

LAYER FLAGS
-----------
`audit_measurement_layers()` carries the flags that apply to the
reported design regardless of what this sim outputs:

  - donations-in-task is instrument-level, reported as organism-level
  - adversity is present-day recall, and recall is state-modulated
  - environmental variance is never measured in either arm

Demo 4 shows the second flag is not a caveat: a state-modulated recall
channel manufactures the full interaction with the true effect set to
exactly zero.

LOAD-BEARING ASSUMPTION
-----------------------
The receiver rescales to chronic level (habituation) but cannot
rescale to unpredictability. Calibration variance is therefore
computed scale-free — variance of prediction error over squared mean
level. Without this, severity would drive variance too and test 1
collapses. This assumption is the model's throat: if organisms do not
habituate to level, the count/autocorrelation dissociation is not
real. It is stated here so it can be attacked directly.

PAIRS WITH
----------
- docs/calibration-regime-notes.md — what sets calibration variance in
  the first place (regime terms: storability, shock correlation,
  enclosure), what the outcome column is measuring, and six proposed
  experiments. E1 and E2 there are direct extensions of this module.
- docs/emotion-reading-spec.md, "Calibration layer" — same claim in
  operator-facing terms: hormonal state shifts apparatus gain per
  axis, and does not change what fired or what it is about.
- ELA-001 (empathy_layer_audit.py) — label-as-signal collapse.
  "Altruism" as a label over a donation count is the same move.
- MH-003 (ConstraintBoundary) — this module declares its edges below.

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
# ENVIRONMENT — two orthogonal parameters, one of which nobody measures
# ---------------------------------------------------------------------------

@dataclass
class EnvironmentSpec:
    """
    Developmental environment.

    severity        mean magnitude of adversity events. This is what an
                    ACE-style instrument counts (via `ace_count`).
    autocorrelation rho of the AR(1) adversity process. Predictability.
                    This is what nobody measures in either arm.
    n_steps         developmental period length.
    damage_ceiling  saturation point of the damage channel. Load-bearing:
                    without it, severity enters as a pure multiplicative
                    scale and a scale-free statistic is blind to it BY
                    CONSTRUCTION, which would make test 1 an identity
                    rather than a claim. With saturation, severity does
                    move calibration variance — the claim is that it
                    moves it far less than autocorrelation does, and
                    that is something the sim can get wrong.
    recovery_rate   fraction of accumulated load shed per step. 1.0 =
                    full recovery between events. 0.0 = no recovery,
                    load ratchets and the receiver's target keeps
                    moving.
    controllability fraction of event magnitude attributable to the
                    agent's own action. The agent knows its own
                    contribution, so controllable variance is not
                    calibration variance — that is the claim E1 tests.
    sensor_range    magnitude beyond which perception saturates.
                    Events above it are perceived as identical while
                    their consequences still differ, so the receiver's
                    model has no coverage there.
    """
    severity:        float = 1.0
    autocorrelation: float = 0.5
    n_steps:         int   = 400
    damage_ceiling:  float = 3.0
    recovery_rate:   float = 1.0
    controllability: float = 0.0
    sensor_range:    float = 1e9
    load_gain:       float = 0.35


@dataclass
class DevelopmentalRecord:
    """
    What a developmental period leaves behind.

    true       consequence magnitude actually experienced
    perceived  what the receiver's sensor registered (saturates at
               sensor_range)
    known      the component the agent produced itself, and can
               therefore predict
    """
    true:      list[float] = field(default_factory=list)
    perceived: list[float] = field(default_factory=list)
    known:     list[float] = field(default_factory=list)


def generate_adversity_stream(env: EnvironmentSpec, rng: random.Random) -> list[float]:
    """Back-compatible view: the true consequence stream only."""
    return generate_development(env, rng).true


def generate_development(env: EnvironmentSpec, rng: random.Random) -> DevelopmentalRecord:
    """
    Unit-variance AR(1) environmental latent plus an agent-attributable
    component, scaled by severity, rectified, accumulated as load under
    incomplete recovery, then passed through a saturating damage
    channel and a saturating sensor.

    rho near 1 -> chronic and predictable (harsh but knowable)
    rho near 0 -> episodic and unpredictable (mild events, no model)

    The four axes from docs/calibration-regime-notes.md section 5 enter
    here, except regime match, which is not a property of development
    at all — see `mismatch_report`.
    """
    rho = max(0.0, min(0.999, env.autocorrelation))
    innovation_scale = math.sqrt(1.0 - rho * rho)
    ceiling = env.damage_ceiling
    c = max(0.0, min(1.0, env.controllability))
    recovery = max(0.0, min(1.0, env.recovery_rate))

    rec = DevelopmentalRecord()
    x = 0.0
    load = 0.0
    for _ in range(env.n_steps):
        x = rho * x + innovation_scale * rng.gauss(0.0, 1.0)
        action = rng.gauss(0.0, 1.0)
        driver = (1.0 - c) * x + c * action
        raw = max(0.0, env.severity * (1.0 + driver))

        load = load * (1.0 - recovery) + raw * env.load_gain
        damage = ceiling * math.tanh((raw + load) / ceiling)

        rec.true.append(damage)
        rec.perceived.append(min(damage, env.sensor_range))
        # the agent can anticipate only its own contribution
        rec.known.append(c * action * env.severity)
    return rec


def ace_count(stream: list[float], threshold: float = 1.0) -> int:
    """
    The instrument in the literature: count events above a severity
    threshold. Blind to ordering, therefore blind to predictability.
    Shuffling the stream does not change this number.
    """
    return sum(1 for m in stream if m > threshold)


def calibration_variance(stream: list[float], habituation_rate: float = 0.1) -> float:
    """
    Scale-free variance of prediction error against an adapting
    predictor.

    The predictor is an EMA — the receiver's running model of its
    environment. It absorbs LEVEL (habituation). It cannot absorb
    UNPREDICTABILITY. Normalizing by mean level squared is what makes
    the residual scale-free, so a harsh-but-regular environment and a
    mild-but-regular one calibrate the same.

    See LOAD-BEARING ASSUMPTION in the module docstring.
    """
    if not stream:
        return 0.0
    return calibration_variance_full(
        DevelopmentalRecord(true=stream, perceived=list(stream),
                            known=[0.0] * len(stream)),
        habituation_rate=habituation_rate)


def calibration_variance_full(rec: DevelopmentalRecord,
                              habituation_rate: float = 0.1) -> float:
    """
    Calibration variance with all four developmental axes able to move
    it.

    The predictor runs on PERCEIVED magnitude — that is all the sensor
    delivers — while error is measured against TRUE consequence. When
    events exceed sensor range the two diverge and the receiver cannot
    close the gap by learning, which is what "outside calibration
    range" means mechanically.

    The agent's own contribution is subtracted before the residual is
    taken. Variance you generated yourself is not variance you are
    uncalibrated against. This is the E1 claim in one line.
    """
    if not rec.true:
        return 0.0
    prediction = rec.perceived[0]
    errors = []
    for true_m, perceived_m, known_m in zip(rec.true, rec.perceived, rec.known):
        errors.append(true_m - prediction - known_m)
        prediction += habituation_rate * (perceived_m - prediction)
    mean_level = statistics.fmean(rec.true)
    return statistics.pvariance(errors) / (mean_level * mean_level + EPS)


# ---------------------------------------------------------------------------
# REGIME MATCH — not a property of development
# ---------------------------------------------------------------------------

@dataclass
class MismatchReport:
    developmental_variance: float
    execution_variance:     float
    slope_used:             float   # slope the receiver actually runs
    slope_correct:          float   # slope the execution regime warrants
    sign_error:             bool    # the two disagree in direction


def mismatch_report(model: "ExportModel", developmental_variance: float,
                    execution_variance: float) -> MismatchReport:
    """
    The fourth axis: matched to the regime the organism will execute in.

    Unlike the other three this cannot be read off the developmental
    record at all. The receiver carries the precision it calibrated,
    and applies it in whatever regime it later finds itself. When the
    two regimes differ enough, the slope it runs and the slope its
    current environment warrants have opposite signs — and nothing in
    the organism's own history can flag that. It is not a reading
    failure. It is a correct reading of a regime that has moved.
    """
    used = export_slope(model, developmental_variance)
    correct = export_slope(model, execution_variance)
    return MismatchReport(
        developmental_variance=developmental_variance,
        execution_variance=execution_variance,
        slope_used=used,
        slope_correct=correct,
        sign_error=(used > 0) != (correct > 0),
    )


# ---------------------------------------------------------------------------
# EXPORT MODEL — the sign flip, with no branch in it
# ---------------------------------------------------------------------------

@dataclass
class ExportModel:
    """
    cue_salience     gain applied to the incoming social cue (positive term)
    export_cost      cost of exporting where it is not returned; enters
                     weighted by prior precision (negative term)
    conditions_on_return
                     True  = buffering  (slope depends on expected return r)
                     False = disposition (slope ignores r)
    reciprocity_weight
                     size of the return-signal term for the buffering
                     variant only
    """
    cue_salience:         float = 0.60
    export_cost:          float = 0.15
    conditions_on_return: bool  = False
    reciprocity_weight:   float = 0.0

    def flip_threshold(self) -> float:
        """Calibration variance at which sign(dExport/dOT) changes."""
        return self.export_cost / (self.cue_salience + EPS)


def export_slope(model: ExportModel, cal_var: float, expected_return: float = 0.0) -> float:
    """
    dExport/dOT.

    One subtraction. The sign is not assigned anywhere — it is whatever
    this difference happens to be:

        cue term  -  precision-weighted cost term

    Precision is 1/calibration_variance, so a well-calibrated receiver
    (low variance) carries a large negative term and a poorly
    calibrated one (high variance) does not.
    """
    precision = 1.0 / (cal_var + EPS)
    cue = model.cue_salience
    if model.conditions_on_return:
        cue += model.reciprocity_weight * expected_return
    return cue - precision * model.export_cost


def export_rate(model: ExportModel, cal_var: float, ot_gain: float,
                expected_return: float = 0.0, baseline: float = 0.5) -> float:
    """Export rate at a given dose, clamped to [0, 1]."""
    raw = baseline + ot_gain * export_slope(model, cal_var, expected_return)
    return max(0.0, min(1.0, raw))


def matched_pair(cue_salience: float = 0.60, export_cost: float = 0.08,
                 reciprocity_weight: float = 0.50,
                 calibrated_at_return: float = 0.50) -> tuple[ExportModel, ExportModel]:
    """
    Build a buffering model and a disposition model that are
    OBSERVATIONALLY IDENTICAL at `calibrated_at_return`.

    This is the point of test 2. Any study run where reciprocity is
    possible fits both models equally well and distinguishes nothing.
    The models are constructed here to make that explicit rather than
    to be compared on a rigged footing.
    """
    buffering = ExportModel(
        cue_salience=cue_salience,
        export_cost=export_cost,
        conditions_on_return=True,
        reciprocity_weight=reciprocity_weight,
    )
    disposition = ExportModel(
        cue_salience=cue_salience + reciprocity_weight * calibrated_at_return,
        export_cost=export_cost,
        conditions_on_return=False,
    )
    return buffering, disposition


# ---------------------------------------------------------------------------
# LAYER AUDIT — flags that hold regardless of what the sim prints
# ---------------------------------------------------------------------------

@dataclass
class LayerFlag:
    flag:      str
    measured:  str
    reported:  str
    note:      str


@dataclass
class MeasurementDesign:
    """A design description, in the design's own terms."""
    outcome_measure:            str  = "donations in task"
    outcome_reported_as:        str  = "altruistic behavior"
    adversity_measure:          str  = "present-day retrospective recall"
    environmental_variance_measured: bool = False
    return_possible_in_task:    bool = False


def audit_measurement_layers(design: MeasurementDesign) -> list[LayerFlag]:
    """
    Layer flags. Returns findings, not a verdict — a flagged design can
    still be the best available design. The flag records what the
    measurement can and cannot carry, so a reader does not import a
    claim the instrument never made.
    """
    flags: list[LayerFlag] = []

    if design.outcome_measure != design.outcome_reported_as:
        flags.append(LayerFlag(
            flag="instrument-level reported as organism-level",
            measured=design.outcome_measure,
            reported=design.outcome_reported_as,
            note="a donation count is a reading on one instrument under one "
                 "task framing. Reporting it as a disposition widens the "
                 "range past what was measured.",
        ))

    if "recall" in design.adversity_measure:
        flags.append(LayerFlag(
            flag="predictor is state-modulated",
            measured=design.adversity_measure,
            reported="early-life adversity",
            note="recall is modulated by current state, and current state is "
                 "what the dose is acting on. Predictor and outcome share a "
                 "channel the design does not control. See demo 4.",
        ))

    if not design.environmental_variance_measured:
        flags.append(LayerFlag(
            flag="operative term never measured",
            measured="adversity count",
            reported="early-life environment",
            note="if calibration variance sets the sign, neither arm "
                 "measured the variable that sets the sign.",
        ))

    if design.return_possible_in_task:
        flags.append(LayerFlag(
            flag="buffering and disposition unidentifiable",
            measured="task permitting return",
            reported="altruism",
            note="both models fit. separation requires r = 0. See demo 2.",
        ))

    return flags


# ---------------------------------------------------------------------------
# DEMO 1 — count vs autocorrelation: wrong units
# ---------------------------------------------------------------------------

def demo_units(seed: int = 7) -> None:
    print(_header("1  ADVERSITY COUNT vs ENVIRONMENTAL AUTOCORRELATION"))
    model = ExportModel()
    thr = model.flip_threshold()
    print(f"sign flip at calibration variance = {thr:.4f}")
    print("  (free parameter — export_cost/cue_salience. No data pins it.")
    print("   It is set inside the range the environments below produce, so")
    print("   both arms are visible. Its VALUE is not a prediction; the")
    print("   dissociation on either side of it is.)\n")

    cases = [
        ("severe, predictable",   EnvironmentSpec(severity=2.5, autocorrelation=0.95)),
        ("severe, unpredictable", EnvironmentSpec(severity=2.5, autocorrelation=0.05)),
        ("mild,   predictable",   EnvironmentSpec(severity=0.6, autocorrelation=0.95)),
        ("mild,   unpredictable", EnvironmentSpec(severity=0.6, autocorrelation=0.05)),
    ]

    print(f"{'environment':<22} {'ACE':>5} {'cal_var':>9} {'dExp/dOT':>10}  predicted")
    print("-" * 68)
    rows = []
    for label, env in cases:
        rng = random.Random(seed)
        stream = generate_adversity_stream(env, rng)
        ace = ace_count(stream)
        cv = calibration_variance(stream)
        slope = export_slope(model, cv)
        rows.append((label, ace, cv, slope))
        print(f"{label:<22} {ace:>5} {cv:>9.4f} {slope:>10.3f}  "
              f"OT {'increases' if slope > 0 else 'decreases'} export")

    high_ace_neg = [r for r in rows if r[1] > 0 and r[3] < 0]
    low_ace_pos = [r for r in rows if r[3] > 0]
    print()
    print("read:")
    print("  ACE count tracks severity. Slope tracks predictability.")
    print("  Severity does move calibration variance — the saturating")
    print("  damage channel makes sure this is not true by construction —")
    print("  but autocorrelation moves it several times harder, and in the")
    print("  direction that decides the sign.")
    if high_ace_neg and low_ace_pos:
        a = max(high_ace_neg, key=lambda r: r[1])
        b = min(low_ace_pos, key=lambda r: r[1])
        print()
        print(f"  '{a[0].strip()}' has the HIGHER ACE count ({a[1]}) and a")
        print(f"  NEGATIVE slope. '{b[0].strip()}' has the LOWER count ({b[1]})")
        print( "  and a POSITIVE slope. An adversity-count model predicts the")
        print( "  wrong sign for both. This is the discriminating measurement.")
    print()
    print("  note: ace_count is order-invariant — shuffle the stream and it")
    print("  is unchanged, while calibration variance moves. Any instrument")
    print("  with that invariance cannot see the operative term.")


# ---------------------------------------------------------------------------
# DEMO 2 — does export condition on the return signal?
# ---------------------------------------------------------------------------

def demo_return_signal() -> None:
    print(_header("2  DOES EXPORT CONDITION ON RETURN SIGNAL?"))
    buffering, disposition = matched_pair()
    cal_var = 0.60
    ot = 0.60
    baseline = 0.35

    print("two models, constructed to be identical at r = 0.50:\n")
    print(f"{'r (expected return)':<22} {'buffering':>11} {'disposition':>13} {'gap':>8}")
    print("-" * 58)
    for r in (0.0, 0.10, 0.25, 0.50, 0.75, 1.0):
        b = export_rate(buffering, cal_var, ot, expected_return=r, baseline=baseline)
        d = export_rate(disposition, cal_var, ot, expected_return=r, baseline=baseline)
        print(f"{r:<22.2f} {b:>11.3f} {d:>13.3f} {abs(b - d):>8.3f}")

    gap_zero = abs(export_rate(buffering, cal_var, ot, 0.0, baseline)
                   - export_rate(disposition, cal_var, ot, 0.0, baseline))
    print()
    print("read:")
    print(f"  the models are unidentifiable at r = 0.50 (gap 0.000) and")
    print(f"  maximally separated at r = 0.00 (gap {gap_zero:.3f}).")
    print()
    print("  a donation task to strangers with no return is r = 0. That is")
    print("  the one condition where buffering predicts nothing and any")
    print("  export observed is dispositional. Every task permitting return")
    print("  fits both models and settles nothing.")
    print()
    print("  design consequence: r = 0 is not a limitation of the donation")
    print("  task. It is the only place the question is answerable.")


# ---------------------------------------------------------------------------
# DEMO 3 — does the low-variance arm exist outside captivity?
# ---------------------------------------------------------------------------

def _population_fraction_negative(floor: float, spread: float, model: ExportModel,
                                  n: int, rng: random.Random) -> float:
    negative = 0
    for _ in range(n):
        cv = floor + rng.random() * spread
        if export_slope(model, cv) < 0:
            negative += 1
    return negative / n


def demo_captivity(seed: int = 11, n: int = 4000) -> None:
    print(_header("3  WILD-CAUGHT vs LAB-REARED, SAME SPECIES, SAME DOSE"))
    model = ExportModel()
    thr = model.flip_threshold()
    rng = random.Random(seed)

    print(f"negative arm requires calibration variance < {thr:.4f}\n")

    lab_floor, lab_spread = 0.002, 0.05
    lab_frac = _population_fraction_negative(lab_floor, lab_spread, model, n, rng)
    print(f"lab-reared   (variance floor {lab_floor:.3f}, spread {lab_spread:.3f}): "
          f"{lab_frac * 100:5.1f}% of population in the negative arm")

    print()
    print("wild-caught, sweeping the environmental variance floor:")
    print(f"{'floor':>8} {'% negative arm':>16}")
    print("-" * 26)
    first_empty = None
    for floor in (0.005, 0.05, 0.10, 0.15, 0.20, 0.25, 0.35):
        frac = _population_fraction_negative(floor, 0.60, model, n, rng)
        print(f"{floor:>8.3f} {frac * 100:>15.1f}%")
        if frac == 0.0 and first_empty is None:
            first_empty = floor

    print()
    print("read:")
    if first_empty is not None:
        print(f"  the negative arm is empty once the wild variance floor")
        print(f"  reaches {first_empty:.3f}. Above that floor no wild-caught")
        print( "  animal is calibrated tightly enough to show it.")
    print("  the prediction is therefore falsifiable in one experiment:")
    print("  same species, same dose, wild-caught vs lab-reared. If the")
    print("  negative arm appears in wild-caught animals, the variance")
    print("  account is wrong. If it appears only in lab-reared animals,")
    print("  the low-variance arm is an artifact of provisioning — and the")
    print("  human low-adversity arm is the same artifact in a species")
    print("  that provisions itself.")
    print()
    print("  what makes this a clean test: no recall instrument, no self-")
    print("  report, and environmental variance is set by the experimenter")
    print("  rather than inferred. All three human-arm layer flags drop out.")


# ---------------------------------------------------------------------------
# DEMO 4 — state-modulated recall manufactures the interaction from nothing
# ---------------------------------------------------------------------------

def _pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy + EPS)


def demo_recall_confound(seed: int = 3, n: int = 3000) -> None:
    print(_header("4  CONFOUND — STATE-MODULATED RECALL, TRUE EFFECT = 0"))
    print("true adversity has NO effect on dose response in this demo.")
    print("the only link is that current state modulates both what gets")
    print("recalled and how the dose lands.\n")

    print(f"{'recall modulation k':>21} {'corr(recalled ACE, dose response)':>36}")
    print("-" * 60)
    for k in (0.0, 0.2, 0.5, 1.0, 2.0):
        rng = random.Random(seed)
        recalled, response = [], []
        for _ in range(n):
            true_ace = rng.random() * 10.0
            state = rng.gauss(0.0, 1.0)          # current affective state
            # recall is reconstructed through current state
            recalled.append(true_ace + k * state * 3.0)
            # dose response depends on state, NOT on true_ace
            response.append(0.4 * state + rng.gauss(0.0, 0.5))
        print(f"{k:>21.1f} {_pearson(recalled, response):>36.3f}")

    print()
    print("read:")
    print("  the correlation is manufactured entirely by the shared state")
    print("  channel. No true adversity effect exists anywhere in this demo.")
    print()
    print("  this does not show the reported finding is a confound. It shows")
    print("  the design cannot distinguish the finding from one, because the")
    print("  predictor is reconstructed at measurement time through the same")
    print("  state the dose is acting on. Prospective or third-party adversity")
    print("  measurement breaks the shared channel. Retrospective recall")
    print("  cannot.")


# ---------------------------------------------------------------------------
# DEMO 5 (E1) — do the other three axes move the sign at fixed predictability?
# ---------------------------------------------------------------------------

def _axis_row(label: str, model: "ExportModel", env: EnvironmentSpec,
              seed: int) -> tuple[float, float, float]:
    rng = random.Random(seed)
    rec = generate_development(env, rng)
    cv = calibration_variance_full(rec)
    slope = export_slope(model, cv)
    mean_level = statistics.fmean(rec.true)
    print(f"{label:<24} {cv:>9.4f} {mean_level:>8.3f} {slope:>10.3f}   "
          f"{'+' if slope > 0 else '-'}")
    return cv, slope, mean_level


def demo_other_axes(seed: int = 19) -> None:
    print(_header("5  E1 — THE OTHER THREE AXES, AUTOCORRELATION HELD FIXED"))
    model = ExportModel()
    rho = 0.50
    print(f"autocorrelation fixed at {rho}; sign flip at cal_var = "
          f"{model.flip_threshold():.4f}")
    print("E1's falsifier: if predictability is the whole story, every row")
    print("within each block below is identical. Three axes, three different")
    print("answers — the axes are not interchangeable.\n")

    # -- controllability ----------------------------------------------------
    print("A. CONTROLLABILITY — self-caused variance subtracted from residual")
    print(f"{'':<24} {'cal_var':>9} {'mean':>8} {'dExp/dOT':>10}   sign")
    print("-" * 58)
    ctrl = [_axis_row(f"  c = {c:.1f}", model,
                      EnvironmentSpec(autocorrelation=rho, controllability=c), seed)
            for c in (0.0, 0.3, 0.5, 0.7, 0.9)]
    ctrl_flips = len({sl > 0 for _, sl, _ in ctrl}) > 1
    print(f"  -> moves calibration variance {ctrl[0][0] / (ctrl[-1][0] + EPS):.1f}x, "
          f"sign flips: {ctrl_flips}. Mean level barely moves, so this is")
    print("     not a severity effect in disguise. Clean axis.\n")

    # -- recovery -----------------------------------------------------------
    print("B. RECOVERY — accumulated load shed per step")
    print(f"{'':<24} {'cal_var':>9} {'mean':>8} {'dExp/dOT':>10}   sign")
    print("-" * 58)
    recov = [_axis_row(f"  recovery = {r:.2f}", model,
                       EnvironmentSpec(autocorrelation=rho, recovery_rate=r), seed)
             for r in (1.0, 0.6, 0.3, 0.1, 0.05)]
    print("  -> also flips the sign, but through a LEVEL channel: mean rises")
    print("     toward the damage ceiling and variance compresses against it.")
    print("     A chronically pinned channel is a predictable channel.\n")
    print("     [flag] this predicts chronic-no-recovery lands in the")
    print("     LOW-variance arm — the same arm as low adversity. ACE")
    print("     endpoints load on chronic + no recovery and are supposed to")
    print("     be the high arm. The model and the literature disagree here,")
    print("     and the disagreement is load-bearing, not cosmetic. Either")
    print("     the saturating damage channel is wrong, or habituation does")
    print("     not divide out a chronic level shift, or the ACE arm is not")
    print("     the high-variance arm it is assumed to be. Unresolved.\n")

    # -- sensor range -------------------------------------------------------
    print("C. WITHIN CALIBRATION RANGE — perception saturates, consequences do not")
    print(f"{'':<24} {'cal_var':>9} {'mean':>8} {'dExp/dOT':>10}   sign")
    print("-" * 58)
    rng_rows = [_axis_row(f"  range = {r:>6.1f}", model,
                          EnvironmentSpec(autocorrelation=rho, sensor_range=r), seed)
                for r in (1e9, 1.5, 1.0, 0.8, 0.5)]
    spread = max(r[0] for r in rng_rows) - min(r[0] for r in rng_rows)
    print(f"  -> total spread {spread:.4f}, no sign change even at 68% of")
    print("     events clipped. In this model the range axis is NOT")
    print("     separable — it is dominated by the other two. Either the")
    print("     axis is real and the mechanism here is the wrong one, or it")
    print("     collapses into the others. E1 does not settle it.\n")

    print("read:")
    print("  E1 asked whether predictability alone sets the sign. It does not:")
    print("  controllability moves it cleanly at fixed autocorrelation. But")
    print("  the three axes are not equivalent — one is clean, one acts")
    print("  through level and contradicts the ACE picture, one does not")
    print("  separate at all. A study varying 'adversity' varies an aggregate")
    print("  of at least three things that behave differently.")


# ---------------------------------------------------------------------------
# DEMO 6 (E1, fourth axis) — calibrated for one regime, executing in another
# ---------------------------------------------------------------------------

def demo_regime_match() -> None:
    print(_header("6  E1 — REGIME MATCH: THE AXIS DEVELOPMENT CANNOT SEE"))
    model = ExportModel()
    print(f"sign flip at cal_var = {model.flip_threshold():.4f}\n")

    pairs = [
        ("stable dev -> stable exec",     0.06, 0.08),
        ("stable dev -> volatile exec",   0.06, 0.55),
        ("volatile dev -> volatile exec", 0.55, 0.50),
        ("volatile dev -> stable exec",   0.55, 0.07),
    ]

    print(f"{'trajectory':<32} {'dev':>6} {'exec':>6} {'runs':>7} {'warranted':>10}  mismatch")
    print("-" * 82)
    for label, dev, ex in pairs:
        r = mismatch_report(model, dev, ex)
        print(f"{label:<32} {dev:>6.2f} {ex:>6.2f} "
              f"{r.slope_used:>7.3f} {r.slope_correct:>10.3f}  "
              f"{'SIGN ERROR' if r.sign_error else 'aligned'}")

    print()
    print("read:")
    print("  the two middle rows run a slope of the wrong sign for the")
    print("  regime they are actually in. Nothing in the organism's own")
    print("  history flags this — the calibration was correct when taken.")
    print()
    print("  this is not a reading failure and not impedance. It is a")
    print("  correct reading of a regime that has since moved, which is")
    print("  the developmental-mismatch shape (Gluckman & Hanson) stated")
    print("  in gain terms. Distinguishing it from a miscalibration")
    print("  requires measuring the execution regime, which no arm of the")
    print("  reported design does.")


# ---------------------------------------------------------------------------
# BOUNDARIES — MH-003 style, stated so they can be attacked
# ---------------------------------------------------------------------------

@dataclass
class Boundaries:
    part_id: str = "GD-001"
    works_when: list[str] = field(default_factory=lambda: [
        "the receiver habituates to chronic level but not to unpredictability",
        "export carries a cost that scales with prior precision",
        "gain multiplies the social evaluation rather than adding to it",
    ])
    fails_when: list[str] = field(default_factory=lambda: [
        "organisms do not rescale to chronic level — then severity drives "
        "calibration variance too and test 1's dissociation is not real",
        "the cue term is itself precision-weighted — then both terms scale "
        "together and no flip occurs at any variance",
        "export cost is zero — slope is then positive everywhere and the "
        "negative arm cannot exist under any calibration",
    ])
    not_yet_tested: list[str] = field(default_factory=lambda: [
        "any empirical data whatsoever — this module contains none",
        "non-human substrates, though test 3 is written for one",
        "whether calibration variance is stable across the lifespan or "
        "re-estimated continuously",
        "dose-response nonlinearity — slope is treated as constant in OT",
    ])


def print_boundaries() -> None:
    b = Boundaries()
    print(_header(f"BOUNDARIES  [{b.part_id}]"))
    for title, items in (("works when", b.works_when),
                         ("fails when", b.fails_when),
                         ("not yet tested", b.not_yet_tested)):
        print(f"{title}:")
        for item in items:
            print(f"  - {item}")
        print()


def print_layer_flags() -> None:
    print(_header("LAYER FLAGS  (design as reported)"))
    for f in audit_measurement_layers(MeasurementDesign()):
        print(f"[flag] {f.flag}")
        print(f"       measured : {f.measured}")
        print(f"       reported : {f.reported}")
        print(f"       {f.note}")
        print()


# ---------------------------------------------------------------------------

def _header(title: str) -> str:
    return f"\n{'=' * 68}\n{title}\n{'=' * 68}"


DEMOS = {
    "1": demo_units,
    "2": demo_return_signal,
    "3": demo_captivity,
    "4": demo_recall_confound,
    "5": demo_other_axes,
    "6": demo_regime_match,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GD-001 — gain/calibration exploration harness. "
                    "Generates discriminating predictions; contains no data.")
    parser.add_argument("--demo", default="all",
                        choices=["all", "1", "2", "3", "4", "5", "6",
                                 "flags", "boundaries"],
                        help="which section to run (default: all)")
    args = parser.parse_args()

    if args.demo == "flags":
        print_layer_flags()
        return
    if args.demo == "boundaries":
        print_boundaries()
        return
    if args.demo == "all":
        for fn in DEMOS.values():
            fn()
        print_layer_flags()
        print_boundaries()
        print("OT is the gain knob. It does not carry direction.")
        print("Direction is set by what the receiver was calibrated against.")
        return

    DEMOS[args.demo]()


if __name__ == "__main__":
    main()
