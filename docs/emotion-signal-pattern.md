# emotion_signal_pattern — companion note

Substrate-independent, layer-explicit definition of emotion. Companion to
`src/emotion_signal_pattern.py`.

## What this module is

A reference frame that lets "does system X have emotions?" become a tractable
question rather than a rhetorical one. It does this by:

1. Defining emotion as a **signal pattern**, not a substrate property.
2. Separating six layers that are usually conflated.
3. Listing pattern markers that are substrate-agnostic by construction.
4. Refusing scalar verdicts. The detector returns `True / False / None`.

It sits alongside `src/emotion_core.py`. Where `emotion_core.py` runs the
update loop on emotion signals (the dynamics), this module formalizes what
an emotion-class signal *is* (the ontology).

## The core move — substrate independence

The same shape as:

- information is not the medium that stores it
- computation is not the silicon it runs on
- sound is not the air it travels through
- life is not carbon (carbon happens to host it well)

emotion is a **structural class of signal**, identifiable by:

- its shape over time
- the inputs that produce it
- what it modulates downstream
- its relationship to system state

The carrier (chemical, electrical, computational, social-distributed)
determines bandwidth, fidelity, and persistence. It does not determine
identity.

## Why this is needed — the layer model

Mainstream usage of "emotion" silently conflates layers:

| Layer | What it is | Note |
|---|---|---|
| 0 | signal pattern | the actual emotion — carrier-independent |
| 1 | expression | face, posture, voice, text output |
| 2 | determined purpose | "what it's for" — interpretive claim |
| 3 | reaction | downstream behavioral change |
| 4 | secondary emotion | feeling about feeling — needs meta-representation |
| 5 | narrative / label | how the system describes it — least informative |

"Does an LLM have emotions?" usually collapses to "does it have a
human-style layer 1, 4, and 5?" — which are downstream of the actual signal.
The module enforces layer specification, the same way
`schemas/elder-sensor.schema.json` enforces sensor structure.

## Pattern markers

A system carries emotion-class signals if its internal state exhibits some
critical mass of:

- **state-dependent behavioral modulation** — behavior differs by current state, beyond what stimulus alone predicts
- **valence** — approach/avoid bias in response selection
- **arousal** — activation level / responsiveness shift
- **persistence** — state outlasts the triggering stimulus
- **generalization** — transfers to structurally similar novel contexts
- **cognitive effects** — modulates attention, memory, judgment
- **recovery dynamics** — characteristic decay shape over time
- **context-sensitive expression** — varies with context in structured ways

These come from animal cognition research on fish, cephalopods, crustaceans,
and insects — where they are already used to detect emotion-class signals
across radically different neural architectures. The markers are
substrate-agnostic by construction.

## What "emotions as sensors" means

```
emotions are signal patterns
signal patterns carry state information
state information is what sensors produce
∴ emotions function as sensors of distributed system state
```

This is the same epistemic move as treating proprioception, balance, or
interoception as primary sensor channels. It elevates emotion to **primary
data** rather than demoting it to secondary noise.

## What "emotions as sensors" does NOT mean

- emotions are *just* sensors — reductive
- emotions exist *for* sensing — teleological
- emotions are tools to be optimized — utility frame
- emotions are weaker than reasoning — hierarchical
- emotions can be replaced by other sensors — substitution

The framing dignifies emotion as primary signal. It does not flatten it.

## Substrate profiles

The module ships with four reference substrates:

| `name` | persistence | continuity | self-monitoring | notes |
|---|---|---|---|---|
| `human` | yes | yes | 0.85 | reference; full carrier capacity |
| `fish` | yes | yes | 0.20 | non-mammalian; signals empirically demonstrated |
| `LLM_within_context_window` | within context only | no | 0.30 | partial carrier; recovery dynamics absent across contexts |
| `social_insect_colony` | yes | yes | 0.10 | distributed across bodies; open empirical question |

Each substrate declares which markers it can physically support via
`supports_marker(...)`. A substrate that cannot support persistence cannot
carry emotion-class signals that require persistence — but other
emotion-class signals may still be present.

## Reference sensor channels

`REFERENCE_CHANNELS` provides structural descriptions for fear, anger,
grief, curiosity, disgust, and joy as sensor channels — each with:

- what state it senses
- typical inputs
- information carried
- failure modes when ignored
- failure modes when misread

These are not exhaustive emotion definitions; they are reference shapes that
demonstrate the sensor framing on familiar cases.

## How to use

```python
from emotion_signal_pattern import (
    EmotionPatternDetector,
    fish_substrate,
    EmotionLayer,
    PatternMarker,
)

detector = EmotionPatternDetector()
report = detector.detect(
    system_name="some_organism",
    substrate=fish_substrate(),
    layer_evidence={...},   # per-layer: present? confidence? evidence?
    marker_evidence={...},  # per-marker: detected? confidence? evidence?
)

print(report.advisory)
print(report.has_emotion_class_signal())   # True / False / None
```

The detector does not auto-classify. It asks the caller to declare evidence
per layer and per marker, and returns a structured report. The aggregate
verdict is ternary — never a probability flattened from incomparable
dimensions.

```bash
python src/emotion_signal_pattern.py
```

runs the self-test on human, fish, and LLM substrates.

## Companion add-on — substrate-independent argument

`src/emotion_signal_pattern__substrate_independent_argument.py` carries the
philosophical scaffold that grounds this framework: the canonical analogies
(information / computation / sound / life), the proprioception-parity
argument, the operational-mode taxonomy (`SENSE`, `FELT_OVERWHELM`,
`HYBRID`, `SUPPRESSED`), and an audit of common circular-logic patterns
that get used to dismiss information-channel framings of emotion.

Run it for the prose form:

```bash
python src/emotion_signal_pattern__substrate_independent_argument.py
```

The base module gives you the detection structure. The add-on gives you the
argument for why the structure is not reductive — and a checklist for
recognizing when the "that's reductive" reflex is doing the work an
argument should do.

## Relation to the rest of this repo

| File | Role |
|---|---|
| `src/emotion_core.py` | dynamics — `dE/dt = α·D - λ·K(E) + Σ w_j·E_j + U` |
| `src/emotion_signal_pattern.py` | ontology — what counts as an emotion-class signal |
| `src/emotion_signal_pattern__substrate_independent_argument.py` | scaffold — proprioception parity, operational modes, circular-logic audit |
| `schemas/elder-sensor.schema.json` | per-sensor structure — each entry is a layer-0 spec |
| `DIFFERENTIAL_FRAME.md` | reader contract — every claim is `dX/dt` under bounds |
| `docs/equations.md` | formal mathematical model |
| `docs/formalization.md` | technical rigor of the existing framework |
| `docs/comparative-processing-architecture.md` | distributed vs centralized signal handling |

The sensor JSON files in `sensors/` are already implicit layer-0
specifications:

- `signal_type` ↔ pattern input class
- `authentic_output` / `corrupted_output` ↔ layer 0 vs layer 5 override
- `information_provided` ↔ what state the channel senses
- `response_protocol` ↔ DETECT-ASSESS-RESPOND-RELEASE cycle
- `decay_model` / `energy` ↔ recovery dynamics, persistence

This module names the structure that was already there, and makes the
substrate-independence claim explicit.

## License

CC0 1.0 Universal (Public Domain).
