# Adopt clean-dev in an existing repo

Use this when a repo has old or ad-hoc planning docs: clean-dev v1 docs (`docs/PLAN.md`, `docs/phases/`), root `phase*.md` files, or a status-heavy AGENTS.md. A working repo with no planning docs doesn't need this; planning.md "Foundations" covers it. For a repo already on clean-dev v2, skip to "Upgrading from v2".

Adoption is a doc-only `Kind: fix` phase and needs the user's approval like any other. It changes no product code.

## 0. Make the worktree safe

Run `git status`. If there are uncommitted changes, ask the user to commit or stash them first. Adoption moves files, and it must not sweep in-flight work into its commits.

## 1. Inventory

List:
- every planning or status doc (`AGENTS.md`, `CLAUDE.md`, `docs/**`, root `phase*.md`, `PLAN.md`, `TODO.md`);
- the commands in `package.json`, `pyproject.toml`, or the Makefile;
- the top-level source folders.

Read enough code to describe the modules as they are built. Note:
- where each cross-cutting concern lives today, and any duplicates you find (lean-code.md rule 1);
- the best existing example of each kind of change the repo repeats, for Patterns.

## 2. Write the adoption plan

Write `docs/plans/PNN-adopt-clean-dev.md` (v3, `Kind: fix`), where NN is one above the highest existing phase number. Use these tasks:

1. **Archive old plans unchanged.** Run `git mv` on old phase or plan files into `docs/archive/` (e.g. `docs/archive/phases/`, `docs/archive/phase4.md`), and update links to them. The Docs check ignores `docs/archive/`.
2. **Write ROADMAP.**
   - Each old phase becomes a row with its original number, its status mapped to `planned/approved/built/done/dropped`, and a plan link pointing into the archive.
   - Lettered sub-phases (10a–10e) fold into their parent row.
   - Unfinished and pending items go into the backlog.
3. **Rewrite AGENTS.md** to the template:
   - status and progress → ROADMAP;
   - domain invariants → ARCHITECTURE `## Invariants` as I-IDs, each with "enforced by";
   - product or prompt-behavior prose → a topic doc, or the code it describes;
   - generic style advice the model already knows → deleted;
   - "Where things live" and Patterns filled in from step 1.
4. **Write or trim ARCHITECTURE** to as-built facts. Move appended per-phase sections into the module map and invariants. Keep topic docs (database catalog, setup, runbooks) and link to them.
5. **Leave DECISIONS history alone.** Add `# Decisions` and new-format entries going forward. Don't rewrite old entries.
6. **Replan any active phase.** If a phase is in progress, the remaining work becomes a new v3 plan. Its log starts with a `Baseline` that summarises the archived evidence in at most 8 lines.

## 3. Archived-plan rows in ROADMAP

An archived plan has no tasks the Docs check can read. Mark its row with a link into `docs/archive/`; the linter accepts that for `done`, `built`, and `dropped`. If such a phase is still `approved` (in progress), step 2.6 replaces it with a new plan.

## 4. Code comments

Don't sweep the code to remove old phase or decision references. Remove them only when a later task touches that file anyway (lean-code.md rule 8). A sweep creates churn with no behavior change.

## 5. Close

1. Run the Docs check until it reports no errors.
2. Read the new AGENTS.md as if you were the builder: can a cheap model find every command, owner, and exemplar?
3. Commit the adoption as its task commits.
4. Then plan the next real phase.

## Upgrading from v2

A v2 repo needs no adoption phase. v2 and v3 plans live side by side, and the Docs check validates each by its own rules: plans with `Format: 3` are v3, and plans without it are v2.

- **Keep history.** Done and built v2 plans, their logs, and their approvals stay as they are.
- **An active v2 phase keeps v2 rules.** Builders follow its cards (building.md "v2 plans") unless the planner explicitly converts its remaining work.
  - To convert: add `Format: 3`, rewrite the unchecked tasks as checklist items with `Done when:`, keep the requirements and consequential Choices, drop the recipes, and add a `Changes` line.
  - Approval for the converted tasks carries over when their scope is unchanged.
- **Convert the next unstarted phase when it comes up,** not before.
  - Write a v3 plan from its outline, using the old plan as input. Keep its requirements, failure cases, seams, and consequential choices; drop private designs, log text, mock setups, and edit steps.
  - Recheck everything against the code as it is now.
- **Never bulk-rewrite future plans.** Plans detailed ahead of the build stay as they are until each is next. Then convert it, or drop it back to an outline if too much has changed.
- **Add Patterns to AGENTS.md** when you next plan, from the best existing files.
- **Only what you touch.** Don't clean up unrelated docs as part of the upgrade. Existing Docs check warnings on v2 plans can stay.
