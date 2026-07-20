from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
CLI_PATH = SCRIPTS_DIR / "install_superpowers_profile.py"


def load(name: str):
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PROFILES = load("superpowers_profiles")
INSTALLER = load("superpowers_profile_installer")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_skill(path: Path, name: str) -> None:
    write(
        path / "SKILL.md",
        f"---\nname: {name}\ndescription: test {name}\n---\n",
    )


def create_profile_repository(
    root: Path,
    *,
    validator_exit: int = 0,
    malformed_skill: str | None = None,
    extra_skill: str | None = None,
    symlink_skill: str | None = None,
) -> tuple[Path, object]:
    repository = root / "profile-repository"
    skills_root = repository / "skills" / "superpowers"
    for name in PROFILES.GPT56_PROFILE.skills:
        if name == symlink_skill:
            external_skill = root / f"external-{name}"
            write_skill(external_skill, name)
            (skills_root / name).parent.mkdir(parents=True, exist_ok=True)
            (skills_root / name).symlink_to(external_skill, target_is_directory=True)
            continue
        frontmatter_name = "wrong-name" if name == malformed_skill else name
        write_skill(skills_root / name, frontmatter_name)
    if extra_skill is not None:
        write_skill(skills_root / extra_skill, extra_skill)
    validator = skills_root / "check-context-budget.sh"
    write(validator, f"#!/usr/bin/env bash\nexit {validator_exit}\n")
    validator.chmod(0o755)

    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Test"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repository), "add", "."], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-q", "-m", "fixture"],
        check=True,
    )
    revision = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    profile = replace(
        PROFILES.GPT56_PROFILE,
        repository=str(repository),
        revision=revision,
    )
    return repository, profile


def options(root: Path, **overrides):
    values = {
        "model": "gpt-5.6",
        "skills_dir": root / "active-skills",
        "state_root": root / "state",
        "replace_existing": False,
        "dry_run": False,
    }
    values.update(overrides)
    return INSTALLER.InstallOptions(**values)


class InstallSuperpowersProfileTests(unittest.TestCase):
    def test_installer_cli_exists(self) -> None:
        self.assertTrue(CLI_PATH.is_file())

    def test_clean_install_activates_exact_profile_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)

            result = INSTALLER.install_profile(options(root), profile=profile)

            self.assertEqual(result.status, "installed")
            self.assertEqual(result.skills_dir, (root / "active-skills").resolve())
            for name in profile.skills:
                target = result.skills_dir / name
                self.assertTrue(target.is_symlink(), name)
                self.assertEqual(
                    target.resolve(),
                    result.source_dir / "skills" / "superpowers" / name,
                )
            manifest = json.loads(
                (root / "state" / PROFILES.MANIFEST_FILENAME).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["profile"], "gpt56")
            self.assertEqual(manifest["revision"], profile.revision)
            self.assertEqual(set(manifest["skills"]), set(profile.skills))

    def test_dry_run_does_not_create_state_or_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)

            result = INSTALLER.install_profile(
                options(root, dry_run=True), profile=profile
            )

            self.assertEqual(result.status, "dry-run")
            self.assertFalse((root / "state").exists())
            self.assertFalse((root / "active-skills").exists())

    def test_conflicts_are_reported_before_any_change(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            target = root / "active-skills" / "using-superpowers"
            write_skill(target, "using-superpowers")

            with self.assertRaisesRegex(INSTALLER.InstallError, "Existing skills conflict"):
                INSTALLER.install_profile(options(root), profile=profile)

            self.assertTrue(target.is_dir())
            self.assertFalse(target.is_symlink())
            self.assertFalse((root / "state").exists())

    def test_replace_existing_backs_up_all_skills_and_removes_dispatch_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            skills_dir = root / "active-skills"
            for name in profile.skills + profile.removed_skills:
                write_skill(skills_dir / name, name)

            result = INSTALLER.install_profile(
                options(root, replace_existing=True), profile=profile
            )

            self.assertIsNotNone(result.backup_dir)
            assert result.backup_dir is not None
            for name in profile.skills + profile.removed_skills:
                self.assertTrue((result.backup_dir / "skills" / name / "SKILL.md").is_file())
            for name in profile.skills:
                self.assertTrue((skills_dir / name).is_symlink())
            self.assertFalse((skills_dir / "subagent-driven-development").exists())

    def test_replace_existing_refuses_unknown_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            conflict = root / "active-skills" / "using-superpowers"
            write(conflict, "unknown")

            with self.assertRaisesRegex(INSTALLER.InstallError, "Unsafe conflict"):
                INSTALLER.install_profile(
                    options(root, replace_existing=True), profile=profile
                )

            self.assertEqual(conflict.read_text(encoding="utf-8"), "unknown")
            self.assertFalse((root / "state").exists())

    def test_validator_failure_does_not_change_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root, validator_exit=1)

            with self.assertRaisesRegex(INSTALLER.InstallError, "context-budget"):
                INSTALLER.install_profile(options(root), profile=profile)

            self.assertFalse((root / "state").exists())
            self.assertFalse((root / "active-skills").exists())

    def test_malformed_frontmatter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(
                root, malformed_skill="using-superpowers"
            )

            with self.assertRaisesRegex(INSTALLER.InstallError, "frontmatter name"):
                INSTALLER.install_profile(options(root), profile=profile)

            self.assertFalse((root / "state").exists())

    def test_extra_skill_inventory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root, extra_skill="unexpected")

            with self.assertRaisesRegex(INSTALLER.InstallError, "skill inventory"):
                INSTALLER.install_profile(options(root), profile=profile)

            self.assertFalse((root / "state").exists())

    def test_activation_failure_restores_original_tree_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            skills_dir = root / "active-skills"
            write_skill(skills_dir / "using-superpowers", "using-superpowers")
            write_skill(skills_dir / "writing-plans", "writing-plans")
            state_root = root / "state"
            state_root.mkdir()
            manifest_path = state_root / PROFILES.MANIFEST_FILENAME
            manifest_path.write_text('{"previous": true}\n', encoding="utf-8")
            manifest_alias = state_root / "previous-manifest-hardlink.json"
            manifest_alias.hardlink_to(manifest_path)

            with self.assertRaisesRegex(INSTALLER.InstallError, "Injected failure"):
                INSTALLER.install_profile(
                    options(root, replace_existing=True),
                    profile=profile,
                    fail_after="link:3",
                )

            for name in ("using-superpowers", "writing-plans"):
                target = skills_dir / name
                self.assertTrue(target.is_dir())
                self.assertFalse(target.is_symlink())
            self.assertFalse((skills_dir / "brainstorming").exists())
            self.assertEqual(
                manifest_path.read_text(encoding="utf-8"), '{"previous": true}\n'
            )
            self.assertTrue(manifest_path.samefile(manifest_alias))

    def test_same_revision_install_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            first = INSTALLER.install_profile(options(root), profile=profile)

            second = INSTALLER.install_profile(options(root), profile=profile)

            self.assertEqual(second.status, "already-active")
            self.assertEqual(second.source_dir, first.source_dir)
            self.assertEqual(second.backup_dir, first.backup_dir)

    def test_tampered_cached_checkout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            first = INSTALLER.install_profile(options(root), profile=profile)
            skill_file = (
                first.source_dir
                / "skills"
                / "superpowers"
                / "brainstorming"
                / "SKILL.md"
            )
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8") + "tampered\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(INSTALLER.InstallError, "checkout has changes"):
                INSTALLER.install_profile(options(root), profile=profile)

    def test_symlinked_cached_checkout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            first = INSTALLER.install_profile(options(root), profile=profile)
            external_checkout = root / "external-checkout"
            first.source_dir.rename(external_checkout)
            first.source_dir.symlink_to(external_checkout, target_is_directory=True)

            with self.assertRaisesRegex(
                INSTALLER.InstallError, "checkout path must not be a symlink"
            ):
                INSTALLER.install_profile(
                    options(root, replace_existing=True), profile=profile
                )

    def test_symlinked_dependency_cache_ancestor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            first = INSTALLER.install_profile(options(root), profile=profile)
            dependencies = first.source_dir.parent.parent
            external_dependencies = root / "external-dependencies"
            dependencies.rename(external_dependencies)
            dependencies.symlink_to(external_dependencies, target_is_directory=True)
            manifest_path = root / "state" / PROFILES.MANIFEST_FILENAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"] = {
                name: str(
                    (
                        first.source_dir
                        / "skills"
                        / "superpowers"
                        / name
                    ).resolve()
                )
                for name in profile.skills
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(
                INSTALLER.InstallError, "cache path must not contain symlinks"
            ):
                INSTALLER.install_profile(options(root), profile=profile)

    def test_symlinked_source_skill_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(
                root, symlink_skill="writing-skills"
            )

            with self.assertRaisesRegex(
                INSTALLER.InstallError, "skill directory boundary"
            ):
                INSTALLER.install_profile(options(root), profile=profile)

            self.assertFalse((root / "state").exists())

    def test_incomplete_manifest_is_not_treated_as_already_active(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            INSTALLER.install_profile(options(root), profile=profile)
            manifest_path = root / "state" / PROFILES.MANIFEST_FILENAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.pop("schema_version")
            manifest.pop("skills")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            result = INSTALLER.install_profile(
                options(root, replace_existing=True), profile=profile
            )

            self.assertEqual(result.status, "installed")
            repaired = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(repaired["schema_version"], PROFILES.MANIFEST_SCHEMA_VERSION)
            self.assertEqual(set(repaired["skills"]), set(profile.skills))

    def test_non_file_manifest_path_is_rejected_before_activation(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            original = root / "active-skills" / "using-superpowers"
            write_skill(original, "using-superpowers")
            manifest_path = root / "state" / PROFILES.MANIFEST_FILENAME
            manifest_path.mkdir(parents=True)

            with self.assertRaisesRegex(INSTALLER.InstallError, "Unsafe manifest path"):
                INSTALLER.install_profile(
                    options(root, replace_existing=True), profile=profile
                )

            self.assertTrue(original.is_dir())
            self.assertFalse(original.is_symlink())
            self.assertFalse((root / "state" / "backups").exists())

    def test_preexisting_manifest_temp_file_is_rejected_and_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            manifest_path = root / "state" / PROFILES.MANIFEST_FILENAME
            manifest_temp = manifest_path.with_name(f".{manifest_path.name}.tmp")
            write(manifest_temp, "user-owned temp file\n")

            with self.assertRaisesRegex(INSTALLER.InstallError, "Unsafe manifest path"):
                INSTALLER.install_profile(options(root), profile=profile)

            self.assertEqual(
                manifest_temp.read_text(encoding="utf-8"), "user-owned temp file\n"
            )
            self.assertFalse((root / "active-skills").exists())

    def test_ambiguous_existing_installations_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            home = root / "home"
            write_skill(home / ".agents" / "skills" / "using-superpowers", "using-superpowers")
            write_skill(home / ".codex" / "skills" / "using-superpowers", "using-superpowers")

            with self.assertRaisesRegex(INSTALLER.InstallError, "Multiple Superpowers installations"):
                INSTALLER.install_profile(
                    options(root, skills_dir=None), profile=profile, home=home
                )

            self.assertFalse((root / "state").exists())

    def test_no_existing_install_defaults_to_official_agents_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            _, profile = create_profile_repository(root)
            home = root / "home"

            result = INSTALLER.install_profile(
                options(root, skills_dir=None), profile=profile, home=home
            )

            self.assertEqual(result.skills_dir, (home / ".agents" / "skills").resolve())


if __name__ == "__main__":
    unittest.main()
