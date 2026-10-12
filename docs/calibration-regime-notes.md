# Calibration Regime — notes for further experimentation

Status: notes, with two experiments now run. E1 and E2 have results
(§7); everything else is unmeasured. Nothing here is empirical — the
runs are simulations of the model, not tests of the world.

GD-001 (`metrology/gain_direction_sim.py`) models the receiver: gain ×
calibration sets the export sign. It takes calibration variance as
given. These notes are about what sets it — the regime the receiver
was calibrated against — and about what the outcome column is
measuring when someone reports whether a result was good.

---

## 1. Regime terms — when zero-sum is the correct model

Three terms on a resource:

| term | question |
|---|---|
| storability | can the stock be held without loss? |
| shock_corr  | do agents fail independently, or together? |
| enclosure   | is the stock bounded and assignable? |

**zero-sum correct when** storable + covariant + enclosed

- pooling buys nothing — all fail at once
- holding beats circulating
- total is knowable, so transfer is pure loss
- grain, land, herds

**sharing correct when** non-storable + idiosyncratic + unenclosed

- your bad day is not my bad day
- the pool *is* the storage medium
- export now = claim on the pool later
- large game, fish runs, forage windfalls

Neither is a moral position. Both are correct strategies, each under
its own regime. "Sharing culture" and "hoarding culture" are regime
readouts, not dispositions — the same structure as a neuromodulator
carrying gain and no direction.

### Consequence for GD-001's test 2 [inf]

Demo 2 establishes that r = 0 is the only condition where buffering
and disposition separate. The regime terms say r = 0 is also a regime
imposition: a task with no return has stripped storability and
enclosure to the zero-sum corner.

So low export at r = 0 has two readings that the task cannot separate:

- reduced altruism (a disposition reading)
- a correct regime reading — export into a pool that does not exist is
  not storage, and declining it is the calibrated response

Both are consistent with the same number. This does not undo test 2 —
it is still the only place buffering and disposition come apart — but
it means the r = 0 measurement carries its own confound, and the
identifying condition and the confounding condition are the same
condition.

*Since resolved by E2 (§7): the confound is real and large — a 7.6x
disposition difference is invisible in the level — and the escape is a
paired design rather than a better single task.*

---

## 2. Which term actually moved

- storability — ~flat
- shock_corr — ↑ regional and sectoral shocks hit whole areas at once;
  covariant failure
- enclosure — ↑↑ the big mover

Pooled → individually assigned:

```
defined benefit           →  individual account
employer/union risk pool  →  individual market
tenure / seniority        →  at-will + individual contract
```

Two readings, and the measurement that splits them:

| reading | prediction |
|---|---|
| enclosure-increased | pooled-share time series should decline — pension type mix, risk-pool participation, coverage breadth |
| visibility-increased | pooled share ~flat, but coverage breadth was low the whole time and the excluded fraction was large |

This is a discriminating archival measurement, not a simulation.
Sources not yet identified. [open]

---

## 3. The outcome column

- **measured** — mortality, morbidity, height, birth weight, years of
  schooling, income, self-report scales
- **objective** — never stated. Inferred from which direction of the
  measured variable gets called improvement.

So: *"comfort is better" is not a finding. It is the sign convention
on the outcome column.*

This is a layer flag of the same family GD-001 already carries: an
unstated objective reported as a result. It differs from the others in
that no amount of care with the measured variables fixes it — the
objective is upstream of all of them.

---

## 4. Adjacent literatures — what each gives, and what it does not

| literature | gives | does not give |
|---|---|---|
| hormesis | dose-response with a beneficial low-dose region. Established in toxicology, exercise physiology, some thermal and fasting work. The shape is a fact. | the extrapolation to "adversity is good." That is not in the data. |
| developmental mismatch | Gluckman & Hanson; the "old friends" / microbial exposure work. Calibration set for one regime, executed in another — the same shape being run here. | a measurement of the regime gap itself |
| antifragility | Taleb. Useful vocabulary. | evidence, or any measurement protocol. It is a framework. |

---

## 5. What is actually varying

Not adversity magnitude. Whether the stressor is:

- within calibration range
- followed by recovery
- predictable / agent-controllable
- matched to the regime the organism will execute in

ACE endpoints load on chronic + unpredictable + no recovery + no
control. Hormetic protocols load on bounded + recovered + controlled.

The two literatures are therefore not measuring one variable at
different doses. They are measuring different variables, and the
apparent contradiction between them is an artifact of the shared word.

GD-001 now implements all four — predictability as AR(1)
autocorrelation, recovery as shed load, controllability as
self-attributable variance, range as sensor saturation, and regime
match as the mismatch report. E1 ran them and they did not behave
alike; see §7.

---

## 6. The divergence, and where it does not survive

The physics ran a very long optimization for reproductive success
under Holocene-and-earlier conditions. That is not the objective
comfort optimizes for. The two diverge, and the divergence is the
part with no instrument on it: a regime that maximizes lifespan and
reported wellbeing can simultaneously produce a population that fails
on capacities never in the outcome column.

**Where it does not survive.** "Selection ran it, therefore it is
right" imports an objective too. Selection optimizes fitness in the
ancestral regime, full stop — indifferent to suffering, no foresight,
keeps whatever was locally reachable, and its answers are correct for
conditions that no longer obtain. Same mismatch problem, opposite
direction.

**The n=1 constraint.** No alternative regime is available to compare
against. One observed instance of a functioning biosphere, and it is
also the only calibration set. This resolves neither direction. It
states that the comparison arm does not exist. [obs]

**What would measure it.** An outcome variable neither literature
has: *capacity under conditions the environment normally supplies and
has stopped supplying.* There is no study to cite because nobody is
measuring that column. This is the tool-off metrology case — see the
carrier note in `docs/emotion-reading-spec.md`. [open]

---

## 7. Proposed experiments

**E1 — the other three axes.** *Run — GD-001 demos 5 and 6.*
Predictability alone does not set the sign, but the three axes are not
equivalent and the run gave three different answers:

- *controllability* — clean. Moves calibration variance ~8x at fixed
  autocorrelation with almost no change in mean level, and flips the
  sign. Self-caused variance is not variance you are uncalibrated
  against.
- *recovery* — flips the sign too, but through a level channel: mean
  rises toward the damage ceiling and variance compresses against it,
  so a chronically pinned channel reads as predictable. **This puts
  chronic-no-recovery in the LOW-variance arm, the same arm as low
  adversity — the opposite of where ACE endpoints are assumed to sit.**
  Either the saturating damage channel is wrong, or habituation does
  not divide out a chronic level shift, or the ACE arm is not the
  high-variance arm it is taken to be. [open]
- *within calibration range* — not separable. Total spread 0.022 with
  no sign change even at 68% of events clipped. Either the axis is
  real and the mechanism modeled is the wrong one, or it collapses
  into the others. [open]

Regime match (demo 6) behaves as its own axis: it cannot be read off
the developmental record at all, and produces slopes of the wrong sign
for the current regime with nothing in the organism's history to flag
it.

**E2 — regime layer.** *Run — GD-002 (`metrology/regime_layer_sim.py`).*
Both named corners came out as claimed when the strategies were
actually run rather than asserted. Three results beyond that:

- *shock correlation is the decisive term*, not enclosure. High
  enclosure alone does not make zero-sum correct — when deficits are
  rare and uncorrelated, the small unenclosed remainder still covers
  them. Enclosure needs covariant shocks to bite, which is the pairing
  §2 flags as having moved together.
- *the confound is real and large.* In a task that reveals nothing
  about its own regime, a full-disposition agent calibrated in a
  zero-sum regime and a 7.6x-less-disposed agent calibrated in a
  sharing regime emit the same number. Export at r = 0 does not rank
  disposition unless calibration is known.
- *the fix is the opposite of the obvious one.* Making the return
  channel observable does not probe calibration — it washes the prior
  out, which is why disposition survives in the delta. The delta
  recovers the true disposition ratio to within 7% where the level is
  off by 87%. So the level at low observability carries calibration
  and the delta at high observability carries disposition, and neither
  readout alone is interpretable.

**E3 — pooled-share time series.** Archival, not simulated. Pension
type mix, risk-pool participation, coverage breadth over time.
*Discriminates:* enclosure-increased from visibility-increased (§2).
Blocked on source identification. [open]

**E4 — outcome column audit.** Take a set of published adversity
studies, extract the measured variables, and record the objective each
one implies from its improvement direction. Output is the distribution
of implied sign conventions, not a verdict on any study.
*Instrument:* extend `audit_measurement_layers()` in GD-001 to take a
list of designs.

**E5 — capacity under withdrawal.** The missing column from §6.
Measure capacity in conditions the environment normally supplies and
has stopped supplying. Design constraint: the withdrawal must be of
something normally supplied, or it measures novelty response instead.
No existing instrument. This is the one that has to be built rather
than borrowed. [open]

**E6 — wild-caught vs lab-reared.** Already specified as GD-001 test
3. Needs a species with both populations available and an existing
neuromodulator literature. The cleanest of the six: no recall
instrument, no self-report, and environmental variance set by the
experimenter rather than inferred.

**E7 — the provisioning probe.** *Run — GD-003
(`metrology/provisioning_probe_sim.py`).* Four parts, four results:

1. *Confidence is flat across the entire provisioning gradient* while
   validity falls monotonically. Every agent's own internal state
   reads nominal because the buffer absorbed what would have
   contradicted it. The confidence-accuracy gap is the coupling
   deficit, and the probe ratio converges on (1 − coupling) exactly.
2. *Probe sizing is the protocol's main cost driver, and it was not
   visible before running it.* The ratio is not scale-free — below the
   observation-noise floor it is noise, and the required probe size
   scales inversely with the deficit being detected. Detecting a 5%
   coupling deficit needs a probe 10x the one that detects 50%. Small
   probes are small relative to a real shock, not absolutely.
3. *Calibrated keeps the ceiling and steepens the working range.* Full
   response remains available at high severity; what changed is that
   less is spent below threshold. Blunted has no gradient anywhere.
   The two are identical at a matched stimulus by construction, so the
   minimum viable protocol is ≥3 severities plus a recovery time
   constant plus resting level.
4. *The deficit reading and the allocation reading are identical on
   single-domain data.* The bidirectional protocol produces a
   crossover under allocation (+0.453 interaction) and none under
   deficit (0.000), but env-B-only items return "A deficit" under
   both. The verdict is computed from the run, not asserted.

This is the runnable form of §6's missing column — capacity under
conditions the environment normally supplies and has stopped
supplying. [obs on the model; no empirical data]

*Open:* the domain-transfer coefficient in parts 3–4 is stipulated,
not derived, and it is what makes the crossover appear. Probe-rate
effects are unswept — repeated contingency breaks are training trials,
so a probe frequent enough becomes the environment.

**E8 — the three probes with no slot.** *Run — GD-003 demo 5 and
`--demo gradient`.* Added K11 throughput, K12 reliance validation, K13
relearn time constant, against an inventory whose probes all sit at
fixed regime and none of which returns a rate.

- *K11 throughput* — distinguishable environmental states registered
  per unit time. Neither delay nor reliability: the buffer is fast and
  perfectly consistent, and what it is not is wide. Capacity, not
  quality.
- *K12 reliance validation* — reliance weight and sensor validity are
  two numbers routinely reported as one. Trust is a measurement only
  if validity was ever run against outcome; otherwise it is a weight
  with an empty validation history. The probe returns the pair plus
  the history count and labels the unvalidated case explicitly.
- *K13 tau* — **its own prediction is falsified.** "tau rises with
  provisioning; flat tau falsifies" comes out flat under fixed-rate
  updating (7% relative spread, tracking the analytic constant
  1/(rate x E[act^2]) = 20) and flat under confidence-weighted
  updating (14%), while latency moves 46x over the same rows.
  Provisioning moves where relearning *starts*, not how fast it
  proceeds.
  - The reason is not separate from E7: confidence is flat across the
    provisioning gradient because the buffer absorbs what would raise
    observed error, so any rate mechanism driven by confidence is flat
    too. Building the slowdown into the update rule does not rescue
    the prediction — it slows every agent equally.
  - What tau does separate is the *update rule* (24 vs 237, ~10x). Its
    object_of is the learner, not the environment. The declaration
    moves; the result stands.
  - Latency cannot substitute. It rises under both rules and across
    the whole gradient, reading as "slow relearn" in every cell where
    the rate is in fact unchanged.

*Gradient audit.* The stated falsifier is about a gradient; a probe
that generates at a single point cannot fail it whatever it returns.
3 of 8 parts in GD-003 sweep something — severity, condition, domain —
but not the variable the falsifier names. Not a missing probe: a
missing dimension on probes that already exist. [open]

---

## Ordering

E1, E2, E7 and E8 have been run — see above. E4 is a paper
exercise. E6 is a real experiment with an existing design. E3 is
blocked on sources. E5 is blocked on having no instrument, which is
also what makes it the one worth building.

---

## Tags

- [obs]   direct operator observation
- [inf]   inference
- [open]  unresolved

Referenced, not in this repo: tool-off-metrology; G-FIT (see
`logs/reflex-log-1.md`).
