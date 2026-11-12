---
name: clean-dev
description: "Plan, build, and review applications in small approved phases with lean, lasting engineering records. A strong model writes the foundations (constraints, stack decisions with tradeoffs, architecture with diagrams, living specs, owners and patterns), plans one phase at a time as requirements and seams, and reviews the real diff once; a cheaper model builds, tests, and commits each task with its choices in the commit. Use when starting or continuing an app, planning a phase or a fix, building an approved phase, reviewing or closing a phase, writing specs or architecture docs, or adopting or upgrading this workflow in an existing repo."
---

# Clean Dev

The planner decides what must hold. The builder decides how. A fresh reviewer reads the real diff once. Every fact has one home, and git carries the history.

## Pick the mode

| The user asks to… | Mode | Read |
| --- | --- | --- |
| start an app; adopt or upgrade this workflow; write or fix ARCHITECTURE, a spec, DECISIONS, or AGENTS.md | Foundations | [foundations.md](references/foundations.md), [templates.md](references/templates.md) |
| plan or design a phase, plan a fix | Plan | [planning.md](references/planning.md), [templates.md](references/templates.md), [plan-example.md](references/plan-example.md) |
| build, implement, or continue a phase, or its fix task | Build | [building.md](references/building.md) |
| review, verify, or close a phase; answer a blocked task; clear a checkpoint | Review | [review.md](references/review.md), [lean-code.md](references/lean-code.md) |
| make one small, clear change | Direct | "Direct changes" below |

If a build request names a phase with no approved tasks left, say so and stop. Never infer approval.

## One home per fact

| Record | Holds | Who edits |
| --- | --- | --- |
| `AGENTS.md` | Summary, commands, owners, Patterns, "When you change", Gotchas, rules. 80 lines or fewer. Never status. | planner; builder keeps commands and owners current |
| `docs/ARCHITECTURE.md` | Structure as built: context diagram, modules, import direction, invariants `I01…`, boundaries, glossary, spec list | planner and reviewer; builder keeps module rows current |
| `docs/specs/<area>.md` | What one area does now: rules `R1…`, a flow diagram, pointers to contract files | reviewer at close; planner when creating one |
| `docs/DECISIONS.md` | Why: lasting choices `D001…` with the rejected alternative, 8 lines each | planner |
| `docs/ROADMAP.md` | Goal, constraints, phase table (**the only place for status**), outlines, backlog | planner and reviewer |
| `docs/plans/P07-slug.md` | What this phase changes: requirements, seams, tasks; then an append-only Log | planner; builder ticks boxes and appends Log entries |
| git commits | What each task did and chose: one commit per task, with `Check:`, `Choices:`, and `Follow-up:` trailers | builder |

When two records would say the same thing, one cites the other. Code that can generate a reference (env vars, API docs, types) generates it, and the docs link to it.

## IDs and status

- `P07` is a phase: one user-visible outcome, titled as a noun ("Email alerts").
- `P07-T03` is a task: one commit, titled with a verb. The commit subject is the task line, `P07-T03 Add triage table`.
- `C1…` are requirements local to one plan. `R1…` are rules local to one spec, cited as `checkout R6`. `D014` is a decision and `I05` an invariant.
- Never letter, reuse, or renumber IDs, and never put any of them in code.

Phase status, kept in ROADMAP only: `planned → approved → built → done`, plus `dropped`. `built` means the review passed; `done` means the manual checks passed, the user waived them, or there were none. Progress is the plan's checkboxes. "Blocked" is a Log entry, not a status.

Plans with `Format: 4` follow this version. Older plans and `docs/logs/` are history; leave them as they are ([foundations.md](references/foundations.md) "Upgrading").

## Approval

- Approval is explicit and names a phase or a task range; the plan's `Approved:` line records it. A request to build an app does not approve a plan written afterwards.
- Approval covers the implementation choices inside its scope, plus the one review fix task that makes approved requirements hold.
- It never covers new scope, or changes to approved requirements, contracts, decisions, or invariants.

## Risk checklist

The planner states each item that applies as a requirement, the builder tests it, and the reviewer checks it.

- **Input:** invalid, empty, oversized, or unknown fields.
- **External calls:** errors, timeouts, retries, and what the caller sees.
- **Repeats and races:** idempotency, double submit, lost responses, concurrent writers, and the lock order in ARCHITECTURE.
- **Time:** zone, day boundaries, clock source, DST.
- **Existing data:** additive migrations, backfill, old rows and clients, rollback.
- **Untrusted content:** user input, email, web pages, model output; path traversal, open redirects, injection.
- **Secrets and personal data:** never in logs, errors, or captured output.
- **Screens:** loading, empty, error, and partial-failure states.
- **Performance:** numbers from ROADMAP `Constraints:`, measured by Auto acceptance.
- **LLM behavior:** a fixed eval-case file with objective pass criteria, rerun on every prompt change.
- **Ownership:** a second helper for a concern that already has an owner.

## Direct changes

A change needs no plan when all of these hold: the user asked for it explicitly; the cause is clear; it changes no public contract, persisted format, dependency, service, or architecture; and the Fast check is enough to verify it.

1. For a bug, reproduce it first.
2. Make the change, fix the docs and comments it makes stale, and run the Fast check.
3. Commit as `fix: …` or `chore: …`, with a `Check:` trailer.

Anything else gets a plan (Plan mode; `Kind: fix` for bugs).

## Lean code

1. **One owner per concern.** Before adding shared code, search AGENTS.md "Where things live" and the code. Add missing helpers to the owner; never write a second one.
2. **Size is a prompt, not a cap.** A file past ~400 lines or a function past ~80 asks whether it holds a second responsibility. Put a new responsibility in a new module. Never compress formatting to fit a number.
3. **Extend the existing shape.** A new variant reuses the existing core and follows the Patterns exemplar. Delete the old path in the same phase.
4. **No re-export shims or alias names inside an app.** Update the callers.
5. **Validate at trust boundaries only** (env, request input, external APIs, model output, files), with the project's one schema library. Add a custom error class only when a caller catches it.
6. **No interface, base class, or registry before two real implementations.** A test fake counts.
7. **Export only what something imports.** Delete code your change makes dead. Build nothing for future phases.
8. **Comments explain why.** Never put plan, task, rule, or decision IDs, phase names, or status in code.
9. **One data-access layer.** Routes, handlers, and components stay thin.
10. **Pure logic in the core, I/O at the edges, imports flowing one way.** Test the core directly.

## Always

- Preserve unrelated work. Never revert changes you didn't make.
- Never claim a check passed unless you ran it. Record the actual command and result.
- Stage by explicit path, never `git add -A` or `git add .`.
- Never write secrets, tokens, personal data, infrastructure IDs, or pasted command output into docs, logs, or commit messages.
