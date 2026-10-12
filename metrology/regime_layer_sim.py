"""
regime_layer_sim.py
===================

GD-002 — the regime layer under GD-001. Which resource regime makes
holding correct and which makes pooling correct, and what that does to
the reading of a no-return donation task.

    storability   can the stock be held without loss?
    shock_corr    do agents fail independently, or together?
    enclosure     is the stock bounded and assignable?

    zero-sum correct when   storable + covariant + enclosed
    sharing correct when    non-storable + idiosyncratic + unenclosed

WHAT THIS IS
------------
E2 from docs/calibration-regime-notes.md. Two parts:

  PART 1  derive the corners rather than assert them. Run both
          strategies through all eight corners of the three-term cube
          and report which wins where. The table in the notes is a
          claim; this is the check on it.

  PART 2  the confound E2 exists to expose. GD-001's test 2 says a
          no-return task (r = 0) is the only place buffering and
          disposition separate. The regime terms say r = 0 has also
          stripped the environment to the zero-sum corner. So low
          export at r = 0 has two readings the task cannot separate:
          reduced disposition, or a correct regime response to a pool
          that does not exist.

          Part 2 holds disposition EXACTLY constant across two agents
          and varies only what regime they were calibrated in. If the
          two produce different export at r = 0, then export at r = 0
          is not a disposition measurement, and any study reading it
          as one is reading a regime.

THE MECHANISM
-------------
Holding and pooling are different storage technologies, and the three
terms decide which one works:

  holding   moves resource ACROSS periods. Storability is its
            efficiency. Shock correlation is irrelevant to it — your
            own store does not care whether others also failed.

  pooling   moves resource ACROSS AGENTS within a period. It works by
            drawing on somebody else's current surplus, which is why
            it substitutes for storage at all. Shock correlation is
            its efficiency: if everyone fails together there is no
            surplus to draw on. Enclosure sets how much surplus is
            even reachable.

The pool does not persist between periods. That is not a
simplification — it is the point. "The pool IS the storage medium"
means pooling buys you access to others' present, not to your own
past.

NOT A CLAIM ABOUT PEOPLE
------------------------
Neither strategy is a disposition and neither is a virtue. Both are
correct under their own regime and wrong under the other. "Sharing
culture" and "hoarding culture" are regime readouts — the same
structure as a neuromodulator carrying gain and no direction.

PAIRS WITH
----------
- GD-001 (gain_direction_sim.py) — the receiver-side model. This is
  the regime that sets its calibration. The export-slope subtraction
  is mirrored below rather than imported, so each part stays
  independently runnable; GD-001 is the source of truth for it.
- docs/calibration-regime-notes.md — sections 1 and 2, and E2/E3.
- docs/evidence-weighting.md — why a persisting strategy is read as
  encoding something about its regime before it is read as a defect.

License: CC0
Dependencies: stdlib only
"""

import argparse
import random
import statistics
from dataclasses import dataclass


EPS = 1e-9


# ---------------------------------------------------------------------------
# REGIME
# ---------------------------------------------------------------------------

@dataclass
class Regime:
    """
    storability  fraction of a private store surviving to the next
                 period. 1.0 = grain in a dry silo. 0.05 = meat in
                 summer.
    shock_corr   fraction of windfall variance that is common across
                 agents. 1.0 = the drought hits everyone. 0.0 = your
                 bad day is not my bad day.
    enclosure    fraction of surplus that is bounded and assignable,
                 and therefore withheld from any pool.
    """
    storability: float = 0.5
    shock_corr:  float = 0.5
    enclosure:   float = 0.5

    def label(self) -> str:
        return (f"stor={self.storability:.2f} "
                f"corr={self.shock_corr:.2f} "
                f"encl={self.enclosure:.2f}")


@dataclass
class Population:
    n_agents:   int   = 60
    n_periods:  int   = 300
    need:       float = 1.0
    mean_yield: float = 1.05
    yield_sd:   float = 0.85


def _draw_yields(pop: Population, regime: Regime,
                 rng: random.Random) -> list[float]:
    """One period of windfalls, split into common and idiosyncratic parts."""
    common = rng.gauss(0.0, 1.0)
    c = max(0.0, min(1.0, regime.shock_corr))
    common_w = c ** 0.5
    idio_w = (1.0 - c) ** 0.5
    return [max(0.0, pop.mean_yield + pop.yield_sd *
                (common_w * common + idio_w * rng.gauss(0.0, 1.0)))
            for _ in range(pop.n_agents)]


def run_hold(pop: Population, regime: Regime, rng: random.Random) -> float:
    """
    Every agent keeps its own surplus. Returns total unmet need,
    normalized per agent-period. Lower is better.
    """
    stores = [0.0] * pop.n_agents
    unmet = 0.0
    for _ in range(pop.n_periods):
        for i, y in enumerate(_draw_yields(pop, regime, rng)):
            available = y + stores[i]
            if available >= pop.need:
                stores[i] = (available - pop.need) * regime.storability
            else:
                unmet += pop.need - available
                stores[i] = 0.0
    return unmet / (pop.n_agents * pop.n_periods)


def run_share(pop: Population, regime: Regime, rng: random.Random) -> float:
    """
    Surplus above what enclosure withholds goes into a within-period
    pool; deficits draw from it pro rata. The pool clears each period —
    it is access to others' present, not to your own past.
    """
    stores = [0.0] * pop.n_agents
    unmet = 0.0
    for _ in range(pop.n_periods):
        yields = _draw_yields(pop, regime, rng)
        pool = 0.0
        deficits = [0.0] * pop.n_agents
        for i, y in enumerate(yields):
            available = y + stores[i]
            if available >= pop.need:
                surplus = available - pop.need
                withheld = surplus * regime.enclosure
                pool += surplus - withheld
                stores[i] = withheld * regime.storability
            else:
                deficits[i] = pop.need - available
                stores[i] = 0.0
        total_deficit = sum(deficits)
        if total_deficit > 0.0:
            fill = min(1.0, pool / total_deficit)
            unmet += total_deficit * (1.0 - fill)
    return unmet / (pop.n_agents * pop.n_periods)


# ---------------------------------------------------------------------------
# PART 1 — derive the corners
# ---------------------------------------------------------------------------

def demo_corners(seed: int = 5) -> None:
    print(_header("E2 PART 1 — WHICH STRATEGY WINS IN WHICH CORNER"))
    pop = Population()
    print("unmet need per agent-period; lower is better.\n")
    print(f"{'storability':>11} {'shock_corr':>11} {'enclosure':>10} "
          f"{'hold':>8} {'share':>8}   winner")
    print("-" * 68)

    lo, hi = 0.05, 0.95
    predicted_hold = 0
    correct = 0
    rows = []
    for storability in (lo, hi):
        for shock_corr in (lo, hi):
            for enclosure in (lo, hi):
                regime = Regime(storability, shock_corr, enclosure)
                h = run_hold(pop, regime, random.Random(seed))
                s = run_share(pop, regime, random.Random(seed))
                winner = "hold" if h < s else "share"
                # the notes' claim, stated before the numbers were seen
                claim = ("hold" if (storability > 0.5 and shock_corr > 0.5
                                    and enclosure > 0.5) else
                         "share" if (storability < 0.5 and shock_corr < 0.5
                                     and enclosure < 0.5) else None)
                if claim is not None:
                    predicted_hold += 1
                    correct += (claim == winner)
                mark = "" if claim is None else ("  <- predicted " + claim)
                rows.append((regime, h, s, winner))
                print(f"{storability:>11.2f} {shock_corr:>11.2f} "
                      f"{enclosure:>10.2f} {h:>8.4f} {s:>8.4f}   "
                      f"{winner}{mark}")

    print()
    print("read:")
    print(f"  the two corners the notes name explicitly: {correct}/{predicted_hold} "
          f"came out as claimed.")
    print("  the table was a claim about a mechanism. This is the mechanism")
    print("  run. The corners are derived here, not asserted.")

    # which term actually decides? share_advantage > 0 means share wins.
    def influence(index: int) -> float:
        hi = [h - s for r, h, s, _w in rows if _term(r, index) > 0.5]
        lo = [h - s for r, h, s, _w in rows if _term(r, index) <= 0.5]
        return statistics.fmean(hi) - statistics.fmean(lo)

    infl = {"storability": influence(0),
            "shock_corr":  influence(1),
            "enclosure":   influence(2)}
    print()
    print("  effect of raising each term on share's advantage over hold:")
    for name, value in sorted(infl.items(), key=lambda kv: -abs(kv[1])):
        arrow = "favors share" if value > 0 else "favors hold"
        print(f"    {name:<12} {value:>+8.4f}   {arrow}")
    decisive = max(infl, key=lambda k: abs(infl[k]))
    print(f"  -> {decisive} is the decisive term in this cube.")

    ties = [r for r, h, s, _w in rows if abs(h - s) < 0.005]
    if ties:
        print()
        print(f"  {len(ties)} row(s) are within 0.005 — at or below run-to-run")
        print("  noise. Those winners are not real and should not be read.")

    print()
    print("  note the high-storability / idiosyncratic / ENCLOSED row: share")
    print("  still wins. High enclosure alone does not make zero-sum correct.")
    print("  When deficits are rare and uncorrelated, the small unenclosed")
    print("  remainder still covers them. Enclosure needs covariant shocks")
    print("  to bite — which is the pairing the notes flag as having moved")
    print("  together historically.")
    print()
    print("  the middle rows matter more than the corners: most real regimes")
    print("  are mixed, and the winner there is set by which term moved.")


def _term(regime: Regime, index: int) -> float:
    return (regime.storability, regime.shock_corr, regime.enclosure)[index]


# ---------------------------------------------------------------------------
# PART 2 — the r = 0 confound
# ---------------------------------------------------------------------------

@dataclass
class Agent:
    """
    disposition      standing willingness to export, regime-independent
    calibrated_in    the regime this agent learned in
    """
    name:          str
    disposition:   float
    calibrated_in: Regime


def prior_return(regime: Regime) -> float:
    """
    What the agent's CALIBRATION says export is worth. Pooling pays when
    shocks are idiosyncratic and surplus is reachable.

    This is a property of the regime the agent learned in — not of the
    task it is currently sitting in.
    """
    return (1.0 - regime.shock_corr) * (1.0 - regime.enclosure)


def export_of(agent: Agent, task_return: float, observability: float,
              cue: float = 0.30, export_cost: float = 0.08) -> float:
    """
    Export under the agent's own calibration.

    `observability` is how much the task reveals about its own regime.
    A one-shot laboratory donation task reveals almost nothing, so the
    agent runs its prior — which is exactly why the measurement reads
    calibration rather than the task.

    Mirrors GD-001's subtraction, a cue term against a precision-
    weighted cost, with precision supplied here by the regime rather
    than by developmental variance. GD-001 is the source of truth.
    """
    perceived = (observability * task_return
                 + (1.0 - observability) * prior_return(agent.calibrated_in))
    precision = 1.0 / (perceived + 0.25)
    drive = cue + perceived - precision * export_cost
    return max(0.0, min(1.0, agent.disposition * drive))


# a one-shot task tells the participant almost nothing about its regime
LAB_OBSERVABILITY = 0.20


def demo_r_zero_confound() -> None:
    print(_header("E2 PART 2 — LOW EXPORT AT r = 0: DISPOSITION OR REGIME?"))

    sharing = Regime(storability=0.05, shock_corr=0.05, enclosure=0.05)
    zerosum = Regime(storability=0.95, shock_corr=0.70, enclosure=0.70)

    print(f"prior return on export, by calibration regime:")
    print(f"  sharing regime   {prior_return(sharing):.4f}")
    print(f"  zero-sum regime  {prior_return(zerosum):.4f}")
    print(f"task observability = {LAB_OBSERVABILITY:.2f} — a one-shot donation")
    print("task reveals almost nothing about its own regime, so the agent")
    print("runs its prior.\n")

    full_sharing = Agent("full disposition, sharing", 1.0, sharing)
    full_zerosum = Agent("full disposition, zero-sum", 1.0, zerosum)

    e_sharing = export_of(full_sharing, 0.0, LAB_OBSERVABILITY)
    e_zerosum = export_of(full_zerosum, 0.0, LAB_OBSERVABILITY)

    # what disposition makes a sharing-calibrated agent look identical to
    # a FULL-disposition zero-sum-calibrated one? Solved, not tuned.
    unit = export_of(Agent("unit", 1.0, sharing), 0.0, LAB_OBSERVABILITY)
    matching = e_zerosum / (unit + EPS)
    matched = Agent("reduced disposition, sharing", matching, sharing)

    print("all agents in a task with NO pool (r = 0):\n")
    print(f"{'agent':<34} {'disposition':>12} {'export':>8}")
    print("-" * 56)
    for agent in (full_sharing, full_zerosum, matched):
        print(f"{agent.name:<34} {agent.disposition:>12.3f} "
              f"{export_of(agent, 0.0, LAB_OBSERVABILITY):>8.3f}")

    print()
    print("read:")
    print(f"  a zero-sum-calibrated agent at FULL disposition and a")
    print(f"  sharing-calibrated agent at {matching:.3f} disposition emit the")
    print(f"  same number ({e_zerosum:.3f}). That is a "
          f"{1.0 / (matching + EPS):.1f}x disposition")
    print("  difference, invisible to the measurement.")
    print()
    print("  so export at r = 0 does not rank disposition unless calibration")
    print("  is known. Reading it as altruism reads a regime and reports it")
    print("  as a trait.")
    print()

    print("what separates them — run the SAME task with the return channel")
    print("made observable, and read the delta:\n")
    print(f"{'agent':<34} {'no pool':>9} {'pool':>8} {'delta':>8}")
    print("-" * 62)
    deltas = {}
    for agent in (full_sharing, full_zerosum, matched):
        no_pool = export_of(agent, 0.0, 0.90)
        pool = export_of(agent, 1.0, 0.90)
        deltas[agent.name] = pool - no_pool
        print(f"{agent.name:<34} {no_pool:>9.3f} {pool:>8.3f} "
              f"{pool - no_pool:>8.3f}")

    true_ratio = full_zerosum.disposition / (matched.disposition + EPS)
    level_ratio = e_zerosum / (export_of(matched, 0.0, LAB_OBSERVABILITY) + EPS)
    delta_ratio = (deltas[full_zerosum.name]
                   / (deltas[matched.name] + EPS))

    print()
    print("read:")
    print("  raising observability washes out the prior, so what is left in")
    print("  the delta is disposition. Compare how well each readout")
    print("  recovers the true disposition ratio between the two agents the")
    print("  level could not tell apart:")
    print()
    print(f"    true disposition ratio          {true_ratio:>6.2f}x")
    print(f"    recovered from LEVEL at r=0     {level_ratio:>6.2f}x   "
          f"(off by {abs(true_ratio - level_ratio) / true_ratio * 100:.0f}%)")
    print(f"    recovered from DELTA            {delta_ratio:>6.2f}x   "
          f"(off by {abs(true_ratio - delta_ratio) / true_ratio * 100:.0f}%)")
    print()
    print("  the level says the two agents are identical when they differ by")
    print(f"  {true_ratio:.1f}x. The delta recovers that ratio to within")
    print(f"  {abs(true_ratio - delta_ratio) / true_ratio * 100:.0f}%.")
    print()
    print("  note this is the OPPOSITE of the reading that suggests itself:")
    print("  the delta is not a calibration probe. Making the channel")
    print("  observable is what REMOVES calibration from the measurement,")
    print("  which is precisely why disposition survives in it. To measure")
    print("  calibration instead, read the level at LOW observability — the")
    print("  first table — with disposition independently pinned.")
    print()
    print("  the discriminating design is therefore not a bigger donation")
    print("  task. It is the same task run twice at different observability,")
    print("  because the two readouts carry different variables and neither")
    print("  alone is interpretable.")
    print()
    print("  this does not overturn GD-001 test 2 — r = 0 is still the only")
    print("  place buffering and disposition separate. It says the r = 0")
    print("  measurement carries its own confound, so the identifying")
    print("  condition and the confounding condition are the same condition,")
    print("  and only the paired design escapes both.")


# ---------------------------------------------------------------------------
# BOUNDARIES
# ---------------------------------------------------------------------------

def print_boundaries() -> None:
    print(_header("BOUNDARIES  [GD-002]"))
    print("works when:")
    for x in [
        "need is a per-period threshold, not a cumulative target",
        "pooling is within-period redistribution and holding is across-period",
        "enclosure withholds surplus from the pool rather than blocking need",
    ]:
        print(f"  - {x}")
    print("\nfails when:")
    for x in [
        "the pool can itself be stored — then pooling and holding stop being "
        "different technologies and the three terms collapse to one",
        "shocks are correlated in time as well as across agents — this model "
        "draws each period independently",
        "enforcement is costly — free-riding is not modeled at all, so the "
        "sharing arm is measured at its best case",
    ]:
        print(f"  - {x}")
    print("\nnot yet tested:")
    for x in [
        "any empirical data whatsoever — this module contains none",
        "partial enclosure regimes where assignability itself is contested",
        "whether real calibration tracks the winning strategy or lags it",
        "the E3 archival measurement, which is where the historical claim "
        "in section 2 of the notes would actually be settled",
    ]:
        print(f"  - {x}")
    print()


def _header(title: str) -> str:
    return f"\n{'=' * 68}\n{title}\n{'=' * 68}"


DEMOS = {"1": demo_corners, "2": demo_r_zero_confound}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GD-002 — regime layer. Derives the zero-sum/sharing "
                    "corners and exposes the r = 0 confound.")
    parser.add_argument("--demo", default="all",
                        choices=["all", "1", "2", "boundaries"])
    args = parser.parse_args()

    if args.demo == "boundaries":
        print_boundaries()
        return
    if args.demo == "all":
        demo_corners()
        demo_r_zero_confound()
        print_boundaries()
        print("Neither strategy is a disposition. Both are regime readouts.")
        return
    DEMOS[args.demo]()


if __name__ == "__main__":
    main()
