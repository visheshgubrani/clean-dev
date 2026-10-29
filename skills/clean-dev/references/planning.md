# Planning and review

This file is for the model that plans and reviews. A cheaper model builds by following [building.md](building.md): it reads the code, chooses the implementation, and writes the tests. Your plan settles what must hold (behavior, boundaries, and consequential choices) so the builder can't build the wrong thing. Leave the how to the builder. Spend your effort on requirements, seams, slicing, and review, not on code written out as prose.

## Approval

- **Before approval** you may inspect, reproduce, and write planning docs. You may not scaffold, install, change implementation or configuration, or deploy.
- **Asking for approval:** present the plan and the choices that need the user's input, then ask for explicit approval of a named phase or task range.
  - Write every plan with `Approved: pending` and its ROADMAP row as `planned`. When the user approves, record `Approved: <date> all` or ranges (`T01–T04`), and set the row to `approved`.
  - A request to "build X" does not approve a plan written afterwards. The user may approve several phases at once.
- **Scope changes** (a new task, or a change to approved requirements, design decisions, contracts, or invariants) need approval before any builder runs them. Edit the plan and add a `Changes` line. Implementation choices inside the approved scope need no approval.
- **After writing or changing a plan,** give the user the exact builder prompt, e.g. `Use $clean-dev to build P07 T01–T04.`

## Foundations

The foundation records are written once and kept current: AGENTS.md (commands, owners, Patterns, rules), ARCHITECTURE, DECISIONS, and ROADMAP. They are the reusable part of the work. Plans cite them and never restate them. When the docs disagree with the code, the code wins; fix the docs in the same planning pass.

**New app:**
1. Interview the user: users and the core job; must-haves and non-goals; stack preferences; where it runs; which data must never be lost. Propose the smallest stack that fits, and ask before committing to it.
2. Write ROADMAP: the goal, "Not doing", and every foreseeable phase as an outline row (see "Planning horizon"). P01 is the thinnest end-to-end path: a real entry point reaching real storage or output, with Fast and Full checks that run.
3. Write AGENTS.md: commands (to be verified in P01), the owners P01 creates, hard rules, and the resolved Docs check path (the absolute path of this skill's `scripts/check_docs.py`). Patterns come from P01's code and are added when P01 closes.
4. Write ARCHITECTURE with `Status: planned`, then plan P01.

**Working app without records:** write AGENTS.md, ROADMAP, and an as-built ARCHITECTURE while planning its first phase. Repos with older planning docs, or with v2 plans, use [adopt.md](adopt.md).

**Patterns.** List one exemplar per kind of change the repo repeats: route, service, query, schema change, background job, UI component, test, CLI command. Use one line each: the path and what to copy from it. Pick the best existing file, not the most common one. When no good exemplar exists, the phase that creates one adds it at close.

**New owners.** When a plan creates an owner module, add it to AGENTS.md "Where things live" while planning, with `(created by P07)`. Remove the note when the phase closes. Never add owners for phases that aren't approved.

## Planning horizon

- **ROADMAP outlines every foreseeable phase.** Give each 1–3 lines: the outcome, dependencies, and major risks.
- **Detail only the next phase in each independent track.** Never write a plan against code that an unbuilt phase will create. It goes stale and must be rechecked anyway.
  - Seen: ten phases planned in full ahead of the build, each written against code that didn't exist yet, each needing its readiness check rerun later.
- **Design that spans phases goes into DECISIONS** (or TARGET-ARCHITECTURE for a milestone), once. Phase plans cite it.
- **One phase is one user-visible outcome you could demo or verify.** If the user would want to approve part of it on its own, it is two phases.
- **Order by risk:** unknowns and external integrations early, behind spikes; the data model before the features that depend on it; vertical slices before polish.
- **The backlog takes ideas, requests, and non-urgent bugs** as one-line bullets. A finished phase is never reopened; later work on the same area is a new phase.

## Writing a plan

Use the v3 template in [templates.md](templates.md). [plan-example.md](plan-example.md) shows the intended depth. Aim for about 200 lines or fewer; a longer plan usually means implementation has crept in.

### What the plan states exactly

Only what the phase changes among:
- public APIs, routes, and CLI arguments: names, request and response shapes, status and error codes;
- persisted formats: schema, migration strategy, file and event formats;
- compatibility: which old data, clients, or messages must keep working;
- env and config names;
- security and trust behavior;
- failure semantics a caller observes: retries, idempotency, timeouts, and the state left behind.

State an internal API only for an architectural reason, for example when two tasks or two modules depend on the same internal seam.

### What it never contains

- new private helper designs, function bodies, or internal signatures that no seam requires;
- log text, or internal error text that isn't part of a contract;
- mock, fixture, and test-setup instructions;
- step-by-step edits ("delete the guard and its comment");
- pasted invariant or decision text. Cite `I05` or `D015` with a one-line gist; the builder reads the source.

The test: if two good engineers would do it differently and both would pass review, leave it out. Existing internal symbols are fine as `Reuse:` pointers.

- Seen: a 640-line plan whose spec held full schemas, exact log lines, private helper names, and mock setups, then restated them in every task. The builder reread all of it for each of eight tasks.
- Seen: a plan dictated internal task names that the queue library's parser rejected. The builder had to block on a choice it should have made itself.

### Requirements

- **Number each rule as a C-item a test or acceptance step can check.** Describe observable behavior, not code structure.
- **Walk the failure-mode checklist and state each item that applies:**
  - invalid, empty, oversized, or unknown-field input (reject or ignore?);
  - external service errors and timeouts (retry? how many? surfaced how?);
  - idempotency and retries (what makes a repeat safe?);
  - concurrency, double submit, and lost responses (the state after each);
  - time: which zone, day boundaries, clock source, DST;
  - existing data: additive migrations, backfill, old rows, rollback;
  - untrusted content (user input, email, web pages, model output), and what gets logged;
  - secrets and key material, including where they can leak indirectly: error messages, exceptions, and captured command output;
  - LLM behavior: a fixed eval-case file with objective pass criteria. Every prompt change reruns it, and keyword scores alone don't count.

### Design

Required when the phase changes a public contract, a persisted format, or the architecture. Otherwise it is optional.
- **Contracts at the seams, written as code:** types, signatures, schema columns, request and response shapes.
- **A Choices table for consequential choices only:** those that change behavior, a seam, cost, or risk. Routine choices belong to the builder and go in its log.
- **Owner placement:** which module owns each new concern. Any step up the complexity ladder in [lean-code.md](lean-code.md) gets a Choices row.

### Context (optional)

- **Read:** IDs and section links the builder needs beyond AGENTS.md.
- **Reuse:** existing symbols the builder might not find, with their paths. Confirm each one with `grep`.

Keep it short; AGENTS.md owners and Patterns already cover the usual ground.

### Tasks

- **One checklist.** Each task has a verb title and an indented `Done when:` that names observable results (requirements met, tests, behavior). Optional fields:
  - `Check:` a command;
  - `Checkpoint:` the reason to pause for review;
  - `Avoid:` a tempting wrong move.
- **Size by cohesion and risk, not file counts.** A task is one coherent commit that leaves the repo green.
- **Order:** contracts and data, pure logic, I/O adapters, wiring and UI, then deletion of the replaced path.
- **Unknowns become `Spike:` tasks** that run first. The builder logs the finding; you update the plan and append `cleared`.
- **Add `Checkpoint:` to the task that sets a seam or pattern later tasks build on.**
- **`Touches:`** (header) names the area the phase expects to change: packages, modules, and shared files such as the lockfile, schema, or root config. Phases build in parallel, each in its own worktree, only when their areas don't overlap. A shared lockfile, schema, migrations, root config, or runtime contract counts as overlap.

### Acceptance

- **Auto:** commands and their expected results. Run each one once yourself to confirm it works here.
- **Manual:** only steps the user can actually perform, as action → expected. Say plainly when a step needs credentials, devices, or a deploy. The phase reaches `built` without the manual steps and `done` with them.

## Definition of Ready

Before asking for approval, confirm:

- [ ] Every requirement is testable, and the failure cases that apply are stated.
- [ ] Every seam the phase changes is specified exactly; nothing private is designed.
- [ ] Every cited ID exists, and every `Reuse:` symbol was found with `grep`.
- [ ] `Touches:` is set, every task has `Done when:`, and spikes come first.
- [ ] The plan is near 200 lines or fewer.

Then run the Docs check and fix every error.

## Blocked tasks, checkpoints, and spikes

- **Blocked:** read the entry. Answer it by editing the plan (Requirements, Design, or a new task), add a `Changes` line, and append `## P07-T03 · unblocked · <date>` with a one-line resolution. If the answer changes approved scope, ask the user first. If the builder could have decided it alone, say so in the resolution.
- **Checkpoint or spike:** review that task's diff and log against the Review gate. After a spike, update the plan first. Then append `## P07-T02 · cleared · <date>` with one line on what you checked, or add fix tasks (with approval if they fall outside the approved scope). The builder resumes only after `cleared`.

## Review gate

Run this when the builder writes `Ready for review`, or when the user asks.

```bash
BASE=$(git log --grep='^P07-T' --format=%H | tail -1)~1   # commit before the phase's first task
git log --oneline "$BASE"..HEAD                          # one commit per task, subjects match the plan
git diff --stat "$BASE"..HEAD                            # files vs the plan's Touches:
git diff "$BASE"..HEAD -U0 | grep -E '^\+.*\b(function|def|class|const [A-Za-z_]+ = (async )?\()' # new definitions: grep each name repo-wide for duplicates
git diff "$BASE"..HEAD | grep -nE '^\+.*(console\.log|print\(|debugger|\.only\(|TODO|FIXME)'
git grep -nE '\bP[0-9]{2,3}(-T[0-9]{2})?\b|\b[DI][0-9]{2,3}\b|[Pp]hase [0-9]|[Ii]ncrement [0-9]' -- . ':!docs' ':!*.md'
git diff --name-only "$BASE"..HEAD | xargs wc -l 2>/dev/null | sort -n | tail -5   # large touched files: a second responsibility?
```

Read the diff itself, not only the tests. Check:

- **Coverage:** every C-item has a test or an acceptance step, and every failure case is exercised.
- **Correctness:** the code does what the requirements say, including the edge cases.
- **Seams:** contracts match the Design exactly.
- **Architecture:** owners are used, imports flow one way, edges stay thin, and invariants hold.
- **Duplication:** no second helper for a concern an owner already covers; new shared code sits with its owner; new code follows the Patterns exemplar.
- **Complexity:** the lean-code rules hold. No interface with one implementation, no dead code left by the change, no formatting compressed to meet a size.
- **The builder's `Choices:`:** accept each one, or turn it into a fix task.
- **Docs:** the builder updated commands, owners, module rows, and stale comments, and didn't edit planner-owned records.
- **Evidence:** the logged checks match the real commands. Rerun the Full check and the Auto acceptance where risk or missing evidence warrants it.

Record the review in the log as `## Review N · <date>`, with one line per finding:

```
`path` `symbol` — wrong behavior — required fix → P07-T09
```

Then:
1. Append each fix as a new task.
2. Add a `Changes` line and get approval for the fix tasks. If the user approved the whole phase, fixes inside its scope are covered.
3. Repeat until clean.
4. Set ROADMAP to `built`.

When the same shape shows up in several places, add it to Patterns.

## Closing a phase

1. ROADMAP: set `built`, or `done` if the manual checks passed or the user waived them.
2. ARCHITECTURE: add invariants (I-IDs with "enforced by") and boundaries; check the builder's module rows. Describe what exists now, concisely.
3. DECISIONS: mark this phase's entries `accepted`. Supersede an entry with a link; never rewrite it.
4. AGENTS.md: verify the commands, remove `(created by …)` notes, add new exemplars to Patterns, and keep it at 80 lines or fewer.
5. Log: append `## Outcome · <date>`, covering what was delivered, the manual checks, and follow-ups added to the backlog.
6. Refresh the outline rows. Detail the next plan only if it is next in its track. Run the Docs check.

## Bugs

- **A bug inside the scope of an active phase:** add a fix task to that phase.
- **Otherwise, write a `Kind: fix` plan:**
  - Give the Repro, Expected, and Actual.
  - Cause: when you know it, give the path, symbol, and evidence. When you don't, write `unknown` and bound the diagnosis: the area to search and the evidence to collect. The builder diagnoses inside that bound and blocks if the cause lies outside it.
  - Where practical, one task adds the regression test and the fix; the log shows the test failing before the fix. Split them only when the fix is large or risky.
  - If you can't reproduce the bug, ask for the missing evidence. Never guess a fix.
- **Small direct changes** follow SKILL.md "Direct changes".
- **A problem in a deployed environment** also gets `docs/incidents/YYYY-MM-DD-slug.md`.

## Decisions

Choices live at three levels:
- **Routine implementation choices:** the builder's log, on the `Choices:` line.
- **Consequential choices for one phase:** the plan's Choices table.
- **Lasting choices a future planner could undo without knowing why:** DECISIONS, 8 lines or fewer. Typical cases are architecture or module boundaries, dependencies and services, data contracts and schema shape, security or privacy posture, and deliberate tradeoffs.
