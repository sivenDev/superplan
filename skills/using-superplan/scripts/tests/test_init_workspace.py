from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "init_workspace.py"
SPEC = importlib.util.spec_from_file_location("init_workspace", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

SYNC = MODULE._load("sync_agents_guardrails")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_superpowers_install(skills_dir: Path) -> None:
    required = [
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
    ]
    for name in required:
        write(skills_dir / name / "SKILL.md", f"# {name}\n")


class InitWorkspaceTests(unittest.TestCase):
    def test_init_scaffolds_docs_agents_and_plans_index(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills_dir = root / ".test-agent" / "skills"
            create_superpowers_install(skills_dir)

            self.assertEqual(
                MODULE.run(
                    [
                        "--root",
                        str(root),
                        "--superpowers-skills-dir",
                        str(skills_dir),
                        "--no-default-superpowers-search",
                    ]
                ),
                0,
            )

            for name in ("prd.md", "features.md", "bugs.md"):
                self.assertTrue((root / "docs" / "superplan" / "human" / name).exists())
            features_text = (root / "docs" / "superplan" / "human" / "features.md").read_text(encoding="utf-8")
            self.assertTrue(features_text.startswith("# Features"))
            self.assertIn("status", features_text)
            self.assertIn("F<NNN>", features_text)
            self.assertIn("F001@branch-slug", features_text)
            bugs_text = (root / "docs" / "superplan" / "human" / "bugs.md").read_text(encoding="utf-8")
            self.assertIn("B001@branch-slug", bugs_text)

            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(SYNC.START_MARKER, agents)
            self.assertIn("# Workflow Guardrails", agents)

            readme = (root / "docs" / "superplan" / "plans" / "README.md").read_text(encoding="utf-8")
            self.assertIn("# Plans Index", readme)

    def test_init_is_idempotent_and_preserves_human_edits(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills_dir = root / ".test-agent" / "skills"
            create_superpowers_install(skills_dir)
            self.assertEqual(
                MODULE.run(
                    [
                        "--root",
                        str(root),
                        "--superpowers-skills-dir",
                        str(skills_dir),
                        "--no-default-superpowers-search",
                    ]
                ),
                0,
            )

            features = root / "docs" / "superplan" / "human" / "features.md"
            features.write_text("# Features\n\n## F001: Existing\n", encoding="utf-8")

            self.assertEqual(
                MODULE.run(
                    [
                        "--root",
                        str(root),
                        "--superpowers-skills-dir",
                        str(skills_dir),
                        "--no-default-superpowers-search",
                    ]
                ),
                0,
            )

            self.assertEqual(
                features.read_text(encoding="utf-8"),
                "# Features\n\n## F001: Existing\n",
            )
            self.assertEqual((root / "AGENTS.md").read_text(encoding="utf-8").count(SYNC.START_MARKER), 1)

    def test_init_runs_as_standalone_subprocess(self) -> None:
        # A subprocess has a clean sys.modules, so this catches the importlib
        # loader defect where sub-scripts were not registered before exec and
        # dataclass annotation resolution failed.
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills_dir = root / ".test-agent" / "skills"
            create_superpowers_install(skills_dir)
            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--root",
                    str(root),
                    "--superpowers-skills-dir",
                    str(skills_dir),
                    "--no-default-superpowers-search",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue((root / "docs" / "superplan" / "plans" / "README.md").exists())
            self.assertTrue((root / "docs" / "superplan" / "human" / "prd.md").exists())

    def test_init_fails_when_superpowers_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)

            self.assertEqual(
                MODULE.run(["--root", str(root), "--no-default-superpowers-search"]),
                1,
            )
            self.assertFalse((root / "docs" / "superplan").exists())

    def test_init_can_skip_superpowers_check(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)

            self.assertEqual(MODULE.run(["--root", str(root), "--skip-superpowers-check"]), 0)
            self.assertTrue((root / "docs" / "superplan" / "plans" / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
