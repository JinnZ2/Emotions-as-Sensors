import json, sys, pathlib
from jsonschema import validate, Draft202012Validator

schema_dir = pathlib.Path(__file__).parent.parent/'schemas'
data_dir = pathlib.Path(__file__).parent.parent/'data'

with open(schema_dir/'emotion.schema.json') as f: emo_schema = json.load(f)
with open(schema_dir/'unified-sensor-event.schema.json') as f: event_schema = json.load(f)

Draft202012Validator.check_schema(emo_schema)
Draft202012Validator.check_schema(event_schema)

print("Schemas OK")

# Validate composites
with open(data_dir/'composites.json') as f: comps = json.load(f)
atoms = set(emo_schema["definitions"]["atom"]["enum"])
for c in comps["composites"]:
    missing = [a for a in c["atoms"] if a not in atoms]
    if missing:
        print(f"[ERR] {c['name']}: unknown atoms {missing}"); sys.exit(1)
print("Data OK")
