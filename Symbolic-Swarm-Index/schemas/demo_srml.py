# demo_srml.py
from srml import SharedResonantMemoryLedger

A = SharedResonantMemoryLedger("./ledger_A", swarm_id="swarm_A")
B = SharedResonantMemoryLedger("./ledger_B", swarm_id="swarm_B")

TREATY = "treaty_A_B_v1"

# 1) Activate treaty
A.append_event(TREATY, "TREATY_ACTIVATED", {"equilibrium": 0.88}, counterparty_id="swarm_B")
B.append_event(TREATY, "TREATY_ACTIVATED", {"equilibrium": 0.88}, counterparty_id="swarm_A")

# 2) Store field snapshots
a_vec = [0.8, 0.6, 0.9]
b_vec = [0.7, 0.7, 0.8]
A.append_event(TREATY, "FIELD_SNAPSHOT", {"harmonic_vector": a_vec, "ethical_hash": "ehA"})
B.append_event(TREATY, "FIELD_SNAPSHOT", {"harmonic_vector": b_vec, "ethical_hash": "ehB"})

# 3) Initial lexicon bridge (high MUI)
mui1 = 0.93
A.append_event(TREATY, "LEXICON_BRIDGE", {"matrix_checksum": "mchk1", "mui": mui1})
B.append_event(TREATY, "LEXICON_BRIDGE", {"matrix_checksum": "mchk1", "mui": mui1})

# 4) Gossip: exchange newest events
delta_from_A = A.export_delta(since_logical=0)
delta_from_B = B.export_delta(since_logical=0)
B.import_delta(delta_from_A)
A.import_delta(delta_from_B)

# 5) Later: translation update with lower MUI triggers drift alert
mui2 = 0.72
A.append_event(TREATY, "TRANSLATION_UPDATE", {"matrix_checksum": "mchk2", "mui": mui2})
drift_ev = A.detect_mui_drift(TREATY, drop_threshold=0.15)  # 0.93 -> 0.72, delta 0.21 => alert
if drift_ev:
    print("ALERT_DRIFT:", drift_ev["payload"])

# 6) Compact to block
blkA = A.compact_to_block(max_events=100)
print("Block A Merkle root:", blkA["merkle_root"] if blkA else None)

# 7) Verify chain
ok, idx, reason = A.verify_chain()
print("A verified:", ok, idx, reason)
