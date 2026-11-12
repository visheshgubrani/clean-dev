# Review and close

Run this when the plan's last Log entry is `Ready for review`, or when the user asks. Review the real diff once, route each finding, and close the phase in the same pass. At most one fix round follows.

**Review in a fresh context:** a session that didn't build the phase, given the plan and the diff, not the builder's reasoning. A review by the building session doesn't count. If the user waives review, append `### Review N · <date>` with `Waived by the user.` and close, so the skip is visible.

## 1. Gather

```bash
python3 <skill>/scripts/phase_diff.py P07     # the Phase diff command in AGENTS.md
```

It prints the phase's BASE commit and flags:
- unrelated commits inside the phase's range;
- files outside `Touches:`;
- task commits without a `Check:` trailer, or whose subject doesn't match a plan task;
- ticked tasks with no commit;
- new top-level names that are already defined elsewhere;
- debug statements and TODOs, and plan or decision IDs in code;
- touched files of 400 lines or more;
- the `Follow-up:` trailers.

Then read the diff itself (`git diff <BASE> <end>`, as printed) and the trail (`git log --format='%s%n%b' <BASE>..<end>`). Don't read only the tests.

## 2. Check

- **Coverage:** every C-item has a test or an acceptance step, and every risk checklist item that applies (SKILL.md) is exercised.
- **Correctness:** the code does what the requirements say, including the edge cases.
- **Seams:** contracts match the Design exactly.
- **Architecture:** owners are used, imports follow ARCHITECTURE's direction, edges stay thin, and invariants hold, including lock order.
- **Duplication:** each name the Phase diff flags is either intended (say why) or a finding. New shared code sits with its owner and follows the Patterns exemplar.
- **Complexity:** the lean-code rules hold. No interface with one implementation, no dead code left by the change, no formatting compressed to meet a size.
- **The builder's `Choices:`:** accept each one, or make it a finding.
- **Docs:** the builder updated commands, owners, module rows, generated references, and stale comments, and didn't edit planner-owned records.
- **Evidence:** the `Check:` trailers match the real commands. Rerun the Full check and the Auto acceptance where risk or thin evidence warrants it.

## 3. Route each finding

Append `### Review N · <date>` to the Log, one line per finding, ranked most severe first:

```
- `path` `symbol` — what is wrong — the fix → route
```

| Route | When | What you do |
| --- | --- | --- |
| `fixed` | Trivial and design-free: a dead export, a rename, a stale comment, a missing assert for an obvious case | Fix it yourself, run the Fast check, and commit as `P07 Review N` with a `Check:` trailer |
| `→ P07-T0N` | Anything else needed to make the approved requirements hold | Collect all of them into **one** new task, `P07-T0N Fix review findings`, whose `Done when:` points at this entry |
| `backlog` | Unrelated to this phase's requirements, or new scope | Add a line to the ROADMAP backlog |
| `user` | Fixing it would change approved scope, a contract, or a decision | Ask the user before routing it |

- The fix task needs no new approval, since it only makes approved requirements hold. If `Approved:` lists ranges, append `; <date> T0N`.
- Never keep a standing list of gaps. Every finding is fixed, sits in the fix task, or is a backlog line.
- With no findings, write `No findings.` and close.
- Otherwise, give the user the builder prompt `Use $clean-dev to build P07 T0N.`

## 4. Verify the fix task

When `Ready for review` follows the fix task, read only that task's commit (`git show <sha>`) against the findings routed to it.

- Every finding fixed → close.
- A miss → fix it inline, or add one more task in a `Review N+1` entry.
- Never re-review the whole phase. A new problem outside the findings goes to the backlog, unless it is a security or data-loss problem.

## 5. Close, in the same pass

1. **Specs:** fold each tagged C-item into its spec, as built.
   - `[slug Rn]` rewrites or deletes rule Rn.
   - `[slug new]` adds a rule numbered one above the spec's highest R.
   - A flow diagram the phase drew moves into the spec.
   - Untagged C-items stay in the plan.
2. **ARCHITECTURE:** module rows, new invariants (each "enforced by"), boundaries, import direction, and glossary terms. Describe what exists now, concisely.
3. **DECISIONS:** set this phase's entries `accepted (P07)`. Supersede an entry with a link; never rewrite it.
4. **AGENTS.md:**
   - verify the commands;
   - add new exemplars to Patterns;
   - add a Gotcha for each mistake that cost a fix or a block;
   - delete "When you change" lines that a check now enforces;
   - keep it to 80 lines or fewer.
5. **Backlog:** add every `Follow-up:` trailer and backlog-routed finding that isn't there yet, drop items that are done or obsolete, and keep it grouped by area.
6. **ROADMAP:** set `done` when the plan has no Manual steps or they passed (or the user waived them); otherwise set `built`. Refresh the outlines of the phases this one unblocks.
7. **Log:** append `### Outcome · <date>`:

   ```
   Delivered: <one or two lines>. Verified P07-T0N.
   Specs: checkout R6 changed, R9 added.
   Manual: none | passed | pending: <which> | waived by the user: <which>
   Backlog: +N
   ```

   Leave out `Backlog:` when nothing was added. When pending manual checks pass later, edit that `Manual:` line and set the phase to `done`.
8. Run the Docs check, and commit everything as `P07 Close`, with a one-line summary and a `Check:` trailer for the Docs check.

If the phase ran on its own branch, merge it without squashing (or keep the default squash message that lists every commit), so the task trailers survive. Then remove its worktree.

## Blocks, checkpoints, and spikes

- **Blocked:** read the entry. Answer it by editing the plan (requirements, design, or a new task), and append `### P07-T03 · cleared · <date>` with a one-line resolution.
  - If the answer changes approved scope, ask the user first and add a `Changed` entry.
  - If the builder could have decided it alone, say so in the resolution.
- **Checkpoint:** review that task's commit against the checks above. Append `cleared`, or route findings as in step 3. The user may clear a checkpoint themselves; record "cleared by the user".
- **Spike outside its decision rule:** update the plan, add a `Changed` entry (with approval if scope changed), then `cleared`.
