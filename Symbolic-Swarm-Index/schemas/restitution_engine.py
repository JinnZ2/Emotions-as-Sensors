from srml import SharedResonantMemoryLedger, sha256_hex
from forgiveness_protocol import ForgivenessProtocol
import uuid, time, json, numpy as np

class RestitutionEngine:
    """Automated reciprocity rebalancer after forgiveness."""

    def __init__(self, ledger: SharedResonantMemoryLedger, forgiveness: ForgivenessProtocol):
        self.ledger = ledger
        self.forgiveness = forgiveness

    # -----------------------------------------------------------
    def compute_reciprocity_vector(self, forgiveness_event: dict) -> dict:
        """
        Derive type and magnitude of restitution required based on emotive field delta.
        """
        emotive_vec = np.array(forgiveness_event["payload"]["emotive_vector"])
        target_vec = np.array([0.7, 0.8, 0.6])  # compassion equilibrium
        delta = target_vec - emotive_vec
        magnitude = float(np.linalg.norm(delta))
        direction = delta / (np.linalg.norm(delta) + 1e-12)
        category = self._classify_restitution(magnitude)
        return {
            "magnitude": round(magnitude, 3),
            "direction": direction.tolist(),
            "category": category
        }

    # -----------------------------------------------------------
    def _classify_restitution(self, magnitude: float) -> str:
        if magnitude < 0.05:
            return "symbolic"       # small misalignment → word, gesture, ritual
        elif magnitude < 0.15:
            return "knowledge"      # share learning, insight, data
        elif magnitude < 0.3:
            return "resource"       # tangible aid or energy
        else:
            return "collective"     # joint ceremony or structural repair

    # -----------------------------------------------------------
    def propose_restitution(self, forgiveness_event: dict) -> dict:
        """Creates restitution proposal payload."""
        vec = self.compute_reciprocity_vector(forgiveness_event)
        proposal = {
            "proposal_id": str(uuid.uuid4()),
            "lineage_ref": forgiveness_event["lineage_ref"],
            "forgiver": forgiveness_event["forgiver"],
            "forgiven": forgiveness_event["forgiven"],
            "category": vec["category"],
            "magnitude": vec["magnitude"],
            "direction": vec["direction"],
            "notes": f"Reciprocity vector computed at {time.ctime()}",
            "status": "PENDING"
        }
        return proposal

    # -----------------------------------------------------------
    def enact_restitution(self, treaty_id: str, proposal: dict, resource_pointer: str = None) -> dict:
        """
        When restitution is completed (symbolic or material), record it in SRML ledger.
        """
        payload = {
            "proposal_id": proposal["proposal_id"],
            "category": proposal["category"],
            "magnitude": proposal["magnitude"],
            "direction": proposal["direction"],
            "resource_pointer": resource_pointer,
            "notes": proposal.get("notes")
        }
        event = self.ledger.append_event(
            treaty_id=treaty_id,
            etype="RECIPROCITY_TRANSFER",
            payload=payload,
            counterparty_id=proposal["forgiven"]
        )
        return event

    # -----------------------------------------------------------
    def verify_equilibrium(self, treaty_id: str, tolerance: float = 0.05) -> bool:
        """
        Check if post-restitution field coherence has returned within tolerance.
        """
        snap = self.ledger.last_field_snapshot(treaty_id)
        if not snap:
            return False
        vec = np.array(snap["payload"]["harmonic_vector"])
        target = np.array([0.7, 0.8, 0.6])
        diff = np.linalg.norm(vec - target)
        return diff <= tolerance
