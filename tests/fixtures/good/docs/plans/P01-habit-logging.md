# P01 Habit logging

Kind: feature
Approved: 2026-10-26 T01–T02
Depends on: none

## Goal
The user can create a habit and check it in once per day.

In: create habit, check in today.
Out: editing, deleting, streaks.

## Spec
C1. `checkIn(habitId: number, day: string): Promise<"created" | "exists">` inserts once per day.
C2. Unknown habit id → throws `Error("habit not found")`.

### Choices
| Question | Decision | Why |
| --- | --- | --- |
| Duplicate check-in | Return "exists" | Retries stay safe |

## Builder context
Read first: `src/db/schema.ts`
Reuse:
- `db` — `src/db/client.ts` — Drizzle client
Rules that apply:
- I01 A habit has at most one check-in per local day.
Test one file: `pnpm vitest run <file>`

## Tasks
- [x] P01-T01 Add check-in table
- [ ] P01-T02 Add check-in query
- [ ] P01-T03 Add check-in route

### P01-T01 Add check-in table
Implements: C1
Files:
- `src/db/schema.ts` (edit)
- `drizzle/0001_checkins.sql` (generated)
Do:
1. Add `checkins` with a unique index on `(habit_id, day)`.
Test: `tests/schema.test.ts` (new)
- insert same habit/day twice → unique violation
Check: `pnpm vitest run tests/schema.test.ts`

### P01-T02 Add check-in query
Implements: C1, C2
Files:
- `src/db/queries.ts` (edit)
Do:
1. Add `checkIn` with `ON CONFLICT DO NOTHING`.
Test: `tests/queries.test.ts` (edit)
- first check-in → "created"; second → "exists"
Check: `pnpm vitest run tests/queries.test.ts`

### P01-T03 Add check-in route
Files:
- `src/routes.ts` (edit)
Do:
1. Add `POST /habits/:id/checkins` calling `checkIn`.
Check: `pnpm vitest run tests/routes.test.ts`

## Acceptance
Auto:
- `pnpm vitest run` → pass
Manual:
- Check in twice in the browser → one mark for today

## Changes
- none
