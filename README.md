# Clean Dev

A lean agent skill for building applications in small approved phases. A strong model decides what must hold; a cheaper model decides how.

- **Foundations once.** Commands, owners, Patterns (one exemplar file per kind of change), architecture, and decisions are written once and kept current. Plans cite them instead of copying them.
- **Plans settle behavior and boundaries.** Each plan states requirements, the contracts at the seams it changes, consequential choices, and outcome tasks with a `Done when:` each. It leaves out private helpers, internal signatures, file lists, and coding steps.
- **Builders own the implementation.** Within the approved phase, the builder reads the code, chooses the design of internals, writes the tests, and keeps factual docs current. It stops only when the approved design would have to change.
- **Review carries the quality bar.** The strong model reads the real diff for coverage, correctness, architecture, duplication, and complexity, instead of pre-writing the code.
- Status lives in one roadmap. Execution notes go into separate logs. A small linter keeps the records in shape.

## Install

Install with [Vercel's Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add visheshgubrani/clean-dev --skill clean-dev -g
```

The CLI lets you choose your coding agent. Omit `-g` to install only in the current project. The skill uses the standard `SKILL.md` format and works with any language or framework. The linter needs Python 3.9+ and no packages.

## The two-model loop

| Step | Model | Prompt |
| --- | --- | --- |
| Plan | strong | `Use $clean-dev to plan the next phase: <what you want>.` |
| Approve | you | `Approve P07 T01–T04.` (or `Approve P07.`) |
| Build | cheap | `Use $clean-dev to build P07 T01–T04.` |
| Review | strong | `Use $clean-dev to review P07.` |
| Close | strong | `Use $clean-dev to close P07.` |

Other entry points:

- **New app:** `Use $clean-dev to start <app idea>. Write the roadmap and plan P01.`
- **Existing repo:** `Use $clean-dev to adopt this repo.` This archives the old phase docs and writes the foundation records.
- **Bug:** `Use $clean-dev to plan a fix for <symptom>.` A small change with a clear cause that touches no contract, schema, or dependency is a direct change; just ask.

What each model does:

| Strong model (planner, reviewer) | Cheap model (builder) |
| --- | --- |
| Foundations: commands, owners, Patterns, architecture, decisions | Reads the code the task touches, and the phase log |
| Requirements and failure cases | Picks internal files, helpers, and signatures; searches owners before adding any |
| Exact contracts where the phase changes a seam | Implements, writes tests, and runs the checks |
| Task order, spikes, and checkpoints | Updates commands, owners, module rows, and stale comments |
| Review of the real diff; clears checkpoints; answers blocks | Logs notable choices; blocks only when the approved design would change |

The builder commits each task as `P07-T03 <task title>`, ticks its box, and appends a short log entry. It stops after a `Checkpoint:` task until the planner records `cleared`.

## Project records

| File | Holds |
| --- | --- |
| `AGENTS.md` | App summary, commands, owners, Patterns, hard rules. 80 lines or fewer, never status. |
| `docs/ROADMAP.md` | Goal, phase table (the **only** place for status), phase outlines, backlog. |
| `docs/ARCHITECTURE.md` | Modules as built, data flow, invariants (`I01…`), boundaries. |
| `docs/DECISIONS.md` | Lasting choices (`D001…`), 8 lines each. |
| `docs/plans/P07-slug.md` | Goal, requirements, design at the seams, tasks with `Done when:`, acceptance. About 200 lines or fewer. |
| `docs/logs/P07-slug.md` | Baseline, task entries with the builder's choices, blocks, checkpoints, reviews, outcome. Append-only. |

Each ID has one shape and one meaning:

- `P07` is a phase: one user-visible outcome, titled as a noun.
- `P07-T03` is a task: one commit, titled with a verb.
- IDs are never lettered or reused.

Phase status goes `planned → approved → built → done`, plus `dropped`. Only the next phase in each independent track gets a detailed plan; later phases stay as outlines.

## Lint the records

```bash
python3 <path-to-skill>/scripts/check_docs.py <project-root>
```

The linter reports:
- missing records;
- bad IDs or statuses;
- tasks checked outside the approved range;
- a `built` phase with open tasks;
- orphan logs and entries for unknown tasks;
- oversized AGENTS.md and status in AGENTS.md;
- legacy plan files;
- for v3 plans (`Format: 3`): missing sections or header lines, tasks without `Done when:`, a missing `Touches:`, and plans over 250 lines;
- for v2 plans: checklists and cards that disagree, and cards without `Files:`, `Do:`, or `Check:`.

It exits 1 on errors. Tests: `python3 -m unittest discover -s tests`.

## What's in the skill

| File | Read by | Words |
| --- | --- | --- |
| [SKILL.md](skills/clean-dev/SKILL.md) | every mode: routing, records, approval, lean-code rules | ~1,000 |
| [building.md](skills/clean-dev/references/building.md) | builder | ~950 |
| [planning.md](skills/clean-dev/references/planning.md) | planner and reviewer | ~2,400 |
| [plan-example.md](skills/clean-dev/references/plan-example.md) | planner: one phase written as v2 and as v3 | ~1,400 |
| [lean-code.md](skills/clean-dev/references/lean-code.md) | reviewer, and anyone who needs the long form of the rules | ~1,200 |
| [templates.md](skills/clean-dev/references/templates.md) | planner when writing records | ~1,800 |
| [adopt.md](skills/clean-dev/references/adopt.md) | adopting a repo, or upgrading from v2 | ~800 |

The builder reads `SKILL.md`, `building.md`, AGENTS.md, and the plan. The planner never loads the build procedure.

## Upgrading from v2

v2 plans keep working. Plans with `Format: 3` use the new rules, and plans without it keep the v2 rules, so one repo can hold both.

1. Leave done phases and their logs as they are.
2. Let an active v2 phase finish on v2 rules, or convert its remaining tasks explicitly.
3. Convert each unstarted phase only when it is next. Rewrite its plan to v3 against the current code, keeping requirements, seams, and consequential choices.
4. Add a Patterns section to AGENTS.md.

See [adopt.md](skills/clean-dev/references/adopt.md) "Upgrading from v2". v1 repos (`docs/phases/`, `docs/PLAN.md`) run `Use $clean-dev to adopt this repo.` first.

## Contribute

Open an issue or pull request with a concrete example where the workflow breaks down or adds unnecessary overhead. Keep changes concise and test them against a realistic task.

## License

[MIT](LICENSE). Copyright 2026 Vishesh Gubrani.
