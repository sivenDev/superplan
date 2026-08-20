from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
MODULE_PATH = SCRIPTS_DIR / "init_workspace.py"
SPEC = importlib.util.spec_from_file_location("init_workspace", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

SYNC = MODULE._load("sync_agents_guardrails")
VERSION = MODULE._load("superplan_version")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def snapshot(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def initialized_workspace(root: Path) -> None:
    code = MODULE.run(["--root", str(root)])
    if code != 0:
        raise AssertionError(f"initialization failed with {code}")


class InitWorkspaceTests(unittest.TestCase):
    def test_init_scaffolds_workspace_offline_without_home_or_profile_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            with patch.object(Path, "home", side_effect=AssertionError("home inspected")):
                self.assertEqual(MODULE.run(["--root", str(root)]), 0)

            for name in ("prd.md", "features.md", "bugs.md"):
                self.assertTrue((root / "docs" / "superplan" / "human" / name).exists())
            feature_guidance = (
                root / "docs" / "superplan" / "human" / "features.md"
            ).read_text(encoding="utf-8")
            self.assertIn("可选正文（一段话即可）", feature_guidance)
            self.assertIn("设计决策、替代方案与风险论证留给 RFC", feature_guidance)
            self.assertIn("requires_rfc: true", feature_guidance)
            self.assertIn("docs/superplan/rfcs/<feature-id>.md", feature_guidance)
            self.assertIn("docs/superplan/rfcs/<feature-id>/NN-<slug>.md", feature_guidance)
            self.assertIn("两种布局互斥", feature_guidance)
            self.assertIn("所有 RFC 批准后才能创建开发计划", feature_guidance)
            self.assertIn("计划仍需单独批准后才能编码", feature_guidance)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(SYNC.START_MARKER, agents)
            self.assertIn(VERSION.workspace_marker(), agents)
            self.assertIn("# Plans Index", (root / "docs" / "superplan" / "plans" / "README.md").read_text(encoding="utf-8"))

    def test_init_is_idempotent_and_preserves_human_and_custom_agents_content(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            initialized_workspace(root)
            features = root / "docs" / "superplan" / "human" / "features.md"
            features.write_text(
                "# Features\n\n## F001: Existing\n\n- status: proposed\n- created: 2026-07-31\n",
                encoding="utf-8",
            )
            agents = root / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\n## Custom\nkeep me\n", encoding="utf-8")

            self.assertEqual(MODULE.run(["--root", str(root)]), 0)
            self.assertEqual(
                features.read_text(encoding="utf-8"),
                "# Features\n\n## F001: Existing\n\n- status: proposed\n- created: 2026-07-31\n",
            )
            self.assertIn("## Custom\nkeep me\n", agents.read_text(encoding="utf-8"))
            self.assertEqual(agents.read_text(encoding="utf-8").count(SYNC.START_MARKER), 1)

    def test_init_runs_as_standalone_subprocess(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue((root / "docs" / "superplan" / "plans" / "README.md").exists())

    def test_help_exposes_only_workspace_options(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("--check", result.stdout)
        self.assertIn("--migrate", result.stdout)
        for obsolete in ("superpowers", "profile", "model", "state-root", "skills-dir"):
            self.assertNotIn(obsolete, result.stdout.lower())

    def test_check_current_workspace_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            initialized_workspace(root)
            before = snapshot(root)

            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 0)
            self.assertEqual(snapshot(root), before)

    def test_check_missing_or_older_schema_requires_migration_without_writing(self) -> None:
        cases = [
            f"{SYNC.START_MARKER}\n# old\n{SYNC.END_MARKER}\n",
            (
                f"{SYNC.START_MARKER}\n"
                f"<!-- superplan-workspace: schema=0; generated-by=0.1.0 -->\n"
                f"# old\n{SYNC.END_MARKER}\n"
            ),
        ]
        for content in cases:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                write(root / "AGENTS.md", content)
                before = snapshot(root)
                self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 1)
                self.assertEqual(snapshot(root), before)

    def test_check_rejects_newer_and_malformed_schema_without_writing(self) -> None:
        cases = [
            (
                f"{SYNC.START_MARKER}\n"
                f"<!-- superplan-workspace: schema={VERSION.WORKSPACE_SCHEMA_VERSION + 1}; generated-by=9.0.0 -->\n"
                f"# future\n{SYNC.END_MARKER}\n",
                2,
            ),
            (
                f"{SYNC.START_MARKER}\n"
                f"<!-- superplan-workspace: schema=nope; generated-by=bad -->\n"
                f"# broken\n{SYNC.END_MARKER}\n",
                3,
            ),
        ]
        for content, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                write(root / "AGENTS.md", content)
                before = snapshot(root)
                self.assertEqual(MODULE.run(["--root", str(root), "--check"]), expected)
                self.assertEqual(snapshot(root), before)

    def test_check_detects_stale_guardrails_but_ignores_generator_version_only(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            initialized_workspace(root)
            agents = root / "AGENTS.md"
            current = agents.read_text(encoding="utf-8")
            agents.write_text(current.replace("# Workflow Guardrails", "# Stale Guardrails"), encoding="utf-8")
            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 1)

            agents.write_text(
                current.replace(
                    f"generated-by={VERSION.SUPERPLAN_VERSION}",
                    "generated-by=0.1.0",
                ),
                encoding="utf-8",
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 0)

    def test_migrate_updates_only_managed_generated_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(root / "docs" / "superplan" / "human" / "features.md", "# Features\n\nkeep exactly\n")
            write(
                root / "AGENTS.md",
                f"{SYNC.START_MARKER}\nold\n{SYNC.END_MARKER}\n\n## Custom\nkeep exactly\n",
            )

            self.assertEqual(MODULE.run(["--root", str(root), "--migrate"]), 0)

            self.assertEqual(
                (root / "docs" / "superplan" / "human" / "features.md").read_text(encoding="utf-8"),
                "# Features\n\nkeep exactly\n",
            )
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(VERSION.workspace_marker(), agents)
            self.assertIn("## Custom\nkeep exactly\n", agents)
            self.assertTrue((root / "docs" / "superplan" / "human" / "bugs.md").exists())

    def test_migrate_never_downgrades_newer_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "AGENTS.md",
                f"{SYNC.START_MARKER}\n"
                f"<!-- superplan-workspace: schema={VERSION.WORKSPACE_SCHEMA_VERSION + 1}; generated-by=9.0.0 -->\n"
                f"future\n{SYNC.END_MARKER}\n",
            )
            before = snapshot(root)
            self.assertEqual(MODULE.run(["--root", str(root), "--migrate"]), 2)
            self.assertEqual(snapshot(root), before)

    def test_migrate_preflights_plan_generation_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "AGENTS.md",
                f"{SYNC.START_MARKER}\nold\n{SYNC.END_MARKER}\n\n## Custom\nkeep exactly\n",
            )
            write(root / "docs" / "superplan" / "plans" / "broken.md", "not frontmatter\n")
            before = snapshot(root)

            self.assertEqual(MODULE.run(["--root", str(root), "--migrate"]), 3)
            self.assertEqual(snapshot(root), before)

    def test_init_rolls_back_earlier_files_when_a_later_replace_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            safe_writes = MODULE._load("safe_writes")
            real_replace = safe_writes.os.replace
            replace_count = 0

            def fail_second_replace(source: Path, destination: Path) -> None:
                nonlocal replace_count
                replace_count += 1
                if replace_count == 2:
                    raise OSError("injected replacement failure")
                real_replace(source, destination)

            with patch.object(safe_writes.os, "replace", side_effect=fail_second_replace):
                self.assertEqual(MODULE.run(["--root", str(root)]), 3)

            self.assertEqual(snapshot(root), {})


if __name__ == "__main__":
    unittest.main()
