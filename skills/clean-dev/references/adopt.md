# Adopt clean-dev in an existing repo

Use this when a repo has old or ad-hoc planning docs, such as clean-dev v1 docs (`docs/PLAN.md`, `docs/phases/`), root `phase*.md` files, or a status-heavy AGENTS.md. A working repo with no planning docs doesn't need this; planning.md "Existing app" covers it. Adoption is a doc-only `Kind: fix` phase and needs the user's approval like any other. It changes no product code.

## 0. Make the worktree safe

Run `git status`. If there are uncommitted changes, ask the user to commit or stash them first. Adoption moves files, and it must not sweep in-flight work into its commits.

## 1. Inventory

List:
- every planning or status doc (`AGENTS.md`, `CLAUDE.md`, `docs/**`, root `phase*.md`, `PLAN.md`, `TODO.md`);
- the commands in `package.json`, `pyproject.toml`, or the Makefile;
- the top-level source folders.

Read enough code to describe the modules as they are built. Note where each cross-cutting concern lives today, and any duplicates you find (see lean-code.md rule 1).

## 2. Write the adoption plan

Write `docs/plans/PNN-adopt-clean-dev.md`, where NN is one above the highest existing phase number. Use these tasks:

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
   - "Where things live" filled in from step 1.
4. **Write or trim ARCHITECTURE** to as-built facts. Move appended per-phase sections into the module map and invariants. Keep topic docs (database catalog, setup, runbooks) and link to them.
5. **Leave DECISIONS history alone.** Add `# Decisions` and new-format entries going forward. Don't rewrite old entries.
6. **Replan any active phase.**
   - If a phase is in progress, the remaining work becomes a new plan with task cards (planning.md).
   - Its log starts with a `Baseline` that summarises the archived evidence in at most 8 lines.

## 3. Archived-plan rows in ROADMAP

An archived plan has no cards, so the Docs check can't validate it. Mark its row with a link into `docs/archive/`; the linter accepts that for `done`, `built`, and `dropped`. If such a phase is still `approved` (in progress), step 2.6 replaces it with a new plan.

## 4. Code comments

Don't sweep the code to remove old phase or decision references. Remove them only when a later task touches that file anyway (lean-code.md rule 8). A sweep creates churn with no behavior change.

## 5. Close

1. Run the Docs check until it reports no errors.
2. Read the new AGENTS.md as if you were the builder: can a cheap model find every command and owner?
3. Commit the adoption as its task commits.
4. Then plan the next real phase.
