# claim-table

How `CLAIM_TABLE.json` and `emotions.claims` carry a compression glyph.

## The glyph is a key, the table is the expansion

`CLAIM_SCHEMA.py` packs a claim into 17 bytes. The first 4 are an
`id_hash`; the rest are indices and 16-bit masks into a lookup table.
A glyph here is that `id_hash`: one key standing for a whole constraint
set. What the table stores under it is what the glyph compresses TO,
which is physics. No English gloss of the glyph is stored anywhere.

## Glyph-scoped tables

A 16-bit mask addresses 16 entries. A single repo-wide table overflows
that before it reaches a second glyph, so every lookup list lives under
its glyph in `CLAIM_TABLE.json["glyphs"][handle]`. `tools/validate_claims.py`
refuses a 17th entry rather than truncating. A claim's glyph is the text
before the first `.` in its id.

## The glyph: provisional for AI readers, originating still unkeyed

The originating glyph has no key-form. [stated, K] it is likely
catalogued elsewhere under a classification that is not its function,
so a keyboard form may be a long way off. Work does not wait on it: a
PROVISIONAL glyph, `U+29BF` (circled bullet), is assigned under
`glyph_form` with the reason recorded there, for AI readers only. It
pictures the structure the bundle compresses (a reading enclosed by the
channels it sits in), carries no family meaning elsewhere in this repo,
and collides with none of the decompression glyphs; the checker refuses
a collision. The `originating` block stays `NOT_REPRESENTABLE` with its
own reason, and `supersede_when` says the stand-in is retired, not kept
as an alias, once a key-form exists.

The binary codec never needed a glyph string: the 4-byte `id_hash` is
the key. The provisional glyph is for shared reference between a human
and an AI reader, nothing more.

The handle `channel_audit` is a repo-local label and is marked
`handle_is_not_the_glyph`. The unicode glyphs already in this repo
(`data/glyphs.json`, `sensors/glyph-map.json`, `sensors/alignment/felt.json`)
are recorded as decompressions of the originating glyph, written for AI
readers; they are readings of it, not the glyph.

## The bundle

Seven claims under one glyph: one per channel the reading sits in (gut
biome, mitochondria, hormones, exogenous chemistry, circadian state), one
for reception fidelity, one for the audit itself. Each channel claim has
its own `fail` condition. A channel that is unmeasured is `UNRATED` on
that channel, kept apart from a channel measured and found flat. No
composite across channels is emitted.

Every constant (`k_g k_m k_h k_c k_t a l r N`) is PLACEHOLDER: declared so
the bundle parses, measured by nobody. The checker prints the count.

## Run

    python3 tools/validate_claims.py            # resolve, round-trip, report
    python3 tools/validate_claims.py --selftest # plants defects, proves each refusal fires
