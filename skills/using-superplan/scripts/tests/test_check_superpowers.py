from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_superpowers.py"
GPT56_REVISION = "aa973775906c8761a78019aaa21e4f0ccd987925"
GPT56_REPOSITORY = "https://github.com/eagleagentic/superpowers-gpt-5.6.git"
GPT56_SKILLS = (
    "brainstorming",
    "executing-plans",
    "finishing-a-development-branch",
    "receiving-code-review",
    "requesting-code-review",
    "systematic-debugging",
    "test-driven-development",
    "using-git-worktrees",
    "using-superpowers",
    "verification-before-completion",
    "writing-implementation-logs",
    "writing-plans",
    "writing-skills",
)
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


def create_gpt56_install(root: Path, *, model: str = "gpt-5.6") -> tuple[Path, Path]:
    state_root = root / "state"
    source_root = (
        state_root
        / "dependencies"
        / "superpowers-gpt-5.6"
        / GPT56_REVISION
    )
    source_skills = source_root / "skills" / "superpowers"
    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True)

    links: dict[str, str] = {}
    for name in GPT56_SKILLS:
        source = source_skills / name
        write(
            source / "SKILL.md",
            f"---\nname: {name}\ndescription: test {name}\n---\n",
        )
        target = skills_dir / name
        target.symlink_to(source, target_is_directory=True)
        links[name] = str(source.resolve())

    manifest = {
        "schema_version": 1,
        "profile": "gpt56",
        "model": model,
        "repository": GPT56_REPOSITORY,
        "revision": GPT56_REVISION,
        "source_dir": str(source_root.resolve()),
        "skills_dir": str(skills_dir.resolve()),
        "skills": links,
        "backup_dir": "",
    }
    write(
        state_root / "active-superpowers-profile.json",
        json.dumps(manifest, indent=2) + "\n",
    )
    return state_root, skills_dir


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

    def test_gpt56_model_check_validates_active_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir = create_gpt56_install(Path(tempdir))

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--model",
                        "gpt-5.6",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 0)
            rendered = output.getvalue()
            self.assertIn("profile gpt56", rendered)
            self.assertIn(GPT56_REVISION, rendered)

    def test_gpt56_suffix_model_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir = create_gpt56_install(
                Path(tempdir), model="gpt-5.6-terra"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--model",
                        "gpt-5.6-terra",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 0)

    def test_unsupported_model_is_rejected_without_fallback(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            code = MODULE.run(["--model", "gpt-5.5", "--no-default-search"])

        self.assertEqual(code, 2)
        self.assertIn("Unsupported model: gpt-5.5", output.getvalue())

    def test_profile_and_model_must_agree(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            code = MODULE.run(
                [
                    "--profile",
                    "gpt56",
                    "--model",
                    "gpt-5.5",
                    "--no-default-search",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("does not match model", output.getvalue())

    def test_gpt56_check_lists_exact_missing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir = create_gpt56_install(Path(tempdir))
            (skills_dir / "writing-skills").unlink()

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--profile",
                        "gpt56",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 1)
            rendered = output.getvalue()
            self.assertIn("Missing required skills", rendered)
            self.assertIn("- writing-skills", rendered)
            self.assertNotIn("subagent-driven-development", rendered)

    def test_gpt56_check_rejects_manifest_revision_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir = create_gpt56_install(Path(tempdir))
            manifest_path = state_root / "active-superpowers-profile.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["revision"] = "0" * 40
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--model",
                        "gpt-5.6",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("revision mismatch", output.getvalue())

    def test_gpt56_check_rejects_link_target_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir = create_gpt56_install(root)
            target = skills_dir / "writing-skills"
            target.unlink()
            target.symlink_to(root / "unexpected", target_is_directory=True)

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--model",
                        "gpt-5.6",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("link target mismatch", output.getvalue())

    def test_gpt56_check_rejects_duplicate_superpowers_installations(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir = create_gpt56_install(root)
            duplicate = root / "duplicate-skills"
            create_superpowers_install(duplicate)

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--model",
                        "gpt-5.6",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--skills-dir",
                        str(duplicate),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 1)
            self.assertIn("Multiple Superpowers installations detected", output.getvalue())

    def test_no_argument_check_uses_active_manifest_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir = create_gpt56_install(Path(tempdir))

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn("profile gpt56", output.getvalue())

    def test_default_search_includes_official_agents_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            fake_home = Path(tempdir)
            skills_dir = fake_home / ".agents" / "skills"
            create_superpowers_install(skills_dir)

            output = io.StringIO()
            with patch("pathlib.Path.home", return_value=fake_home), redirect_stdout(output):
                code = MODULE.run([])

            self.assertEqual(code, 0)
            self.assertIn(str(skills_dir), output.getvalue())


if __name__ == "__main__":
    unittest.main()
