# Approval Cycle Time (ESS)

## Business question
How long do requests take to get approved/denied, and where are approvals getting stuck?

## Recommended grains
- Dashboard: **request-day** or **org-day**
- Drill-through: **request-event** (status history)

## Required decisions
- Which request types are included (time off, swap/cover, etc.)
- Start/stop timestamps:
  - created → final decision
  - submitted → final decision
- Reassignment handling (who “owns” the delay)

## Data strategy
- Use request + status history (not just current status)
- Treat workflows as multi-step; measure the total time across steps

## Cost-safe filters
- Bound by request created date
- Partition filters required

## Validation checklist
- Sample a handful of requests and compare timeline to UI history
- Confirm status history ordering and de-duplication

## Common gotchas
- status updates can be re-written (backfills)
- some requests pause waiting on employee input
- “pending” may mean different steps depending on config
