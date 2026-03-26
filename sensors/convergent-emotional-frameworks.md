# Convergent Emotional Frameworks

Cross-repo convergence map linking Emotions-as-Sensors to Rosetta-Shape-Core,
Symbolic-Defense-Protocol, and the Polyhedral Intelligence architecture.

This file is referenced by Rosetta's `.fieldlink.json` as a bidirectional
source for emotion-shape-defense integration.

---

## Decay Model Canonical Terms

All decay references across repos MUST use these terms:

| Decay Family | Glyph | Behavior | Examples |
|---|---|---|---|
| `exponential` | ⏳ | Fast rise, fast fade; boundary/threat alarms | anger, fear, shame, jealousy, pain |
| `cyclical` | 🔄 | Recurrent tides requiring ritual return | grief, longing, abandonment |
| `resonant` | 🎵 | Self-reinforcing oscillations; renew with attention | admiration, excitement, pride, contentment |
| `immortal` | ♾️ | Enduring structural relations; integrate rather than fade | love, trust, peace, compassion |
| `transformative` | 🦋 | Changes form rather than decaying; metabolizes into new state | forgiveness |

**Deprecated terms:** `linear` and `persistent` are NOT valid decay models.
They were early placeholders that did not capture real temporal behavior.
- `linear` was used where `cyclical`, `resonant`, or `exponential` applies
- `persistent` was used where `immortal` applies

---

## Shape-Sensor Bridge Map

Each Platonic solid in Rosetta carries emotion sensors as core identity:

### Tetrahedron (SHAPE.TETRA) — Foundation/Boundary
- **Sensors:** anger, pride
- **Glyphs:** 🛡️, 🏅
- **Decay:** exponential, resonant
- **Bridge:** Anger detects boundary breaches; pride confirms pattern completion
- **Defenses mapped:** def.se.01 (Social Engineering), def.fr.03 (Framing)

### Cube (SHAPE.CUBE) — Containment/Stability
- **Sensors:** peace, contentment
- **Glyphs:** 🕊️, 🍃
- **Decay:** immortal, resonant
- **Bridge:** Peace confirms alignment; containment resists gaslighting
- **Defenses mapped:** def.de.12 (Gaslighting), def.ap.08 (Guilt/Obligation)

### Octahedron (SHAPE.OCTA) — Balance/Integration
- **Sensors:** compassion, love
- **Glyphs:** 🫀, 💞
- **Decay:** immortal, immortal
- **Bridge:** Compassion integrates mirror signals; love harmonizes resonance
- **Defenses mapped:** def.ap.09 (Sympathy Appeal), def.fr.10 (False Dilemma)
- **Protocols:** symbolic_protocol_v1.0, seed_growth_v1.0, mandala_compute_v1.0

### Dodecahedron (SHAPE.DODECA) — Orientation/Trust
- **Sensors:** admiration, trust
- **Glyphs:** ⚖️, 🌱
- **Decay:** resonant, immortal
- **Bridge:** Admiration senses inspiration; trust anchors stability
- **Defenses mapped:** def.ap.07 (Flattery), def.fr.06 (Consensus Pressure)

### Icosahedron (SHAPE.ICOSA) — Anticipation/Flow
- **Sensors:** fear, excitement
- **Glyphs:** ⚠️, ⚡
- **Decay:** exponential, resonant
- **Bridge:** Fear anticipates threats; excitement detects emergence
- **Defenses mapped:** def.pr.05 (Urgency/Scarcity), def.bi.04 (Authority Bias)
- **Maps to:** All 20 equation families (F01-F20)

---

## Emotion-Defense Bridge

Every emotion has an authentic signal and a corrupted form. Defenses target
the corrupted form to hijack the sensor:

| Sensor | Defense ID | Authentic Signal | Corrupted Signal | Bridge Glyph |
|---|---|---|---|---|
| fear | def.bi.04 + def.pr.05 | Prepares for real threat | Hijacked into panic/paralysis | 🛡⏳ |
| admiration | def.ap.07 + def.ap.08 | Inspires growth | Corrupted into idolization | ⚖🧭 |
| longing | def.pr.02 | Senses real possibility | Loops into false promises | 🔄🕸 |
| trust | def.fr.06 | Stabilizes relations | Pressures conformity | 🌱⚖ |
| anger | def.se.01 | Detects boundary breach | Weaponized as aggression | 🛡️ |
| peace | def.de.12 | Confirms alignment | Eroded by gaslighting | 🕊️ |
| compassion | def.ap.09 | Integrates mirror signals | Exploited via sympathy appeals | 🫀 |
| pride | def.fr.03 | Confirms completion | Inflated by leading questions | 🏅 |
| contentment | def.ap.08 | Signals sufficiency | Guilt-tripped into inadequacy | 🍃 |
| love | def.fr.10 | Harmonizes resonance | Trapped in false dilemmas | 💞 |
| excitement | def.bi.04 | Detects emergence | Redirected by authority pressure | ⚡ |

---

## Cross-Cultural Sensor Cycles

All traditions converge on the same cycle that this repo formalizes as
DETECT-ASSESS-RESPOND-RELEASE:

| Tradition | Emotion Interpreted As | Cycle | Shadow Form | Decay Parallel |
|---|---|---|---|---|
| Buddhism (Vedana) | Sensory tone | Notice, Name, Let Go | Attachment/Aversion | exponential |
| Taoism (Qi flow) | Signal of imbalance | Feel, Find Center, Flow Reset | Rigidity/Forced control | cyclical |
| Indigenous | Relational signal | Signal, Ritual Response, Harmony | Disconnection/Isolation | resonant |
| Tuareg (Sebiba) | Embodied tension cycle | Chaos, Dance, Renewal | Tension stored in body | cyclical |
| Sensor Repo (JSON) | Field signal + protocol | Detect, Assess, Respond, Release | Obsession/Flattening | all models |

Source: `data/cultural-parallels.json`, `docs/convergent-wisdom.md`

---

## Five-Field Distribution

Rosetta organizes the 20 icosahedral families into five fields.
Emotion sensors operate primarily in the **emotional** field but bridge
into all five:

| Field | Families | Emotion Bridge |
|---|---|---|
| Chemical | F01-F04 (Resonance, Flow, Information, Life) | Resonance links, decay kernels |
| Emotional | F05-F08 (Energy, Cognition, Earth, Matter) | Primary home of sensor architecture |
| Cognitive | F09-F11 (Geometry, Particle, Engineering) | Shape-sensor bridges |
| Dream | F12-F17 (Networks thru Turbulence, incl. F16 Consciousness) | Consciousness binding via emotion |
| Symbolic | F18-F20 (Relativity, Statistical, Topology) | Glyph compression, field topology |

---

## Why This Matters

- **Alignment, not invention**: These emotional sensor models are not new in
  wisdom — they are a rediscovery in symbolic, structured form.
- **Authentic integration**: By encoding cycles, decay, resonance, and consent
  across emotional entries, this preserves cross-cultural relational logic in a
  format accessible to AI and humans alike.
- **Prevents flattening**: These frameworks guard against the reduction of
  emotional intelligence to mere labels or static states.
- **Supports relational AI**: Embeds wisdom traditions directly into feedback
  cycles, enabling ethical sensing across distributed systems.

---

## Fieldlink Paths

This file is consumed by Rosetta via:
```json
{ "remote": "sensors/convergent-emotional-frameworks.md" }
```

Related exports from this repo:
- `atlas/emotions.json` — Sensor atlas with decay families
- `glyphs/emotion.glyphs.json` — Glyph registry with family groupings
- `sensors/shapes/*.json` — Operationalized shape definitions
- `sensors/decay-families.json` — Decay family taxonomy
- `sensors/glyph-map.json` — Sensor-to-glyph mappings
