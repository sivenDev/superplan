#!/usr/bin/env python3
"""Detect whether the required Superpowers skills are installed."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


INSTALL_URL = "https://github.com/obra/superpowers"
REQUIRED_SKILLS = (
    "using-superpowers",
    "brainstorming",
    "writing-plans",
    "subagent-driven-development",
    "executing-plans",
    "test-driven-development",
    "systematic-debugging",
    "verification-before-completion",
    "requesting-code-review",
    "receiving-code-review",
    "using-git-worktrees",
    "finishing-a-development-branch",
)


@dataclass(frozen=True)
class CheckResult:
    skills_dir: Path | None
    missing: tuple[str, ...]
    searched: tuple[Path, ...]

    @property
    def ok(self) -> bool:
        return self.skills_dir is not None and not self.missing


def _unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def default_search_paths() -> list[Path]:
    home = Path.home()
    return [
        home / ".codex" / "skills",
        home / ".claude" / "skills",
        home / ".codex" / "plugins",
        home / ".claude" / "plugins",
    ]


def candidate_skills_dirs(
    *,
    skills_dirs: list[Path] | None = None,
    superpowers_roots: list[Path] | None = None,
    include_defaults: bool = True,
) -> list[Path]:
    candidates: list[Path] = []
    for path in skills_dirs or []:
        candidates.append(path)
    for root in superpowers_roots or []:
        candidates.append(root / "skills")
    if include_defaults:
        for base in default_search_paths():
            candidates.append(base)
            candidates.append(base / "skills")
            if base.is_dir():
                for child in sorted(base.glob("*/skills")):
                    candidates.append(child)
    return _unique_paths(candidates)


def missing_skills(skills_dir: Path) -> tuple[str, ...]:
    return tuple(
        name
        for name in REQUIRED_SKILLS
        if not (skills_dir / name / "SKILL.md").is_file()
    )


def check_installation(
    *,
    skills_dirs: list[Path] | None = None,
    superpowers_roots: list[Path] | None = None,
    include_defaults: bool = True,
) -> CheckResult:
    searched: list[Path] = []
    best_skills_dir: Path | None = None
    best_missing: tuple[str, ...] = REQUIRED_SKILLS

    for skills_dir in candidate_skills_dirs(
        skills_dirs=skills_dirs,
        superpowers_roots=superpowers_roots,
        include_defaults=include_defaults,
    ):
        searched.append(skills_dir)
        if not (skills_dir / "using-superpowers" / "SKILL.md").is_file():
            continue

        missing = missing_skills(skills_dir)
        if not missing:
            return CheckResult(skills_dir=skills_dir, missing=(), searched=tuple(searched))
        if best_skills_dir is None or len(missing) < len(best_missing):
            best_skills_dir = skills_dir
            best_missing = missing

    return CheckResult(
        skills_dir=best_skills_dir,
        missing=best_missing,
        searched=tuple(searched),
    )


def format_result(result: CheckResult) -> str:
    if result.ok:
        return f"Superpowers installation found: {result.skills_dir}"

    lines = [
        "Superpowers is required before using Superplan.",
        f"Install superpowers first: {INSTALL_URL}",
        "",
    ]
    if result.skills_dir is not None:
        lines.append(f"Detected partial installation: {result.skills_dir}")
        lines.append("Missing required skills:")
        for name in result.missing:
            lines.append(f"- {name}")
        lines.append("")
    else:
        lines.append("No Superpowers installation was detected.")
        lines.append("")

    if result.searched:
        lines.append("Searched these locations:")
        for path in result.searched:
            lines.append(f"- {path}")
        lines.append("")

    lines.extend(
        [
            "If Superpowers is installed in a non-standard location, rerun the check with one of:",
            "  --superpowers-root /path/to/superpowers",
            "  --skills-dir /path/to/skills",
        ]
    )
    return "\n".join(lines)
