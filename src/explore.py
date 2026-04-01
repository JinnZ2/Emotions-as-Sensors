"""
Emotions-as-Sensors — Explore Channel

A discovery interface for any AI or human to explore emotion sensors,
cultural overlays, decay models, resonance graphs, and PAD coordinates.

No dependencies beyond stdlib + this repo's JSON files. Designed to be
imported, called from CLI, or queried programmatically.

Usage:
    python src/explore.py                       # interactive summary
    python src/explore.py sensors               # list all sensors
    python src/explore.py sensor anger          # detail view
    python src/explore.py overlays              # list cultural overlays
    python src/explore.py overlay honor_culture # detail view
    python src/explore.py compare anger shame   # compare sensors
    python src/explore.py family boundary       # list sensors in family
    python src/explore.py decay exponential     # list sensors by decay model
    python src/explore.py pad -0.5 0.8 0.7     # find nearest sensor to PAD
    python src/explore.py graph anger           # show resonance neighbors
    python src/explore.py graph anger depth=2   # 2-hop resonance walk
    python src/explore.py help                  # show all commands

Programmatic:
    from explore import ExploreChannel
    ch = ExploreChannel()
    ch.sensor("anger")
    ch.overlay("honor_culture")
    ch.compare("anger", "fear")
    ch.nearest_pad(-0.5, 0.8, 0.7)
    ch.graph("anger", depth=2)
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
SENSORS_DIR = ROOT / "sensors"
DATA_DIR = ROOT / "data"
ATLAS_PATH = ROOT / "atlas" / "emotions.json"


class ExploreChannel:
    """Discovery interface for Emotions-as-Sensors."""

    def __init__(self):
        self.sensors = self._load_sensors()
        self.overlays = self._load_overlays()
        self.atlas = self._load_atlas()
        self.families = self.atlas.get("sensor_families", {})
        self.decay_families = self.atlas.get("decay_families", {})

    # ── Loaders ──────────────────────────────────────────────────────────

    def _load_sensors(self) -> Dict[str, dict]:
        sensors = {}
        for fp in sorted(SENSORS_DIR.rglob("*.json")):
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
                data["_path"] = str(fp.relative_to(ROOT))
                if name not in sensors or data.get("math"):
                    sensors[name] = data
            except (json.JSONDecodeError, KeyError):
                pass
        return sensors

    def _load_overlays(self) -> List[dict]:
        p = DATA_DIR / "cultural-overlays.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8")).get("overlays", [])
        return []

    def _load_atlas(self) -> dict:
        if ATLAS_PATH.exists():
            return json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
        return {}

    # ── Core queries ─────────────────────────────────────────────────────

    def help(self) -> str:
        """Show all available exploration commands."""
        return (
            "Emotions-as-Sensors — Explore Channel\n"
            "======================================\n\n"
            f"  {len(self.sensors)} sensors | {len(self.overlays)} cultural overlays | "
            f"{len(self.families)} families | {len(self.decay_families)} decay models\n\n"
            "Commands:\n"
            "  sensors                    List all sensors with PAD + decay\n"
            "  sensor <name>              Detail view of one sensor\n"
            "  overlays                   List all cultural overlays\n"
            "  overlay <culture_id>       Detail view + D-axis shifts\n"
            "  compare <a> <b> [overlay]  Side-by-side sensor comparison\n"
            "  family <name>              List sensors in a family\n"
            "  families                   List all families\n"
            "  decay <model>              List sensors using a decay model\n"
            "  pad <P> <A> <D>            Find nearest sensor to PAD coordinates\n"
            "  graph <name> [depth=N]     Walk the resonance graph\n"
            "  schema                     Show the canonical sensor JSON schema\n"
        )

    def list_sensors(self) -> str:
        """List all sensors with key attributes."""
        lines = [f"{'Sensor':<20} {'Decay':<15} {'P':>6} {'A':>6} {'D':>6}  Family"]
        lines.append("-" * 75)
        for name in sorted(self.sensors):
            s = self.sensors[name]
            pad = s.get("math", {}).get("pad", {})
            p = pad.get("P", "")
            a = pad.get("A", "")
            d = pad.get("D", "")
            dm = s.get("math", {}).get("kernel", {}).get("type", "")
            if not dm:
                dm = s.get("decay_model", "")
                if isinstance(dm, dict):
                    dm = dm.get("type", "?")
            family = self._get_family(name)
            p_str = f"{p:+.2f}" if isinstance(p, (int, float)) else "  —  "
            a_str = f"{a:+.2f}" if isinstance(a, (int, float)) else "  —  "
            d_str = f"{d:+.2f}" if isinstance(d, (int, float)) else "  —  "
            lines.append(f"{name:<20} {dm:<15} {p_str} {a_str} {d_str}  {family}")
        return "\n".join(lines)

    def sensor(self, name: str) -> str:
        """Detail view of a single sensor."""
        s = self.sensors.get(name.lower())
        if not s:
            return f"Sensor '{name}' not found. Available: {', '.join(sorted(self.sensors))}"

        lines = [f"SENSOR: {name.upper()}", "=" * 50]

        for field in ["function", "signal_type", "authentic_output", "corrupted_output"]:
            val = s.get(field, "")
            if val:
                lines.append(f"  {field}: {val}")

        proto = s.get("response_protocol", {})
        if proto:
            lines.append("\n  Response Protocol:")
            for step in ["detect", "assess", "respond", "release"]:
                if step in proto:
                    lines.append(f"    {step}: {proto[step]}")

        math_cfg = s.get("math", {})
        if math_cfg:
            pad = math_cfg.get("pad", {})
            kernel = math_cfg.get("kernel", {}).get("type", "?")
            lam = math_cfg.get("lambda", "?")
            alpha = math_cfg.get("alpha", "?")
            lines.append(f"\n  Math:")
            lines.append(f"    kernel: {kernel}  lambda: {lam}  alpha: {alpha}")
            if pad:
                lines.append(f"    PAD: P={pad.get('P', 0):+.2f}  A={pad.get('A', 0):+.2f}  D={pad.get('D', 0):+.2f}")
            corrupted = math_cfg.get("corrupted_pad", {})
            if corrupted:
                lines.append(f"    corrupted PAD: P={corrupted.get('P', 0):+.2f}  "
                             f"A={corrupted.get('A', 0):+.2f}  D={corrupted.get('D', 0):+.2f}")
            couplings = math_cfg.get("couplings", [])
            if couplings:
                coup_str = ", ".join(f"{c['to']}(w={c['w']})" for c in couplings)
                lines.append(f"    couplings: {coup_str}")
            policy = math_cfg.get("policy", {})
            if policy:
                lines.append(f"    policy: role={policy.get('role', '?')}  "
                             f"max_cost={policy.get('max_action_cost', '?')}")

        bridge = s.get("defense_bridge", {})
        if bridge:
            lines.append(f"\n  Defense Bridge:")
            lines.append(f"    defense: {bridge.get('defense_id', '')} ({bridge.get('defense_name', '')})")
            lines.append(f"    shape: {bridge.get('shape', '')}")
            lines.append(f"    corrupted form: {bridge.get('corrupted_form', '')}")

        family = self._get_family(name)
        if family:
            lines.append(f"\n  Family: {family}")
        lines.append(f"  Source: {s.get('_path', '?')}")

        return "\n".join(lines)

    def list_overlays(self) -> str:
        """List all cultural overlays."""
        lines = [f"{'ID':<30} {'PAG Mode':<10} {'D-offset':>8}  Label"]
        lines.append("-" * 75)
        for o in self.overlays:
            lines.append(
                f"{o['culture_id']:<30} {o['PAG_default_mode']:<10} "
                f"{o['D_offset']:+.2f}     {o['label']}"
            )
        return "\n".join(lines)

    def overlay(self, culture_id: str) -> str:
        """Detail view of a cultural overlay with D-axis shifts per sensor."""
        ov = None
        for o in self.overlays:
            if o["culture_id"] == culture_id:
                ov = o
                break
        if not ov:
            ids = [o["culture_id"] for o in self.overlays]
            return f"Overlay '{culture_id}' not found. Available: {', '.join(ids)}"

        lines = [
            f"OVERLAY: {ov['label']}",
            "=" * 50,
            f"  {ov.get('description', '')}",
            f"\n  PAG default mode: {ov['PAG_default_mode']}",
            f"  Global D-offset: {ov['D_offset']:+.2f}",
            f"  Shame trigger: {ov.get('shame_trigger_radius', '?')}",
            f"  Anger threshold: {ov.get('anger_threshold', '?')}",
            f"  Trust radius: {ov.get('trust_radius', '?')}",
            f"  Grief expression: {ov.get('grief_expression', '?')}",
        ]

        overrides = ov.get("sensor_overrides", {})
        if overrides:
            lines.append("\n  Per-sensor D overrides:")
            for sname, override in sorted(overrides.items()):
                raw_d = self.sensors.get(sname, {}).get("math", {}).get("pad", {}).get("D", 0)
                d_off = override.get("D_offset", ov["D_offset"])
                eff = max(-1.0, min(1.0, raw_d + d_off))
                note = override.get("note", "")
                lines.append(f"    {sname:<15} D: {raw_d:+.2f} -> {eff:+.2f}  {note}")

        # Show all sensors with this overlay applied
        lines.append(f"\n  All sensor D-shifts (global offset {ov['D_offset']:+.2f}):")
        demo = ["anger", "fear", "shame", "trust", "peace", "compassion", "grief", "pride", "love", "curiosity"]
        for sname in demo:
            s = self.sensors.get(sname, {})
            pad = s.get("math", {}).get("pad", {})
            if not pad:
                continue
            raw_d = pad.get("D", 0)
            override = overrides.get(sname, {})
            d_off = override.get("D_offset", ov["D_offset"])
            eff = max(-1.0, min(1.0, raw_d + d_off))
            lines.append(f"    {sname:<15} D: {raw_d:+.2f} -> {eff:+.2f}")

        refs = ov.get("references", [])
        if refs:
            lines.append(f"\n  References: {', '.join(refs)}")

        return "\n".join(lines)

    def compare(self, name_a: str, name_b: str, culture_id: Optional[str] = None) -> str:
        """Side-by-side comparison of two sensors, optionally with cultural overlay."""
        a = self.sensors.get(name_a.lower())
        b = self.sensors.get(name_b.lower())
        if not a:
            return f"Sensor '{name_a}' not found."
        if not b:
            return f"Sensor '{name_b}' not found."

        ov = None
        if culture_id:
            for o in self.overlays:
                if o["culture_id"] == culture_id:
                    ov = o
                    break

        def _pad_str(s, sensor_name):
            pad = s.get("math", {}).get("pad", {})
            p, aa, d = pad.get("P", 0), pad.get("A", 0), pad.get("D", 0)
            if ov:
                override = ov.get("sensor_overrides", {}).get(sensor_name, {})
                d_off = override.get("D_offset", ov.get("D_offset", 0))
                d = max(-1.0, min(1.0, d + d_off))
            return f"P={p:+.2f}  A={aa:+.2f}  D={d:+.2f}"

        header = f"{'':20} {name_a.upper():<30} {name_b.upper():<30}"
        sep = "-" * 80
        lines = [header, sep]

        for field in ["function", "signal_type", "authentic_output", "corrupted_output"]:
            va = a.get(field, "—")[:28]
            vb = b.get(field, "—")[:28]
            lines.append(f"  {field:<18} {va:<30} {vb:<30}")

        ka = a.get("math", {}).get("kernel", {}).get("type", "?")
        kb = b.get("math", {}).get("kernel", {}).get("type", "?")
        lines.append(f"  {'decay':<18} {ka:<30} {kb:<30}")

        pa = _pad_str(a, name_a)
        pb = _pad_str(b, name_b)
        label = "PAD" + (f" ({ov['label']})" if ov else "")
        lines.append(f"  {label:<18} {pa:<30} {pb:<30}")

        fa = self._get_family(name_a)
        fb = self._get_family(name_b)
        lines.append(f"  {'family':<18} {fa:<30} {fb:<30}")

        return "\n".join(lines)

    def list_family(self, family_name: str) -> str:
        """List all sensors in a family."""
        members = self.families.get(family_name)
        if not members:
            return f"Family '{family_name}' not found. Available: {', '.join(sorted(self.families))}"

        lines = [f"Family: {family_name} ({len(members)} sensors)", "-" * 50]
        for name in sorted(members):
            s = self.sensors.get(name, {})
            pad = s.get("math", {}).get("pad", {})
            p = pad.get("P", "")
            a = pad.get("A", "")
            d = pad.get("D", "")
            dm = s.get("math", {}).get("kernel", {}).get("type", "?")
            p_str = f"P={p:+.2f}" if isinstance(p, (int, float)) else ""
            a_str = f"A={a:+.2f}" if isinstance(a, (int, float)) else ""
            d_str = f"D={d:+.2f}" if isinstance(d, (int, float)) else ""
            lines.append(f"  {name:<20} {dm:<15} {p_str} {a_str} {d_str}")
        return "\n".join(lines)

    def list_families(self) -> str:
        """List all sensor families."""
        lines = [f"{'Family':<20} {'Members':>8}  Sensors"]
        lines.append("-" * 70)
        for fname in sorted(self.families):
            members = self.families[fname]
            lines.append(f"{fname:<20} {len(members):>8}  {', '.join(sorted(members))}")
        return "\n".join(lines)

    def list_by_decay(self, decay_model: str) -> str:
        """List all sensors using a specific decay model."""
        matches = []
        for name, s in sorted(self.sensors.items()):
            kernel = s.get("math", {}).get("kernel", {}).get("type", "")
            dm = s.get("decay_model", "")
            if isinstance(dm, dict):
                dm = dm.get("type", "")
            if kernel == decay_model or dm == decay_model:
                matches.append(name)

        if not matches:
            return (f"No sensors with decay model '{decay_model}'. "
                    f"Available: exponential, cyclical, resonant, immortal, transformative")

        desc = self.decay_families.get(decay_model, {})
        glyph = desc.get("glyph", "")
        behavior = desc.get("behavior", "")

        lines = [f"Decay: {decay_model} {glyph}", f"  {behavior}", "-" * 50]
        for name in sorted(matches):
            lines.append(f"  {name}")
        lines.append(f"\n  Total: {len(matches)} sensors")
        return "\n".join(lines)

    def nearest_pad(self, p: float, a: float, d: float, top_n: int = 5) -> str:
        """Find sensors nearest to given PAD coordinates."""
        distances = []
        for name, s in self.sensors.items():
            pad = s.get("math", {}).get("pad", {})
            if not pad:
                continue
            sp, sa, sd = pad.get("P", 0), pad.get("A", 0), pad.get("D", 0)
            dist = math.sqrt((p - sp) ** 2 + (a - sa) ** 2 + (d - sd) ** 2)
            distances.append((dist, name, sp, sa, sd))

        distances.sort()
        lines = [f"Nearest sensors to PAD ({p:+.2f}, {a:+.2f}, {d:+.2f}):", "-" * 50]
        for dist, name, sp, sa, sd in distances[:top_n]:
            lines.append(f"  {dist:.3f}  {name:<20} P={sp:+.2f} A={sa:+.2f} D={sd:+.2f}")
        return "\n".join(lines)

    def graph(self, name: str, depth: int = 1) -> str:
        """Walk the resonance graph from a sensor."""
        if name.lower() not in self.sensors:
            return f"Sensor '{name}' not found."

        visited = set()
        frontier = [name.lower()]
        all_edges = []

        for d in range(depth):
            next_frontier = []
            for sname in frontier:
                if sname in visited:
                    continue
                visited.add(sname)
                s = self.sensors.get(sname, {})
                couplings = s.get("math", {}).get("couplings", [])
                for c in couplings:
                    target = c["to"]
                    weight = c["w"]
                    all_edges.append((sname, target, weight, d + 1))
                    if target not in visited:
                        next_frontier.append(target)
            frontier = next_frontier

        lines = [f"Resonance graph from {name.upper()} (depth={depth}):", "-" * 50]
        for src, tgt, w, d in all_edges:
            indent = "  " * d
            arrow = "→" if w > 0 else "⇥"
            lines.append(f"{indent}{src} {arrow} {tgt} (w={w:+.2f})")

        lines.append(f"\n  Nodes visited: {len(visited)}")
        lines.append(f"  Edges: {len(all_edges)}")
        return "\n".join(lines)

    def schema(self) -> str:
        """Show the canonical sensor JSON schema."""
        return (
            "Canonical Sensor JSON Schema (Pattern A)\n"
            "=========================================\n\n"
            '  "sensor":           string   — unique identifier\n'
            '  "function":         string   — what it detects\n'
            '  "signal_type":      string   — input type (kebab-case)\n'
            '  "authentic_output": string   — healthy signal\n'
            '  "corrupted_output": string   — distorted signal\n'
            '  "response_protocol": {\n'
            '    "detect":  string\n'
            '    "assess":  string\n'
            '    "respond": string\n'
            '    "release": string\n'
            '  }\n'
            '  "decay_model":      exponential|cyclical|resonant|immortal|transformative\n'
            '  "decay":            string   — canonical decay family\n'
            '  "energy":           adds|conserves|depletes|transforms\n'
            '  "math": {\n'
            '    "lambda":  float  — decay rate\n'
            '    "alpha":   float  — input gain\n'
            '    "kernel":  {"type": string}  — decay kernel\n'
            '    "pad":     {"P": float, "A": float, "D": float}\n'
            '    "corrupted_pad": {"P": float, "A": float, "D": float}  (optional)\n'
            '    "couplings": [{"to": string, "w": float}]\n'
            '    "policy":  {"role": string, "max_action_cost": float}\n'
            '  }\n'
            '  "defense_bridge": {  (optional)\n'
            '    "defense_id": string, "shape": string, "corrupted_form": string\n'
            '  }\n'
            '  "tags":             [string]\n'
        )

    # ── Helpers ──────────────────────────────────────────────────────────

    def _get_family(self, sensor_name: str) -> str:
        for fname, members in self.families.items():
            if sensor_name in members:
                return fname
        return ""


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ch = ExploreChannel()
    args = sys.argv[1:]

    if not args or args[0] == "help":
        print(ch.help())
    elif args[0] == "sensors":
        print(ch.list_sensors())
    elif args[0] == "sensor" and len(args) > 1:
        print(ch.sensor(args[1]))
    elif args[0] == "overlays":
        print(ch.list_overlays())
    elif args[0] == "overlay" and len(args) > 1:
        print(ch.overlay(args[1]))
    elif args[0] == "compare" and len(args) >= 3:
        overlay = args[3] if len(args) > 3 else None
        print(ch.compare(args[1], args[2], overlay))
    elif args[0] == "family" and len(args) > 1:
        print(ch.list_family(args[1]))
    elif args[0] == "families":
        print(ch.list_families())
    elif args[0] == "decay" and len(args) > 1:
        print(ch.list_by_decay(args[1]))
    elif args[0] == "pad" and len(args) >= 4:
        print(ch.nearest_pad(float(args[1]), float(args[2]), float(args[3])))
    elif args[0] == "graph" and len(args) > 1:
        depth = 1
        for a in args[2:]:
            if a.startswith("depth="):
                depth = int(a.split("=")[1])
        print(ch.graph(args[1], depth))
    elif args[0] == "schema":
        print(ch.schema())
    else:
        print(ch.help())


if __name__ == "__main__":
    main()
