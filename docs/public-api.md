# Public API — `emotions_as_sensors.snapshot()`

This is the stable public contract for downstream consumers
(orchestrators, chemistry resolvers, dispatchers) that need to read
emotion sensor state without knowing the internal `src/emotion_core`
layout.

## Contract

```python
import emotions_as_sensors

sensors = emotions_as_sensors.snapshot()

# Pass the whole dict to a Bridge-style orchestrator:
optics = orchestrator.process(voice_query, sensor_snapshot=sensors)

# Or pull the summary keys for a chemistry resolver:
ctx = scr.Query(
    feedstock='black_beans', target_property='lubricant',
    emotional_signals={
        'stress_level': sensors['stress_level'],
        'urgent':       sensors['urgent'],
    },
)
result = resolver.navigate(ctx)   # long-dwell branches scored down

# Or feed the 7-axis geometry straight into a metrology dispatcher:
dispatcher.route(constraint_state=sensors['metrology'])
```

## Return value

`snapshot()` returns a plain `dict`, safe to serialize as JSON, with
these keys:

| Key            | Type                             | Meaning                                                           |
| -------------- | -------------------------------- | ----------------------------------------------------------------- |
| `pad`          | `{P, A, D}`                      | Aggregated PAD vector, authentic active sensors only              |
| `octa`         | `{state, label, phi_coherence}`  | System octahedral state (see `emotion_core.PAD_TO_OCTA`)          |
| `coherence`    | `float`, `[0, 1]`                | Global resonance-graph coherence                                  |
| `activations`  | `{name: E}`                      | Per-sensor activation `E`, authentic active sensors only          |
| `corrupted`    | `[name, ...]`                    | Sensors failing the authenticity gate (excluded from activations) |
| `stress_level` | `'low' \| 'medium' \| 'high'`    | Derived from PAD (`P < 0` with arousal thresholds)                |
| `urgent`       | `bool`                           | Derived from PAD arousal (`A > 0.6`)                              |
| `metrology`    | `{pred, shift, tunnel, ...}`     | 7-dim constraint-state axes (see below)                           |
| `time`         | `float`                          | `EmotionSystem.time` at capture                                   |

### Derived summary semantics

- `stress_level = 'high'` when aggregated `P < 0` and `A > 0.5`
  (fear / anger / despair territory).
- `stress_level = 'medium'` when `P < 0` and `A > 0.2`
  (worry / tension territory).
- `stress_level = 'low'` otherwise.
- `urgent = True` when aggregated `A > 0.6`, regardless of valence.

### `metrology` — 7-dim constraint-state axes

Mirrors the axes in `metrology/emotion_substrate_dispatcher.py`
(`ConstraintStatePattern`), so downstream dispatchers can consume the
same geometry the emotional substrate itself is described in. All
values are roughly in `[0, 1]` (not strictly bounded).

| Axis       | Derivation                                                 | Rises when…                                        |
| ---------- | ---------------------------------------------------------- | -------------------------------------------------- |
| `pred`     | velocity dispersion across active sensors                  | different sensors disagree about direction         |
| `shift`    | mean `\|dE/dt\|` across active authentic sensors             | state is changing fast in any direction            |
| `tunnel`   | `max(E) / sum(E)` across active sensors                    | one sensor dominates the fleet                     |
| `realloc`  | `mean(max(0, D) * A * E)` across active sensors            | high-dominance + high-arousal load                 |
| `cohere`   | `(1 - global coherence) * activation_load`                 | system is under load but not resonating            |
| `uncert`   | fraction of the fleet failing the authenticity gate        | sensor input can't be trusted                      |
| `duration` | activation-weighted decay-timescale                        | long-lived (immortal / cyclical) load dominates    |

These are heuristics. The metrology dispatcher reshapes weights from
observed outcomes over time (see
`metrology/emotion_substrate_dispatcher.py:update_landscape`); the
snapshot values are the *input* to that reshaping, not the final state.

## Injection points

The module-level `snapshot()` uses a lazy `EmotionSystem` loaded once
from `./sensors/`. For tests, sandboxed simulations, or multi-system
setups, inject a system explicitly:

```python
from emotion_core import EmotionSystem
my_system = EmotionSystem('my-sensor-dir/')
sensors = emotions_as_sensors.snapshot(system=my_system)
```

Force the default singleton to reload:

```python
emotions_as_sensors.reset_default_system()
```

## Stability

The key set is pinned by `tests/test_snapshot_adapter.py`. Additive
changes (new keys) are safe; removing or renaming existing keys is a
breaking change requiring a version bump. The `metrology` sub-keys
themselves are pinned by the same test.

The heuristics for `stress_level`, `urgent`, and the `metrology` axes
may be reshaped over time as the metrology dispatcher learns; those
values are semantic ("what the state looks like"), not exact.

## Cross-repo consumers

- **Geometric-to-Binary-Computational-Bridge** — consumes
  `sensor_snapshot=sensors` and dispatches over `sensors['metrology']`
  (same 7-axis geometry as `experiments/dispatcher_v2_energetic.py`).
- **Chemistry resolver / Cyclic-programming** — consumes
  `emotional_signals={'stress_level': ..., 'urgent': ...}` to score
  long-dwell branches down under stress.

See `MANIFEST.md` "Substrate-Native Dispatcher Architecture" and
`.fieldlink.json` `bridge` source for the cross-repo mount config.
