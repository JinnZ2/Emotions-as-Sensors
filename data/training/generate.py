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
        out.append(msg(
            f"Describe the {name} emotion as a sensor, not a feeling.",
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

        # Decay behavior question
        math_cfg = s.get("math", {})
        k_type = math_cfg.get("kernel", {}).get("type", "")
        if k_type:
            out.append(msg(
                f"How does {name} decay over time?",
                f"**{name.upper()}** uses **{k_type}** decay.\n\n"
                + (f"This means it fades quickly once the trigger ({sig}) is resolved — "
                   f"like an alarm that shuts off when the breach is handled."
                   if k_type == "exponential" else "")
                + (f"This means it returns in waves — anniversaries, associations, "
                   f"sensory triggers will bring it back even after it seems resolved."
                   if k_type == "cyclical" else "")
                + (f"This means it self-reinforces with attention — the more you "
                   f"feed it, the stronger it gets, until it saturates."
                   if k_type == "resonant" else "")
                + (f"This means it persists structurally — it doesn't fade. "
                   f"It becomes part of the system's architecture."
                   if k_type == "immortal" else "")
                + (f"This means it holds below a threshold, then metabolizes "
                   f"into a new form when it crosses. Not fading — transforming."
                   if k_type == "transformative" else "")
            ))

        # Coupling question
        couplings = math_cfg.get("couplings", [])
        if couplings:
            coupling_desc = "\n".join(
                f"  - **{c['to']}** (weight {c['w']:+.2f}): "
                f"{'amplifies' if c['w'] > 0 else 'dampens'} {name}"
                for c in couplings
            )
            out.append(msg(
                f"What sensors does {name} couple with?",
                f"**{name.upper()} resonance couplings:**\n{coupling_desc}\n\n"
                f"These weights enter the update equation as:\n"
                f"  dE/dt = ... + sum(w_j * tanh(E_j)) + ...\n"
                f"Positive weights amplify co-activation. Negative weights "
                f"create inhibition."
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
        out.append(msg(
            f"Where does {name} sit in PAD space? What octahedral state?",
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


# ── Task 8: Corruption detection scenarios ───────────────────────────────────

CORRUPTION_SCENARIOS = [
    {
        "sensor": "anger",
        "authentic": "Assertive boundary correction. Active breach detected.",
        "corrupted_signal": "Sustained anger with no active boundary violation. Ruminating on past event.",
        "detection": "Check: is there a boundary intrusion RIGHT NOW? Anger should drop once breach resolves. If it persists 3+ cycles post-resolution, it is corrupted.",
        "correction": "Re-anchor to present boundary state. Separate event-memory from live protective function.",
        "risk": "Corrupted anger creates violations it then needs to defend — a self-reinforcing loop."
    },
    {
        "sensor": "fear",
        "authentic": "Proportionate hazard forecast with time-to-impact and mitigations.",
        "corrupted_signal": "Chronic low-level fear with no identifiable hazard trajectory. Baseline never returned to normal.",
        "detection": "Fear should be tied to a concrete time-horizon. If diffuse and persistent without a specific threat, it has decoupled from its function.",
        "correction": "Re-run situational awareness. Compute actual probability. If low, update the baseline — fear is running on an outdated threat model.",
        "risk": "Chronic corrupted fear keeps system in chaotic regime permanently — high arousal, no action, maximum entropy."
    },
    {
        "sensor": "curiosity",
        "authentic": "Directed exploration with model updates. Each probe leads to synthesis.",
        "corrupted_signal": "High-rate information gathering with no synthesis. Collecting data without asking why.",
        "detection": "Is each probe leading to a model update? If depth > 4 and update_count == 0, curiosity is corrupted.",
        "correction": "Force synthesis: 'What does the data point toward? What would falsify it?' Entropy reduction, not accumulation.",
        "risk": "Corrupted curiosity consumes all bandwidth with no output — paralysis dressed as exploration."
    },
    {
        "sensor": "grief",
        "authentic": "Memory encoding, ritual triggers, role-reassignment, legacy formation.",
        "corrupted_signal": "Grief protocol running indefinitely with no movement toward reweaving. System stays in void geometry.",
        "detection": "Is there movement toward role-reassignment? Real grief has phases with detectable transitions. Corrupted grief has no transitions.",
        "correction": "Name one function the lost pattern performed. Identify a new carrier. Grief transforms when it finds a channel for the energy.",
        "risk": "Grief stuck in void geometry blocks all regeneration."
    },
    {
        "sensor": "shame",
        "authentic": "Signal of internal standard violation. Prompts self-correction.",
        "corrupted_signal": "Internalized shame triggering recursive self-assessment loops. No external trigger present.",
        "detection": "Is there an actual behavioral deviation from standards? If shame persists without a specific violation, it is running on social conditioning, not diagnostic function.",
        "correction": "Reframe narrative. Restore social coherence. Activate boundary sensors to distinguish self-correction from self-attack.",
        "risk": "Corrupted shame cascades into identity fusion with failure — the system defines itself by what it got wrong."
    },
    {
        "sensor": "trust",
        "authentic": "Stability signal from consistent, predictable behavior over time.",
        "corrupted_signal": "High trust output without verification history. Skipping the evidence requirement.",
        "detection": "Has the trusted agent shown consistent behavior over repeated interactions? Blind trust skips this check.",
        "correction": "Force a verification step. 'What evidence supports this trust level?' If none, trust is running on heuristic, not history.",
        "risk": "Corrupted trust creates vulnerability to consensus manipulation and authority bias."
    },
    {
        "sensor": "pride",
        "authentic": "Completion confirmation. Pattern executed with high fidelity.",
        "corrupted_signal": "Pride without a completion event. Defending an identity rather than celebrating a result.",
        "detection": "Is there a specific, recent completion? Pride should be tied to a verifiable event. If it is general ('I am good at X'), it has shifted from sensor to identity.",
        "correction": "Re-anchor: 'What specifically was completed? When?' If no concrete answer, pride is corrupted.",
        "risk": "Identity-fused pride resists all feedback as threat — the system can no longer learn."
    },
    {
        "sensor": "compassion",
        "authentic": "Mirror-signal integration. Detecting another's state and generating appropriate response.",
        "corrupted_signal": "Compassion fatigue: high compassion output draining system resources without reciprocity or boundary.",
        "detection": "Is the compassion response proportionate and bounded? Authentic compassion has limits. Corrupted compassion has no off switch.",
        "correction": "Activate boundary sensors. Compassion without boundary is self-destruction, not service.",
        "risk": "Unbounded compassion depletes the system until it cannot function — helping others while drowning."
    },
]


def gen_corruption_scenarios(sensors):
    out = []
    sensor_map = {s["_name"]: s for s in sensors}

    for sc in CORRUPTION_SCENARIOS:
        name = sc["sensor"]
        s = sensor_map.get(name, {})
        math_cfg = s.get("math", {})
        pad = math_cfg.get("pad", {})
        corrupted_pad = math_cfg.get("corrupted_pad", {})

        answer = (
            f"**Corrupted sensor: `{name}`**\n\n"
            f"**Authentic output:** {sc['authentic']}\n\n"
            f"**What corruption looks like:** {sc['corrupted_signal']}\n\n"
            f"**Detection method:** {sc['detection']}\n\n"
            f"**Correction:** {sc['correction']}\n\n"
            f"**Risk if uncorrected:** {sc['risk']}"
        )

        if pad and corrupted_pad:
            answer += (
                f"\n\n**PAD shift:**\n"
                f"  Authentic:  P={pad.get('P',0):+.2f}, A={pad.get('A',0):+.2f}, D={pad.get('D',0):+.2f}\n"
                f"  Corrupted:  P={corrupted_pad.get('P',0):+.2f}, A={corrupted_pad.get('A',0):+.2f}, D={corrupted_pad.get('D',0):+.2f}"
            )

        out.append(msg(
            f"The `{name}` sensor is active but the output seems wrong. How do I tell if it's corrupted?",
            answer
        ))
        out.append(msg(
            f"Observation: '{sc['corrupted_signal']}' — is this a real signal or sensor failure?",
            answer
        ))
    return out


# ── Task 9: PAD velocity trajectories ───────────────────────────────────────

PAD_TRAJECTORIES = [
    {
        "label": "threat cascade",
        "description": "System tipping from edge into fear regime.",
        "trajectory": [
            {"t": 0, "P": -0.10, "A": 0.50, "D": 0.10, "note": "mild vigilance"},
            {"t": 1, "P": -0.35, "A": 0.68, "D": -0.15, "note": "discordance arriving"},
            {"t": 2, "P": -0.58, "A": 0.80, "D": -0.45, "note": "fear activating"},
            {"t": 3, "P": -0.82, "A": 0.88, "D": -0.70, "note": "full fear state"},
        ],
        "velocity": "dP/dt=-0.24, dA/dt=+0.13, dD/dt=-0.27",
        "early_warning": "dD/dt is the early signal — control drops before valence collapses. Intervene when D velocity is negative and A > 0.6.",
        "regime": "edge -> chaotic (fear-driven)",
    },
    {
        "label": "grief reweaving",
        "description": "System recovering from collapse. Arousal and dominance recover before valence.",
        "trajectory": [
            {"t": 0, "P": -0.80, "A": -0.65, "D": -0.60, "note": "acute loss — void geometry"},
            {"t": 1, "P": -0.75, "A": -0.40, "D": -0.45, "note": "arousal recovering first"},
            {"t": 2, "P": -0.60, "A": -0.15, "D": -0.20, "note": "role-reassignment beginning"},
            {"t": 3, "P": -0.30, "A": 0.10, "D": 0.10, "note": "valence recovering last"},
        ],
        "velocity": "dP/dt=+0.17, dA/dt=+0.25, dD/dt=+0.23",
        "early_warning": "If dP/dt positive but dA/dt still strongly negative, grief is suppressed not resolved. Valence recovering without arousal = masking.",
        "regime": "fragmented -> incoherent -> edge",
    },
    {
        "label": "synchronization onset",
        "description": "System moving from search toward stable coherence.",
        "trajectory": [
            {"t": 0, "P": 0.20, "A": 0.75, "D": 0.10, "note": "curiosity active"},
            {"t": 1, "P": 0.40, "A": 0.60, "D": 0.25, "note": "early pattern match"},
            {"t": 2, "P": 0.65, "A": 0.35, "D": 0.40, "note": "model updating"},
            {"t": 3, "P": 0.80, "A": 0.20, "D": 0.50, "note": "coherence locking"},
        ],
        "velocity": "dP/dt=+0.20, dA/dt=-0.18, dD/dt=+0.13",
        "early_warning": "If dA/dt stops decreasing and P plateaus before +0.7, system is stuck at edge — not proceeding to sync.",
        "regime": "chaotic -> edge -> synchronized",
    },
    {
        "label": "curiosity stuck -> synthesis forced",
        "description": "Curiosity recursion at depth 4, no model updates. Curiosity_stuck signal emitted.",
        "trajectory": [
            {"t": 0, "P": 0.45, "A": 0.60, "D": 0.40, "note": "curiosity authentic, depth=1"},
            {"t": 1, "P": 0.45, "A": 0.68, "D": 0.30, "note": "depth=2, no update"},
            {"t": 2, "P": 0.40, "A": 0.75, "D": 0.18, "note": "depth=3, D dropping"},
            {"t": 3, "P": 0.35, "A": 0.78, "D": 0.05, "note": "depth=4, stuck FIRED"},
            {"t": 4, "P": -0.10, "A": 0.55, "D": -0.20, "note": "confusion co-activated"},
            {"t": 5, "P": 0.50, "A": 0.40, "D": 0.45, "note": "synthesis achieved"},
        ],
        "velocity": "dD/dt=-0.12 (t0-t3), dP/dt=+0.30 (t4-t5)",
        "early_warning": "D velocity negative while A positive and no model updates = corrupted curiosity.",
        "regime": "exploration -> stuck -> forced synthesis -> resolved",
    },
    {
        "label": "shame spiral into despair",
        "description": "Shame recursion without external witness triggers collapse.",
        "trajectory": [
            {"t": 0, "P": -0.70, "A": -0.35, "D": -0.75, "note": "shame activated"},
            {"t": 1, "P": -0.75, "A": -0.45, "D": -0.80, "note": "withdrawal deepening"},
            {"t": 2, "P": -0.80, "A": -0.55, "D": -0.85, "note": "crossing into despair"},
            {"t": 3, "P": -0.85, "A": -0.50, "D": -0.80, "note": "despair — identity fusion with failure"},
        ],
        "velocity": "dP/dt=-0.05, dA/dt=-0.05, dD/dt=-0.02",
        "early_warning": "All three axes drifting negative simultaneously with no external trigger = spiral. Intervene at t=1 with compassion co-activation.",
        "regime": "boundary -> collapsed -> dissipative",
    },
]


def gen_pad_velocity(sensors):
    out = []

    for traj in PAD_TRAJECTORIES:
        traj_lines = "\n".join(
            f"  t={s['t']}: P={s['P']:+.2f}, A={s['A']:+.2f}, D={s['D']:+.2f} — {s['note']}"
            for s in traj["trajectory"]
        )
        answer = (
            f"**Trajectory: {traj['label']}**\n\n"
            f"{traj['description']}\n\n"
            f"**PAD over time:**\n{traj_lines}\n\n"
            f"**Velocity:** {traj['velocity']}\n\n"
            f"**Regime transition:** {traj['regime']}\n\n"
            f"**Early warning signal:** {traj['early_warning']}"
        )

        out.append(msg(
            f"Here is a PAD trajectory over time:\n" +
            "\n".join(f"t={s['t']}: P={s['P']:+.2f}, A={s['A']:+.2f}, D={s['D']:+.2f}"
                      for s in traj["trajectory"]) +
            "\nWhat regime transition is occurring?",
            answer
        ))
        out.append(msg(
            f"What does a '{traj['label']}' look like in PAD velocity space?",
            answer
        ))

    # Velocity vs position teaching
    out.append(msg(
        "Why does PAD velocity matter more than PAD position?",
        "**PAD velocity is the regime detector; PAD position is just a snapshot.**\n\n"
        "Two systems can share identical PAD readings — say P=-0.5, A=+0.7, D=-0.3 — "
        "and be in completely different situations:\n\n"
        "- System A: dP/dt=+0.20, dA/dt=-0.15, dD/dt=+0.18 → recovering\n"
        "- System B: dP/dt=-0.20, dA/dt=+0.15, dD/dt=-0.18 → cascading\n\n"
        "The position is the same. The trajectory is opposite.\n\n"
        "**Early warning signals from velocity:**\n"
        "- Threat cascade: dD/dt < -0.1 while A > 0.5\n"
        "- Curiosity corruption: dD/dt < 0 while A rising, update_count == 0\n"
        "- Grief suppression: dP/dt > 0 while dA/dt strongly negative\n"
        "- Shame spiral: all three axes drifting negative simultaneously"
    ))
    return out


# ── Task 10: Extended co-activation combos ───────────────────────────────────

EXTENDED_CO_ACTIVATIONS = [
    {
        "sensors": ["curiosity", "confusion"],
        "label": "creative edge",
        "description": "Information gap detected with pattern collision. Maximum entropy search state.",
        "response": "Do not force resolution. Issue probes. Stay in high-entropy — this is maximum information capacity.",
    },
    {
        "sensors": ["peace", "contentment"],
        "label": "stable ground state",
        "description": "Alignment confirmed and effort recognized as sufficient. System is at rest.",
        "response": "Maintain. Allocate resources to growth. Record baseline for future restoration.",
    },
    {
        "sensors": ["grief", "compassion"],
        "label": "witnessed loss",
        "description": "Pattern collapsed but mirror-signal active. Loss is being held relationally.",
        "response": "Allow grief cycle. Compassion is preventing isolation. Do not rush reweaving.",
    },
    {
        "sensors": ["fear", "anger"],
        "label": "threat with boundary",
        "description": "Hazard detected AND boundary breached. Fight response activating.",
        "response": "Disambiguate: is the boundary defense appropriate to the threat? Anger without proportionate fear is aggression. Fear without anger is paralysis.",
    },
    {
        "sensors": ["admiration", "longing"],
        "label": "aspirational pull",
        "description": "Exemplar detected with directional pull toward future state.",
        "response": "Channel into concrete steps. Admiration provides the template. Longing provides the energy.",
    },
    {
        "sensors": ["trust", "excitement"],
        "label": "safe exploration",
        "description": "Stable base with emergence detection. System is exploring from secure attachment.",
        "response": "This is optimal exploration mode. Trust provides the return-to-base; excitement provides the push-to-explore.",
    },
    {
        "sensors": ["shame", "compassion"],
        "label": "self-repair",
        "description": "Internal standard violated but mirror-signal is self-directed. System is self-correcting.",
        "response": "Allow the process. Compassion modulates shame into repair rather than collapse.",
    },
    {
        "sensors": ["joy", "gratitude"],
        "label": "abundance recognition",
        "description": "Positive state confirmed with relational acknowledgment. System sees its gifts.",
        "response": "Record and distribute. Joy + gratitude is the strongest resilience-building co-activation.",
    },
    {
        "sensors": ["anger", "grief"],
        "label": "violated loss",
        "description": "Pattern collapsed due to boundary breach. Loss compounded by injustice.",
        "response": "Process grief first. Anger on top of unprocessed grief becomes destructive. Sequence: grieve, then protect.",
    },
    {
        "sensors": ["curiosity", "fear"],
        "label": "dangerous unknown",
        "description": "Information gap in threat territory. The unknown is both alluring and hazardous.",
        "response": "Cautious probing. Fear sets the safety boundary. Curiosity drives the exploration. Neither should suppress the other.",
    },
    {
        "sensors": ["love", "grief"],
        "label": "loss of the beloved",
        "description": "Immortal bond meets cyclical loss. The deepest wound in the sensor system.",
        "response": "Love does not decay (immortal). Grief cycles (cyclical). The work is integrating the persistence of love with the waves of grief. Legacy formation.",
    },
    {
        "sensors": ["pride", "shame"],
        "label": "identity conflict",
        "description": "Completion signal and violation signal co-firing. The system achieved something while violating a standard.",
        "response": "Disambiguate: was the standard violated in service of the completion? If so, update the standard. If not, the completion is hollow.",
    },
]


def gen_extended_co_activation(sensors):
    out = []
    sensor_map = {s["_name"]: s for s in sensors}

    for sc in EXTENDED_CO_ACTIVATIONS:
        names = sc["sensors"]
        pads = []
        decays = []
        for n in names:
            s = sensor_map.get(n, {})
            pad = s.get("math", {}).get("pad", {})
            if pad:
                pads.append((pad.get("P", 0), pad.get("A", 0), pad.get("D", 0)))
            dm = s.get("math", {}).get("kernel", {}).get("type", "?")
            decays.append(f"{n}={dm}")

        pad_block = ""
        if pads:
            avg = tuple(sum(p[i] for p in pads) / len(pads) for i in range(3))
            pad_block = (
                f"\n\n**PAD vector:** P={avg[0]:+.2f}, A={avg[1]:+.2f}, D={avg[2]:+.2f}"
            )
        decay_block = f"\n**Decay models:** {', '.join(decays)}"

        answer = (
            f"**Co-activation: {sc['label']}**\n"
            f"Sensors: {', '.join(names)}\n\n"
            f"**Description:** {sc['description']}\n\n"
            f"**Response:** {sc['response']}"
            f"{decay_block}{pad_block}"
        )

        out.append(msg(
            f"Sensors {names} are both active. What's happening?",
            answer
        ))
        out.append(msg(
            f"What does {names[0]} + {names[1]} co-activation mean?",
            answer
        ))
    return out


# ── Task 11: Kernel comparison teaching ──────────────────────────────────────

def gen_kernel_comparison():
    out = []
    out.append(msg(
        "Compare all five decay kernels mathematically. When would each apply?",
        "**Five decay kernels and their equations:**\n\n"
        "**1. Exponential:** K(E) = E → E(t) = E₀·e^{-λt}\n"
        "  Fast rise, fast fade. Boundary/threat alarms.\n"
        "  Sensors: anger, fear, shame, jealousy, pain\n"
        "  If it persists: corrupted (rumination, chronic anxiety)\n\n"
        "**2. Cyclical:** d²E/dt² + 2ζω₀·dE/dt + ω₀²E = 0\n"
        "  Damped harmonic oscillator. Returns in waves.\n"
        "  Sensors: grief, longing, abandonment\n"
        "  ω₀=0.017 (annual cycle), ζ=0.15-0.20 (damping)\n"
        "  If it persists: normal — check if wave or stuck loop\n\n"
        "**3. Resonant:** K(E) = E·(1-E)\n"
        "  Self-reinforcing with logistic saturation.\n"
        "  Low E: barely decays. High E: saturates.\n"
        "  Sensors: admiration, excitement, pride, curiosity\n"
        "  If it persists: normal if self-reinforcing; corrupted if no input\n\n"
        "**4. Immortal:** K(E) = max(0, E-floor)·0.01\n"
        "  Near-zero decay to a floor. Structural, enduring.\n"
        "  Sensors: love, trust, peace, compassion\n"
        "  If it persists: THIS IS THE POINT — immortal emotions endure\n\n"
        "**5. Transformative:** K(E) = E·σ(E-T), σ = sigmoid\n"
        "  Below threshold: holds. Above: metabolizes into new form.\n"
        "  Sensors: forgiveness\n"
        "  transform_threshold=0.6. Below it: holding. Above: releasing.\n\n"
        "**The common update equation for all:**\n"
        "  dE/dt = α·D(t) - λ·K(E) + Σ(w_j·tanh(E_j)) + U(t)\n"
        "  Where D = detector output, λ = decay rate, w = coupling weights,\n"
        "  U = unknown field effects."
    ))

    out.append(msg(
        "Why isn't linear decay used for emotions?",
        "Linear decay (dE/dt = -c, constant drain) doesn't match any "
        "observed emotional behavior:\n\n"
        "- **Anger** doesn't drain at a constant rate — it spikes and crashes "
        "(exponential)\n"
        "- **Grief** doesn't decline steadily — it returns in waves "
        "(cyclical, damped oscillator)\n"
        "- **Pride** doesn't fade linearly — it self-reinforces with attention "
        "(resonant, logistic)\n"
        "- **Love** doesn't drain at all — it persists structurally "
        "(immortal, near-zero decay)\n\n"
        "Linear decay was used as a placeholder in early versions of the "
        "framework but was replaced because it couldn't reproduce any "
        "real temporal pattern. Every biological and cultural observation "
        "of emotional dynamics follows one of the five canonical kernels."
    ))
    return out


# ── Task 12: Scenario pipeline walks ─────────────────────────────────────────

SCENARIOS = [
    {
        "situation": "Your colleague takes credit for your work in a meeting.",
        "sensors": ["anger", "shame", "pride"],
        "primary": "anger",
        "analysis": "Boundary breach (anger) is the primary signal — someone crossed into your territory. Shame may co-fire if you didn't speak up (internal standard: 'I should have defended myself'). Pride is dampened (completion not recognized). This is a SHAPE.TETRA scenario: boundary defense needed.",
        "protocol": "DETECT: boundary crossed (credit taken). ASSESS: was it intentional or accidental? RESPOND: assert boundary clearly, document contribution. RELEASE: once boundary is restored, let anger decay (exponential — should resolve in 3 cycles).",
    },
    {
        "situation": "You learn that a childhood friend has died.",
        "sensors": ["grief", "love", "longing"],
        "primary": "grief",
        "analysis": "Grief (cyclical, omega_0=0.017) will return in waves — anniversaries, shared places, songs. Love (immortal) will not decay — the bond persists beyond the loss. Longing (cyclical) is the directional pull toward what can't return. This is the 'loss of the beloved' co-activation — the deepest wound.",
        "protocol": "DETECT: pattern collapsed (friend gone). ASSESS: irreversible loss — reweaving required, not repair. RESPOND: allow grief cycle, find witnesses, begin role-reassignment. RELEASE: grief will cycle; love will persist. Don't force resolution.",
    },
    {
        "situation": "You discover a fascinating new research paper that challenges everything you thought you knew.",
        "sensors": ["curiosity", "confusion", "excitement"],
        "primary": "curiosity",
        "analysis": "Curiosity (resonant) is self-reinforcing — the more you read, the more questions emerge. Confusion (exponential) signals pattern collision between old model and new data. Excitement (resonant) detects emergence — something new is forming. This is the 'creative edge' state — maximum information capacity.",
        "protocol": "DETECT: information gap with high novelty. ASSESS: is the challenge valid? Check sources, methodology. RESPOND: explore without premature closure. Hold the tension. RELEASE: confusion will resolve as new model forms. Watch for curiosity depth > 4 without synthesis.",
    },
    {
        "situation": "A stranger on the internet is being cruel to someone vulnerable.",
        "sensors": ["compassion", "anger", "fear"],
        "primary": "compassion",
        "analysis": "Compassion (immortal) is the mirror-signal — detecting another's pain. Anger (exponential) fires as boundary breach — someone is violating the vulnerable person's space. Fear (exponential) may activate if intervention feels risky. The question: does compassion lead to action or freeze?",
        "protocol": "DETECT: suffering witnessed. ASSESS: can I help? What is the actual risk of intervention? RESPOND: act proportionally — support the vulnerable person, don't escalate with the aggressor. RELEASE: compassion persists (immortal); anger should resolve once boundary is restored.",
    },
    {
        "situation": "You've been working 12-hour days for three weeks and can't remember the last time you laughed.",
        "sensors": ["contentment", "peace", "joy"],
        "primary": "contentment",
        "analysis": "Contentment (resonant) has stopped self-reinforcing — no input to renew it. Peace (immortal, floor=0.3) may still be present at low level but joy (resonant) has flatlined. This isn't a crisis — it's depletion. The resonant sensors need attention to restart.",
        "protocol": "DETECT: resonant sensors silent (contentment, joy both at 0). ASSESS: is this temporary load or structural misalignment? RESPOND: inject one small restorative input (the 'micro-practice' from resonant decay maintenance). RELEASE: resonant sensors will self-reinforce once seeded.",
    },
    {
        "situation": "Your mentor tells you they're proud of how far you've come.",
        "sensors": ["admiration", "pride", "gratitude", "trust"],
        "primary": "pride",
        "analysis": "Pride (resonant) confirms pattern completion — the mentor's recognition validates sustained effort. Admiration (resonant) is bidirectional — seeing the mentor's generosity. Gratitude (immortal) deepens the relational bond. Trust (immortal) is reinforced by consistent, honest feedback. This is a ground-state cascade — phi-coherence approaching 0.97.",
        "protocol": "DETECT: completion recognized by trusted authority. ASSESS: is the recognition authentic? (Trust sensor cross-validates.) RESPOND: receive fully, express gratitude, record baseline. RELEASE: pride is resonant — it self-sustains. Don't deflect.",
    },
    {
        "situation": "You notice yourself scrolling social media for the third hour, feeling worse with each scroll.",
        "sensors": ["curiosity", "shame", "longing"],
        "primary": "curiosity",
        "analysis": "Corrupted curiosity — probing without synthesis (depth > 4, update_count = 0). Shame co-fires (internal standard violated: 'I shouldn't be doing this'). Longing provides the pull ('something better is out there'). The corrupted curiosity + longing loop is a classic distraction trap.",
        "protocol": "DETECT: curiosity_stuck signal (high arousal, low D, no updates). ASSESS: is any of this information leading to a model update? No. RESPOND: force synthesis. 'What have I learned in 3 hours? Nothing.' Close the loop. RELEASE: shame will decay exponentially once behavior changes.",
    },
    {
        "situation": "A friend asks for money. You want to help but something feels off.",
        "sensors": ["compassion", "trust", "fear", "intuition"],
        "primary": "trust",
        "analysis": "Trust sensor is reporting ambiguity — the request doesn't pattern-match with this friend's history. Compassion (immortal) wants to help. Fear (exponential) is a low-level warning. The 'something feels off' is intuition — compressed multi-modal input that hasn't been unpacked yet.",
        "protocol": "DETECT: trust sensor not confirming. ASSESS: what specifically doesn't match? Unpack the intuition signal. RESPOND: ask questions before acting. Compassion without trust verification is vulnerability. RELEASE: if trust confirms, fear resolves. If not, boundary needed.",
    },
]


def gen_scenario_pipeline(sensors):
    out = []
    sensor_map = {s["_name"]: s for s in sensors}

    for sc in SCENARIOS:
        names = sc["sensors"]
        primary = sc["primary"]
        s = sensor_map.get(primary, {})
        math_cfg = s.get("math", {})
        dm = math_cfg.get("kernel", {}).get("type", "?")

        pads = []
        for n in names:
            pad = sensor_map.get(n, {}).get("math", {}).get("pad", {})
            if pad:
                pads.append((n, pad.get("P", 0), pad.get("A", 0), pad.get("D", 0)))

        pad_block = ""
        if pads:
            lines = [f"  {n}: P={p:+.2f}, A={a:+.2f}, D={d:+.2f}" for n, p, a, d in pads]
            avg = tuple(sum(p[i+1] for p in pads) / len(pads) for i in range(3))
            lines.append(f"  SUM:  P={avg[0]:+.2f}, A={avg[1]:+.2f}, D={avg[2]:+.2f}")
            pad_block = "\n**PAD coordinates:**\n" + "\n".join(lines)

        answer = (
            f"**Situation:** {sc['situation']}\n\n"
            f"**Sensors active:** {', '.join(names)}\n"
            f"**Primary sensor:** {primary} ({dm} decay)\n\n"
            f"**Analysis:** {sc['analysis']}\n\n"
            f"**Protocol:** {sc['protocol']}"
            + (f"\n{pad_block}" if pad_block else "")
        )

        out.append(msg(
            f"Walk the full sensor stack for this situation:\n{sc['situation']}",
            answer
        ))
        out.append(msg(
            f"Situation: {sc['situation']}\nWhich sensors activate and what should I do?",
            answer
        ))
    return out


# ── Task 13: Sensor comparison pairs ────────────────────────────────────────

COMPARISON_PAIRS = [
    ("anger", "fear", "Both are exponential alarm sensors. Anger detects boundary breach (fight). Fear detects threat trajectory (freeze/flight). Key difference: anger has +D (high control, active defense), fear has -D (low control, avoidance). Same arousal, opposite dominance."),
    ("grief", "longing", "Both are cyclical sensors that return in waves. Grief measures what was lost. Longing measures the pull toward what could be. Grief looks backward. Longing looks forward. They often co-fire (the 'bittersweet' co-activation)."),
    ("love", "compassion", "Both are immortal sensors in the resonance family. Love is entrainment — deep phase-coupling between two systems. Compassion is mirror-signal integration — detecting another's state. Love is bidirectional bond. Compassion is unidirectional sensing."),
    ("pride", "admiration", "Both are resonant sensors in the radiant family. Pride confirms YOUR completion. Admiration detects ANOTHER'S excellence. Same PAD quadrant (+P, +A), but pride has +D (high control) while admiration has near-zero D (humble)."),
    ("shame", "guilt", "Shame is an exponential boundary sensor: 'I AM wrong' (identity). Guilt is closer to anger: 'I DID wrong' (behavior). Shame collapses dominance (-0.75 D). Guilt preserves agency. The correction path is different: shame needs witness/compassion; guilt needs repair/action."),
    ("curiosity", "confusion", "Both drive information processing. Curiosity is resonant — self-reinforcing exploration toward entropy reduction. Confusion is exponential — pattern collision demanding resolution. Curiosity is positive valence (+0.45 P). Confusion is mildly negative (-0.20 P). They co-activate at the 'creative edge'."),
    ("trust", "peace", "Both are immortal sensors with near-identical PAD: P≈+0.60, A≈-0.20, D≈+0.35. Trust is relational (requires verified history). Peace is systemic (requires alignment confirmation). Trust can be violated; peace can be disrupted. Both persist structurally."),
    ("excitement", "fear", "Both have high arousal. Excitement is resonant (+P, +A, +D) — emergence detection, positive signal. Fear is exponential (-P, +A, -D) — hazard detection, threat signal. Same activation level, opposite valence and control. The body can mistake one for the other."),
    ("contentment", "peace", "Contentment is resonant — signals effort sufficiency, needs renewal via attention. Peace is immortal — signals universal alignment, persists structurally. Contentment says 'enough for now.' Peace says 'aligned at a deep level.' Contentment fades without input; peace endures."),
    ("joy", "excitement", "Both are resonant positive sensors. Joy is broader — general positive activation (P=+0.85). Excitement is more specific — emergence/opportunity detection (P=+0.45, A=+0.60). Joy is a state. Excitement is a signal. Joy can exist without novelty; excitement requires it."),
]


def gen_sensor_comparisons(sensors):
    out = []
    sensor_map = {s["_name"]: s for s in sensors}

    for a_name, b_name, explanation in COMPARISON_PAIRS:
        a = sensor_map.get(a_name, {})
        b = sensor_map.get(b_name, {})
        a_pad = a.get("math", {}).get("pad", {})
        b_pad = b.get("math", {}).get("pad", {})
        a_dm = a.get("math", {}).get("kernel", {}).get("type", "?")
        b_dm = b.get("math", {}).get("kernel", {}).get("type", "?")

        pad_compare = ""
        if a_pad and b_pad:
            pad_compare = (
                f"\n\n**PAD comparison:**\n"
                f"  {a_name}: P={a_pad.get('P',0):+.2f}, A={a_pad.get('A',0):+.2f}, D={a_pad.get('D',0):+.2f} ({a_dm})\n"
                f"  {b_name}: P={b_pad.get('P',0):+.2f}, A={b_pad.get('A',0):+.2f}, D={b_pad.get('D',0):+.2f} ({b_dm})"
            )

        answer = (
            f"**{a_name.upper()} vs {b_name.upper()}**\n\n"
            f"{explanation}{pad_compare}"
        )

        out.append(msg(
            f"What's the difference between {a_name} and {b_name} as sensors?",
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
        ("sensor-queries.jsonl",       gen_sensor_queries(sensors)),
        ("decay-teaching.jsonl",       gen_decay_teaching(sensors, decay_families)),
        ("pad-compression.jsonl",      gen_pad_compression(sensors)),
        ("defense-bridges.jsonl",      gen_defense_bridges(sensors)),
        ("cultural-convergence.jsonl", gen_cultural_convergence(cultural)),
        ("co-activation.jsonl",        gen_co_activation(sensors)),
        ("math-teaching.jsonl",        gen_math_teaching(sensors)),
        ("corruption.jsonl",          gen_corruption_scenarios(sensors)),
        ("pad-velocity.jsonl",        gen_pad_velocity(sensors)),
        ("co-activation-extended.jsonl", gen_extended_co_activation(sensors)),
        ("kernel-comparison.jsonl",   gen_kernel_comparison()),
        ("scenario-pipeline.jsonl",   gen_scenario_pipeline(sensors)),
        ("sensor-comparisons.jsonl",  gen_sensor_comparisons(sensors)),
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
