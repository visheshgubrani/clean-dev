# Planning and review

This file is for the model that plans and reviews. The plans you write are executed by a cheaper model that follows `SKILL.md` "Build mode" literally. Every design decision has to be made in the plan, because the builder will not make it.

## Approval

- **Before approval** you may inspect, reproduce, and write planning docs. You may not scaffold, install, change implementation or configuration, or deploy.
- **Asking for approval:** present the plan and the choices that need the user's input, then ask for explicit approval of a named phase or task range.
  - Write every plan with `Approved: pending` and its ROADMAP row as `planned`. When the user approves, record the answer as `Approved: <date> all` or as ranges (`T01–T04`), and set the row to `approved`.
  - Only approval itself moves ROADMAP from `planned` to `approved`.
  - A request to "build X" does not approve a plan written afterwards.
  - The user may approve several phases at once.
- **Approved scope changes** (new behavior, a dependency, a data contract, or architecture): edit the plan, add a `Changes` line, and get approval for the new tasks before any builder runs them. Routine wording fixes need no new approval.
- **After writing or changing a plan,** give the user the exact builder prompt, e.g. `Use $clean-dev to build P07 T01–T04.`

## New app

1. Interview the user. Cover:
   - users and the core job;
   - must-haves and explicit non-goals;
   - stack preferences;
   - where it runs;
   - which data must never be lost.
   Propose the smallest stack that fits, and ask before committing to it.
2. Write `docs/ROADMAP.md`:
   - the goal and "Not doing";
   - every foreseeable phase as a `planned` outline row.
   P01 is the thinnest end-to-end path. It is a real entry point reaching real storage or output, with Fast and Full checks that run.
3. Write `AGENTS.md`:
   - the commands, marked as to be verified in P01;
   - "Where things live", listing only the owners P01 creates;
   - the hard rules;
   - the resolved Docs check path. This is the absolute path of this skill's `scripts/check_docs.py`.
4. Write `docs/ARCHITECTURE.md` with `Status: planned`.
5. Detail P01 as a plan, run the Definition of Ready, and ask for approval.

## Existing app (already on this layout)

1. Read AGENTS.md, ROADMAP, the relevant ARCHITECTURE sections, and the code the next phase touches.
2. If the docs disagree with the code, the code wins. Fix the docs in the same planning pass.
3. Pick the next phase with the user. Then detail it into a plan.

For a working app with no records, write AGENTS.md, ROADMAP, and an as-built ARCHITECTURE as part of planning its first phase. No adoption phase is needed. For a repo with older or ad-hoc planning docs, use [adopt.md](adopt.md) first.

When a plan creates a new owner module (for example `src/dates.ts`), add it to AGENTS.md "Where things live" while planning, with the note `(created by P07-T02)`. The builder then sees it, and you remove the note when the phase closes.

## Shaping the roadmap

- **One phase is one user-visible outcome you could demo or verify.** It has 3–8 tasks. If the user would want to approve part of it on its own, it is two phases.
- **Order phases by risk:**
  - unknowns and external integrations early, behind spikes;
  - the data model before features that depend on it;
  - vertical slices before polish.
- **The backlog takes ideas, requests, and non-urgent bugs** as one-line bullets. A bullet becomes a phase only when it is scheduled.
- **When a phase is `done`,** later work on the same area is a new phase. Never reopen it and never append to it.

## Writing a plan

Use the feature or fix template in [templates.md](templates.md).

### Spec

- **Write every rule as a numbered C-item a test can check.** Give contracts as code: types, function signatures, schema columns, request and response shapes, CLI arguments, and file formats.
- **Settle every design question in the Choices table.** If the builder would have to choose, you have not finished.
- **Walk the failure-mode checklist and specify each item that applies:**
  - invalid, empty, oversized, or unknown-field input (reject or ignore?);
  - external service errors and timeouts (retry? how many? surfaced how?);
  - idempotency and retries (what makes a repeat safe?);
  - concurrency, double submit, and lost responses (the state after each);
  - time: which zone, day boundaries, clock source, DST;
  - existing data: additive migrations, backfill, old rows, rollback;
  - untrusted content (user input, email, web pages, model output), secrets, and what gets logged;
  - LLM behavior: a fixed eval-case file with objective pass criteria. Every prompt change reruns it, and keyword scores alone don't count.
- **Apply [lean-code.md](lean-code.md).** Name the owning module for each new helper. Any step up the complexity ladder goes in Choices with a reason.

### Builder context

- **Read first:** the 2–5 files the builder must understand.
- **Reuse:** each helper with its symbol, path, and purpose. Confirm each one exists with `grep` before listing it.
- **Rules that apply:** paste the full text of the relevant invariants and decisions. The builder does not open ARCHITECTURE or DECISIONS.
- **Test one file:** the command pattern.

### Task cards

- **Order:**
  1. contracts and data;
  2. pure logic;
  3. I/O adapters;
  4. wiring and UI;
  5. deletion of the replaced path.

  Every task leaves the repo green.
- **Sizing:** each card is at most 5 source files and roughly 300 changed lines. Generated files are listed and marked `(generated)`, and don't count.
- **Do steps** name the symbols to add or change, and say what each one does. Write "Add `enqueueAlert(input: AlertInput): Promise<void>` to `src/alerts/outbox.ts` that inserts with `ON CONFLICT DO NOTHING`", not "Implement the outbox".
- **Test cases** are written as `input → expected`, and cover the failure cases from the Spec.
- **The Check command** runs exactly this task's tests and must be fast.
- **Unknowns become `Spike:` tasks** that run first. Their result goes in the log, and you update the plan before the remaining tasks run.
- **Oversized files:** if a touched file is already over the size budget, first add a task that splits it without changing behavior.
- **No line numbers.** Name files and symbols only, because line numbers go stale.

### Acceptance

- **Auto:** commands and their expected results. Run each one once yourself to confirm it works in this environment.
- **Manual:** only steps the user can actually perform, stated as action → expected. If a check needs credentials, devices, or a deploy, say so plainly. The phase reaches `built` without it and `done` with it.

## Definition of Ready

Before asking for approval, confirm each card meets all of these:

- [ ] Every path exists or is marked `(new)`. No line numbers.
- [ ] Every Reuse symbol was found with `grep`.
- [ ] Each `Check:` command runs here. A new test file failing to be found is fine.
- [ ] No design judgment is left: names, types, error behavior, and file placement are all stated.
- [ ] At most 5 source files and roughly 300 changed lines.
- [ ] Failure cases from the Spec have test cases.
- [ ] The repo stays green after the task.

Then run the Docs check and fix every error.

## Resolving a blocked task

Read the `blocked` log entry, then:

1. Answer the question by editing the plan: the Spec, the card, or a new card.
2. Add a `Changes` line.
3. Append a log entry `## P07-T03 · unblocked · <date>` with a one-line resolution.

If the answer changes approved scope, ask the user first.

## Review gate

Run this when the builder writes `Ready for review`, or when the user asks.

```bash
BASE=$(git log --grep='^P07-T' --format=%H | tail -1)~1   # commit before the phase's first task
git log --oneline "$BASE"..HEAD                          # one commit per task, subjects match cards
git diff --stat "$BASE"..HEAD                            # files vs each card's Files:
git diff "$BASE"..HEAD -U0 | grep -E '^\+.*\b(function|def|class|const [A-Za-z_]+ = (async )?\()' # new definitions: grep each name repo-wide for duplicates
git diff "$BASE"..HEAD | grep -nE '^\+.*(console\.log|print\(|debugger|\.only\(|TODO|FIXME)'
git grep -nE '\bP[0-9]{2,3}(-T[0-9]{2})?\b|\b[DI][0-9]{2,3}\b|[Pp]hase [0-9]|[Ii]ncrement [0-9]' -- . ':!docs' ':!*.md'
git ls-files | grep -vE '(lock|\.d\.ts$|/migrations?/|/drizzle/|/vendor/|/generated/)' | grep -E '\.(ts|tsx|js|jsx|py|go|rs|rb)$' | xargs wc -l | sort -n | tail -15
```

Check:

- Each task's diff matches its card: listed files only, and contracts as specified.
- Every C-item has a test, and every Spec failure case is exercised.
- No duplicate helpers. New shared code sits with the owner named in AGENTS.md.
- The lean-code rules hold. In particular: no new interface with one implementation, no shims, no dead code left by the change, and no validation of trusted internal data.
- Errors are handled at boundaries and never swallowed. Nothing logs secrets or untrusted payloads.
- The builder didn't edit ROADMAP, ARCHITECTURE, DECISIONS, AGENTS.md, or plan text beyond checkboxes.
- Rerun the Full check and the Auto acceptance yourself.

Record the review in the log as `## Review N · <date>`, with one line per finding:

```
`path` `symbol` — wrong behavior — required fix → P07-T09
```

Then:

1. Append each fix as a new card, continuing the task numbers.
2. Add a `Changes` line and get approval for the fix tasks. If the user approved the whole phase, review fixes inside its scope are covered.
3. Repeat until clean.
4. Set ROADMAP to `built`.

## Closing a phase

1. ROADMAP: set `built`, or `done` if the manual checks passed or the user waived them.
2. ARCHITECTURE: update the module map, the invariants (add I-IDs for new rules, with "enforced by"), and the boundaries. Describe what exists now, concisely. Don't copy the plan.
3. DECISIONS: mark this phase's entries `accepted`. Supersede with a link; never rewrite.
4. AGENTS.md: verify every command, add any new owners to "Where things live", and keep it at 80 lines or fewer. Move detail to topic docs.
5. Log: append `## Outcome · <date>`, covering what was delivered, the manual checks, and follow-ups added to the backlog.
6. Outline or refresh the next phase rows, and run the Docs check.

## Bugs

- **A bug inside the scope of an active phase:** add a fix task to that phase.
- **Otherwise:** write a `Kind: fix` plan.
  - Reproduce the bug first, with minimal steps or a failing test.
  - Find the cause in the code (path, symbol, evidence).
  - The first task adds a regression test that fails. The next task makes it pass.
  - If you can't reproduce it, ask for the missing evidence. Never guess a fix.
- **Small direct changes** follow SKILL.md "Direct changes".
- **A problem in a deployed environment** also gets `docs/incidents/YYYY-MM-DD-slug.md`.

## Decisions

Add a D-entry only if a future planner could undo the choice without knowing why. Typical cases:
- architecture or module boundaries;
- dependencies and services;
- data contracts and schema shape;
- security or privacy posture;
- deliberate tradeoffs.

Implementation details, parameter values, and process notes belong in the plan's Choices table. Keep each entry to 8 lines or fewer.
