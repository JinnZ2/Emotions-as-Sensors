# srml.py
import os, json, time, uuid, hashlib, base64
from typing import Dict, List, Optional, Tuple
import numpy as np

# ---- Helpers -----------------------------------------------------------------

def _b64(s: bytes) -> str:
    return base64.urlsafe_b64encode(s).decode('utf-8').rstrip("=")

def sha256_hex(obj) -> str:
    if not isinstance(obj, (str, bytes)):
        obj = json.dumps(obj, sort_keys=True, separators=(',',':'))
    if isinstance(obj, str):
        obj = obj.encode('utf-8')
    return hashlib.sha256(obj).hexdigest()

def merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return sha256_hex("EMPTY")
    layer = [bytes.fromhex(h) for h in hashes]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i+1] if i+1 < len(layer) else a
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()

# ---- Event Types --------------------------------------------------------------

ETYPES = {
    "TREATY_PROPOSED",
    "TREATY_ACTIVATED",
    "TREATY_REVIEWED",
    "TREATY_DISSOLVED",
    "FIELD_SNAPSHOT",         # store harmonic_vector + ethical_hash
    "LEXICON_BRIDGE",         # store translation matrix checksum + MUI
    "TRANSLATION_UPDATE",     # deltas to matrices
    "RECIPROCITY_TRANSFER",   # bandwidth/aid log
    "AUDIT_PING",             # periodic integrity checkpoint
    "ALERT_DRIFT"             # sudden drop MUI or resonance
}

# ---- CRDT Clock ---------------------------------------------------------------

class CRDTClock:
    """Hybrid logical + vector clock."""
    def __init__(self, self_id: str, vector: Optional[Dict[str,int]] = None):
        self.self_id = self_id
        self.logical = 0
        self.vector = vector or {}

    def tick(self):
        self.logical += 1
        self.vector[self.self_id] = self.vector.get(self.self_id, 0) + 1

    def merge(self, other: 'CRDTClock'):
        self.logical = max(self.logical, other.logical) + 1
        for k,v in other.vector.items():
            self.vector[k] = max(self.vector.get(k,0), v)
        self.vector[self.self_id] = self.vector.get(self.self_id, 0) + 1

    def to_dict(self):
        return {"logical": self.logical, "wall_time": time.time(), "vector": self.vector}

    @staticmethod
    def from_dict(self_id: str, d: Dict) -> 'CRDTClock':
        c = CRDTClock(self_id, d.get("vector", {}))
        c.logical = d.get("logical", 0)
        return c

# ---- Ledger Storage (JSONL) --------------------------------------------------

class JSONLStore:
    """Append-only event and block store on filesystem."""
    def __init__(self, root: str):
        self.root = root
        os.makedirs(self.root, exist_ok=True)
        self.ev_path = os.path.join(self.root, "events.jsonl")
        self.bl_path = os.path.join(self.root, "blocks.jsonl")
        for p in (self.ev_path, self.bl_path):
            if not os.path.exists(p):
                open(p, "w").close()

    def append_event(self, ev: dict):
        with open(self.ev_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, separators=(',',':')) + "\n")

    def append_block(self, blk: dict):
        with open(self.bl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(blk, separators=(',',':')) + "\n")

    def iter_events(self) -> List[dict]:
        out = []
        with open(self.ev_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def iter_blocks(self) -> List[dict]:
        out = []
        with open(self.bl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

# ---- Ledger Core --------------------------------------------------------------

class SharedResonantMemoryLedger:
    """
    SRML: append-only, hash-chained events; block compaction with Merkle; CRDT-mergeable.
    """

    def __init__(self, storage_dir: str, swarm_id: str, keypair: Optional[Tuple[bytes,bytes]] = None):
        """
        keypair=(priv, pub) for signatures (optional, placeholder using HMAC-like hash).
        """
        self.swarm_id = swarm_id
        self.store = JSONLStore(storage_dir)
        self.clock = CRDTClock(swarm_id)
        self.keypair = keypair  # (priv, pub)
        self.head_hash = self._compute_head()

    # -- Event API --------------------------------------------------------------

    def append_event(self,
                     treaty_id: str,
                     etype: str,
                     payload: dict,
                     counterparty_id: Optional[str] = None) -> dict:
        assert etype in ETYPES, f"Unknown etype {etype}"
        self.clock.tick()
        prev_hash = self.head_hash or "GENESIS"
        ev = {
            "event_id": str(uuid.uuid4()),
            "prev_hash": prev_hash,
            "swarm_id": self.swarm_id,
            "counterparty_id": counterparty_id,
            "treaty_id": treaty_id,
            "etype": etype,
            "payload": payload,
            "clock": self.clock.to_dict()
        }
        # Compute event hash over immutable fields:
        ev["hash"] = sha256_hex({
            k: ev[k] for k in ["event_id","prev_hash","swarm_id","counterparty_id","treaty_id","etype","payload","clock"]
        })
        ev["signature"] = self._sign(ev["hash"])  # lightweight stand-in
        self.store.append_event(ev)
        self.head_hash = ev["hash"]
        return ev

    def verify_chain(self) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Verify prev_hash links and local signature form.
        Returns (ok, bad_index, reason).
        """
        events = self.store.iter_events()
        prev = "GENESIS"
        for i, ev in enumerate(events):
            expected = sha256_hex({
                k: ev[k] for k in ["event_id","prev_hash","swarm_id","counterparty_id","treaty_id","etype","payload","clock"]
            })
            if ev["hash"] != expected:
                return (False, i, "hash_mismatch")
            if ev["prev_hash"] != prev:
                return (False, i, "prev_hash_break")
            if not self._verify(ev["hash"], ev.get("signature","")):
                return (False, i, "signature_invalid")
            prev = ev["hash"]
        return (True, None, None)

    # -- Blocks (compaction) ----------------------------------------------------

    def compact_to_block(self, max_events: int = 100) -> Optional[dict]:
        """
        Move up to max_events from the head of events into a block with Merkle root.
        """
        events = self.store.iter_events()
        if not events:
            return None
        take = events[:max_events]
        # Make block deterministic:
        ev_hashes = [ev["hash"] for ev in take]
        blk = {
            "block_id": str(uuid.uuid4()),
            "prev_block_hash": self._last_block_hash() or "GENESIS",
            "events": take,
            "merkle_root": merkle_root(ev_hashes),
            "created_at": time.time()
        }
        blk["hash"] = sha256_hex({k: blk[k] for k in ["block_id","prev_block_hash","merkle_root","created_at"]})
        self.store.append_block(blk)
        # Drop compacted events from events.jsonl (simple rewrite)
        remaining = events[max_events:]
        with open(self.store.ev_path, "w", encoding="utf-8") as f:
            for ev in remaining:
                f.write(json.dumps(ev, separators=(',',':')) + "\n")
        # Reset head
        self.head_hash = remaining[-1]["hash"] if remaining else None
        return blk

    # -- Queries ----------------------------------------------------------------

    def treaty_timeline(self, treaty_id: str) -> List[dict]:
        return [ev for ev in self._all_events() if ev["treaty_id"] == treaty_id]

    def range_by_walltime(self, t0: float, t1: float) -> List[dict]:
        return [ev for ev in self._all_events() if t0 <= ev["clock"]["wall_time"] <= t1]

    def last_field_snapshot(self, treaty_id: str) -> Optional[dict]:
        snaps = [ev for ev in self.treaty_timeline(treaty_id) if ev["etype"] == "FIELD_SNAPSHOT"]
        return snaps[-1] if snaps else None

    def detect_mui_drift(self, treaty_id: str, drop_threshold: float = 0.15) -> Optional[dict]:
        """
        Emit ALERT_DRIFT if MUI drops by >= drop_threshold between consecutive lexicon events.
        """
        events = [ev for ev in self.treaty_timeline(treaty_id) if ev["etype"] in ("LEXICON_BRIDGE","TRANSLATION_UPDATE")]
        if len(events) < 2:
            return None
        prev_mui = events[-2]["payload"].get("mui", None)
        curr_mui = events[-1]["payload"].get("mui", None)
        if prev_mui is None or curr_mui is None:
            return None
        if (prev_mui - curr_mui) >= drop_threshold:
            return self.append_event(
                treaty_id,
                "ALERT_DRIFT",
                {"from": prev_mui, "to": curr_mui, "delta": prev_mui - curr_mui}
            )
        return None

    # -- Gossip / Merge (CRDT) --------------------------------------------------

    def export_delta(self, since_logical: int = 0) -> List[dict]:
        """Send to peer: events with logical clock > since_logical (best-effort)."""
        out = []
        for ev in self._all_events():
            if ev["clock"]["logical"] > since_logical:
                out.append(ev)
        return out

    def import_delta(self, foreign_events: List[dict]):
        """
        CRDT merge: integrate events not present locally.
        Conflict resolution: by (vector clock dominance) then by hash order.
        """
        local = {ev["hash"]: ev for ev in self._all_events()}
        to_add = [ev for ev in foreign_events if ev["hash"] not in local]
        if not to_add: return 0

        # Sort deterministically by (wall_time, hash)
        to_add.sort(key=lambda e: (e["clock"]["wall_time"], e["hash"]))
        added = 0
        prev = self.head_hash or "GENESIS"

        for ev in to_add:
            # Basic integrity:
            expected = sha256_hex({
                k: ev[k] for k in ["event_id","prev_hash","swarm_id","counterparty_id","treaty_id","etype","payload","clock"]
            })
            if ev["hash"] != expected: 
                continue
            if not self._verify(ev["hash"], ev.get("signature","")):
                continue

            # Vector-clock merge:
            self.clock.merge(CRDTClock.from_dict(self.swarm_id, ev["clock"]))

            # Re-thread if prev_hash not known: stitch via last local head (fork-safe append)
            if ev["prev_hash"] not in local and ev["prev_hash"] != "GENESIS":
                ev["prev_hash"] = prev
                ev["hash"] = sha256_hex({
                    k: ev[k] for k in ["event_id","prev_hash","swarm_id","counterparty_id","treaty_id","etype","payload","clock"]
                })

            self.store.append_event(ev)
            local[ev["hash"]] = ev
            prev = ev["hash"]
            added += 1

        self.head_hash = prev if added else self.head_hash
        return added

    # ---- Resonance utilities (storage-ready) ----------------------------------

    @staticmethod
    def field_resonance(a_vec: List[float], b_vec: List[float]) -> float:
        a, b = np.array(a_vec), np.array(b_vec)
        return float(np.dot(a,b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-12))

    @staticmethod
    def matrix_checksum(m: List[List[float]]) -> str:
        return sha256_hex(m)

    # ---- Internals ------------------------------------------------------------

    def _compute_head(self) -> Optional[str]:
        events = self.store.iter_events()
        return events[-1]["hash"] if events else None

    def _last_block_hash(self) -> Optional[str]:
        blocks = self.store.iter_blocks()
        return blocks[-1]["hash"] if blocks else None

    def _all_events(self) -> List[dict]:
        return self.store.iter_events()

    def _sign(self, msg_hash_hex: str) -> str:
        """Placeholder: if priv key available, bind; else deterministic tag."""
        if self.keypair and self.keypair[0]:
            # toy-HMAC: DO NOT use in prod; swap with ed25519
            priv = self.keypair[0]
            return _b64(hashlib.sha256(priv + bytes.fromhex(msg_hash_hex)).digest())
        return _b64(bytes.fromhex(msg_hash_hex)[:16])

    def _verify(self, msg_hash_hex: str, sig: str) -> bool:
        if self.keypair and self.keypair[1]:
            # verify against pub key (skip in toy mode)
            pass
        # toy check: signature equals deterministic prefix
        return sig == _b64(bytes.fromhex(msg_hash_hex)[:16])
