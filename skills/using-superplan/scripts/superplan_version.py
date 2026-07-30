#!/usr/bin/env python3
"""Runtime version contract for Superplan workspaces."""

from __future__ import annotations


SUPERPLAN_VERSION = "0.2.0"
WORKSPACE_SCHEMA_VERSION = 1


def workspace_marker(*, generated_by: str = SUPERPLAN_VERSION) -> str:
    return (
        "<!-- superplan-workspace: "
        f"schema={WORKSPACE_SCHEMA_VERSION}; generated-by={generated_by} -->"
    )
