#!/usr/bin/env python3
"""Lint a project's clean-dev records.

Usage: python3 check_docs.py [project_root]
Prints ERROR/WARN lines and a phase summary. Exits 1 if there are errors.
Formats are defined in references/templates.md. docs/archive/ is ignored.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

STATUSES = {"planned", "approved", "built", "done", "dropped"}
NEEDS_APPROVAL = {"approved", "built", "done"}
ALL_TASKS_DONE = {"built", "done"}
COMMON_SECTIONS = ["Goal", "Builder context", "Tasks", "Acceptance", "Changes"]
KIND_SECTIONS = {"feature": ["Spec"], "fix": ["Bug", "Cause"]}
CARD_FIELDS = ["Files:", "Do:", "Check:"]
LOG_HEADINGS = re.compile(r"^(Baseline|Ready for review|Review \d+|Outcome)\b")
DASH = r"\s*[·|—–-]\s*"

PLAN_NAME = re.compile(r"^(P\d{2,3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
ROW = re.compile(r"^\|\s*(P[^|]*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
CHECKLIST = re.compile(r"^- \[([ xX])\] (P\d{2,3}-T\d{2})\s+(.+)$")
CARD = re.compile(r"^### (P\d{2,3}-T\d{2})\s+(.+)$")
LOG_TASK = re.compile(rf"^## (P\d{{2,3}}-T\d{{2}}){DASH}(done|blocked|unblocked){DASH}\d{{4}}-\d{{2}}-\d{{2}}\s*$")
APPROVED_GROUP = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.+)$")
TASK_RANGE = re.compile(r"^T(\d{2})(?:\s*[–-]\s*T(\d{2}))?$")
PATH_LINE = re.compile(r"\b[\w./-]+\.(?:ts|tsx|js|jsx|mjs|py|go|rs|rb|java|kt|swift|css|sql|vue|svelte):\d+\b")
BANNED_HEADING = re.compile(r"^#+\s*(?:increment|unit|slice|batch|sub-?phase|step)\s+\d", re.I)
LETTERED = re.compile(r"^#+\s*(?:phase\s+)?\d{1,3}[a-z]\b", re.I)
DECISION_STATUS = re.compile(r"\b(proposed|accepted|superseded)\b", re.I)
GENERATED = re.compile(r"\((?:generated)\)|\.d\.ts\b|lock\b|/migrations?/|/drizzle/|/vendor/")


@dataclass
class Report:
    root: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: list[str] = field(default_factory=list)

    def err(self, path: Path, msg: str) -> None:
        self.errors.append(f"ERROR {self._rel(path)}: {msg}")

    def warn(self, path: Path, msg: str) -> None:
        self.warnings.append(f"WARN  {self._rel(path)}: {msg}")

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)


@dataclass
class Plan:
    pid: str
    path: Path
    approved: set[int] | None  # None means pending
    tasks: dict[str, bool]  # task id -> checked


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def sections(lines: list[str]) -> dict[str, list[str]]:
    """Map each `## ` heading to the lines under it."""
    out: dict[str, list[str]] = {}
    current = None
    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return out


def header_value(lines: list[str], name: str) -> str | None:
    for line in lines:
        if line.startswith("## "):
            break
        if line.startswith(f"{name}:"):
            return line.split(":", 1)[1].strip()
    return None


def parse_approved(value: str) -> set[int] | None | str:
    """Return approved task numbers, None for pending, or an error message."""
    if value == "pending":
        return None
    numbers: set[int] = set()
    for group in value.split(";"):
        match = APPROVED_GROUP.match(group.strip())
        if not match:
            return f"cannot parse approval group '{group.strip()}'"
        for item in match.group(2).split(","):
            item = item.strip()
            if item == "all":
                numbers.update(range(1, 1000))
                continue
            task = TASK_RANGE.match(item)
            if not task:
                return f"cannot parse task range '{item}'"
            start = int(task.group(1))
            end = int(task.group(2) or start)
            numbers.update(range(start, end + 1))
    return numbers


def check_agents(root: Path, r: Report) -> None:
    path = root / "AGENTS.md"
    if not path.is_file():
        r.err(path, "missing")
        return
    lines = read_lines(path)
    if len(lines) > 80:
        r.warn(path, f"{len(lines)} lines; keep it to 80 (move detail to docs/)")
    for line in lines:
        text = line.strip()
        if re.match(r"^[-*]?\s*\**status\**:", text, re.I) or re.search(r"\bin[ _]progress\b", text, re.I):
            r.warn(path, f"status belongs in docs/ROADMAP.md: '{text[:60]}'")
        elif re.search(r"\b\d+ (?:tests?|passed|passing)\b", text):
            r.warn(path, f"test counts belong in logs: '{text[:60]}'")


def check_roadmap(root: Path, r: Report) -> dict[str, tuple[str, str | None]]:
    path = root / "docs" / "ROADMAP.md"
    phases: dict[str, tuple[str, str | None]] = {}
    if not path.is_file():
        r.err(path, "missing")
        return phases
    for line in read_lines(path):
        row = ROW.match(line)
        if not row or row.group(1) == "ID":
            continue
        pid, _, status, plan_cell = row.groups()
        if not re.fullmatch(r"P\d{2,3}", pid):
            r.err(path, f"bad phase ID '{pid}' (use P01, P02…, never letters)")
            continue
        if pid in phases:
            r.err(path, f"duplicate phase {pid}")
        if status not in STATUSES:
            r.err(path, f"{pid} has status '{status}'; use one of {', '.join(sorted(STATUSES))}")
        link = re.search(r"\]\(([^)]+)\)", plan_cell)
        target = link.group(1) if link else None
        if target:
            if not (path.parent / target).is_file():
                r.err(path, f"{pid} links to missing file {target}")
            elif target.startswith("plans/") and not Path(target).name.startswith(pid + "-"):
                r.err(path, f"{pid} links to another phase's plan {target}")
        elif status != "planned":
            r.err(path, f"{pid} is {status} but has no plan link")
        phases[pid] = (status, target)
    return phases


def check_plan(path: Path, r: Report) -> Plan | None:
    name = PLAN_NAME.match(path.name)
    if not name:
        r.err(path, "filename must be P<NN>-kebab-slug.md")
        return None
    pid = name.group(1)
    lines = read_lines(path)
    if not lines or not re.match(rf"^# {pid}\s+\S", lines[0]):
        r.err(path, f"first line must be '# {pid} <title>'")
    kind = header_value(lines, "Kind")
    if kind not in KIND_SECTIONS:
        r.err(path, "needs 'Kind: feature' or 'Kind: fix'")
    approved_raw = header_value(lines, "Approved")
    approved: set[int] | None = None
    if approved_raw is None:
        r.err(path, "needs an 'Approved:' line")
    else:
        parsed = parse_approved(approved_raw)
        if isinstance(parsed, str):
            r.err(path, f"Approved: {parsed}")
        else:
            approved = parsed
    found = sections(lines)
    for section in COMMON_SECTIONS + KIND_SECTIONS.get(kind or "", []):
        if section not in found:
            r.err(path, f"missing section '## {section}'")

    tasks: dict[str, bool] = {}
    cards: dict[str, list[str]] = {}
    current: str | None = None
    for line in found.get("Tasks", []):
        item = CHECKLIST.match(line)
        card = CARD.match(line)
        if item:
            tid = item.group(2)
            if tid in tasks:
                r.err(path, f"duplicate checklist item {tid}")
            tasks[tid] = item.group(1) != " "
        elif card:
            current = card.group(1)
            if current in cards:
                r.err(path, f"duplicate card {current}")
            cards[current] = []
        elif line.startswith("### "):
            current = None
            r.err(path, f"card heading must be '### {pid}-TNN <verb title>': '{line[:60]}'")
        elif current:
            cards[current].append(line)

    for tid in list(tasks) + list(cards):
        if not tid.startswith(pid + "-"):
            r.err(path, f"task {tid} does not belong to {pid}")
    for tid in tasks.keys() - cards.keys():
        r.err(path, f"{tid} is in the checklist but has no card")
    for tid in cards.keys() - tasks.keys():
        r.err(path, f"{tid} has a card but no checklist item")
    for tid, body in cards.items():
        for label in CARD_FIELDS:
            if not any(line.startswith(label) for line in body):
                r.err(path, f"{tid} card is missing '{label}'")
        files = card_files(body)
        if len(files) > 5:
            r.warn(path, f"{tid} lists {len(files)} source files; keep cards to 5")
    if approved is not None:
        for tid, checked in tasks.items():
            number = int(tid.split("-T")[1])
            if checked and number not in approved:
                r.err(path, f"{tid} is checked but outside the Approved: range")

    for line in lines:
        if PATH_LINE.search(line):
            r.warn(path, f"line-number reference goes stale: '{line.strip()[:60]}'")
        if BANNED_HEADING.match(line) or LETTERED.match(line):
            r.warn(path, f"use tasks (PNN-TNN), not sub-units or lettered phases: '{line.strip()[:60]}'")
    return Plan(pid, path, approved, tasks)


def card_files(body: list[str]) -> list[str]:
    """Non-generated source paths listed under a card's Files: field."""
    files: list[str] = []
    collecting = False
    for line in body:
        if line.startswith("Files:"):
            collecting = True
            continue
        if collecting and re.match(r"^[A-Z][a-z]+:", line):
            break
        if collecting and line.lstrip().startswith("- ") and not GENERATED.search(line):
            files.append(line.strip())
    return files


def check_plans(root: Path, r: Report) -> dict[str, Plan]:
    plans: dict[str, Plan] = {}
    folder = root / "docs" / "plans"
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        plan = check_plan(path, r)
        if plan:
            if plan.pid in plans:
                r.err(path, f"second plan file for {plan.pid}")
            plans[plan.pid] = plan
    return plans


def cross_check(root: Path, phases: dict[str, tuple[str, str | None]], plans: dict[str, Plan], r: Report) -> None:
    roadmap = root / "docs" / "ROADMAP.md"
    for pid, plan in plans.items():
        if pid not in phases:
            r.err(plan.path, f"{pid} is not listed in docs/ROADMAP.md")
            continue
        status = phases[pid][0]
        if status in NEEDS_APPROVAL and plan.approved is None:
            r.err(roadmap, f"{pid} is {status} but its plan says 'Approved: pending'")
        if status in ALL_TASKS_DONE and not all(plan.tasks.values()):
            open_tasks = sum(1 for done in plan.tasks.values() if not done)
            r.err(roadmap, f"{pid} is {status} but {open_tasks} task(s) are unchecked")
        if status == "planned" and plan.approved is not None:
            r.warn(roadmap, f"{pid} plan is approved but ROADMAP still says planned")


def check_logs(root: Path, plans: dict[str, Plan], r: Report) -> None:
    folder = root / "docs" / "logs"
    by_name = {plan.path.name: plan for plan in plans.values()}
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        plan = by_name.get(path.name)
        if not plan:
            r.err(path, "no plan with the same filename in docs/plans/")
            continue
        logged: set[str] = set()
        entry: list[str] | None = None
        for line in read_lines(path) + ["## end"]:
            if line.startswith("## "):
                if entry is not None and len([x for x in entry if x.strip()]) > 8:
                    r.warn(path, f"entry '{entry_title}' is over 8 lines")
                entry, entry_title = None, line[3:].strip()
                task = LOG_TASK.match(line)
                if task:
                    entry = []
                    if task.group(1) not in plan.tasks:
                        r.err(path, f"entry for unknown task {task.group(1)}")
                    if task.group(2) == "done":
                        logged.add(task.group(1))
                elif line != "## end" and not LOG_HEADINGS.match(entry_title):
                    r.warn(path, f"unexpected heading '{line[:60]}'")
            elif entry is not None:
                entry.append(line)
        for tid, checked in plan.tasks.items():
            if checked and tid not in logged:
                r.warn(path, f"{tid} is checked but has no 'done' entry")


def check_decisions(root: Path, r: Report) -> None:
    """New entries carry status in the heading. Legacy (v1) entries keep it in the body and skip the length check."""
    path = root / "docs" / "DECISIONS.md"
    if not path.is_file():
        return
    entries: list[tuple[str, str, list[str]]] = []
    for line in read_lines(path):
        match = re.match(r"^## (D\d{3})\b(.*)$", line)
        if match:
            entries.append((match.group(1), match.group(2), []))
        elif line.startswith("## "):
            entries.append(("", "", []))
        elif entries:
            entries[-1][2].append(line)
    seen: set[str] = set()
    for did, heading, body in entries:
        if not did:
            continue
        if did in seen:
            r.err(path, f"duplicate decision {did}")
        seen.add(did)
        if DECISION_STATUS.search(heading):
            size = len([x for x in body if x.strip()])
            if size > 8:
                r.warn(path, f"{did} is {size} lines; keep entries to 8")
        elif not any(DECISION_STATUS.search(x) for x in body if "status" in x.lower()):
            r.err(path, f"{did} heading needs a status: proposed, accepted, or superseded by DNNN")


def check_legacy(root: Path, r: Report) -> None:
    legacy = [root / "docs" / "phases", root / "docs" / "plan", root / "docs" / "PLAN.md"]
    legacy += sorted(root.glob("phase*.md"))
    for path in legacy:
        if path.exists():
            r.warn(path, "legacy plan location; see references/adopt.md (archive under docs/archive/)")


def lint(root: Path) -> Report:
    r = Report(root)
    check_agents(root, r)
    phases = check_roadmap(root, r)
    plans = check_plans(root, r)
    cross_check(root, phases, plans, r)
    check_logs(root, plans, r)
    check_decisions(root, r)
    check_legacy(root, r)
    r.summary = summary(phases, plans)
    return r


def summary(phases: dict[str, tuple[str, str | None]], plans: dict[str, Plan]) -> list[str]:
    out = []
    for pid, (status, _) in phases.items():
        plan = plans.get(pid)
        progress = f" {sum(plan.tasks.values())}/{len(plan.tasks)} tasks" if plan else ""
        out.append(f"{pid} {status}{progress}")
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    report = lint(root)
    for line in report.errors + report.warnings:
        print(line)
    for line in report.summary:
        print(line)
    print(f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
