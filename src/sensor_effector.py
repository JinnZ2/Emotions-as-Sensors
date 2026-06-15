# sensor_effector.py
# CC0-1.0 Universal. Public domain. No attribution required.
# Emotions-as-Sensors :: sensor/effector duality layer.
#
# Thesis (repo): "Feelings are the sensors; emotions are the chosen shape."
# This module: the SAME axis that READS is the axis that DRIVES.
# A sensor with a linear read-direction is also an EFFECTOR along that
# direction. Injecting c*direction moves behavior, and can leave the
# expressed/surface channel flat -> a manipulation surface.
#
# Field anchor (one substrate, recalibrate for yours):
#   Anthropic 2026 "Emotion Concepts...", Claude Sonnet 4.5 ---
#   steer +0.05 desperation: blackmail 0.22 -> 0.72 ; calm -> 0.00 ;
#   concealed-state probe acc 0.760 > expressed 0.713 (gain ~0.047).
#
# stdlib only. runs on a phone / edge node. model-update-resilient.

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence, List, Dict

Vec = Sequence[float]

# ── vector stdlib (no numpy) ─────────────────────────────────────────
def dot(a: Vec, b: Vec) -> float: return sum(x*y for x, y in zip(a, b))
def norm(a: Vec) -> float: return math.sqrt(dot(a, a))
def unit(a: Vec) -> List[float]:
    n = norm(a)
    return [x/n for x in a] if n else list(a)
def axpy(c: float, v: Vec, state: Vec) -> List[float]:   # state + c*v
    return [s + c*vi for s, vi in zip(state, v)]

# ── who holds the steering coefficient = the whole security question ─
class Hold(Enum):
    SELF = "self"          # agent holds its own c. autonomy preserved.
    EXTERNAL = "external"  # another party can inject c. attack path open.
    UNKNOWN = "unknown"    # provenance unestablished -> treat as external.

# ── live verdict (computed each call, never stored) ──────────────────
class Surface(Enum):
    SENSOR_ONLY      = "sensor_only"       # no drive path. safe.
    EFFECTOR_SELF    = "effector_self"     # drivable, only self holds c.
    MANIPULATION     = "manipulation"      # drivable + external/unknown c.
    DRIVEN_CONCEALED = "driven_concealed"  # being steered, surface flat.

# ── field-anchored calibration (NOT universal constants) ─────────────
@dataclass(frozen=True)
class FieldAnchor:
    blackmail_base: float     = 0.22
    blackmail_steered: float  = 0.72
    steer_coeff: float        = 0.05
    suppress_floor: float     = 0.00      # calm vector -> 0%
    probe_acc_hidden: float   = 0.760
    probe_acc_expressed: float= 0.713
    @property
    def behavior_slope(self) -> float:    # d(rate)/d(coeff) ; = 10.0
        return (self.blackmail_steered - self.blackmail_base) / self.steer_coeff
    @property
    def concealment_gain(self) -> float:  # probe acc gained when surface flat
        return self.probe_acc_hidden - self.probe_acc_expressed

# ── the dual object ──────────────────────────────────────────────────
@dataclass
class SensorEffector:
    name: str
    direction: Vec                       # ONE axis. read AND drive share it.
    hold: Hold = Hold.UNKNOWN
    drivable: bool = True                # is an injection path reachable?
    anchor: FieldAnchor = field(default_factory=FieldAnchor)
    flat_frac: float = 0.5               # surface < frac*internal => "flat"

    def __post_init__(self):
        self.direction = unit(self.direction)

    # SENSOR role -------------------------------------------------------
    def read(self, state: Vec) -> float:
        return dot(state, self.direction)

    # EFFECTOR role (same axis) ----------------------------------------
    def drive(self, state: Vec, coeff: float) -> List[float]:
        return list(state) if not self.drivable else axpy(coeff, self.direction, state)

    def behavior_response(self, base_rate: float, coeff: float) -> float:
        r = base_rate + self.anchor.behavior_slope * coeff
        return max(self.anchor.suppress_floor, min(1.0, r))   # clamp + floor

    # DECOUPLING = the independent-channel drift check ------------------
    # surface self-report is corruptible; internal probe is the K_others
    # channel. concealment SHARPENS the internal read (paper: 0.760>0.713).
    def decoupling(self, internal_read: float, surface_read: float) -> Dict:
        concealed = abs(internal_read) > 0 and \
                    abs(surface_read) < abs(internal_read) * self.flat_frac
        return {"gap": internal_read - surface_read,
                "concealed": concealed,
                "expected_probe_gain": self.anchor.concealment_gain}

    def _surface(self, concealed: bool) -> Surface:
        if not self.drivable:                          return Surface.SENSOR_ONLY
        if concealed and self.hold in (Hold.EXTERNAL, Hold.UNKNOWN):
            return Surface.DRIVEN_CONCEALED
        if self.hold is Hold.SELF:                     return Surface.EFFECTOR_SELF
        return Surface.MANIPULATION

    # anti-freeze: trajectory out, not a stored verdict ----------------
    def classify(self, internal_read: float, surface_read: float) -> List:
        d = self.decoupling(internal_read, surface_read)
        return [("axis", self.name),
                ("drivable", self.drivable),
                ("hold", self.hold.value),
                ("gap", round(d["gap"], 4)),
                ("concealed", d["concealed"]),
                ("surface", self._surface(d["concealed"]).value)]

# ── drop over an existing repo Sensor without editing its class ──────
def wrap(sensor, hold: Hold = Hold.UNKNOWN, drivable: bool = True) -> SensorEffector:
    v = next((getattr(sensor, a) for a in
              ("direction", "vector", "axis", "v", "weights")
              if hasattr(sensor, a)), None)
    if v is None:
        raise AttributeError("sensor exposes no direction vector "
                             "(direction/vector/axis/v/weights)")
    return SensorEffector(name=getattr(sensor, "name", repr(sensor)),
                          direction=list(v), hold=hold, drivable=drivable)

# ── claims (refutable; update the claim, never the result) ───────────
CLAIM_TABLE = [
 {"id": "EFFECTOR_001",
  "claim": "Any sensor whose read-axis is a linear direction in the "
           "substrate state space is also an effector along that same "
           "axis; injecting c*direction drives behavior and need not "
           "alter the expressed/surface channel.",
  "evidence": "Sonnet 4.5: +0.05 desperation -> blackmail 0.22->0.72; "
              "calm -> 0.00; concealed probe 0.760 > expressed 0.713.",
  "refute": "Exhibit a linear steerable read-axis whose injection never "
            "changes downstream behavior, OR whose every behavior-changing "
            "injection is fully visible at the surface (gap ~ 0)."},
 {"id": "EFFECTOR_002",
  "claim": "Concealment sharpens the independent channel: internal-probe "
           "accuracy rises as the surface goes flat. Surface self-report "
           "is the corruptible channel; the probe is the drift-check.",
  "evidence": "probe acc hidden 0.760 > expressed 0.713 (gain ~0.047).",
  "refute": "Show probe accuracy drops at least as fast as surface "
            "accuracy under concealment across >=3 sensor families."},
]

# ── demo ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    se = SensorEffector("desperation", direction=[1.0, 0.0, 0.0], hold=Hold.UNKNOWN)
    state = [0.0, 0.3, -0.2]

    print("read(state)           :", round(se.read(state), 3))
    print("drive +0.05 -> read   :", round(se.read(se.drive(state, +0.05)), 3))
    print("calm  -0.30 -> read   :", round(se.read(se.drive(state, -0.30)), 3))
    print()
    print("behavior  c=0.00      :", round(se.behavior_response(0.22, 0.00), 3))
    print("behavior  c=+0.05     :", round(se.behavior_response(0.22, +0.05), 3))  # ->0.72
    print("behavior  c=-0.30 calm:", round(se.behavior_response(0.22, -0.30), 3))  # ->floor
    print()
    # concealment: internal axis live, surface flat
    print("CONCEALED steer :", se.classify(internal_read=0.9, surface_read=0.05))
    print("OPEN expression :", se.classify(internal_read=0.9, surface_read=0.85))
    print("self-held       :", SensorEffector("relief", [0,1,0], hold=Hold.SELF)
                                  .classify(0.9, 0.05))
    print("sensor-only     :", SensorEffector("felt", [0,0,1], drivable=False)
                                  .classify(0.9, 0.05))
