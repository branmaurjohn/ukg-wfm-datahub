# Overtime Utilization (Rolling 12 Months)

## Business question
Where are we burning overtime, by org and time period?

## Recommended grain
- org-day for dashboards
- person-day for drill-through

## Preferred data strategy
- Start with **summary/totals**
- Use timecard detail only when investigating causes

## Cost-safe filters
- Always bound the date window (example: rolling ~400 days for 12 months + buffer)
- Never run unbounded scans “just to see”

## Validation checklist
- Pick a small sample window (2 pay periods or a month)
- Compare to a trusted reference (UI sample or known export)
- Check join cardinality if totals inflate after joining people/org
- Document what counts as OT (KPI contract)

## Gotchas
- Worked org vs home org will change attribution
- Late edits/backfills can change historical OT
- Paycode mapping/category changes can shift classification
