"""Canonical parsing and validation for Superplan human request registries."""

from __future__ import annotations

import datetime
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


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


def load_kind(root: Path, kind: str) -> tuple[Path, str, list[HumanRequest], list[str]]:
    path = human_path(root, kind)
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    entries, issues = parse_registry(content, kind)
    return path, content, entries, issues
