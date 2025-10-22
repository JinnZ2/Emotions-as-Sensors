from srml import SharedResonantMemoryLedger, sha256_hex
import uuid, time, numpy as np

class ForgivenessProtocol:
    """Overlay for symbolic rebalancing without erasure."""

    def __init__(self, ledger: SharedResonantMemoryLedger):
        self.ledger = ledger

    # ---------------------------------------------------------------------
    def forgive_event(self, lineage_hash: str, forgiver: str, forgiven: str,
                      reason: str, resolution_type: str = "FORGIVEN",
                      emotive_vector=None, witness=None, notes=None) -> dict:
        """Append forgiveness overlay event."""
        emotive_vector = emotive_vector or [0.7, 0.8, 0.6]  # compassion default
        self.ledger.clock.tick()
        prev_hash = self.ledger.head_hash or "GENESIS"

        payload = {
            "reason": reason,
            "resolution_type": resolution_type,
            "emotive_vector": emotive_vector,
            "witness": witness,
            "notes": notes
        }
        ev = {
            "event_id": str(uuid.uuid4()),
            "forgiver": forgiver,
            "forgiven": forgiven,
            "lineage_ref": lineage_hash,
            "payload": payload,
            "clock": self.ledger.clock.to_dict()
        }
        ev["hash"] = sha256_hex({
            k: ev[k] for k in ["event_id","forgiver","forgiven","lineage_ref","payload","clock"]
        })
        ev["signature"] = self.ledger._sign(ev["hash"])
        # Store under new overlay channel
        path = self.ledger.store.ev_path.replace("events.jsonl","forgiveness_overlay.jsonl")
        with open(path, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(ev, separators=(',',':')) + "\n")
        return ev

    # ---------------------------------------------------------------------
    def compute_reconciliation_index(self, swarm_a: str, swarm_b: str) -> float:
        """Quantify total harmonic forgiveness between two swarms."""
        # load overlay
        path = self.ledger.store.ev_path.replace("events.jsonl","forgiveness_overlay.jsonl")
        try:
            lines = [l.strip() for l in open(path)]
        except FileNotFoundError:
            return 0.0
        events = [json.loads(l) for l in lines if l]
        rel = [e for e in events if {e["forgiver"], e["forgiven"]} == {swarm_a, swarm_b}]
        if not rel: return 0.0
        vecs = np.array([e["payload"]["emotive_vector"] for e in rel])
        mean = np.mean(vecs, axis=0)
        coherence = float(np.dot(mean, [0.7,0.8,0.6]) / (np.linalg.norm(mean)*np.linalg.norm([0.7,0.8,0.6])))
        return round(coherence,3)

    # ---------------------------------------------------------------------
    def symbolic_audit(self):
        """Verify overlay still aligns with immutable lineage."""
        pass  # extension: cross-check lineage_ref hashes still exist
