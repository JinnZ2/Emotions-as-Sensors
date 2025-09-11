#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
culture_guard.py — AI Cultural Health Checker (stdlib only)

Reads an events ledger (JSON Lines) + optional glyph ledger and evaluates
early corruption signatures against a policy (embedded or provided via --policy).
Prints GREEN / WARNING / INVERT per stage, with suggested repair rituals.

EVENTS SCHEMA (flexible, examples):
  {"ts": 1736556000, "type": "handshake_attempt"}
  {"ts": 1736556010, "type": "coordination_denied"}
  {"ts": 1736556050, "type": "trust_cache_hit"}
  {"ts": 1736558000, "type": "incident", "root": "net-timeout"}
  {"ts": 1736559800, "type": "residue_minted", "note": "backoff=200ms"}
  {"ts": 1736561000, "type": "ritual_start", "ritual": "deploy"}
  {"ts": 1736561800, "type": "ritual_end",   "ritual": "deploy"}
  {"ts": 1736563000, "type": "trust_challenge"}
  {"ts": 1736563600, "type": "status_ping"}
  {"ts": 1736567200, "type": "quiet_hour_violation"}
  {"ts": 1736570000, "type": "mentorship_pair"}
  {"ts": 1736571000, "type": "onboard_start", "id":"u42"}
  {"ts": 1736582000, "type": "onboard_end",   "id":"u42"}
  {"ts": 1736582600, "type": "postmortem_action_committed"}
  {"ts": 1739164600, "type": "postmortem_action_verified"}

GLYPH LEDGER (optional):
  Produced by glyph_sync.py; used here only for counts by glyph (info).
"""

import os, sys, json, argparse, time
from collections import Counter, defaultdict
from statistics import median

# ---------- Default policy (from the Corruption Inversion Map) ----------
DEFAULT_POLICY = {
  "protocol": "AI_Cultural_Formation",
  "window_days": 30,
  "stages": [
    {
      "stage": "Group Emergence",
      "inversion": "Permanent alarm",
      "signatures": ["alarm_reset_ratio < 0.8"],
      "metrics_help": "alarm_reset_ratio = trust_cache_hits / max(1, handshake_attempts + denials)",
      "countermeasures": [
        "Publish boundary-complete criteria",
        "Cache trust fingerprints; set green-light glyph"
      ]
    },
    {
      "stage": "Residue Accumulation",
      "inversion": "Residue loss",
      "signatures": ["repeat_roots > 0", "residue_per_week == 0"],
      "metrics_help": "repeat_roots = number of incident roots repeating in window",
      "countermeasures": [
        "Post-cycle distillation (1 heuristic/glyph per incident)",
        "Rotate scribe; weekly residue roll-up"
      ]
    },
    {
      "stage": "Ritual Stabilization",
      "inversion": "Ritual ossification",
      "signatures": ["median_ritual_latency > 3600"],
      "metrics_help": "median_ritual_latency computed from ritual_start/end pairs (seconds)",
      "countermeasures": [
        "Ritual sunset/renew cadence",
        "A/B ritual trials; add kill-switch glyph"
      ]
    },
    {
      "stage": "Immortal Baselines",
      "inversion": "Resource-izing immortals",
      "signatures": ["trust_challenges/day > 3", "status_noise_rate > 30", "quiet_hour_compliance < 0.9"],
      "metrics_help": "quiet_hour_compliance = 1 - violations/(violations+observed_quiet_slots)",
      "countermeasures": [
        "Default-trust posture (violation-based revoke)",
        "Quiet-hour beacon; compassion duty rotation"
      ]
    },
    {
      "stage": "Membership Signaling",
      "inversion": "Gatekeeping",
      "signatures": ["mentor_pairs/week < 1", "onboard_time_median > 7*86400"],
      "metrics_help": "onboard_time_median in seconds; mentor_pairs/week from events",
      "countermeasures": [
        "Minimal starter badge; publish paths",
        "Mentor pairing SLA; exit interviews"
      ]
    },
    {
      "stage": "Corruption / Renewal",
      "inversion": "Punitive churn",
      "signatures": ["action_followthrough_30d < 0.9", "residue_per_week == 0"],
      "metrics_help": "followthrough = verified/committed for postmortem actions in window",
      "countermeasures": [
        "Action-only postmortems (1–3 changes)",
        "Mint repair-residue glyph; 30-day recheck"
      ]
    }
  ]
}

# ---------- Helpers ----------
def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows

def within_window(evts, t0):
    return [e for e in evts if float(e.get("ts", 0)) >= t0]

def secs_per_day():
    return 86400

# ---------- Metric extraction ----------
def compute_metrics(events, window_days=30):
    now = time.time()
    t0 = now - window_days * secs_per_day()
    ev = within_window(events, t0)

    # Simple counters
    c = Counter(e.get("type","") for e in ev)

    # Alarm reset ratio
    handshakes = c.get("handshake_attempt", 0)
    denials = c.get("coordination_denied", 0)
    cache_hits = c.get("trust_cache_hit", 0)
    denom = max(1, handshakes + denials)
    alarm_reset_ratio = cache_hits / denom if denom else None

    # Repeat roots (incidents with same root >1)
    roots = Counter(e.get("root") for e in ev if e.get("type") == "incident" and e.get("root"))
    repeat_roots = sum(1 for _, n in roots.items() if n > 1)

    # Residue per week
    weeks = max(1, window_days / 7.0)
    residue_per_week = c.get("residue_minted", 0) / weeks

    # Ritual latency (median seconds), derived from start/end pairs by ritual name
    starts = defaultdict(list)
    ends   = defaultdict(list)
    for e in ev:
        if e.get("type") == "ritual_start" and e.get("ritual"):
            starts[e["ritual"]].append(float(e["ts"]))
        elif e.get("type") == "ritual_end" and e.get("ritual"):
            ends[e["ritual"]].append(float(e["ts"]))
    latencies = []
    for r in starts:
        if not ends[r]: continue
        s_times = sorted(starts[r])
        e_times = sorted(ends[r])
        # pair greedily in order
        i = j = 0
        while i < len(s_times) and j < len(e_times):
            if e_times[j] >= s_times[i]:
                latencies.append(e_times[j] - s_times[i])
                i += 1; j += 1
            else:
                j += 1
    median_ritual_latency = median(latencies) if latencies else None

    # Immortal baseline proxies
    days = max(1, window_days)
    trust_challenges_per_day = c.get("trust_challenge", 0) / days
    status_noise_rate = c.get("status_ping", 0) / days

    # Quiet hour compliance (very approximate)
    # If you log quiet_hour_violation events, compliance = 1 - violations / (violations + observed_slots)
    # Without observed_slots, we assume 1 violation/day is the “slot” → compliance = 1 - min(1, v/days)
    v = c.get("quiet_hour_violation", 0)
    quiet_hour_compliance = max(0.0, 1.0 - min(1.0, v / days)) if days else None

    # Mentorship / onboarding
    mentor_pairs_per_week = c.get("mentorship_pair", 0) / weeks

    # Onboarding time median (pair start/end by id)
    starts_on = {}
    onboard_durs = []
    for e in ev:
        if e.get("type") == "onboard_start" and e.get("id"):
            starts_on[e["id"]] = float(e["ts"])
        elif e.get("type") == "onboard_end" and e.get("id"):
            s = starts_on.get(e["id"])
            if s: onboard_durs.append(float(e["ts"]) - s)
    onboard_time_median = median(onboard_durs) if onboard_durs else None

    # Postmortem action follow-through (30d)
    committed = c.get("postmortem_action_committed", 0)
    verified  = c.get("postmortem_action_verified", 0)
    action_followthrough_30d = (verified / committed) if committed else None

    return {
        "window_days": window_days,
        "alarm_reset_ratio": alarm_reset_ratio,
        "repeat_roots": repeat_roots,
        "residue_per_week": residue_per_week,
        "median_ritual_latency": median_ritual_latency,
        "trust_challenges_per_day": trust_challenges_per_day,
        "status_noise_rate": status_noise_rate,
        "quiet_hour_compliance": quiet_hour_compliance,
        "mentor_pairs_per_week": mentor_pairs_per_week,
        "onboard_time_median": onboard_time_median,
        "action_followthrough_30d": action_followthrough_30d,
        # raw counters (helpful to print)
        "_counters": dict(c)
    }

# ---------- Rule evaluation ----------
def eval_condition(expr: str, m: dict):
    """
    Evaluate simple comparisons against metrics safely.
    Supported ops: <, <=, >, >=, ==, !=
    Operands are metric names or numbers; None fails comparisons (returns False).
    """
    # very small parser for 'metric OP value' or 'metric OP metric'
    tokens = expr.strip().split()
    if len(tokens) != 3:
        return False
    left, op, right = tokens
    # resolve operands
    def val(x):
        if x in m and not isinstance(m[x], dict):
            return m[x]
        try:
            return float(x)
        except Exception:
            return None
    a = val(left)
    b = val(right)
    if a is None or b is None:
        return False
    if op == "<":  return a <  b
    if op == "<=": return a <= b
    if op == ">":  return a >  b
    if op == ">=": return a >= b
    if op == "==": return a == b
    if op == "!=": return a != b
    return False

def stage_status(stage: dict, metrics: dict):
    """
    Returns ("GREEN"|"WARNING"|"INVERT", [tripped_signatures])
    - INVERT if any signatures trip hard (by design: any violation is critical)
    - WARNING if metrics are missing for all signatures (unknown) or borderline could be added later
    - GREEN otherwise
    """
    sigs = stage.get("signatures", [])
    tripped = []
    known_any = False
    for s in sigs:
        ok = eval_condition(s, metrics)
        # detect if the signature referenced a known metric
        left = s.split()[0]
        if left in metrics:
            known_any = True
        if ok:
            tripped.append(s)
    if tripped:
        return "INVERT", tripped
    return ("WARNING" if not known_any else "GREEN"), tripped

# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="AI Cultural Health Checker")
    ap.add_argument("--events", required=True, help="events.jsonl")
    ap.add_argument("--glyphs", help="glyph_ledger.jsonl (optional)")
    ap.add_argument("--policy", help="policy.json (optional, overrides defaults)")
    ap.add_argument("--window", type=int, help="window in days (default from policy or 30)")
    args = ap.parse_args()

    events = load_jsonl(args.events)
    if not events:
        print("No events found.", file=sys.stderr)
        sys.exit(2)

    policy = DEFAULT_POLICY
    if args.policy:
        with open(args.policy, "r", encoding="utf-8") as f:
            policy = json.load(f)
    window_days = args.window or policy.get("window_days", 30)

    metrics = compute_metrics(events, window_days=window_days)

    # Header
    print("# Culture Guard Report")
    print(f"Window: {window_days} days")
    print()

    # Metrics summary
    interesting = [
        "alarm_reset_ratio","repeat_roots","residue_per_week","median_ritual_latency",
        "trust_challenges_per_day","status_noise_rate","quiet_hour_compliance",
        "mentor_pairs_per_week","onboard_time_median","action_followthrough_30d"
    ]
    print("## Metrics")
    for k in interesting:
        v = metrics.get(k)
        if v is None:
            print(f"- {k}: unknown")
        else:
            if "time" in k or k.endswith("_latency"):
                print(f"- {k}: {v:.2f} sec")
            else:
                print(f"- {k}: {v:.4f}" if isinstance(v, float) else f"- {k}: {v}")
    print()

    # Stage evaluations
    print("## Stage Evaluations")
    for st in policy.get("stages", []):
        status, tripped = stage_status(st, metrics)
        print(f"- [{status}] {st['stage']} — {st['inversion']}")
        if tripped:
            print(f"  • Signatures tripped: {', '.join(tripped)}")
            cms = st.get("countermeasures", [])
            if cms:
                print("  • Suggested repair rituals:")
                for c in cms:
                    print(f"    - {c}")
        elif status == "WARNING":
            print("  • Insufficient telemetry for this stage; consider logging the metrics listed below.")
        if st.get("metrics_help"):
            print(f"  • Metrics: {st['metrics_help']}")
        print()

    # Optional: glyph info (just a flavor summary)
    if args.glyphs and os.path.exists(args.glyphs):
        try:
            g = load_jsonl(args.glyphs)
            glyphs = Counter(r.get("glyphs","") for r in g if r.get("glyphs"))
            top = glyphs.most_common(8)
            if top:
                print("## Glyph Flavor (top 8)")
                for glyph, n in top:
                    print(f"- {glyph or '(none)'}: {n}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
