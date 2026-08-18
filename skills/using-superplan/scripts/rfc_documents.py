"""Parse and validate optional feature RFC documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from human_registry import valid_date


FEATURE_ID_PATTERN = re.compile(r"^F\d{3,}(?:@[A-Za-z0-9._-]+)?$")
DIRECTORY_FILENAME_PATTERN = re.compile(
    r"^(?P<sequence>\d{2,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
RFC_STATUSES = {"draft", "approved"}
RFC_SOURCE = "docs/superplan/human/features.md"
REQUIRED_KEYS = {"id", "title", "status", "version", "source", "created"}


@dataclass(frozen=True)
class RFCDocument:
    id: str
    feature_id: str
    layout: str
    sequence: int | None
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


def validate_shared_metadata(path: Path, metadata: dict[str, str]) -> None:
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


def load_rfc(path: Path, rfc_dir: Path) -> RFCDocument:
    metadata = parse_frontmatter(path)
    is_flat = path.parent == rfc_dir
    required_keys = REQUIRED_KEYS if is_flat else REQUIRED_KEYS | {"feature"}
    missing = sorted(required_keys - metadata.keys())
    if missing:
        raise ValueError(f"{path}: missing metadata keys: {', '.join(missing)}")

    rfc_id = metadata["id"]
    if is_flat:
        if FEATURE_ID_PATTERN.fullmatch(rfc_id) is None:
            raise ValueError(f"{path}: invalid feature RFC id '{rfc_id}'")
        if path.stem != rfc_id:
            raise ValueError(f"{path}: RFC filename must match id '{rfc_id}'")
        feature_id = rfc_id
        layout = "flat"
        sequence = None
    else:
        feature_id = path.parent.name
        if FEATURE_ID_PATTERN.fullmatch(feature_id) is None:
            raise ValueError(f"{path}: invalid RFC feature directory '{feature_id}'")
        if metadata["feature"] != feature_id:
            raise ValueError(
                f"{path}: RFC feature must match directory '{feature_id}', "
                f"got '{metadata['feature']}'"
            )
        filename_match = DIRECTORY_FILENAME_PATTERN.fullmatch(path.name)
        if filename_match is None:
            raise ValueError(
                f"{path}: directory RFC filename must match NN-<slug>.md"
            )
        sequence_text = filename_match.group("sequence")
        sequence = int(sequence_text)
        if sequence < 1:
            raise ValueError(f"{path}: directory RFC sequence must be positive")
        expected_id = f"{feature_id}-R{sequence_text}"
        if rfc_id != expected_id:
            raise ValueError(
                f"{path}: directory RFC id must be '{expected_id}', got '{rfc_id}'"
            )
        layout = "directory"

    validate_shared_metadata(path, metadata)

    return RFCDocument(
        id=rfc_id,
        feature_id=feature_id,
        layout=layout,
        sequence=sequence,
        title=metadata["title"],
        status=metadata["status"],
        version=int(metadata["version"]),
        source=metadata["source"],
        created=metadata["created"],
        path=path,
    )


def discover_rfcs(root: Path) -> list[RFCDocument]:
    rfc_dir = root / "docs" / "superplan" / "rfcs"
    if not rfc_dir.exists():
        return []
    paths = sorted(rfc_dir.rglob("*.md"))
    too_deep = [
        path
        for path in paths
        if path.parent != rfc_dir and path.parent.parent != rfc_dir
    ]
    if too_deep:
        raise ValueError(
            f"{too_deep[0]}: RFC documents must use "
            "docs/superplan/rfcs/<feature-id>.md or "
            "docs/superplan/rfcs/<feature-id>/NN-<slug>.md"
        )

    flat_features = {path.stem for path in paths if path.parent == rfc_dir}
    directory_features = {path.parent.name for path in paths if path.parent != rfc_dir}
    conflicts = sorted(flat_features & directory_features)
    if conflicts:
        feature_id = conflicts[0]
        raise ValueError(
            f"{rfc_dir / f'{feature_id}.md'} and {rfc_dir / feature_id}: "
            f"feature '{feature_id}' cannot mix flat and directory RFC layouts"
        )

    documents = [load_rfc(path, rfc_dir) for path in paths]
    by_id: dict[str, RFCDocument] = {}
    for document in documents:
        previous = by_id.get(document.id)
        if previous is not None:
            raise ValueError(
                f"duplicate RFC id '{document.id}': {previous.path} and {document.path}"
            )
        by_id[document.id] = document
    return documents
