#!/usr/bin/env python3
"""Compatibility entry point for recording a Superplan human request."""

from human_requests import (
    CONFIG,
    ENTRY_PATTERN,
    INITIAL_STATUSES as HUMAN_STATUSES,
    append_entry,
    branch_slug,
    git_output,
    human_path,
    id_qualifier,
    is_linked_worktree,
    next_id,
    normalize_body_text,
    render_entry,
    resolve_git_path,
    run_record_compat,
)


def run(argv: list[str] | None = None) -> int:
    return run_record_compat(argv)


if __name__ == "__main__":
    raise SystemExit(run())
