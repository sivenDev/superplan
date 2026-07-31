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
from human_registry import (
    ACTIVE_STATUSES,
    CONFIG,
    CREATED_PATTERN,
    ENTRY_PATTERN,
    HUMAN_STATUSES,
    INITIAL_STATUSES,
    STATUS_PATTERN,
    STATUS_TRANSITIONS,
    HumanRequest,
    human_path,
    load_kind,
    parse_registry,
    valid_date,
)
from safe_writes import TextUpdate, commit_text_updates, workspace_lock
from workspace_paths import resolve_existing_workspace


LEGACY_MISSING_ISSUE_PATTERN = re.compile(
    r"^[^:]+:\s+([FB]\d+(?:@[A-Za-z0-9._-]+)?):\s+missing\s+(status|created)$"
)


@dataclass(frozen=True)
class MigrationField:
    request_id: str
    name: str
    value: str | None
    evidence: str


@dataclass(frozen=True)
class RegistryMigration:
    path: Path
    original: str
    updated: str


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
    try:
        with workspace_lock(root):
            path = human_path(root, kind)
            original = path.read_text(encoding="utf-8") if path.exists() else None
            content = original or ""
            _, issues = parse_registry(content, kind)
            if issues:
                return (
                    1,
                    "registry validation failed; run human_requests.py validate; "
                    "for legacy missing fields, run human_requests.py migrate-legacy --check",
                )
            config = CONFIG[kind]
            entry_id = next_id(content, config["prefix"]) + id_qualifier(root)
            entry = render_entry(entry_id, clean_title, body, date, status)
            updated = append_entry(content, config["heading"], entry)
            commit_text_updates([TextUpdate(path, original, updated)])
            return 0, entry_id
    except OSError as exc:
        return 1, f"request write failed: {exc}"


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


def request_kind(request_id: str) -> str | None:
    if request_id.startswith("F"):
        return "feature"
    if request_id.startswith("B"):
        return "bug"
    return None


def request_completion_error(root: Path, request_id: str) -> str | None:
    plans = plan_index.discover_plans(root / "docs" / "superplan" / "plans")
    plan_index.validate_plans(plans, root, enforce_request_states=False)
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


def set_request_status(root: Path, request_id: str, status: str) -> tuple[int, str]:
    kind = request_kind(request_id)
    if kind is None:
        return 1, f"invalid request id '{request_id}'"
    try:
        with workspace_lock(root):
            path, content, entries, issues = load_kind(root, kind)
            matches = [entry for entry in entries if entry.request_id == request_id]
            if len(matches) != 1:
                return 1, f"request id '{request_id}' matched {len(matches)} entries"
            if issues:
                return 1, "\n".join(issues)
            entry = matches[0]
            if entry.status is None or entry.status_span is None:
                return 1, f"{request_id}: status is missing or ambiguous"
            if status != entry.status and STATUS_TRANSITIONS.get(entry.status) != status:
                return 1, f"{request_id}: invalid status transition {entry.status} -> {status}"
            if entry.status == "accepted" and status == "done":
                completion_error = request_completion_error(root, request_id)
                if completion_error is not None:
                    return 1, completion_error
            start, end = entry.status_span
            updated = content[:start] + status + content[end:]
            commit_text_updates([TextUpdate(path, content, updated)])
            return 0, f"{request_id}\t{status}"
    except (OSError, ValueError) as exc:
        return 1, f"{request_id}: status write failed: {exc}"


def is_legacy_missing_issue(issue: str) -> bool:
    return LEGACY_MISSING_ISSUE_PATTERN.fullmatch(issue) is not None


def infer_legacy_status(
    request_id: str,
    plans_by_source: dict[str, list[plan_index.PlanMetadata]],
) -> tuple[str, str]:
    deliverable = [
        plan
        for plan in plans_by_source.get(request_id, [])
        if plan.status != "superseded"
    ]
    if not deliverable:
        return "proposed", "no-deliverable-plan"
    evidence = "plans:" + ",".join(
        f"{plan.id}={plan.status}" for plan in sorted(deliverable, key=lambda item: item.id)
    )
    if all(plan.status == "complete" for plan in deliverable):
        return "done", evidence
    return "accepted", evidence


def git_first_appearance_date(root: Path, path: Path, request_id: str) -> str | None:
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None
    output = git_output(
        root,
        "log",
        "--follow",
        "--reverse",
        "--format=%as",
        f"-G^##[[:space:]]+{re.escape(request_id)}:",
        "--",
        relative,
    )
    if not output:
        return None
    candidate = output.splitlines()[0].strip()
    return candidate if valid_date(candidate) else None


def infer_legacy_created(
    *,
    root: Path,
    path: Path,
    request_id: str,
    plans_by_source: dict[str, list[plan_index.PlanMetadata]],
) -> tuple[str | None, str]:
    related = plans_by_source.get(request_id, [])
    if related:
        earliest = min(plan.created for plan in related)
        sources = ",".join(
            plan.id for plan in sorted(related, key=lambda item: item.id)
            if plan.created == earliest
        )
        return earliest, f"plan:{sources}"
    git_date = git_first_appearance_date(root, path, request_id)
    if git_date is not None:
        return git_date, "git:first-appearance"
    return None, "no-plan-or-git-evidence"


def insert_missing_metadata(
    raw: str,
    *,
    status: str | None,
    created: str | None,
) -> str:
    if status is not None and created is not None:
        heading_end = raw.find("\n")
        insertion = f"\n\n- status: {status}\n- created: {created}"
        if heading_end == -1:
            return raw + insertion
        return raw[:heading_end] + insertion + raw[heading_end:]
    if status is not None:
        created_match = CREATED_PATTERN.search(raw)
        if created_match is None:
            raise ValueError("cannot place missing status without one created field")
        return raw[: created_match.start()] + f"- status: {status}\n" + raw[created_match.start() :]
    if created is not None:
        status_match = STATUS_PATTERN.search(raw)
        if status_match is None:
            raise ValueError("cannot place missing created without one status field")
        return raw[: status_match.end()] + f"\n- created: {created}" + raw[status_match.end() :]
    return raw


def apply_entry_replacements(
    content: str,
    replacements: list[tuple[HumanRequest, str]],
) -> str:
    updated = content
    for entry, raw in sorted(replacements, key=lambda item: item[0].start, reverse=True):
        end = entry.start + len(entry.raw)
        updated = updated[: entry.start] + raw + updated[end:]
    return updated


def prepare_legacy_migration(
    root: Path,
    kinds: list[str],
) -> tuple[list[RegistryMigration], list[MigrationField], list[str]]:
    loaded = [(kind, *load_kind(root, kind)) for kind in kinds]
    blocking = [
        issue
        for _, _, _, _, issues in loaded
        for issue in issues
        if not is_legacy_missing_issue(issue)
    ]
    if blocking:
        return [], [], blocking

    affected = [
        entry
        for _, _, _, entries, _ in loaded
        for entry in entries
        if entry.status is None or entry.created is None
    ]
    if not affected:
        return [], [], []

    plans = plan_index.discover_plans(root / "docs" / "superplan" / "plans")
    plan_index.validate_plans(
        plans,
        root,
        enforce_request_states=False,
        allow_legacy_missing=True,
    )
    plans_by_source: dict[str, list[plan_index.PlanMetadata]] = {}
    for plan in plans:
        if plan.source_id:
            plans_by_source.setdefault(plan.source_id, []).append(plan)

    migrations: list[RegistryMigration] = []
    fields: list[MigrationField] = []
    for kind, path, content, entries, _ in loaded:
        replacements: list[tuple[HumanRequest, str]] = []
        for entry in entries:
            if entry.status is not None and entry.created is not None:
                continue
            status = None
            created = None
            if entry.status is None:
                status, evidence = infer_legacy_status(entry.request_id, plans_by_source)
                fields.append(MigrationField(entry.request_id, "status", status, evidence))
            if entry.created is None:
                created, evidence = infer_legacy_created(
                    root=root,
                    path=path,
                    request_id=entry.request_id,
                    plans_by_source=plans_by_source,
                )
                fields.append(MigrationField(entry.request_id, "created", created, evidence))
            if entry.created is None and created is None:
                continue
            replacements.append(
                (
                    entry,
                    insert_missing_metadata(entry.raw, status=status, created=created),
                )
            )
        updated = apply_entry_replacements(content, replacements)
        if updated != content:
            _, updated_issues = parse_registry(updated, kind)
            if updated_issues:
                raise ValueError(
                    f"{path}: migration would remain invalid: {'; '.join(updated_issues)}"
                )
            migrations.append(RegistryMigration(path, content, updated))
    return migrations, fields, []


def write_registry_migrations(migrations: list[RegistryMigration]) -> None:
    commit_text_updates(
        [
            TextUpdate(migration.path, migration.original, migration.updated)
            for migration in migrations
        ]
    )


def _run_legacy_migration(root: Path, kinds: list[str], *, write: bool) -> int:
    try:
        migrations, fields, blocking = prepare_legacy_migration(root, kinds)
    except (OSError, ValueError) as exc:
        print(f"legacy migration preflight failed: {exc}")
        return 1
    if blocking:
        print("\n".join(blocking))
        return 1
    if not fields:
        print("legacy registry is current")
        return 0

    for field in fields:
        value = field.value if field.value is not None else "unresolved"
        print(f"{field.request_id}\t{field.name}\t{value}\t{field.evidence}")
    unresolved = [field for field in fields if field.value is None]
    if unresolved:
        print("legacy migration unresolved; no files written")
        return 1

    requests = len({field.request_id for field in fields})
    if not write:
        print(f"ready {requests} requests ({len(fields)} fields)")
        return 0
    try:
        write_registry_migrations(migrations)
    except OSError as exc:
        print(f"legacy migration write failed: {exc}")
        return 1
    print(f"migrated {requests} requests ({len(fields)} fields)")
    return 0


def run_legacy_migration(root: Path, kinds: list[str], *, write: bool) -> int:
    if not write:
        return _run_legacy_migration(root, kinds, write=False)
    try:
        with workspace_lock(root):
            return _run_legacy_migration(root, kinds, write=True)
    except OSError as exc:
        print(f"legacy migration write failed: {exc}")
        return 1


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

    migrate_parser = subparsers.add_parser(
        "migrate-legacy",
        help="Preview or write missing legacy status/created metadata",
    )
    migrate_parser.add_argument("--type", choices=["all", *CONFIG], default="all")
    migrate_mode = migrate_parser.add_mutually_exclusive_group(required=True)
    migrate_mode.add_argument("--check", action="store_true", help="Preview without writing")
    migrate_mode.add_argument("--write", action="store_true", help="Write a fully resolved migration")

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

    if args.command == "migrate-legacy":
        return run_legacy_migration(
            root,
            selected_kinds(args.type),
            write=args.write,
        )

    if args.command == "set-status":
        code, message = set_request_status(root, args.id, args.status)
        print(message)
        return code

    if args.command == "show":
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
            relevant = [issue for issue in issues if args.id in issue]
            if relevant:
                print("\n".join(relevant))
                return 1
        entry = matches[0]
        print(entry.raw)
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
