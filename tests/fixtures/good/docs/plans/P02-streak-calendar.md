# P02 Streak calendar

Format: 4
Kind: feature
Approved: 2026-10-27 all
Depends on: P01
Touches: `src/streaks.ts` (new), `src/routes.ts`, `src/views/`

## Goal
The user sees each habit's current streak and a 30-day calendar of check-ins.

In: current streak, 30-day calendar per habit.
Out: longest streak, editing past days.

## Requirements
C1. [streaks new] The current streak counts consecutive local days with a check-in, ending today or yesterday; otherwise it is 0.
C2. [streaks new] The calendar lists the last 30 local days, oldest first, each marked checked or not.
C3. [streaks new] An unknown habit id → 404 `{ "error": "habit_not_found" }`.

## Design
    GET /habits/:id/streak → 200 { current: number, days: { day: string, checked: boolean }[] }

| Question | Decision | Rejected | Why |
| --- | --- | --- | --- |
| Where streaks are computed | Pure functions over day strings | SQL window functions | Testable without a database; D001 keeps days as strings |

## Tasks
- [x] P02-T01 Compute streaks from check-in days
  Done when: C1 and C2 hold for empty, gapped, and month-crossing histories.
- [x] P02-T02 Serve the streak endpoint
  Done when: the contract and C3 hold in route tests.
- [x] P02-T03 Show the calendar on the habit page
  Done when: the page renders the streak and 30 day cells, with an empty state for a new habit.
- [x] P02-T04 Fix review findings
  Done when: the Review 1 findings routed here are fixed, with a month-boundary test.

## Acceptance
Auto:
- `pnpm vitest run` → pass
Manual:
- Check in on two consecutive days → the habit shows a 2-day streak

## Log

### Ready for review · 2026-10-28
Full check → pass. Auto acceptance → pass. Docs check → pass. Phase diff → clean.

### Review 1 · 2026-10-28
- `src/streaks.ts` `currentStreak` — skips a missing day at a month boundary — compare dates, not day numbers → P02-T04
- `src/views/habit.ts` `fmtDay` — a second day formatter beside `src/dates.ts` — use the owner → fixed

### Ready for review · 2026-10-29
Full check → pass. P02-T04 only.

### Outcome · 2026-10-29
Delivered: current streak and a 30-day calendar per habit. Verified P02-T04.
Specs: streaks R1–R3 added.
Manual: pending: two consecutive days in a real browser
