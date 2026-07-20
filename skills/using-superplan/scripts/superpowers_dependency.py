#!/usr/bin/env python3
"""Detect whether the required Superpowers skills are installed."""

from __future__ import annotations

import importlib.util
import json
import subprocess
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


def _git_output(source_dir: Path, *arguments: str) -> tuple[str | None, str | None]:
    try:
        result = subprocess.run(
            ["git", "-C", str(source_dir), *arguments],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return None, str(exc)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return None, detail or f"git exited with status {result.returncode}"
    return result.stdout.strip(), None


def _skill_name(skill_file: Path) -> str | None:
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0] != "---":
        return None
    names: list[str] = []
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("name:"):
            names.append(line.removeprefix("name:").strip())
    return names[0] if len(names) == 1 else None


def _validate_profile_source(
    source_path: Path, *, state_root: Path, profile: object
) -> tuple[str, ...]:
    errors: list[str] = []
    source_absolute = source_path.absolute()
    source_dir = source_absolute.resolve()
    expected_source = (
        state_root.expanduser().resolve()
        / "dependencies"
        / "superpowers-gpt-5.6"
        / profile.revision
    )
    if source_absolute != expected_source:
        errors.append(
            "manifest source is outside the expected dependency cache path: "
            f"expected {expected_source}, got {source_absolute}"
        )
    else:
        current = state_root.expanduser().resolve()
        for part in source_absolute.relative_to(current).parts:
            current /= part
            if current.is_symlink():
                if current == source_absolute:
                    errors.append(
                        f"manifest source path must not be a symlink: {current}"
                    )
                else:
                    errors.append(
                        "manifest source cache path must not contain symlinks: "
                        f"{current}"
                    )
                break

    git_root, git_error = _git_output(source_dir, "rev-parse", "--show-toplevel")
    if git_error is not None or git_root is None:
        errors.append(f"manifest source is not a valid Git checkout: {source_dir}")
        return tuple(errors)
    if Path(git_root).resolve() != source_dir.resolve():
        errors.append(f"manifest source is not the Git checkout root: {source_dir}")

    revision, revision_error = _git_output(source_dir, "rev-parse", "HEAD")
    if revision_error is not None or revision is None:
        errors.append(f"could not inspect manifest source HEAD: {source_dir}")
    elif revision != profile.revision:
        errors.append(
            f"manifest source HEAD mismatch: expected {profile.revision}, got {revision}"
        )

    status, status_error = _git_output(
        source_dir, "status", "--porcelain", "--untracked-files=all"
    )
    if status_error is not None or status is None:
        errors.append(f"could not inspect manifest source checkout: {source_dir}")
    elif status:
        errors.append(f"manifest source checkout has changes:\n{status}")

    skills_root = source_dir / "skills" / "superpowers"
    if skills_root.is_symlink() or not skills_root.is_dir():
        errors.append(f"manifest source skills root is invalid: {skills_root}")
        return tuple(errors)
    discovered = {
        child.name
        for child in skills_root.iterdir()
        if child.is_dir() or child.is_symlink()
    }
    if discovered != set(profile.skills):
        errors.append(
            "manifest source skill inventory mismatch: "
            f"expected {sorted(profile.skills)}, got {sorted(discovered)}"
        )

    for name in profile.skills:
        skill_dir = skills_root / name
        skill_file = skill_dir / "SKILL.md"
        if skill_dir.is_symlink():
            errors.append(
                f"manifest source skill directory must not be a symlink: {skill_dir}"
            )
        if not skill_dir.is_dir():
            errors.append(f"manifest source skill directory is missing: {skill_dir}")
            continue
        if skill_file.is_symlink() or not skill_file.is_file():
            errors.append(f"manifest source skill file boundary is invalid: {skill_file}")
            continue
        actual_name = _skill_name(skill_file)
        if actual_name != name:
            errors.append(
                "manifest source frontmatter name mismatch: "
                f"expected {name}, got {actual_name}"
            )
    return tuple(errors)


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
    source_path = (
        Path(raw_source_dir).expanduser()
        if isinstance(raw_source_dir, str) and raw_source_dir
        else None
    )
    source_dir = source_path.resolve() if source_path is not None else None
    if source_dir is None or not source_dir.is_dir():
        errors.append(f"manifest source directory is missing: {raw_source_dir}")
    elif source_path is not None:
        errors.extend(
            _validate_profile_source(
                source_path, state_root=state_root, profile=profile
            )
        )

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
