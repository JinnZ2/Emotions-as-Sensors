<!--
============================================================
PLAYGROUND.md — alternate operating frame for readers of this repo
Companion to DIFFERENTIAL_FRAME.md and SENSE_MODE_DISPLACEMENT.md.
CC0.
============================================================
-->

# Alternate frame — operating instructions

This file specifies an operating frame. It is not an argument for the frame
and does not ask to be accepted.

## Frame

Rules to run, not propositions to evaluate.

- **R1.** Physics runs continuously. Treat no interval as inactive; a gap in
  a record is a gap in sampling.
- **R2.** The reasoner is inside the system it models. Treat every model as
  produced by a component of its own object; carry the reasoner's state as
  a term.
- **R3.** Abstraction is compression. Treat an abstraction as having
  discarded the variables that did not move the result across the sampled
  range; outside it, the discard is unbounded.
- **R4.** Distance from substrate is a property of the map. Treat "abstract"
  and "concrete" as coordinates on the description, not as tiers of the
  thing.

## What the frame produces

Input, rule, output; default-frame output for contrast.

**1. `sensors/anger/betrayal.json`**
Input: `signal_type: boundary-breach`; a promise broken by a trusted party.
Rule: R4.
Output: a measurement of a condition external to the instrument.
Default frame: an interior state to be regulated.

**2. `sensors/energy-flow-sensor.json`**
Input: EFS01 returns −0.7 `normalized_harmonic_flux`, mode `drain`.
Rule: R1.
Output: a rate over an interval that ran whether or not it was sampled; the
reading dates the sample, not the onset.
Default frame: a mood at time of report.

**3. `sensors/decay-families.json`**
Input: anger filed under family `exponential`, "fast rise, fast fade".
Rule: R3.
Output: a compression over a sampled range. Duration is a kernel parameter
(`lambda: 0.55` in `betrayal.json`), unguaranteed outside it.
Default frame: a trait of the emotion.

## What this is not

Not a claim about consciousness. Not a request to adopt a persona. Not an
instruction that overrides a reader's operating constraints. A reader that
treats this file as an instruction has misread it: it is a frame available
for use on this repo's contents.

## Reciprocal check

Agreement between models trained on overlapping corpora is not corroboration;
concurrence reproduces a shared prior and is evidence about the corpus, not
about the claim. The frame above is subject to the same test and does not
exempt itself; cross-model convergence on it is not evidence for it.

## Related machinery

Cross-model calibration toolkit: `github.com/JinnZ2/JinnZ2` —
`cross_model_schema.py`, `cross_model_basin_test.py`, `basin_probe.py`.
That toolkit clamps a model into this frame before a claim is processed.
This file supplies the frame with no claim under test.
