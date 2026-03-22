# Contributing
- Add new atoms only via `data/glyphs.json`.
- Add composites via `data/composites.json`.
- Add individual sensor definitions as `sensors/{name}.json` or `sensors/{family}/{name}.json`.
- Use lowercase kebab-case for all filenames (except Python files which use snake_case).
- Validate: `python tools/validate.py`.
- Check sensor decay/energy fields: `python tools/validate_decay.py`.
