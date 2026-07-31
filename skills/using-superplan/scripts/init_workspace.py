#!/usr/bin/env python3
"""Initialize, check, or migrate a Superplan workspace without external setup."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from safe_writes import TextUpdate, commit_text_updates, workspace_lock
from superplan_version import SUPERPLAN_VERSION, WORKSPACE_SCHEMA_VERSION
from workspace_paths import resolve_initialization_root


SCRIPTS_DIR = Path(__file__).resolve().parent
HUMAN_ASSETS_DIR = SCRIPTS_DIR.parent / "assets" / "human"
HUMAN_FILES = ("prd.md", "features.md", "bugs.md")

CHECK_CURRENT = 0
CHECK_MIGRATION_REQUIRED = 1
CHECK_NEWER_SCHEMA = 2
CHECK_MALFORMED = 3

WORKSPACE_MARKER_PREFIX = "<!-- superplan-workspace:"
WORKSPACE_MARKER_RE = re.compile(
    r"<!-- superplan-workspace: schema=(?P<schema>\d+); "
    r"generated-by=(?P<version>[0-9A-Za-z.+-]+) -->"
)


@dataclass(frozen=True)
class WorkspaceCheck:
    code: int
    message: str
    initialized: bool


def _load(name: str) -> ModuleType:
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def human_doc_updates(root: Path) -> list[TextUpdate]:
    updates: list[TextUpdate] = []
    human_dir = root / "docs" / "superplan" / "human"
    for filename in HUMAN_FILES:
        path = human_dir / filename
        if not path.exists():
            updates.append(
                TextUpdate(
                    path=path,
                    original=None,
                    updated=(HUMAN_ASSETS_DIR / filename).read_text(encoding="utf-8"),
                )
            )
    return updates


def _normalized_generator_marker(text: str) -> str:
    return WORKSPACE_MARKER_RE.sub(
        lambda match: (
            "<!-- superplan-workspace: "
            f"schema={match.group('schema')}; generated-by=<compatible> -->"
        ),
        text,
    )


def _plans_index_is_current(root: Path) -> bool:
    readme = _load("generate_plans_readme")
    plans_dir = root / "docs" / "superplan" / "plans"
    readme_path = plans_dir / "README.md"
    if not readme_path.exists():
        return False
    try:
        generated = readme.generate_readme(root, plans_dir)
    except (OSError, ValueError):
        return False
    return readme_path.read_text(encoding="utf-8") == generated


def inspect_workspace(root: Path) -> WorkspaceCheck:
    sync = _load("sync_agents_guardrails")
    agents_path = root / "AGENTS.md"
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    initialized = (
        (root / "docs" / "superplan").exists()
        or sync.START_MARKER in existing
        or sync.END_MARKER in existing
    )

    if not initialized:
        return WorkspaceCheck(
            CHECK_MIGRATION_REQUIRED,
            "workspace is not initialized",
            False,
        )

    if (sync.START_MARKER in existing) != (sync.END_MARKER in existing):
        return WorkspaceCheck(
            CHECK_MALFORMED,
            "AGENTS.md contains an incomplete managed guardrail block",
            True,
        )

    matches = list(WORKSPACE_MARKER_RE.finditer(existing))
    if not matches:
        if WORKSPACE_MARKER_PREFIX in existing:
            return WorkspaceCheck(
                CHECK_MALFORMED,
                "workspace version marker is malformed",
                True,
            )
        return WorkspaceCheck(
            CHECK_MIGRATION_REQUIRED,
            "workspace schema is missing; run with --migrate",
            True,
        )
    if len(matches) != 1:
        return WorkspaceCheck(
            CHECK_MALFORMED,
            "workspace contains multiple version markers",
            True,
        )

    schema = int(matches[0].group("schema"))
    generated_by = matches[0].group("version")
    if schema > WORKSPACE_SCHEMA_VERSION:
        return WorkspaceCheck(
            CHECK_NEWER_SCHEMA,
            (
                f"workspace schema {schema} is newer than supported schema "
                f"{WORKSPACE_SCHEMA_VERSION}; install a newer Superplan"
            ),
            True,
        )
    if schema < WORKSPACE_SCHEMA_VERSION:
        return WorkspaceCheck(
            CHECK_MIGRATION_REQUIRED,
            (
                f"workspace schema {schema} is older than supported schema "
                f"{WORKSPACE_SCHEMA_VERSION}; run with --migrate"
            ),
            True,
        )

    try:
        expected = sync.render_synced(existing, sync.load_asset())
    except ValueError as exc:
        return WorkspaceCheck(CHECK_MALFORMED, str(exc), True)
    if _normalized_generator_marker(existing) != _normalized_generator_marker(expected):
        return WorkspaceCheck(
            CHECK_MIGRATION_REQUIRED,
            "managed workspace artifacts are stale; run with --migrate",
            True,
        )

    missing_human = [
        name
        for name in HUMAN_FILES
        if not (root / "docs" / "superplan" / "human" / name).exists()
    ]
    if missing_human or not _plans_index_is_current(root):
        return WorkspaceCheck(
            CHECK_MIGRATION_REQUIRED,
            "generated workspace artifacts are missing or stale; run with --migrate",
            True,
        )

    suffix = ""
    if generated_by != SUPERPLAN_VERSION:
        suffix = (
            f" (generated by {generated_by}; current plugin {SUPERPLAN_VERSION}; "
            "schema compatible)"
        )
    return WorkspaceCheck(CHECK_CURRENT, f"workspace schema {schema} is current{suffix}", True)


def _write_workspace(root: Path) -> int:
    sync = _load("sync_agents_guardrails")
    readme = _load("generate_plans_readme")
    try:
        with workspace_lock(root):
            agents_path = root / "AGENTS.md"
            existing_agents = (
                agents_path.read_text(encoding="utf-8") if agents_path.exists() else None
            )
            plans_dir = root / "docs" / "superplan" / "plans"
            readme_path = plans_dir / "README.md"
            existing_readme = (
                readme_path.read_text(encoding="utf-8") if readme_path.exists() else None
            )
            synced_agents = sync.render_synced(existing_agents or "", sync.load_asset())
            generated_readme = readme.generate_readme(root, plans_dir)
            human_updates = human_doc_updates(root)
            updates = [
                *human_updates,
                TextUpdate(agents_path, existing_agents, synced_agents),
                TextUpdate(readme_path, existing_readme, generated_readme),
            ]
            commit_text_updates(updates)
    except (OSError, ValueError) as exc:
        print(f"workspace migration preflight failed: {exc}")
        return CHECK_MALFORMED

    created_docs = [update.path.as_posix() for update in human_updates]
    agents_state = "updated" if synced_agents != existing_agents else "unchanged"
    plans_state = "updated" if generated_readme != existing_readme else "unchanged"

    print(f"root: {root}")
    if created_docs:
        for path in created_docs:
            print(f"created {path}")
    else:
        print("human docs: already present")
    print(f"AGENTS.md: {agents_state}")
    print(f"docs/superplan/plans/README.md: {plans_state}")
    return 0


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(resolve_initialization_root(Path.cwd())),
        help="Repository root. Defaults to the Git top-level, an existing Superplan ancestor, or the current directory.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Check workspace compatibility without writing")
    mode.add_argument("--migrate", action="store_true", help="Safely refresh managed and generated workspace artifacts")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    check = inspect_workspace(root)
    if args.check:
        print(check.message)
        return check.code

    if check.code in (CHECK_NEWER_SCHEMA, CHECK_MALFORMED):
        print(check.message)
        return check.code
    if check.initialized and check.code == CHECK_MIGRATION_REQUIRED and not args.migrate:
        print(check.message)
        return check.code

    return _write_workspace(root)


if __name__ == "__main__":
    raise SystemExit(run())
