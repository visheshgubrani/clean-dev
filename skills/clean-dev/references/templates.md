# Record templates

Adapt these to the project. Reuse equivalent existing files and link their actual paths. Replace placeholders with facts; omit unused sections. Keep commands verified, approval pending until received, and proposed architecture clearly labeled.

## AGENTS.md

```markdown
# Project instructions

## Workflow
- Read docs/PLAN.md and its active phase before changing code.
- Write the phase scope, TODOs, and acceptance checks first; wait for explicit user approval before implementation.
- Work on one approved phase at a time. Ask before material changes to approved scope or design.
- Mark tasks complete only after finishing them. Mark the phase done only after its acceptance checks pass.

## Code
- Reuse existing helpers/components; keep responsibilities clear and abstractions minimal.
- Use descriptive names and short comments explaining non-obvious reasons.
- Reproduce bugs before fixing them and verify the original reproduction afterward.
- Preserve unrelated work; review the diff and update affected docs.

## Commands
- Dev: <verified command>
- Checks: <verified commands>

## Records
- Roadmap and current phase: docs/PLAN.md
- Structure and data flow: docs/ARCHITECTURE.md
- Choices and reasons: docs/DECISIONS.md
- Phase TODOs, approvals, and evidence: docs/phases/
```

## docs/PLAN.md

```markdown
# Plan
Goal: <user-visible result>
Constraints: <agreed limits>
Active phase: <link or none>

| Phase | Outcome | Status | Details |
| --- | --- | --- | --- |
| 01 | <one reviewable result> | proposed | [Phase 01](phases/01-short-name.md) |
```

## docs/ARCHITECTURE.md

```markdown
# Architecture
Status: <proposed / implemented; label mixed sections separately>

## Responsibilities and flow
<Main components, relevant paths, and how a request/data moves between them.>

## Data and boundaries
<Storage, contracts, external services, and error ownership.>

## Constraints
<Current limits and links to relevant decisions.>
```

## docs/DECISIONS.md

```markdown
# Decisions

## D001: <choice>
Date: <YYYY-MM-DD> | Status: proposed | Phase: <link>
- Context: <problem or constraint>
- Choice and reason: <recommendation and why>
- Alternative: <viable option and why it was not chosen>
- Consequence: <tradeoff or limitation>
- Approval: pending
```

Append entries only as needed. When superseding an accepted choice, link the replacement and keep the original rationale.

## docs/phases/NN-short-name.md

```markdown
# Phase NN: <name>
Status: proposed
Approval: pending

## Goal and scope
<Outcome, included work, exclusions, and relevant decision IDs.>

## Choices needing input
<Recommendation and unresolved questions, or none.>

## TODOs
- [ ] <concrete implementation task>
- [ ] <verification task>
- [ ] Update affected records and review the diff.

## Acceptance
- <observable behavior or check proving completion>

## Evidence and outcome
<Actual checks/results, changed areas, limitations, and next action.>
```

Use `proposed → approved → in_progress → done`; use `blocked` for unfinished work. Record the user's approval date and scope when granted. Keep evidence empty until observed. For a bug, add reproduction steps, expected/actual behavior, cause, and before/after verification here rather than creating a separate bug diary.
