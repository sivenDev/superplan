#!/usr/bin/env python3
"""Install and activate the pinned GPT-5.6 Superpowers profile."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


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


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        required=True,
        help="Model id to install for. Only gpt-5.6 and gpt-5.6-* are supported.",
    )
    parser.add_argument(
        "--skills-dir",
        help="Explicit user skills directory. Otherwise reuse one existing installation or use $HOME/.agents/skills.",
    )
    parser.add_argument(
        "--state-root",
        default=str(Path.home() / ".superplan"),
        help="Dependency, backup, and active-profile state directory.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Back up and replace verified same-name Superpowers skills.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve the target and report conflicts without cloning or changing files.",
    )
    args = parser.parse_args(argv)

    installer = _load("superpowers_profile_installer")
    profiles = _load("superpowers_profiles")
    try:
        profile = profiles.resolve_profile(model=args.model)
        result = installer.install_profile(
            installer.InstallOptions(
                model=args.model,
                skills_dir=Path(args.skills_dir) if args.skills_dir else None,
                state_root=Path(args.state_root),
                replace_existing=args.replace_existing,
                dry_run=args.dry_run,
            ),
            profile=profile,
        )
    except profiles.ProfileSelectionError as exc:
        print(str(exc))
        return 2
    except installer.InstallError as exc:
        print(f"GPT-5.6 Superpowers installation failed: {exc}")
        return 1

    print(f"status: {result.status}")
    print(f"profile: {result.profile}")
    print(f"revision: {result.revision}")
    print(f"skills directory: {result.skills_dir}")
    print(f"dependency: {result.source_dir}")
    if result.conflicts:
        print("conflicts:")
        for path in result.conflicts:
            print(f"- {path}")
    if result.backup_dir is not None:
        print(f"backup: {result.backup_dir}")
    if result.status != "dry-run":
        print("Restart Codex or open a new chat so the activated skills are rediscovered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
