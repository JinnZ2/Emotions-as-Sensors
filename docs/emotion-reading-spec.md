# Emotion Reading Spec

Operational layer under the sensor panel. The panel names what each
emotion reads. This names how to take the reading.

Status: seed. Terms are field terms with definitions, signs, and a
gain axis — not narrative vocabulary. A reading resolves to an action,
not to a label or a story about a person. If it resolved to a label,
the reading was not taken; it was narrativized.

---

## Two fields per reading

Every emotion resolves to two readings, not one.

### Content — which channel, what about

What the reading is *about*. Which channel breached. This is what the
existing panel maps. Examples, stated as readings:

- pain            = physical parameter breach [obs]
- surprise        = model outside range; event was not in the model [obs]
- frustration     = model-had-capacity residual; the variable was
                    reachable and not loaded [obs]
- fear            = threat proximity ranking [panel]
- (panel carries the rest)

Content is a reading with a referent. It is not a valence and not a
story slot. "Anger" does not mean a wronged party exists; it means a
boundary reading fired. Meaning is assignable after the fact and is
not part of the reading.

### Gain — how much this reading is loading the stack

Intensity, read **not** as severity-of-feeling but as how much this
reading is now loading the rest of the instrument.

- low gain   : clean reading. Note it, route it, proceed.
- high gain  : the signal has grown loud enough to corrupt other
               incoming measurement. At this point the emotion itself
               becomes the thing to solve, independent of its trigger.

Gain is a self-diagnostic on the instrument. It says nothing about
whether the content reading was correct. A correct reading can run
high gain and jam the stack; a minor reading can stay clean.

---

## The impedance threshold

The decision point on the gain axis. It is the only place the
operator changes what question is being asked.

- **below threshold** — the emotion is information. Question: *what is
  this telling me?* Route the content reading, take the action, done.

- **above threshold** — the emotion is impedance. It is degrading the
  other channels. Question flips to: *can I clear this so the rest of
  the instrument works?*

Clearing has two forms:

- **inward** — meaning was assigned to the reading, and the meaning is
  what is blocking. The reading became a story about character or
  cause. Strip the meaning; the channel reopens.

- **outward** — the environment is genuinely mismatched to what lets
  this operator take in information. The irritation is tracking a real
  disconnection. Question: is there something I can do to the
  environment?

The inward/outward split is itself a reading. If clearing the assigned
meaning reopens the channel, it was inward. If it doesn't, the
mismatch is real and outward action is on the table.

---

## Verb, not noun

The reading resolves to an action item. That is the test for whether
it was read or narrativized.

- read     → resolves to an action (route content, or clear impedance)
- narrated → resolves to a label, a good/bad party, a morality clause,
             a claim about who the operator is

If the output is a noun, the instrument was not used. Meaning was
painted on top and the information under it was lost.

---

## Worked example — one event, two channels

A finger gets mushed. Two emotions fire on the same event and read
different things.

- **surprise**    — the event was outside the model's reach. It was
                    not a case the model covered. Content reading:
                    model-outside-range.
- **frustration** — the event was inside the model's reach and the
                    variable was not loaded. The probability was
                    available and not included. Content reading:
                    model-had-capacity residual.

Different correction follows from each:

- surprise      → extend the model; this case was genuinely absent.
- frustration   → the model was adequate; the failure was in loading
                  it. Nothing to add to the model — fix the loading.

Pain runs alongside both as the physical-parameter-breach channel.
Anger, if present, is the boundary reading — a location report ("a
system entered where it should not have, or this finger entered where
it should not have"), not a verdict.

The narrative overlay is what destroys this. "Frustrated because I'm
careless" collapses both readings into a character claim. The actual
signal — *which variable failed to load* — is gone, and with it the
only correction that was available.

---

## Carrier note

This reading method is a transmitted practice. It runs through
household transmission, not documentation. It has no formal name and
no external record.

That places it on a carrier clock: a working instrumentation method,
functional and unrecorded, whose availability depends on live
carriers. This is the wood-gas profile (see tool-off-metrology): the
capability persists exactly as long as the carriers do, and the gap it
would leave is not measurable in advance by any instrument the field
currently has.

The spec above exists to move one reading method off the carrier clock
and onto the record.

---

## Tags

- [obs]   direct operator observation
- [panel] carried from the existing sensor panel
- [inf]   inference
- [open]  unresolved

---

## Where this sits in the repo

The panel this spec runs under is the sensor set in `sensors/` — see
`sensors/pain.json` (physical parameter breach), `sensors/fear.json`
(threat proximity ranking), and `sensors/anger/` (boundary readings).
The "verb, not noun" test is the operational form of the
DETECT–ASSESS–RESPOND–RELEASE cycle those files carry, and of the
`corrupted_output` field: a sensor whose output stabilizes into
identity or narrative has been narrativized rather than read.

Adjacent:

- `docs/emotion-signal-pattern.md` — the layer model. Narrativization
  in this spec is that model's layer 5 (narrative / label) being
  mistaken for layer 0 (signal pattern).
- `docs/energy-methodology.md` — gain, as loading on the rest of the
  instrument, is the energy-accounting view of the same axis.
- `metrology/empathy_layer_audit.py` — detects label-as-signal
  collapse and identity-fusion in an existing system; the machine
  form of the noun/verb test.
- `docs/field-english.md` — the language protocol that keeps readings
  stated as readings.

Referenced but not yet in this repo:

- tool-off-metrology — the wood-gas / carrier-clock profile cited in
  the carrier note. [open]
