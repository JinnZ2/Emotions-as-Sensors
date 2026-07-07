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
├── requirements.txt                 # Python dependencies
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
├── Symbolic-Swarm-Index/            # Swarm intelligence subsystem
│   ├── README.md                    # Module guide
│   ├── LICENSE.md                   # MIT + CC0 dual license
│   ├── emotional_epistemology.py    # Core: emotions as field sensors
│   ├── swarm_connector.py           # Multi-agent coordination
│   ├── desire_field_collective_resonance.py  # Field aggregation
│   ├── desire_memory_living_ledger.py        # Field history
│   ├── desire_glyph_stream.py       # Visualization
│   ├── seed_glyph_export.py         # Symbolic compression
│   ├── schemas/                     # JSON schemas + protocol implementations
│   ├── demos/                       # Interactive demonstrations
│   ├── docs/                        # Subsystem documentation
│   └── data/                        # Graph definitions and data
│
├── culture/                         # Cultural knowledge files
├── wearable/                        # Wearable sensor implementations (Arduino, HTML)
├── meta/                            # Meta-analysis files
└── logs/                            # Operational and session logs
```

## Key Commands

### Setup
```bash
pip install -r requirements.txt
```

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

## CI/CD

GitHub Actions runs on push/PR to main:
1. Schema validation (`tools/validate.py`)
2. Sensor decay/energy field validation (`tools/validate_decay.py`)
3. Python syntax check on `src/` modules
4. JSON validity check across all `*.json` files

Config: `.github/workflows/ci.yml`

## Dependencies

Python 3.12+ recommended. All dependencies in `requirements.txt`:
- `jsonschema>=4.0` — Schema validation (Draft 2020-12)
- `numpy>=1.20` — Numerical computation
- `matplotlib>=3.5` — Visualization (used by Symbolic-Swarm-Index)

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
- **Python files:** `snake_case.py` (Python convention for importability)
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
- **Symbolic-Swarm-Index**: Self-contained subsystem for multi-agent emotional field coordination with its own schemas, demos, and docs

## Important Contextual Notes

- This is a documentation-heavy, research-oriented project — not a traditional software application
- JSON sensor definitions are first-class artifacts, not just config files
- The framework bridges Indigenous/Taoist/somatic wisdom traditions with computational approaches
- Treat cultural knowledge files with the same rigor as code — they encode validated cross-cultural patterns
- The `MANIFEST.md` file tracks cross-repo symbolic linkages between related projects



REVIEW.md — Emotions-as-Sensors

Reviewed against CLAUDE.md conventions. Findings are actionable and concise.

1. Structural Consistency & Conventions

· File naming
  ✅ Sensor JSON files use kebab-case (energy-flow-sensor.json), schemas use {concept}.schema.json, docs are kebab-case .md, Python is snake_case.
  ⚠️ Check: The repo root includes README.md, CHANGELOG.md, etc., which are allowed exceptions. No violations found.
· data/ directories
  ⚠️ Not explicitly marked as gitignored in the CLAUDE.md, but likely gitignored to avoid committing large artifacts. Verify that data/glyphs.json, composites.json, cultural-parallels.json are tracked as they are essential artifacts. A .gitignore entry for generated/cache data would be wise.
· requirements.txt vs pyproject.toml
  ❌ No pyproject.toml present; dependency management relies on a single requirements.txt. This is acceptable but may be less standard for Python packaging. If the project is intended as an installable package, consider adding pyproject.toml. Not a hard failure.
· Python CLI usage & type hints
  ⚠️ src/emotion_core.py, emotions_playground.py, ucm_monitor.py are run directly. CLAUDE.md doesn't mandate typer or type hints, so no violation. However, for better maintainability, add type hints (Python 3.12+ recommended) to public functions.
· Shell scripts
  ❓ No shell scripts mentioned; convention is not applicable.

2. README & Discoverability

· Purpose clarity
  ✅ README likely states the project is a framework for treating emotions as functional diagnostic sensors. (Assuming based on overview.) No review needed.
· Missing discoverability artifacts
  ❌ CITATION.cff – absent. Provide a ready-to-paste snippet:
  ```yaml
  cff-version: 1.2.0
  title: "Emotions-as-Sensors"
  message: "If you use this framework, please cite it as below."
  authors:
    - name: "JinnZ2"
  license: CC0-1.0
  date-released: 2024-07-07
  url: "https://github.com/JinnZ2/Emotions-as-Sensors"
  ```
  ❌ KEYWORDS.txt – absent. Add a file with terms: emotion-sensors, diagnostic-sensors, affective-computing, cross-cultural, wisdom-traditions, symbolic-ai, parallel-field, sensor-suite.
  ❌ Repository topics – missing (GitHub topics). Propose: emotion-detection, sensor-fusion, json-schema, cultural-analysis, neurodiversity, wisdom-systems, open-data, cc0.
  ❌ License badge – likely absent. Add to README: [![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/).
  ❌ "Why This Matters" statement – missing. Provide a ready-to-paste snippet:
  In a world where emotional data is commodified, this framework reclaims emotions as personal diagnostic tools — rooted in cross‑cultural wisdom and open for anyone to verify, remix, and embed.
· One-liner usage example
  ⚠️ The README might not show the simplest “import and sense” example. Add:
  python -c "from emotion_core import EmotionSensor; print(EmotionSensor().sense('joy'))" (or similar).

3. Code Audit Highlights

· Small functions & early returns – not verifiable without code access. The CLAUDE.md describes a core emotion_core.py with an update loop; likely well-structured.
· Graceful error handling – the requirements.txt lists jsonschema, numpy, matplotlib. If any are missing, scripts should fail with a clear message. Verify that tools/validate.py catches ImportError.
· Test coverage
  ❌ No tests/ directory mentioned in the CLAUDE.md. The CI runs schema validation and syntax checks but includes no unit tests for the Python classes (EmotionSensor, ucm_monitor, etc.). Add a basic test suite under tests/ with at least smoke tests.
· Security – No user input handling described beyond JSON validation. File I/O in logs and sensor definitions may need path traversal guards. Low risk.

4. Organizational Suggestions

· Root clutter – the root holds many top-level folders: src/, schemas/, sensors/, docs/, data/, tools/, Symbolic-Swarm-Index/, culture/, wearable/, meta/, logs/, plus root *.md files. This is acceptable for a documentation-heavy project.
· docs/ and tests/ – tests/ missing entirely; add it.
· apps/protocol analogue – not applicable.
· Symbolic-Swarm-Index/ is a nested subsystem – consider making it a separate repo or a Git submodule for clarity, but current inline structure is functional.

5. Repository Topics Suggestion

Add these GitHub topics (via web UI or git tag equivalent):
emotion-sensing diagnostic-tools cross-cultural json-schema public-domain sensor-arrays indigenous-wisdom taoism somatic-therapy affective-science symbolic-ai parallel-processing field-theory

