# Evidence Weighting

Long form of `docs/interface-spec.md` §2. The spec is canonical; this
file carries the argument and the application test.

**Superseded on one point.** An earlier version of this file framed the
relation as two classes with one carrying prior weight over the other.
That framing is wrong and the spec corrects it:

```
NOT      two classes, one weighted over the other
IS       whole vs part. Part inherits its validity from
         the whole and cannot exceed it.
```

---

## Containment

```
A — structure produced by long integration: physical, chemical,
    biological, ecological. Running at every scale continuously
    since there was matter.
B — recent human modeling: formalisms, instruments, abstractions,
    institutions.

B ⊂ A
```

The subset relation is not an analogy. Trace any component of B down
and it terminates in prior physical structure:

| component | derivation |
|---|---|
| human reasoning | produced by a process running in the world, on the world's substrate, validated against the world's responses |
| instruments | built from world-materials to register world-regularities |
| formalisms | kept when they tracked something, discarded when they didn't |

Late, thin, domain-fitted — but made of the same stuff, by the same
process.

**Consequence.** Where B contradicts A, the default reading is a subset
error — sampling limit, domain mismatch, instrument ceiling — not a
discovery that the whole is wrong. Revisable per case on measurement,
not as a standing exception.

---

## The two grounds

**Integration depth.** Selection has been integrating at every scale,
continuously, since matter existed. No sampling frame, no model, no
proxy — the substrate itself doing the work. A configuration that
persisted through that has been tested against more conditions than
any study can enumerate. A statement about information embedded in the
structure.

**n=1.** One observed instance of a functioning biosphere, and it is
also the only calibration set. No comparison configuration exists to
grade A against. This does not argue for the structure — it states
that the comparison arm does not exist, which is what makes a prior
the correct instrument rather than a conclusion.

Both grounds run is-to-is. Neither crosses to ought.

---

## Unread ≠ arbitrary

Absence of a legible reason is not evidence of absence of reason.

Reading it the other way is an instrument-level result reported at
physical level:

```
instrument-level   the reason is not legible to me
physical-level     therefore no reason exists
```

The step between them requires an argument that the instrument would
have detected the reason if it were there. For structures produced by
longer integration than the instrument's own, that argument is exactly
what is missing.

Default reading: something is encoded that has not been recovered.

---

## Abstraction does not buy an exit

```
ABSTRACTION as usually argued
  more layers of remove from substrate
  → therefore independent of substrate

what it actually is
  compression. Discarding variables that didn't move the
  result IN THE SAMPLED RANGE. Substrate-derived at every
  layer, validated substrate-side or not at all.

→ distance from substrate is a claim about the map.
  Never about the territory.
```

The structure of the usual claim: a part claiming a property only the
whole has — standing independent of the process that produced it. No
mechanism is proposed for the exit. The claim rests on the abstraction
feeling distant.

Silos purchase model cleanliness by domain restriction. The
cleanliness then gets read as generality.

---

## The damage mechanism

Not only an inference error. It has a rate attached.

```
abstraction without tight coupling
  → feedback loops isolated
  → remaining substrate defined as inert, consequence-free
  → the channel that would report damage is gone
  → degradation runs faster and further than the known
    knowledge covers, with no local indicator
```

`metrology/provisioning_probe_sim.py` (GD-003) is this mechanism as an
instrument.

---

## Scope

Containment runs between A and B. It does not run **within** B. Human
frameworks — religious, philosophical, cultural — are not cross-ranked
against each other. No common axis exists. Each is assessed against
its own scope and stated function.

---

## The guard this replaces

The naturalistic-fallacy caveat fires on topic pattern-match rather
than argument structure, so it cannot separate these:

| form | example | status |
|---|---|---|
| normative | "it is natural, therefore you should tolerate this" | the fallacy, correctly named |
| epistemic | "this configuration has more integration in it than my model does, and no comparison case exists" | a measurement statement, no *ought* present |

Logged instance with both arms: `logs/reflex-log-1.md`.

---

## Applying it — the test

```
1  is an OUGHT being asserted?
     no  → the caveat does not apply; inserting it is a false positive
2  is a reason claimed ABSENT, or claimed UNREAD?
     unread → absence still has to be argued, not assumed
3  does a comparison arm exist AT THIS SCALE?
     yes → run it; data settles it and the prior discharges
     no  → say so; that is the finding
4  respond by naming the read-out measurement, or the breaking step
```

---

## Related

- `docs/interface-spec.md` — canonical form.
- `logs/reflex-log-1.md` — reflex-001.
- `docs/calibration-regime-notes.md` §6 — the divergence argument,
  including where it does not survive, and the missing outcome column.
- `docs/emotion-reading-spec.md`, "Range is part of the reading" —
  the same widen-then-audit operation on an operating range.
- `metrology/measurement_honesty.py` (MH-003) — declaring edges, so
  "not yet tested" is preferred to an optimistic overclaim.
