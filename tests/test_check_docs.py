"""Tests for skills/clean-dev/scripts/check_docs.py.

Each case copies the good fixture, applies one mutation, and expects one message.
The good fixture: P01 is a frozen v2 plan (done), P02 a v4 plan (built, reviewed),
P03 a v4 plan in progress that cites the streaks spec, P04 an outline.
Run: python3 -m unittest discover -s tests
"""
import io
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills" / "clean-dev" / "scripts"))
import check_docs  # noqa: E402

GOOD = REPO / "tests" / "fixtures" / "good"
OLD = "docs/plans/P01-habit-logging.md"
BUILT = "docs/plans/P02-streak-calendar.md"
PLAN = "docs/plans/P03-daily-reminders.md"
ROADMAP = "docs/ROADMAP.md"
ARCH = "docs/ARCHITECTURE.md"
SPEC = "docs/specs/streaks.md"
DECISIONS = "docs/DECISIONS.md"


class CheckDocsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "project"
        shutil.copytree(GOOD, self.root)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def replace(self, rel, old, new):
        path = self.root / rel
        text = path.read_text()
        self.assertIn(old, text, f"fixture lacks {old!r}")
        path.write_text(text.replace(old, new, 1))

    def append(self, rel, text):
        with (self.root / rel).open("a") as f:
            f.write(text)

    def assertError(self, fragment):
        errors = check_docs.lint(self.root).errors
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")

    def assertWarning(self, fragment):
        warnings = check_docs.lint(self.root).warnings
        self.assertTrue(any(fragment in w for w in warnings), f"{fragment!r} not in {warnings}")

    def assertClean(self):
        report = check_docs.lint(self.root)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    # The fixture and the records around plans

    def test_good_fixture_is_clean(self):
        self.assertClean()
        self.assertEqual(check_docs.lint(self.root).summary,
                         ["P01 done 3/3 tasks", "P02 built 4/4 tasks", "P03 approved 1/3 tasks", "P04 planned"])

    def test_old_logs_are_ignored(self):
        (self.root / "docs/logs/P09-orphan.md").write_text("# P09 log\n\n## Whatever\n")
        self.assertClean()

    def test_missing_agents(self):
        (self.root / "AGENTS.md").unlink()
        self.assertError("AGENTS.md: missing")

    def test_agents_status_warning(self):
        self.append("AGENTS.md", "Status: P03 in progress\n")
        self.assertWarning("status belongs in docs/ROADMAP.md")

    def test_agents_test_count_warning(self):
        self.append("AGENTS.md", "- Suite: 412 tests green\n")
        self.assertWarning("test counts belong in commits")

    def test_architecture_status_warning(self):
        self.replace(ARCH, "# Architecture\n", "# Architecture\n\nStatus: planned\n")
        self.assertWarning("ARCHITECTURE.md: status belongs in docs/ROADMAP.md")

    def test_duplicate_invariant(self):
        self.append(ARCH, "- I01 Again — enforced by `tests/queries.test.ts`\n")
        self.assertError("duplicate invariant I01")

    def test_legacy_layout_warning(self):
        (self.root / "phase1.md").write_text("# Phase 1\n")
        self.assertWarning("legacy plan location")

    # ROADMAP

    def test_bad_status(self):
        self.replace(ROADMAP, "| approved |", "| in progress |")
        self.assertError("P03 has status 'in progress'")

    def test_lettered_phase_id(self):
        self.replace(ROADMAP, "| P04 |", "| P03a |")
        self.assertError("bad phase ID 'P03a'")

    def test_plan_not_in_roadmap(self):
        self.replace(ROADMAP, "| P03 | Daily reminders | approved | [plan](plans/P03-daily-reminders.md) |\n", "")
        self.assertError("P03 is not listed in docs/ROADMAP.md")

    def test_archived_plan_link_allowed_for_done(self):
        archive = self.root / "docs/archive/phases"
        archive.mkdir(parents=True)
        (archive / "04-summary.md").write_text("# old\n")
        self.replace(ROADMAP, "| P04 | Weekly summary | planned | — |", "| P04 | Weekly summary | done | [plan](archive/phases/04-summary.md) |")
        self.assertEqual(check_docs.lint(self.root).errors, [])

    # Plans: shared checks

    def test_heading_mismatch(self):
        self.replace(PLAN, "# P03 Daily reminders", "# P04 Daily reminders")
        self.assertError("first line must be '# P03 <title>'")

    def test_bad_approved_line(self):
        self.replace(PLAN, "Approved: 2026-10-30 T01–T02", "Approved: yes")
        self.assertError("cannot parse approval group 'yes'")

    def test_checked_outside_approved_range(self):
        self.replace(PLAN, "- [ ] P03-T03", "- [x] P03-T03")
        self.assertError("P03-T03 is checked but outside the Approved: range")

    def test_status_approved_but_plan_pending(self):
        self.replace(PLAN, "Approved: 2026-10-30 T01–T02", "Approved: pending")
        self.replace(PLAN, "- [x] P03-T01", "- [ ] P03-T01")
        self.assertError("P03 is approved but its plan says 'Approved: pending'")

    def test_built_with_open_tasks(self):
        self.replace(BUILT, "- [x] P02-T04", "- [ ] P02-T04")
        self.assertError("P02 is built but 1 task(s) are unchecked")

    def test_unknown_format(self):
        self.replace(PLAN, "Format: 4", "Format: 5")
        self.assertError("unknown 'Format: 5'")

    # Plans: frozen history

    def test_frozen_plans_skip_v4_rules(self):
        self.replace(OLD, "Check: `pnpm vitest run tests/routes.test.ts`\n", "")
        self.replace(OLD, "## Changes\n- none\n", "")
        self.assertClean()

    def test_frozen_v3_plan_is_tolerated(self):
        self.replace(BUILT, "Format: 4", "Format: 3")
        self.replace(BUILT, "  Done when: the contract and C3 hold in route tests.\n", "")
        self.assertClean()

    def test_frozen_plan_still_checks_approval(self):
        self.replace(OLD, "Approved: 2026-10-26 all", "Approved: 2026-10-26 T01")
        self.assertError("P01-T02 is checked but outside the Approved: range")

    def test_frozen_approved_with_every_task_checked(self):
        self.replace(ROADMAP, "| P01 | Habit logging | done |", "| P01 | Habit logging | approved |")
        self.assertWarning("P01 has every task checked but ROADMAP still says approved")

    # Plans: v4

    def test_v4_task_without_done_when(self):
        self.replace(PLAN, "  Done when: C2 and C3 hold, with tests at the day boundary.\n", "")
        self.assertError("P03-T02 needs an indented 'Done when:' line")

    def test_v4_duplicate_task(self):
        self.replace(PLAN, "\n## Acceptance", "- [ ] P03-T02 Show it again\n  Done when: x\n\n## Acceptance")
        self.assertError("duplicate task P03-T02")

    def test_v4_task_from_another_phase(self):
        self.replace(PLAN, "- [ ] P03-T03", "- [ ] P01-T03")
        self.assertError("task P01-T03 does not belong to P03")

    def test_v4_t00_task(self):
        self.replace(PLAN, "- [ ] P03-T03", "- [ ] P03-T00")
        self.assertError("never carry work into a phase as T00")

    def test_v4_too_many_tasks(self):
        extra = "".join(f"- [ ] P03-T{n:02d} Do more\n  Done when: x\n" for n in range(4, 11))
        self.replace(PLAN, "\n## Acceptance", f"{extra}\n## Acceptance")
        self.assertWarning("10 tasks; a phase is 8 tasks or fewer")

    def test_v4_missing_requirements(self):
        self.replace(PLAN, "## Requirements\n", "")
        self.assertError("P03-daily-reminders.md: missing section '## Requirements'")

    def test_v4_fix_needs_bug_section(self):
        self.replace(PLAN, "Kind: feature", "Kind: fix")
        self.assertError("missing section '## Bug'")

    def test_v4_needs_kind(self):
        self.replace(PLAN, "Kind: feature\n", "")
        self.assertError("needs 'Kind: feature' or 'Kind: fix'")

    def test_v4_needs_depends_on(self):
        self.replace(PLAN, "Depends on: P02\n", "")
        self.assertError("needs a 'Depends on:' line")

    def test_v4_needs_touches(self):
        self.replace(PLAN, "Touches: `src/reminders.ts` (new), `src/routes.ts`, `src/db/`\n", "")
        self.assertError("needs a 'Touches:' line")

    def test_v4_needs_log(self):
        path = self.root / PLAN
        text = path.read_text()
        path.write_text(text[: text.index("## Log")])
        self.assertError("missing section '## Log'")

    def test_v4_oversized_plan_warning(self):
        self.replace(PLAN, "\n## Tasks", "".join(f"- note {n}\n" for n in range(220)) + "\n## Tasks")
        self.assertWarning("lines above the Log; keep plans near 200")

    def test_v4_log_does_not_count_toward_size(self):
        self.append(PLAN, "".join(f"\n### Changed · 2026-11-0{n % 9 + 1}\nnote\n" for n in range(120)))
        self.assertClean()

    def test_v4_line_number_reference(self):
        self.replace(PLAN, "Touches: `src/reminders.ts` (new)", "Touches: `src/reminders.ts:42` (new)")
        self.assertWarning("line-number reference")

    def test_v4_banned_sub_unit_heading(self):
        self.replace(PLAN, "\n## Tasks", "\n### Unit 2 — more work\n\n## Tasks")
        self.assertWarning("use tasks (PNN-TNN)")

    # The Log

    def test_log_unknown_heading(self):
        self.append(PLAN, "\n### Notes · 2026-11-01\nsomething\n")
        self.assertWarning("unexpected log heading '### Notes")

    def test_log_entry_for_unknown_task(self):
        self.append(PLAN, "\n### P03-T09 · blocked · 2026-11-01\nQuestion: x\n")
        self.assertError("log entry for unknown task P03-T09")

    def test_log_entry_too_long(self):
        self.append(PLAN, "\n### Changed · 2026-11-01\n" + "".join(f"line {n}\n" for n in range(9)))
        self.assertWarning("log entry 'Changed · 2026-11-01' is over 8 lines")

    def test_log_must_be_last(self):
        self.append(PLAN, "\n## Notes\nx\n")
        self.assertError("'## Log' must be the last section")

    def test_duplicate_outcome(self):
        self.append(BUILT, "\n### Outcome · 2026-10-30\nManual: passed\n")
        self.assertWarning("more than one Outcome entry")

    def test_summary_shows_ready_and_blocked(self):
        self.append(PLAN, "\n### P03-T02 · blocked · 2026-11-01\nQuestion: x\n")
        self.assertIn("P03 approved 1/3 tasks, blocked", check_docs.lint(self.root).summary)
        self.append(PLAN, "\n### Ready for review · 2026-11-02\nFull check → pass.\n")
        self.assertIn("P03 approved 1/3 tasks, ready for review", check_docs.lint(self.root).summary)

    # Status against the Log

    def test_built_without_review(self):
        self.replace(BUILT, "### Review 1 · 2026-10-28", "### Changed · 2026-10-28")
        self.assertError("P02 is built but its Log has no Review entry")

    def test_outcome_but_not_built(self):
        self.replace(ROADMAP, "| P02 | Streak calendar | built |", "| P02 | Streak calendar | approved |")
        self.assertError("P02 has an Outcome entry but ROADMAP says approved")

    def test_every_task_checked_without_ready(self):
        self.replace(PLAN, "Approved: 2026-10-30 T01–T02", "Approved: 2026-10-30 all")
        self.replace(PLAN, "- [ ] P03-T02", "- [x] P03-T02")
        self.replace(PLAN, "- [ ] P03-T03", "- [x] P03-T03")
        self.assertWarning("P03 has every task checked but no 'Ready for review' entry")

    # DECISIONS

    def test_duplicate_decision(self):
        self.append(DECISIONS, "\n## D001 Again — accepted (P01)\nContext: x\nRejected: y — z\n")
        self.assertError("duplicate decision D001")

    def test_decision_without_status(self):
        self.append(DECISIONS, "\n## D003 Use Hono\nContext: x\n")
        self.assertError("D003 heading needs a status")

    def test_decision_without_rejected(self):
        self.replace(DECISIONS, "Rejected: A job queue — a second service for a handful of jobs a day.\n", "")
        self.assertWarning("D002 needs a 'Rejected:' line")

    def test_legacy_decision_with_status_in_body_is_accepted(self):
        long_body = "".join(f"- detail {n}\n" for n in range(12))
        self.append(DECISIONS, f"\n## D003: Use Hono\nDate: 2026-10-01 | Status: accepted\n{long_body}")
        self.assertClean()

    def test_decision_still_proposed_after_build(self):
        self.replace(DECISIONS, "proposed (P03)", "proposed (P02)")
        self.assertWarning("D002 is still proposed but P02 is built")

    # Specs

    def test_spec_needs_rules(self):
        self.replace(SPEC, "## Rules\n", "## Behavior\n")
        self.assertError("streaks.md: missing section '## Rules'")

    def test_spec_duplicate_rule(self):
        self.replace(SPEC, "- R3 ", "- R2 ")
        self.assertError("duplicate rule R2")

    def test_spec_unnumbered_rule(self):
        self.replace(SPEC, "- R3 ", "- ")
        self.assertWarning("number each rule R<n>")

    def test_spec_bad_name(self):
        (self.root / "docs/specs/Streak_Rules.md").write_text("# Streaks\n\n## Rules\n- R1 x\n")
        self.assertError("filename must be a kebab-case area name")

    def test_spec_oversized(self):
        self.append(SPEC, "".join(f"note {n}\n" for n in range(150)))
        self.assertWarning("split the area")

    def test_spec_status_warning(self):
        self.replace(SPEC, "# Streaks\n", "# Streaks\n\nStatus: draft\n")
        self.assertWarning("streaks.md: status belongs in docs/ROADMAP.md")

    # Paths in lasting records

    def test_missing_path_in_architecture(self):
        self.replace(ARCH, "| `src/streaks.ts` |", "| `src/streak-calc.ts` |")
        self.assertError("`src/streak-calc.ts` does not exist")

    def test_missing_path_in_agents(self):
        self.replace("AGENTS.md", "- Dates/time: `src/dates.ts`", "- Dates/time: `src/lib/dates.ts`")
        self.assertError("AGENTS.md: `src/lib/dates.ts` does not exist")

    def test_missing_path_in_spec(self):
        self.replace(SPEC, "Code: `src/streaks.ts`", "Code: `src/streaks/index.ts`")
        self.assertError("streaks.md: `src/streaks/index.ts` does not exist")

    def test_paths_that_are_not_repo_paths_are_skipped(self):
        self.append(ARCH, "Uses `react-dom/client`, `application/json`, `https://x.dev/a`, `src/<area>/`, `~/bin/x`, `src/*.ts`, `docs/specs/later.md`.\n")
        self.assertClean()

    def test_paths_in_code_fences_are_skipped(self):
        self.append(ARCH, "\n```\n`src/gone.ts`\n```\n")
        self.assertClean()

    # Citations in plans that aren't built yet

    def test_cites_unknown_decision(self):
        self.replace(PLAN, "In-process timer (D002)", "In-process timer (D009)")
        self.assertError("cites D009, which is not in docs/DECISIONS.md")

    def test_cites_unknown_invariant(self):
        self.replace(PLAN, "I01 still holds", "I07 still holds")
        self.assertError("cites I07, which is not in docs/ARCHITECTURE.md invariants")

    def test_tag_names_unknown_spec(self):
        self.replace(PLAN, "[streaks new]", "[reminders new]")
        self.assertError("[reminders new] names no spec docs/specs/reminders.md")

    def test_tag_names_unknown_rule(self):
        self.replace(PLAN, "[streaks new]", "[streaks R9]")
        self.assertError("docs/specs/streaks.md has no rule R9")

    def test_prose_cites_unknown_rule(self):
        self.replace(PLAN, "the same day streaks R1 counts", "the same day streaks R7 counts")
        self.assertError("cites streaks R7, which docs/specs/streaks.md does not have")

    def test_read_names_unknown_spec(self):
        self.replace(PLAN, "Read: streaks, D002, I01", "Read: streaks, billing, D002, I01")
        self.assertError("Read: 'billing' names no spec")

    def test_cites_another_plans_requirements(self):
        self.replace(PLAN, "C4. Saving the same time twice", "C4. As in P02 C2, saving the same time twice")
        self.assertWarning("cites P02's requirements; cite the spec rule instead")

    def test_built_plans_are_not_checked_for_citations(self):
        self.replace(BUILT, "[streaks new] An unknown", "[streaks R9] An unknown")
        self.assertClean()

    def test_exit_code(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check_docs.main(["x", str(self.root)]), 0)
            (self.root / "AGENTS.md").unlink()
            self.assertEqual(check_docs.main(["x", str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
