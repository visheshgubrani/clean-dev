---
name: clean-dev
description: "Guide application development with approved phases, lean AGENTS.md instructions, architecture notes, decision records, and verified completion. Use when starting an application, continuing phased development, or fixing bugs under a plan-first workflow. Keep code simple, reusable, and easy for humans to audit."
---

# Clean Dev

## Orient and document

Read applicable `AGENTS.md`, relevant code, manifests, and existing docs. Check the worktree and preserve unrelated changes. Reuse project conventions and the user's stack preferences. If choices are missing, propose the smallest suitable approach and ask before committing to it.

Before approval, inspect, reproduce issues, and write planning docs only. Do not scaffold the app, install dependencies, change implementation/configuration, or deploy. Follow higher-priority instructions if they limit any action.

Maintain these small records; reuse equivalent existing docs instead of creating duplicates:

| File | Purpose |
| --- | --- |
| `AGENTS.md` | Stable rules, verified commands, and links to docs. Aim for under 50 lines. |
| `docs/PLAN.md` | Goal, phase order, status, and links to phase files. |
| `docs/ARCHITECTURE.md` | Component responsibilities, data flow, boundaries, and constraints. Separate proposed from implemented design. |
| `docs/DECISIONS.md` | Important choices, reasons, alternatives, and consequences. |
| `docs/phases/NN-short-name.md` | One phase's scope, approval, TODOs, acceptance checks, and outcome. |

Read [templates.md](references/templates.md) only when creating these records. Keep future phases as brief outlines; detail the next phase before requesting approval. Keep TODOs in the phase file, not a second task log.

## Plan → approve → implement → verify

1. **Plan:** Create the phase file before coding. State its goal, scope, exclusions, concrete TODOs, acceptance checks, and unresolved choices. Size it to one reviewable outcome; use one short phase for a small fix.
2. **Ask:** Present the plan, recommended choices, and questions that affect implementation. Request explicit approval for the named phase and wait. An initial request to build something is not approval of a subsequently written plan. Reuse prior explicit approval of the same scope; the user may approve several documented phases together.
3. **Execute:** Record approval and mark the phase `in_progress`. Work only within approved scope, one phase at a time. Update checkboxes as tasks actually finish. Handle routine implementation details without repeated questions. For a material scope, architecture, dependency, or data-contract change, record the proposal and obtain approval before implementing it.
4. **Verify:** Run focused checks against acceptance criteria and affected behavior, plus applicable project lint/type/build checks. Add meaningful tests for changed behavior; avoid tests that merely mirror implementation. Inspect the diff for duplication, unrelated edits, and stale docs. Record actual commands and results; never claim an unrun check passed.
5. **Close:** Mark `done` only when the agreed scope and acceptance checks are satisfied. Record changed areas, verification evidence, relevant decision IDs, and remaining limitations. Leave incomplete or unverifiable work `blocked`; record the next action. Move deferred work only with user agreement. Update the roadmap and architecture when affected.
6. **Handoff:** Briefly report the result, checks, and next phase. Stop before implementing another phase unless that exact phase already has approval.

## Keep code readable

- Prefer direct, idiomatic code and small modules with clear responsibilities. Separate UI, business rules, and external I/O where useful; do not impose extra layers on a small app.
- Search for existing helpers and components before adding new ones. Extract shared logic when it removes meaningful duplication or clarifies intent; avoid generic helpers for hypothetical future reuse.
- Use descriptive names and explicit inputs/outputs. Handle errors at appropriate boundaries; never silently swallow them.
- Keep comments short and plain: explain a non-obvious reason, constraint, or invariant. Let clear code describe obvious operations.
- Add dependencies or abstractions only for a current, explained need. Avoid unrelated refactors, speculative features, and unnecessary configuration.

## Fix bugs with evidence

Before changing code, reproduce the report with minimal steps or a failing check. Compare expected and actual behavior, inspect the relevant path, and identify the cause. Record this in the phase file, then propose and approve the fix. If reproduction is blocked, record the missing evidence and ask for it; do not guess at a fix. After fixing, rerun the reproduction and check adjacent behavior; add a regression test when practical.

## Record choices without a diary

Log choices affecting behavior, structure, dependencies, schema, interfaces, or meaningful tradeoffs before implementing them. Record a short reason, viable alternative, consequence, and phase link. Mark proposals, accepted choices, and superseded decisions accurately; preserve history. Skip mechanical edits and variable-name trivia.

On resuming, read `AGENTS.md`, the roadmap, the active phase, and only relevant architecture/decision entries. Reconcile records with the code and worktree. Never infer approval from a status label alone or rewrite approved history to match unfinished work. Keep docs factual and concise; never store credentials or sensitive logs.
