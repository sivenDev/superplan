#!/usr/bin/env python3
"""Record a new human-authored feature or bug request with stable numbering.

Appends an entry to docs/superplan/human/features.md or
docs/superplan/human/bugs.md following the numbering rule in
references/intake-spec.md. Intake only records intent; it never writes plans
or code.
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
from pathlib import Path


CONFIG = {
    "feature": {"filename": "features.md", "prefix": "F", "heading": "# Features"},
    "bug": {"filename": "bugs.md", "prefix": "B", "heading": "# Bugs"},
}

ENTRY_PATTERN = re.compile(r"^##\s+([A-Za-z])(\d+)(?:@[A-Za-z0-9._-]+)?:", re.MULTILINE)


def detect_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "docs").exists() or (candidate / ".git").exists():
            return candidate
    raise ValueError(f"unable to locate repository root from {start}")


def human_path(root: Path, kind: str) -> Path:
    return root / "docs" / "superplan" / "human" / CONFIG[kind]["filename"]


def next_id(content: str, prefix: str) -> str:
    numbers = [
        int(match.group(2))
        for match in ENTRY_PATTERN.finditer(content)
        if match.group(1).upper() == prefix
    ]
    value = (max(numbers) + 1) if numbers else 1
    return f"{prefix}{value:03d}"


def git_output(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def resolve_git_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_linked_worktree(root: Path) -> bool:
    git_dir = git_output(root, "rev-parse", "--git-dir")
    git_common = git_output(root, "rev-parse", "--git-common-dir")
    if not git_dir or not git_common:
        return False

    superproject = git_output(root, "rev-parse", "--show-superproject-working-tree")
    if superproject:
        return False

    return resolve_git_path(root, git_dir) != resolve_git_path(root, git_common)


def branch_slug(root: Path) -> str:
    name = git_output(root, "branch", "--show-current")
    if not name:
        name = git_output(root, "rev-parse", "--short", "HEAD")
    if not name:
        name = "detached"

    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name)
    slug = re.sub(r"-+", "-", slug).strip("-._")
    if not slug:
        slug = "detached"
    if re.search(r"-\d+$", slug):
        slug = f"{slug}-branch"
    return slug


def id_qualifier(root: Path) -> str:
    if not is_linked_worktree(root):
        return ""
    return f"@{branch_slug(root)}"


def normalize_body_text(body: str) -> str:
    return body.replace("\\r\\n", "\n").replace("\\n", "\n")


def render_entry(entry_id: str, title: str, body: str | None, date: str) -> str:
    lines = [
        f"## {entry_id}: {title}",
        "",
        "- status: proposed",
        f"- created: {date}",
        "",
    ]
    body_text = normalize_body_text(body or "").strip()
    if body_text:
        lines.append(body_text)
        lines.append("")
    return "\n".join(lines).rstrip()


def append_entry(content: str, heading: str, entry: str) -> str:
    base = content.rstrip()
    if not base:
        base = heading
    return base + "\n\n" + entry + "\n"


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", required=True, choices=sorted(CONFIG), help="Request kind")
    parser.add_argument("--title", required=True, help="Short entry title")
    parser.add_argument("--body", default="", help="Optional description body")
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the nearest ancestor of the current directory containing docs/ or .git.",
    )
    parser.add_argument(
        "--date",
        default=datetime.date.today().isoformat(),
        help="Creation date (YYYY-MM-DD). Defaults to today.",
    )
    args = parser.parse_args(argv)

    title = args.title.strip()
    if not title:
        print("error: --title must not be empty")
        return 1

    try:
        root = Path(args.root).resolve() if args.root else detect_repo_root(Path.cwd())
    except ValueError as exc:
        print(exc)
        return 1

    config = CONFIG[args.type]
    path = human_path(root, args.type)
    content = path.read_text(encoding="utf-8") if path.exists() else ""

    entry_id = next_id(content, config["prefix"]) + id_qualifier(root)
    entry = render_entry(entry_id, title, args.body, args.date)
    updated = append_entry(content, config["heading"], entry)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")
    print(entry_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
