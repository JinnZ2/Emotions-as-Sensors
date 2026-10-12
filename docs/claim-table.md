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

## The glyph has no key-form yet

`glyph_form.status = NOT_REPRESENTABLE` with a reason. The handle
`channel_audit` is a repo-local label and is marked
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
