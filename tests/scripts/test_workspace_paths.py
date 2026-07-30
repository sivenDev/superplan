from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
MODULE_PATH = SCRIPTS_DIR / "workspace_paths.py"
SPEC = importlib.util.spec_from_file_location("workspace_paths", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def init_git(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(
        ["git", "-C", str(root), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(root), "config", "user.name", "Test"],
        check=True,
    )


class WorkspacePathsTests(unittest.TestCase):
    def test_git_top_level_wins_over_nested_superplan_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            init_git(root)
            nested = root / "packages" / "demo"
            (nested / "docs" / "superplan").mkdir(parents=True)

            self.assertEqual(MODULE.resolve_existing_workspace(nested), root.resolve())

    def test_linked_worktree_resolves_to_worktree_top_level(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            main = Path(tempdir) / "main"
            worktree = Path(tempdir) / "linked"
            main.mkdir()
            init_git(main)
            (main / "tracked.txt").write_text("fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(main), "add", "tracked.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(main), "commit", "-q", "-m", "fixture"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(main), "worktree", "add", "-q", "-b", "feature", str(worktree)],
                check=True,
            )
            nested = worktree / "src" / "nested"
            nested.mkdir(parents=True)

            self.assertEqual(
                MODULE.resolve_existing_workspace(nested),
                worktree.resolve(),
            )

    def test_non_git_superplan_ancestor_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs" / "superplan").mkdir(parents=True)
            nested = root / "src" / "nested"
            nested.mkdir(parents=True)

            self.assertEqual(MODULE.resolve_existing_workspace(nested), root.resolve())

    def test_existing_workspace_fails_without_git_or_superplan(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            start = Path(tempdir)

            with self.assertRaisesRegex(ValueError, "unable to locate Superplan workspace"):
                MODULE.resolve_existing_workspace(start)

    def test_initialization_can_target_a_new_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            start = Path(tempdir) / "new-project"
            start.mkdir()

            self.assertEqual(MODULE.resolve_initialization_root(start), start.resolve())

    def test_workspace_clis_do_not_write_into_nested_superplan_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            init_git(root)
            nested = root / "packages" / "demo"
            (nested / "docs" / "superplan").mkdir(parents=True)

            commands = [
                ["init_workspace.py"],
                [
                    "record_human_request.py",
                    "--type",
                    "feature",
                    "--title",
                    "Root safety",
                ],
                ["sync_agents_guardrails.py", "--write"],
                ["generate_plans_readme.py", "--write", "--check"],
            ]
            for script, *args in commands:
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS_DIR / script), *args],
                    cwd=nested,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            self.assertTrue((root / "docs" / "superplan" / "human" / "features.md").exists())
            self.assertTrue((root / "docs" / "superplan" / "plans" / "README.md").exists())
            self.assertTrue((root / "AGENTS.md").exists())
            self.assertFalse((nested / "docs" / "superplan" / "human").exists())


if __name__ == "__main__":
    unittest.main()
