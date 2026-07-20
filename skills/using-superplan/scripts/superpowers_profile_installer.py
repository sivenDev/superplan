#!/usr/bin/env python3
"""Transactional installer for supported external Superpowers profiles."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Callable


SCRIPTS_DIR = Path(__file__).resolve().parent


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


class InstallError(RuntimeError):
    """Raised when the profile cannot be installed without risking user state."""


@dataclass(frozen=True)
class InstallOptions:
    model: str
    skills_dir: Path | None
    state_root: Path
    replace_existing: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class InstallResult:
    status: str
    profile: str
    model: str
    revision: str
    skills_dir: Path
    source_dir: Path
    backup_dir: Path | None
    conflicts: tuple[Path, ...] = ()


def _run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        raise InstallError(f"Command failed: {' '.join(command)}\n{detail}") from exc


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


def _user_skills_dirs(home: Path) -> tuple[Path, ...]:
    return (
        home / ".agents" / "skills",
        home / ".codex" / "skills",
        home / ".claude" / "skills",
    )


def resolve_skills_dir(explicit: Path | None, *, home: Path) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    detected = tuple(
        path.resolve()
        for path in _user_skills_dirs(home)
        if (path / "using-superpowers" / "SKILL.md").is_file()
    )
    if len(detected) > 1:
        rendered = ", ".join(str(path) for path in detected)
        raise InstallError(f"Multiple Superpowers installations detected: {rendered}")
    if detected:
        return detected[0]
    return (home / ".agents" / "skills").resolve()


def _validate_repository(source_dir: Path, profile: object) -> None:
    if source_dir.is_symlink():
        raise InstallError(f"Dependency checkout path must not be a symlink: {source_dir}")
    git_root = _run(
        ["git", "-C", str(source_dir), "rev-parse", "--show-toplevel"]
    ).stdout.strip()
    if Path(git_root).resolve() != source_dir.resolve():
        raise InstallError(f"Dependency path is not the Git checkout root: {source_dir}")
    revision = _run(["git", "-C", str(source_dir), "rev-parse", "HEAD"]).stdout.strip()
    if revision != profile.revision:
        raise InstallError(
            f"Dependency revision mismatch: expected {profile.revision}, got {revision}"
        )
    status = _run(
        [
            "git",
            "-C",
            str(source_dir),
            "status",
            "--porcelain",
            "--untracked-files=all",
        ]
    ).stdout.strip()
    if status:
        raise InstallError(f"Dependency checkout has changes:\n{status}")

    skills_root = source_dir / "skills" / "superpowers"
    if skills_root.is_symlink():
        raise InstallError(f"Invalid skills root boundary: {skills_root}")
    discovered = {
        child.name
        for child in skills_root.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    } if skills_root.is_dir() else set()
    expected = set(profile.skills)
    if discovered != expected:
        raise InstallError(
            "External skill inventory mismatch: "
            f"expected {sorted(expected)}, got {sorted(discovered)}"
        )

    for name in profile.skills:
        skill_dir = skills_root / name
        skill_file = skill_dir / "SKILL.md"
        if skill_dir.is_symlink() or not skill_dir.is_dir():
            raise InstallError(f"Invalid skill directory boundary: {skill_dir}")
        if skill_file.is_symlink() or not skill_file.is_file():
            raise InstallError(f"Invalid skill file boundary: {skill_file}")
        actual_name = _skill_name(skill_file)
        if actual_name != name:
            raise InstallError(
                f"Invalid frontmatter name for {name}: expected {name}, got {actual_name}"
            )

    validator = source_dir / profile.context_budget_script
    if validator.is_symlink() or not validator.is_file():
        raise InstallError(f"Missing context-budget validator: {validator}")
    try:
        subprocess.run(
            ["bash", str(validator)],
            cwd=source_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        raise InstallError(f"External context-budget validation failed: {detail}") from exc
    status = _run(
        [
            "git",
            "-C",
            str(source_dir),
            "status",
            "--porcelain",
            "--untracked-files=all",
        ]
    ).stdout.strip()
    if status:
        raise InstallError(f"Context-budget validator changed the checkout:\n{status}")


def _clone_and_validate(profile: object, destination: Path) -> None:
    _run(["git", "clone", "--quiet", "--no-checkout", profile.repository, str(destination)])
    _run(
        [
            "git",
            "-C",
            str(destination),
            "checkout",
            "--quiet",
            "--detach",
            profile.revision,
        ]
    )
    _validate_repository(destination, profile)


def _path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _replaceable_skill(path: Path, expected_name: str) -> bool:
    if path.is_symlink():
        skill_file = path.resolve() / "SKILL.md"
    elif path.is_dir():
        skill_file = path / "SKILL.md"
    else:
        return False
    return skill_file.is_file() and _skill_name(skill_file) == expected_name


def _conflicts(skills_dir: Path, profile: object) -> tuple[Path, ...]:
    names = profile.skills + profile.removed_skills
    return tuple(skills_dir / name for name in names if _path_exists(skills_dir / name))


def _manifest_data(
    *,
    options: InstallOptions,
    profile: object,
    skills_dir: Path,
    source_dir: Path,
    backup_dir: Path | None,
) -> dict[str, object]:
    profiles = _load("superpowers_profiles")
    source_skills = source_dir / "skills" / "superpowers"
    return {
        "schema_version": profiles.MANIFEST_SCHEMA_VERSION,
        "profile": profile.name,
        "model": options.model,
        "repository": profile.repository,
        "revision": profile.revision,
        "source_dir": str(source_dir),
        "skills_dir": str(skills_dir),
        "skills": {
            name: str((source_skills / name).resolve()) for name in profile.skills
        },
        "backup_dir": str(backup_dir) if backup_dir is not None else "",
    }


def _read_json(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _already_active(
    *,
    manifest_path: Path,
    options: InstallOptions,
    profile: object,
    skills_dir: Path,
    source_dir: Path,
) -> InstallResult | None:
    profiles = _load("superpowers_profiles")
    manifest = _read_json(manifest_path)
    if manifest is None:
        return None
    if (
        manifest.get("schema_version") != profiles.MANIFEST_SCHEMA_VERSION
        or manifest.get("profile") != profile.name
        or manifest.get("model") != options.model
        or manifest.get("repository") != profile.repository
        or manifest.get("revision") != profile.revision
        or manifest.get("skills_dir") != str(skills_dir)
        or manifest.get("source_dir") != str(source_dir)
    ):
        return None
    raw_skills = manifest.get("skills")
    if not isinstance(raw_skills, dict) or set(raw_skills) != set(profile.skills):
        return None
    for name in profile.skills:
        target = skills_dir / name
        expected = source_dir / "skills" / "superpowers" / name
        if raw_skills.get(name) != str(expected.resolve()):
            return None
        if not target.is_symlink() or target.resolve() != expected.resolve():
            return None
    for name in profile.removed_skills:
        if _path_exists(skills_dir / name):
            return None
    raw_backup = manifest.get("backup_dir")
    backup_dir = Path(raw_backup).resolve() if isinstance(raw_backup, str) and raw_backup else None
    return InstallResult(
        status="already-active",
        profile=profile.name,
        model=options.model,
        revision=profile.revision,
        skills_dir=skills_dir,
        source_dir=source_dir,
        backup_dir=backup_dir,
    )


def _remove_empty(path: Path) -> None:
    try:
        path.rmdir()
    except OSError:
        pass


def _inject(fail_after: str | None, point: str) -> None:
    if fail_after == point:
        raise InstallError(f"Injected failure after {point}")


def _validate_manifest_paths(manifest_path: Path) -> None:
    manifest_temp = manifest_path.with_name(f".{manifest_path.name}.tmp")
    if manifest_path.is_symlink() or (
        manifest_path.exists() and not manifest_path.is_file()
    ):
        raise InstallError(f"Unsafe manifest path: {manifest_path}")
    if _path_exists(manifest_temp):
        raise InstallError(f"Unsafe manifest path: {manifest_temp}")


def _validate_dependency_cache_path(source_dir: Path, state_root: Path) -> None:
    current = state_root
    relative_parts = source_dir.relative_to(state_root).parts
    for part in relative_parts[:-1]:
        current /= part
        if current.is_symlink():
            raise InstallError(
                f"Dependency cache path must not contain symlinks: {current}"
            )


def _rollback_activation(
    *,
    manifest_path: Path,
    previous_manifest: bytes | None,
    manifest_published: bool,
    created_links: list[Path],
    moved: list[tuple[Path, Path]],
    backup_dir: Path | None,
    source_published: bool,
    source_dir: Path,
    skills_dir_created: bool,
    skills_dir: Path,
    state_root_created: bool,
    state_root: Path,
) -> tuple[str, ...]:
    errors: list[str] = []

    def attempt(label: str, operation: Callable[[], None]) -> None:
        try:
            operation()
        except Exception as exc:
            errors.append(f"{label}: {exc}")

    manifest_temp = manifest_path.with_name(f".{manifest_path.name}.tmp")
    if manifest_temp.is_file() or manifest_temp.is_symlink():
        attempt("remove temporary manifest", manifest_temp.unlink)
    if manifest_published:
        if manifest_path.is_file() or manifest_path.is_symlink():
            attempt("remove active manifest", manifest_path.unlink)
        if previous_manifest is not None:
            def restore_manifest() -> None:
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                manifest_path.write_bytes(previous_manifest)

            attempt("restore previous manifest", restore_manifest)

    for target in reversed(created_links):
        if target.is_symlink() or target.exists():
            attempt(f"remove activated link {target}", target.unlink)
    for original, backup_path in reversed(moved):
        if _path_exists(backup_path):
            def restore_skill(
                original_path: Path = original, backup: Path = backup_path
            ) -> None:
                original_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(backup), str(original_path))

            attempt(f"restore skill {original}", restore_skill)

    if backup_dir is not None:
        attempt("remove empty backup skills directory", lambda: _remove_empty(backup_dir / "skills"))
        attempt("remove empty backup directory", lambda: _remove_empty(backup_dir))
        attempt("remove empty backups root", lambda: _remove_empty(backup_dir.parent))
    if source_published and source_dir.exists():
        attempt("remove published dependency", lambda: shutil.rmtree(source_dir))
        attempt("remove empty revision parent", lambda: _remove_empty(source_dir.parent))
        attempt("remove empty dependency parent", lambda: _remove_empty(source_dir.parent.parent))
        attempt("remove empty dependencies root", lambda: _remove_empty(source_dir.parent.parent.parent))
    if skills_dir_created:
        attempt("remove empty skills directory", lambda: _remove_empty(skills_dir))
    if state_root_created:
        attempt("remove empty state root", lambda: _remove_empty(state_root))
    return tuple(errors)


def install_profile(
    options: InstallOptions,
    *,
    profile: object | None = None,
    home: Path | None = None,
    fail_after: str | None = None,
    now: Callable[[], datetime] | None = None,
) -> InstallResult:
    profiles = _load("superpowers_profiles")
    selected = profile or profiles.resolve_profile(model=options.model)
    if selected is None or not selected.matches_model(options.model):
        raise InstallError(f"Unsupported model: {options.model}")

    resolved_home = (home or Path.home()).expanduser().resolve()
    skills_dir = resolve_skills_dir(options.skills_dir, home=resolved_home)
    state_root = options.state_root.expanduser().resolve()
    source_dir = (
        state_root
        / "dependencies"
        / "superpowers-gpt-5.6"
        / selected.revision
    )
    manifest_path = state_root / profiles.MANIFEST_FILENAME
    _validate_manifest_paths(manifest_path)
    _validate_dependency_cache_path(source_dir, state_root)

    if source_dir.is_dir():
        _validate_repository(source_dir, selected)
        active = _already_active(
            manifest_path=manifest_path,
            options=options,
            profile=selected,
            skills_dir=skills_dir,
            source_dir=source_dir,
        )
        if active is not None:
            return active

    conflicts = _conflicts(skills_dir, selected)
    unsafe = tuple(
        path for path in conflicts if not _replaceable_skill(path, path.name)
    )
    if unsafe:
        raise InstallError(
            "Unsafe conflict cannot be replaced: " + ", ".join(str(path) for path in unsafe)
        )
    if conflicts and not options.replace_existing and not options.dry_run:
        raise InstallError(
            "Existing skills conflict; rerun with --replace-existing after review: "
            + ", ".join(str(path) for path in conflicts)
        )
    if options.dry_run:
        return InstallResult(
            status="dry-run",
            profile=selected.name,
            model=options.model,
            revision=selected.revision,
            skills_dir=skills_dir,
            source_dir=source_dir,
            backup_dir=None,
            conflicts=conflicts,
        )

    temporary: tempfile.TemporaryDirectory[str] | None = None
    staged_source: Path | None = None
    if not source_dir.is_dir():
        temporary = tempfile.TemporaryDirectory(prefix="superplan-gpt56-")
        staged_source = Path(temporary.name) / "checkout"
        try:
            _clone_and_validate(selected, staged_source)
        except Exception:
            temporary.cleanup()
            raise

    timestamp = (now or (lambda: datetime.now(timezone.utc)))().strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    backup_dir = state_root / "backups" / timestamp if conflicts else None
    previous_manifest = manifest_path.read_bytes() if manifest_path.is_file() else None
    manifest_published = False
    moved: list[tuple[Path, Path]] = []
    created_links: list[Path] = []
    source_published = False
    skills_dir_created = not skills_dir.exists()
    state_root_created = not state_root.exists()

    try:
        source_dir.parent.mkdir(parents=True, exist_ok=True)
        if staged_source is not None:
            source_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(staged_source), str(source_dir))
            source_published = True
        else:
            _validate_repository(source_dir, selected)
        _inject(fail_after, "source")

        skills_dir.mkdir(parents=True, exist_ok=True)
        if backup_dir is not None:
            (backup_dir / "skills").mkdir(parents=True, exist_ok=False)
            for path in conflicts:
                backup_path = backup_dir / "skills" / path.name
                shutil.move(str(path), str(backup_path))
                moved.append((path, backup_path))
            _inject(fail_after, "backup")

        source_skills = source_dir / "skills" / "superpowers"
        for index, name in enumerate(selected.skills, start=1):
            target = skills_dir / name
            target.symlink_to(source_skills / name, target_is_directory=True)
            created_links.append(target)
            _inject(fail_after, f"link:{index}")

        for name in selected.skills:
            target = skills_dir / name
            if not target.is_symlink() or target.resolve() != (source_skills / name).resolve():
                raise InstallError(f"Activation verification failed for {name}")
        for name in selected.removed_skills:
            if _path_exists(skills_dir / name):
                raise InstallError(f"Removed skill remains active: {name}")

        manifest = _manifest_data(
            options=options,
            profile=selected,
            skills_dir=skills_dir,
            source_dir=source_dir,
            backup_dir=backup_dir,
        )
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_temp = manifest_path.with_name(f".{manifest_path.name}.tmp")
        manifest_temp.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        os.replace(manifest_temp, manifest_path)
        manifest_published = True
        _inject(fail_after, "manifest")
    except Exception as exc:
        rollback_errors = _rollback_activation(
            manifest_path=manifest_path,
            previous_manifest=previous_manifest,
            manifest_published=manifest_published,
            created_links=created_links,
            moved=moved,
            backup_dir=backup_dir,
            source_published=source_published,
            source_dir=source_dir,
            skills_dir_created=skills_dir_created,
            skills_dir=skills_dir,
            state_root_created=state_root_created,
            state_root=state_root,
        )
        message = str(exc)
        if rollback_errors:
            message += "\nRollback errors:\n- " + "\n- ".join(rollback_errors)
        if isinstance(exc, InstallError) and not rollback_errors:
            raise
        raise InstallError(message) from exc
    finally:
        if temporary is not None:
            temporary.cleanup()

    return InstallResult(
        status="installed",
        profile=selected.name,
        model=options.model,
        revision=selected.revision,
        skills_dir=skills_dir,
        source_dir=source_dir,
        backup_dir=backup_dir,
        conflicts=conflicts,
    )
