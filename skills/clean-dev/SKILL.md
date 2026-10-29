---
name: clean-dev
description: "Plan, build, and review applications in small approved phases. A strong model writes the project foundations once (commands, owners, patterns, architecture, decisions), plans one phase at a time as requirements, seams, and outcome tasks, and reviews the result; a cheaper model reads the code, chooses the implementation, writes the tests, and keeps factual docs current. Use when starting or continuing an app, planning a phase or a bug fix, building an approved phase, reviewing or closing a phase, or adopting or upgrading this workflow in an existing repo."
---

# Clean Dev

The planner decides what must hold. The builder decides how. A plan settles behavior and boundaries; new private helpers, internal signatures, file lists, and coding steps belong to the builder.

## Pick the mode

| The user asks to… | Mode | Read |
| --- | --- | --- |
| start an app, plan or design a phase, plan a fix | Plan | [planning.md](references/planning.md), [templates.md](references/templates.md), [plan-example.md](references/plan-example.md) |
| build, implement, execute, or continue a phase or tasks | Build | [building.md](references/building.md) |
| review a phase, clear a checkpoint, answer a blocked task, close a phase | Review | [planning.md](references/planning.md), [lean-code.md](references/lean-code.md) |
| adopt this workflow, or upgrade from v1 or v2 | Adopt | [adopt.md](references/adopt.md), [templates.md](references/templates.md) |
| make one small, clear change | Direct | "Direct changes" below |

If a build request names a phase with no approved tasks left, say so and stop. Never infer approval.

## Records

| File | Holds | Who edits |
| --- | --- | --- |
| `AGENTS.md` | App summary, commands, owners ("Where things live"), Patterns, hard rules. Max 80 lines. Never status. | planner; builder keeps commands and owners current |
| `docs/ARCHITECTURE.md` | As-built modules, data flow, invariants `I01…`, boundaries | planner; builder keeps module rows current |
| `docs/DECISIONS.md` | Lasting choices `D001…`, max 8 lines each | planner |
| `docs/ROADMAP.md` | Goal, phase table (**the only place for status**), phase outlines, backlog | planner |
| `docs/plans/P07-slug.md` | Goal, requirements, design at the seams, tasks, acceptance | planner; the builder only ticks boxes |
| `docs/logs/P07-slug.md` | Append-only: baseline, task entries, blocks, checkpoints, reviews, outcome | builder and planner |

The first four are the foundation. They are written once, kept current, and cited by plans instead of copied into them. A milestone whose design spans several phases may add `docs/TARGET-ARCHITECTURE.md`.

**Patterns** is a short AGENTS.md section naming one exemplar file per kind of change ("New route: copy the shape of `src/routes/orders.ts`"). Builders extend these shapes instead of inventing parallel ones.

IDs and names:
- `P07` is a phase: one user-visible outcome. Its title is an outcome noun ("Email alerts").
- `P07-T03` is a task: one commit. Its title starts with a verb ("Add triage table"), and the commit subject is `P07-T03 Add triage table`.
- `C1…` are requirements local to one plan. `D014` and `I05` are decisions and invariants.
- Never letter, reuse, or renumber IDs. The only word for a piece of a phase is "task".

Phase status, set by the planner in ROADMAP only: `planned → approved → built → done`, plus `dropped`. Progress is the plan's checkboxes. "Blocked" is a log entry, not a status.

Plans with `Format: 3` follow this version. Plans without it are v2 plans with task cards; they keep their rules until converted ([building.md](references/building.md), [adopt.md](references/adopt.md)).

## Approval

- Approval is explicit and names a phase or task range; the plan's `Approved:` line records it. A request to build an app does not approve a plan written afterwards.
- Approval covers the implementation choices inside its scope. It never covers tasks outside the range, or changes to approved requirements, design decisions, contracts, or invariants.

## Direct changes

A change needs no plan or log when all of these hold: the user asked for it explicitly; the cause is clear; it changes no public contract, persisted format, dependency, service, or architecture; and the Fast check is enough to verify it.

1. For a bug, reproduce it first.
2. Make the change, fix docs and comments it makes stale, and run the Fast check.
3. Commit as `fix: …` or `chore: …` if commits are on.

Anything else gets a plan (Plan mode; `Kind: fix` for bugs).

## Lean code

1. **One owner per concern.** Before adding shared code, search AGENTS.md "Where things live" and the code. Add missing helpers to the owner. Never write a second one.
2. **Size is a prompt, not a cap.** A file past ~400 lines or a function past ~80 asks whether it holds a second responsibility. Put a new responsibility in a new module. Never compress formatting to fit a number.
3. **Extend the existing shape.** A new variant reuses the existing core and follows the Patterns exemplar. Delete the old path in the same phase.
4. **No re-export shims or alias names inside an app.** Update the callers.
5. **Validate at trust boundaries only** (env, request input, external APIs, model output, files), with the project's one schema library. Add a custom error class only when a caller catches it.
6. **No interface, base class, or registry before two real implementations.** A test fake counts.
7. **Export only what something imports.** Delete code that your change makes dead. Build nothing for future phases.
8. **Comments explain why.** Never put plan, task, or decision IDs, phase names, or status in code.
9. **One data-access layer.** Routes, handlers, and components stay thin.
10. **Pure logic in the core, I/O at the edges, imports flowing one way.** Test the core directly.

## Always

- Preserve unrelated work. Never revert changes you didn't make.
- Never claim a check passed unless you ran it. Record the actual command and result.
- Never write secrets, tokens, personal data, or pasted command output into docs or logs.
