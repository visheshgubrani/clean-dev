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

## Rules
- Never hand-edit an applied migration; add a new one.
- Invariants: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#invariants).

## Workflow
Use the clean-dev skill. Status: [docs/ROADMAP.md](docs/ROADMAP.md). Plans: `docs/plans/`. Notes: `docs/logs/`. Decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
- Build one approved task at a time; change only the files its card lists; commit as `P07-T03 <task title>`.
- Never write status or progress in this file.
