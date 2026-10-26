"""Tests for skills/clean-dev/scripts/check_docs.py.

Each case copies the good fixture, applies one mutation, and expects one message.
Run: python3 -m unittest discover -s tests
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills" / "clean-dev" / "scripts"))
import check_docs  # noqa: E402

GOOD = REPO / "tests" / "fixtures" / "good"
PLAN = "docs/plans/P01-habit-logging.md"
LOG = "docs/logs/P01-habit-logging.md"
ROADMAP = "docs/ROADMAP.md"


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
        report = check_docs.lint(self.root)
        self.assertTrue(any(fragment in w for w in report.warnings), f"{fragment!r} not in {report.warnings}")

    def test_good_fixture_is_clean(self):
        report = check_docs.lint(self.root)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.summary, ["P01 approved 1/3 tasks", "P02 planned"])

    def test_missing_agents(self):
        (self.root / "AGENTS.md").unlink()
        self.assertError("AGENTS.md: missing")

    def test_bad_status(self):
        self.replace(ROADMAP, "| approved |", "| in progress |")
        self.assertError("P01 has status 'in progress'")

    def test_lettered_phase_id(self):
        self.replace(ROADMAP, "| P02 |", "| P01a |")
        self.assertError("bad phase ID 'P01a'")

    def test_plan_not_in_roadmap(self):
        self.replace(ROADMAP, "| P01 | Habit logging | approved | [plan](plans/P01-habit-logging.md) |\n", "")
        self.assertError("P01 is not listed in docs/ROADMAP.md")

    def test_heading_mismatch(self):
        self.replace(PLAN, "# P01 Habit logging", "# P02 Habit logging")
        self.assertError("first line must be '# P01 <title>'")

    def test_missing_section(self):
        self.replace(PLAN, "## Changes\n- none\n", "")
        self.assertError("missing section '## Changes'")

    def test_checklist_without_card(self):
        self.replace(PLAN, "- [ ] P01-T03 Add check-in route\n", "- [ ] P01-T03 Add check-in route\n- [ ] P01-T04 Add form\n")
        self.assertError("P01-T04 is in the checklist but has no card")

    def test_card_missing_check(self):
        self.replace(PLAN, "Check: `pnpm vitest run tests/routes.test.ts`\n", "")
        self.assertError("P01-T03 card is missing 'Check:'")

    def test_checked_outside_approved_range(self):
        self.replace(PLAN, "- [ ] P01-T03", "- [x] P01-T03")
        self.assertError("P01-T03 is checked but outside the Approved: range")

    def test_status_approved_but_plan_pending(self):
        self.replace(PLAN, "Approved: 2026-10-26 T01–T02", "Approved: pending")
        self.replace(PLAN, "- [x] P01-T01", "- [ ] P01-T01")
        self.assertError("P01 is approved but its plan says 'Approved: pending'")

    def test_built_with_open_tasks(self):
        self.replace(ROADMAP, "| approved |", "| built |")
        self.assertError("P01 is built but 2 task(s) are unchecked")

    def test_bad_approved_line(self):
        self.replace(PLAN, "Approved: 2026-10-26 T01–T02", "Approved: yes")
        self.assertError("cannot parse approval group 'yes'")

    def test_log_without_plan(self):
        (self.root / "docs/logs/P09-orphan.md").write_text("# P09 log\n")
        self.assertError("no plan with the same filename")

    def test_log_entry_for_unknown_task(self):
        self.append(LOG, "\n## P01-T09 · done · 2026-10-26\nNotes: none\n")
        self.assertError("entry for unknown task P01-T09")

    def test_duplicate_decision(self):
        self.append("docs/DECISIONS.md", "\n## D001 Again — accepted (P01)\nContext: x\n")
        self.assertError("duplicate decision D001")

    def test_decision_without_status(self):
        self.append("docs/DECISIONS.md", "\n## D002 Use Hono\nContext: x\n")
        self.assertError("D002 heading needs a status")

    def test_v1_decision_with_status_in_body_is_accepted(self):
        long_body = "".join(f"- detail {n}\n" for n in range(12))
        self.append("docs/DECISIONS.md", f"\n## D002: Use Hono\nDate: 2026-10-01 | Status: accepted\n{long_body}")
        report = check_docs.lint(self.root)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_agents_status_warning(self):
        self.append("AGENTS.md", "Status: P01 in progress\n")
        self.assertWarning("status belongs in docs/ROADMAP.md")

    def test_agents_test_count_warning(self):
        self.append("AGENTS.md", "- Suite: 412 tests green\n")
        self.assertWarning("test counts belong in logs")

    def test_legacy_layout_warning(self):
        (self.root / "phase1.md").write_text("# Phase 1\n")
        self.assertWarning("legacy plan location")

    def test_banned_sub_unit_heading(self):
        self.append(PLAN, "\n### Unit 2 — more work\n")
        self.assertWarning("use tasks (PNN-TNN)")

    def test_line_number_reference(self):
        self.replace(PLAN, "Read first: `src/db/schema.ts`", "Read first: `src/db/schema.ts:42`")
        self.assertWarning("line-number reference")

    def test_checked_task_without_log_entry(self):
        self.replace(PLAN, "- [ ] P01-T02", "- [x] P01-T02")
        self.assertWarning("P01-T02 is checked but has no 'done' entry")

    def test_archived_plan_link_allowed_for_done(self):
        archive = self.root / "docs/archive/phases"
        archive.mkdir(parents=True)
        (archive / "02-streaks.md").write_text("# old\n")
        self.replace(ROADMAP, "| P02 | Streak calendar | planned | — |", "| P02 | Streak calendar | done | [plan](archive/phases/02-streaks.md) |")
        self.assertEqual(check_docs.lint(self.root).errors, [])

    def test_exit_code(self):
        self.assertEqual(check_docs.main(["x", str(self.root)]), 0)
        (self.root / "AGENTS.md").unlink()
        self.assertEqual(check_docs.main(["x", str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
