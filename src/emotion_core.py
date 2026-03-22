"""
Emotion Core Engine
Implements the formal update loop for Emotions-as-Sensors JSON modules.
Compatible with Bridge Orchestrator and Resonance Analyzer.
"""

import json, math, random
from pathlib import Path

class EmotionSensor:
    def __init__(self, config):
        self.name = config["sensor"]
        self.function = config.get("function", "")
        self.signal_type = config.get("signal_type", "")
        self.decay_model = config.get("decay_model", "exponential")
        self.resonance_links = config.get("resonance_links", [])
        self.energy_role = config.get("energy_role", "transform")

        # math parameters (optional section)
        math_cfg = config.get("math", {})
        self.lambda_ = math_cfg.get("lambda", 0.5)
        self.alpha = math_cfg.get("alpha", 1.0)
        self.couplings = {c["to"]: c["w"] for c in math_cfg.get("couplings", [])}
        self.max_action_cost = math_cfg.get("policy", {}).get("max_action_cost", 0.3)

        # dynamic state
        self.E = 0.0  # activation
        self.U = 0.0  # unknown field
        self.active = True

    def sense(self, external_signal):
        """Input detection step."""
        D = external_signal.get(self.signal_type, 0.0)
        return self.alpha * D

    def kernel(self, E):
        if self.decay_model == "exponential":
            return E
        elif self.decay_model == "cyclical":
            # simulate oscillation
            return math.sin(E)
        elif self.decay_model == "power":
            return E ** 0.7
        return E

    def update(self, dt, inputs, neighbors):
        """Integrate one timestep."""
        drive = self.sense(inputs)
        coupling = sum(self.couplings.get(n.name, 0.0) * n.E for n in neighbors)
        dE = drive - self.lambda_ * self.kernel(self.E) + coupling + self.U
        self.E += dt * dE
        self.E = max(0.0, min(1.0, self.E))

    def release(self):
        """Release / decay control."""
        self.lambda_ *= 0.95  # gradual relaxation

    def energy_budget(self, inputs):
        drive = self.sense(inputs)
        loss = self.lambda_ * self.kernel(self.E)
        return self.alpha * drive - loss

class EmotionSystem:
    def __init__(self, sensor_dir):
        self.sensors = []
        self.load_sensors(sensor_dir)
        self.time = 0.0
        self.history = []

    def load_sensors(self, directory):
        for path in Path(directory).rglob("*.json"):
            with open(path) as f:
                cfg = json.load(f)
            self.sensors.append(EmotionSensor(cfg))

    def step(self, dt, inputs):
        """One global time step."""
        for s in self.sensors:
            neighbors = [n for n in self.sensors if n.name in s.couplings]
            s.update(dt, inputs, neighbors)
        self.time += dt
        self.history.append({s.name: s.E for s in self.sensors})

    def run(self, duration=10.0, dt=0.1):
        for _ in range(int(duration / dt)):
            # Example synthetic input: random mild signals
            inputs = {"boundary breach": random.random() * 0.2,
                      "absence": random.random() * 0.1}
            self.step(dt, inputs)
        return self.history

if __name__ == "__main__":
    # Example usage
    system = EmotionSystem("sensors")
    data = system.run(duration=5.0)
    print("Final states:")
    for s in system.sensors:
        print(f"{s.name:12s} E={s.E:.3f}")
