# P01 log

## Baseline · 2026-10-26
Full check: `pnpm lint && pnpm typecheck && pnpm vitest run && pnpm build` → pass
Pre-existing failures: none

## P01-T01 · done · 2026-10-26
Changed: `src/db/schema.ts`, `drizzle/0001_checkins.sql`, `tests/schema.test.ts`
Check: `pnpm vitest run tests/schema.test.ts` → pass
Notes: none
