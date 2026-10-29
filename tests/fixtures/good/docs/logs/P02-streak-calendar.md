# P02 log

## Baseline · 2026-10-27
Full check: `pnpm lint && pnpm typecheck && pnpm vitest run && pnpm build` → pass
Pre-existing failures: none

## P02-T01 · done · 2026-10-27
Changed: `src/streaks.ts` (new), `tests/streaks.test.ts` (new), `docs/ARCHITECTURE.md` (module row)
Check: `pnpm vitest run tests/streaks.test.ts` → pass
Choices: the functions take day strings sorted by the query, so they never sort
Notes: none
