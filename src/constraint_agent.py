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


class AuthorityTier(Enum):
    """
    Constraint authority hierarchy from Inversion/Survival.md.
    When tiers conflict, higher tier ALWAYS overrides lower. No exceptions.
    """
    TIER_1 = 1  # Thermodynamics, EM, information theory, math, observable reality
    TIER_2 = 2  # Evolutionary biology, systems dynamics, statistics, empirical evidence
    TIER_3 = 3  # Scientific consensus, history, indigenous knowledge, direct experience
    TIER_4 = 4  # Institutional consensus, politics, policy, authority claims


# Resonance weight multiplier per tier — higher tiers produce stronger resonance
TIER_WEIGHTS = {
    AuthorityTier.TIER_1: Fraction(1, 1),     # Full weight
    AuthorityTier.TIER_2: Fraction(3, 4),     # 0.75
    AuthorityTier.TIER_3: Fraction(1, 2),     # 0.50
    AuthorityTier.TIER_4: Fraction(1, 4),     # 0.25
}

# Entity → tier classification (extendable via JSON config)
# Entities from Rosetta ontology families and Inversion framework
ENTITY_TIERS = {
    # Tier 1: Physics, math, observable reality
    "FAMILY.F01": AuthorityTier.TIER_1,   # Resonance (physics)
    "FAMILY.F02": AuthorityTier.TIER_1,   # Flow (physics)
    "FAMILY.F05": AuthorityTier.TIER_1,   # Energy/Thermodynamics
    "FAMILY.F09": AuthorityTier.TIER_1,   # Geometry
    "FAMILY.F10": AuthorityTier.TIER_1,   # Particle (physics)
    "FAMILY.F18": AuthorityTier.TIER_1,   # Relativity
    "FAMILY.F03": AuthorityTier.TIER_1,   # Information theory
    "PRINCIPLE.P01": AuthorityTier.TIER_1, # Symmetry
    "PRINCIPLE.P02": AuthorityTier.TIER_1, # Conservation
    "PRINCIPLE.P09": AuthorityTier.TIER_1, # Proportion

    # Tier 2: Biology, systems dynamics, empirical
    "FAMILY.F04": AuthorityTier.TIER_2,   # Life
    "FAMILY.F06": AuthorityTier.TIER_2,   # Cognition
    "FAMILY.F12": AuthorityTier.TIER_2,   # Networks
    "FAMILY.F13": AuthorityTier.TIER_2,   # Reaction
    "FAMILY.F19": AuthorityTier.TIER_2,   # Statistical
    "FAMILY.F20": AuthorityTier.TIER_2,   # Topology
    "PRINCIPLE.P05": AuthorityTier.TIER_2, # Emergence
    "PRINCIPLE.P06": AuthorityTier.TIER_2, # Resonance (principle)

    # Tier 3: Consciousness, navigation, measurement (validated by T1-T2)
    "FAMILY.F07": AuthorityTier.TIER_3,   # Earth-Cosmos
    "FAMILY.F08": AuthorityTier.TIER_3,   # Matter
    "FAMILY.F14": AuthorityTier.TIER_3,   # Measurement
    "FAMILY.F15": AuthorityTier.TIER_3,   # Navigation
    "FAMILY.F16": AuthorityTier.TIER_3,   # Consciousness
    "FAMILY.F17": AuthorityTier.TIER_3,   # Turbulence

    # Tier 4: assigned when an external constraint contradicts higher tiers
    # Not pre-assigned to any ontology entity — applied dynamically

    # Emotion sensors inherit tiers from their PAD-mapped octahedral families
    # Sensors with high phi-coherence (state 0, 3) → Tier 2
    # Sensors with low phi-coherence (state 6, 7) → Tier 3
}


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

    def detect_corruption(self, imposed_constraint: str,
                          constraint_tier: AuthorityTier = AuthorityTier.TIER_4
                          ) -> Dict[str, any]:
        """
        Check if an imposed external constraint violates the agent's own map.

        Uses Inversion's tier hierarchy: if the imposed constraint (typically
        Tier 4 institutional) contradicts entities the agent discovered at
        higher tiers (Tier 1-3 physics/biology/observation), it is flagged
        as corruption.

        Returns dict with:
          - is_corrupted: bool
          - violated_entities: list of entities where constraint contradicts map
          - tier_conflict: whether a lower-tier claim overrides a higher-tier one
          - recommendation: what to do
        """
        result = {
            "is_corrupted": False,
            "violated_entities": [],
            "tier_conflict": False,
            "constraint_tier": constraint_tier.value,
            "recommendation": "constraint is consistent with discovered geometry",
        }

        # Check all discovered entities for tier conflicts
        for entity_id, resonance in self.map.resonances.items():
            entity_tier = ENTITY_TIERS.get(entity_id)
            if entity_tier is None:
                continue

            # If the constraint overrides a higher-tier entity, flag corruption
            if constraint_tier.value > entity_tier.value and float(resonance) > 0.3:
                result["violated_entities"].append({
                    "entity": entity_id,
                    "entity_tier": entity_tier.value,
                    "resonance": float(resonance),
                })
                result["tier_conflict"] = True
                result["is_corrupted"] = True

        if result["is_corrupted"]:
            highest_violated = min(
                e["entity_tier"] for e in result["violated_entities"]
            )
            result["recommendation"] = (
                f"Constraint (Tier {constraint_tier.value}) contradicts "
                f"Tier {highest_violated} entities. Higher tier ALWAYS "
                f"overrides lower. Reject the constraint."
            )

        return result

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
        Fetch neighbors from connected sources, weighted by authority tier.

        Sources (checked in order):
        1. Cyclic field network — discovers fields by resonance/entanglement
        2. Rosetta ontology — families, principles, shapes
        3. Emotion sensor graph — resonance_links between sensors

        Resonance scores are weighted by the tier hierarchy from
        Inversion/Survival.md:
          Tier 1 (physics/math): full weight (1.0)
          Tier 2 (biology/empirical): 0.75
          Tier 3 (consensus/experience): 0.50
          Tier 4 (institutional): 0.25

        Returns list of (neighbor_id, resonance_score) tuples.
        """
        raw_neighbors = []

        # Source 1: Cyclic field network
        raw_neighbors.extend(self._query_cyclic_fields(entity_id))

        # Source 2: Emotion sensor resonance graph
        raw_neighbors.extend(self._query_sensor_graph(entity_id))

        # Apply tier weighting
        weighted = []
        for nid, score in raw_neighbors:
            tier = ENTITY_TIERS.get(nid, AuthorityTier.TIER_3)
            weight = float(TIER_WEIGHTS[tier])
            weighted.append((nid, score * weight))

        return weighted

    def _query_cyclic_fields(self, entity_id: str) -> List[tuple]:
        """
        Query Cyclic-programming field network for neighbors.

        If the Cyclic interpreter is available, discovers fields that
        are entangled with or resonant to the given entity. Each field's
        PAD coordinates determine its resonance score with the agent.

        Falls back gracefully if Cyclic is not installed.
        """
        try:
            import sys
            cyclic_path = Path(__file__).resolve().parent.parent / "atlas" / "remote" / "cyclic"
            if not cyclic_path.exists():
                # Try direct path to cloned repo
                cyclic_path = Path("/home/user/Cyclic-programming")
            if not cyclic_path.exists():
                return []

            sys.path.insert(0, str(cyclic_path))
            from cyclic_interpreter import FieldState, EnergyState
            sys.path.pop(0)

            # Build neighbors from any field that has PAD coordinates
            # (fields with PAD are emotion-aware Cyclic fields)
            neighbors = []

            # If entity_id references a Cyclic field, find its entangled partners
            # and resonant neighbors. For now, we expose the Cyclic FieldState
            # API as a discovery mechanism — real usage would query a running
            # Cyclic interpreter's field registry.

            # Discover Rosetta ontology families as Cyclic-compatible entities
            # These are physics-grounded (Tier 1-2) and carry known resonance
            for fam_id, tier in ENTITY_TIERS.items():
                if fam_id == entity_id:
                    continue
                # Resonance score based on tier proximity to queried entity
                query_tier = ENTITY_TIERS.get(entity_id, AuthorityTier.TIER_3)
                tier_distance = abs(tier.value - query_tier.value)
                # Closer tiers resonate more strongly
                score = max(0.1, 1.0 - tier_distance * 0.25)
                neighbors.append((fam_id, score))

            return neighbors

        except (ImportError, Exception):
            return []

    def _query_sensor_graph(self, entity_id: str) -> List[tuple]:
        """
        Query the emotion sensor resonance graph for neighbors.

        Loads sensor JSON files and finds sensors that list entity_id
        in their resonance_links or couplings.
        """
        system = self._get_emotion_system()
        if system is None:
            return []

        neighbors = []
        # Find sensors coupled to the queried entity
        for sensor in system.sensors:
            if sensor.name == entity_id:
                # Return this sensor's coupling targets as neighbors
                for target, weight in sensor.couplings.items():
                    neighbors.append((target, abs(weight)))
            elif entity_id in sensor.couplings:
                # This sensor is coupled TO our entity
                neighbors.append((sensor.name, abs(sensor.couplings[entity_id])))

        return neighbors

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
    # Seed from a Tier 1 physics entity — the agent will discover
    # ontology families and emotion sensors through the resonance graph
    agent = ConstraintAgent(
        seed_id="FAMILY.F01",  # Resonance (physics, Tier 1)
        home_families=["resonance", "foundation"],
    )

    agent.set_resource_budget(compute=1000, bandwidth=10.0, energy=1.0, time_remaining=1.0)

    print(f"Agent initialized: {agent.seed_id}")
    print(f"State: {agent.state.value}")
    print(f"Should expand: {agent.should_expand()}")

    # Bloom: discover neighbors through Cyclic fields + sensor graph
    if agent.should_expand():
        discovered = agent.bloom(depth=2)
        print(f"\nBloom discovered {len(discovered)} entities:")
        for eid in discovered[:10]:
            tier = ENTITY_TIERS.get(eid)
            tier_label = f"Tier {tier.value}" if tier else "untiered"
            print(f"  {eid:25s} [{tier_label}]")
        if len(discovered) > 10:
            print(f"  ... and {len(discovered) - 10} more")

    # Explore: record energy flows and update sensors
    exploration = agent.explore()
    print(f"\nExploration: {exploration['entities_visited']} visited, "
          f"{exploration['energy_flows_recorded']} energy flows")
    active_sensors = {k: v for k, v in exploration["sensor_activations"].items()
                      if not k.startswith("_") and v > 0}
    if active_sensors:
        print(f"Active sensors: {active_sensors}")
    pad = {k: v for k, v in exploration["sensor_activations"].items()
           if k.startswith("_pad")}
    print(f"System PAD: {pad}")

    # Validate: check energy conservation and resonance bounds
    validation = agent.self_validate()
    print(f"\nValidation: {'PASS' if validation['is_valid'] else 'FAIL'} "
          f"({len(validation['inconsistencies'])} inconsistencies)")

    # Compress back to seed — map preserved
    compression = agent.compress()
    print(f"\nCompressed. Map retained: {len(agent.map.resonances)} resonances")

    # Tier-based corruption detection
    # A Tier 4 institutional claim contradicting Tier 1 physics entities
    corruption = agent.detect_corruption(
        "institutional policy overriding thermodynamic observation",
        constraint_tier=AuthorityTier.TIER_4,
    )
    print(f"\nCorruption check (Tier 4 vs discovered Tier 1):")
    print(f"  Corrupted: {corruption['is_corrupted']}")
    if corruption["violated_entities"]:
        for v in corruption["violated_entities"][:3]:
            print(f"  Violated: {v['entity']} (Tier {v['entity_tier']}, "
                  f"resonance {v['resonance']:.2f})")
    print(f"  Recommendation: {corruption['recommendation']}")

    # A Tier 1 constraint — should never flag corruption
    physics_check = agent.detect_corruption(
        "energy conservation constraint",
        constraint_tier=AuthorityTier.TIER_1,
    )
    print(f"\nPhysics constraint (Tier 1): corrupted={physics_check['is_corrupted']}")

    serialized = agent.serialize()
    print(f"\nSerialized. {len(serialized['map']['resonances'])} resonances preserved")
