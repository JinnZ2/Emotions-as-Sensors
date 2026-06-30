# Attribution flags — reference table

A flag system for vocabulary that commonly smuggles **motive, moral judgment,
diagnosis, emotion-as-explanation, or mind-reading** into descriptions of
relational dynamics.

**Not a blacklist.** A flagged word is not wrong. It is a signal to slow down and
check whether the word is doing work you did not intend — exactly the "walk more
cautiously here" reflex. Each category below is paired with the observable move
that replaces it.

The runnable version is `attribution_lexicon.py`:

```
python3 attribution_lexicon.py "your description here"
```

It tags every match by category and gives the rewrite. The table below is the
same source, organized for scanning by eye.

---

## The seven categories

| Category | What it smuggles | The tell | Observable replacement |
|---|---|---|---|
| **MOTIVE** | An aim or goal you cannot see | "to / in order to / so that they" | State the act; drop the purpose clause |
| **MORAL** | A verdict (good/bad) dressed as description | "should", "unfair", "toxic" | Name the load or asymmetry; drop the verdict |
| **DIAGNOSIS** | A clinical or role label on a person | "-ist", "-ic", role nouns | Map the dynamic's rules; drop the label |
| **EMOTION_CAUSE** | A feeling used as the explanation | "out of ___", "because they feel" | Same output holds regardless of feeling; remove it |
| **MIND_READING** | An asserted interior state | "feels", "believes", "thinks", "knows" | Replace with what was said or done |
| **CAUSAL_LINK** | A connective asserting an internal cause | "driven by", "out of a need to" | Keep the event sequence; drop the drive |
| **QUANTIFIER** | An absolute that pre-judges frequency | "always", "never", "constantly" | Replace with the observed count or rate |

---

## Why moral language earns the heaviest caution

A moral verdict is the highest-compression form of attribution: it bundles
motive, judgment, and often diagnosis into a single word, and it presents the
bundle as if it were an observation. "Selfish" asserts an interior orientation,
ranks it as bad, and implies it is stable across situations — none of which is
observed. The word *feels* like description because it is short and confident.

The cautious move is not to decide the verdict is false. It is to treat the word
as a marker that an unexamined inference has been compressed into a label, and to
**decompress it back into the observable**: which act, which load, which ledger,
which asymmetry. Often the decompressed version is more useful *and* survives
scrutiny that the label would not.

A "should" is the quiet member of this category. It encodes a norm without
stating it. The fix is to surface the norm as an explicit, contestable condition
rather than leaving it implied inside the word.

---

## Worked decompression

> "She **always** **tries to** **control** the schedule because she **feels
> threatened**, which is **manipulative** and **selfish**."

Five flags, four categories. Decompressed to observable:

> "Across the last N scheduling decisions, the final schedule matched her stated
> preference in M of N. When an alternative was proposed, the proposal was
> reclassified as conflict (Self-Sealing Reframe, R1). The load of re-proposing
> falls on the other party (burden-of-proof transfer); it does not appear on
> hers (externalized cost)."

The decompressed version names counts (testable), rules (mapped), and loads
(located). It drops every interior claim and every verdict — and it is the
version someone else, or an AI, can actually act on.

---

## Note on scope

This table covers the high-frequency offenders in family-systems, psychological,
and everyday relational discourse. It is a work in progress; the runnable lexicon
is the source of truth and grows as new smuggling patterns are found. The point
is never to police language for its own sake — it is to keep the map observable
so that it stays usable and stays falsifiable.
