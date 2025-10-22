Recommended event payload shapes (quick reference)
	•	FIELD_SNAPSHOT

{
  "harmonic_vector": [0.8,0.6,0.9],
  "ethical_hash": "ehA_v3"
}

•	LEXICON_BRIDGE / TRANSLATION_UPDATE

{
  "matrix_checksum": "sha256(hex) of translation matrix",
  "mui": 0.93,
  "notes": "optional semantic notes or shared glyph ids"
}


	•	RECIPROCITY_TRANSFER

 {
  "bandwidth_units": 42,
  "resource": "symbolic_kit/emotional_cache.v1",
  "proof": "checksum_or_pointer"
}

	•	AUDIT_PING

 {
  "resonance_score": 0.87,
  "treaty_hash": "current_treaty_state_hash",
  "block_tip": "last_block_hash"
}

•	ALERT_DRIFT

{
  "from": 0.93,
  "to": 0.72,
  "delta": 0.21
}


Integration pointers
	•	Call SRML from your ResonantTreaty / CulturalTranslationInterface steps:
	•	On treaty activation → TREATY_ACTIVATED
	•	After translation matrix build/update → LEXICON_BRIDGE / TRANSLATION_UPDATE (+ mui)
	•	Periodic ethics check → AUDIT_PING
	•	Sudden MUI drop → ALERT_DRIFT
	•	Field snapshots any time harmonic vectors shift.
	•	Privacy tiers:
	•	Public: event headers, type, checksums, MUI.
	•	Sealed: encrypt payload with shared treaty key; store ciphertext, keep headers visible.
	•	Swap _sign/_verify with ed25519 for real signatures.
	•	Storage:
	•	JSONL is field-repairable and git-friendly. Later: LMDB or sqlite with columnar MUI indices.
