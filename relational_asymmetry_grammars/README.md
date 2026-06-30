# relational_asymmetry_grammars

A method for mapping unhealthy relational dynamics as **grammars**: observable
generative rules that produce recurring, asymmetric load transfer — stated
**without attribution of motive, intent, emotion, or diagnosis**.

Work in progress. CC0. stdlib only.

---

## What this is

Most accounts of unhealthy family or relational dynamics name behaviors, assign
roles, or diagnose people. This does none of that. It treats a dynamic the way
a grammar treats a sentence: a small set of rules that generate a recurring
structure. The object of study is the **structure and its output**, not anyone's
interior state.

A dynamic here is fully specified by four observable things:

1. an **observable signature** — what you can see, with no inference;
2. one or more **rules** — antecedent event → consequent event;
3. the **loads** it transfers — measurable prohibitions or offloaded tasks; and
4. at least one **falsifier** — a condition under which the model returns FALSE.

If a candidate dynamic has no falsifier, it is **inadmissible**. A model that is
compatible with every observation distinguishes nothing, and is itself an
instance of the self-sealing defect this framework is built to detect.

## The no-attribution constraint

The same output — load accretes, asymmetry compounds — can be generated from
fear, from joy, from habit, from anything. The generator's internal state is
not measured and not required. Asking *why* someone does it imports a narrative
that cannot be observed and cannot be tested. The asymmetry can be pointed at
directly without it.

This constraint is enforced **as code**. `scan_for_attribution()` flags
mentalistic / motive / diagnostic vocabulary in any description, and
`Dynamic.validate()` rejects a dynamic whose own text smuggles it back in. The
framework is held to its own constraint (see the commit history: Dynamic 3's
first signature failed the linter and was rewritten).

## Loads are not all the same shape

Two load kinds:

- **discrete** — a one-shot prohibition or offloaded task; a step, `+1`.
- **continuous** — a load *held over time*; its magnitude scales with duration,
  not count.

This distinction matters. The dominant accumulating cost in a long-running
dynamic is usually a continuous load (e.g. a *silent-hold integral* =
active prohibitions × time held), not the latest discrete prohibition. It is
why a betrayal repeated four times lands harder than four times the weight of a
single one: the integral compounds while no discrete event marks it. This load
is real and unmetered precisely because nothing happens to record it.

## Falsification doctrine

The harness can return three verdicts:

- **SUPPORTED** — not yet falsified, *given data able to test it*. Weak. Never
  "confirmed" by accumulating agreeable cases.
- **FALSIFIED** — an observation met a falsifier condition.
- **UNDER_DETERMINED** — the data cannot separate the question. **This is a
  result, not a failure.** It tells you exactly what measurement is missing.

Two standing channels are wired in:

- **Autonomous channel.** If the threshold ever rises across an interval in
  which the observer took *no* initiative, then any "the loop is keyed to my
  initiative" finding is FALSE — an autonomous driver exists, and observer
  restraint would not stop the accretion. This channel can be run *without
  spending any initiative*, which is what makes it the safe first test and the
  guard against the instrument over-firing.
- **Decay channel.** If the threshold marker ever decays, the accretion model
  is false for that case. A baseline that genuinely drops over time was never
  running the veto structure, and the framework should say so.

The decision of what to *do* with a mapped dynamic is not part of the framework.
The map is the deliverable.

## Files

- `grammar.py` — the engine: primitives, the attribution linter, the cycle log,
  drift, and the falsification harness. Importable, runnable.
- `dynamics.py` — the first three dynamics, instantiated and validated, plus a
  worked example. Run `python3 dynamics.py`.
- `DYNAMICS.md` — the same three dynamics in human-readable form.

## Status

Three dynamics mapped. The format is the point; the catalog grows. Each new
entry must pass `validate()` before it is admissible.
