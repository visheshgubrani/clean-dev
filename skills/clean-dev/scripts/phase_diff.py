#!/usr/bin/env python3
"""Summarize one phase's changes for the builder's pre-flight and the reviewer.

Usage: python3 phase_diff.py P07 [project_root]
Prints the phase's BASE commit and flags what review usually finds: unrelated commits
in the range, files outside the plan's Touches:, task commits without a Check: trailer
or that don't match a plan task, new definitions whose name is already defined
elsewhere, debug statements, plan or decision IDs in code, large touched files, and
Follow-up: trailers. It only reads git and the working tree.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
LARGE_FILE = 400
# Top-level definitions only: methods and local closures legitimately share names.
DEFINITION = re.compile(
    r"^(?:export\s+)?(?:default\s+)?(?:pub(?:\([^)]*\))?\s+)?(?:abstract\s+)?(?:async\s+)?"
    r"(?:function\*?\s+(\w+)|def\s+(\w+)|class\s+(\w+)|fn\s+(\w+)|func\s+(\w+)"
    r"|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*(?::[^=]+)?=>|\w+\s*=>))"
)
# Names that frameworks expect many files to define.
COMMON = {
    "main", "init", "setup", "teardown", "handler", "handle", "render", "constructor", "default",
    "test", "run", "new", "New", "String", "Error", "ServeHTTP", "toString", "get", "set", "load",
    "GET", "POST", "PUT", "PATCH", "DELETE", "loader", "action", "Page", "Layout", "middleware",
    "config", "up", "down", "__init__", "__str__", "__repr__",
}
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|e2e|fixtures?|testdata)/|[._-](test|spec)\.\w+$|(^|/)test_[^/]+\.py$|_test\.go$")
SKIP_PATH = re.compile(
    r"(^|/)(node_modules|vendor|dist|build|\.next|target|migrations?)/|\.min\.\w+$|\.d\.ts$|\.gen\.\w+$"
    r"|_pb2?\.\w+$|\.pb\.go$|(^|/)[^/]*lock[^/]*$|\.(lock|svg|map|png|jpg|gif|ico|woff2?)$"
)
DEBUG = re.compile(r"console\.log\(|\bdebugger\b|\.only\(|\bdbg!\(|\bbreakpoint\(\)|\bpdb\.set_trace|\bTODO\b|\bFIXME\b")
IDS = re.compile(r"\bP\d{2,3}(?:-T\d{2})?\b|\b(?:D\d{3}|I\d{2})\b|\b[Pp]hase \d")
FAMILY = {"tsx": "ts", "js": "ts", "jsx": "ts", "mjs": "ts", "cjs": "ts", "mts": "ts", "cts": "ts"}
CHECKLIST = re.compile(r"^- \[([ xX])\] (P\d{1,3}-T\d{2})\s+(.+?)\s*$")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=True)
    return result.stdout


def definition_name(line: str) -> str | None:
    match = DEFINITION.match(line)
    if not match:
        return None
    return next(name for name in match.groups() if name)


def family(path: str) -> str:
    """Compare names only within one language family."""
    ext = path.rsplit(".", 1)[-1] if "." in path.rsplit("/", 1)[-1] else ""
    return FAMILY.get(ext, ext)


def comparable(name: str | None, path: str) -> bool:
    """Skip framework names, and Go's exported names, which their package already namespaces."""
    if not name or len(name) < 3 or name in COMMON:
        return False
    return not (path.endswith(".go") and name[0].isupper())


def is_docs(path: str) -> bool:
    return path.startswith("docs/") or path.endswith(".md")


def read_plan(root: Path, pid: str) -> tuple[list[str], dict[str, tuple[bool, str]]]:
    """Touches: entries and checklist tasks (id -> (checked, title)) from the phase's plan."""
    plans = sorted((root / "docs" / "plans").glob(f"{pid}-*.md"))
    if not plans:
        return [], {}
    touches: list[str] = []
    tasks: dict[str, tuple[bool, str]] = {}
    for line in plans[0].read_text(encoding="utf-8").splitlines():
        if line.startswith("Touches:"):
            touches = re.findall(r"`([^`]+)`", line)
        item = CHECKLIST.match(line)
        if item:
            tasks[item.group(2)] = (item.group(1) != " ", item.group(3))
    return touches, tasks


def phase_commits(root: Path, pid: str) -> list[tuple[str, str, str]]:
    log = git(root, "log", "--reverse", "--format=%H%x1f%s%x1f%B%x1e", "-E", f"--grep=^{pid}([ -]|$)")
    commits = []
    for record in log.split("\x1e"):
        record = record.strip("\n")
        if record:
            sha, subject, body = record.split("\x1f", 2)
            if re.match(rf"^{pid}([ -]|$)", subject):
                commits.append((sha, subject, body))
    return commits


def collect(root: Path, pid: str) -> dict:
    commits = phase_commits(root, pid)
    task_commits = [c for c in commits if re.match(rf"^{pid}-T\d{{2}}\b", c[1])]
    if not task_commits:
        return {"error": f"no commits whose subject starts with '{pid}-T'"}
    parents = git(root, "rev-list", "--parents", "-n", "1", task_commits[0][0]).split()
    base = parents[1] if len(parents) > 1 else EMPTY_TREE
    end = commits[-1][0]  # the phase's last commit, so later work stays out of a finished phase
    span = end if base == EMPTY_TREE else f"{base}..{end}"
    in_range = git(root, "log", "--format=%h %s", span).splitlines()
    touches, tasks = read_plan(root, pid)

    touched = [p for p in git(root, "diff", "--name-only", base, end).splitlines() if p]
    outside = [p for p in touched if touches and not is_docs(p)
               and not any(p == t.rstrip("/") or p.startswith(t.rstrip("/") + "/") for t in touches)]

    task_issues = []
    committed = set()
    for _, subject, body in task_commits:
        tid, _, title = subject.partition(" ")
        committed.add(tid)
        if tasks and tid not in tasks:
            task_issues.append(f"{tid}: not a task in the plan")
        elif tasks and title != tasks[tid][1]:
            task_issues.append(f"{tid}: subject differs from the plan ('{tasks[tid][1]}')")
        if not re.search(r"^Check:\s*\S", body, re.M):
            task_issues.append(f"{tid}: no Check: trailer")
    for tid, (checked, _) in tasks.items():
        if checked and tid not in committed:
            task_issues.append(f"{tid}: checked in the plan but has no commit")

    new_defs: dict[str, str] = {}
    debug, ids = [], []
    current = None
    for line in git(root, "diff", "-U0", base, end).splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
            continue
        if not line.startswith("+") or not current or SKIP_PATH.search(current) or is_docs(current):
            continue
        text = line[1:]
        name = definition_name(text)
        if comparable(name, current) and not TEST_PATH.search(current):
            new_defs.setdefault(name, current)
        if DEBUG.search(text):
            debug.append(f"{current}: {text.strip()[:80]}")
        if IDS.search(text):
            ids.append(f"{current}: {text.strip()[:80]}")

    duplicates: dict[str, list[str]] = {}
    if new_defs:
        for path in git(root, "ls-files").splitlines():
            if SKIP_PATH.search(path) or TEST_PATH.search(path) or is_docs(path):
                continue
            file = root / path
            try:
                if file.stat().st_size > 1_000_000:
                    continue
                lines = file.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for line in lines:
                name = definition_name(line)
                if name in new_defs and path != new_defs[name] and family(path) == family(new_defs[name]):
                    duplicates.setdefault(name, [])
                    if path not in duplicates[name]:
                        duplicates[name].append(path)

    large = []
    for path in touched:
        file = root / path
        if SKIP_PATH.search(path) or is_docs(path) or not file.is_file():
            continue
        try:
            count = len(file.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            continue
        if count >= LARGE_FILE:
            large.append((count, path))

    followups = [line.split(":", 1)[1].strip() for _, _, body in commits
                 for line in body.splitlines() if line.startswith("Follow-up:")]
    return {
        "base": base,
        "end": end,
        "task_commits": len(task_commits),
        "stat": git(root, "diff", "--shortstat", base, end).strip(),
        "other_commits": [c for c in in_range if not re.match(rf"^\w+ {pid}([ -]|$)", c)],
        "outside_touches": outside,
        "task_issues": task_issues,
        "duplicates": {name: (new_defs[name], paths) for name, paths in duplicates.items()},
        "debug": debug,
        "ids": ids,
        "large": [f"{path} {count}" for count, path in sorted(large, reverse=True)[:5]],
        "followups": followups,
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2 or not re.fullmatch(r"P\d{1,3}", argv[1]):
        print("usage: phase_diff.py P07 [project_root]")
        return 2
    pid, root = argv[1], Path(argv[2] if len(argv) > 2 else ".").resolve()
    try:
        data = collect(root, pid)
    except subprocess.CalledProcessError as error:
        print(f"git failed: {error.stderr.strip()}")
        return 2
    if "error" in data:
        print(f"{pid}: {data['error']}")
        return 2
    print(f"{pid}: {data['task_commits']} task commit(s). BASE={data['base'][:12]}")
    print(f"Diff: git diff {data['base'][:12]} {data['end'][:12]}   ({data['stat']})")
    sections = [
        ("Commits in the range that aren't this phase's", data["other_commits"]),
        ("Files outside the plan's Touches", data["outside_touches"]),
        ("Task commits", data["task_issues"]),
        ("New names already defined elsewhere (reuse the owner, or say why not)",
         [f"{name}  {new}  also: {', '.join(paths)}" for name, (new, paths) in data["duplicates"].items()]),
        ("Debug statements and TODOs", data["debug"]),
        ("Plan or decision IDs in code", data["ids"]),
        (f"Touched files of {LARGE_FILE}+ lines (a second responsibility?)", data["large"]),
        ("Follow-ups", data["followups"]),
    ]
    flagged = False
    for title, items in sections:
        if items:
            flagged = True
            print(f"\n{title}:")
            for item in items:
                print(f"  {item}")
    if not flagged:
        print("\nNothing to flag.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
