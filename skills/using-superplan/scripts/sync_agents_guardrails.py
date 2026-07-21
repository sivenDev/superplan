#!/usr/bin/env python3
"""Sync managed workflow guardrails into AGENTS.md."""

from __future__ import annotations

import argparse
from pathlib import Path

from workspace_paths import resolve_existing_workspace


START_MARKER = "<!-- managed-by: superplan:start -->"
END_MARKER = "<!-- managed-by: superplan:end -->"


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def asset_path() -> Path:
    return skill_dir() / "assets" / "agents-guardrails.md"


def load_asset() -> str:
    body = asset_path().read_text(encoding="utf-8").strip()
    return f"{START_MARKER}\n{body}\n{END_MARKER}\n"


def render_synced(existing: str, managed_block: str) -> str:
    normalized_block = managed_block.strip("\n")
    if START_MARKER in existing or END_MARKER in existing:
        if START_MARKER not in existing or END_MARKER not in existing:
            raise ValueError("AGENTS.md contains only one managed marker; fix it manually first")
        start = existing.index(START_MARKER)
        end = existing.index(END_MARKER) + len(END_MARKER)
        prefix = existing[:start].strip("\n")
        suffix = existing[end:].strip("\n")
        parts: list[str] = []
        if prefix:
            parts.append(prefix)
        parts.append(normalized_block)
        if suffix:
            parts.append(suffix)
        return "\n\n".join(parts) + "\n"

    if existing.strip():
        return normalized_block + "\n\n" + existing.strip("\n") + "\n"
    return managed_block


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the Git top-level or nearest existing Superplan ancestor.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Write the managed guardrails into AGENTS.md")
    mode.add_argument("--check", action="store_true", help="Fail if AGENTS.md is missing or stale")
    args = parser.parse_args(argv)

    try:
        root = Path(args.root).resolve() if args.root else resolve_existing_workspace(Path.cwd())
    except ValueError as exc:
        print(exc)
        return 1
    agents_path = root / "AGENTS.md"
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    managed_block = load_asset()
    synced = render_synced(existing, managed_block)

    if args.write:
        agents_path.write_text(synced, encoding="utf-8")
        print(f"updated {agents_path}")
        return 0

    if args.check:
        if existing != synced:
            print(f"stale {agents_path}")
            return 1
        print(f"ok {agents_path}")
        return 0

    print(synced, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
