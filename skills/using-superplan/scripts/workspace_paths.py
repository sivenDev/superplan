#!/usr/bin/env python3
"""Resolve Superplan workspace roots consistently."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_top_level(start: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).resolve()


def existing_superplan_ancestor(start: Path) -> Path | None:
    resolved = start.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / "docs" / "superplan").is_dir():
            return candidate
    return None


def resolve_existing_workspace(start: Path) -> Path:
    resolved = start.resolve()
    root = git_top_level(resolved) or existing_superplan_ancestor(resolved)
    if root is None:
        raise ValueError(f"unable to locate Superplan workspace from {resolved}")
    return root


def resolve_initialization_root(start: Path) -> Path:
    resolved = start.resolve()
    return git_top_level(resolved) or existing_superplan_ancestor(resolved) or resolved
