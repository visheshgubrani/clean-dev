# Decisions

## D001 Store check-ins as local day strings — accepted (P01)
Context: Streaks are counted in the user's local days.
Decision: Store `YYYY-MM-DD` computed on the client.
Rejected: UTC timestamps — streaks shift across midnight.
Consequence: Changing time zone does not move past days.

## D002 Send reminders from an in-process timer — proposed (P03)
Context: One user and one server process; a few reminders a day.
Decision: A timer in the server process checks due reminders every minute.
Rejected: A job queue — a second service for a handful of jobs a day.
Consequence: Reminders pause while the server is down.
Revisit when: more than one server process runs.
