from __future__ import annotations

import importlib.util
import json
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
PROFILES = MODULE._load("superpowers_profiles")


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
    state_root = root / "profile-state"
    source_root = (
        state_root
        / "dependencies"
        / "superpowers-gpt-5.6"
        / PROFILES.GPT56_REVISION
    )
    source_skills = source_root / "skills" / "superpowers"
    skills_dir = root / ".test-agent" / "gpt56-skills"
    skills_dir.mkdir(parents=True)
    links: dict[str, str] = {}
    for name in PROFILES.GPT56_PROFILE.skills:
        source = source_skills / name
        write(
            source / "SKILL.md",
            f"---\nname: {name}\ndescription: test {name}\n---\n",
        )
        (skills_dir / name).symlink_to(source, target_is_directory=True)
        links[name] = str(source.resolve())
    manifest = {
        "schema_version": PROFILES.MANIFEST_SCHEMA_VERSION,
        "profile": "gpt56",
        "model": model,
        "repository": PROFILES.GPT56_REPOSITORY,
        "revision": PROFILES.GPT56_REVISION,
        "source_dir": str(source_root.resolve()),
        "skills_dir": str(skills_dir.resolve()),
        "skills": links,
        "backup_dir": "",
    }
    write(
        state_root / PROFILES.MANIFEST_FILENAME,
        json.dumps(manifest, indent=2) + "\n",
    )
    return state_root, skills_dir


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

    def test_init_accepts_valid_gpt56_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir = create_gpt56_install(root)

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--model",
                    "gpt-5.6",
                    "--superpowers-profile",
                    "gpt56",
                    "--superpowers-state-root",
                    str(state_root),
                    "--superpowers-skills-dir",
                    str(skills_dir),
                    "--no-default-superpowers-search",
                ]
            )

            self.assertEqual(code, 0)
            self.assertTrue((root / "docs" / "superplan" / "human" / "prd.md").is_file())

    def test_init_auto_detects_active_profile_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir = create_gpt56_install(root)

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--superpowers-state-root",
                    str(state_root),
                    "--superpowers-skills-dir",
                    str(skills_dir),
                    "--no-default-superpowers-search",
                ]
            )

            self.assertEqual(code, 0)
            self.assertTrue((root / "docs" / "superplan" / "plans" / "README.md").is_file())

    def test_init_rejects_unsupported_model_before_writing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)

            code = MODULE.run(["--root", str(root), "--model", "gpt-5.5"])

            self.assertEqual(code, 2)
            self.assertFalse((root / "docs" / "superplan").exists())

    def test_init_rejects_model_profile_mismatch_before_writing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--model",
                    "gpt-5.5",
                    "--superpowers-profile",
                    "gpt56",
                ]
            )

            self.assertEqual(code, 2)
            self.assertFalse((root / "docs" / "superplan").exists())

    def test_init_rejects_profile_link_drift_before_writing_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir = create_gpt56_install(root)
            (skills_dir / "writing-skills").unlink()

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--model",
                    "gpt-5.6",
                    "--superpowers-state-root",
                    str(state_root),
                    "--superpowers-skills-dir",
                    str(skills_dir),
                    "--no-default-superpowers-search",
                ]
            )

            self.assertEqual(code, 1)
            self.assertFalse((root / "docs" / "superplan").exists())


if __name__ == "__main__":
    unittest.main()
