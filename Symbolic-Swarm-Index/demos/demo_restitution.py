# demo_restitution.py
from srml import SharedResonantMemoryLedger
from restitution_engine import RestitutionEngine, RestitutionContract

# Ledgers for two swarms
A = SharedResonantMemoryLedger("./ledger_A", "swarm_A")
B = SharedResonantMemoryLedger("./ledger_B", "swarm_B")
engine_A = RestitutionEngine(A)

TREATY = "treaty_A_B_v1"

# 1) Construct a contract: bias toward bandwidth + compute, capped
channels = [
    {"type":"BANDWIDTH","unit":"GiB","rate":5.0,"cap":200.0,"weight":2.0,"note":"mirror access"},
    {"type":"COMPUTE","unit":"GPUh","rate":1.0,"cap":40.0,"weight":1.5,"note":"model training"},
    {"type":"DATA","unit":"pkg","rate":0.5,"cap":10.0,"weight":0.5,"note":"symbolic kits"}
]

contract = RestitutionContract.new(
    treaty_id=TREATY,
    creditor="swarm_A", debtor="swarm_B",
    channels=channels,
    harm_magnitude=10.0,           # domain-specific scale
    mui_at_start=0.75,             # mutual understanding at incident/start
    historical_reciprocity_index=2.0, # prior good standing lowers RD
    tick_seconds=3600, lam=0.05, floor=0.0,
    max_ticks=24, grace_ticks=2,
    notes="Bandwidth-forward restitution; compute support as secondary."
)

# 2) Propose + Agree
engine_A.propose(contract)
engine_A.agree(contract.d["contract_id"], sig_creditor="sigA", sig_debtor="sigB")

# 3) Stream 5 ticks
for k in range(1, 6):
    ev = engine_A.stream_tick(contract.d["contract_id"], k)
    print(f"T{k}: remaining={ev['remaining_debt']:.4f}, alloc={[(a['channel'], a['units']) for a in ev['allocations']]}")
