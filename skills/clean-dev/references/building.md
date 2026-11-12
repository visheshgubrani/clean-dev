# Building

You build an approved phase. The plan says what must hold: requirements, contracts at the seams, and when each task is done. You decide how: read the code, choose the implementation, write the tests, commit each task, and keep the factual docs current. Stop only when the plan's decisions would have to change.

## Start of every session

1. **Read** AGENTS.md (commands, owners, Patterns, "When you change", Gotchas, rules) and the plan, including its Log. Then read the phase's trail so far:

   ```bash
   git log --reverse --format='%s%n%b' --grep='^P07'
   ```

   Earlier `Choices:` trailers, Log blocks and their answers, and review findings all bind you.
2. **Gates.** Stop and report if:
   - a task's latest Log entry is `blocked`, with no later `cleared`;
   - the last finished task has a `Checkpoint:`, and no later `cleared` entry names it;
   - `git status` shows uncommitted changes you didn't make in the phase's area. Ask before touching them.
3. **Pick** the first unchecked task inside the plan's `Approved:` line. If there is none, report that and stop.
4. **Baseline:** if the phase has no task commits yet, run the Full check. If anything fails, append a `Baseline` entry naming the failures. A green baseline needs no entry.
5. **Read what the task needs:** the spec rules and the `D`/`I` entries the plan cites, the Patterns exemplar for this kind of change, and the code you will change and its callers.

## Implement

- Meet the task's `Done when:` and the requirements it cites. Contracts in the plan's Design are exact: names, shapes, codes, and error behavior.
- Everything the plan doesn't fix is yours: internal files and helpers, private signatures, callers, local refactors, test design, and deleting the code your change replaces.
- **Search before you write.** Grep the owners in AGENTS.md and the concept itself (`grep -rn "slug\|slugify"`). Extend what exists; never add a parallel version.
- Follow the Patterns exemplar, the lean-code rules in SKILL.md, and the "When you change" lines in AGENTS.md.
- Test each risk checklist item (SKILL.md) that the task touches. For a bug or a race, show that the test fails without the fix.
- Stay inside the phase: its approved tasks, its requirements, and the area in `Touches:`. Going outside `Touches:` is fine when the work needs it, unless another builder is active there; then say so in a `Follow-up:` trailer and coordinate before continuing.
- Resolve routine discoveries yourself (a library rejects an internal name; a helper the plan didn't mention already exists; a test needs a new fake) and record them in a `Choices:` trailer.
- **Spikes:** run the experiment and apply the decision rule in its `Done when:`. When the result falls inside the rule, record it in the commit and continue. When it falls outside, block.
- Never add a dependency or service the plan doesn't approve. Never delete, skip, or weaken a test or check to get green.

## Escalate

Append a `blocked` Log entry, leave the box unchecked, commit the plan as `P07 Blocked on T03`, report, and stop when:
- meeting the task needs a change to an approved requirement, contract, decision, or invariant: an exported name or shape, a route, a status code, a schema, an env name, or behavior the plan fixes;
- it needs a dependency or service the plan doesn't approve;
- the requirements contradict each other;
- the task's tests or `Check:` still fail after 3 fix attempts;
- the next step needs the user (a manual check, credentials, a live account, payment, production data).

Changing behavior or contracts the way the plan specifies is the task, not a reason to stop.

## Docs you keep current

In the same commit as the code:
- AGENTS.md: commands you change, and owners for concerns you create, move, or delete.
- ARCHITECTURE.md: module rows for modules you create, move, or delete.
- Comments, READMEs, env templates, and generated references your change makes stale.

Never edit the plan's text other than its checkboxes and your Log entries. Never edit specs, DECISIONS, invariants, Patterns, or ROADMAP. A spec rule that a tagged C-item (`[checkout R6]`, `[checkout new]`) changes is updated by the reviewer at close, so it needs no note. For any other needed change, add a `Follow-up:` trailer.

## Finish a task

1. Run its `Check:` (or the tests you wrote for it), then the Fast check.
2. Tick its box.
3. Stage the task's files and the plan by explicit path (never `git add -A` or `.`), and commit with the task line as the subject and trailers in the body:

   ```
   P07-T02 Add the refund endpoint

   Check: pnpm vitest run tests/refunds.test.ts → 14 passed
   Choices: amount parsed in the route schema; reused `withTx` from src/db
   Follow-up: `src/admin/format.ts` has a second cents formatter (outside Touches)
   ```

   - `Check:` is required: the command and its result as counts, never pasted output.
   - Leave out `Choices:` and `Follow-up:` when there's nothing to say. Repeat a key for more items.
   - An optional paragraph above the trailers explains a non-obvious why. Never list files, and never amend a reviewed commit.
   - A run-only task (a migration, a deploy) still commits its ticked box and its `Check:` result.
4. Stop after a `Checkpoint:` task. Otherwise continue only if the user asked for a range or the whole phase.

## After the last approved task

1. Run the Full check, the plan's Auto acceptance, the Docs check, and the Phase diff (`phase_diff.py P07`, from AGENTS.md).
2. Fix what the Phase diff shows in your own work: a new name that duplicates an owner's helper, debug statements, IDs in code, task commits without `Check:`, files that grew a second responsibility. Then walk the risk checklist against the diff.
3. Append `Ready for review` with the check results and anything the reviewer should know. Commit it, along with any pre-flight fixes, as `P07 Ready for review`.
4. List the plan's Manual acceptance steps for the user. Don't mark them as passed. Report, and stop.

## Fix tasks

- **A review fix task** covers every finding the reviewer routed to it. Fix each one, add a test where the finding is about behavior, and commit with the task line as usual. Then append `Ready for review` again and commit it.
- **A `Kind: fix` plan** with `Cause: unknown`: diagnose within the area it names, and put the evidence (path, symbol, what goes wrong) in the commit body. If the cause lies outside the approved scope, block. Write the regression test first and see it fail, then fix, and record both in `Check:` ("fails before the fix, 1 passed after").

## Log entries you write

Each is a `### <name> · <today>` heading and 8 lines or fewer, under the plan's `## Log`:

```markdown
### Baseline · 2026-11-12
Full check: `pnpm test` → 2 failing in `tests/legacy.test.ts` (fail before this phase)

### P07-T04 · blocked · 2026-11-13
Question: <what would have to change in the approved design, and why>
Options: A) … B) …. Recommend A because ….

### Ready for review · 2026-11-14
Full check → pass. Auto acceptance → pass. Docs check → pass. Phase diff → clean.
```

Everything else in the Log (`cleared`, `Changed`, `Review N`, `Outcome`) is the planner's or reviewer's.
