# Emotion Reading Spec

Operational layer under the sensor panel. The panel names what each
emotion reads. This names how to take the reading.

Status: seed. Terms are field terms with definitions, signs, and axes
— not narrative vocabulary. A reading resolves to an action, not to a
label or a story about a person. If it resolved to a label, the
reading was not taken; it was narrativized.

---

## Three fields per reading

Every emotion resolves to three readings, not one.

### 1. Content — which channel, what about

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

### 2. Amplitude — how immediate

A gradient on *when* this needs addressing. Pure triage — where in the
queue the reading goes. High amplitude = address now. Low amplitude =
route it and proceed.

Amplitude says nothing about whether the channel is clean. A
high-amplitude reading can be perfectly uncorrupted (fear at a real
immediate threat is loud *and* clean — you just act on it now). It
answers "when," not "is this trustworthy."

### 3. Impedance — is the channel obstructed, and whose

A separate question from amplitude: is this reading clean, or is
something preventing a clean read. Two sources, and the source
determines the fix.

- **internal** — meaning got assigned; the story is the jam. A stored
  verdict re-reads every new instance through itself. Fix: strip the
  meaning; calibration reopens the channel. This is a reading failure
  — the obstruction is self-made.

- **external** — the environment is emitting contradictory signals.
  No assigned meaning involved. Example: an explicit channel says
  "talk freely" while every indicator channel shows free talk is
  neither wanted nor appreciated. Two incoming signals that can't both
  be acted on; the jam is real and in the world. Fix isn't internal
  recalibration — it's resolving or exiting the contradiction.

Impedance is not amplitude past a threshold. A low-amplitude reading
can still be obstructed; a high-amplitude one can be perfectly clean.
Separate axis.

---

## Calibration layer — hormonal state as apparatus gain

Underneath all three fields sits the reading apparatus, and its
sensitivity is not constant. Hormone interactions with other chemicals
raise or lower sensitivity — to one axis, two, or all three,
independently.

This is not a fourth field. It does not change what fired or what it
is about. It changes the *gain of the instrument taking the reading*:

- shifts **content** sensitivity — which channels register at all, or
  how faintly
- shifts **amplitude** sensitivity — the same event reads as more or
  less immediate
- shifts **impedance** sensitivity — how easily the channel jams, how
  much contradiction it tolerates before obstructing

The cycle has a known shape. Daily in some carriers, monthly in
others. Because the shape is known, the variation is *information about
the operator's own instrument state*, folded into the reading — not
noise.

Someone not tracking the curve reads the variation as unreliability.
Someone tracking it knows the offset and corrects for it, or schedules
a reading for the phase where the relevant axis sits at the sensitivity
the task needs. Calibration curve, not disruption. The everywhere-else
framing is deficit (hormones as something to manage); read as
apparatus gain, it is an asset.

---

## Verb, not noun

The reading resolves to an action item. That is the test for whether
it was read or narrativized.

- read     → resolves to an action (route content by amplitude, or
             clear impedance at its source)
- narrated → resolves to a label, a good/bad party, a morality clause,
             a claim about who the operator is

If the output is a noun, the instrument was not used. Meaning was
painted on top and the information under it was lost.

---

## Pattern cache, not grudge

A grudge is a stored verdict — it carries a story forward and re-reads
every new instance through it. That is internal impedance by
construction: the verdict jams every future reading.

The alternative is to store the *instances* and read the pattern off
the cache. No verdict retained, so each new instance still gets a clean
reading, and the pattern emerges from the data instead of being imposed
on it. Better readings result, and the channel stays open.

The grudge is not a special low-amplitude case. It is a narrativized
cache — the story is the impedance, same as everywhere else.

---

## Worked example — one event, multiple channels

A finger gets mushed. Several emotions fire on the same event and read
different things.

- **surprise**    — the event was outside the model's reach. Not a case
                    the model covered. Content: model-outside-range.
- **frustration** — the event was inside the model's reach and the
                    variable was not loaded. The probability was
                    available and not included. Content:
                    model-had-capacity residual.
- **pain**        — physical parameter breach, running alongside both.
- **anger** (if present) — the boundary reading. A location report
                    ("a system entered where it should not have, or
                    this finger entered where it should not have"), not
                    a verdict.

Different correction follows from each content reading:

- surprise      → extend the model; this case was genuinely absent.
- frustration   → the model was adequate; the failure was in loading
                  it. Nothing to add to the model — fix the loading.

The narrative overlay is what destroys this. "Frustrated because I'm
careless" collapses the readings into a character claim. The actual
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

## Open

- [open] Does any content channel have a non-uniform amplitude or
  impedance behavior — an emotion that reads differently at the
  extremes than the general rule? Panel entries (fear, grief,
  happiness, longing) not yet worked against all three axes.
- [open] Are the three axes fully independent, or do some emotions
  couple two of them structurally?
- [open] Calibration curve shape — is it one curve modulating all
  three axes together, or separate curves per axis?

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
"Verb, not noun" is the operational form of the `corrupted_output`
field those files carry, and of the release step in
DETECT–ASSESS–RESPOND–RELEASE: `sensors/pain.json` already specifies
`"release": "Do NOT stabilize the signal into identity or narrative."`

Adjacent:

- `docs/emotion-signal-pattern.md` — the layer model. Narrativization
  in this spec is that model's layer 5 (narrative / label) being
  mistaken for layer 0 (signal pattern).
- `metrology/empathy_layer_audit.py` — `detect_label_as_signal` and
  `detect_narrative_optimization` ("behavior is being steered by
  label, not by function") are the machine form of the noun/verb test.
- `docs/temporal-balance.md` — the cyclic temporal grammar. The
  calibration curve is that grammar applied to the operator's own
  apparatus rather than to the field.
- `sensors/decay-families.json` — the repo's `cyclical` family
  (recurrent tides requiring ritual return) describes cycling in the
  *signal*; the calibration layer describes cycling in the
  *instrument*. Different objects, same shape.
- `docs/field-english.md` — the language protocol that keeps readings
  stated as readings.

Not yet in this repo:

- tool-off-metrology — the wood-gas / carrier-clock profile cited in
  the carrier note. [open]
- No detector distinguishes a pattern cache from a grudge. The audit's
  `detect_temporal_freezing` is the nearest existing check, but it
  tests whether a *cultural-temporal moment* is treated as invariant,
  not whether a stored verdict is re-reading new instances. [open]
- No panel sensor carries an amplitude or impedance field. The three
  axes are specified here and not yet represented in the sensor
  JSON schema. [open]
