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
- Phase diff: `python3 ~/.agents/skills/clean-dev/scripts/phase_diff.py <phase>`

## Where things live
One owner per concern. Search here before adding shared code; never create a second.
- Config/env: `src/env.ts`
- Database access: `src/db/queries.ts`
- Dates/time: `src/dates.ts`

## Patterns
Copy the shape of these files; extend them instead of starting a parallel style.
- Route: `src/routes.ts` `POST /habits/:id/checkins` (parse input, call one query, map the result)
- Query: `src/db/queries.ts` `checkIn` (one function per operation, typed result)
- Test: `tests/queries.test.ts` (behavior at the public function, fresh database per test)

## When you change
- The database schema → run `pnpm db:generate` and commit the migration (CI fails on a schema diff).

## Gotchas
- Day strings come from the client's zone; never derive "today" on the server (D001).

## Rules
- Never hand-edit an applied migration; add a new one.
- Invariants: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#invariants).

## Workflow
Use the clean-dev skill. Status: [docs/ROADMAP.md](docs/ROADMAP.md). Plans: `docs/plans/`. Specs: `docs/specs/`. Decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
- Commit each task as `P07-T03 <task title>` with a `Check:` trailer.
- Never write status or progress in this file.
