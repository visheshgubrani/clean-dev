# Planning

This file is for the model that plans. A cheaper model builds by following [building.md](building.md), and a fresh context reviews by following [review.md](review.md). Your plan settles what must hold (behavior, seams, and consequential choices) so the builder can't build the wrong thing. Leave the how to the builder.

## Approval

- **Before approval** you may inspect, reproduce, and write planning records: the plan, specs, DECISIONS, and ROADMAP. You may not scaffold, install, change implementation or configuration, or deploy.
- **Asking for approval:** write the plan with `Approved: pending` and its ROADMAP row as `planned`. Present the plan and the choices that need the user, then ask for explicit approval of the phase or a task range.
  - When the user approves, record `Approved: <date> all` or ranges (`T01–T04`), and set the row to `approved`.
  - A request to "build X" does not approve a plan written afterwards. The user may approve several phases at once.
- **Commit** the planning records as `P07 Plan`, then give the user the exact builder prompt, e.g. `Use $clean-dev to build P07.`
- **Scope changes after approval** need approval before any builder runs them: a new task (other than the review fix task), or a change to approved requirements, contracts, decisions, or invariants. Edit the plan and append a `Changed` Log entry.

## Planning horizon

- **ROADMAP outlines every foreseeable phase** in 1–3 lines: the outcome, dependencies, and major risks. Delete the outline once the phase has a plan.
- **Detail only the next phase in each independent track.** Never write a plan against code that an unbuilt phase will create; it goes stale and must be rechecked anyway.
- **One phase is one user-visible outcome you could demo or verify:** 8 tasks or fewer, and about 200 lines above the Log. If the user would want to approve part of it on its own, or it's bigger than that, it is two phases.
  - Seen: a 14-task payments phase with a 449-line plan; its Requirements held column types, the order of error checks, and UI wording.
- **Order by risk:** unknowns and external integrations early, behind spikes; the data model before the features that depend on it; vertical slices before polish.
- **Design that spans phases** goes into a spec or DECISIONS, once. Phase plans cite it.
- **The backlog** takes ideas, requests, and non-urgent bugs as one-line bullets under an area. A finished phase is never reopened; later work on the same area is a new phase.

## Read before you write

Read the specs the phase touches, the D and I entries around it, and the code. If the phase changes an area whose behavior so far lives only in older plans, first write that area's spec from the code ([foundations.md](foundations.md) "Specs"). Never cite another plan's C-items.

- Seen: understanding checkout meant reading four plans (1,116 lines), because each one cited the last one's requirements.

## Requirements

- **Number each requirement as a C-item a test or acceptance step can check.** Describe observable behavior, not code structure.
- **Tag C-items that change an area's lasting behavior:** `[checkout R6]` replaces or removes rule R6, and `[checkout new]` adds a rule. An untagged C-item is local to the phase (a migration, a one-off). At close, the reviewer folds tagged items into the spec.
- **Cite rules that must keep holding** instead of restating them: "checkout R1–R5 keep holding."
- **Walk the risk checklist** in SKILL.md and state each item that applies.
- **Give performance targets as numbers** from ROADMAP `Constraints:`, with how Auto acceptance measures them (for example, p95 over 200 requests on seeded data).

## Design

Required when the phase changes a public contract, a persisted format, or the architecture. Otherwise it is optional.

- **State exactly only what the phase changes among:**
  - public APIs, routes, and CLI arguments: names, request and response shapes, status and error codes;
  - persisted formats: schema, migration strategy, and file and event formats;
  - compatibility: which old data, clients, or messages must keep working;
  - env and config names;
  - security and trust behavior;
  - failure semantics a caller observes: retries, idempotency, timeouts, and the state left behind.
- **Write contracts as a delta, as code.** When a source-of-truth file owns the shape (OpenAPI, schema, proto, test vectors), name the change in one line instead of pasting the shape. State an internal API only when two tasks or two modules depend on it.
- **Draw a diagram** (Mermaid) when a new flow has more than 3 steps or crosses a process boundary, or when an entity gets 3 or more states. It moves into the spec at close.
- **Owners:** which module owns each new concern, and which existing owner the phase reuses. Confirm each with `grep`.
- **Choices table:** `Question | Decision | Rejected | Why`.
  - Add a row only for a choice with a viable rejected alternative that changes behavior, a seam, cost, or risk. A question with no real alternative is a requirement or the builder's call.
  - A new dependency needs a row, and "write it ourselves in about 30 lines" is one of the alternatives.
  - A choice a future planner might undo without knowing why also gets a DECISIONS entry, `proposed (P07)`, which the row cites.

### What a plan never contains

- new private helper designs, function bodies, or internal signatures that no seam requires;
- log text, or internal error text that isn't part of a contract;
- mock, fixture, and test-setup instructions;
- step-by-step edits ("delete the guard and its comment");
- pasted spec rules, decisions, or invariants. Cite `checkout R6`, `D015`, or `I05` with a one-line gist instead;
- column-by-column detail that the migration itself will hold;
- `file:line` references.

The test: if two good engineers would do it differently and both would pass review, leave it out.

- Seen: a 640-line plan whose spec held full schemas, exact log lines, private helper names, and mock setups, then restated them in every task.
- Seen: a plan dictated internal task names that the queue library's parser rejected, so the builder had to block on a choice it should have made itself.

## Tasks

- **One checklist.** Each task has a verb title and an indented `Done when:` that cites the C-IDs it satisfies and names the failure cases it tests. It never restates them. Optional fields:
  - `Check:` a command;
  - `Avoid:` a tempting wrong move;
  - `Checkpoint:` the reason to pause for review. Use at most one per phase, on the task that sets a seam later tasks copy.
- **Size by cohesion and risk, not file counts.** A task is one coherent commit that leaves the repo green.
- **Order:** contracts and data, pure logic, I/O adapters, wiring and UI, then deletion of the replaced path.
- **Unknowns become `Spike:` tasks** that run first. Their `Done when:` states the decision rule ("p95 < 200 ms → keep SQLite; otherwise block"), so the build continues when the result falls inside it.
- **A phase with new screens** may start with a static mock as its checkpoint task, so the user signs off on the flow before it's wired.
- **Never carry work across phases.** There is no T00. Pending manual acceptance keeps a phase at `built`; it doesn't move into the next one.
- **`Touches:`** (a required header line) names the area the phase expects to change: packages, modules, and shared files such as the lockfile, schema, or root config. Phases build in parallel, each in its own worktree, only when their areas don't overlap. A shared lockfile, schema, migrations, root config, runtime contract, or spec counts as overlap.

## Acceptance

- **Auto:** commands and their expected results. Run each one once yourself to confirm it works here.
- **Manual:** only steps the user can actually perform, as action → expected, walking the spec's flow. Say plainly when a step needs credentials, devices, or a deploy. The phase reaches `built` without the manual steps and `done` with them.

## Definition of Ready

Before asking for approval, confirm:

- [ ] Every requirement is testable, and the risk items that apply are stated.
- [ ] Every seam the phase changes is specified exactly, and nothing private is designed.
- [ ] Every cited spec rule, D, and I exists; no other plan's C-items are cited; every owner and `Reuse` symbol was found with `grep`.
- [ ] `Touches:` is set, every task has `Done when:`, spikes come first, and the plan has 8 tasks or fewer.
- [ ] The part above the Log is near 200 lines or fewer.

Then run the Docs check and fix every error.

## Bugs

- **A bug inside the scope of an active phase:** the reviewer routes it to that phase's fix task.
- **Otherwise, write a `Kind: fix` plan:**
  - Give the Repro, Expected, and Actual.
  - Cause: when you know it, give the path, symbol, and evidence. When you don't, write `unknown` and bound the diagnosis: the area to search and the evidence to collect. The builder diagnoses inside that bound and blocks if the cause lies outside it.
  - Where practical, one task adds the regression test and the fix, and its commit shows the test failing before the fix. Split them only when the fix is large or risky.
  - If you can't reproduce the bug, ask for the missing evidence. Never guess a fix.
- **Small direct changes** follow SKILL.md "Direct changes".
- **A problem in a deployed environment** also gets `docs/incidents/YYYY-MM-DD-slug.md`.
