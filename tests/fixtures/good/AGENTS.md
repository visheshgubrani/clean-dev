# Habit tracker

Single-user web app for logging daily habits and seeing streaks.
Stack: TypeScript, Hono, SQLite via Drizzle, Vitest.

## Commands
- Setup: `pnpm install`
- Dev: `pnpm dev`
- Test one file: `pnpm vitest run <file>`
- Fast check: `pnpm lint && pnpm typecheck && pnpm vitest run`
- Full check: `pnpm lint && pnpm typecheck && pnpm vitest run && pnpm build`
- Docs check: `python3 ~/.agents/skills/clean-dev/scripts/check_docs.py .`
- Commits: per-task

## Where things live
One owner per concern. Reuse it; never create a second. The planner adds new owners here.
- Config/env: `src/env.ts`
- Database queries: `src/db/queries.ts`
- Dates/time: `src/dates.ts`

## Patterns
Copy the shape of these files; extend them instead of starting a parallel style.
- Route: `src/routes.ts` `POST /habits/:id/checkins` (parse input, call one query, map the result)
- Query: `src/db/queries.ts` `checkIn` (one function per operation, typed result)
- Test: `tests/queries.test.ts` (behavior at the public function, fresh database per test)

## Rules
- Never hand-edit an applied migration; add a new one.
- Invariants: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#invariants).

## Workflow
Use the clean-dev skill. Status: [docs/ROADMAP.md](docs/ROADMAP.md). Plans: `docs/plans/`. Notes: `docs/logs/`. Decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
- Build approved tasks in order within the phase's scope; commit each as `P07-T03 <task title>`.
- Never write status or progress in this file.
