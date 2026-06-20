# Usage split — the same word, two ways

The constraint was never on the *word*. It is on whether the word is pinned to
an **act** or pinned to a **person**.

- **Observable-effect usage** names an act, effect, or pattern. Clean. Usable.
- **Attributive usage** labels the person as a trait, nature, motive, or
  diagnosis. Smuggles the unobservable.

"Manipulation occurred" (an effect) is not "she is manipulative" (a trait).
"Narcissistic behavior" (a pattern) does not require "he is a narcissist" (an
identity). You can keep the word — you cannot pin it to the person.

Runnable companion: `usage_split.py`

```
python3 usage_split.py narciss      # one term
python3 usage_split.py              # all terms
```

---

## Three tiers

Not every word has a clean usage. The honest move is to say so.

| Tier | Meaning |
|---|---|
| **SPLITTABLE** | Has a clean observable usage *and* an attributive usage. Keep the observable form; flag the attributive form. |
| **REPLACE_ONLY** | Functions only as a verdict. No clean observable usage exists. Replace the word entirely with the named load/asymmetry. |
| **SENSITIVE** | An observable category exists, but the usable form requires naming the *specific act*, never the label on the person. |

---

## SPLITTABLE — keep the observable form

| Term | Observable (clean) | Attributive (flagged) |
|---|---|---|
| **manipulation / manipulative** | "a manipulation of the option set" — choices narrowed by reframing | "she is manipulative" — trait + aim |
| **narcissistic / narcissist** | "the narcissistic pattern" — competing accounts reclassified as attacks | "he is a narcissist" — identity label |
| **controlling / control** | "a constraint imposed on the schedule" | "he is controlling" — disposition |
| **gaslighting** | the reframe pattern — observation reclassified as the observer's fault | "he is a gaslighter" — role |
| **defensive / defensiveness** | topic shifted from content to the character of the namer | "she's so defensive" — trait |
| **dismissive** | observation set aside without its content addressed | "he is dismissive" — trait |
| **passive-aggressive** | grievance expressed through an indirect act, not stated | "he's passive-aggressive" — trait |
| **withdrawal / avoidant** | "engagement dropped after event X" | "he's avoidant" — attachment-style diagnosis |

The strongest form of each is not the pattern-name but the **decomposition** —
the specific rule and load. Pattern-naming ("the narcissistic pattern") is
acceptable shorthand; mapping to a rule ("competing account → reclassified as
hostility; burden-of-proof transferred") is stronger and more testable.

---

## SENSITIVE — name the act, never the label

| Term | Observable (clean) | Attributive (flagged) |
|---|---|---|
| **abuse / abusive** | "On [date], [specific act] occurred; it transferred [load]" | "he is abusive" — whole-person label |

Naming the specific act, with date and load, is also exactly what makes a record
usable by someone else later. The label compresses away the very detail a record
needs.

---

## REPLACE_ONLY — the word is a verdict; swap it out

| Term | Why it has no clean form | Replace with |
|---|---|---|
| **toxic** | global appraisal, not an observation | the load, the asymmetry, the ledger |
| **selfish** | asserts an interior orientation and ranks it | the externalized-cost description |
| **unfair** | a verdict about a norm left unstated | counts per ledger; surface the norm as a condition |

---

## The grammatical tell

When in doubt, check what the word is attached to:

- attached to an **act / effect / pattern / sequence** → likely observable, keep it
- attached to the **person** as *is / are / a ___* → attributive, flag it

"A manipulation occurred" vs "she **is** manipulative."
"Narcissistic **behavior**" vs "he **is a** narcissist."
"Engagement **dropped**" vs "he **is** avoidant."

The first of each pair points at something countable and falsifiable. The second
points at a person and closes the question. Work in progress; the runnable module
is the source of truth.
