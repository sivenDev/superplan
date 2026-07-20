#!/usr/bin/env python3
"""Detect whether the required Superpowers skills are installed."""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


INSTALL_URL = "https://github.com/obra/superpowers"
SCRIPTS_DIR = Path(__file__).resolve().parent
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


@dataclass(frozen=True)
class CheckResult:
    skills_dir: Path | None
    missing: tuple[str, ...]
    searched: tuple[Path, ...]
    profile: str | None = None
    revision: str | None = None
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.skills_dir is not None and not self.missing and not self.errors


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
        home / ".agents" / "skills",
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


def missing_skills(
    skills_dir: Path, required_skills: tuple[str, ...] = REQUIRED_SKILLS
) -> tuple[str, ...]:
    return tuple(
        name
        for name in required_skills
        if not (skills_dir / name / "SKILL.md").is_file()
    )


def _manifest_path(state_root: Path) -> Path:
    profiles = _load("superpowers_profiles")
    return state_root.expanduser().resolve() / profiles.MANIFEST_FILENAME


def _read_manifest(path: Path) -> tuple[dict[str, object] | None, tuple[str, ...]]:
    if not path.is_file():
        return None, (f"Active profile manifest not found: {path}",)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, (f"Invalid active profile manifest {path}: {exc}",)
    if not isinstance(data, dict):
        return None, (f"Invalid active profile manifest {path}: expected an object",)
    return data, ()


def _check_profile_installation(
    *,
    profile: object,
    model: str | None,
    state_root: Path,
    skills_dirs: list[Path] | None,
    superpowers_roots: list[Path] | None,
    include_defaults: bool,
) -> CheckResult:
    profiles = _load("superpowers_profiles")
    manifest_path = _manifest_path(state_root)
    manifest, read_errors = _read_manifest(manifest_path)
    searched = tuple(
        candidate_skills_dirs(
            skills_dirs=skills_dirs,
            superpowers_roots=superpowers_roots,
            include_defaults=include_defaults,
        )
    )
    if manifest is None:
        return CheckResult(
            skills_dir=None,
            missing=tuple(profile.skills),
            searched=searched,
            profile=profile.name,
            revision=profile.revision,
            errors=read_errors,
        )

    errors: list[str] = []
    installations = tuple(
        path
        for path in searched
        if (path / "using-superpowers" / "SKILL.md").is_file()
    )
    if len(installations) > 1:
        rendered = ", ".join(str(path) for path in installations)
        errors.append(f"Multiple Superpowers installations detected: {rendered}")
    if manifest.get("schema_version") != profiles.MANIFEST_SCHEMA_VERSION:
        errors.append("manifest schema version mismatch")
    if manifest.get("profile") != profile.name:
        errors.append(
            f"manifest profile mismatch: expected {profile.name}, got {manifest.get('profile')}"
        )
    manifest_model = manifest.get("model")
    if not isinstance(manifest_model, str) or not profile.matches_model(manifest_model):
        errors.append(f"manifest model is not supported by {profile.name}: {manifest_model}")
    elif model is not None and manifest_model != model:
        errors.append(f"manifest model mismatch: expected {model}, got {manifest_model}")
    if manifest.get("repository") != profile.repository:
        errors.append("manifest repository mismatch")
    if manifest.get("revision") != profile.revision:
        errors.append(
            f"manifest revision mismatch: expected {profile.revision}, got {manifest.get('revision')}"
        )

    raw_skills_dir = manifest.get("skills_dir")
    if not isinstance(raw_skills_dir, str) or not raw_skills_dir:
        skills_dir = None
        errors.append("manifest skills_dir is missing")
    else:
        skills_dir = Path(raw_skills_dir).expanduser().resolve()

    if skills_dir is not None and skills_dirs:
        explicit = {path.expanduser().resolve() for path in skills_dirs}
        if skills_dir not in explicit:
            errors.append(
                f"manifest skills directory {skills_dir} is not one of the explicit --skills-dir paths"
            )

    raw_source_dir = manifest.get("source_dir")
    source_dir = (
        Path(raw_source_dir).expanduser().resolve()
        if isinstance(raw_source_dir, str) and raw_source_dir
        else None
    )
    if source_dir is None or not source_dir.is_dir():
        errors.append(f"manifest source directory is missing: {raw_source_dir}")

    raw_links = manifest.get("skills")
    links = raw_links if isinstance(raw_links, dict) else {}
    if set(links) != set(profile.skills):
        errors.append("manifest skill inventory mismatch")

    missing = missing_skills(skills_dir, profile.skills) if skills_dir else tuple(profile.skills)
    if skills_dir is not None and source_dir is not None:
        source_skills = source_dir / "skills" / "superpowers"
        for name in profile.skills:
            target = skills_dir / name
            expected_source = (source_skills / name).resolve()
            recorded_source = links.get(name)
            if recorded_source != str(expected_source):
                errors.append(f"manifest source mismatch for {name}")
            if not target.is_symlink() or target.resolve() != expected_source:
                errors.append(f"link target mismatch for {name}: {target}")

    return CheckResult(
        skills_dir=skills_dir,
        missing=missing,
        searched=searched,
        profile=profile.name,
        revision=profile.revision,
        errors=tuple(errors),
    )


def check_installation(
    *,
    skills_dirs: list[Path] | None = None,
    superpowers_roots: list[Path] | None = None,
    include_defaults: bool = True,
    profile_name: str | None = None,
    model: str | None = None,
    state_root: Path | None = None,
) -> CheckResult:
    profiles = _load("superpowers_profiles")
    resolved_state_root = state_root or (Path.home() / ".superplan")
    manifest_exists = _manifest_path(resolved_state_root).is_file()
    profile = profiles.resolve_profile(profile_name=profile_name, model=model)
    if profile is None and manifest_exists:
        manifest, errors = _read_manifest(_manifest_path(resolved_state_root))
        if manifest is None:
            return CheckResult(None, REQUIRED_SKILLS, (), errors=errors)
        manifest_profile = manifest.get("profile")
        manifest_model = manifest.get("model")
        profile = profiles.resolve_profile(
            profile_name=manifest_profile if isinstance(manifest_profile, str) else None,
            model=manifest_model if isinstance(manifest_model, str) else None,
        )
        model = manifest_model if isinstance(manifest_model, str) else None
    if profile is not None:
        return _check_profile_installation(
            profile=profile,
            model=model,
            state_root=resolved_state_root,
            skills_dirs=skills_dirs,
            superpowers_roots=superpowers_roots,
            include_defaults=include_defaults,
        )

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
        if result.profile is not None:
            return (
                f"Superpowers profile {result.profile} found: {result.skills_dir}\n"
                f"Revision: {result.revision}"
            )
        return f"Superpowers installation found: {result.skills_dir}"

    install_url = INSTALL_URL
    if result.profile == "gpt56":
        install_url = _load("superpowers_profiles").GPT56_REPOSITORY
    lines = [
        "Superpowers is required before using Superplan.",
        f"Install superpowers first: {install_url}",
        "",
    ]
    if result.errors:
        lines.append("Profile validation failed:")
        for error in result.errors:
            lines.append(f"- {error}")
        lines.append("")
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
