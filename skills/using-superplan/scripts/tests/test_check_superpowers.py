from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
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


def create_gpt56_install(
    root: Path, *, model: str = "gpt-5.6"
) -> tuple[Path, Path, object]:
    state_root = root / "state"
    staging_source = root / "source-staging"
    staging_skills = staging_source / "skills" / "superpowers"
    for name in GPT56_SKILLS:
        write(
            staging_skills / name / "SKILL.md",
            f"---\nname: {name}\ndescription: test {name}\n---\n",
        )
    subprocess.run(["git", "init", "-q", str(staging_source)], check=True)
    subprocess.run(
        ["git", "-C", str(staging_source), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(staging_source), "config", "user.name", "Test"],
        check=True,
    )
    subprocess.run(["git", "-C", str(staging_source), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(staging_source), "commit", "-q", "-m", "fixture"],
        check=True,
    )
    revision = subprocess.run(
        ["git", "-C", str(staging_source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    profile = replace(PROFILES.GPT56_PROFILE, revision=revision)
    source_root = (
        state_root
        / "dependencies"
        / "superpowers-gpt-5.6"
        / revision
    )
    source_root.parent.mkdir(parents=True)
    staging_source.rename(source_root)
    source_skills = source_root / "skills" / "superpowers"
    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True)

    links: dict[str, str] = {}
    for name in GPT56_SKILLS:
        source = source_skills / name
        target = skills_dir / name
        target.symlink_to(source, target_is_directory=True)
        links[name] = str(source.resolve())

    manifest = {
        "schema_version": 1,
        "profile": "gpt56",
        "model": model,
        "repository": profile.repository,
        "revision": profile.revision,
        "source_dir": str(source_root.resolve()),
        "skills_dir": str(skills_dir.resolve()),
        "skills": links,
        "backup_dir": "",
    }
    write(
        state_root / "active-superpowers-profile.json",
        json.dumps(manifest, indent=2) + "\n",
    )
    return state_root, skills_dir, profile


def run_with_profile(profile: object, argv: list[str]) -> int:
    active_profiles = MODULE._load("superpowers_profiles")
    targets = {id(module): module for module in (PROFILES, active_profiles)}
    with ExitStack() as stack:
        for target in targets.values():
            stack.enter_context(patch.object(target, "GPT56_PROFILE", profile))
            stack.enter_context(patch.dict(target.PROFILES, {"gpt56": profile}))
        return MODULE.run(argv)


def commit_and_retarget_profile(
    state_root: Path, skills_dir: Path, profile: object, message: str
) -> object:
    source_dir = (
        state_root
        / "dependencies"
        / "superpowers-gpt-5.6"
        / profile.revision
    )
    subprocess.run(["git", "-C", str(source_dir), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(source_dir), "commit", "-q", "-m", message],
        check=True,
    )
    revision = subprocess.run(
        ["git", "-C", str(source_dir), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    new_profile = replace(profile, revision=revision)
    new_source_dir = source_dir.parent / revision
    source_dir.rename(new_source_dir)

    manifest_path = state_root / "active-superpowers-profile.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["revision"] = revision
    manifest["source_dir"] = str(new_source_dir.resolve())
    links: dict[str, str] = {}
    for name in GPT56_SKILLS:
        target = skills_dir / name
        target.unlink()
        source = new_source_dir / "skills" / "superpowers" / name
        target.symlink_to(source, target_is_directory=True)
        links[name] = str(source.resolve())
    manifest["skills"] = links
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return new_profile


class CheckSuperpowersTests(unittest.TestCase):
    def test_check_passes_with_valid_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills_dir = root / "skills"
            create_superpowers_install(skills_dir)

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--state-root",
                        str(root / "state"),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn("Superpowers installation found", output.getvalue())

    def test_check_fails_with_install_guidance_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills_dir = root / "skills"

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--state-root",
                        str(root / "state"),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 1)
            rendered = output.getvalue()
            self.assertIn("Install superpowers first", rendered)
            self.assertIn("https://github.com/obra/superpowers", rendered)

    def test_check_detects_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plugin_root = root / "superpowers"
            create_superpowers_install(plugin_root / "skills")

            output = io.StringIO()
            with redirect_stdout(output):
                code = MODULE.run(
                    [
                        "--state-root",
                        str(root / "state"),
                        "--superpowers-root",
                        str(plugin_root),
                        "--no-default-search",
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn(str(plugin_root / "skills"), output.getvalue())

    def test_gpt56_model_check_validates_active_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir, profile = create_gpt56_install(Path(tempdir))

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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
            self.assertIn(profile.revision, rendered)

    def test_gpt56_suffix_model_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            state_root, skills_dir, profile = create_gpt56_install(
                Path(tempdir), model="gpt-5.6-terra"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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
            state_root, skills_dir, profile = create_gpt56_install(Path(tempdir))
            (skills_dir / "writing-skills").unlink()

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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
            state_root, skills_dir, profile = create_gpt56_install(Path(tempdir))
            manifest_path = state_root / "active-superpowers-profile.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["revision"] = "0" * 40
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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
            state_root, skills_dir, profile = create_gpt56_install(root)
            target = skills_dir / "writing-skills"
            target.unlink()
            target.symlink_to(root / "unexpected", target_is_directory=True)

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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
            state_root, skills_dir, profile = create_gpt56_install(root)
            duplicate = root / "duplicate-skills"
            create_superpowers_install(duplicate)

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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
            state_root, skills_dir, profile = create_gpt56_install(Path(tempdir))

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
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

    def test_gpt56_check_rejects_non_git_source(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            shutil.rmtree(source_dir / ".git")

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model",
                        "gpt-5.6",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("not a valid Git checkout", output.getvalue())

    def test_gpt56_check_rejects_dirty_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_file = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
                / "skills"
                / "superpowers"
                / "writing-skills"
                / "SKILL.md"
            )
            source_file.write_text(
                source_file.read_text(encoding="utf-8") + "dirty\n",
                encoding="utf-8",
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model",
                        "gpt-5.6",
                        "--state-root",
                        str(state_root),
                        "--skills-dir",
                        str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("checkout has changes", output.getvalue())

    def test_gpt56_check_rejects_source_outside_expected_cache_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            moved_source = root / "moved-source"
            source_dir.rename(moved_source)
            manifest_path = state_root / "active-superpowers-profile.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["source_dir"] = str(moved_source)
            links: dict[str, str] = {}
            for name in GPT56_SKILLS:
                target = skills_dir / name
                target.unlink()
                source = moved_source / "skills" / "superpowers" / name
                target.symlink_to(source, target_is_directory=True)
                links[name] = str(source.resolve())
            manifest["skills"] = links
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("expected dependency cache path", output.getvalue())

    def test_gpt56_check_rejects_symlinked_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            real_source = root / "real-source"
            source_dir.rename(real_source)
            source_dir.symlink_to(real_source, target_is_directory=True)

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("source path must not be a symlink", output.getvalue())

    def test_gpt56_check_rejects_symlinked_dependency_cache_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            dependencies = state_root / "dependencies"
            external_dependencies = root / "external-dependencies"
            dependencies.rename(external_dependencies)
            dependencies.symlink_to(external_dependencies, target_is_directory=True)
            manifest_path = state_root / "active-superpowers-profile.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            logical_source = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            manifest["skills"] = {
                name: str(
                    (logical_source / "skills" / "superpowers" / name).resolve()
                )
                for name in GPT56_SKILLS
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("cache path must not contain symlinks", output.getvalue())

    def test_gpt56_check_rejects_wrong_source_head(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            write(source_dir / "README.md", "new commit\n")
            subprocess.run(["git", "-C", str(source_dir), "add", "README.md"], check=True)
            subprocess.run(
                ["git", "-C", str(source_dir), "commit", "-q", "-m", "drift"],
                check=True,
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("source HEAD mismatch", output.getvalue())

    def test_gpt56_check_rejects_source_skill_inventory_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            write(
                source_dir / "skills" / "superpowers" / "unexpected" / "SKILL.md",
                "---\nname: unexpected\n---\n",
            )
            profile = commit_and_retarget_profile(
                state_root, skills_dir, profile, "add unexpected skill"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("source skill inventory mismatch", output.getvalue())

    def test_gpt56_check_rejects_source_frontmatter_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            skill_file = (
                source_dir / "skills" / "superpowers" / "writing-skills" / "SKILL.md"
            )
            skill_file.write_text(
                "---\nname: wrong-name\ndescription: drift\n---\n",
                encoding="utf-8",
            )
            profile = commit_and_retarget_profile(
                state_root, skills_dir, profile, "change frontmatter"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("source frontmatter name mismatch", output.getvalue())

    def test_gpt56_check_rejects_symlinked_source_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            skill_dir = source_dir / "skills" / "superpowers" / "writing-skills"
            shutil.rmtree(skill_dir)
            external_skill = root / "external-writing-skills"
            write(
                external_skill / "SKILL.md",
                "---\nname: writing-skills\ndescription: external\n---\n",
            )
            skill_dir.symlink_to(external_skill, target_is_directory=True)
            profile = commit_and_retarget_profile(
                state_root, skills_dir, profile, "symlink skill directory"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("source skill directory must not be a symlink", output.getvalue())

    def test_gpt56_check_rejects_symlinked_source_skill_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            state_root, skills_dir, profile = create_gpt56_install(root)
            source_dir = (
                state_root
                / "dependencies"
                / "superpowers-gpt-5.6"
                / profile.revision
            )
            skill_file = (
                source_dir / "skills" / "superpowers" / "writing-skills" / "SKILL.md"
            )
            skill_file.unlink()
            external_file = root / "external-SKILL.md"
            external_file.write_text(
                "---\nname: writing-skills\ndescription: external\n---\n",
                encoding="utf-8",
            )
            skill_file.symlink_to(external_file)
            profile = commit_and_retarget_profile(
                state_root, skills_dir, profile, "symlink skill file"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                code = run_with_profile(
                    profile,
                    [
                        "--model", "gpt-5.6",
                        "--state-root", str(state_root),
                        "--skills-dir", str(skills_dir),
                        "--no-default-search",
                    ],
                )

            self.assertEqual(code, 1)
            self.assertIn("source skill file boundary is invalid", output.getvalue())

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
