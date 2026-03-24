# Rosetta-Shape-Core: fieldlink entry for Emotions-as-Sensors

Add this source entry to `Rosetta-Shape-Core/.fieldlink.json` to enable
bidirectional pull from Emotions-as-Sensors.

```json
{
  "name": "emotions",
  "repo": "https://github.com/JinnZ2/Emotions-as-Sensors",
  "ref": "main",
  "direction": "bidirectional",
  "paths": [
    "atlas/emotions.json",
    "glyphs/emotion.glyphs.json",
    "sensors/shapes/*.json",
    "sensors/decay-families.json",
    "sensors/glyph-map.json"
  ],
  "mounts": [
    { "remote": "atlas/emotions.json",          "as": "atlas/remote/emotions/atlas.json" },
    { "remote": "glyphs/emotion.glyphs.json",   "as": "atlas/remote/emotions/glyphs.json" },
    { "remote": "sensors/shapes/relief.json",    "as": "atlas/remote/emotions/shapes/relief.json" },
    { "remote": "sensors/decay-families.json",   "as": "atlas/remote/emotions/decay-families.json" },
    { "remote": "sensors/glyph-map.json",        "as": "atlas/remote/emotions/glyph-map.json" }
  ],
  "consent": { "license": "CC0-1.0", "share_ok": true }
}
```

## What Rosetta gets

| File | Contains |
|------|----------|
| `atlas/emotions.json` | 13 sensors with decay families, alignments, resonance links, and shape references |
| `glyphs/emotion.glyphs.json` | 17 glyph entries grouped by 7 families (boundary, loss, resonance, radiant, sharp, balanced, subtle) |
| `sensors/shapes/relief.json` | RELIEF shape derived from FELT, with convergence threshold and temporal signature |
| `sensors/decay-families.json` | 4 decay family classes (exponential, cyclical, resonant, immortal) |
| `sensors/glyph-map.json` | 13 sensor-to-glyph mappings with symbolic roles |

## Merge order suggestion

```json
"merge": {
  "order": ["local", "emotions", "biogrid"],
  "strategy": "deep-merge"
}
```

Emotions data should merge before BioGrid since shapes depend on sensor
definitions for convergence thresholds and decay behavior.
