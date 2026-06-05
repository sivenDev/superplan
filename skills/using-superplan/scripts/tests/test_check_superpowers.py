from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_superpowers.py"
SPEC = importlib.util.spec_from_file_location("check_superpowers", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


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


class CheckSuperpowersTests(unittest.TestCase):
    def test_check_passes_with_valid_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            skills_dir = Path(tempdir) / "skills"
            create_superpowers_install(skills_dir)

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(["--skills-dir", str(skills_dir), "--no-default-search"])

            self.assertEqual(code, 0)
            self.assertIn("Superpowers installation found", output.getvalue())

    def test_check_fails_with_install_guidance_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            skills_dir = Path(tempdir) / "skills"

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(["--skills-dir", str(skills_dir), "--no-default-search"])

            self.assertEqual(code, 1)
            rendered = output.getvalue()
            self.assertIn("Install superpowers first", rendered)
            self.assertIn("https://github.com/obra/superpowers", rendered)

    def test_check_detects_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            plugin_root = Path(tempdir) / "superpowers"
            create_superpowers_install(plugin_root / "skills")

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    ["--superpowers-root", str(plugin_root), "--no-default-search"]
                )

            self.assertEqual(code, 0)
            self.assertIn(str(plugin_root / "skills"), output.getvalue())


if __name__ == "__main__":
    unittest.main()
