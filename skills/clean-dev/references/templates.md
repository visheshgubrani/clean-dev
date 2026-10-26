# Record templates

These formats are parsed by `scripts/check_docs.py`. Keep the headings, field names, and ID shapes exactly as shown.

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
One owner per concern. Reuse it; never create a second. The planner adds new owners here.
- Config/env: `<path>`
- Logging: `<path>`
- Errors: `<path>`
- Database queries: `<path>`
- API/HTTP client: `<path>`
- Dates/time: `<path>`
- Validation schemas: `<path>`
- Shared contracts/types: `<path>`

## Rules
- <Project hard rule, one line, e.g. "Never hand-edit an applied migration; add a new one.">
- Invariants: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#invariants).

## Workflow
Use the clean-dev skill. Status: [docs/ROADMAP.md](docs/ROADMAP.md). Plans: `docs/plans/`. Notes: `docs/logs/`. Decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
- Build one approved task at a time; change only the files its card lists; commit as `P07-T03 <task title>`.
- Never write status or progress in this file.
```

`Commits:` is `per-task` (the default) or `off` (when the user commits manually). Remove any concern from "Where things live" that the app doesn't have yet.

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
- **Large apps:** group rows under `### <Milestone>` headings inside `## Phases`, with one table per milestone.

## docs/ARCHITECTURE.md

This file describes the code as built. Planned design lives in plans until it ships.

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

The filename is the phase ID plus a kebab-case slug, and the heading repeats the same ID.

```markdown
# P02 Email alerts

Kind: feature
Approved: pending
Depends on: P01

## Goal
<User-visible outcome in 1–3 sentences.>

In: <included work>
Out: <excluded work that someone might reasonably expect>

## Spec
C1. <Behavior or rule, stated so a test can check it.>
C2. <Contract, written as code:>

    type TriageResult = { messageId: string; label: "important" | "ignore"; reason: string }
    function classify(message: CleanMessage): Promise<TriageResult>

C3. <Failure case: what happens on timeout / duplicate / invalid input.>

### Choices
| Question | Decision | Why |
| --- | --- | --- |
| <design question> | <decision> | <reason> |

## Builder context
Read first: `<path>`, `<path>`
Reuse:
- `createLogger` — `src/logger.ts` — structured logs
- `<symbol>` — `<path>` — <what for>
Rules that apply:
- <Full text of each relevant invariant or decision, with its ID, e.g. "I03 Email content is untrusted; never send raw HTML to the model.">
Test one file: `<command>`

## Tasks
- [ ] P02-T01 Add triage table
- [ ] P02-T02 Classify new messages

### P02-T01 Add triage table
Implements: C1
Files:
- `src/db/schema/triage.ts` (new)
- `src/db/schema/index.ts` (edit: export the new table)
- `drizzle/0007_triage.sql` (generated)
Do:
1. <Concrete step naming the symbol to add or change.>
2. Run `<generate command>` and keep the generated migration as is.
Test: `tests/db/triage.test.ts` (new)
- <input or action> → <expected result>
- <edge case> → <expected result>
Check: `<command that runs this task's tests>`
Avoid: <tempting wrong move, e.g. "Do not add an index; no query needs one yet.">

### P02-T02 Classify new messages
Implements: C2, C3
Files:
- `src/mail/classify.ts` (new)
Do:
1. <step>
Test: `src/mail/classify.test.ts` (new)
- <case> → <expected>
Check: `<command>`

## Acceptance
Auto:
- `<command>` → <expected result>
Manual:
- <step the user performs> → <expected result>

## Changes
- none
```

- **Cards:**
  - Every card needs `Files:`, `Do:`, and `Check:`.
  - `Test:` is required unless the task changes no behavior.
  - `Implements:` and `Avoid:` are optional.
- **Unknowns:** prefix the task title with `Spike:` and order spikes first. A spike records its finding in the log and changes no product code unless the card says so.
- **Run-only tasks:** a task that only runs something (a migration, a data job, a deploy) uses `Files: none (run-only)` and adds `Output: <what to record in the log>`.
- **Generated files:** mark them `(generated)` in `Files:`. They don't count toward the size limit.
- **The `Approved:` line** takes three forms:
  - `Approved: pending`
  - `Approved: 2026-10-26 all`
  - `Approved: 2026-10-26 T01–T04; 2026-10-27 T05` (ranges and single tasks, separated by `;` or `,`)
- **`Changes`:** after approval, the planner edits the plan in place and adds one dated line here per edit, e.g. `- 2026-10-27: C3 now rejects unknown fields; added P02-T05 (review 1).`

## docs/plans/PNN-slug.md (fix)

```markdown
# P09 Upload finalization fix

Kind: fix
Approved: pending
Depends on: none

## Goal
<What works after the fix, in 1–2 sentences.>

## Bug
Repro:
1. <minimal step>
2. <minimal step>
Expected: <behavior>
Actual: <behavior and the error text, without secrets>

## Cause
`<path>` `<symbol>` — <what goes wrong and the evidence that shows it>

## Builder context
Read first: `<path>`
Test one file: `<command>`

## Tasks
- [ ] P09-T01 Add failing regression test for early close
- [ ] P09-T02 Await admission before closing the uploader

### P09-T01 Add failing regression test for early close
Files:
- `<test path>` (edit)
Do:
1. Add a test that reproduces the bug through <entry point>.
Test: `<test path>`
- <repro input> → <expected behavior> (fails before P09-T02)
Check: `<command>` → the new test fails for the reason in Cause

### P09-T02 Await admission before closing the uploader
Files:
- `<path>` (edit)
Do:
1. <step>
Check: `<command>` → all tests pass, including the new one

## Acceptance
Auto:
- `<command>` → pass
Manual:
- <repro steps from Bug> → <expected behavior>

## Changes
- none
```

## docs/logs/PNN-slug.md

The log has the same filename as its plan. It is append-only: only the builder adds task entries, and only the planner adds Review, Outcome, and `unblocked` entries. Each entry is 8 lines or fewer.

```markdown
# P02 log

## Baseline · 2026-10-26
Full check: `<command>` → pass
Pre-existing failures: none

## P02-T01 · done · 2026-10-26
Changed: `src/db/schema/triage.ts`, `src/db/schema/index.ts`, `tests/db/triage.test.ts`
Check: `<command>` → pass
Notes: none

## P02-T02 · blocked · 2026-10-26
Question: <what the plan does not answer, or how it differs from the code>
Options: A) <option> B) <option>. Recommend A because <reason>.

## P02-T02 · unblocked · 2026-10-27
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
