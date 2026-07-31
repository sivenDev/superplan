#!/usr/bin/env python3
"""Run the authoritative Superplan repository verification contract."""

from __future__ import annotations

import os
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]) -> int:
    print(f"+ {' '.join(command)}", flush=True)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    return result.returncode


def compile_sources() -> int:
    source_roots = [ROOT / "skills", ROOT / "tests", ROOT / "tools"]
    missing = [path for path in source_roots if not path.is_dir()]
    if missing:
        print(f"missing Python source root: {missing[0]}")
        return 1
    sources = sorted(path for root in source_roots for path in root.rglob("*.py"))
    if not sources:
        print("no Python sources found")
        return 1

    print(f"+ py_compile ({len(sources)} files)", flush=True)
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            output_root = Path(tempdir)
            for source in sources:
                relative = source.relative_to(ROOT)
                compiled = output_root / relative.with_suffix(".pyc")
                compiled.parent.mkdir(parents=True, exist_ok=True)
                py_compile.compile(str(source), cfile=str(compiled), doraise=True)
    except (OSError, py_compile.PyCompileError) as exc:
        print(exc)
        return 1
    return 0


def main() -> int:
    tests_dir = ROOT / "tests" / "scripts"
    if not tests_dir.is_dir():
        print(f"missing test suite: {tests_dir}")
        return 1

    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests/scripts"],
        [sys.executable, "skills/using-superplan/scripts/init_workspace.py", "--check", "--root", "."],
        [sys.executable, "skills/using-superplan/scripts/human_requests.py", "--root", ".", "validate"],
        [sys.executable, "skills/using-superplan/scripts/sync_agents_guardrails.py", "--check", "--root", "."],
        [sys.executable, "skills/using-superplan/scripts/generate_plans_readme.py", "--root", ".", "--check"],
        ["git", "diff", "--check"],
    ]

    if run_command(commands[0]) != 0 or compile_sources() != 0:
        return 1
    for command in commands[1:]:
        if run_command(command) != 0:
            return 1
    print("repository verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
