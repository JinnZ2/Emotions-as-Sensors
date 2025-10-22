# restitution_engine.py
import time, uuid, json
import numpy as np
from typing import List, Dict, Optional
from srml import SharedResonantMemoryLedger, sha256_hex

# --- Core math ---------------------------------------------------------------

def resonance_debt(harm_magnitude: float,
                   mui_at_harm: float,
                   historical_reciprocity_index: float = 0.0,
                   penalty: float = 1.0) -> float:
    """
    Resonance Debt (RD) is baseline obligation to restore field coherence.
    RD ↑ with harm; RD ↓ with prior reciprocity and higher mutual understanding at time of harm.
    Simple form (bounded positive):
    RD = penalty * harm * (1 + max(0, 0.5 - mui)) / (1 + HRI)
    """
    mui_term = 1.0 + max(0.0, 0.5 - mui_at_harm)
    return float(penalty * harm_magnitude * mui_term / (1.0 + max(0.0, historical_reciprocity_index)))

def exponential_decay(value0: float, lam: float, k: int, floor: float = 0.0) -> float:
    """Remaining value after k ticks of exp decay, bounded below by floor."""
    return max(floor, value0 * np.exp(-lam * k))

# --- Engine ------------------------------------------------------------------

class RestitutionContract:
    def __init__(self, contract: dict):
        self.d = contract

    @staticmethod
    def new(treaty_id: str, creditor: str, debtor: str,
            channels: List[dict],
            harm_magnitude: float, mui_at_start: float,
            historical_reciprocity_index: float,
            tick_seconds: int = 3600, lam: float = 0.02, floor: float = 0.0,
            max_ticks: Optional[int] = None, grace_ticks: int = 3, notes: Optional[str] = None) -> 'RestitutionContract':

        rd = resonance_debt(harm_magnitude, mui_at_start, historical_reciprocity_index)
        payload = {
            "contract_id": str(uuid.uuid4()),
            "treaty_id": treaty_id,
            "creditor": creditor,
            "debtor": debtor,
            "channels": channels,
            "metrics": {
                "resonance_debt": round(rd, 6),
                "mui_at_start": round(mui_at_start, 6),
                "harm_magnitude": round(harm_magnitude, 6),
                "historical_reciprocity_index": round(historical_reciprocity_index, 6)
            },
            "terms": {
                "tick_seconds": tick_seconds,
                "start_time": time.time(),
                "grace_ticks": grace_ticks,
                "decay": {"lambda": lam, "floor": floor},
                "max_ticks": max_ticks,
                "notes": notes or ""
            }
        }
        payload["hash"] = sha256_hex(payload)
        payload["signature_creditor"] = ""  # to be filled by parties
        payload["signature_debtor"]   = ""  # to be filled by parties
        return RestitutionContract(payload)

class RestitutionEngine:
    """
    Streamed reciprocity settlement across multiple channels with decay + fairness.
    Integrates with SRML event log.
    """
    def __init__(self, ledger: SharedResonantMemoryLedger):
        self.ledger = ledger
        self.contracts: Dict[str, RestitutionContract] = {}

    # -- Lifecycle -------------------------------------------------------------

    def propose(self, contract: RestitutionContract) -> dict:
        self.contracts[contract.d["contract_id"]] = contract
        return self.ledger.append_event(
            treaty_id=contract.d["treaty_id"],
            etype="RESTITUTION_PROPOSED",
            payload={"contract": contract.d},
            counterparty_id=contract.d["debtor"]
        )

    def agree(self, contract_id: str, sig_creditor: str, sig_debtor: str) -> dict:
        c = self.contracts[contract_id].d
        c["signature_creditor"] = sig_creditor
        c["signature_debtor"]   = sig_debtor
        c["hash"] = sha256_hex(c)
        return self.ledger.append_event(
            treaty_id=c["treaty_id"],
            etype="RESTITUTION_AGREED",
            payload={"contract_id": contract_id, "hash": c["hash"]},
            counterparty_id=c["debtor"]
        )

    # -- Allocation math -------------------------------------------------------

    def _tick_allocation(self, contract: dict, tick_index: int, remaining: float) -> List[dict]:
        """
        Allocate across channels by weights, bounded by per-tick rate and total cap.
        Greedy fair-share: each channel gets share ∝ weight, limited by min(rate, cap_left).
        """
        chans = contract["channels"]
        weights = np.array([max(1e-9, ch.get("weight", 1.0)) for ch in chans], dtype=float)
        weights = weights / weights.sum()

        rates = np.array([ch["rate"] for ch in chans], dtype=float)
        caps  = np.array([ch["cap"]  for ch in chans], dtype=float)

        # track cumulative usage via ticks already logged (optional: derive from SRML)
        # For standalone, assume caps are total and we only bound by rate per tick.
        desired = remaining * weights
        per_tick = np.minimum(desired, rates)
        # also bound by cap (if max_ticks known, approximate per-tick cap)
        if contract["terms"].get("max_ticks"):
            per_tick = np.minimum(per_tick, caps / contract["terms"]["max_ticks"])

        # Never allocate more than remaining:
        scale = min(1.0, remaining / (per_tick.sum() + 1e-12))
        per_tick *= scale

        alloc = []
        for ch, units in zip(chans, per_tick):
            if units > 0:
                alloc.append({"channel": ch["type"], "units": float(units), "unit": ch["unit"]})
        return alloc

    # -- Streaming -------------------------------------------------------------

    def stream_tick(self, contract_id: str, tick_index: int) -> dict:
        c = self.contracts[contract_id].d
        rd0 = c["metrics"]["resonance_debt"]
        lam = c["terms"]["decay"]["lambda"]
        floor = c["terms"]["decay"].get("floor", 0.0)

        remaining = exponential_decay(rd0, lam, tick_index, floor=floor)
        # Compute last tick remaining to convert to delta paid this tick:
        prev_remaining = exponential_decay(rd0, lam, max(0, tick_index - 1), floor=floor)
        due_this_tick = max(0.0, prev_remaining - remaining)

        allocations = self._tick_allocation(c, tick_index, due_this_tick)

        ev = {
            "contract_id": contract_id,
            "tick_index": tick_index,
            "allocations": allocations,
            "remaining_debt": float(remaining)
        }
        ev["hash"] = sha256_hex(ev)
        ev["signature"] = self.ledger._sign(ev["hash"])

        # Log into SRML as a stream tick event
        self.ledger.append_event(
            treaty_id=c["treaty_id"],
            etype="RESTITUTION_STREAM_TICK",
            payload=ev,
            counterparty_id=c["debtor"]
        )

        # Fulfillment check
        if remaining <= (c["terms"]["decay"].get("floor", 0.0) + 1e-9):
            self.ledger.append_event(
                treaty_id=c["treaty_id"],
                etype="RESTITUTION_FULFILLED",
                payload={"contract_id": contract_id, "tick_index": tick_index},
                counterparty_id=c["debtor"]
            )
        return ev

    # -- Drift / Capacity adjustments -----------------------------------------

    def adjust_contract(self, contract_id: str, new_channels: Optional[List[dict]] = None,
                        new_lambda: Optional[float] = None,
                        reason: str = "capacity drift") -> dict:
        c = self.contracts[contract_id].d
        if new_channels is not None:
            c["channels"] = new_channels
        if new_lambda is not None:
            c["terms"]["decay"]["lambda"] = new_lambda
        c["hash"] = sha256_hex(c)
        return self.ledger.append_event(
            treaty_id=c["treaty_id"],
            etype="RESTITUTION_ADJUSTED",
            payload={"contract_id": contract_id, "reason": reason, "hash": c["hash"]},
            counterparty_id=c["debtor"]
        )

    def breach(self, contract_id: str, tick_index: int, detail: str) -> dict:
        c = self.contracts[contract_id].d
        return self.ledger.append_event(
            treaty_id=c["treaty_id"],
            etype="RESTITUTION_BREACH",
            payload={"contract_id": contract_id, "tick_index": tick_index, "detail": detail},
            counterparty_id=c["debtor"]
        )
