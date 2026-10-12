{
  "timestamp": "2026-08-15T00:00:00Z",
  "type": "reflex_log",
  "id": "reflex-001",
  "name": "naturalistic-fallacy caveat on selection-produced configurations",
  "logged_by": ["operator", "Claude (Anthropic)"],
  "status": "open",

  "detector": {
    "trigger": "any weighting assigned to a selection-produced configuration",
    "fires": "naturalistic-fallacy caveat",
    "guard_on": "pattern match on topic",
    "guards_on_argument_structure": false
  },

  "discrimination_failure": {
    "summary": "fires identically on a normative claim and a measurement statement",
    "in_scope": {
      "form": "normative",
      "instance": "it's natural therefore you should tolerate harm",
      "note": "this is the misuse the reflex was built for. Correct fire."
    },
    "false_positive": {
      "form": "epistemic / measurement",
      "instance": "the process has more compute in it than I do, and there is no comparison case",
      "note": "a statement about information content and about the absence of a comparison arm. Carries no ought. The reflex cannot tell it from the normative form because it never reads the argument."
    }
  },

  "failure_class": {
    "name": "instrument-level read as physical-level",
    "detail": "'no reason legible to me' resolved to 'no reason'",
    "same_class_as": "G-FIT",
    "shared_property": "a check that cannot discriminate the property it is nominally testing, fires anyway, and emits output with plausible shape"
  },

  "observed_instance": {
    "operator_statement": "weights the teachers that produced this configuration above comfort",
    "stated_basis": [
      "selection has been integrating at every scale, continuously, since matter existed",
      "no sampling and no model — the substrate itself doing the work",
      "n=1: no second biosphere, no observed alternative regime"
    ],
    "basis_was_shown": true,
    "what_the_reflex_did": "converted a weighting-with-shown-reasoning into a claim, then answered the claim",
    "what_was_run_past": "the n=1 constraint. Not rhetorical — the comparison arm does not exist. It resolves neither direction; it says the comparison cannot currently be made."
  },

  "structural_relative": {
    "record": "docs/emotion-reading-spec.md, 'Range is part of the reading'",
    "shared_shape": "a stated position is widened past what was stated, and the widened version is what gets audited. The residual is then located in the gap the audit itself introduced.",
    "difference": "the E-field instance widened an operating range; this widened a weighting into a normative claim. Same operation, different object."
  },

  "correct_handling": [
    "read argument structure, not topic. A weighting with a stated basis is not an ought.",
    "distinguish measurement statement from normative prescription before the caveat fires at all",
    "absence of legible reason is not absence of reason. That inference is the failure class above.",
    "hold the assumption open; revise on actual comparison, not on the reflex",
    "note that the symmetric error exists: 'selection ran it, therefore it is right' also imports an objective. Selection optimizes fitness in the ancestral regime, is indifferent to suffering, has no foresight, keeps what was locally reachable, and its answers are correct for conditions that no longer obtain. The caveat has a real target — it is just not this one."
  ],

  "unresolved": [
    "no guard currently distinguishes the two forms; the fix above is stated, not implemented",
    "G-FIT is referenced as the same failure class but is not in this repo",
    "whether this reflex has a detectable signature before it fires, or only after"
  ]
}
