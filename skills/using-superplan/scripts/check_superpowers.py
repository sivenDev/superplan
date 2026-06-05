#!/usr/bin/env python3
"""Verify that Superpowers is installed before using Superplan."""

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
        "--skills-dir",
        action="append",
        default=[],
        help="Explicit Superpowers skills directory to check. Can be passed multiple times.",
    )
    parser.add_argument(
        "--superpowers-root",
        action="append",
        default=[],
        help="Explicit Superpowers plugin/repository root containing a skills/ directory.",
    )
    parser.add_argument(
        "--no-default-search",
        action="store_true",
        help="Only check explicitly provided --skills-dir/--superpowers-root locations.",
    )
    args = parser.parse_args(argv)

    dependency = _load("superpowers_dependency")
    result = dependency.check_installation(
        skills_dirs=[Path(path) for path in args.skills_dir],
        superpowers_roots=[Path(path) for path in args.superpowers_root],
        include_defaults=not args.no_default_search,
    )
    print(dependency.format_result(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
