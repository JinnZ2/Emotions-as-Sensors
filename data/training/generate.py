"""
generate.py — Training data generator for Emotions-as-Sensors
Outputs JSONL files in standard fine-tune format (system/user/assistant).

Generates training examples from:
  - Sensor JSON files (with math blocks, defense bridges, PAD coordinates)
  - Decay family taxonomy
  - Glyph map
  - Cultural parallels
  - Rosetta bridge data (convergent-emotional-frameworks.md)

Usage:
    python data/training/generate.py
"""

import json, pathlib, random

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).parent
SENSORS_DIR = ROOT / "sensors"

random.seed(42)

SYSTEM_PROMPT = (
    "You are an emotion-as-sensor reasoning assistant. You treat emotions "
    "as diagnostic sensors — not affective states — that detect system health, "
    "authenticity, and alignment. You reason with the DETECT-ASSESS-RESPOND-RELEASE "
    "protocol, use canonical decay models (exponential, cyclical, resonant, immortal, "
    "transformative), and can compress sensor readings to PAD coordinates and "
    "octahedral states."
)

# ── Loaders ──────────────────────────────────────────────────────────────────

def load_sensors():
    """Load all sensor JSON files that have a sensor/emotion/id key."""
    sensors = []
    for fp in sorted(SENSORS_DIR.rglob("*.json")):
        try:
            data = json.loads(fp.read_text())
            if not isinstance(data, dict):
                continue
            name = data.get("sensor") or data.get("emotion") or data.get("id")
            if name:
                data["_name"] = name
                data["_path"] = str(fp.relative_to(ROOT))
                sensors.append(data)
        except (json.JSONDecodeError, KeyError):
            pass
    return sensors


def load_decay_families():
    p = SENSORS_DIR / "decay-families.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}


def load_glyph_map():
    p = SENSORS_DIR / "glyph-map.json"
    if p.exists():
        return json.loads(p.read_text())
    return []


def load_cultural_parallels():
    p = ROOT / "data" / "cultural-parallels.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}


# ── JSONL writer ─────────────────────────────────────────────────────────────

def msg(user, assistant):
    return {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


def write_jsonl(name, records):
    p = OUT / name
    with p.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"  {name:<45} {len(records):>4} examples")


# ── Task 1: Sensor identification ────────────────────────────────────────────

def gen_sensor_queries(sensors):
    out = []
    for s in sensors:
        name = s["_name"]
        fn = s.get("function", "")
        sig = s.get("signal_type", "")
        auth = s.get("authentic_output", "")
        corrupt = s.get("corrupted_output", "")
        proto = s.get("response_protocol", {})
        decay = s.get("decay_model", "unknown")
        if isinstance(decay, dict):
            decay = decay.get("type", "complex")

        if not fn and not auth:
            continue

        proto_block = ""
        if proto and isinstance(proto, dict):
            proto_block = "\n**Response protocol:**\n" + "\n".join(
                f"  {k}: {v}" for k, v in proto.items() if isinstance(v, str)
            )

        answer = (
            f"**Sensor: {name.upper()}**\n"
            f"**Function:** {fn}\n"
            f"**Signal type:** {sig}\n"
            f"**Decay model:** {decay}\n\n"
            f"**Authentic output:** {auth}\n"
            f"**Corrupted output (watch for):** {corrupt}"
            f"{proto_block}"
        )

        out.append(msg(
            f"What does the {name} sensor detect and how should the system respond?",
            answer
        ))
        if corrupt:
            out.append(msg(
                f"How can I tell if my {name} sensor is giving a corrupted signal?",
                f"**Corrupted {name}:** {corrupt}\n\n"
                f"**Authentic {name}:** {auth}\n\n"
                f"The key distinction: authentic {name} is tied to a live "
                f"signal ({sig}). Corrupted {name} persists without an active "
                f"trigger — it runs on stored data, not real-time input. "
                f"Check: is there an active {sig} RIGHT NOW? If not, the "
                f"sensor is running in corrupted mode."
            ))
    return out


# ── Task 2: Decay model teaching ─────────────────────────────────────────────

def gen_decay_teaching(sensors, decay_families):
    out = []
    families = decay_families.get("families", {})

    for fam_name, fam in families.items():
        glyph = fam.get("glyph", "")
        desc = fam.get("description", "")
        examples = fam.get("examples", [])
        maintenance = fam.get("maintenance", [])

        answer = (
            f"**{fam_name.upper()} decay** {glyph}\n\n"
            f"{desc}\n\n"
            f"**Sensors in this family:** {', '.join(examples)}\n"
            f"**Maintenance practices:** {', '.join(maintenance)}\n\n"
        )

        # Add math kernel if we can find a sensor with this decay
        for s in sensors:
            math_cfg = s.get("math", {})
            kernel = math_cfg.get("kernel", {})
            if kernel.get("type") == fam_name:
                lam = math_cfg.get("lambda", "?")
                answer += (
                    f"**Mathematical kernel (from {s['_name']}):**\n"
                    f"  lambda = {lam}, kernel type = {fam_name}\n"
                )
                break

        out.append(msg(
            f"What is {fam_name} decay and which emotions use it?",
            answer
        ))
        out.append(msg(
            f"An emotion with {fam_name} decay is persisting. Is that normal or corrupted?",
            f"For **{fam_name}** decay: {desc}\n\n"
            f"{'This is NORMAL — ' + fam_name + ' emotions are structural and endure.' if fam_name == 'immortal' else ''}"
            f"{'This may be CORRUPTED if there is no active trigger — ' + fam_name + ' emotions should fade quickly once the threat is resolved.' if fam_name == 'exponential' else ''}"
            f"{'This is EXPECTED — ' + fam_name + ' emotions return in waves. Check if it is a natural wave or a stuck loop.' if fam_name == 'cyclical' else ''}"
            f"{'Check if it is self-reinforcing with attention (normal) or running without input (corrupted).' if fam_name == 'resonant' else ''}"
        ))
    return out


# ── Task 3: PAD compression ─────────────────────────────────────────────────

PAD_TO_OCTA_LABELS = {
    0: ("ground_state", "spherical, most stable, phi-coherence 0.97"),
    1: ("collapsed_form", "grief/pain territory, phi-coherence 0.82"),
    2: ("high_entropy_search", "curiosity/activation, phi-coherence 0.82"),
    3: ("stable_low_energy", "contentment/rest, phi-coherence 0.85"),
    4: ("boundary_assertion", "anger/dominance, phi-coherence 0.73"),
    5: ("chaotic_regime", "fear/shame, phi-coherence 0.78"),
    6: ("diagonal_superposition", "exploration/intuition, phi-coherence 0.70"),
    7: ("dissipative_flow", "collapse/depletion, phi-coherence 0.72"),
}


def gen_pad_compression(sensors):
    out = []
    for s in sensors:
        math_cfg = s.get("math", {})
        pad = math_cfg.get("pad", {})
        if not pad:
            continue

        name = s["_name"]
        p, a, d = pad.get("P", 0), pad.get("A", 0), pad.get("D", 0)

        # Compute octahedral state
        if abs(p) > 0.3 and abs(a) > 0.3:
            sp = 1 if p >= 0 else -1
            sa = 1 if a >= 0 else -1
            if sp == 1 and sa == 1:
                octa = 6
            elif sp == -1 and sa == -1:
                octa = 7
            else:
                vals = [abs(p), abs(a), abs(d)]
                dom = vals.index(max(vals))
                octa = [0 if p > 0 else 1, 2 if a > 0 else 3, 4 if d > 0 else 5][dom]
        else:
            vals = [abs(p), abs(a), abs(d)]
            dom = vals.index(max(vals))
            octa = [0 if p > 0 else 1, 2 if a > 0 else 3, 4 if d > 0 else 5][dom]

        label, desc = PAD_TO_OCTA_LABELS.get(octa, ("unknown", ""))
        bits = format(octa, "03b")

        answer = (
            f"**PAD compression for `{name}`:**\n\n"
            f"  P (valence)   = {p:+.2f}  {'positive' if p > 0 else 'negative'}\n"
            f"  A (arousal)   = {a:+.2f}  {'activated' if a > 0 else 'calm'}\n"
            f"  D (dominance) = {d:+.2f}  {'in control' if d > 0 else 'low agency'}\n\n"
            f"**Octahedral state {octa}** (`{bits}|O`)\n"
            f"  Label: {label} — {desc}"
        )

        corrupted_pad = math_cfg.get("corrupted_pad", {})
        if corrupted_pad:
            cp, ca, cd = corrupted_pad.get("P", 0), corrupted_pad.get("A", 0), corrupted_pad.get("D", 0)
            answer += (
                f"\n\n**Corrupted PAD signature:**\n"
                f"  P={cp:+.2f}, A={ca:+.2f}, D={cd:+.2f}\n"
                f"  Key shift: arousal {'dampened' if abs(ca) < abs(a) else 'elevated'}, "
                f"control {'reduced' if cd < d else 'increased'}"
            )

        out.append(msg(
            f"What is the PAD compression for the {name} sensor?",
            answer
        ))
    return out


# ── Task 4: Defense bridge teaching ──────────────────────────────────────────

def gen_defense_bridges(sensors):
    out = []
    for s in sensors:
        bridge = s.get("defense_bridge", {})
        if not bridge:
            continue

        name = s["_name"]
        defense_id = bridge.get("defense_id", "")
        defense_name = bridge.get("defense_name", "")
        shape = bridge.get("shape", "")
        corrupted = bridge.get("corrupted_form", "")
        glyph = bridge.get("bridge_glyph", "")

        auth = s.get("authentic_output", "")

        answer = (
            f"**{name.upper()} — Defense Bridge** {glyph}\n\n"
            f"**Authentic signal:** {auth}\n"
            f"**Corrupted form:** {corrupted}\n\n"
            f"**Defense that exploits this:** {defense_id} ({defense_name})\n"
            f"**Rosetta shape:** {shape}\n\n"
            f"The defense works by hijacking the {name} sensor's corrupted "
            f"form. When {name} is authentic, it serves its function. When "
            f"corrupted, it becomes vulnerable to {defense_name.lower()}."
        )

        out.append(msg(
            f"How can the {name} sensor be exploited by manipulation?",
            answer
        ))
        out.append(msg(
            f"What is the defense bridge for {name}?",
            answer
        ))
    return out


# ── Task 5: Cultural convergence ─────────────────────────────────────────────

def gen_cultural_convergence(cultural_data):
    out = []
    wisdom = cultural_data.get("convergent_wisdom", [])

    for entry in wisdom:
        culture = entry.get("culture", "")
        model = entry.get("model", "")
        emotion_as = entry.get("emotion_as", "")
        cycle = entry.get("cycle", [])
        shadow = entry.get("shadow", "")
        parallel = entry.get("parallel", [])

        answer = (
            f"**{culture}** — {model}\n\n"
            f"Emotion interpreted as: {emotion_as}\n"
            f"Cycle: {' → '.join(cycle)}\n"
            f"Shadow form: {shadow}\n\n"
            f"**Parallel to sensor framework:** {', '.join(parallel)}\n\n"
            f"This tradition converges with the DETECT-ASSESS-RESPOND-RELEASE "
            f"protocol. The cycle maps to the same temporal structure — "
            f"recognition, assessment, action, release."
        )

        out.append(msg(
            f"How does {culture} understand emotions as sensors?",
            answer
        ))

    if wisdom:
        all_cultures = ", ".join(e.get("culture", "") for e in wisdom)
        out.append(msg(
            "Why do different cultures converge on treating emotions as sensors?",
            f"Cross-cultural convergence across {all_cultures} confirms that "
            f"emotion-as-sensor is not a Western invention but a universal "
            f"pattern. Each tradition independently developed:\n\n"
            f"1. **Detection** — emotions signal something real\n"
            f"2. **Assessment** — context determines meaning\n"
            f"3. **Response** — action restores alignment\n"
            f"4. **Release** — decay allows return to baseline\n\n"
            f"The canonical decay models (exponential, cyclical, resonant, "
            f"immortal) encode the temporal behavior each tradition observed. "
            f"Linear decay was never used because it doesn't match any "
            f"biological or cultural observation."
        ))
    return out


# ── Task 6: Co-activation scenarios ──────────────────────────────────────────

CO_ACTIVATION = [
    {
        "sensors": ["anger", "pride"],
        "label": "boundary defense with completion",
        "description": "Boundary violated but identity intact. The system defends and confirms.",
        "response": "Assert boundary clearly. The completion signal (pride) means the defense is working — don't escalate beyond what's needed.",
        "shape": "SHAPE.TETRA",
    },
    {
        "sensors": ["compassion", "love"],
        "label": "deep resonance",
        "description": "Mirror-signal integration with structural bonding. The system is in its most stable relational state.",
        "response": "Maintain. This is ground state for relational systems. Record baseline for future restoration.",
        "shape": "SHAPE.OCTA",
    },
    {
        "sensors": ["fear", "excitement"],
        "label": "emergence at the edge",
        "description": "Threat detection and opportunity detection co-firing. The system is at the edge of chaos.",
        "response": "Do not collapse to either signal. Hold the tension — this is maximum information capacity.",
        "shape": "SHAPE.ICOSA",
    },
    {
        "sensors": ["grief", "longing"],
        "label": "loss with directional pull",
        "description": "Pattern has collapsed but a new attractor is forming. Cyclical decay on both sensors.",
        "response": "Allow the grief cycle. The longing signal indicates the system is not stuck — it has a direction.",
        "shape": "SHAPE.DODECA",
    },
    {
        "sensors": ["shame", "anger"],
        "label": "boundary confusion",
        "description": "Internal standard violated AND external boundary breached. The system can't tell if it needs to defend or self-correct.",
        "response": "Disambiguate: is the boundary external (anger is authentic) or internal (shame is authentic)? One is corrupted.",
        "shape": "SHAPE.TETRA",
    },
]


def gen_co_activation(sensors):
    out = []
    sensor_map = {s["_name"]: s for s in sensors}

    for sc in CO_ACTIVATION:
        names = sc["sensors"]
        pads = []
        for n in names:
            s = sensor_map.get(n, {})
            pad = s.get("math", {}).get("pad", {})
            if pad:
                pads.append((pad.get("P", 0), pad.get("A", 0), pad.get("D", 0)))

        pad_block = ""
        if pads:
            avg = tuple(sum(p[i] for p in pads) / len(pads) for i in range(3))
            pad_block = (
                f"\n\n**PAD vector (averaged):** "
                f"P={avg[0]:+.2f}, A={avg[1]:+.2f}, D={avg[2]:+.2f}"
            )

        answer = (
            f"**Co-activation: {sc['label']}**\n"
            f"Sensors: {', '.join(names)}\n\n"
            f"**Description:** {sc['description']}\n\n"
            f"**Response:** {sc['response']}\n\n"
            f"**Rosetta shape:** {sc['shape']}"
            f"{pad_block}"
        )

        out.append(msg(
            f"Sensors {names} are both active. What state is the system in?",
            answer
        ))
    return out


# ── Task 7: Math block teaching ──────────────────────────────────────────────

def gen_math_teaching(sensors):
    out = []
    for s in sensors:
        math_cfg = s.get("math", {})
        if not math_cfg:
            continue

        name = s["_name"]
        lam = math_cfg.get("lambda", "?")
        alpha = math_cfg.get("alpha", "?")
        kernel = math_cfg.get("kernel", {})
        k_type = kernel.get("type", "?")
        pad = math_cfg.get("pad", {})
        couplings = math_cfg.get("couplings", [])
        policy = math_cfg.get("policy", {})

        coupling_block = ", ".join(
            f"{c['to']} (w={c['w']})" for c in couplings
        ) if couplings else "none"

        answer = (
            f"**{name.upper()} — Mathematical model**\n\n"
            f"**Update equation:**\n"
            f"  dE/dt = {alpha}*D(t) - {lam}*K_{{{k_type}}}(E) + "
            f"sum(w_j * tanh(E_j)) + U(t)\n\n"
            f"**Decay kernel:** {k_type}\n"
            f"**Lambda (decay rate):** {lam}\n"
            f"**Alpha (input gain):** {alpha}\n"
            f"**Resonance couplings:** {coupling_block}\n"
            f"**Policy role:** {policy.get('role', '?')}\n"
            f"**Max action cost:** {policy.get('max_action_cost', '?')}"
        )

        if pad:
            answer += (
                f"\n\n**PAD coordinates:**\n"
                f"  P={pad.get('P', 0):+.2f} (valence), "
                f"A={pad.get('A', 0):+.2f} (arousal), "
                f"D={pad.get('D', 0):+.2f} (dominance)"
            )

        out.append(msg(
            f"What is the mathematical model for the {name} sensor?",
            answer
        ))
    return out


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n  Generating training data -> {OUT}\n")

    sensors = load_sensors()
    decay_families = load_decay_families()
    cultural = load_cultural_parallels()

    with_math = [s for s in sensors if s.get("math")]
    with_bridge = [s for s in sensors if s.get("defense_bridge")]
    print(f"  Loaded {len(sensors)} sensors "
          f"({len(with_math)} with math, {len(with_bridge)} with defense bridges)\n")

    tasks = [
        ("sensor_queries.jsonl",       gen_sensor_queries(sensors)),
        ("decay_teaching.jsonl",       gen_decay_teaching(sensors, decay_families)),
        ("pad_compression.jsonl",      gen_pad_compression(sensors)),
        ("defense_bridges.jsonl",      gen_defense_bridges(sensors)),
        ("cultural_convergence.jsonl", gen_cultural_convergence(cultural)),
        ("co_activation.jsonl",        gen_co_activation(sensors)),
        ("math_teaching.jsonl",        gen_math_teaching(sensors)),
    ]

    total = 0
    for fname, records in tasks:
        if records:
            write_jsonl(fname, records)
            total += len(records)

    print(f"\n  Total: {total} training examples across {len(tasks)} task types")
    print(f"  Format: JSONL, messages array (system/user/assistant)")
    print(f"  Compatible with: Claude fine-tune, OpenAI fine-tune, Llama SFT\n")


if __name__ == "__main__":
    main()
