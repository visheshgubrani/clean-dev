# P02 Streak calendar

Format: 3
Kind: feature
Approved: 2026-10-27 all
Depends on: P01
Touches: `src/streaks.ts` (new), `src/routes.ts`, `src/views/`

## Goal
The user sees each habit's current streak and a 30-day calendar of check-ins.

In: current streak, 30-day calendar per habit.
Out: longest streak, editing past days.

## Requirements
C1. The current streak counts consecutive local days with a check-in, ending today or yesterday; otherwise it is 0.
C2. The calendar lists the last 30 local days, oldest first, each marked checked or not.
C3. An unknown habit id → 404 `{ "error": "habit_not_found" }`.

## Design
Contract:

    GET /habits/:id/streak → 200 { current: number, days: { day: string, checked: boolean }[] }

### Choices
| Question | Decision | Why |
| --- | --- | --- |
| Where streaks are computed | Pure functions over day strings, not SQL | Testable without a database; D001 keeps days as strings |

## Context
Read: I01, D001.
Reuse: `checkIn` in `src/db/queries.ts`; day helpers in `src/dates.ts`.

## Tasks
- [x] P02-T01 Compute streaks from check-in days
  Done when: C1 and C2 hold for empty, gapped and month-crossing histories, tested on the pure functions.
- [ ] P02-T02 Serve the streak endpoint
  Done when: the contract and C3 hold in route tests.
  Checkpoint: first route returning computed data; review its shape before the view uses it.
- [ ] P02-T03 Show the calendar on the habit page
  Done when: the habit page renders the streak and 30 day cells from the endpoint.

## Acceptance
Auto:
- `pnpm vitest run` → pass
Manual:
- Check in on two consecutive days → the habit shows a 2-day streak
