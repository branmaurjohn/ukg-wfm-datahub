# Grain and Keys

## Grain (the one concept that decides if your report is right)
**Grain = what one row represents.**

Examples of common grains:
- **person-day**: one row per employee per date
- **org-day**: one row per org per date
- **shift-segment**: one row per scheduled segment
- **punch-event**: one row per clock event

If you don’t choose grain first, joins will choose it for you… badly.

## Keys (join glue)
Keys are the fields that make a row unique at your chosen grain.

Best practices:
- Prefer **IDs** over names/labels (labels change)
- Define “unique key” explicitly for each table/view you use
- Validate uniqueness before joining

## Anti-pattern: accidental many-to-many joins
If you join two detail tables that both have multiple rows per person/day, you get inflated totals.

Quick sanity checks:
- row count before join vs after join
- distinct key counts before join vs after join
- “does this dimension have duplicates on my join key?”
