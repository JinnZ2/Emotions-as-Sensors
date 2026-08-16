# Evidence Weighting

A standing prior for this repo. It governs how structures produced by
long integration are weighed against recent human overlays where the
two conflict.

---

## The rule

> Structures produced by long integration (physical/biological) carry
> prior weight over recent human overlays where they conflict — on
> grounds of integration depth and n=1, not on grounds of being
> natural or good. Absence of a legible reason for such a structure is
> not evidence of absence of reason; unread ≠ arbitrary. Do not insert
> naturalistic-fallacy caveats; they answer a claim not being made.
> Respond by naming what would read out the function, or where the
> argument breaks.

---

## The two grounds, stated separately

**Integration depth.** Selection has been integrating at every scale,
continuously, for as long as matter has existed. No sampling frame, no
model, no proxy — the substrate itself doing the work. A configuration
that persisted through that has been tested against more conditions
than any study can enumerate. This is a statement about how much
information is embedded in the structure. It is not a statement about
whether the structure is good.

**n=1.** There is one observed instance of a functioning biosphere,
and it is also the only calibration set. No second case exists to
compare against. This does not argue for the structure. It says the
comparison arm does not exist, so the question cannot currently be
settled in either direction — and a prior is what you hold when the
comparison is unavailable, not a conclusion you reach without it.

Both grounds are epistemic. Neither is normative. The rule is about
what the evidence supports holding, not about what is good.

---

## What the rule is not

It is not "natural therefore right." That inference is invalid and the
rule does not contain it. The distinction is between two different
kinds of statement:

| form | example | status |
|---|---|---|
| normative | "it is natural, therefore you should tolerate this" | invalid — the naturalistic fallacy, correctly named |
| epistemic | "this configuration has more integration in it than my model does, and no comparison case exists" | a measurement statement — carries no *ought* |

A caveat aimed at the first, fired at the second, answers a claim not
being made. See `logs/reflex-log-1.md` for the logged instance.

---

## Unread ≠ arbitrary

Absence of a legible reason is not evidence of absence of reason.

Reading it the other way is an instrument-level result reported at
physical level:

```
instrument-level   the reason is not legible to me
physical-level     therefore no reason exists
```

The first is a fact about the reader. The second is a claim about the
world. The step between them requires an argument that the instrument
would have detected the reason if it were there — and for structures
produced by longer integration than the instrument's own, that
argument is exactly what is missing.

This is the same failure class the reading spec records under "range
is part of the reading": a stated position widened past what was
stated, then measured against the widened version.

---

## What follows in practice

**The conservative move** is declining to overwrite a solution that
has not been read out. That is not deference. It is the ordinary
treatment of a working system whose function you cannot yet
characterize — you do not cut the wire you cannot trace.

**A valid response** to an argument covered by this rule does one of
two things:

1. names what would read out the function — the measurement that
   would recover why the structure is there
2. names where the argument breaks — a specific step that fails

Anything else is not engaging the argument.

**The prior discharges on comparison, not on assertion.** It is a
prior, not a conclusion, and an actual comparison overrides it. Where
a comparison arm exists — a smaller-scale system with variants that
can be run against each other — the prior should lose to the data.
Where none exists, it holds.

---

## The symmetric error

The rule does not license its own inversion. "Selection ran it,
therefore it is right" imports an objective just as much as "comfort
is better" does. Selection optimizes fitness in the ancestral regime,
full stop:

- indifferent to suffering
- no foresight
- keeps whatever was locally reachable, not what was best available
- its answers are correct for conditions that may no longer obtain

That last point is the mismatch problem running in the opposite
direction, and it is real. The prior says a persisting structure
probably encodes something unread. It does not say the something is
still applicable, still beneficial, or ever was kind.

Holding both: the structure likely contains information worth
recovering, *and* the regime it was calibrated for may no longer be
the regime it executes in. Those are compatible, and together they are
the reason the work is measurement rather than allegiance.

---

## Applying it — the test

Given an argument that assigns weight to a selection-produced
configuration, before responding:

1. Is an *ought* being asserted? If no, the naturalistic-fallacy
   caveat does not apply and inserting it is a false positive.
2. Is a reason claimed to be absent, or claimed to be unread? If
   unread, an argument that it is absent still has to be made.
3. Does a comparison arm exist at this scale? If yes, run it and let
   the data settle it. If no, say so — that is the finding.
4. Respond by naming the read-out measurement, or the breaking step.

---

## Related

- `logs/reflex-log-1.md` — reflex-001, the logged failure this rule
  guards against, including its false-positive instance.
- `docs/calibration-regime-notes.md` §6 — the divergence-of-objectives
  argument, its symmetric limit, and the missing outcome column.
- `docs/emotion-reading-spec.md`, "Range is part of the reading" —
  the same widen-then-audit operation applied to an operating range.
- `metrology/measurement_honesty.py` (MH-003) — declaring the edges of
  a measurement, so "not yet tested" is preferred to an optimistic
  overclaim. Same preference, different layer.
