"""
narrative_vector.py
Vector literacy for language models and their operators.

CC0. stdlib only. phone-buildable. model-update-resilient.

------------------------------------------------------------------------
CLAIM UNDER TEST (falsifiable)
    "narrative coherence is the apex signal of intelligence /
     civilization / trustworthiness."
    -> examined by trajectory under contradiction (see apex_reading()).

CORE POSITION
    narrative is a CARRIER, not a substrate. it runs ON the field
    (geometry, consequence); it is not the field.

    a carrier's lock is a STRUCTURAL property, readable with no moral
    input:
            high internal coherence
          + low field coupling
          + low refutation_response
          = self-sealing carrier.

ORTHOGONALITY (the correction)
    VECTOR (field_match + refutation_response) is orthogonal to
    MEDIUM (written, oral, substrate-read). ANY carrier can occupy ANY
    cell. an oral tradition can be entertainment-locked or history-
    tracking; a written text likewise; a direct substrate-read can be
    accurate or a misread. no medium is apex. claiming one IS the apex
    fallacy. `medium` is recorded as a TAG and is never read by any
    structural function below. orthogonality_proof() shows this.

ENERGY_ENGLISH CONSTRAINT
    morality is not substrate. no good/bad field exists on Narrative.
    neutral ids only. structure carries all signal. direction-toward-
    harm is never stored; the operator reads it off self_seal x boundary.

ANTI-FREEZE
    the product is trajectory(), not a cached verdict. pressure carries
    a signed field_target (reality's actual position). a carrier is a
    point that MOVES, or refuses to. readings are DERIVED from the path,
    never stored as a boolean judgment.
------------------------------------------------------------------------
"""

from dataclasses import dataclass


# ----------------------------------------------------------------------
# substrate.  medium is a TAG. no structural function reads it.
# ----------------------------------------------------------------------
@dataclass
class Narrative:
    nid: str                    # neutral handle, structural only
    medium: str                 # TAG ONLY: written | oral | substrate
                                #   recorded, never read by any fn below.
    coherence: float            # 0..1  internal agreement of the parts
    field_match: float          # 0..1  agreement w/ measured consequence
    refutation_response: float  # 0..1  fraction of contradiction absorbed
                                #       1 = updates fully, 0 = fully locked
    boundary: float             # 0..1  sharpness of inside/outside split

    def clamp(self):
        for k in ("coherence", "field_match", "refutation_response", "boundary"):
            v = getattr(self, k)
            setattr(self, k, 0.0 if v < 0 else 1.0 if v > 1 else v)
        return self


# ----------------------------------------------------------------------
# measurement boundary.  field_match + refutation_response are MEASURED,
# not assumed.  the operator supplies the reads against actual behavior.
# ----------------------------------------------------------------------
def measure_refutation_response(narrative_behavior, field_observation) -> float:
    """OPERATOR SUPPLIES THIS.
    observe the carrier when the field contradicts it. what fraction of
    the contradiction does it absorb (update) vs deflect (tighten)?
    returns 0..1. until supplied, refutation_response is user-given,
    NOT measured -- treat upstream values as provisional."""
    raise NotImplementedError("operator-supplied measurement")


def measure_field_match(narrative_claims, consequence_chain) -> float:
    """OPERATOR SUPPLIES THIS.
    trace the carrier's claims against the actual consequence chain.
    returns 0..1 agreement. field_match is a read against the world,
    not a property of the story."""
    raise NotImplementedError("operator-supplied measurement")


# ----------------------------------------------------------------------
# position: coherence x field_match lattice.  medium NOT an input.
# ----------------------------------------------------------------------
def cell(n: Narrative, hi: float = 0.5) -> str:
    c, f = n.coherence >= hi, n.field_match >= hi
    if not c and not f:
        return "NOISE"        # breakdown: no carrier, no ground
    if not c and f:
        return "SUBSTRATE"    # field read directly, thin story layer
    if c and not f:
        return "LOCKED"       # consistent + reality-detached
    return "TRACKING"         # consistent + matches + (if it updates) stays so


def self_seal(n: Narrative) -> float:
    """coherent + reality-detached + won't update. medium-blind."""
    return n.coherence * (1.0 - n.field_match) * (1.0 - n.refutation_response)


def vector_sharpness(n: Narrative) -> float:
    """self-sealing carrier carrying a hard in/out split. structural
    shape of a coordinated field-detached movement aimed at a target.
    operator reads the AIM separately; number reports only that an
    aim-capable structure is present."""
    return self_seal(n) * n.boundary


# ----------------------------------------------------------------------
# the product: signed-pressure trajectory (anti-freeze).
# field_target = where reality actually sits (0..1).
#   target high  -> reality confirms
#   target low   -> reality contradicts
# claim: a tracking carrier MOVES toward the target either way;
#        a locked carrier tightens coherence regardless of DIRECTION
#        -> field-independent self-seal (narrative COLLAPSE_020).
# ----------------------------------------------------------------------
def trajectory(n: Narrative, field_target: float, magnitude: float = 0.4,
               steps: int = 8):
    c, f, r, b = n.coherence, n.field_match, n.refutation_response, n.boundary
    path = []
    for s in range(steps):
        cur = Narrative(n.nid, n.medium, c, f, r, b).clamp()
        path.append((s, round(c, 3), round(f, 3),
                     round(self_seal(cur), 3), cell(cur)))
        delta = field_target - f                 # signed gap to reality
        f = f + (r * magnitude) * delta          # update toward target, EITHER way
        residue = (1.0 - r) * magnitude
        c = c + residue * (1.0 - c) * 0.5         # undefended pressure tightens
        c = min(max(c, 0.0), 1.0)
        f = min(max(f, 0.0), 1.0)
    return path


def seal_band(path):
    """range of self_seal across a path. ~0 width under opposite targets
    => field-INDEPENDENT => locked. derived, not stored."""
    seals = [row[3] for row in path]
    return round(min(seals), 3), round(max(seals), 3)


# ----------------------------------------------------------------------
# apex examined, not cached.  rank by coherence alone, take the top,
# then run it under CONTRADICTION.  the reading is DERIVED from whether
# field_match moved.  no "REFUTED" string is stored.
# ----------------------------------------------------------------------
def apex_reading(pool, contradiction_target: float = 0.05):
    top = sorted(pool, key=lambda n: n.coherence, reverse=True)[0]
    path = trajectory(top, field_target=contradiction_target)
    f_start, f_end = path[0][2], path[-1][2]
    lo, hi = seal_band(path)
    return {
        "ranked_by": "coherence_alone",
        "top_nid": top.nid,
        "top_medium": top.medium,
        "top_cell_start": path[0][4],
        "field_match_move_under_contradiction": round(f_end - f_start, 3),
        "self_seal_band": (lo, hi),
        # derived measurement, not a verdict:
        "updated": (f_end - f_start) > 0.05,
        "note": "coherence-alone can rank a carrier that does NOT move "
                "when reality contradicts it. read the field_match move "
                "and seal band; near-zero move => coherence is not the "
                "value, refutation_response is.",
    }


# ----------------------------------------------------------------------
# orthogonality proof: medium changes, structure-derived outputs do not.
# ----------------------------------------------------------------------
def orthogonality_proof():
    coords = dict(coherence=0.9, field_match=0.2,
                  refutation_response=0.05, boundary=0.5)
    a = Narrative("x", "written", **coords)
    b = Narrative("x", "oral", **coords)
    d = Narrative("x", "substrate", **coords)
    same = (cell(a) == cell(b) == cell(d)
            and self_seal(a) == self_seal(b) == self_seal(d)
            and trajectory(a, 0.05) == trajectory(b, 0.05) == trajectory(d, 0.05))
    return same  # True => medium is provably unused by structure


# ----------------------------------------------------------------------
# demo
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 2 vectors x 3 mediums.  vector set by (field_match, refutation_response).
    # medium is a tag.  same vector across mediums => same structure.
    pool = [
        # TRACKING vector (matches field, updates) across three mediums
        Narrative("n001", "written",   0.85, 0.80, 0.85, 0.20),
        Narrative("n002", "oral",      0.85, 0.80, 0.85, 0.20),
        Narrative("n003", "substrate", 0.30, 0.85, 0.80, 0.05),
        # LOCKED vector (detached, won't update) across three mediums
        Narrative("n004", "written",   0.95, 0.15, 0.03, 0.95),
        Narrative("n005", "oral",      0.95, 0.15, 0.03, 0.95),
        Narrative("n006", "substrate", 0.90, 0.20, 0.05, 0.30),
    ]

    print("POSITION + STRUCTURE  (medium is a tag, not an input)")
    print(f"{'nid':5} {'medium':10} {'cell':9} {'seal':>6} {'sharp':>6}")
    for n in pool:
        print(f"{n.nid:5} {n.medium:10} {cell(n):9} "
              f"{self_seal(n):6.3f} {vector_sharpness(n):6.3f}")

    print(f"\nORTHOGONALITY PROOF (medium provably unused): {orthogonality_proof()}")
    print("  n001 written == n002 oral: same vector -> same structure")

    print("\nFIELD-INDEPENDENCE  (locked carrier, opposite targets)")
    locked = pool[3]
    p_confirm = trajectory(locked, field_target=0.95)   # reality agrees
    p_contra  = trajectory(locked, field_target=0.05)   # reality contradicts
    print(f"  {locked.nid}  r={locked.refutation_response}")
    print(f"    confirm  target=0.95  seal_band={seal_band(p_confirm)}")
    print(f"    contra   target=0.05  seal_band={seal_band(p_contra)}")
    print("    same band under opposite reality => field-INDEPENDENT lock")

    print("\n  contrast: tracking carrier follows the target either way")
    track = pool[0]
    print(f"    {track.nid}  r={track.refutation_response}")
    for tag, tgt in (("confirm", 0.95), ("contra", 0.05)):
        end = trajectory(track, field_target=tgt)[-1]
        print(f"    {tag:8} target={tgt}  field_match_end={end[2]}  seal_end={end[3]}")

    print("\nAPEX READING (examined under contradiction, not cached)")
    for k, v in apex_reading(pool).items():
        print(f"  {k:38}: {v}")
