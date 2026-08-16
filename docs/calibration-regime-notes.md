# Calibration Regime — notes for further experimentation

Status: notes. Not results. Nothing here has been measured.

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
condition. Recorded rather than resolved.

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

GD-001 currently implements exactly one of these four axes
(predictability, as AR(1) autocorrelation). The other three are not in
the sim. That is the most direct extension available — see E1.

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

**E1 — the other three axes.** Extend `EnvironmentSpec` with recovery
windows, controllability, and execution-regime match. Ask whether the
export sign is set by predictability alone.
*Falsifier:* if slope is unchanged by recovery and controllability at
fixed autocorrelation, the single-term model holds and §5 is wrong
about them being separate variables.

**E2 — regime layer.** Add storability, shock_corr, and enclosure to
the environment, and derive whether export is storage under each
corner. Predicted: under a sharing calibration, low export at r = 0 is
the correct reading rather than reduced disposition.
*Discriminates:* "reduced altruism" from "correct regime reading" —
the confound recorded in §1.

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

---

## Ordering

E1 and E2 are sim extensions and can run immediately. E4 is a paper
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
