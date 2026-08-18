"""Parse and validate optional feature RFC documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from human_registry import valid_date


RFC_ID_PATTERN = re.compile(r"^F\d{3,}(?:@[A-Za-z0-9._-]+)?$")
RFC_STATUSES = {"draft", "approved"}
RFC_SOURCE = "docs/superplan/human/features.md"
REQUIRED_KEYS = {"id", "title", "status", "version", "source", "created"}


@dataclass(frozen=True)
class RFCDocument:
    id: str
    title: str
    status: str
    version: int
    source: str
    created: str
    path: Path


def parse_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    end = content.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")

    metadata: dict[str, str] = {}
    for raw_line in content[4:end].splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid metadata line '{raw_line}'")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{path}: empty metadata key")
        if key in metadata:
            raise ValueError(f"{path}: duplicate metadata key '{key}'")
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        metadata[key] = value
    return metadata


def load_rfc(path: Path) -> RFCDocument:
    metadata = parse_frontmatter(path)
    missing = sorted(REQUIRED_KEYS - metadata.keys())
    if missing:
        raise ValueError(f"{path}: missing metadata keys: {', '.join(missing)}")

    rfc_id = metadata["id"]
    if RFC_ID_PATTERN.fullmatch(rfc_id) is None:
        raise ValueError(f"{path}: invalid feature RFC id '{rfc_id}'")
    if path.stem != rfc_id:
        raise ValueError(f"{path}: RFC filename must match id '{rfc_id}'")
    if not metadata["title"].strip():
        raise ValueError(f"{path}: RFC title must not be empty")
    if metadata["status"] not in RFC_STATUSES:
        raise ValueError(
            f"{path}: unknown RFC status '{metadata['status']}', expected draft or approved"
        )
    version_text = metadata["version"]
    if not version_text.isdigit() or int(version_text) < 1:
        raise ValueError(f"{path}: RFC version must be a positive integer")
    if metadata["source"] != RFC_SOURCE:
        raise ValueError(f"{path}: RFC source must be '{RFC_SOURCE}'")
    if not valid_date(metadata["created"]):
        raise ValueError(f"{path}: invalid RFC created '{metadata['created']}'")

    return RFCDocument(
        id=rfc_id,
        title=metadata["title"],
        status=metadata["status"],
        version=int(version_text),
        source=metadata["source"],
        created=metadata["created"],
        path=path,
    )


def discover_rfcs(root: Path) -> list[RFCDocument]:
    rfc_dir = root / "docs" / "superplan" / "rfcs"
    if not rfc_dir.exists():
        return []
    paths = sorted(rfc_dir.rglob("*.md"))
    nested = [path for path in paths if path.parent != rfc_dir]
    if nested:
        raise ValueError(f"{nested[0]}: RFC documents must use docs/superplan/rfcs/<feature-id>.md")
    return [load_rfc(path) for path in paths]
