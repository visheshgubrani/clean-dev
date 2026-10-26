# Decisions

## D001 Store check-ins as local day strings — accepted (P01)
Context: Streaks are counted in the user's local days.
Decision: Store `YYYY-MM-DD` computed on the client.
Rejected: UTC timestamps — streaks shift across midnight.
Consequence: Changing time zone does not move past days.
