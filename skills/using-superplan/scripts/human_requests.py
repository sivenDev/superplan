#!/usr/bin/env python3
"""Inspect, validate, record, and update Superplan human requests."""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import generate_plans_readme as plan_index
from workspace_paths import resolve_existing_workspace


CONFIG = {
    "feature": {"filename": "features.md", "prefix": "F", "heading": "# Features"},
    "bug": {"filename": "bugs.md", "prefix": "B", "heading": "# Bugs"},
}
INITIAL_STATUSES = ("proposed", "accepted")
HUMAN_STATUSES = ("proposed", "accepted", "done")
ACTIVE_STATUSES = ("proposed", "accepted")
STATUS_TRANSITIONS = {
    "proposed": "accepted",
    "accepted": "done",
    "done": None,
}
ENTRY_PATTERN = re.compile(
    r"^##\s+([FB])(\d+)(@[A-Za-z0-9._-]+)?:\s*(.*)$",
    re.MULTILINE,
)
STATUS_PATTERN = re.compile(r"^- status:\s*(\S+)\s*$", re.MULTILINE)
CREATED_PATTERN = re.compile(r"^- created:\s*(\S+)\s*$", re.MULTILINE)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class HumanRequest:
    request_id: str
    title: str
    status: str | None
    created: str | None
    raw: str
    start: int
    end: int
    status_span: tuple[int, int] | None


def valid_date(value: str) -> bool:
    if DATE_PATTERN.fullmatch(value) is None:
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def human_path(root: Path, kind: str) -> Path:
    return root / "docs" / "superplan" / "human" / CONFIG[kind]["filename"]


def parse_registry(content: str, kind: str) -> tuple[list[HumanRequest], list[str]]:
    matches = list(ENTRY_PATTERN.finditer(content))
    prefix = CONFIG[kind]["prefix"]
    filename = CONFIG[kind]["filename"]
    entries: list[HumanRequest] = []
    issues: list[str] = []
    counts: Counter[str] = Counter()

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        raw = content[start:end].rstrip("\n")
        request_id = f"{match.group(1)}{match.group(2)}{match.group(3) or ''}"
        title = match.group(4).strip()
        counts[request_id] += 1
        if match.group(1) != prefix:
            issues.append(f"{filename}: {request_id}: wrong id prefix for {kind}")
        if not title:
            issues.append(f"{filename}: {request_id}: missing title")

        status_matches = list(STATUS_PATTERN.finditer(raw))
        created_matches = list(CREATED_PATTERN.finditer(raw))
        status = status_matches[0].group(1) if len(status_matches) == 1 else None
        created = created_matches[0].group(1) if len(created_matches) == 1 else None
        status_span = None
        if len(status_matches) == 1:
            value_start, value_end = status_matches[0].span(1)
            status_span = (start + value_start, start + value_end)
        elif not status_matches:
            issues.append(f"{filename}: {request_id}: missing status")
        else:
            issues.append(f"{filename}: {request_id}: multiple status fields")
        if status is not None and status not in HUMAN_STATUSES:
            issues.append(f"{filename}: {request_id}: unknown status '{status}'")

        if not created_matches:
            issues.append(f"{filename}: {request_id}: missing created")
        elif len(created_matches) > 1:
            issues.append(f"{filename}: {request_id}: multiple created fields")
        elif created is not None and not valid_date(created):
            issues.append(f"{filename}: {request_id}: invalid created '{created}'")

        entries.append(
            HumanRequest(
                request_id=request_id,
                title=title,
                status=status,
                created=created,
                raw=raw,
                start=start,
                end=end,
                status_span=status_span,
            )
        )

    for request_id, count in sorted(counts.items()):
        if count > 1:
            issues.append(f"{filename}: duplicate id {request_id} ({count} entries)")
    return entries, issues


def next_id(content: str, prefix: str) -> str:
    numbers = [
        int(match.group(2))
        for match in ENTRY_PATTERN.finditer(content)
        if match.group(1) == prefix
    ]
    value = max(numbers, default=0) + 1
    return f"{prefix}{value:03d}"


def git_output(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def resolve_git_path(root: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else root / path).resolve()


def is_linked_worktree(root: Path) -> bool:
    git_dir = git_output(root, "rev-parse", "--git-dir")
    git_common = git_output(root, "rev-parse", "--git-common-dir")
    if not git_dir or not git_common:
        return False
    if git_output(root, "rev-parse", "--show-superproject-working-tree"):
        return False
    return resolve_git_path(root, git_dir) != resolve_git_path(root, git_common)


def branch_slug(root: Path) -> str:
    name = git_output(root, "branch", "--show-current") or git_output(
        root, "rev-parse", "--short", "HEAD"
    )
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name or "detached")
    slug = re.sub(r"-+", "-", slug).strip("-._") or "detached"
    if re.search(r"-\d+$", slug):
        slug = f"{slug}-branch"
    return slug


def id_qualifier(root: Path) -> str:
    return f"@{branch_slug(root)}" if is_linked_worktree(root) else ""


def normalize_body_text(body: str) -> str:
    return body.replace("\\r\\n", "\n").replace("\\n", "\n")


def render_entry(
    entry_id: str,
    title: str,
    body: str | None,
    date: str,
    status: str = "proposed",
) -> str:
    lines = [
        f"## {entry_id}: {title}",
        "",
        f"- status: {status}",
        f"- created: {date}",
        "",
    ]
    body_text = normalize_body_text(body or "").strip()
    if body_text:
        lines.extend([body_text, ""])
    return "\n".join(lines).rstrip()


def append_entry(content: str, heading: str, entry: str) -> str:
    base = content.rstrip() or heading
    return base + "\n\n" + entry + "\n"


def resolve_root(raw_root: str | None) -> Path:
    return Path(raw_root).resolve() if raw_root else resolve_existing_workspace(Path.cwd())


def record_request(
    *,
    root: Path,
    kind: str,
    title: str,
    body: str,
    status: str,
    date: str,
) -> tuple[int, str]:
    clean_title = title.strip()
    if not clean_title:
        return 1, "error: --title must not be empty"
    if not valid_date(date):
        return 1, f"error: invalid date '{date}', expected YYYY-MM-DD"
    path = human_path(root, kind)
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    _, issues = parse_registry(content, kind)
    if issues:
        return 1, "registry validation failed; run human_requests.py validate"
    config = CONFIG[kind]
    entry_id = next_id(content, config["prefix"]) + id_qualifier(root)
    entry = render_entry(entry_id, clean_title, body, date, status)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(append_entry(content, config["heading"], entry), encoding="utf-8")
    return 0, entry_id


def add_record_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--type", required=True, choices=sorted(CONFIG), help="Request kind")
    parser.add_argument("--title", required=True, help="Short entry title")
    parser.add_argument("--body", default="", help="Optional description body")
    parser.add_argument(
        "--status",
        choices=INITIAL_STATUSES,
        default="proposed",
        help="Initial request status. Defaults to proposed.",
    )
    parser.add_argument(
        "--date",
        default=datetime.date.today().isoformat(),
        help="Creation date (YYYY-MM-DD). Defaults to today.",
    )


def run_record_compat(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record a new Superplan human request.")
    add_record_arguments(parser)
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the Git top-level or nearest existing Superplan ancestor.",
    )
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.root)
    except ValueError as exc:
        print(exc)
        return 1
    code, message = record_request(
        root=root,
        kind=args.type,
        title=args.title,
        body=args.body,
        status=args.status,
        date=args.date,
    )
    print(message)
    return code


def selected_kinds(kind: str) -> list[str]:
    return list(CONFIG) if kind == "all" else [kind]


def load_kind(root: Path, kind: str) -> tuple[Path, str, list[HumanRequest], list[str]]:
    path = human_path(root, kind)
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    entries, issues = parse_registry(content, kind)
    return path, content, entries, issues


def request_kind(request_id: str) -> str | None:
    if request_id.startswith("F"):
        return "feature"
    if request_id.startswith("B"):
        return "bug"
    return None


def request_completion_error(root: Path, request_id: str) -> str | None:
    plans = plan_index.discover_plans(root / "docs" / "superplan" / "plans")
    plan_index.validate_plans(plans, root)
    deliverable = [
        plan
        for plan in plans
        if plan.source_id == request_id and plan.status != "superseded"
    ]
    if not deliverable:
        return f"{request_id}: no deliverable related plans"

    blockers = [plan for plan in deliverable if plan.status != "complete"]
    if blockers:
        details = ", ".join(f"{plan.id} ({plan.status})" for plan in blockers)
        return f"{request_id}: incomplete related plans: {details}"
    return None


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the Git top-level or nearest existing Superplan ancestor.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser("summary", help="Print bounded status counts")
    summary_parser.add_argument("--type", choices=["all", *CONFIG], default="all")

    list_parser = subparsers.add_parser("list", help="List compact request metadata")
    list_parser.add_argument("--type", choices=["all", *CONFIG], default="all")
    list_parser.add_argument(
        "--status",
        choices=["active", "all", *HUMAN_STATUSES],
        default="active",
    )

    show_parser = subparsers.add_parser("show", help="Show one exact request entry")
    show_parser.add_argument("--id", required=True)

    record_parser = subparsers.add_parser("record", help="Record a request")
    add_record_arguments(record_parser)

    status_parser = subparsers.add_parser("set-status", help="Advance one request status")
    status_parser.add_argument("--id", required=True)
    status_parser.add_argument("--status", required=True, choices=HUMAN_STATUSES)

    validate_parser = subparsers.add_parser("validate", help="Validate request registries")
    validate_parser.add_argument("--type", choices=["all", *CONFIG], default="all")

    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.root)
    except ValueError as exc:
        print(exc)
        return 1

    if args.command == "record":
        code, message = record_request(
            root=root,
            kind=args.type,
            title=args.title,
            body=args.body,
            status=args.status,
            date=args.date,
        )
        print(message)
        return code

    if args.command in {"show", "set-status"}:
        kind = request_kind(args.id)
        if kind is None:
            print(f"invalid request id '{args.id}'")
            return 1
        path, content, entries, issues = load_kind(root, kind)
        matches = [entry for entry in entries if entry.request_id == args.id]
        if len(matches) != 1:
            print(f"request id '{args.id}' matched {len(matches)} entries")
            return 1
        if issues:
            relevant = issues if args.command == "set-status" else [
                issue for issue in issues if args.id in issue
            ]
            if relevant:
                print("\n".join(relevant))
                return 1
        entry = matches[0]
        if args.command == "show":
            print(entry.raw)
            return 0

        if entry.status is None or entry.status_span is None:
            print(f"{args.id}: status is missing or ambiguous")
            return 1
        if args.status != entry.status and STATUS_TRANSITIONS.get(entry.status) != args.status:
            print(f"{args.id}: invalid status transition {entry.status} -> {args.status}")
            return 1
        if entry.status == "accepted" and args.status == "done":
            try:
                completion_error = request_completion_error(root, args.id)
            except (OSError, ValueError) as exc:
                print(f"{args.id}: cannot validate related plans: {exc}")
                return 1
            if completion_error is not None:
                print(completion_error)
                return 1
        start, end = entry.status_span
        path.write_text(content[:start] + args.status + content[end:], encoding="utf-8")
        print(f"{args.id}\t{args.status}")
        return 0

    kinds = selected_kinds(args.type)
    loaded = [(kind, *load_kind(root, kind)[2:]) for kind in kinds]
    if args.command == "validate":
        issues = [issue for _, _, kind_issues in loaded for issue in kind_issues]
        if issues:
            print("\n".join(issues))
            return 1
        print(f"ok {sum(len(entries) for _, entries, _ in loaded)} requests")
        return 0

    if args.command == "summary":
        for kind, entries, issues in loaded:
            counts = Counter(entry.status for entry in entries if entry.status in HUMAN_STATUSES)
            print(
                f"{kind} total={len(entries)} proposed={counts['proposed']} "
                f"accepted={counts['accepted']} done={counts['done']} invalid={len(issues)}"
            )
        return 0

    if args.status == "all":
        statuses = set(HUMAN_STATUSES)
    elif args.status == "active":
        statuses = set(ACTIVE_STATUSES)
    else:
        statuses = {args.status}
    for _, entries, _ in loaded:
        for entry in entries:
            if entry.status in statuses:
                print(
                    f"{entry.request_id}\t{entry.status}\t{entry.created or '-'}\t{entry.title}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
