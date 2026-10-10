# Clean Dev

A lean agent skill for developing applications in approved phases, with readable code and a clear record of the important choices.

Write the plan, get input, implement one phase, verify it, and update the records. Keep the code and documentation small enough for a human to audit.

## Install

Install with [Vercel's Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add visheshgubrani/clean-dev --skill clean-dev -g
```

The CLI lets you choose your coding agent. Omit `-g` to install only in the current project.

The skill uses the standard `SKILL.md` format and is independent of your framework, language, and hosting provider. Read the [complete skill](skills/clean-dev/SKILL.md) or the [record templates](skills/clean-dev/references/templates.md) directly.

## Use

Invoke `clean-dev` through your agent's skill picker or ask it to use the skill. For Codex:

```text
Use $clean-dev to develop this application. Prepare the roadmap and first
phase with TODOs and acceptance checks. Ask for my input before coding.
```

For an existing project:

```text
Use $clean-dev. Read the project instructions and current phase, inspect
what is already implemented, and propose the next reviewable phase.
```

## Workflow

1. **Inspect:** Read the relevant code, project instructions, and existing records. Preserve unrelated work.
2. **Plan:** Write the phase file with its goal, scope, exclusions, TODOs, acceptance checks, and choices needing input.
3. **Approve:** Present the plan and wait for explicit approval of the named phase. Inspection and planning can happen beforehand; application scaffolding, dependency installation, and implementation wait.
4. **Implement:** Work within that phase. Reuse helpers and components, update completed TODOs, and record important decisions. Ask again when a material change would exceed the approved scope or design.
5. **Verify and close:** Run the relevant checks, review the changes, record actual results, and mark the phase done. Stop before the next phase unless it has already been approved.

The user can approve several documented phases together. Routine implementation details within approved scope do not need repeated questions.

## Project records

The skill creates or updates these records in the application being developed. It reuses equivalent existing documentation when available.

| File | What it records |
| --- | --- |
| `AGENTS.md` | Stable rules, verified commands, and links. Target: under 50 lines. |
| `docs/PLAN.md` | Goal, phase order, current phase, statuses, and links. |
| `docs/ARCHITECTURE.md` | Component responsibilities, data flow, boundaries, and constraints. Proposed and implemented designs are labeled separately. |
| `docs/DECISIONS.md` | Important choices, their reasons, alternatives, consequences, and approval status. |
| `docs/phases/NN-short-name.md` | A phase's scope, approval, TODOs, acceptance checks, verification evidence, and outcome. |

Phase states: `proposed → approved → in_progress → done`. Unfinished or unverifiable work stays `blocked` with a next action. Future phases can remain brief outlines until they are ready to plan.

## Code and bug fixes

Keep responsibilities clear, use descriptive names, and extract helpers when they remove meaningful duplication or make the code easier to understand. Add abstractions and dependencies for a current, explained need. Keep comments short and focused on non-obvious reasons or constraints.

For a bug, reproduce the report, compare expected and actual behavior, identify the cause, and get approval for the fix. After changing the code, rerun the original reproduction and check adjacent behavior. Add a regression test when practical. If reproduction is blocked, record the missing evidence and ask for it.

Record choices that affect behavior, structure, dependencies, data, interfaces, or meaningful tradeoffs. Keep mechanical edits and naming trivia out of the decision log.

## Keep it lean

The core instructions are 792 words. Templates load only when creating records. The skill reads the active phase and relevant decisions when resuming, rather than loading the whole project history. Small fixes use one short phase.

These are instructions for the agent; compliance depends on the agent following them. Checks and recorded evidence still need human review.

## Contribute

Open an issue or pull request with a concrete example where the workflow breaks down or adds unnecessary overhead. Keep changes concise and validate them against a realistic task.

## License

[MIT](LICENSE). Copyright 2026 Vishesh Gubrani.
