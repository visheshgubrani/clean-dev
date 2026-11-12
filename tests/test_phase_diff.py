"""Tests for skills/clean-dev/scripts/phase_diff.py against a throwaway git repo.

Run: python3 -m unittest discover -s tests
"""
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills" / "clean-dev" / "scripts"))
import phase_diff  # noqa: E402

PLAN = """# P01 Refunds

Format: 4
Touches: `src/payments/`

## Tasks
- [x] P01-T01 Add refunds
  Done when: x
- [x] P01-T02 Add the refund page
  Done when: x
- [x] P01-T03 Email the receipt
  Done when: x
"""


class PhaseDiffTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.git("init", "-q")
        self.write("src/lib/money.ts", "export function fmtCents(n: number) {\n  return `${n}`\n}\n")
        self.write("docs/plans/P01-refunds.md", PLAN)
        self.commit("Initial")
        self.write("src/payments/refunds.ts",
                   "export function fmtCents(n: number) {}\n"
                   "export const refundOrder = async (id: string) => {}\n"
                   "console.log('refund')\n"
                   "// P01 lock first\n")
        self.write("other.txt", "outside\n")
        self.commit("P01-T01 Add refunds\n\nCheck: vitest → 3 passed\nFollow-up: a second cents formatter")
        self.write("src/unrelated.ts", "export const x = 1\n")
        self.commit("Tidy something else")
        self.write("src/payments/page.ts", "export function refundPage() {}\n")
        self.commit("P01-T02 Add refunds to the page")
        self.write("src/later.ts", "export const y = 2\n")
        self.commit("Later work after the phase")

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, *args):
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "-c", "commit.gpgsign=false", *args], cwd=self.root, check=True, capture_output=True)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def test_report(self):
        data = phase_diff.collect(self.root, "P01")
        self.assertEqual(data["task_commits"], 2)
        self.assertEqual(data["duplicates"], {"fmtCents": ("src/payments/refunds.ts", ["src/lib/money.ts"])})
        self.assertIn("other.txt", data["outside_touches"])
        self.assertIn("src/unrelated.ts", data["outside_touches"])
        self.assertTrue(any("Tidy something else" in c for c in data["other_commits"]))
        self.assertNotIn("src/later.ts", data["outside_touches"])
        self.assertFalse(any("Later work" in c for c in data["other_commits"]))
        self.assertIn("P01-T02: subject differs from the plan ('Add the refund page')", data["task_issues"])
        self.assertIn("P01-T02: no Check: trailer", data["task_issues"])
        self.assertIn("P01-T03: checked in the plan but has no commit", data["task_issues"])
        self.assertTrue(any("console.log" in d for d in data["debug"]))
        self.assertTrue(any("P01 lock first" in i for i in data["ids"]))
        self.assertEqual(data["followups"], ["a second cents formatter"])

    def test_no_task_commits(self):
        self.assertIn("error", phase_diff.collect(self.root, "P02"))

    def test_main_prints_sections(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(phase_diff.main(["x", "P01", str(self.root)]), 0)
            self.assertEqual(phase_diff.main(["x", "P02", str(self.root)]), 2)
            self.assertEqual(phase_diff.main(["x", "seven"]), 2)
        self.assertIn("New names already defined elsewhere", out.getvalue())


if __name__ == "__main__":
    unittest.main()
