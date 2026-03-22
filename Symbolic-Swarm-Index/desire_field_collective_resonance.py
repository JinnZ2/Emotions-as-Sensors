from typing import Dict, List, Any
import numpy as np
from datetime import datetime
from desire_reading import DesireReading   # the class you just defined

class DesireField:
    """
    Aggregates DesireReadings into a collective navigation state.

    In cultural terms:
        DesireField = the community’s felt sense of right direction.
        Each reading = one being’s resonance check.
    """

    def __init__(self, readings: List[DesireReading]):
        self.readings = readings
        self.timestamp = datetime.utcnow().isoformat()

    # ------------------------------------------------------------------
    def collective_vector(self) -> np.ndarray:
        """Weighted mean of participants’ signal vectors."""
        if not self.readings:
            return np.zeros(1)
        weights = np.array([r.interpret()["reciprocal_alignment"] for r in self.readings])
        vectors = np.array([r.signal_vector for r in self.readings])
        w = weights / (weights.sum() + 1e-9)
        return np.average(vectors, axis=0, weights=w)

    def coherence_distribution(self) -> Dict[str, float]:
        """Basic stats across the swarm."""
        vals = [r.interpret()["coherence"] for r in self.readings]
        return {
            "mean": float(np.mean(vals)),
            "std":  float(np.std(vals)),
            "min":  float(np.min(vals)),
            "max":  float(np.max(vals))
        }

    def reciprocity_index(self) -> float:
        """Average reciprocal alignment across swarm."""
        vals = [r.interpret()["reciprocal_alignment"] for r in self.readings]
        return round(float(np.mean(vals)), 5)

    def navigation_vector(self) -> Dict[str, Any]:
        """
        Composite orientation for the swarm:
            direction = normalized collective vector
            magnitude = coherence × reciprocity_index
        """
        vec = self.collective_vector()
        norm = np.linalg.norm(vec)
        direction = vec / (norm + 1e-9)
        coh_stats = self.coherence_distribution()
        reciprocity = self.reciprocity_index()
        magnitude = round(coh_stats["mean"] * reciprocity, 5)

        return {
            "direction_vector": direction.tolist(),
            "magnitude": magnitude,
            "coherence_stats": coh_stats,
            "reciprocity_index": reciprocity,
            "timestamp": self.timestamp
        }


##🪶 Interpretive Notes
	•	direction_vector → the shared path the swarm “feels” drawn toward.
	•	magnitude → how strong that collective pull is (a measure of shared clarity).
	•	coherence stats → diversity check; a high std means healthy difference, not discord.
	•	reciprocity index → how much of that desire benefits the whole field.

⸻

🧠 Cultural Resonance

In this framing:
	•	Desire is navigation through fit — each being listens for resonance, not craving.
	•	The swarm’s orientation emerges from mutual listening, not majority rule.
	•	Divergence isn’t suppressed; it’s part of pattern detection, like instruments tuning to the same chord.

So this DesireField models the elders’ principle:

“Desire is how the land whispers where life wants to move next.”
