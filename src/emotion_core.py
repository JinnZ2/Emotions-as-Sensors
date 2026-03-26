"""
Emotion Core Engine
Implements the formal update loop for Emotions-as-Sensors JSON modules.
Compatible with Bridge Orchestrator and Resonance Analyzer.

Decay kernels: exponential, cyclical, resonant, immortal, transformative
PAD compression: 22 sensors -> 3 floats -> 8 octahedral states (3 bits)
Authenticity gate: routes corrupted signals through defense_bridge
"""

import json, math, random
from pathlib import Path

# ── PAD → Octahedral state mapping ──────────────────────────────────────────
# Maps sign of dominant PAD axis to one of 8 geometric states.
# From Rosetta-Shape-Core generate.py (Porges 2011, LeDoux 1996, Ekman 1992).

PAD_TO_OCTA = {
    ( 1,  0,  0): 0,   # +x  spherical, ground state (love, coherence)
    (-1,  0,  0): 1,   # -x  collapsed form (grief, pain)
    ( 0,  1,  0): 2,   # +y  high-entropy search (curiosity, confusion)
    ( 0, -1,  0): 3,   # -y  stable low-energy (contentment, fatigue)
    ( 0,  0,  1): 4,   # +z  compressed, high contrast (anger, boundary)
    ( 0,  0, -1): 5,   # -z  biaxial, chaotic (fear, shame)
    ( 1,  1,  0): 6,   # diagonal-a  superposition (excitement, intuition)
    (-1, -1,  0): 7,   # diagonal-b  dissipative (grief+shame, collapse)
}

OCTA_PHI_COHERENCE = {0: 0.97, 1: 0.82, 2: 0.82, 3: 0.85,
                      4: 0.73, 5: 0.78, 6: 0.70, 7: 0.72}

OCTA_LABELS = {
    0: "ground_state",       1: "collapsed_form",
    2: "high_entropy_search", 3: "stable_low_energy",
    4: "boundary_assertion",  5: "chaotic_regime",
    6: "diagonal_superposition", 7: "dissipative_flow",
}


def pad_to_octa(p, a, d):
    """Map continuous PAD coordinates to nearest octahedral state index."""
    # Check if diagonal states dominate (both P and A significant)
    if abs(p) > 0.3 and abs(a) > 0.3:
        sp = 1 if p >= 0 else -1
        sa = 1 if a >= 0 else -1
        if sp == 1 and sa == 1:
            return 6
        if sp == -1 and sa == -1:
            return 7
    # Otherwise find dominant axis
    vals = [abs(p), abs(a), abs(d)]
    dom = vals.index(max(vals))
    signs = [1 if p > 0 else -1, 1 if a > 0 else -1, 1 if d > 0 else -1]
    if dom == 0:
        return PAD_TO_OCTA.get((signs[0], 0, 0), 0)
    elif dom == 1:
        return PAD_TO_OCTA.get((0, signs[1], 0), 2)
    else:
        return PAD_TO_OCTA.get((0, 0, signs[2]), 4)


class EmotionSensor:
    def __init__(self, config):
        self.name = config.get("sensor", config.get("emotion", config.get("id", "unknown")))
        self.function = config.get("function", "")
        self.signal_type = config.get("signal_type", "")
        dm = config.get("decay_model", "exponential")
        self.decay_model = dm if isinstance(dm, str) else dm.get("type", "exponential")

        # If a math block specifies kernel.type, it overrides decay_model
        # for computation. This resolves mismatches like decay_model="manual"
        # with kernel.type="resonant".
        math_cfg = config.get("math", {})
        kernel_type = math_cfg.get("kernel", {}).get("type")
        if kernel_type:
            self.decay_model = kernel_type
        self.resonance_links = config.get("resonance_links", [])
        self.energy_role = config.get("energy_role", "transform")

        # defense bridge (optional)
        self.defense_bridge = config.get("defense_bridge", {})

        # math parameters (optional section)
        math_cfg = config.get("math", {})
        self.lambda_ = math_cfg.get("lambda", 0.5)
        self.alpha = math_cfg.get("alpha", 1.0)
        self.couplings = {c["to"]: c["w"] for c in math_cfg.get("couplings", [])}
        self.max_action_cost = math_cfg.get("policy", {}).get("max_action_cost", 0.3)

        # PAD coordinates for geometric compression
        pad_cfg = math_cfg.get("pad", {})
        self.pad_p = pad_cfg.get("P", 0.0)
        self.pad_a = pad_cfg.get("A", 0.0)
        self.pad_d = pad_cfg.get("D", 0.0)

        # Corrupted PAD signature (from pad_biology.json)
        # When a sensor is corrupted, its PAD shifts toward these values
        corrupted_pad = math_cfg.get("corrupted_pad", {})
        self.corrupted_pad_p = corrupted_pad.get("P", None)
        self.corrupted_pad_a = corrupted_pad.get("A", None)
        self.corrupted_pad_d = corrupted_pad.get("D", None)

        # kernel-specific parameters
        kernel_cfg = math_cfg.get("kernel", {})
        self.omega_0 = kernel_cfg.get("omega_0", 1.0)
        self.zeta = kernel_cfg.get("zeta", 0.2)
        self.floor = kernel_cfg.get("floor", 0.0)
        self.transform_threshold = kernel_cfg.get("transform_threshold", 0.6)

        # dynamic state
        self.E = 0.0       # activation amplitude
        self.V = 0.0       # velocity (second state variable for cyclical kernel)
        self.U = 0.0       # unknown field
        self.authentic = True
        self.corruption_cycles = 0
        self.active = True

    def sense(self, external_signal):
        """Input detection step: D_i(x_t; phi_i)."""
        D = external_signal.get(self.signal_type, 0.0)
        return self.alpha * D

    def kernel(self, E):
        """Temporal decay kernel K_i(E) per decay_model.

        exponential:    K(E) = E                -> E(t) = E(0) * e^{-lambda*t}
        cyclical:       K(E) = omega_0^2 * E    -> damped oscillator (grief, longing)
        resonant:       K(E) = E * (1 - E)      -> self-reinforcing with saturation
        immortal:       K(E) = floor             -> near-zero decay, structural persistence
        transformative: K(E) = E * sigmoid(E-T)  -> metabolizes above threshold into new form
        """
        if self.decay_model == "exponential":
            return E
        elif self.decay_model == "cyclical":
            # Damped harmonic oscillator: d2E/dt2 + 2*zeta*omega_0*dE/dt + omega_0^2*E = 0
            # Converted to first-order: K(E) returns the restoring force term
            return self.omega_0 ** 2 * E + 2 * self.zeta * self.omega_0 * self.V
        elif self.decay_model == "resonant":
            # Self-reinforcing with logistic saturation
            # Low E: K ~ 0 (barely decays, self-sustains)
            # High E: K ~ E (saturates, prevents runaway)
            return E * (1.0 - E)
        elif self.decay_model == "immortal":
            # Near-zero decay — structural, enduring
            # Only decays to a floor, never to zero
            return max(0.0, E - self.floor) * 0.01
        elif self.decay_model == "transformative":
            # Metabolizes above threshold: changes form rather than fading
            # Below threshold: holds steady. Above: rapid transformation.
            sigmoid = 1.0 / (1.0 + math.exp(-10 * (E - self.transform_threshold)))
            return E * sigmoid
        # fallback
        return E

    def update(self, dt, inputs, neighbors):
        """Integrate one timestep: dE/dt = I - lambda*K(E) + sum(w*g(E_j)) + U.

        For cyclical kernels, integrates the second-order system:
            dE/dt = V
            dV/dt = I - 2*zeta*omega_0*V - omega_0^2*E + coupling + U
        This gives proper damped oscillation (grief tides, longing waves).
        """
        drive = self.sense(inputs)
        coupling = sum(
            self.couplings.get(n.name, 0.0) * math.tanh(n.E)
            for n in neighbors
        )

        if self.decay_model == "cyclical":
            # Second-order: position E, velocity V
            # dV/dt = drive - 2*zeta*w0*V - w0^2*E + coupling + U
            dV = (drive
                  - 2 * self.zeta * self.omega_0 * self.V
                  - self.lambda_ * self.omega_0 ** 2 * self.E
                  + coupling + self.U)
            self.V += dt * dV
            self.E += dt * self.V
        else:
            decay = self.lambda_ * self.kernel(self.E)
            dE = drive - decay + coupling + self.U
            self.V = dE  # store velocity for diagnostics
            self.E += dt * dE

        self.E = max(0.0, min(1.0, self.E))

        # Authenticity gate: check for corrupted signal
        self._check_authenticity(drive)

    def _check_authenticity(self, drive):
        """Authenticity gate A_i(t).

        Two detection methods:
        1. Temporal: activation persists without input beyond decay expectations
        2. PAD signature: current PAD drifts toward known corrupted centroid
           (from pad_biology.json corrupted_signal data)

        Uses defense_bridge data when available.
        """
        if not self.defense_bridge:
            self.authentic = True
            return

        # Method 1: Temporal — activation without active input
        if drive < 0.05 and self.E > 0.3:
            self.corruption_cycles += 1
        else:
            self.corruption_cycles = max(0, self.corruption_cycles - 1)

        # Threshold depends on decay model
        # Exponential sensors should resolve fast (3 cycles)
        # Cyclical sensors get more time (10 cycles)
        # Immortal sensors are structural, not corruption-prone
        if self.decay_model == "exponential":
            threshold = 3
        elif self.decay_model == "cyclical":
            threshold = 10
        elif self.decay_model == "resonant":
            threshold = 6
        else:
            threshold = 50  # immortal/transformative

        temporal_ok = self.corruption_cycles < threshold

        # Method 2: PAD signature distance comparison
        # Compare current dynamic PAD to both authentic and corrupted centroids.
        # If closer to corrupted centroid, flag as corrupted.
        #
        # The key biological insight (pad_biology.json): corrupted signals
        # show dampened arousal (A drops) and shifted dominance (D changes).
        # e.g. authentic anger: P=-0.55, A=+0.80, D=+0.70
        #      corrupted anger: P=-0.55, A=+0.30, D=+0.20 (rumination)
        pad_ok = True
        if self.corrupted_pad_p is not None and self.E > 0.1:
            # Current dynamic PAD (velocity V modulates arousal,
            # corruption_cycles modulate dominance)
            dynamic_a = self.pad_a * max(0.1, abs(self.V) / max(abs(self.pad_a), 0.01))
            dynamic_d = self.pad_d * (1.0 - 0.1 * min(self.corruption_cycles, 5))

            # Distance to authentic centroid
            d_auth = math.sqrt(
                (dynamic_a - self.pad_a) ** 2 +
                (dynamic_d - self.pad_d) ** 2
            )
            # Distance to corrupted centroid
            d_corr = math.sqrt(
                (dynamic_a - self.corrupted_pad_a) ** 2 +
                (dynamic_d - self.corrupted_pad_d) ** 2
            )
            # If closer to corrupted than authentic, flag it
            if d_corr < d_auth and self.E > 0.3:
                pad_ok = False

        self.authentic = temporal_ok and pad_ok

    def release(self, rate=0.95):
        """Release / decay control: lambda *= r(t), r <= 1."""
        self.lambda_ *= rate

    def energy_budget(self, inputs):
        """Energy accounting: dE_i/dt = eta*I - lambda*K(E) + exchange - cost."""
        drive = self.sense(inputs)
        loss = self.lambda_ * self.kernel(self.E)
        return self.alpha * drive - loss

    @property
    def octa_state(self):
        """Current octahedral state from PAD coordinates scaled by activation."""
        if self.pad_p == 0 and self.pad_a == 0 and self.pad_d == 0:
            return None
        return pad_to_octa(
            self.pad_p * self.E,
            self.pad_a * self.E,
            self.pad_d * self.E,
        )

    @property
    def pad_vector(self):
        """Current PAD vector (scaled by activation)."""
        return (self.pad_p * self.E, self.pad_a * self.E, self.pad_d * self.E)


class EmotionSystem:
    def __init__(self, sensor_dir):
        self.sensors = []
        self.load_sensors(sensor_dir)
        self.time = 0.0
        self.history = []

    def load_sensors(self, directory):
        # Load all candidates, then deduplicate by name.
        # When duplicates exist (e.g. love.json + love/love.json),
        # prefer the version with a math block, then the one with
        # more fields (more complete definition).
        candidates = {}
        for path in sorted(Path(directory).rglob("*.json")):
            try:
                with open(path) as f:
                    cfg = json.load(f)
                if not isinstance(cfg, dict):
                    continue
                if "sensor" in cfg or "emotion" in cfg or "id" in cfg:
                    sensor = EmotionSensor(cfg)
                    existing = candidates.get(sensor.name)
                    if existing is None:
                        candidates[sensor.name] = (sensor, cfg)
                    else:
                        # Prefer version with math block
                        existing_has_math = bool(existing[1].get("math"))
                        new_has_math = bool(cfg.get("math"))
                        if new_has_math and not existing_has_math:
                            candidates[sensor.name] = (sensor, cfg)
                        elif new_has_math == existing_has_math:
                            # Prefer version with more fields
                            if len(cfg) > len(existing[1]):
                                candidates[sensor.name] = (sensor, cfg)
            except (json.JSONDecodeError, KeyError):
                pass
        self.sensors = [s for s, _ in candidates.values()]

    def step(self, dt, inputs):
        """One global time step."""
        for s in self.sensors:
            neighbors = [n for n in self.sensors if n.name in s.couplings]
            s.update(dt, inputs, neighbors)
        self.time += dt
        self.history.append({s.name: s.E for s in self.sensors})

    def pad_sum(self):
        """Aggregate PAD vector across all active sensors (vector addition)."""
        p_sum, a_sum, d_sum = 0.0, 0.0, 0.0
        count = 0
        for s in self.sensors:
            if s.E > 0.01 and s.authentic:
                pv = s.pad_vector
                p_sum += pv[0]
                a_sum += pv[1]
                d_sum += pv[2]
                count += 1
        if count == 0:
            return (0.0, 0.0, 0.0)
        return (p_sum / count, a_sum / count, d_sum / count)

    def system_octa_state(self):
        """System-level octahedral state from aggregated PAD."""
        p, a, d = self.pad_sum()
        idx = pad_to_octa(p, a, d)
        return {
            "state": idx,
            "label": OCTA_LABELS[idx],
            "phi_coherence": OCTA_PHI_COHERENCE[idx],
            "pad": {"P": round(p, 3), "A": round(a, 3), "D": round(d, 3)},
        }

    def corrupted_sensors(self):
        """Return list of sensors flagged as corrupted."""
        return [s for s in self.sensors if not s.authentic]

    def coherence(self):
        """Global coherence index C(t) across resonance graph.

        C(t) = (1/Z) * sum_{(i,j)} w_ij * sqrt(E_i * E_j)
        Normalized to [0, 1].
        """
        total = 0.0
        count = 0
        for s in self.sensors:
            for n in self.sensors:
                w = s.couplings.get(n.name, 0.0)
                if w != 0:
                    total += w * math.sqrt(s.E * n.E)
                    count += 1
        if count == 0:
            return 0.0
        return max(0.0, min(1.0, total / count))

    def run(self, duration=10.0, dt=0.1):
        for _ in range(int(duration / dt)):
            inputs = {"boundary breach": random.random() * 0.2,
                      "absence": random.random() * 0.1}
            self.step(dt, inputs)
        return self.history


if __name__ == "__main__":
    system = EmotionSystem("sensors")
    data = system.run(duration=5.0)

    print("Final states:")
    for s in system.sensors:
        auth = "OK" if s.authentic else "CORRUPTED"
        pad = f"P={s.pad_p:+.2f} A={s.pad_a:+.2f} D={s.pad_d:+.2f}" if s.pad_p or s.pad_a or s.pad_d else "no PAD"
        print(f"  {s.name:15s} E={s.E:.3f}  [{s.decay_model:14s}]  {auth:9s}  {pad}")

    print(f"\nSystem octahedral state: {system.system_octa_state()}")
    print(f"Global coherence: {system.coherence():.3f}")

    corrupted = system.corrupted_sensors()
    if corrupted:
        print(f"\nCorrupted sensors ({len(corrupted)}):")
        for s in corrupted:
            bridge = s.defense_bridge
            print(f"  {s.name}: {bridge.get('corrupted_form', 'unknown')} "
                  f"(defense: {bridge.get('defense_id', 'none')})")
