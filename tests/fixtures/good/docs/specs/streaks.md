# Streaks

Covers: the current streak and the 30-day calendar for each habit. Code: `src/streaks.ts`, `src/routes.ts`.

## Rules
- R1 The current streak counts consecutive local days with a check-in, ending today or yesterday; otherwise it is 0.
- R2 The calendar lists the last 30 local days, oldest first, each marked checked or not.
- R3 An unknown habit id → 404 `habit_not_found`.

## Contracts
- HTTP: `GET /habits/:id/streak` in `src/routes.ts`
