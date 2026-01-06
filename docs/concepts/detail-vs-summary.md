# Detail vs Summary

## Detail data
Detail data is event-level information (punches, segments, edits, requests, audit events).

Pros:
- great for investigations and drill-through
- shows the “why”

Cons:
- high volume
- easy to double-count
- expensive if you scan wide date ranges

## Summary data
Summary data is pre-aggregated (totals, daily/period metrics).

Pros:
- best for dashboards/KPIs
- faster + cheaper
- fewer duplication traps

Cons:
- you must understand the metric definitions (KPI contract)

## Best practice default
- Dashboards start with **summary**
- Drill-through uses **detail**, tightly filtered by date/employee/org
