# Clean Dev

A lean agent skill for building applications in small approved phases. A strong model plans and reviews; a cheaper model builds.

- Plans are made of executable task cards that leave no design calls to the builder.
- Execution notes go into separate logs, so plans stay clean.
- Status lives in one roadmap.
- Lean-code rules come from real projects, and a small linter keeps the records in shape.

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
- **Existing repo:** `Use $clean-dev to adopt this repo.` This archives the old phase docs and writes the new records.
- **Bug:** `Use $clean-dev to plan a fix for <symptom>.` For an obvious change to at most 2 files, just ask; that is a direct change.

The builder takes one task at a time and changes only the files its card lists. It ticks the box, appends a short log entry, and commits as `P07-T03 <task title>`. It stops with a `blocked` log entry instead of improvising when the plan and the code disagree.

## Project records

| File | Holds |
| --- | --- |
| `AGENTS.md` | App summary, commands, where each concern lives, hard rules. 80 lines or fewer, never status. |
| `docs/ROADMAP.md` | Goal, phase table (the **only** place for status), backlog. |
| `docs/ARCHITECTURE.md` | Modules as built, data flow, invariants (`I01…`), boundaries. |
| `docs/DECISIONS.md` | Lasting choices (`D001…`), 8 lines each. |
| `docs/plans/P07-slug.md` | Goal, spec, task cards, acceptance. Frozen after approval except checkboxes. |
| `docs/logs/P07-slug.md` | Baseline, one entry per task, reviews, outcome. Append-only. |

Each ID has one shape and one meaning:

- `P07` is a phase: one outcome, 3–8 tasks, titled as a noun.
- `P07-T03` is a task: one commit, titled with a verb.
- IDs are never lettered or reused.

Phase status goes `planned → approved → built → done`, plus `dropped`.

## Lint the records

```bash
python3 <path-to-skill>/scripts/check_docs.py <project-root>
```

The linter reports:
- missing records;
- bad IDs or statuses;
- plans whose checklist and cards disagree;
- cards without `Files:`, `Do:`, or `Check:`;
- tasks checked outside the approved range;
- a `built` phase with open tasks;
- orphan logs;
- oversized AGENTS.md and status in AGENTS.md;
- legacy plan files.

It exits 1 on errors. Tests: `python3 -m unittest discover -s tests`.

## What's in the skill

| File | Read by | Words |
| --- | --- | --- |
| [SKILL.md](skills/clean-dev/SKILL.md) | every mode: routing, records, builder rules, lean-code rules | ~1,300 |
| [planning.md](skills/clean-dev/references/planning.md) | planner and reviewer | ~1,800 |
| [lean-code.md](skills/clean-dev/references/lean-code.md) | planner and reviewer | ~1,100 |
| [templates.md](skills/clean-dev/references/templates.md) | planner when writing records | ~1,600 |
| [adopt.md](skills/clean-dev/references/adopt.md) | adopting an existing repo | ~500 |

The builder needs only `SKILL.md` and the plan, which keeps the cheap model's context small.

## Upgrading from v1

v1 kept TODOs, approval, and evidence in `docs/phases/NN-name.md` and status in `docs/PLAN.md`. Run `Use $clean-dev to adopt this repo.` That will:

1. archive the old files unchanged under `docs/archive/`;
2. write the roadmap and a lean AGENTS.md;
3. turn any unfinished phase into a v2 plan.

Old decision entries are kept as they are.

## Contribute

Open an issue or pull request with a concrete example where the workflow breaks down or adds unnecessary overhead. Keep changes concise and test them against a realistic task.

## License

[MIT](LICENSE). Copyright 2026 Vishesh Gubrani.
