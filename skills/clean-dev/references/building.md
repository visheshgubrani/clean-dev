# Building

You build an approved phase. The plan says what must hold: requirements, contracts at the seams, and when each task is done. You decide how: read the code, choose the implementation, write the tests, and keep the factual docs current. Stop only when the plan's decisions would have to change.

## Start of every session

1. **Read** AGENTS.md (commands, owners, Patterns, rules), the plan, and the **whole phase log**: earlier `Choices:`, blocks, reviews, and cleared checkpoints all bind you.
2. **Gates.** Stop and report if:
   - a task's latest entry is `blocked` with no later `unblocked`;
   - the last finished task has a `Checkpoint:` or is a `Spike:`, and no later `cleared` entry names it;
   - `git status` shows uncommitted changes you didn't make in the phase's area. Ask before touching them.
3. **Pick** the first unchecked task inside the plan's `Approved:` line. If there is none, report that and stop.
4. **Baseline:** if the log (`docs/logs/`, same filename as the plan) is missing or has no `Baseline` entry, create it, run the Full check, and record the result and any pre-existing failures.
5. **Read what the task needs:** the `I`/`D` IDs and sections the plan cites (grep for them), the Patterns exemplar for this kind of change, and the code you will change and its callers.

## Implement

- Meet the task's `Done when:` and the requirements it touches. Contracts in the plan's Design are exact: names, shapes, codes, error behavior.
- Everything the plan doesn't fix is yours: internal files and helpers, private signatures, callers, local refactors, test design, and deleting the code your change replaces.
- **Search before you write.** Grep the owners in AGENTS.md and the concept itself (`grep -rn "slug\|slugify"`). Extend what exists; never add a parallel version.
- Follow the Patterns exemplar and the lean-code rules in SKILL.md.
- Stay inside the phase: its approved tasks, its requirements, and the area in `Touches:`. Going outside `Touches:` is fine when the work needs it, unless another builder is active there; then record it and coordinate before continuing. A phase-wide scope never lets you start a task outside `Approved:`.
- Resolve routine discoveries yourself and record them under `Choices:`. For example: a library rejects an internal name, so pick one it accepts; a helper the plan didn't mention already exists, so use it; a test needs a new fake.
- Never add a dependency or service the plan doesn't approve. Never delete, skip, or weaken a test or check to get green.

## Escalate

Write a `blocked` entry (question, options, recommendation), leave the box unchecked, report, and stop when:
- meeting the task needs a change to an approved requirement, design decision, contract, or invariant: an exported name or shape, a route, status code, schema, env name, or behavior the plan fixes;
- it needs a dependency or service the plan doesn't approve;
- the requirements contradict each other;
- the task's tests or `Check:` still fail after 3 fix attempts;
- the next step needs the user (a manual check, credentials, a live account, payment, production data).

Changing behavior or contracts the way the plan specifies is the task, not a reason to stop.

## Docs you keep current

In the same task as the code:
- AGENTS.md: commands you change, and owners for modules you create, move, or delete.
- ARCHITECTURE.md: module-map rows for modules you create, move, or delete.
- Comments, READMEs, and env templates your change makes stale.

Never edit plan text other than checkboxes, ROADMAP, invariants, DECISIONS, or Patterns. Note needed changes in the log for the planner. Never write that review passed.

## Finish a task

1. Run its `Check:` (or the tests you wrote for it), then the Fast check.
2. Tick its box and append a log entry of at most 8 lines.
3. If AGENTS.md says `Commits: per-task`, stage the task's files plus the plan and log by explicit path (never `git add -A` or `.`), and commit as `P07-T03 <title>`.
4. Stop after a `Checkpoint:` or `Spike:` task. Otherwise continue only if the user asked for a range or the whole phase.

**Fix tasks:** when a plan marks the cause unknown, diagnose within the area it names and record the evidence (path, symbol, what goes wrong). If the cause lies outside the approved scope, block. Write the regression test first, see it fail, then fix, and log both results.

## After the last approved task

1. Run the Full check, the plan's Auto acceptance, and the Docs check.
2. Append `Ready for review` and commit the log as `P07 Ready for review`.
3. List the plan's Manual acceptance steps for the user. Don't mark them as passed. Report, and stop.

## Log entries

The Docs check parses these headings. The date is today's.

```markdown
## Baseline · 2026-10-26
Full check: `<command>` → pass. Pre-existing failures: none

## P07-T03 · done · 2026-10-26
Changed: `src/a.ts`, `src/a.test.ts`, `docs/ARCHITECTURE.md`
Check: `<command>` → pass
Choices: <routine decisions a reviewer should see, or none>
Notes: <surprises and follow-ups for the planner, or none>

## P07-T04 · blocked · 2026-10-26
Question: <what would have to change, and why>
Options: A) … B) … Recommend A because …

## Ready for review · 2026-10-26
Full check → pass. Auto acceptance → pass. Docs check → pass.
```

The planner writes `unblocked`, `cleared`, `Review N`, and `Outcome` entries.

## v2 plans

A plan without `Format: 3` has task cards. For it, change only the paths in the card's `Files:` and `Test:` lines, follow its `Do:` steps and the Spec word for word, and block when a needed file isn't listed. Everything else in this file applies.
