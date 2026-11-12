# Foundations

The foundation records are what every plan builds on: AGENTS.md, ARCHITECTURE, specs, DECISIONS, and ROADMAP. Write them once, keep them current, and cite them instead of copying them. When the docs and the code disagree, the code wins; fix the docs in the same pass. [templates.md](templates.md) has every format.

## New app

1. **Interview the user:** who uses it and for what core job; must-haves and non-goals; which data must never be lost; where it runs; stack preferences; and the numbers: how many users, how much data and how fast it grows, latency for the main flows, and the budget.
2. **ROADMAP:** the goal, "Not doing", 3–5 `Constraints:` lines from those numbers, and every foreseeable phase as an outline row.
   - P01 is the thinnest end-to-end path: a real entry point reaching real storage or output, with Fast and Full checks that run.
   - P01 also proves that a clean clone installs and starts with the documented commands. Where the stack allows, the env reference is generated from the config owner.
3. **Stack:** choose each major component (runtime, framework, storage, queue, hosting, key services) by the rules below, and ask before committing to it.
4. **ARCHITECTURE:** before P01 ships, write only the Overview, the context diagram, and the Glossary. P01's plan holds the planned structure; its close adds Modules and Invariants as built.
5. **AGENTS.md:** commands (to be verified in P01), the owners P01 creates marked `(created by P01)`, hard rules, and the Docs check and Phase diff commands with the absolute path of this skill's `scripts/` folder. Patterns come from P01's code at its close.
6. **Plan P01** with [planning.md](planning.md).

## Choosing tools

- **Pick the simplest tool that meets the constraints with about 10× headroom.** Prefer what the team already runs, and boring over novel. Headroom beyond 10× is a cost you pay now for load you may never see.
- **Measure when the choice hinges on an unknown:** throughput, a provider's API, format support. Make it a `Spike:` task first in the phase, with a decision rule.
- **Record each major choice in DECISIONS** with `Rejected:` (with numbers where scale decided it) and `Revisit when:` (the measured threshold that would change it).
  - Seen, good: Postgres over a columnar store for analytics, because about 12k rows a day is far below where the columnar store pays for itself; a conformance suite run against three object stores before picking one.
  - Seen, bad: a framework, ORM, and auth library chosen with no recorded reason, so nobody can tell when they should be revisited.

## ARCHITECTURE

As built and concise: aim for about 200 lines, with area behavior in specs and runbooks in topic docs.

- **Overview** in 3–6 lines, plus a Mermaid context diagram once the app has 3 or more components or any external service.
- **Imports flow:** one line giving the allowed direction between modules. Enforce it with the stack's tool where one exists (an import-lint rule, a dependency test), and say which.
  - Seen: three module moves in one phase, and a later reorder, because the allowed direction was never written down.
- **Modules:** a table of packages or folders and what each owns.
- **Invariants** `I01…`: rules across modules, each "enforced by" a test or module. Once the app takes more than one lock, include the lock order.
  - Seen: a deadlock from two code paths taking the same two locks in opposite order.
- **Boundaries:** each external service or store, what crosses it, who handles its errors, and its trust level.
- **Glossary:** terms with a project-specific meaning, one line each. The code uses exactly these names.
  - Seen: "sales" meant both a price promotion and a purchase, which produced two `sales.service.ts` files and a route that worked only because of mount order.
- **Specs** and **Topic docs:** links.

## Specs

A spec holds the current behavior of one area: rules, flows, and pointers to contracts. It is what plans cite instead of each other.

- **One spec per area of behavior** (checkout, enrollment, media pipeline), named by domain, not by code folder.
- **Create one lazily:** when a plan would otherwise cite another plan's requirements, or when an area's rules span more than one phase. Write it from the code as built, using the existing tests as evidence. A small app may never need one.
- **Rules** `R1…` are numbered per spec, one or two lines each, describing observable behavior, citing a D or I where the reason matters.
  - Never renumber a rule. Delete a retired rule without a tombstone.
  - Never put R-IDs in code or tests.
- **Flow:** Mermaid, only when triggered: a `sequenceDiagram` or `flowchart` for more than 3 steps or a process boundary, and a `stateDiagram-v2` for 3 or more statuses.
- **Contracts:** point to the source-of-truth files (OpenAPI, schema, proto, test vectors). Never copy a shape.
- **Keep it to about 150 lines;** split a sub-area out past that.
- **Who edits:** the reviewer at close, folding in tagged C-items; the planner when creating a spec or correcting it against the code. Builders don't.

## AGENTS.md

- **Where things live** maps *concerns* to their one owner: config, logging, errors and user-facing messages, database access, HTTP client, validation, dates, money and number formatting, pagination, hashing and IDs, retries, shared types. Packages belong in the ARCHITECTURE module table instead.
  - Seen: an owner list that tried to name every package missed 23 of 52; the same app had seven copies of one hash helper.
  - Seen: three money formatters with different rounding, and seven separate maps from error code to message.
- **Patterns:** one exemplar file per kind of change the repo repeats (route, service, query, schema change, job, component, test, CLI command), one line each with what to copy. Pick the best existing file, not the most common one.
- **When you change:** co-change rules, "change X → also do Y". Prefer a check that fails when Y is skipped: a test, or a generator whose diff CI rejects. Once a check enforces a line, delete the line.
  - Seen, good: a table of co-changes backed by tests that fail when a step is missed.
- **Gotchas:** traps that cost a fix or a block, harvested at close.
  - Seen: one schema-library trap broke generated types in three separate phases, because nobody wrote it down.
- **Size:** keep it to 80 lines or fewer. When it grows past that, move detail into ARCHITECTURE or a spec rather than raising the limit.

## Generate, don't write

Reference material that code can produce (env var tables, API reference, CLI help, generated client types) is generated, checked in CI, and linked. The docs hold what code can't say: why, flows, rules, and tradeoffs.

When two components in different languages must agree on a format, keep one shared test-vector file that both test suites read, and point the spec's Contracts at it.

## Existing repos

### A working app with no records

Write AGENTS.md, ROADMAP, and an as-built ARCHITECTURE while planning its first phase. Add specs only as phases need them.

### A repo with old or ad-hoc planning docs

This covers clean-dev v1 docs (`docs/PLAN.md`, `docs/phases/`), root `phase*.md` files, a status-heavy AGENTS.md, or a decisions file used as a log. Adoption is a doc-only `Kind: fix` phase and needs the user's approval like any other. It changes no product code.

1. **Make the worktree safe.** If `git status` shows uncommitted changes, ask the user to commit or stash them first.
2. **Inventory:**
   - every planning or status doc;
   - the commands in the package manifest or Makefile;
   - the top-level source folders;
   - where each cross-cutting concern lives, and any duplicates;
   - the best existing example of each repeated kind of change.
3. **Write the adoption plan** `docs/plans/PNN-adopt-clean-dev.md` (Format 4, `Kind: fix`), where NN is one above the highest existing phase number. Its tasks:
   1. Archive the old plans unchanged with `git mv` into `docs/archive/`, and update the links. The Docs check ignores `docs/archive/`.
   2. Write ROADMAP. Each old phase becomes a row with its original number, its status mapped to `planned/approved/built/done/dropped`, and a link into the archive. Lettered sub-phases fold into their parent row. Unfinished items go into the backlog by area.
   3. Rewrite AGENTS.md to the template:
      - status → ROADMAP;
      - invariants → ARCHITECTURE as I-IDs;
      - product prose → a spec or topic doc;
      - generic style advice → deleted;
      - owners and Patterns from the inventory.
   4. Write or trim ARCHITECTURE to as-built facts.
   5. Leave DECISIONS history alone. Task logs and run results filed as decisions stay where they are, and new entries follow the template.
   6. If a phase is in progress, its remaining work becomes a new Format 4 plan.
4. **Don't sweep code comments** to remove old phase or decision IDs. Remove them only when a later task touches that file anyway.
5. **Close:**
   1. Run the Docs check until it reports no errors.
   2. Read the new AGENTS.md as the builder would: can a cheap model find every command, owner, and exemplar?
   3. Commit the tasks, then plan the next real phase.

### Upgrading from v2 or v3

No adoption phase is needed.

- **History stays.** Done and built plans, their `docs/logs/` files, and their approvals stay as they are. The Docs check only reads an older plan's ID, approval, and checkboxes, and ignores `docs/logs/`.
- **An in-flight phase:**
  1. Add `Format: 4` and a `## Log` section at the end. Leave the old log file as history.
  2. Rewrite any unchecked v2 cards as checklist items with `Done when:`.
  3. Keep the approval when the scope is unchanged.

  From then on builders commit with trailers.
- **The next unstarted phase** is written as Format 4 from its outline, rechecked against the code as it is now.
- **AGENTS.md:**
  - remove `Commits:` and the logs pointer;
  - add the Phase diff command and the "When you change" and Gotchas sections, harvesting Gotchas from the old logs' notes and review findings.
- **ARCHITECTURE:**
  - remove `Status: planned` and rows for things that were never built;
  - add the glossary, import direction, and lock order when you next touch it;
  - list specs as they appear.
- **DECISIONS:** set `proposed` entries of built phases to `accepted`.
- **Specs:** write none up front. Write the first one when a plan would cite an older plan's requirements.
- **Run the Docs check.** Its path errors and stale-status warnings are real drift; fix them in what you touch.
