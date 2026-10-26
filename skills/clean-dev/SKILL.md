---
name: clean-dev
description: "Plan, build, and review applications in small approved phases: frozen plans made of executable task cards, execution notes kept in separate logs, one roadmap holding status, and lean code. Use when starting or continuing an app, planning a phase or bug fix, implementing an approved plan task by task, reviewing a built phase, or adopting this workflow in an existing repo. Designed for a strong model that plans and reviews and a cheaper model that builds."
---

# Clean Dev

## Pick the mode

| The user asks to… | Mode | Also read |
| --- | --- | --- |
| plan, design, propose the next phase, start an app, plan a fix | Plan | [planning.md](references/planning.md), [templates.md](references/templates.md), [lean-code.md](references/lean-code.md) |
| build, implement, execute, or continue a phase or tasks | Build | nothing else; follow this file |
| review a phase or check a build | Review | [planning.md](references/planning.md) (Review gate), [lean-code.md](references/lean-code.md) |
| adopt this workflow, migrate old docs, upgrade from v1 | Adopt | [adopt.md](references/adopt.md), [templates.md](references/templates.md) |
| make one small, specific change | Direct | "Direct changes" below |

If a build request names a phase with no approved tasks left, say so and stop. Never infer approval.

## Records

| File | Holds | Who edits |
| --- | --- | --- |
| `AGENTS.md` | App summary, commands, where things live, hard rules. Max 80 lines. Never status. | planner |
| `docs/ROADMAP.md` | Goal, phase table (**the only place for status**), backlog | planner |
| `docs/ARCHITECTURE.md` | As-built modules, data flow, invariants `I01…`, boundaries | planner |
| `docs/DECISIONS.md` | Lasting choices `D001…`, max 8 lines each | planner |
| `docs/plans/P07-slug.md` | The plan: goal, spec, task cards, acceptance | planner; the builder only ticks boxes |
| `docs/logs/P07-slug.md` | Append-only execution notes: baseline, task entries, reviews, outcome | builder and planner |

IDs and names:
- `P07` is a phase: one user-visible outcome with 3–8 tasks. Its title is an outcome noun ("Email alerts").
- `P07-T03` is a task: one commit. Its title starts with a verb ("Add triage table"), and the commit subject is `P07-T03 Add triage table`.
- `C1…` are spec items local to one plan. `D014` and `I05` are decisions and invariants.
- Never letter, reuse, or renumber IDs. The only word for a piece of a phase is "task".

Phase status, set by the planner in ROADMAP only: `planned → approved → built → done`, plus `dropped`. Progress is the plan's checkboxes. "Blocked" is a log entry, not a status.

## Build mode

You implement an approved plan exactly. You do not redesign it.

1. **Read** AGENTS.md, the plan, and the **last entry** of the phase's log. If that entry says `blocked`, stop and report the question; the planner must answer it first.
2. **Pick** the first unchecked task whose number is inside the plan's `Approved:` line. If there is none, report that and stop.
3. **Baseline:** if the log file (`docs/logs/` with the same filename as the plan) doesn't exist or has no `Baseline` entry, create it, run the Full check from AGENTS.md, and record the result and any pre-existing failures. If `git status` shows uncommitted changes in any file this phase lists, stop and ask.
4. **Implement** only that task:
   - Change only the paths in its `Files:` and `Test:` lines.
   - Follow the Spec and contracts word for word: names, types, error behavior.
   - Private helpers inside those files are fine. Reuse what "Builder context" and AGENTS.md "Where things live" name.
   - Edit minimally. No renames, moves, reformatting, or rewriting whole files.
   - Without a plan line saying so, never add an export, file, dependency, env var, config option, schema change, or public signature change. Never delete, skip, or weaken a test or check.
5. **Stop** — write a `blocked` log entry with the question and options, leave the box unchecked, and report — when:
   - a listed path or symbol is missing, or differs from what the plan says;
   - the task needs a file that isn't listed;
   - a test expectation contradicts the Spec, or you need a design choice the Spec doesn't make;
   - `Check:` still fails after 3 fix attempts;
   - a step needs the user (manual check, credentials, live account, payment).
6. **Finish the task:**
   - Run its `Check:`, then the Fast check.
   - Tick its box, and append a log entry of at most 8 lines (Changed / Check / Notes).
   - If AGENTS.md says `Commits: per-task`, stage only the task's files plus the plan and log by explicit path (never `git add -A` or `.`), and commit as `P07-T03 <title>`.
7. **Continue** to the next task only if the user asked for a range or the whole phase. Always stop after a `Spike:` task.
8. **After the last approved task:**
   - Run the Full check, the plan's Auto acceptance, and the Docs check.
   - Append `Ready for review` and commit the log as `P07 Ready for review`.
   - List the plan's Manual acceptance steps for the user. Don't mark them as passed.
   - Report, and stop.
9. **Never edit** plan text other than checkboxes. Never edit ROADMAP, ARCHITECTURE, DECISIONS, or AGENTS.md unless a card gives the exact text.

Log entry formats (the Docs check parses these headings; the date is today's):

```markdown
# P07 log

## Baseline · 2026-10-26
Full check: `<command>` → pass. Pre-existing failures: none

## P07-T03 · done · 2026-10-26
Changed: `src/a.ts`, `src/a.test.ts`
Check: `<command>` → pass
Notes: none

## P07-T04 · blocked · 2026-10-26
Question: <what the plan doesn't answer, or how it differs from the code>
Options: A) … B) … Recommend A because …

## Ready for review · 2026-10-26
Full check → pass. Auto acceptance → pass. Docs check → pass.
```

Run one builder per phase. Builders run in parallel only on phases whose `Files:` don't overlap, each in its own worktree.

## Direct changes

An explicit user request touching at most 2 files, with no dependency, schema, or contract change, needs no plan or log:
1. For a bug, reproduce it first.
2. Make the change and run the Fast check.
3. Commit as `fix: …` or `chore: …` if commits are on.

Anything larger, or any bug whose cause is unclear, gets a plan (Plan mode, `Kind: fix`).

## Lean code

1. **One owner per concern.** Use the module AGENTS.md lists for config, logging, errors, DB access, API client, dates, validation, and shared types. Never write a second one.
2. **Keep files under ~400 lines and functions under ~80.** Planners split oversized files before adding to them.
3. **A new variant reuses the existing core.** Delete the old path in the same phase.
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
- Approval is explicit and names a phase or task range. A request to build an app does not approve a plan written afterwards.
