import json, sys, pathlib

missing = []
for p in pathlib.Path("sensors").rglob("*.json"):
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        for key in ("decay","energy"):
            if key not in obj:
                missing.append((str(p), key))
    except Exception as e:
        print(f"[ERR] {p}: {e}")

if missing:
    print("Missing fields:")
    for path, key in missing:
        print(f" - {path}: {key}")
    sys.exit(1)
else:
    print("All sensor files contain `decay` and `energy`.")
