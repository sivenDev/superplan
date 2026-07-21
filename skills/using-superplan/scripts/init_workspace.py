#!/usr/bin/env python3
"""Initialize a Superplan workspace.

Idempotently scaffolds the docs structure, installs the managed AGENTS.md
guardrails, and generates the plans index:

- docs/superplan/human/{prd.md, features.md, bugs.md} (created only when missing)
- docs/superplan/plans/ directory and docs/superplan/plans/README.md (generated)
- AGENTS.md managed guardrails block (created or refreshed in place)

Existing human docs are never overwritten, so running this on an established
repository is safe.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from workspace_paths import resolve_initialization_root


SCRIPTS_DIR = Path(__file__).resolve().parent
HUMAN_ASSETS_DIR = SCRIPTS_DIR.parent / "assets" / "human"
HUMAN_FILES = ("prd.md", "features.md", "bugs.md")


def _load(name: str) -> ModuleType:
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Register before exec: dataclasses in the loaded module resolve string
    # annotations via sys.modules[cls.__module__], which would otherwise be None.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def scaffold_human_docs(root: Path) -> list[str]:
    created: list[str] = []
    human_dir = root / "docs" / "superplan" / "human"
    human_dir.mkdir(parents=True, exist_ok=True)
    for filename in HUMAN_FILES:
        path = human_dir / filename
        if not path.exists():
            path.write_text(
                (HUMAN_ASSETS_DIR / filename).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            created.append(path.as_posix())
    return created


def sync_agents(root: Path) -> str:
    sync = _load("sync_agents_guardrails")
    agents_path = root / "AGENTS.md"
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    synced = sync.render_synced(existing, sync.load_asset())
    changed = synced != existing
    agents_path.write_text(synced, encoding="utf-8")
    return "updated" if changed else "unchanged"


def generate_plans_index(root: Path) -> str:
    readme = _load("generate_plans_readme")
    plans_dir = root / "docs" / "superplan" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    generated = readme.generate_readme(root, plans_dir)
    readme_path = plans_dir / "README.md"
    current = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    readme_path.write_text(generated, encoding="utf-8")
    return "updated" if generated != current else "unchanged"


def ensure_superpowers_installed(
    *,
    superpowers_roots: list[str],
    superpowers_skills_dirs: list[str],
    include_default_search: bool,
    model: str | None,
    profile_name: str | None,
    state_root: str,
) -> int:
    dependency = _load("superpowers_dependency")
    try:
        result = dependency.check_installation(
            skills_dirs=[Path(path) for path in superpowers_skills_dirs],
            superpowers_roots=[Path(path) for path in superpowers_roots],
            include_defaults=include_default_search,
            profile_name=profile_name,
            model=model,
            state_root=Path(state_root),
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    print(dependency.format_result(result))
    return 0 if result.ok else 1


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(resolve_initialization_root(Path.cwd())),
        help="Repository root. Defaults to the Git top-level, an existing Superplan ancestor, or the current directory.",
    )
    parser.add_argument(
        "--skip-superpowers-check",
        action="store_true",
        help="Skip the bundled Superpowers dependency check.",
    )
    parser.add_argument(
        "--superpowers-root",
        action="append",
        default=[],
        help="Explicit Superpowers plugin/repository root containing a skills/ directory.",
    )
    parser.add_argument(
        "--superpowers-skills-dir",
        action="append",
        default=[],
        help="Explicit Superpowers skills directory to check. Can be passed multiple times.",
    )
    parser.add_argument(
        "--no-default-superpowers-search",
        action="store_true",
        help="Only check explicitly provided Superpowers locations.",
    )
    parser.add_argument(
        "--model",
        help="Model id to validate before initialization. Only GPT-5.6 is profile-aware.",
    )
    parser.add_argument(
        "--superpowers-profile",
        help="Explicit active Superpowers profile to validate.",
    )
    parser.add_argument(
        "--superpowers-state-root",
        default=str(Path.home() / ".superplan"),
        help="Superplan dependency, backup, and active-profile state directory.",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if not args.skip_superpowers_check:
        status = ensure_superpowers_installed(
            superpowers_roots=args.superpowers_root,
            superpowers_skills_dirs=args.superpowers_skills_dir,
            include_default_search=not args.no_default_superpowers_search,
            model=args.model,
            profile_name=args.superpowers_profile,
            state_root=args.superpowers_state_root,
        )
        if status != 0:
            return status

    created_docs = scaffold_human_docs(root)
    agents_state = sync_agents(root)
    plans_state = generate_plans_index(root)

    print(f"root: {root}")
    if created_docs:
        for path in created_docs:
            print(f"created {path}")
    else:
        print("human docs: already present")
    print(f"AGENTS.md: {agents_state}")
    print(f"docs/superplan/plans/README.md: {plans_state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
