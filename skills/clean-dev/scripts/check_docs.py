#!/usr/bin/env python3
"""Lint a project's clean-dev records.

Usage: python3 check_docs.py [project_root]
Prints ERROR/WARN lines and a phase summary. Exits 1 if there are errors.
Formats are defined in references/templates.md. docs/archive/ and docs/logs/ are ignored.
Plans with 'Format: 4' get the full checks. Older plans are history: only their
heading, Approved: line, and checkboxes are checked.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

STATUSES = {"planned", "approved", "built", "done", "dropped"}
NEEDS_APPROVAL = {"approved", "built", "done"}
ALL_TASKS_DONE = {"built", "done"}
ACTIVE = {"planned", "approved"}
SECTIONS = ["Goal", "Requirements", "Tasks", "Acceptance"]
KIND_SECTIONS = {"feature": [], "fix": ["Bug"]}
HEADER_LINES = ["Depends on", "Touches"]
AGENTS_LINES = 80
PLAN_LINES = 250
SPEC_LINES = 150
MAX_TASKS = 9
ENTRY_LINES = 8
DASH = r"\s*[·|—–-]\s*"
DATE = r"\d{4}-\d{2}-\d{2}"
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"

PLAN_NAME = re.compile(rf"^(P\d{{2,3}})-{SLUG}\.md$")
SPEC_NAME = re.compile(rf"^{SLUG}\.md$")
ROW = re.compile(r"^\|\s*(P[^|]*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
CHECKLIST = re.compile(r"^- \[([ xX])\] (P\d{2,3}-T\d{2})\s+(.+)$")
LOG_PHASE = re.compile(rf"^### (Baseline|Changed|Ready for review|Review \d+|Outcome){DASH}{DATE}\s*$")
LOG_TASK = re.compile(rf"^### (P\d{{2,3}}-T\d{{2}}){DASH}(blocked|cleared){DASH}{DATE}\s*$")
APPROVED_GROUP = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.+)$")
TASK_RANGE = re.compile(r"^T(\d{2})(?:\s*[–-]\s*T(\d{2}))?$")
PATH_LINE = re.compile(r"\b[\w./-]+\.(?:ts|tsx|js|jsx|mjs|py|go|rs|rb|java|kt|swift|css|sql|vue|svelte):\d+\b")
BANNED_HEADING = re.compile(r"^#+\s*(?:increment|unit|slice|batch|sub-?phase|step)\s+\d", re.I)
LETTERED = re.compile(r"^#+\s*(?:phase\s+)?\d{1,3}[a-z]\b", re.I)
DECISION = re.compile(r"^## (D\d{3})\b(.*)$")
DECISION_STATUS = re.compile(r"\b(proposed|accepted|superseded)\b", re.I)
PROPOSED_FOR = re.compile(r"\bproposed\s*\((P\d{2,3})\)", re.I)
RULE = re.compile(r"^- (R\d+)\b")
INVARIANT = re.compile(r"^- (I\d{2,3})\b")
TAG = re.compile(rf"\[({SLUG}) (R\d+|new)\]")
SPEC_CITE = re.compile(rf"\b({SLUG}) (R\d+)\b")
CITED_ID = re.compile(r"\b(D\d{3}|I\d{2,3})\b")
OTHER_PLAN_C = re.compile(r"\b(P\d{2,3})(?:'s)?\s+C\d+\b")
BACKTICK = re.compile(r"`([^`\s]+)`")
STATUS_LINE = re.compile(r"^[-*]?\s*\**status\**:", re.I)
IN_PROGRESS = re.compile(r"\bin[ _]progress\b", re.I)
TEST_COUNT = re.compile(r"\b\d+ (?:tests?|passed|passing)\b")
NOT_A_PATH = set("<>*?{}$|:=,;()[]'\"")


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
    v4: bool
    approved: set[int] | None  # None means pending
    tasks: dict[str, bool]  # task id -> checked
    lines: list[str]  # the lines above ## Log
    log: list[str] = field(default_factory=list)  # entry kinds in order


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
    for group in re.split(r";", value):
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


def check_text(path: Path, lines: list[str], r: Report, strict: bool) -> None:
    """Status, test counts, and line-number references don't belong in lasting records."""
    for line in lines:
        text = line.strip()
        if STATUS_LINE.match(text) or (strict and IN_PROGRESS.search(text)):
            r.warn(path, f"status belongs in docs/ROADMAP.md: '{text[:60]}'")
        elif TEST_COUNT.search(text):
            r.warn(path, f"test counts belong in commits: '{text[:60]}'")
        if PATH_LINE.search(line):
            r.warn(path, f"line-number reference goes stale: '{text[:60]}'")


def check_agents(root: Path, r: Report) -> None:
    path = root / "AGENTS.md"
    if not path.is_file():
        r.err(path, "missing")
        return
    lines = read_lines(path)
    if len(lines) > AGENTS_LINES:
        r.warn(path, f"{len(lines)} lines; keep it to {AGENTS_LINES} (move detail to docs/)")
    check_text(path, lines, r, strict=True)


def check_architecture(root: Path, r: Report) -> set[str]:
    path = root / "docs" / "ARCHITECTURE.md"
    invariants: set[str] = set()
    if not path.is_file():
        return invariants
    lines = read_lines(path)
    check_text(path, lines, r, strict=False)
    for line in lines:
        match = INVARIANT.match(line)
        if match:
            if match.group(1) in invariants:
                r.err(path, f"duplicate invariant {match.group(1)}")
            invariants.add(match.group(1))
    return invariants


def check_specs(root: Path, r: Report) -> dict[str, set[str]]:
    specs: dict[str, set[str]] = {}
    folder = root / "docs" / "specs"
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        if not SPEC_NAME.match(path.name):
            r.err(path, "filename must be a kebab-case area name, e.g. checkout.md")
            continue
        lines = read_lines(path)
        if not lines or not lines[0].startswith("# "):
            r.err(path, "first line must be '# <Area>'")
        if len(lines) > SPEC_LINES:
            r.warn(path, f"{len(lines)} lines; split the area when a spec passes {SPEC_LINES}")
        check_text(path, lines, r, strict=False)
        found = sections(lines)
        if "Rules" not in found:
            r.err(path, "missing section '## Rules'")
        rules: set[str] = set()
        for line in found.get("Rules", []):
            match = RULE.match(line)
            if match:
                if match.group(1) in rules:
                    r.err(path, f"duplicate rule {match.group(1)}")
                rules.add(match.group(1))
            elif line.startswith("- "):
                r.warn(path, f"number each rule R<n>: '{line[:60]}'")
        specs[path.stem] = rules
    return specs


def path_candidate(token: str) -> str | None:
    """A backticked token that looks like a repo path, or None."""
    if "/" not in token or any(c in NOT_A_PATH for c in token):
        return None
    if token.startswith(("/", "~", "@", "-", "..", "http")):
        return None
    token = token[2:] if token.startswith("./") else token
    if token.startswith("docs/"):
        return None
    return token


def check_paths(root: Path, paths: list[Path], r: Report) -> None:
    """Backticked code paths must exist. Tokens whose first segment isn't in the repo are skipped."""
    for path in paths:
        if not path.is_file():
            continue
        fenced = False
        for line in read_lines(path):
            if line.lstrip().startswith("```"):
                fenced = not fenced
                continue
            if fenced:
                continue
            for token in BACKTICK.findall(line):
                candidate = path_candidate(token)
                if not candidate:
                    continue
                bases = [root, path.parent]
                first = candidate.split("/")[0]
                if not any((base / first).exists() for base in bases):
                    continue
                if not any((base / candidate).exists() for base in bases):
                    r.err(path, f"`{candidate}` does not exist; update or remove it")


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
    fmt = header_value(lines, "Format")
    if fmt not in (None, "3", "4"):
        r.err(path, f"unknown 'Format: {fmt}' (write new plans as 'Format: 4')")
    v4 = fmt == "4"
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

    log_at = next((i for i, line in enumerate(lines) if line.strip() == "## Log"), len(lines))
    body, log = lines[:log_at], lines[log_at + 1:]
    found = sections(body)
    tasks = checklist(pid, path, found.get("Tasks", []), r, v4)
    if approved is not None:
        for tid, checked in tasks.items():
            if checked and int(tid.split("-T")[1]) not in approved:
                r.err(path, f"{tid} is checked but outside the Approved: range")
    plan = Plan(pid, path, v4, approved, tasks, body)
    if v4:
        check_v4(plan, found, log_at < len(lines), r)
        plan.log = check_log(plan, log, r)
    return plan


def checklist(pid: str, path: Path, body: list[str], r: Report, v4: bool) -> dict[str, bool]:
    """Checklist items with their indented fields. v4 items need 'Done when:'."""
    tasks: dict[str, bool] = {}
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for line in body:
        item = CHECKLIST.match(line)
        if item:
            current = item.group(2)
            if current in tasks:
                r.err(path, f"duplicate task {current}")
            tasks[current] = item.group(1) != " "
            fields.setdefault(current, [])
        elif current and line[:1] in (" ", "\t"):
            fields[current].append(line.strip())
        elif line.strip():
            current = None
    if not v4:
        return tasks
    for tid, lines in fields.items():
        if not tid.startswith(pid + "-"):
            r.err(path, f"task {tid} does not belong to {pid}")
        if tid.endswith("-T00"):
            r.err(path, f"{tid}: number tasks from T01; never carry work into a phase as T00")
        if not any(line.startswith("Done when:") for line in lines):
            r.err(path, f"{tid} needs an indented 'Done when:' line")
    if len(tasks) > MAX_TASKS:
        r.warn(path, f"{len(tasks)} tasks; a phase is 8 tasks or fewer plus one review fix task, so split it")
    return tasks


def check_v4(plan: Plan, found: dict[str, list[str]], has_log: bool, r: Report) -> None:
    path, lines = plan.path, plan.lines
    kind = header_value(lines, "Kind")
    if kind not in KIND_SECTIONS:
        r.err(path, "needs 'Kind: feature' or 'Kind: fix'")
    for name in HEADER_LINES:
        if header_value(lines, name) is None:
            r.err(path, f"needs a '{name}:' line")
    for section in SECTIONS + KIND_SECTIONS.get(kind or "", []):
        if section not in found:
            r.err(path, f"missing section '## {section}'")
    if not has_log:
        r.err(path, "missing section '## Log' (the plan's last section)")
    if len(lines) > PLAN_LINES:
        r.warn(path, f"{len(lines)} lines above the Log; keep plans near 200 by stating seams and outcomes, not implementation")
    for line in lines:
        if PATH_LINE.search(line):
            r.warn(path, f"line-number reference goes stale: '{line.strip()[:60]}'")
        if BANNED_HEADING.match(line) or LETTERED.match(line):
            r.warn(path, f"use tasks (PNN-TNN), not sub-units or lettered phases: '{line.strip()[:60]}'")


def check_log(plan: Plan, log: list[str], r: Report) -> list[str]:
    """Validate '### <entry> · <date>' entries; return their kinds in order."""
    kinds: list[str] = []
    title: str | None = None
    size = 0

    def close_entry() -> None:
        if title is not None and size > ENTRY_LINES:
            r.warn(plan.path, f"log entry '{title}' is over {ENTRY_LINES} lines")

    for line in log:
        if line.startswith("## "):
            r.err(plan.path, f"'## Log' must be the last section: '{line[:60]}'")
            break
        if not line.startswith("### "):
            size += bool(line.strip())
            continue
        close_entry()
        title, size = line[4:].strip(), 0
        phase, task = LOG_PHASE.match(line), LOG_TASK.match(line)
        if phase:
            kinds.append(phase.group(1).split()[0])
        elif task:
            if task.group(1) not in plan.tasks:
                r.err(plan.path, f"log entry for unknown task {task.group(1)}")
            kinds.append(task.group(2))
        else:
            r.warn(plan.path, f"unexpected log heading '{line[:60]}'")
    close_entry()
    if kinds.count("Outcome") > 1:
        r.warn(plan.path, "more than one Outcome entry; edit the first instead")
    return kinds


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


def check_decisions(root: Path, r: Report) -> dict[str, str]:
    """Map decision ID -> heading. Legacy entries keep status in the body and skip the newer checks."""
    path = root / "docs" / "DECISIONS.md"
    if not path.is_file():
        return {}
    entries: list[tuple[str, str, list[str]]] = []
    for line in read_lines(path):
        match = DECISION.match(line)
        if match:
            entries.append((match.group(1), match.group(2), []))
        elif line.startswith("## "):
            entries.append(("", "", []))
        elif entries:
            entries[-1][2].append(line)
    out: dict[str, str] = {}
    for did, heading, body in entries:
        if not did:
            continue
        if did in out:
            r.err(path, f"duplicate decision {did}")
        out[did] = heading
        if DECISION_STATUS.search(heading):
            size = len([x for x in body if x.strip()])
            if size > ENTRY_LINES:
                r.warn(path, f"{did} is {size} lines; keep entries to {ENTRY_LINES}")
            if not any(x.startswith("Rejected:") for x in body):
                r.warn(path, f"{did} needs a 'Rejected:' line (a choice with no viable alternative isn't a decision)")
        elif not any(DECISION_STATUS.search(x) for x in body if "status" in x.lower()):
            r.err(path, f"{did} heading needs a status: proposed, accepted, or superseded by DNNN")
    return out


def cross_check(root: Path, phases: dict[str, tuple[str, str | None]], plans: dict[str, Plan],
                decisions: dict[str, str], r: Report) -> None:
    roadmap = root / "docs" / "ROADMAP.md"
    for pid, plan in plans.items():
        if pid not in phases:
            r.err(plan.path, f"{pid} is not listed in docs/ROADMAP.md")
            continue
        status = phases[pid][0]
        open_tasks = sum(1 for done in plan.tasks.values() if not done)
        all_done = bool(plan.tasks) and not open_tasks
        if status in NEEDS_APPROVAL and plan.approved is None:
            r.err(roadmap, f"{pid} is {status} but its plan says 'Approved: pending'")
        if status in ALL_TASKS_DONE and open_tasks:
            r.err(roadmap, f"{pid} is {status} but {open_tasks} task(s) are unchecked")
        if status == "planned" and plan.approved is not None:
            r.warn(roadmap, f"{pid} plan is approved but ROADMAP still says planned")
        if plan.v4:
            if status in ALL_TASKS_DONE and "Review" not in plan.log:
                r.err(plan.path, f"{pid} is {status} but its Log has no Review entry (a waived review is recorded as one)")
            if "Outcome" in plan.log and status not in ALL_TASKS_DONE:
                r.err(roadmap, f"{pid} has an Outcome entry but ROADMAP says {status}")
            if status == "approved" and all_done and "Ready" not in plan.log:
                r.warn(plan.path, f"{pid} has every task checked but no 'Ready for review' entry")
        elif status == "approved" and all_done:
            r.warn(roadmap, f"{pid} has every task checked but ROADMAP still says approved")
    for did, heading in decisions.items():
        match = PROPOSED_FOR.search(heading)
        if match and phases.get(match.group(1), ("",))[0] in ALL_TASKS_DONE:
            r.warn(root / "docs" / "DECISIONS.md", f"{did} is still proposed but {match.group(1)} is built; mark it accepted")


def check_citations(root: Path, phases: dict[str, tuple[str, str | None]], plans: dict[str, Plan],
                    decisions: dict[str, str], invariants: set[str], specs: dict[str, set[str]], r: Report) -> None:
    """Plans not yet built may cite only IDs, specs, and rules that exist."""
    for pid, plan in plans.items():
        if not plan.v4 or phases.get(pid, ("",))[0] not in ACTIVE:
            continue
        missing: set[str] = set()
        for line in plan.lines:
            for cited in CITED_ID.findall(line):
                known = decisions if cited.startswith("D") else invariants
                if cited not in known:
                    missing.add(cited)
            for slug, rule in TAG.findall(line):
                if slug not in specs:
                    r.err(plan.path, f"[{slug} {rule}] names no spec docs/specs/{slug}.md")
                elif rule != "new" and rule not in specs[slug]:
                    r.err(plan.path, f"[{slug} {rule}]: docs/specs/{slug}.md has no rule {rule}")
            for slug, rule in SPEC_CITE.findall(line):
                if slug in specs and rule not in specs[slug] and f"[{slug} {rule}]" not in line:
                    r.err(plan.path, f"cites {slug} {rule}, which docs/specs/{slug}.md does not have")
            for other in OTHER_PLAN_C.findall(line):
                if other != pid:
                    r.warn(plan.path, f"cites {other}'s requirements; cite the spec rule instead (write the spec if there is none)")
        for cited in sorted(missing):
            home = "docs/DECISIONS.md" if cited.startswith("D") else "docs/ARCHITECTURE.md invariants"
            r.err(plan.path, f"cites {cited}, which is not in {home}")
        for item in (header_value(plan.lines, "Read") or "").split(","):
            item = item.strip()
            if re.fullmatch(SLUG, item) and item not in specs:
                r.err(plan.path, f"Read: '{item}' names no spec docs/specs/{item}.md")


def check_legacy(root: Path, r: Report) -> None:
    legacy = [root / "docs" / "phases", root / "docs" / "plan", root / "docs" / "PLAN.md"]
    legacy += sorted(root.glob("phase*.md"))
    for path in legacy:
        if path.exists():
            r.warn(path, "legacy plan location; see references/foundations.md (archive under docs/archive/)")


def lint(root: Path) -> Report:
    r = Report(root)
    check_agents(root, r)
    invariants = check_architecture(root, r)
    specs = check_specs(root, r)
    spec_files = sorted((root / "docs" / "specs").glob("*.md"))
    check_paths(root, [root / "AGENTS.md", root / "docs" / "ARCHITECTURE.md", *spec_files], r)
    phases = check_roadmap(root, r)
    plans = check_plans(root, r)
    decisions = check_decisions(root, r)
    cross_check(root, phases, plans, decisions, r)
    check_citations(root, phases, plans, decisions, invariants, specs, r)
    check_legacy(root, r)
    r.summary = summary(phases, plans)
    return r


def summary(phases: dict[str, tuple[str, str | None]], plans: dict[str, Plan]) -> list[str]:
    out = []
    for pid, (status, _) in phases.items():
        plan = plans.get(pid)
        line = f"{pid} {status}"
        if plan:
            line += f" {sum(plan.tasks.values())}/{len(plan.tasks)} tasks"
            last = plan.log[-1] if plan.log else ""
            if status == "approved" and last in ("Ready", "blocked"):
                line += ", ready for review" if last == "Ready" else ", blocked"
        out.append(line)
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
