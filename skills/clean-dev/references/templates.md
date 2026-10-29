# Record templates

`scripts/check_docs.py` parses these formats. Keep the headings, field names, and ID shapes exactly as shown.

## How to fill them in

- Replace placeholders with facts and omit optional parts you don't use.
- Never record secrets, tokens, personal data, or pasted command output.
- Paths are repo-relative and never carry line numbers (`src/mail/triage.ts`, not `src/mail/triage.ts:120`).

## AGENTS.md

Keep it at 80 lines or fewer. It holds stable facts only: no status, progress, dates, test counts, or generic style advice.

```markdown
# <App name>

<What it does and for whom, in 1–3 lines.>
Stack: <language, framework, database, key services>.

## Commands
- Setup: `<verified command>`
- Dev: `<verified command>`
- Test one file: `<command with <file> placeholder>`
- Fast check: `<lint + typecheck + unit tests; under ~1 minute>`
- Full check: `<everything CI or release needs>`
- Docs check: `python3 <absolute path to clean-dev>/scripts/check_docs.py .`
- Commits: per-task

## Where things live
One owner per concern. Search here before adding shared code; never create a second.
- Config/env: `<path>`
- Logging: `<path>`
- Errors: `<path>`
- Database queries: `<path>`
- API/HTTP client: `<path>`
- Dates/time: `<path>`
- Validation schemas: `<path>`
- Shared contracts/types: `<path>`

## Patterns
Copy the shape of these files; extend them instead of starting a parallel style.
- Route: `<path>` (<what to copy, e.g. parse with its schema, call one service, map the result>)
- Service: `<path>` (<…>)
- Schema change: `<path>` (<…>)
- Test: `<path>` (<…>)

## Rules
- <Project hard rule, one line, e.g. "Never hand-edit an applied migration; add a new one.">
- Invariants: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#invariants).

## Workflow
Use the clean-dev skill. Status: [docs/ROADMAP.md](docs/ROADMAP.md). Plans: `docs/plans/`. Notes: `docs/logs/`. Decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
- Build approved tasks in order within the phase's scope; commit each as `P07-T03 <task title>`.
- Never write status or progress in this file.
```

- `Commits:` is `per-task` (the default) or `off` (when the user commits manually).
- Remove any concern from "Where things live" that the app doesn't have yet.
- Add a Patterns line only when a good exemplar exists.

## docs/ROADMAP.md

This file is the only place phase status lives.

```markdown
# Roadmap

Goal: <who uses the app and what it does for them, 1–2 sentences>
Not doing: <product-level exclusions>

## Phases

| ID | Phase | Status | Plan |
| --- | --- | --- | --- |
| P01 | Walking skeleton | done | [plan](plans/P01-walking-skeleton.md) |
| P02 | Email alerts | approved | [plan](plans/P02-email-alerts.md) |
| P03 | Lead tracking | planned | — |

Outlines:
- **P03** <outcome in one line>. Depends on: P02. Risk: <the main unknown, or none>.

## Backlog
- <idea, request, or bug not yet in a phase> (<source>, <YYYY-MM-DD>)
```

- **Phase column:** an outcome noun phrase.
- **Statuses:**
  - `planned`: an outline or an unapproved plan
  - `approved`: some or all tasks approved; progress is the checkboxes
  - `built`: all tasks done, review passed, and Auto acceptance green
  - `done`: manual checks passed, or the user waived them
  - `dropped`: abandoned; give the reason in the Phase cell
- **Outlines** stay at 1–3 lines until a phase is next in its track.
- **Large apps:** group rows under `### <Milestone>` headings inside `## Phases`, with one table per milestone.

## docs/ARCHITECTURE.md

This file describes the code as built. Planned design lives in plans, or in TARGET-ARCHITECTURE, until it ships.

```markdown
# Architecture

## Overview
<3–6 lines: the main parts and how they fit.>
Data flow: <entry point> → <module> → <module> → <storage or external service>

## Modules
| Path | Owns |
| --- | --- |
| `src/routes/` | HTTP handlers: parse input, call services, map errors to responses |
| `src/db/queries/` | All database reads and writes |

## Invariants
- I01 <statement that must always hold> — enforced by `<test or module path>`
- I02 <statement> — enforced by `<path>`

## Boundaries
- <external service or storage>: <what we send/receive, who handles its errors, trust level>

## Topic docs
- [DATABASE.md](DATABASE.md) — <one line>
```

Before the first phase ships, add `Status: planned` under the title, and remove it when P01 closes.

## docs/TARGET-ARCHITECTURE.md (optional)

Use this only when a milestone needs a design that spans several phases. When a phase ships, its part moves into ARCHITECTURE and leaves this file.

```markdown
# Target architecture

Status: proposed for P17–P21. Reasons: D014–D016.

## Components
<The parts after the milestone, how they talk, and which phase builds each.>

## Contracts between components
<Shapes other phases depend on, at the level of messages and APIs, not code.>
```

## docs/DECISIONS.md

Record only choices a future planner might undo without knowing why. Each entry is 8 lines or fewer.

```markdown
# Decisions

## D001 <Choice as a short phrase> — accepted (P01)
Context: <the problem or constraint, one line>
Decision: <the choice and its main reason>
Rejected: <viable alternative> — <why not>
Consequence: <tradeoff or limit future work must respect>
```

- **Statuses:**
  - `proposed`: written into a plan and awaiting approval
  - `accepted`
  - `superseded by D0NN`: keep the original text
- Never rewrite an accepted entry. Supersede it instead.

## docs/plans/PNN-slug.md (feature)

The filename is the phase ID plus a kebab-case slug, and the heading repeats the same ID. `Format: 3` marks this version. Aim for about 200 lines or fewer.

```markdown
# P02 Email alerts

Format: 3
Kind: feature
Approved: pending
Depends on: P01
Touches: `src/mail/`, `src/db/schema/` (migration)

## Goal
<User-visible outcome in 1–3 sentences.>

In: <included work>
Out: <excluded work that someone might reasonably expect>

## Requirements
C1. <Observable behavior, stated so a test can check it.>
C2. <Failure case: what happens on timeout / duplicate / invalid input, and the state left behind.>

## Design
<Only the seams this phase changes, written as code.>

    POST /alerts/rules → 201 { id: string } | 400 { error: "invalid_rule" }
    alert_rule(id uuid pk, user_id uuid not null, pattern text not null, created_at timestamptz)

Owners: <new or extended owner modules, one line each>

### Choices
| Question | Decision | Why |
| --- | --- | --- |
| <consequential design question> | <decision> | <reason> |

## Context
Read: I03 (email content is untrusted), D004.
Reuse: `<existing symbol>` — `<path>` — <what for>

## Tasks
- [ ] P02-T01 Add alert rules
  Done when: C1 holds for create and list, with the migration applied and tests for invalid rules.
- [ ] P02-T02 Classify new messages
  Done when: C2 and C3 hold; classification runs on every new message, with failures tested.
  Checkpoint: first use of the model client; review its error handling before alerts build on it.
- [ ] P02-T03 Send alerts
  Done when: a matching message sends one alert; duplicates send none.
  Check: `<command>`

## Acceptance
Auto:
- `<command>` → <expected result>
Manual:
- <step the user performs> → <expected result>

## Changes
- none
```

- **Required:** the header lines `Format`, `Kind`, `Approved`, and `Depends on`, and the sections Goal, Requirements, Tasks, and Acceptance.
- **Design** is required when the phase changes a public contract, a persisted format, or the architecture.
- **Touches**, **Context**, and **Changes** are optional; the Docs check warns when `Touches:` is missing.
- **Tasks:**
  - Each checklist item needs an indented `Done when:`.
  - `Check:`, `Checkpoint:`, and `Avoid:` are optional.
  - There are no separate task cards.
- **Unknowns:** prefix the task title with `Spike:` and order spikes first. A spike records its finding in the log and changes no product code unless its `Done when:` says so.
- **Run-only tasks** (a migration, a data job, a deploy) say in `Done when:` what to record in the log.
- **The `Approved:` line** takes three forms:
  - `Approved: pending`
  - `Approved: 2026-10-26 all`
  - `Approved: 2026-10-26 T01–T04; 2026-10-27 T05` (ranges and single tasks, separated by `;` or `,`)
- **`Changes`:** after approval, the planner edits the plan in place and adds one dated line per edit, e.g. `- 2026-10-27: C3 now rejects unknown fields; added P02-T05 (review 1).`

## docs/plans/PNN-slug.md (fix)

```markdown
# P09 Upload finalization fix

Format: 3
Kind: fix
Approved: pending
Depends on: none
Touches: `src/uploads/`

## Goal
<What works after the fix, in 1–2 sentences.>

## Bug
Repro:
1. <minimal step>
2. <minimal step>
Expected: <behavior>
Actual: <behavior and the error text, without secrets>
Cause: `<path>` `<symbol>` — <what goes wrong and the evidence>
<or> Cause: unknown — diagnose within `<area>`; collect <evidence>.

## Requirements
C1. <The repro now gives the expected behavior.>
C2. <Any related case that must keep working.>

## Tasks
- [ ] P09-T01 Await admission before closing the uploader
  Done when: a regression test reproduces the bug through <entry point>, fails before the fix, and passes after it; C2 still holds.

## Acceptance
Auto:
- `<command>` → pass
Manual:
- <repro steps from Bug> → <expected behavior>
```

## docs/logs/PNN-slug.md

The log has the same filename as its plan. It is append-only. The builder adds the Baseline, task, blocked, and Ready for review entries. The planner adds unblocked, cleared, Review, and Outcome entries. Each entry is 8 lines or fewer.

```markdown
# P02 log

## Baseline · 2026-10-26
Full check: `<command>` → pass
Pre-existing failures: none

## P02-T01 · done · 2026-10-26
Changed: `src/db/schema/alerts.ts`, `src/alerts/rules.ts`, `tests/alerts.test.ts`, `docs/ARCHITECTURE.md`
Check: `<command>` → pass
Choices: rules are validated in the existing schema module, not a new one
Notes: none

## P02-T02 · done · 2026-10-26
Changed: `src/mail/classify.ts`, `src/mail/classify.test.ts`
Check: `<command>` → pass
Choices: none
Notes: none

## P02-T02 · cleared · 2026-10-26
Notes: reviewed model-client error handling; no plan changes

## P02-T03 · blocked · 2026-10-27
Question: <what would have to change in the approved design, and why>
Options: A) <option> B) <option>. Recommend A because <reason>.

## P02-T03 · unblocked · 2026-10-27
Resolution: <what the planner changed; see the plan's Changes>

## Ready for review · 2026-10-27
Full check → pass. Auto acceptance → pass. Docs check → pass.

## Review 1 · 2026-10-27
- `src/mail/classify.ts` `classify` — retry reuses a stale request id — use the stored id → P02-T05
- No other findings.

## Outcome · 2026-10-28
Delivered: <one or two lines>
Manual checks: passed | pending: <which> | waived by the user: <which>
Follow-ups: <added to ROADMAP backlog, or none>
```

## docs/incidents/YYYY-MM-DD-slug.md (optional)

Use this only for a problem in a deployed environment. A local bug only needs a fix plan.

```markdown
# Incident 2026-10-16 Media delivery outage

Impact: <who and what was affected, and for how long>
Cause: <root cause and evidence>
Repair: <what was done, linking the fix phase>
Verification: <how recovery was confirmed>
Prevention: <phase or backlog item that stops a repeat>
```

## v2 plans

Plans without a `Format:` line are v2: a `Spec` section, `Builder context`, a checklist, and one `### PNN-TNN` card per task with `Files:`, `Do:`, and `Check:`. The Docs check still validates them, and builders follow them as building.md "v2 plans" describes. Write new plans in v3.
