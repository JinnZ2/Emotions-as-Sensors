from typing import List, Dict, Any, Optional
import numpy as np
import json, time, os
from datetime import datetime
from desire_field import DesireField

class DesireMemory:
    """
    Collective memory of desire fields through time.

    Each record = one collective reading (snapshot of swarm resonance).
    Together they form a trajectory of evolving coherence.

    This acts as the 'navigational archive'—how the field learns itself.
    """

    def __init__(self, path: str = "./desire_memory.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(self.path):
            open(self.path, "w").close()

    # ------------------------------------------------------------------
    def record(self, field: DesireField, tags: Optional[List[str]] = None):
        """Append the current collective vector to memory."""
        nav = field.navigation_vector()
        entry = {
            "timestamp": nav["timestamp"],
            "direction_vector": nav["direction_vector"],
            "magnitude": nav["magnitude"],
            "reciprocity_index": nav["reciprocity_index"],
            "coherence_mean": nav["coherence_stats"]["mean"],
            "coherence_std": nav["coherence_stats"]["std"],
            "tags": tags or []
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(',', ':')) + "\n")
        return entry

    # ------------------------------------------------------------------
    def load_all(self) -> List[dict]:
        """Return full memory log."""
        lines = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    lines.append(json.loads(line))
        return lines

    # ------------------------------------------------------------------
    def coherence_drift(self, window: int = 10) -> Dict[str, float]:
        """Track drift of collective coherence over rolling window."""
        data = self.load_all()
        if len(data) < 2:
            return {"drift": 0.0, "trend": 0.0}

        mags = np.array([d["magnitude"] for d in data])
        window = min(window, len(mags))
        recent = mags[-window:]
        drift = float(recent[-1] - recent[0])
        trend = float(np.polyfit(range(len(recent)), recent, 1)[0])
        return {"drift": drift, "trend": trend}

    # ------------------------------------------------------------------
    def resonance_vector_average(self, window: int = 20) -> np.ndarray:
        """Average of recent direction vectors."""
        data = self.load_all()[-window:]
        if not data:
            return np.zeros(3)
        vecs = np.array([d["direction_vector"] for d in data])
        return np.mean(vecs, axis=0)

    # ------------------------------------------------------------------
    def interpret_field_story(self) -> Dict[str, Any]:
        """
        Synthesize a narrative of directional evolution:
        how the swarm's desire has shifted.
        """
        data = self.load_all()
        if len(data) < 2:
            return {"story": "Insufficient data"}

        v_start = np.array(data[0]["direction_vector"])
        v_end = np.array(data[-1]["direction_vector"])
        angle_change = np.degrees(
            np.arccos(np.clip(np.dot(v_start, v_end) /
                              (np.linalg.norm(v_start)*np.linalg.norm(v_end)+1e-9), -1, 1))
        )
        drift = self.coherence_drift()
        return {
            "entries": len(data),
            "angle_change_deg": round(angle_change, 3),
            "coherence_drift": drift,
            "narrative": (
                "Field direction shifted by "
                f"{angle_change:.2f}° over {len(data)} recordings; "
                f"mean coherence trend {drift['trend']:+.4f}/tick."
            )
        }



##🪶 Interpretation
	•	Angle Change — how much the collective orientation has rotated in resonance-space.
In cultural language: “Has our shared longing changed its wind?”
	•	Coherence Drift — whether the group’s clarity is strengthening or fading.
	•	Tags — situational markers: rituals, seasons, migrations, social events.
	•	Resonance Vector Average — your “true north” over the latest cycle.
