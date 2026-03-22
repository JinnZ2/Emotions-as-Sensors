# CLAUDE.md — Emotions-as-Sensors

## Project Overview

Emotions-as-Sensors is a framework that formalizes emotions as functional diagnostic sensors rather than affective states. It provides mathematical models, JSON sensor definitions, Python implementations, and extensive documentation for treating emotions as real-time intelligence systems that detect system health, authenticity, and alignment across human and AI contexts.

**License:** CC0 1.0 Universal (Public Domain)

## Repository Structure

```
├── README.md, CHANGELOG.md, CONTRIBUTING.md, LICENSE
├── MANIFEST.md                      # Cross-repo symbolic linkages
├── PROJECTS.md                      # Related ecosystem projects
├── .fieldlink.json                  # Cross-repo mount configuration
│
├── src/                             # Python source code
│   ├── emotion_core.py              # Core emotion sensor engine (EmotionSensor class)
│   ├── emotions_playground.py       # Interactive AI playground
│   ├── ucm_monitor.py               # Unified Consciousness Monitor
│   └── emotional_ai.py              # AI integration patterns
│
├── schemas/                         # JSON Schema definitions (Draft 2020-12)
│   ├── emotion.schema.json          # Core schema: atoms, composites, decay models
│   ├── elder-sensor.schema.json     # Elder Sensor Schema (validates sensor JSON)
│   ├── emotion_atom.schema.json     # Atomic emotion unit schema
│   ├── fieldlink.schema.json        # Cross-repo linking schema
│   └── multi_layer_sensor.template.json
│
├── sensors/                         # Emotion sensor definitions (JSON + docs)
│   ├── suite/comprehensive.json     # Full Parallel-Field Sensor Suite
│   ├── anger/, joy/, grief/, love/, trust/, interest/
│   ├── cognitive/, stability/, alignment/
│   ├── shapes/                      # Emotion shape definitions (e.g., relief.json)
│   ├── *.json                       # Individual emotion sensor files
│   ├── decay-families.json          # Decay family taxonomy
│   └── glyph-map.json              # Symbolic glyph mappings
│
├── docs/                            # All documentation
│   ├── equations.md                 # Complete mathematical formalization
│   ├── formalization.md             # Technical rigor
│   ├── energy-methodology.md        # Energy accounting system
│   ├── elder-sensor-framework.md    # Cultural bridge documentation
│   ├── glyph-web.md                 # Emotion family mapping
│   ├── probability-matrix.md        # Weighted decision-making
│   ├── glossary.md                  # Term definitions
│   ├── evolution-emotions.md        # Historical evolution
│   ├── emotional-cognition-ai.md    # AI integration theory
│   ├── emotions-as-resonance.md     # Resonance model
│   ├── convergent-wisdom.md         # Cross-cultural validation
│   ├── field-english.md             # Field-based language protocol
│   ├── field-english-protocol.md    # Language specification
│   └── ...                          # Additional topic docs
│
├── data/                            # Data definitions and datasets
│   ├── glyphs.json                  # Glyph families and symbols
│   ├── composites.json              # Composite emotion definitions
│   ├── cultural-parallels.json      # Cross-cultural validation data
│   ├── symbolic-archetypes.json     # Archetypal patterns
│   ├── examples/                    # Example data files
│   └── ...                          # Additional data files
│
├── tools/                           # Validation and utility scripts
│   ├── validate.py                  # Schema & composite validation
│   ├── validate_decay.py            # Decay/energy field validation
│   └── validate.example.py          # Validation examples
│
├── culture/                         # Cultural knowledge files
├── wearable/                        # Wearable sensor implementations (Arduino, HTML)
├── meta/                            # Meta-analysis files
├── logs/                            # Operational and session logs
└── Symbolic-Swarm-Index/            # Swarm intelligence subsystem
```

## Key Commands

### Validation
```bash
python tools/validate.py          # Validate schemas and composite data
python tools/validate_decay.py    # Check all sensor JSON files have decay & energy fields
```

### Running Implementations
```bash
python src/emotion_core.py        # Run core emotion sensor engine
python src/emotions_playground.py # Run interactive playground
python src/ucm_monitor.py         # Run consciousness monitor
```

## Dependencies

Python 3.7+ with:
- `jsonschema` — Schema validation (Draft 2020-12)
- `numpy` — Numerical computation
- Standard library: `json`, `math`, `random`, `pathlib`, `dataclasses`, `typing`, `enum`, `datetime`

No package manager config (no `requirements.txt` or `pyproject.toml`). Install manually:
```bash
pip install jsonschema numpy
```

## Development Conventions

### Adding New Emotions
1. Add new atoms only via `data/glyphs.json`
2. Add composites via `data/composites.json`
3. Run `python tools/validate.py` to validate
4. Individual sensor JSON files go in `sensors/` (either root or a family subdirectory)

### Emotion Sensor JSON Structure
Every sensor file follows this pattern:
```json
{
  "sensor": "unique-identifier",
  "function": "what it detects",
  "signal_type": "input type",
  "authentic_output": "healthy state",
  "corrupted_output": "distorted state",
  "information_provided": "what it tells us",
  "response_protocol": {
    "detect": "...",
    "assess": "...",
    "respond": "...",
    "release": "..."
  },
  "alignment_tag": "category",
  "sensor_group": ["group"],
  "resonance_links": ["linked-sensors"],
  "decay_model": "exponential|cyclical|resonant|immortal|transformative",
  "tags": ["metadata"]
}
```

All sensor JSON files must include `decay` and `energy` fields (enforced by `validate_decay.py`).

### Schema Conventions
- JSON Schema Draft 2020-12
- `additionalProperties: false` for strict validation
- Atom enum: `anger, shame, grief, abandonment, love, compassion, joy, admiration, fear, surprise, peace, contentment, longing, forgiveness, trust, excitement, despair`
- Decay models: `exponential, cyclical, resonant, immortal, transformative`
- Energy impacts: `adds, conserves, depletes`
- Composite temporal modes: `unresolved_persistence, acute, phasic`

### File Naming Conventions
- **All files:** lowercase kebab-case (e.g., `energy-flow-sensor.json`)
- **Exceptions:** README.md, LICENSE, CHANGELOG.md, CONTRIBUTING.md, CLAUDE.md, MANIFEST.md, PROJECTS.md
- **Sensor modules:** `{emotion-name}.json` in `sensors/` or `sensors/{family}/`
- **Schemas:** `{concept}.schema.json` in `schemas/`
- **Python files:** `snake_case.py` in `src/` (Python convention for importability)
- **Documentation:** `kebab-case.md` in `docs/`

### Core Mathematical Model
```
E(t) = SENSE -> PATTERN -> RESPOND + U(t)
```
The update loop (in `src/emotion_core.py`):
```
dE/dt = alpha * D(t) - lambda * K(E) + sum(w_j * E_j) + U(t)
```
Where `D` = drive signal, `K` = decay kernel, `w_j` = coupling weights, `U` = unknown field effects.

## Architecture Notes

- **Parallel-Field Architecture**: Multiple sensors operate simultaneously without collapsing plurality
- **DETECT-ASSESS-RESPOND-RELEASE**: The universal response protocol cycle
- **Cross-repo ecosystem**: Linked via `.fieldlink.json` to BioGrid 2.0, Rosetta-Shape-Core, and other repos (see `PROJECTS.md`)
- **Two distinct schemas**: `schemas/elder-sensor.schema.json` validates individual sensor files; `schemas/emotion.schema.json` defines atoms and composites
- **No CI/CD**: No automated pipelines; validation is manual via `tools/validate.py`
- **No linter/formatter config**: Python code follows standard conventions but is not enforced by tooling

## Important Contextual Notes

- This is a documentation-heavy, research-oriented project — not a traditional software application
- JSON sensor definitions are first-class artifacts, not just config files
- The framework bridges Indigenous/Taoist/somatic wisdom traditions with computational approaches
- Treat cultural knowledge files with the same rigor as code — they encode validated cross-cultural patterns
- The `MANIFEST.md` file tracks cross-repo symbolic linkages between related projects
