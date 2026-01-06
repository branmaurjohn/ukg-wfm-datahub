# Entities

These pages document Data Hub tables/views at a practical level.

## How entities are generated (public-safe)
- The raw Data Dictionary Excel file is **not** committed to this repo.
- Instead, we generate markdown pages from it and commit the markdown.

## Generate (one-time, safe environment)
Run:

```bash
python tools/generate_entities.py --dictionary /path/to/dictionary.xlsx --out docs/entities
