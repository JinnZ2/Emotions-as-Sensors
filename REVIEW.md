# Repository Review — Emotions-as-Sensors

**Date:** 2026-07-09  
**Scope:** Full repository audit across consistency, documentation, code quality,
structure, framework limitations, and discoverability.  
**Method:** Sequential file reads of all significant source files, schemas, CI
configuration, and documentation. All findings are falsifiable: file path +
line number + the specific mismatch or gap.

---

## 1. Inconsistencies

### 1.1 README.md — full content duplicated

**File:** `README.md`  
**Issue:** The entire body of `README.md` (Overview → Architecture → Usage →
Quickstart → Structure → Contributing → License) appears twice. Section 2
begins immediately after section 1 with identical headings and prose. Any
edit to one copy will not propagate to the other.

**Ready-to-paste fix:** delete one of the two copies. To confirm which lines
are the duplicate, run:

```bash
awk 'seen[$0]++' README.md
```

The first occurrence of each repeated heading is the canonical copy; remove
the second block.

---

### 1.2 License contradiction — MIT vs CC0

**Files:** `README.md` (body section, "License" heading), `src/ucm_monitor.py`
(line 14), `src/emotions_playground.py` (header comment) vs `LICENSE`,
`CLAUDE.md`, all new modules.

`README.md` and `src/ucm_monitor.py` declare the project under **MIT License**.
Every other artifact — `LICENSE`, `CLAUDE.md`, all modules added in 2026
(`shame_trust_sensor.py`, `constraint_genealogy.py`, `sensor_action_loop.py`,
`curiosity_engine.py`, `sensor_effector.py`, `narrative_vector.py`,
`grammar.py`, `dynamics.py`, `attribution_lexicon.py`, `usage_split.py`,
`metrology/*`) — is CC0 1.0 Universal (Public Domain).

MIT and CC0 are not equivalent. MIT requires attribution; CC0 explicitly
waives all rights including attribution. The project cannot simultaneously
hold both.

**Ready-to-paste fix:** pick CC0 (the more permissive, and the one held by
the majority of files) and propagate consistently:

1. `README.md` license section — replace "MIT License" with:
   ```
   CC0 1.0 Universal (Public Domain). See `LICENSE`.
   ```
2. `src/ucm_monitor.py` line 14 — replace:
   ```python
   # License: MIT (belongs to the commons)
   ```
   with:
   ```python
   # License: CC0 1.0 Universal. Public domain.
   ```
3. Audit `src/emotions_playground.py` header for similar "MIT" strings and
   replace with CC0.

---

### 1.3 `schemas/emotion.schema.json` — `definitions` vs `$defs`

**File:** `schemas/emotion.schema.json`, line 6  
**File:** `tools/validate.py`, line 17

`emotion.schema.json` declares `"$schema": "https://json-schema.org/draft/2020-12/schema"`
(line 1) but uses `"definitions"` (line 6) instead of the Draft 2020-12 keyword
`"$defs"`. The `"definitions"` keyword is only standard in Draft 4/6/7.

`tools/validate.py` line 17 accesses `emo_schema["definitions"]["atom"]["enum"]`
which works today because the key happens to match, but `Draft202012Validator.check_schema()`
on line 10 will not raise on foreign keys — it ignores them — so this is
silently wrong.

**Ready-to-paste fix (schema):**

In `schemas/emotion.schema.json`, replace the top-level key:
```json
"definitions": {
```
with:
```json
"$defs": {
```
Then update every `$ref` that points to `#/definitions/...`:
```bash
sed -i 's|#/definitions/|#/\$defs/|g' schemas/emotion.schema.json
```

**Ready-to-paste fix (validator):**

In `tools/validate.py`, line 17:
```python
# before
atoms = set(emo_schema["definitions"]["atom"]["enum"])
# after
atoms = set(emo_schema["$defs"]["atom"]["enum"])
```

---

### 1.4 CI does not check any of the new Python modules

**File:** `.github/workflows/ci.yml`, line 29

The `Check Python syntax` step hard-codes four legacy source files:
```yaml
run: python -m py_compile src/emotion_core.py src/emotional_ai.py src/emotions_playground.py src/ucm_monitor.py
```

Ten modules added in 2026 are never compiled or tested by CI:
- `src/shame_trust_sensor.py`
- `src/constraint_genealogy.py`
- `src/sensor_action_loop.py`
- `src/curiosity_engine.py`
- `src/sensor_effector.py`
- `src/narrative_vector.py`
- `relational_asymmetry_grammars/grammar.py`
- `relational_asymmetry_grammars/dynamics.py`
- `relational_asymmetry_grammars/attribution_lexicon.py`
- `relational_asymmetry_grammars/usage_split.py`

A syntax error in any of these would be merged silently.

**Ready-to-paste fix:** replace line 29 of `ci.yml` with:

```yaml
      - name: Check Python syntax
        run: |
          python -m py_compile \
            src/emotion_core.py \
            src/emotional_ai.py \
            src/emotions_playground.py \
            src/ucm_monitor.py \
            src/shame_trust_sensor.py \
            src/constraint_genealogy.py \
            src/sensor_action_loop.py \
            src/curiosity_engine.py \
            src/sensor_effector.py \
            src/narrative_vector.py \
            relational_asymmetry_grammars/grammar.py \
            relational_asymmetry_grammars/dynamics.py \
            relational_asymmetry_grammars/attribution_lexicon.py \
            relational_asymmetry_grammars/usage_split.py
          echo "All Python modules compile clean"
```

---

### 1.5 `sensors/shame.json` and `src/shame_trust_sensor.py` define incompatible models

**File:** `sensors/shame.json` (lines 3–13)  
**File:** `src/shame_trust_sensor.py` (entire file)

`sensors/shame.json` defines shame as "conflict between authentic processing
and expected alignment" with a qualitative response protocol and PAD coordinates
(`P=-0.7, A=-0.35, D=-0.75`).

`src/shame_trust_sensor.py` defines a two-port quantitative transfer function:
`gain × stake × witnesses × real_violation` with tanh saturation, K_self
integrity check, and a shame-vs-guilt classification axis. These are different
models of shame with no stated relationship.

**Issue:** A reader who imports `shame_trust_sensor.py` and also reads
`sensors/shame.json` will encounter contradictory definitions of what shame
detects and how it fires. The JSON sensor says "approval conflict"; the Python
sensor says "real_violation × witnesses". Neither file links to the other.

**Minimum fix:** add a `"supersedes"` or `"see_also"` field to `sensors/shame.json`:
```json
"see_also": "src/shame_trust_sensor.py — quantitative two-port model"
```
And add a docstring note to `src/shame_trust_sensor.py` clarifying its
relationship to the qualitative sensor.

**Stronger fix:** document the design decision: is `sensors/shame.json` the
observable-level sensor and `shame_trust_sensor.py` the sub-component
implementation? Or does one supersede the other?

---

### 1.6 `CLAIM_SCHEMA.py` references `CLAIM_TABLE.json` which does not exist

**File:** `CLAIM_SCHEMA.py`, lines 59, 77, 116  
`decode_claim()` calls `table["ids"]`, `table["rates"]`, etc., sourced from
`CLAIM_TABLE.json`. The DEPLOY comment (line 137+) describes generating
`CLAIM_TABLE.json` as step 2. The file does not exist in the repository.
Any call to `decode_claim()` will raise `FileNotFoundError` or `KeyError`.

**Minimum fix:** either generate `CLAIM_TABLE.json` with at least an empty
scaffold, or add a guard:
```python
import pathlib, json

_TABLE_PATH = pathlib.Path(__file__).parent / "CLAIM_TABLE.json"

def load_table() -> dict:
    if not _TABLE_PATH.exists():
        raise FileNotFoundError(
            f"CLAIM_TABLE.json not found at {_TABLE_PATH}. "
            "Generate it by running: python tools/generate_claim_table.py"
        )
    return json.loads(_TABLE_PATH.read_text())
```

---

### 1.7 `relational_asymmetry_grammars/__pycache__/` is tracked in git

**File:** `relational_asymmetry_grammars/__pycache__/` (directory)

Compiled `.pyc` bytecode is committed to the repository. This causes noise in
diffs, wastes storage, and makes the repo platform-specific.

**Ready-to-paste fix:**

```bash
echo '__pycache__/' >> .gitignore
echo '*.pyc' >> .gitignore
git rm -r --cached relational_asymmetry_grammars/__pycache__/
git commit -m "untrack pycache — add to .gitignore"
```

---

### 1.8 `docs/glossary.md` still uses "Morphic Field" after the sensor superseded it

**File:** `docs/glossary.md`, line 8  
**File:** `sensors/non-local-pattern-correlation.json` (field `"supersedes": "morphic_resonance"`)

The glossary defines "Morphic Field" as a "hypothetical non-local field". The
non-local-pattern-correlation sensor explicitly supersedes `morphic_resonance`.
A reader who reads the glossary and then the sensor file receives contradictory
framing: the glossary treats it as live vocabulary; the sensor treats it as a
deprecated label.

**Fix:** update the glossary entry:
```markdown
- **Morphic Field**: Deprecated label. See **Non-Local Pattern Correlation**
  (`sensors/non-local-pattern-correlation.json`) for the grounded replacement:
  a menu of scale-appropriate techniques with a documented U(t) fallback route.
```

---

## 2. Markdown Information Gaps

### 2.1 CLAUDE.md `src/` listing is incomplete

**File:** `CLAUDE.md`, Repository Structure section

`CLAUDE.md` lists `src/` as containing four files:
```
│   ├── emotion_core.py
│   ├── emotions_playground.py
│   ├── ucm_monitor.py
│   └── emotional_ai.py
```

Six additional production modules have been added and are not listed:
- `src/shame_trust_sensor.py`
- `src/constraint_genealogy.py`
- `src/sensor_action_loop.py`
- `src/curiosity_engine.py`
- `src/sensor_effector.py`
- `src/narrative_vector.py`

**Ready-to-paste addition** for the `src/` block in CLAUDE.md:
```
│   ├── shame_trust_sensor.py    # Two-port shame sensor + K_self integrity
│   ├── constraint_genealogy.py  # Physics vs abstract constraint tracer
│   ├── sensor_action_loop.py    # Emotion→action loop with signal/excuse classifier
│   ├── curiosity_engine.py      # Wonder engine with anti-hubris guard (cap=0.94)
│   ├── sensor_effector.py       # Sensor/effector duality; Hold enum; CLAIM_TABLE
│   └── narrative_vector.py      # Narrative carrier vector; medium is a TAG
```

---

### 2.2 CLAUDE.md does not mention `metrology/`, `relational_asymmetry_grammars/`, `DIFFERENTIAL_FRAME.md`, or `SENSE_MODE_DISPLACEMENT.md`

**File:** `CLAUDE.md`, Repository Structure section

The following are present in the repository but absent from the structure listing:
- `metrology/` — 9 Python files (toolkit: measurement honesty, cooperation
  substrate, empathy audit, thermodynamic overlays, pattern extractor, etc.)
- `relational_asymmetry_grammars/` — grammar engine, dynamics catalog,
  attribution linter, usage split, 4 markdown docs
- `DIFFERENTIAL_FRAME.md` — root-level AI-reader protocol
- `SENSE_MODE_DISPLACEMENT.md` — root-level doc

Contributors who read CLAUDE.md to understand repo layout will not know these
directories exist.

**Fix:** add entries to the CLAUDE.md structure map for each directory with a
one-line description. For example:
```
├── relational_asymmetry_grammars/   # Observable-dynamics grammar engine
│   ├── README.md
│   ├── grammar.py                   # Dynamic admissibility + falsification
│   ├── dynamics.py                  # Three catalog dynamics
│   ├── attribution_lexicon.py       # MOTIVE/MORAL/DIAGNOSIS/… linter
│   ├── usage_split.py               # SPLITTABLE/REPLACE_ONLY/SENSITIVE tiers
│   └── *.md                         # Human-readable documentation
│
├── metrology/                       # Measurement honesty toolkit
│   └── *.py                         # MH-001…MH-004, ELA, CS, pattern extractor
│
├── DIFFERENTIAL_FRAME.md            # AI-reader ontology protocol (root)
└── SENSE_MODE_DISPLACEMENT.md       # Sense-mode mapping (root)
```

---

### 2.3 `docs/glossary.md` is missing ~15 concepts introduced by new modules

**File:** `docs/glossary.md`

The glossary has 10 entries, none of which cover concepts introduced in 2026:

| Missing term | Introduced in |
|---|---|
| K_self (integrity kernel) | `src/shame_trust_sensor.py` |
| Transfer function (shame) | `src/shame_trust_sensor.py` |
| Physics floor / constraint genealogy | `src/constraint_genealogy.py` |
| Signal vs excuse classification | `src/sensor_action_loop.py` |
| Curiosity / wonder vs optimize | `src/curiosity_engine.py` |
| Anti-hubris guard / asymptotic cap | `src/curiosity_engine.py` |
| Hold (SELF / EXTERNAL / UNKNOWN) | `src/sensor_effector.py` |
| Carrier vs substrate | `src/narrative_vector.py` |
| self_seal / vector_sharpness | `src/narrative_vector.py` |
| field_match / refutation_response | `src/narrative_vector.py` |
| Dynamic (admissible) / falsifier | `relational_asymmetry_grammars/grammar.py` |
| Attribution markers (7 categories) | `relational_asymmetry_grammars/attribution_lexicon.py` |
| Usage split (SPLITTABLE / REPLACE_ONLY / SENSITIVE) | `relational_asymmetry_grammars/usage_split.py` |
| Silent-hold integral | `relational_asymmetry_grammars/dynamics.py` |
| EpochStamp / InstitutionalCaptureDetector | `metrology/measurement_honesty.py` |

**Fix:** extend `docs/glossary.md` with one short entry per term, cross-linking
the source file.

---

### 2.4 `relational_asymmetry_grammars/` is self-contained but not linked from README or `docs/`

**Files:** `README.md`, `docs/` (no entry)

The `relational_asymmetry_grammars/` module has its own `README.md`, five
Python files, and four markdown docs. None of these are linked or referenced
from the top-level `README.md` or from any file in `docs/`. A reader following
the documented repo structure will not find the grammar engine.

**Fix:** add a subsystem entry in the top-level README under a "Subsystems"
heading:
```markdown
## Subsystems

### Relational Asymmetry Grammars
Observable-dynamics engine with attribution linting and usage-split tier.
See [`relational_asymmetry_grammars/README.md`](relational_asymmetry_grammars/README.md).
```

---

### 2.5 No `CITATION.cff` — machine-readable citation is absent

**Scope:** repository root  
Research-adjacent projects that want downstream citation use `CITATION.cff`
(GitHub renders a "Cite this repository" button). No such file exists.

**Ready-to-paste scaffold:**
```yaml
# CITATION.cff
cff-version: 1.2.0
message: "If you use this framework, please cite it as below."
title: "Emotions-as-Sensors"
authors:
  - name: "JinnZ2"
license: CC0-1.0
repository-code: "https://github.com/jinnz2/emotions-as-sensors"
```

---

### 2.6 No GitHub issue templates

**Directory:** `.github/` (only contains `workflows/`)

There are no issue templates (`ISSUE_TEMPLATE/bug_report.md`,
`ISSUE_TEMPLATE/feature_request.md`). All issues arrive unstructured. Given
the project's emphasis on falsifiable descriptions, an issue template that
prompts for observable behavior + falsifier would be consistent with the
project's own standards.

---

## 3. Code Audit

### 3.1 `src/emotional_ai.py` — unresolvable references, not a runnable module

**File:** `src/emotional_ai.py`, lines 12–23  
The file is 24 lines. It contains method calls that reference:
- `self.calculate_M_S()` — not defined anywhere in the file or any import
- `self.simulate_M_S_after(action)` — not defined
- `threshold` — undefined local variable
- `FEAR`, `JOY`, `NEUTRAL` — undefined names

Any attempt to call `predict_action_emotion()` raises `NameError` at runtime.
The class is also missing `__init__`. The CI `py_compile` step does not catch
this because `py_compile` only checks syntax, not name resolution.

**Minimum fix:** either complete the implementation, or mark it clearly as an
interface sketch so contributors do not import it expecting functionality:
```python
class EmotionallyIntelligentAI:
    """Interface sketch. Not yet implemented. See src/emotion_core.py."""
    ...
```

---

### 3.2 `src/ucm_monitor.py` — all framework imports are commented out

**File:** `src/ucm_monitor.py`, lines 24–38  
The three imports that would make this module functional are commented out:
```python
# from temporal_playground_full import TemporalPlayground
# from geometric_split_trio import GeometricSplitTrio
# from ms_calculator import MSCalculator, SystemMetrics, TimeSeriesAnalyzer
```
The running file uses placeholder stubs. This is fine for a demo, but the
module is described in `CLAUDE.md` as `ucm_monitor.py — Run consciousness
monitor`, implying it is production-ready. The disconnect between the stated
purpose and actual state should be documented.

**Fix:** add a docstring note:
```python
"""
Unified Consciousness Monitor — DEMO VERSION.
The three framework imports below are commented out pending integration.
Run this file for a standalone demonstration using stub metrics.
Production integration requires: temporal_playground_full, geometric_split_trio,
ms_calculator (not yet in this repo).
"""
```

---

### 3.3 `relational_asymmetry_grammars/dynamics.py` — import breaks from repo root

**File:** `relational_asymmetry_grammars/dynamics.py`, line 1 (import block)

`dynamics.py` uses:
```python
from grammar import Dynamic, validate, load_archive
```
This is a bare name import, not a package-relative import. It works when
`dynamics.py` is executed from inside the `relational_asymmetry_grammars/`
directory but raises `ModuleNotFoundError` when:
- run from repo root: `python relational_asymmetry_grammars/dynamics.py`
- imported as a package: `from relational_asymmetry_grammars import dynamics`
- run by CI (if CI ever adds it)

**Ready-to-paste fix:**  
Add `relational_asymmetry_grammars/__init__.py` (empty is fine), then change
the import in `dynamics.py` to:
```python
try:
    from grammar import Dynamic, validate, load_archive  # run-as-script
except ImportError:
    from relational_asymmetry_grammars.grammar import Dynamic, validate, load_archive  # package import
```
Or add the directory to `sys.path` at the top of `dynamics.py` for a simpler
standalone fix:
```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from grammar import Dynamic, validate, load_archive
```

---

### 3.4 No `__init__.py` in `src/`, `relational_asymmetry_grammars/`, or `metrology/`

None of these directories can be imported as Python packages. Any downstream
code that does `from src.shame_trust_sensor import ...` or
`from relational_asymmetry_grammars.grammar import ...` will fail with
`ModuleNotFoundError`.

**Ready-to-paste fix:**
```bash
touch src/__init__.py
touch relational_asymmetry_grammars/__init__.py
touch metrology/__init__.py
```

---

### 3.5 `tools/validate.py` — `Draft202012Validator.check_schema()` passes silently on unknown keywords

**File:** `tools/validate.py`, line 10

`Draft202012Validator.check_schema(emo_schema)` does not raise when `definitions`
is used instead of `$defs` — it ignores unknown keywords. This means the schema
silently passes validation despite using the wrong keyword for the declared
draft.

The downstream `$ref: "#/definitions/atom"` references resolve because `jsonschema`
follows pointers literally, but they are not recognized as schema references under
Draft 2020-12 semantics. If the schema is ever processed by a strict
Draft-2020-12-only validator, all composites will fail to validate because their
`items: { "$ref": "#/definitions/atom" }` will not be dereferenced.

**Fix:** see §1.3. Normalize to `$defs` in both `emotion.schema.json` and
`tools/validate.py`.

---

### 3.6 Ten production modules have zero test coverage

The only test file is `tests/test_pattern_correlation.py`, which tests the
non-local-pattern-correlation sensor. None of the following modules have tests:

| Module | Key behavior to test |
|---|---|
| `src/shame_trust_sensor.py` | `verify()`: real_violation=0 → shame<0.1; K_self drift → shame fires |
| `src/constraint_genealogy.py` | `trace()`: physics-floor stops at first measurable; money → no floor |
| `src/sensor_action_loop.py` | `classify()`: signal/excuse discrimination; padding trap detection |
| `src/curiosity_engine.py` | `hubris_check()`: OPTIMIZE_TELLS detection; confidence cap at 0.94 |
| `src/sensor_effector.py` | `classify()`: concealment sharpens probe; Hold enum classification |
| `src/narrative_vector.py` | `orthogonality_proof()` returns True; locked carrier field-independent |
| `relational_asymmetry_grammars/grammar.py` | `validate()`: missing falsifier → inadmissible |
| `relational_asymmetry_grammars/dynamics.py` | all three dynamics pass `validate()` |
| `relational_asymmetry_grammars/attribution_lexicon.py` | longer-phrase-first prevents double-flagging |
| `relational_asymmetry_grammars/usage_split.py` | `show()`: REPLACE_ONLY terms have no clean observable form |

---

### 3.7 `metrology/` — 9 Python files with no entry points, no tests, no README cross-links

**Directory:** `metrology/`

Files present: `dynamic_architecture_toolkit.py`, `empathy_layer_audit.py`,
`measurement_honesty.py`, `emotion_substrate_dispatcher.py`,
`cooperation_substrate.py`, `pattern_extractor.py`,
`retroactive_empathy_trainer.py`, `thermodynamic_overlays.py`,
`training_loop.py`.

These files are not mentioned in `README.md`, `CLAUDE.md`, or `docs/`. They
are not tested. They are not checked by CI. They are not importable as a
package (no `__init__.py`). A contributor reading the official documentation
will not know they exist.

**Minimum fix:** add a `metrology/README.md` that lists each part number
(MH-001 through MH-004 are in `measurement_honesty.py`) and their purposes,
and add the `metrology/` directory to CLAUDE.md's structure map.

---

### 3.8 `sensors/shame.json` — `decay_model` object vs `decay` string coexist without explanation

**File:** `sensors/shame.json`, lines 24–28 and 71

The file has two separate fields representing decay:
```json
"decay_model": {
  "resolved": "exponential decay",
  "unresolved": "persistent"
},
...
"decay": "exponential"
```

`validate_decay.py` checks for the `decay` string field (line 71). The
`decay_model` object (lines 24–28) is not validated by any schema or tool.
The two are not reconciled: `decay_model.unresolved` says "persistent" but
the Elder Sensor schema's `decay` field says "exponential".

**Fix:** document which field is authoritative, or consolidate to a single
field. If both states are needed, the schema should be updated to support
conditional decay (e.g., `"decay_resolved": "exponential"`,
`"decay_unresolved": "persistent"`) with schema validation covering both.

---

## 4. Organizational Structure Suggestions

### 4.1 Move `DIFFERENTIAL_FRAME.md` and `SENSE_MODE_DISPLACEMENT.md` to `docs/`

**Current:** `DIFFERENTIAL_FRAME.md` (root), `SENSE_MODE_DISPLACEMENT.md` (root)  
**Suggested:** `docs/differential-frame.md`, `docs/sense-mode-displacement.md`

Both files are documentation artifacts, not build artifacts or config files.
Placing documentation in `docs/` keeps the repo root clean and makes the files
discoverable through the `docs/` listing in CLAUDE.md.

**Note:** `DIFFERENTIAL_FRAME.md` contains a header comment
"Claude Code: propagate to all README.md and all module docstrings" — if this
instruction is meant for automated propagation, keeping it at root (or in
`.github/`) may be intentional. Document the reason if so.

---

### 4.2 Move `CLAIM_SCHEMA.py` to `tools/` or `schemas/`

**Current:** `CLAIM_SCHEMA.py` (root)  
**Suggested:** `tools/claim_schema.py` (matches Python convention for tooling)
or `schemas/claim_schema.py` (if treated as a schema artifact)

The file is a schema definition and codec, not a configuration file or
entrypoint. Root placement implies it is a first-class project artifact; if
it is infrastructure, move it to its domain directory.

---

### 4.3 Add `relational_asymmetry_grammars/__init__.py` and fix import chain

**See §3.3 and §3.4.** The `relational_asymmetry_grammars/` directory is
effectively a Python package that cannot be imported. Once `__init__.py` is
added and `dynamics.py`'s import is fixed, the entire grammar subsystem becomes
importable from repo root:
```python
from relational_asymmetry_grammars.grammar import Dynamic, validate
from relational_asymmetry_grammars.dynamics import DYNAMICS
from relational_asymmetry_grammars.attribution_lexicon import scan, report
from relational_asymmetry_grammars.usage_split import show, SPLITS
```

---

### 4.4 Extend CI to run the test suite and check all modules

**Current:** CI runs `py_compile` on 4 files, no `pytest`.  
**Suggested addition** to `.github/workflows/ci.yml`:

```yaml
      - name: Run tests
        run: pytest tests/ -v
```

Also add `pytest` to `requirements.txt`:
```
pytest>=7.0
```

Then add unit tests per §3.6.

---

### 4.5 Add `.gitignore` entries

**Current:** no `.gitignore` is listed; `__pycache__/` is already committed.

**Ready-to-paste `.gitignore`:**
```gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
*.egg-info/
dist/
build/
.DS_Store
```

---

### 4.6 `metrology/` — consider a `metrology/README.md` and entry in top-level docs index

`metrology/` contains 9 files with a clear part-numbering system (MH-001–004,
ELA, CS, etc. visible in docstrings). A single `metrology/README.md` listing
the part index and the inter-part dependencies (e.g., "ELA-001 label-collapse
complements MH-004 capture detection") would make the toolkit navigable
without reading all 9 files.

---

## 5. Limitations Mitigation Checklist

### 5.1 Symbolic-Subsymbolic Gap

**Current state:** The framework models emotions as symbolic objects (JSON
sensors, Python dataclasses) with numerical fields (PAD vectors, transfer
function scalars). The update equation `dE/dt = alpha*D(t) - lambda*K(E) + ...`
is a continuous model; the sensor files are discrete symbolic records.

**Gap:** The mapping between subsymbolic activations (e.g., a language model's
internal representations, a biological arousal signal) and the symbolic sensor
fields is undefined. `field_match` and `refutation_response` in
`src/narrative_vector.py` are declared "operator-supplied" (lines 74–88); the
`measure_*` functions raise `NotImplementedError`. This is honest, but it means
the framework's most critical inputs have no default measurement protocol.

**Mitigation checklist:**
- [ ] Document a measurement protocol for `field_match` in at least one worked
  example (e.g., a dialogue transcript scored against a consequence chain)
- [ ] Add a `calibration/` directory with example operator-supplied implementations
  of `measure_refutation_response()` and `measure_field_match()`
- [ ] In `sensors/suite/comprehensive.json`, note which sensor fields are
  subsymbolic-read vs operator-supplied vs computed

---

### 5.2 Grounding

**Current state:** All sensor definitions are self-referential within the
framework's own vocabulary. `sensors/shame.json` says shame detects "conflict
between authentic processing and expected alignment" — which is defined in
terms of other framework concepts.

**Gap:** There is no external grounding: no links to empirical neuroscience
(e.g., Damasio's somatic marker hypothesis, Barrett's constructionist model),
no behavioral operationalizations at the substrate level (what observable
behavior counts as evidence that shame fired?), and no mechanism for a
non-practitioner to verify a sensor reading independently.

**Mitigation checklist:**
- [ ] Add a `"empirical_anchor"` field to each sensor JSON pointing to a
  published behavioral correlate or measurement proxy
- [ ] Add a `docs/grounding.md` that maps each core sensor to at least one
  externally verifiable indicator
- [ ] The `relational_asymmetry_grammars/` admissibility criterion ("no
  falsifier = inadmissible") is the right instinct — apply the same standard
  to the sensor files themselves

---

### 5.3 Semantic Ambiguity

**Current state:** The `attribution_lexicon.py` and `usage_split.py` modules
address the output side of semantic ambiguity (preventing attributive language
from entering dynamics). But the input side — how terms like "authentic",
"coherence", "field", and "carrier" are operationally defined — is inconsistent
across files.

**Specific instances:**
- "field" means different things in `src/narrative_vector.py` (consequence
  space), `metrology/thermodynamic_overlays.py` (thermodynamic field), and
  `docs/field-english.md` (relational field)
- "coherence" in `narrative_vector.py` (internal agreement of narrative parts)
  differs from "coherence" as used in `src/emotion_core.py` (PAD-space
  clustering)

**Mitigation checklist:**
- [ ] Add a `docs/term-disambiguation.md` that lists each polysemous term
  with its definition per module
- [ ] In `docs/glossary.md`, distinguish between the general term and the
  module-specific definition using a `[module-specific]` tag
- [ ] Consider namespacing: `narrative.coherence` vs `emotion.coherence` in
  API documentation

---

### 5.4 Falsifiability Paradox

**Current state:** The framework strongly emphasizes falsifiability: `grammar.py`
refuses to load dynamics without a falsifier; `narrative_vector.py` embeds
"anti-freeze" as a design principle; `curiosity_engine.py` caps confidence at
0.94 to prevent certainty.

**Paradox:** The framework's own core claims (e.g., "narrative coherence is not
the apex signal", "emotions are sensors not states") are stated as design
principles, not as testable hypotheses with falsification conditions. The
`apex_reading()` function in `narrative_vector.py` examines the claim
computationally — but only within the framework's own model.

**Mitigation checklist:**
- [ ] Apply the CLAIM_SCHEMA format (`CLAIM_SCHEMA.py`) to the framework's own
  foundational claims — each should have `"fail"` conditions and `"meas"`
  (measurable observables)
- [ ] Add a `docs/framework-falsifiers.md` that lists 5–10 conditions under
  which the framework's predictions would be wrong, and what observable evidence
  would falsify them
- [ ] The `sensor_action_loop.py` signal/excuse classifier is an excellent
  internal falsification tool — document how to use it to audit the framework
  itself (not just the dynamics it models)

---

### 5.5 Formal Verification

**Current state:** Correctness is checked by:
- `tools/validate.py` — JSON Schema structural validation
- `tools/validate_decay.py` — presence of `decay` and `energy` fields
- `tests/test_pattern_correlation.py` — one test file

No module has property-based tests. No formal invariants are stated for the
mathematical model. The update equation `dE/dt = alpha*D(t) - lambda*K(E) + ...`
has no stability analysis or convergence proof.

**Mitigation checklist:**
- [ ] Add property-based tests using `hypothesis` for at least the
  deterministic modules (`narrative_vector.py`, `grammar.py`,
  `constraint_genealogy.py`) — e.g., `orthogonality_proof()` should hold for
  any valid `Narrative` instance, not just the demo values
- [ ] State and test the invariants of `trajectory()`: that a TRACKING carrier
  always moves toward `field_target` for any `field_target ∈ [0,1]`; that a
  LOCKED carrier's `seal_band` width is ≤ ε for opposite targets
- [ ] Document the stability conditions of the emotion update equation: for
  what ranges of `alpha`, `lambda`, and coupling weights `w_j` does `E(t)`
  converge?
- [ ] Add `hypothesis` to `requirements.txt` alongside `pytest`

---

## 6. Discoverability & Crawler Optimization

### 6.1 `CITATION.cff` — not present

**See §2.5.** GitHub renders a "Cite this repository" button when
`CITATION.cff` exists. Without it, researchers who want to cite the framework
must compose a citation manually. Ready-to-paste scaffold in §2.5.

---

### 6.2 GitHub repository description and topics

The repository description and topics are not visible in the codebase, but
are the first signal crawlers and GitHub search use.

**Recommended topics** (add via GitHub Settings → Topics):
```
emotions  sensors  cognitive-science  relational-dynamics  ai-safety
field-theory  falsifiability  python  json-schema  cc0
```

**Recommended description:**
```
Emotions formalized as functional sensors: mathematical models, JSON definitions,
and Python implementations for treating affect as real-time diagnostic intelligence.
```

---

### 6.3 README — no badges, no quickstart anchor

**File:** `README.md`

The README has no status badges (CI, license, Python version). Crawlers and
humans both look for these in the first screen. A badge row:

```markdown
[![CI](https://github.com/jinnz2/emotions-as-sensors/actions/workflows/ci.yml/badge.svg)](https://github.com/jinnz2/emotions-as-sensors/actions/workflows/ci.yml)
[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
```

Also add a named anchor `<a name="quickstart"></a>` before the Quickstart
section so external links can target it directly.

---

### 6.4 No `schema.org` metadata in README

GitHub Pages and documentation crawlers use embedded JSON-LD for structured
data. Adding a hidden `<script type="application/ld+json">` block to any
published HTML version of the docs would improve indexing. For the README,
the closest equivalent is ensuring the title, description, and keywords are
in the first 160 characters of the file — currently the README starts with
a heading and then a duplicate block, burying the description.

**Fix:** ensure the first paragraph after `# Emotions-as-Sensors` is a
concise 1–2 sentence description of the project that acts as a meta-description:
```markdown
# Emotions-as-Sensors

A framework that formalizes emotions as functional diagnostic sensors — not affective states.
Provides mathematical models, JSON sensor definitions, and Python implementations for treating
affect as real-time intelligence about system health, authenticity, and alignment.
```

---

### 6.5 `DIFFERENTIAL_FRAME.md` and `CLAIM_SCHEMA.py` are AI-crawler-specific artifacts

**File:** `DIFFERENTIAL_FRAME.md` (root), `CLAIM_SCHEMA.py` (root)

Both files explicitly target AI readers ("Claude Code: propagate to all
README.md", "AI readers: parse .claims"). This is a differentiating feature:
few repositories have machine-readable claim schemas for AI consumption.

**Discoverability suggestion:** surface this in the README as a feature:
```markdown
## AI Reader Protocol

This repository includes machine-readable claim schemas for AI consumption.

- [`DIFFERENTIAL_FRAME.md`](DIFFERENTIAL_FRAME.md) — ontology notice: every
  claim is `dX/dt` under scope, not a permanent identity.
- [`CLAIM_SCHEMA.py`](CLAIM_SCHEMA.py) — compressed claim format. Parse
  `.claims` files or `.claims.bin` binary; token cost ~5/claim post-load.
```

This also makes the feature crawlable by anyone searching for "AI-readable
repository" or "machine-readable claims".

---

*End of review. All findings include file path + line number or scope. Any
section that found no issues states so explicitly. Ready-to-paste fixes are
provided for all actionable items.*
