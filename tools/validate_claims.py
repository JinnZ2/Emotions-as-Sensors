#!/usr/bin/env python3
"""validate_claims.py -- check CLAIM_TABLE.json and the .claims file against
CLAIM_SCHEMA.py. Stdlib only. CC0.

Checks:
  1  CLAIM_TABLE.json parses; every glyph entry is GLYPH-SCOPED and no
     category (cond/rel/fail/meas) exceeds 16 entries -- the 16-bit masks
     in CLAIM_SCHEMA.encode_claim cannot address a 17th. A longer table
     is REFUSED, not truncated.
  2  id_hash == crc32(handle): derived, never typed.
  3  glyph_form is a declared state. NOT_REPRESENTABLE must carry a reason;
     an empty string is refused (absent-with-reason is not a blank).
     PROVISIONAL (a glyph assigned here for AI readers) must carry the
     glyph, a reason, an originating block that is still
     NOT_REPRESENTABLE with its own reason, and a supersede_when; and the
     assigned glyph must not collide with any decompression glyph the
     repo already carries, or the stand-in would merge with one of its
     own readings.
  4  every .claims line splits into 8 fields; its glyph exists; every
     token in rate/bounds/cond/rel/fail/meas resolves inside that glyph's
     table; rel ids exist; cyc is in CYCLE_ENUM.
  5  binary round trip: each claim -> encode_claim -> decode -> same claim.
     Decoding resolves id_hash through the glyph table rather than
     indexing a list by hash, which is the one place this departs from
     CLAIM_SCHEMA.decode_claim as written.
  6  placeholders: every declared PLACEHOLDER constant occurs in some rate
     or fail expression, and the count is printed, never hidden.
It adjudicates nothing about any channel, body or reading.
"""
import io
import json
import os
import re
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import CLAIM_SCHEMA as CS  # noqa: E402

TABLE = os.path.join(ROOT, "CLAIM_TABLE.json")
CLAIMS = os.path.join(ROOT, "emotions.claims")
MASK_BITS = 16
GLYPH_STATES = ("NOT_REPRESENTABLE", "PROVISIONAL", "UNICODE", "IMAGE_REF")
DECOMPRESSION_FILES = ("data/glyphs.json", "sensors/glyph-map.json",
                       "sensors/alignment/felt.json")
FIELDS = ("id", "rate", "bounds", "cond", "rel", "fail", "meas", "cyc")
LISTS = ("cond", "rel", "fail", "meas")


class Refused(Exception):
    pass


def load_table(path=TABLE):
    t = json.load(io.open(path, encoding="utf-8"))
    for handle, g in t["glyphs"].items():
        for cat in LISTS:
            if len(g[cat]) > MASK_BITS:
                raise Refused("glyph %s: %s has %d entries; a %d-bit mask "
                              "addresses %d" % (handle, cat, len(g[cat]),
                                                MASK_BITS, MASK_BITS))
        if g["id_hash"] != zlib.crc32(handle.encode()):
            raise Refused("glyph %s: id_hash %d != crc32(handle) %d"
                          % (handle, g["id_hash"],
                             zlib.crc32(handle.encode())))
        gf = g["glyph_form"]
        if gf["status"] not in GLYPH_STATES:
            raise Refused("glyph %s: glyph_form.status %r not declared"
                          % (handle, gf["status"]))
        if gf["status"] == "NOT_REPRESENTABLE" and not gf.get("reason", "").strip():
            raise Refused("glyph %s: NOT_REPRESENTABLE with no reason" % handle)
        if gf["status"] == "PROVISIONAL":
            for k in ("glyph", "reason", "supersede_when"):
                if not str(gf.get(k, "")).strip():
                    raise Refused("glyph %s: PROVISIONAL with no %s" % (handle, k))
            o = gf.get("originating") or {}
            if o.get("status") != "NOT_REPRESENTABLE" or not o.get("reason", "").strip():
                raise Refused("glyph %s: PROVISIONAL must keep the originating "
                              "glyph NOT_REPRESENTABLE with a reason" % handle)
            used = _decompression_glyphs()
            if gf["glyph"] in used:
                raise Refused("glyph %s: provisional glyph %r collides with a "
                              "decompression glyph" % (handle, gf["glyph"]))
        if "handle_is_not_the_glyph" not in g:
            raise Refused("glyph %s: handle_is_not_the_glyph undeclared" % handle)
    return t


def _decompression_glyphs():
    """Every glyph string the repo's decompression files carry."""
    out = set()
    for rel in DECOMPRESSION_FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        if isinstance(d, dict):
            out.update(str(v) for v in d.get("glyphs", {}).values())
            if "glyph" in d:
                out.add(str(d["glyph"]))
        elif isinstance(d, list):
            out.update(str(e.get("glyph")) for e in d if isinstance(e, dict))
    return out


def parse_claims(path=CLAIMS):
    out = []
    for n, line in enumerate(io.open(path, encoding="utf-8"), 1):
        s = line.rstrip("\n")
        if not s or s.startswith("#"):
            continue
        parts = s.split("|")
        if len(parts) != 8:
            raise Refused("line %d: %d fields, want 8" % (n, len(parts)))
        c = dict(zip(FIELDS, parts))
        for k in LISTS:
            c[k] = [x for x in c[k].split(",") if x]
        c["cyc"] = int(c["cyc"])
        c["_line"] = n
        out.append(c)
    return out


def resolve(claim, table):
    handle = claim["id"].split(".", 1)[0]
    if handle not in table["glyphs"]:
        raise Refused("line %d: glyph %r not in table" % (claim["_line"], handle))
    g = table["glyphs"][handle]
    if claim["id"] not in g["ids"]:
        raise Refused("line %d: id %s not in glyph ids" % (claim["_line"], claim["id"]))
    for cat, key in (("rate", "rates"), ("bounds", "bounds")):
        if claim[cat] not in g[key]:
            raise Refused("line %d: %s %r not in table" % (claim["_line"], cat, claim[cat]))
    for cat in LISTS:
        for tok in claim[cat]:
            if tok not in g[cat]:
                raise Refused("line %d: %s token %r not in table" % (claim["_line"], cat, tok))
    for r in claim["rel"]:
        if r not in g["ids"]:
            raise Refused("line %d: rel %r is not a claim id" % (claim["_line"], r))
    if claim["cyc"] not in CS.CYCLE_ENUM:
        raise Refused("line %d: cyc %d not in CYCLE_ENUM" % (claim["_line"], claim["cyc"]))
    return handle, g


def mask(items, table_list):
    m = 0
    for it in items:
        m |= 1 << table_list.index(it)
    return m


def pack(claim, g):
    return CS.encode_claim({
        "id_hash": g["id_hash"],
        "rate_idx": g["rates"].index(claim["rate"]),
        "bounds_packed": g["bounds"].index(claim["bounds"]),
        "cond_mask": mask(claim["cond"], g["cond"]),
        "rel_mask": mask(claim["rel"], g["rel"]),
        "fail_mask": mask(claim["fail"], g["fail"]),
        "meas_mask": mask(claim["meas"], g["meas"]),
        "cyc": claim["cyc"],
    })


def unpack(blob, table):
    f = struct.unpack(">IHHHHHHB", blob)
    by_hash = {g["id_hash"]: g for g in table["glyphs"].values()}
    g = by_hash[f[0]]
    return g, {
        "rate": g["rates"][f[1]],
        "bounds": g["bounds"][f[2]],
        "cond": [g["cond"][i] for i in CS.unmask(f[3])],
        "rel": [g["rel"][i] for i in CS.unmask(f[4])],
        "fail": [g["fail"][i] for i in CS.unmask(f[5])],
        "meas": [g["meas"][i] for i in CS.unmask(f[6])],
        "cyc": f[7],
    }


def placeholders(g, claims):
    text = " ".join(c["rate"] for c in claims) + " " + " ".join(
        f for c in claims for f in c["fail"])
    seen = {k: bool(re.search(r"\b%s\b" % re.escape(k), text))
            for k in g["placeholders"]["constants"]}
    return seen


def run(table_path=TABLE, claims_path=CLAIMS, out=sys.stdout):
    t = load_table(table_path)
    claims = parse_claims(claims_path)
    w = out.write
    w("CLAIM TABLE CHECK (glyph-scoped; %d-bit masks)\n" % MASK_BITS)
    n_rt = 0
    for c in claims:
        handle, g = resolve(c, t)
        blob = pack(c, g)
        g2, back = unpack(blob, t)
        want = {k: c[k] for k in ("rate", "bounds", "cyc")}
        want.update({k: sorted(c[k], key=g[k].index) for k in LISTS})
        got = dict(back)
        if g2 is not g or got != want:
            raise Refused("line %d: binary round trip changed the claim" % c["_line"])
        n_rt += 1
        w("  %-22s %2dB  cyc=%s  cond=%d rel=%d fail=%d meas=%d\n"
          % (c["id"], len(blob), CS.CYCLE_ENUM[c["cyc"]], len(c["cond"]),
             len(c["rel"]), len(c["fail"]), len(c["meas"])))
    for handle, g in t["glyphs"].items():
        ids_in_file = {c["id"] for c in claims if c["id"].startswith(handle + ".")}
        w("glyph %s: form %s; ids in table %d, in .claims %d; handle_is_not_the_glyph %s\n"
          % (handle, g["glyph_form"]["status"], len(g["ids"]), len(ids_in_file),
             g["handle_is_not_the_glyph"]))
        if set(g["ids"]) != ids_in_file:
            raise Refused("glyph %s: table ids and .claims ids differ: %s"
                          % (handle, set(g["ids"]) ^ ids_in_file))
        ph = placeholders(g, [c for c in claims if c["id"] in ids_in_file])
        w("  PLACEHOLDER constants: %d declared, %d used in rate/fail, %d measured\n"
          % (len(ph), sum(ph.values()), 0))
        for cat in LISTS:
            w("  %-5s %2d of %d slots\n" % (cat, len(g[cat]), MASK_BITS))
    w("round trips: %d of %d\n" % (n_rt, len(claims)))
    return t, claims


def selftest():
    import copy
    import tempfile
    n = [0]

    def chk(name, ok):
        n[0] += 1
        if not ok:
            sys.stderr.write("FAIL %s\n" % name)
            sys.exit(1)

    t, claims = run(out=io.StringIO())
    chk("real table loads and round-trips", len(claims) == 7)
    g = t["glyphs"]["channel_audit"]
    chk("glyph form PROVISIONAL, originating still NOT_REPRESENTABLE",
        g["glyph_form"]["status"] == "PROVISIONAL"
        and g["glyph_form"]["originating"]["status"] == "NOT_REPRESENTABLE")
    chk("decompression files read and non-empty", len(_decompression_glyphs()) >= 13)
    chk("handle marked not the glyph", g["handle_is_not_the_glyph"] is True)
    chk("no composite field on the glyph", not any(k in g for k in ("score", "total", "index")))

    def refused(mut, name):
        bad = copy.deepcopy(t)
        mut(bad)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(bad, f)
        try:
            load_table(f.name)
            chk(name, False)
        except Refused:
            chk(name, True)
        finally:
            os.unlink(f.name)

    refused(lambda b: b["glyphs"]["channel_audit"]["meas"].extend(
        "x%d" % i for i in range(6)), "17th meas entry is refused")
    refused(lambda b: b["glyphs"]["channel_audit"].__setitem__("id_hash", 1),
            "typed id_hash is refused")
    refused(lambda b: b["glyphs"]["channel_audit"]["glyph_form"].__setitem__("reason", ""),
            "PROVISIONAL with blank reason is refused")
    refused(lambda b: b["glyphs"]["channel_audit"]["glyph_form"].__setitem__("glyph", " "),
            "PROVISIONAL with blank glyph is refused")
    refused(lambda b: b["glyphs"]["channel_audit"]["glyph_form"]["originating"].__setitem__("reason", ""),
            "PROVISIONAL that drops the originating reason is refused")
    refused(lambda b: b["glyphs"]["channel_audit"]["glyph_form"].__setitem__(
        "glyph", sorted(_decompression_glyphs())[0]),
            "provisional glyph colliding with a decompression glyph is refused")
    nr = copy.deepcopy(t); nr["glyphs"]["channel_audit"]["glyph_form"] = {
        "status": "NOT_REPRESENTABLE", "reason": "x", "source": "K"}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(nr, f)
    try:
        load_table(f.name); chk("NOT_REPRESENTABLE with a reason still loads", True)
    except Refused:
        chk("NOT_REPRESENTABLE with a reason still loads", False)
    finally:
        os.unlink(f.name)
    refused(lambda b: b["glyphs"]["channel_audit"]["glyph_form"].__setitem__("status", "EMOJI"),
            "undeclared glyph state is refused")
    refused(lambda b: b["glyphs"]["channel_audit"].pop("handle_is_not_the_glyph"),
            "missing handle_is_not_the_glyph is refused")
    # a claims line naming a token outside its glyph's table is refused
    with tempfile.NamedTemporaryFile("w", suffix=".claims", delete=False) as f:
        f.write("channel_audit.gut|dR/dt += k_g * dB/dt|self,24h,per_meal|B_measured|"
                "channel_audit.fid|NOT_IN_TABLE|stool_log|1\n")
    try:
        c = parse_claims(f.name)
        try:
            resolve(c[0], t)
            chk("unknown fail token is refused", False)
        except Refused:
            chk("unknown fail token is refused", True)
    finally:
        os.unlink(f.name)
    # 16 entries pack and unpack exactly at the mask edge
    full = copy.deepcopy(g)
    full["meas"] = ["m%d" % i for i in range(16)]
    chk("mask addresses exactly 16", mask(full["meas"], full["meas"]) == 0xFFFF)
    print("validate_claims selftest: %d/%d checks pass" % (n[0], n[0]))


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        selftest()
    else:
        try:
            run()
        except Refused as e:
            sys.stderr.write("REFUSED: %s\n" % e)
            sys.exit(1)
