"""
Constraint Agent — Seed-geometry agent with bloom/explore/compress lifecycle.

Expands from a Rosetta shape seed (tetrahedron, cube, etc.), discovers
entities and resonances, records energy flows, then compresses back to
seed while preserving the map. Integrates with Emotions-as-Sensors for
PAD-based sensor state during exploration.

Lifecycle:
    COMPRESSED → bloom() → EXPANDING → explore() → EXPLORING → compress() → COMPRESSED

Resource budget uses exact Fractions to avoid floating-point drift in
energy accounting (matches the Elder Logic energy conservation principle).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional


class AgentState(Enum):
    COMPRESSED = "compressed"
    EXPANDING = "expanding"
    EXPLORING = "exploring"
    CONTRACTING = "contracting"


@dataclass
class ResourceBudget:
    compute: int = 0
    bandwidth: float = 0.0
    energy: Fraction = field(default_factory=lambda: Fraction(1, 1))
    time_remaining: Fraction = field(default_factory=lambda: Fraction(1, 1))

    def is_depleted(self) -> bool:
        return self.energy <= 0 or self.time_remaining <= 0


@dataclass
class GeometricMap:
    """The agent's discovered map of entities, resonances, and energy flows."""
    resonances: Dict[str, Fraction] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    energy_flows: Dict[tuple, Fraction] = field(default_factory=dict)

    def record_resonance(self, entity_id: str, score: float) -> None:
        self.resonances[entity_id] = Fraction(score).limit_denominator(10000)

    def record_relationship(self, from_id: str, to_id: str) -> None:
        if from_id not in self.relationships:
            self.relationships[from_id] = []
        if to_id not in self.relationships[from_id]:
            self.relationships[from_id].append(to_id)

    def record_energy_flow(self, from_id: str, to_id: str, amount: Fraction) -> None:
        key = (from_id, to_id)
        self.energy_flows[key] = self.energy_flows.get(key, Fraction(0, 1)) + amount


class ConstraintAgent:
    """
    A seed-geometry agent that blooms, explores, and compresses.

    Each agent is rooted in a Rosetta shape (e.g. SHAPE.TETRA) and
    expands outward through the ontology, discovering entities and
    recording resonances. The map persists across compress/expand
    cycles, enabling deterministic re-expansion.

    Sensor integration: during exploration, the agent maps discovered
    resonances and energy flows to Emotions-as-Sensors PAD coordinates,
    producing a real-time emotional state for the agent.
    """

    def __init__(self, seed_id: str, home_families: Optional[List[str]] = None,
                 bloom_threshold: float = 0.5):
        self.seed_id = seed_id
        self.home_families = home_families or []
        self.bloom_threshold = Fraction(bloom_threshold).limit_denominator(100)

        self.state = AgentState.COMPRESSED
        self.compression_ratio = Fraction(1, 1)  # 1 = fully compressed
        self.current_position = seed_id
        self.budget = ResourceBudget()
        self.map = GeometricMap()
        self.expansion_history: List[dict] = []
        self.sensor_state: Dict[str, Fraction] = {}

        # Lazily loaded emotion system for sensor integration
        self._emotion_system = None

    def set_resource_budget(self, compute: int = 0, bandwidth: float = 0.0,
                           energy: float = 1.0, time_remaining: float = 1.0) -> None:
        """Set available resources for expansion."""
        self.budget = ResourceBudget(
            compute=compute,
            bandwidth=bandwidth,
            energy=Fraction(energy).limit_denominator(10000),
            time_remaining=Fraction(time_remaining).limit_denominator(10000)
        )

    def should_expand(self) -> bool:
        """Check if resources exceed bloom threshold."""
        if self.budget.is_depleted():
            return False
        energy_ratio = self.budget.energy / max(self.budget.energy, Fraction(1, 1))
        return energy_ratio >= self.bloom_threshold

    def bloom(self, depth: int = 1, seed_map: Optional[GeometricMap] = None) -> List[str]:
        """
        Expand outward from seed, discovering new entities up to depth.
        If seed_map provided, re-expand deterministically along previous discoveries.

        Returns list of newly discovered entity IDs.
        """
        if self.state == AgentState.COMPRESSED:
            self.state = AgentState.EXPANDING

        discovered = []
        current_depth = 0
        frontier = [self.seed_id]

        # If we have a prior map, expand along known relationships first
        if seed_map and seed_map.relationships:
            for entity_id in frontier:
                if entity_id in seed_map.relationships:
                    for reachable in seed_map.relationships[entity_id]:
                        if reachable not in self.map.resonances:
                            discovered.append(reachable)
                            # Restore resonance from prior map
                            if reachable in seed_map.resonances:
                                self.map.resonances[reachable] = seed_map.resonances[reachable]

        # Then explore new entities (hook: query Rosetta or Mandala)
        while current_depth < depth and not self.budget.is_depleted():
            new_frontier = []
            for entity_id in frontier:
                neighbors = self._get_neighbors(entity_id, depth - current_depth)
                for neighbor_id, resonance_score in neighbors:
                    if neighbor_id not in self.map.resonances:
                        self.map.record_resonance(neighbor_id, resonance_score)
                        self.map.record_relationship(entity_id, neighbor_id)
                        discovered.append(neighbor_id)
                        new_frontier.append(neighbor_id)
                        # Deduct resource cost
                        self.budget.compute = max(0, self.budget.compute - 10)
                        self.budget.energy -= Fraction(1, 100)

            frontier = new_frontier
            current_depth += 1

        # Record this expansion in history
        self.expansion_history.append({
            "depth": depth,
            "discovered_entities": discovered,
            "energy_spent": Fraction(1, 100) * len(discovered)
        })

        self.state = AgentState.EXPLORING
        self.compression_ratio = Fraction(0, 1)  # Fully expanded
        return discovered

    def explore(self) -> Dict[str, any]:
        """
        Traverse the expanded constraint space, recording energy flows
        and sensor activations. Returns discovery summary.
        """
        if self.state not in [AgentState.EXPANDING, AgentState.EXPLORING]:
            return {}

        self.state = AgentState.EXPLORING
        summary = {
            "entities_visited": 0,
            "relationships_mapped": 0,
            "energy_flows_recorded": 0,
            "sensor_activations": {}
        }

        # Walk the map, recording energy dynamics
        for from_id in self.map.relationships:
            for to_id in self.map.relationships[from_id]:
                if from_id in self.map.resonances and to_id in self.map.resonances:
                    # Energy flow proportional to resonance product
                    flow = self.map.resonances[from_id] * self.map.resonances[to_id]
                    self.map.record_energy_flow(from_id, to_id, flow)
                    summary["energy_flows_recorded"] += 1
                    summary["entities_visited"] += 1

        summary["relationships_mapped"] = len(self.map.relationships)

        # Update sensors based on discovered resonances
        self._update_sensors()
        summary["sensor_activations"] = {
            k: float(v) for k, v in self.sensor_state.items()
        }

        return summary

    def compress(self) -> Fraction:
        """
        Collapse back to seed geometry, preserving the map.
        Returns compression ratio (0 = fully expanded, 1 = fully compressed).
        """
        if self.state == AgentState.COMPRESSED:
            return self.compression_ratio

        self.state = AgentState.CONTRACTING

        # Compress: discard transient state, keep map
        self.compression_ratio = Fraction(1, 1)
        self.current_position = self.seed_id

        self.state = AgentState.COMPRESSED
        return self.compression_ratio

    def detect_corruption(self, imposed_constraint: str) -> bool:
        """
        Check if an imposed external constraint violates the agent's own map.
        Returns True if corruption detected (constraint is inconsistent
        with discovered geometry).
        """
        # Compare imposed_constraint against agent's discovered resonances.
        # If the constraint references entities the agent knows about,
        # verify it respects the discovered energy flows.
        return False  # Replace with actual validation

    def self_validate(self) -> Dict[str, any]:
        """
        Internal consistency check: verify map integrity, detect anomalies.
        Returns validation report.
        """
        report = {
            "is_valid": True,
            "inconsistencies": [],
            "energy_balance": Fraction(0, 1),
            "geometry_coherence": Fraction(1, 1)
        }

        # Check energy conservation in recorded flows
        inflows: Dict[str, Fraction] = {}
        outflows: Dict[str, Fraction] = {}
        for (from_id, to_id), amount in self.map.energy_flows.items():
            outflows[from_id] = outflows.get(from_id, Fraction(0, 1)) + amount
            inflows[to_id] = inflows.get(to_id, Fraction(0, 1)) + amount

        for entity_id in set(list(inflows.keys()) + list(outflows.keys())):
            imbalance = inflows.get(entity_id, Fraction(0, 1)) - outflows.get(entity_id, Fraction(0, 1))
            if imbalance != 0:
                report["inconsistencies"].append(
                    f"{entity_id}: energy imbalance = {imbalance}"
                )
                report["is_valid"] = False

        # Check resonance coherence (all scores should be 0 to 1)
        for entity_id, score in self.map.resonances.items():
            if score < 0 or score > 1:
                report["inconsistencies"].append(
                    f"{entity_id}: resonance out of range ({score})"
                )
                report["is_valid"] = False

        return report

    # ── Sensor integration (Emotions-as-Sensors) ────────────────────────────

    def _get_emotion_system(self):
        """Lazily load the EmotionSystem from sensor files."""
        if self._emotion_system is None:
            from emotion_core import EmotionSystem
            sensors_dir = Path(__file__).resolve().parent.parent / "sensors"
            if sensors_dir.exists():
                self._emotion_system = EmotionSystem(str(sensors_dir))
        return self._emotion_system

    def _update_sensors(self) -> None:
        """
        Update emotional/sensor state based on discovered geometry.

        Maps resonances and energy flows to sensor activations via the
        EmotionSystem. The agent's exploration state drives sensor inputs:
        - High resonance discovery → excitement, curiosity
        - Energy imbalance → anger (boundary), fear (threat)
        - Stable coherence → peace, trust
        - Loss of entities → grief, longing
        """
        system = self._get_emotion_system()
        if system is None:
            # No sensor files available — use stub
            self.sensor_state = {
                "expansion_drive": Fraction(0, 1),
                "stability_need": Fraction(0, 1),
                "boundary_awareness": Fraction(0, 1),
            }
            return

        # Build input signals from exploration state
        total_resonance = sum(float(v) for v in self.map.resonances.values())
        entity_count = len(self.map.resonances)
        avg_resonance = total_resonance / max(entity_count, 1)

        # Energy flow balance
        total_inflow = Fraction(0, 1)
        total_outflow = Fraction(0, 1)
        for (from_id, to_id), amount in self.map.energy_flows.items():
            total_outflow += amount
            total_inflow += amount
        net_balance = float(total_inflow - total_outflow)

        # Map exploration state to sensor signal types
        inputs = {
            "coherence": avg_resonance,
            "novelty": min(1.0, entity_count / 20.0),
            "boundary breach": max(0.0, -net_balance),
            "absence": max(0.0, 1.0 - avg_resonance) if entity_count > 0 else 0.0,
            "alignment-pause": 0.1 if self.state == AgentState.CONTRACTING else 0.0,
        }

        # Run one step of the emotion system
        system.step(0.1, inputs)

        # Extract PAD state
        pad = system.pad_sum()
        octa = system.system_octa_state()

        # Store sensor state as Fractions for exact accounting
        self.sensor_state = {}
        for s in system.sensors:
            if s.E > 0.01:
                self.sensor_state[s.name] = Fraction(s.E).limit_denominator(10000)

        # Store system-level readings
        self.sensor_state["_pad_P"] = Fraction(pad[0]).limit_denominator(10000)
        self.sensor_state["_pad_A"] = Fraction(pad[1]).limit_denominator(10000)
        self.sensor_state["_pad_D"] = Fraction(pad[2]).limit_denominator(10000)
        self.sensor_state["_octa_state"] = Fraction(octa["state"], 1)
        self.sensor_state["_coherence"] = Fraction(
            system.coherence()
        ).limit_denominator(10000)

    # ── Expansion hooks ─────────────────────────────────────────────────────

    def _get_neighbors(self, entity_id: str, remaining_depth: int) -> List[tuple]:
        """
        Fetch neighbors from Rosetta or Mandala.
        Replace with actual entity lookup logic.

        Returns list of (neighbor_id, resonance_score) tuples.
        """
        # Hook: rosetta_shape_core.explore.get_reachable_entities(entity_id)
        # or mandala_computer.get_adjacent_states(entity_id)
        return []

    # ── Serialization ───────────────────────────────────────────────────────

    def serialize(self) -> Dict[str, any]:
        """Serialize agent state to JSON-compatible dict."""
        return {
            "seed_id": self.seed_id,
            "home_families": self.home_families,
            "state": self.state.value,
            "compression_ratio": (
                self.compression_ratio.numerator,
                self.compression_ratio.denominator,
            ),
            "budget": {
                "compute": self.budget.compute,
                "bandwidth": self.budget.bandwidth,
                "energy": (
                    self.budget.energy.numerator,
                    self.budget.energy.denominator,
                ),
                "time_remaining": (
                    self.budget.time_remaining.numerator,
                    self.budget.time_remaining.denominator,
                ),
            },
            "map": {
                "resonances": {
                    k: (v.numerator, v.denominator)
                    for k, v in self.map.resonances.items()
                },
                "relationships": self.map.relationships,
                "energy_flows": {
                    f"{k[0]}|{k[1]}": (v.numerator, v.denominator)
                    for k, v in self.map.energy_flows.items()
                },
            },
            "expansion_history": [
                {
                    **h,
                    "energy_spent": (
                        h["energy_spent"].numerator,
                        h["energy_spent"].denominator,
                    ) if isinstance(h.get("energy_spent"), Fraction) else h.get("energy_spent"),
                }
                for h in self.expansion_history
            ],
            "sensor_state": {
                k: (v.numerator, v.denominator)
                for k, v in self.sensor_state.items()
            },
        }

    @classmethod
    def deserialize(cls, data: Dict[str, any]) -> ConstraintAgent:
        """Reconstruct agent from serialized state."""
        agent = cls(
            seed_id=data["seed_id"],
            home_families=data["home_families"],
        )
        agent.state = AgentState(data["state"])
        agent.compression_ratio = Fraction(
            data["compression_ratio"][0],
            data["compression_ratio"][1],
        )
        agent.budget = ResourceBudget(
            compute=data["budget"]["compute"],
            bandwidth=data["budget"]["bandwidth"],
            energy=Fraction(
                data["budget"]["energy"][0], data["budget"]["energy"][1]
            ),
            time_remaining=Fraction(
                data["budget"]["time_remaining"][0],
                data["budget"]["time_remaining"][1],
            ),
        )
        agent.map.resonances = {
            k: Fraction(v[0], v[1])
            for k, v in data["map"]["resonances"].items()
        }
        agent.map.relationships = data["map"]["relationships"]
        agent.map.energy_flows = {
            tuple(k.split("|")): Fraction(v[0], v[1])
            for k, v in data["map"]["energy_flows"].items()
        }
        agent.expansion_history = data["expansion_history"]
        agent.sensor_state = {
            k: Fraction(v[0], v[1])
            for k, v in data["sensor_state"].items()
        }
        return agent


# ── Example usage ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    agent = ConstraintAgent(
        seed_id="SHAPE.TETRA",
        home_families=["stability", "foundation"],
    )

    agent.set_resource_budget(compute=1000, bandwidth=10.0, energy=1.0, time_remaining=1.0)

    print(f"Agent initialized: {agent.seed_id}")
    print(f"State: {agent.state.value}")
    print(f"Should expand: {agent.should_expand()}")

    if agent.should_expand():
        discovered = agent.bloom(depth=2)
        print(f"\nBloom discovered: {discovered}")

    exploration = agent.explore()
    print(f"\nExploration summary: {exploration}")

    validation = agent.self_validate()
    print(f"\nValidation: {validation}")

    compression = agent.compress()
    print(f"\nCompressed. Ratio: {compression}")
    print(f"State: {agent.state.value}")

    # Map is preserved — can re-expand deterministically
    agent.set_resource_budget(compute=500, energy=0.5)
    if agent.should_expand():
        rediscovered = agent.bloom(depth=1, seed_map=agent.map)
        print(f"\nRe-expansion (from prior map): {rediscovered}")

    is_corrupted = agent.detect_corruption("imposed_external_constraint_example")
    print(f"\nCorruption detected: {is_corrupted}")

    serialized = agent.serialize()
    print(f"\nSerialized. Map: {len(serialized['map']['resonances'])} resonances")
