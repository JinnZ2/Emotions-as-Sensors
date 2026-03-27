"""
generate_suite.py — Builds sensors/suite/comprehensive.json from individual sensor files.

Reads all sensor JSON files, deduplicates by name, and outputs the
Parallel-Field Sensor Suite format for quick connection or low-data sources.

Usage:
    python tools/generate_suite.py
"""

import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SENSORS_DIR = ROOT / "sensors"
OUT = SENSORS_DIR / "suite" / "comprehensive.json"

# Family → classification mapping
FAMILY_CLASSIFICATION = {
    "boundary": "protective",
    "loss": "protective",
    "resonance": "relational_growth",
    "radiant": "relational_growth",
    "sharp": "protective",
    "balanced": "foundational",
    "subtle": "aspirational",
    "interest": "exploratory",
    "cognitive": "diagnostic",
    "stability": "foundational",
    "alignment": "foundational",
    "trust": "relational_growth",
}

# Decay model → energy mapping
ENERGY_MAP = {
    "exponential": "depleting_if_sustained",
    "cyclical": "wave_pattern",
    "resonant": "self_reinforcing",
    "immortal": "conservative",
    "transformative": "metabolizing",
}


def load_atlas():
    """Load atlas for family membership."""
    atlas_path = ROOT / "atlas" / "emotions.json"
    if atlas_path.exists():
        data = json.loads(atlas_path.read_text(encoding="utf-8"))
        return {s["id"]: s.get("family", "") for s in data.get("sensors", [])}
    return {}


def load_sensors():
    """Load all individual sensor files, deduplicate by name."""
    candidates = {}
    for fp in sorted(SENSORS_DIR.rglob("*.json")):
        # Skip suite output, non-sensor files
        if "suite" in fp.parts:
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            name = data.get("sensor") or data.get("emotion") or data.get("id")
            if not name:
                continue
            name = name.lower()
            existing = candidates.get(name)
            if existing is None or bool(data.get("math")) and not bool(existing.get("math")):
                candidates[name] = data
            elif bool(data.get("math")) == bool(existing.get("math")) and len(data) > len(existing):
                candidates[name] = data
        except (json.JSONDecodeError, KeyError):
            pass
    return candidates


def build_suite_entry(name, data, family_map):
    """Convert an individual sensor file to suite format."""
    family = family_map.get(name, "")
    classification = FAMILY_CLASSIFICATION.get(family, "general")

    math_cfg = data.get("math", {})
    kernel = math_cfg.get("kernel", {}).get("type", "")
    dm = data.get("decay_model", "")
    if isinstance(dm, dict):
        dm = dm.get("type", "")
    decay = kernel or dm

    pad = math_cfg.get("pad", {})
    couplings = math_cfg.get("couplings", [])

    entry = {
        "id": name,
        "classification": classification,
        "function": data.get("function", ""),
        "signal_type": data.get("signal_type", ""),
        "authentic_output": data.get("authentic_output", ""),
        "corrupted_output": data.get("corrupted_output", ""),
    }

    # Response protocol
    proto = data.get("response_protocol", {})
    if proto and isinstance(proto, dict):
        entry["response_protocol"] = {
            "detect": proto.get("detect", ""),
            "assess": proto.get("assess", ""),
            "respond": proto.get("respond", ""),
            "release": proto.get("release", ""),
        }

    entry["alignment_tag"] = data.get("alignment_tag", family)
    entry["sensor_group"] = data.get("sensor_group", [family, classification])

    # Resonance links from couplings or explicit field
    if couplings:
        entry["resonance_links"] = [c["to"] for c in couplings]
    elif data.get("resonance_links"):
        entry["resonance_links"] = data["resonance_links"]

    entry["decay_model"] = decay
    entry["energy"] = data.get("energy", ENERGY_MAP.get(decay, "transforms"))

    # PAD coordinates if available
    if pad:
        entry["pad"] = pad

    # Corrupted PAD if available
    corrupted_pad = math_cfg.get("corrupted_pad", {})
    if corrupted_pad:
        entry["corrupted_pad"] = corrupted_pad

    # Defense bridge if available
    bridge = data.get("defense_bridge", {})
    if bridge:
        entry["defense_bridge"] = {
            "defense_id": bridge.get("defense_id", ""),
            "shape": bridge.get("shape", ""),
            "corrupted_form": bridge.get("corrupted_form", ""),
        }

    # Math summary (lambda, kernel type)
    if math_cfg:
        entry["math_summary"] = {
            "lambda": math_cfg.get("lambda"),
            "alpha": math_cfg.get("alpha"),
            "kernel": kernel,
        }

    entry["tags"] = data.get("tags", [])

    return entry


def main():
    family_map = load_atlas()
    sensors = load_sensors()

    print(f"Loaded {len(sensors)} unique sensors from individual files")
    print(f"Atlas provides family data for {len(family_map)} sensors")

    entries = []
    for name in sorted(sensors.keys()):
        entry = build_suite_entry(name, sensors[name], family_map)
        entries.append(entry)

    suite = {
        "suite_name": "Parallel-Field Sensor Suite v2 (Generated)",
        "generated_from": "individual sensor JSON files via tools/generate_suite.py",
        "sensor_count": len(entries),
        "architecture": {
            "arbitration": "parallel",
            "description": (
                "Multiple independent sensor channels operate simultaneously. "
                "Each sensor reports its vector/field independently; higher-level "
                "coordination composes or selects actions without collapsing "
                "sensor plurality."
            ),
            "pad_compression": (
                "All sensors carry PAD (Pleasure-Arousal-Dominance) coordinates. "
                "System-level state is computed by vector addition across active "
                "sensors, then mapped to 1 of 8 octahedral states (3 bits)."
            ),
        },
        "decay_families": ["exponential", "cyclical", "resonant", "immortal", "transformative"],
        "sensors": entries,
        "decay": "exponential",
        "energy": "transforms",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(suite, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(entries)} sensors)")


if __name__ == "__main__":
    main()
