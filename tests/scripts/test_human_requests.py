from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
MODULE_PATH = SCRIPTS_DIR / "human_requests.py"
SPEC = importlib.util.spec_from_file_location("human_requests", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def registry(prefix: str = "F") -> str:
    noun = "Features" if prefix == "F" else "Bugs"
    return (
        f"# {noun}\n\nintro stays byte-for-byte\n\n"
        f"## {prefix}001: Proposed one\n\n"
        "- status: proposed\n"
        "- created: 2026-01-01\n\n"
        "first body\n\n"
        f"## {prefix}002@branch-safe: Accepted two\n\n"
        "- status: accepted\n"
        "- created: 2026-01-02\n\n"
        "artifact: src/export.py\n\n"
        f"## {prefix}003: Completed three\n\n"
        "- status: done\n"
        "- created: 2026-01-03\n\n"
        "large historical body should stay hidden\n"
    )


def plan_document(
    plan_id: str,
    status: str,
    *,
    created: str = "2026-01-01",
    plan_type: str = "feature",
    rfc_reference: str | None = None,
) -> str:
    source = "features.md" if plan_type == "feature" else "bugs.md"
    document = (
        "---\n"
        f'id: "{plan_id}"\n'
        f'title: "Plan {plan_id}"\n'
        f'type: "{plan_type}"\n'
        f'status: "{status}"\n'
        'summary: "Test plan."\n'
        f'source: "docs/superplan/human/{source}"\n'
        f'created: "{created}"\n'
        "depends_on: []\n"
        'parent: ""\n'
        "---\n"
    )
    if rfc_reference is not None:
        document += f"\n## References\n- `{rfc_reference}`\n"
    return document


def rfc_document(rfc_id: str, status: str) -> str:
    return (
        "---\n"
        f'id: "{rfc_id}"\n'
        f'title: "RFC {rfc_id}"\n'
        f'status: "{status}"\n'
        "version: 1\n"
        'source: "docs/superplan/human/features.md"\n'
        'created: "2026-01-01"\n'
        "---\n"
    )


def init_git(root: Path, *, date: str = "2026-01-05T12:00:00+00:00") -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Superplan Test",
            "GIT_AUTHOR_EMAIL": "superplan@example.test",
            "GIT_COMMITTER_NAME": "Superplan Test",
            "GIT_COMMITTER_EMAIL": "superplan@example.test",
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
    )
    subprocess.run(["git", "commit", "-qm", "legacy registry"], cwd=root, env=env, check=True)


class HumanRequestsTests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = MODULE.run(argv)
        return code, output.getvalue()

    def test_summary_and_default_list_emit_only_compact_active_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(root / "docs" / "superplan" / "human" / "features.md", registry())
            write(root / "docs" / "superplan" / "human" / "bugs.md", registry("B"))

            code, summary = self.run_cli(["--root", str(root), "summary"])
            self.assertEqual(code, 0)
            self.assertIn("feature total=3 proposed=1 accepted=1 done=1", summary)
            self.assertIn("bug total=3 proposed=1 accepted=1 done=1", summary)
            self.assertNotIn("large historical body", summary)

            code, listed = self.run_cli(["--root", str(root), "list", "--type", "feature"])
            self.assertEqual(code, 0)
            self.assertIn("F001\tproposed\t2026-01-01\tProposed one", listed)
            self.assertIn("F002@branch-safe\taccepted\t2026-01-02\tAccepted two", listed)
            self.assertNotIn("F003", listed)
            self.assertNotIn("first body", listed)

            code, all_entries = self.run_cli(
                ["--root", str(root), "list", "--type", "feature", "--status", "all"]
            )
            self.assertEqual(code, 0)
            self.assertIn("F003\tdone", all_entries)

    def test_summary_and_list_expose_rfc_required_features_compactly(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            content = registry().replace(
                "- created: 2026-01-02\n",
                "- created: 2026-01-02\n- requires_rfc: true\n",
                1,
            )
            write(root / "docs" / "superplan" / "human" / "features.md", content)

            code, summary = self.run_cli(
                ["--root", str(root), "summary", "--type", "feature"]
            )
            self.assertEqual(code, 0)
            self.assertIn("rfc_required=1", summary)

            code, listed = self.run_cli(
                ["--root", str(root), "list", "--type", "feature"]
            )
            self.assertEqual(code, 0)
            self.assertIn("F002@branch-safe\taccepted\t2026-01-02\tAccepted two\trfc", listed)
            self.assertNotIn("Proposed one\trfc", listed)

    def test_show_returns_one_exact_qualified_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(root / "docs" / "superplan" / "human" / "features.md", registry())

            code, shown = self.run_cli(
                ["--root", str(root), "show", "--id", "F002@branch-safe"]
            )
            self.assertEqual(code, 0)
            self.assertTrue(shown.startswith("## F002@branch-safe: Accepted two\n"))
            self.assertIn("artifact: src/export.py", shown)
            self.assertNotIn("## F001", shown)
            self.assertNotIn("## F003", shown)

    def test_set_status_changes_only_target_status_line(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = registry()
            write(path, original)
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe.md",
                plan_document("F002@branch-safe", "complete"),
            )

            code, output = self.run_cli(
                ["--root", str(root), "set-status", "--id", "F002@branch-safe", "--status", "done"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(output, "F002@branch-safe\tdone\n")
            expected = original.replace(
                "## F002@branch-safe: Accepted two\n\n- status: accepted",
                "## F002@branch-safe: Accepted two\n\n- status: done",
                1,
            )
            self.assertEqual(path.read_text(encoding="utf-8"), expected)

    def test_require_rfc_is_transactional_idempotent_and_preserves_registry_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = registry()
            write(path, original)

            args = [
                "--root",
                str(root),
                "require-rfc",
                "--id",
                "F002@branch-safe",
            ]
            code, output = self.run_cli(args)
            self.assertEqual(code, 0)
            self.assertEqual(output, "F002@branch-safe\trequires_rfc=true\n")
            updated = path.read_text(encoding="utf-8")
            expected = original.replace(
                "- created: 2026-01-02",
                "- created: 2026-01-02\n- requires_rfc: true",
                1,
            )
            self.assertEqual(updated, expected)

            code, output = self.run_cli(args)
            self.assertEqual(code, 0)
            self.assertEqual(path.read_text(encoding="utf-8"), updated)

    def test_require_rfc_replaces_false_and_rejects_late_or_non_feature_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            feature_path = root / "docs" / "superplan" / "human" / "features.md"
            content = registry().replace(
                "- created: 2026-01-01\n",
                "- created: 2026-01-01\n- requires_rfc: false\n",
                1,
            )
            write(feature_path, content)
            write(root / "docs" / "superplan" / "human" / "bugs.md", registry("B"))

            code, _ = self.run_cli(
                ["--root", str(root), "require-rfc", "--id", "F001"]
            )
            self.assertEqual(code, 0)
            self.assertIn("- requires_rfc: true", feature_path.read_text(encoding="utf-8"))

            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe.md",
                plan_document("F002@branch-safe", "draft"),
            )
            before = feature_path.read_text(encoding="utf-8")
            code, output = self.run_cli(
                ["--root", str(root), "require-rfc", "--id", "F002@branch-safe"]
            )
            self.assertEqual(code, 1)
            self.assertIn("cannot enable RFC after plan creation", output)
            self.assertEqual(feature_path.read_text(encoding="utf-8"), before)

            code, output = self.run_cli(
                ["--root", str(root), "require-rfc", "--id", "B001"]
            )
            self.assertEqual(code, 1)
            self.assertIn("valid only for features", output)

    def test_set_status_rejects_backward_or_skipped_transition_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = registry()
            write(path, original)

            code, output = self.run_cli(
                ["--root", str(root), "set-status", "--id", "F001", "--status", "done"]
            )
            self.assertEqual(code, 1)
            self.assertIn("invalid status transition", output)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_set_status_done_rejects_incomplete_split_plan_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = registry()
            write(path, original)
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe-01.md",
                plan_document("F002@branch-safe-01", "complete"),
            )
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe-02.md",
                plan_document("F002@branch-safe-02", "in_progress"),
            )

            code, output = self.run_cli(
                ["--root", str(root), "set-status", "--id", "F002@branch-safe", "--status", "done"]
            )

            self.assertEqual(code, 1)
            self.assertIn("incomplete related plans", output)
            self.assertIn("F002@branch-safe-02", output)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_set_status_done_rejects_missing_or_incomplete_single_plan(self) -> None:
        cases = [(None, "no deliverable related plans"), ("in_progress", "incomplete related plans")]
        for plan_status, expected in cases:
            with self.subTest(plan_status=plan_status), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                path = root / "docs" / "superplan" / "human" / "features.md"
                original = registry()
                write(path, original)
                if plan_status is not None:
                    write(
                        root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe.md",
                        plan_document("F002@branch-safe", plan_status),
                    )

                code, output = self.run_cli(
                    ["--root", str(root), "set-status", "--id", "F002@branch-safe", "--status", "done"]
                )

                self.assertEqual(code, 1)
                self.assertIn(expected, output)
                self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_set_status_done_ignores_superseded_sibling_after_completed_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = registry()
            write(path, original)
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe-01.md",
                plan_document("F002@branch-safe-01", "complete"),
            )
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe-02.md",
                plan_document("F002@branch-safe-02", "superseded"),
            )

            code, output = self.run_cli(
                ["--root", str(root), "set-status", "--id", "F002@branch-safe", "--status", "done"]
            )

            self.assertEqual(code, 0)
            self.assertEqual(output, "F002@branch-safe\tdone\n")
            self.assertIn("- status: done", path.read_text(encoding="utf-8"))

    def test_set_status_done_requires_approved_rfc_for_rfc_backed_feature(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = registry().replace(
                "- created: 2026-01-02\n",
                "- created: 2026-01-02\n- requires_rfc: true\n",
                1,
            )
            write(path, original)
            rfc_path_text = "docs/superplan/rfcs/F002@branch-safe.md"
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F002@branch-safe.md",
                plan_document(
                    "F002@branch-safe",
                    "complete",
                    rfc_reference=rfc_path_text,
                ),
            )

            args = [
                "--root",
                str(root),
                "set-status",
                "--id",
                "F002@branch-safe",
                "--status",
                "done",
            ]
            code, output = self.run_cli(args)
            self.assertEqual(code, 1)
            self.assertIn("no RFC", output)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

            rfc_path = root / rfc_path_text
            write(rfc_path, rfc_document("F002@branch-safe", "draft"))
            code, output = self.run_cli(args)
            self.assertEqual(code, 1)
            self.assertIn("RFC is draft", output)

            write(rfc_path, rfc_document("F002@branch-safe", "approved"))
            code, output = self.run_cli(args)
            self.assertEqual(code, 0)
            self.assertEqual(output, "F002@branch-safe\tdone\n")

    def test_validate_reports_duplicates_missing_fields_and_unknown_status(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            content = (
                "# Features\n\n"
                "## F001: First\n\n- status: proposed\n- created: 2026-01-01\n\n"
                "## F001: Duplicate\n\n- status: mystery\n\n"
            )
            write(root / "docs" / "superplan" / "human" / "features.md", content)

            code, output = self.run_cli(
                ["--root", str(root), "validate", "--type", "feature"]
            )
            self.assertEqual(code, 1)
            self.assertIn("duplicate id F001", output)
            self.assertIn("unknown status 'mystery'", output)
            self.assertIn("missing created", output)

    def test_validate_rejects_invalid_duplicate_and_bug_rfc_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                "# Features\n\n"
                "## F001: Invalid\n\n"
                "- status: accepted\n- created: 2026-01-01\n"
                "- requires_rfc: yes\n- requires_rfc: true\n",
            )
            write(
                root / "docs" / "superplan" / "human" / "bugs.md",
                "# Bugs\n\n"
                "## B001: Invalid\n\n"
                "- status: accepted\n- created: 2026-01-01\n"
                "- requires_rfc: true\n",
            )

            code, output = self.run_cli(["--root", str(root), "validate"])

            self.assertEqual(code, 1)
            self.assertIn("multiple requires_rfc fields", output)
            self.assertIn("requires_rfc is feature-only", output)

    def test_migrate_legacy_previews_then_writes_only_missing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = (
                "# Features\n\nintro stays\n\n"
                "## F001: Legacy request\n\n"
                "legacy body stays byte-for-byte\n"
            )
            write(path, original)
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F001.md",
                plan_document("F001", "complete", created="2025-12-31"),
            )

            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--type", "feature", "--check"]
            )
            self.assertEqual(code, 0)
            self.assertIn("F001\tstatus\tdone", output)
            self.assertIn("F001\tcreated\t2025-12-31", output)
            self.assertIn("plan:F001", output)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--type", "feature", "--write"]
            )
            self.assertEqual(code, 0)
            self.assertIn("migrated 1 requests (2 fields)", output)
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "# Features\n\nintro stays\n\n"
                "## F001: Legacy request\n\n"
                "- status: done\n"
                "- created: 2025-12-31\n\n"
                "legacy body stays byte-for-byte\n",
            )

            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--type", "feature", "--write"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(output, "legacy registry is current\n")

    def test_migrate_legacy_infers_status_from_all_deliverable_plan_states(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            original = (
                "# Features\n\n"
                "## F001: Complete\n\n- created: 2026-01-01\n\n"
                "## F002: Active\n\n- created: 2026-01-02\n\n"
                "## F003: No delivery\n\n- created: 2026-01-03\n"
            )
            write(path, original)
            plans_dir = root / "docs" / "superplan" / "plans" / "features"
            write(plans_dir / "F001-01.md", plan_document("F001-01", "complete"))
            write(plans_dir / "F001-02.md", plan_document("F001-02", "complete"))
            write(plans_dir / "F002.md", plan_document("F002", "blocked"))
            write(plans_dir / "F003.md", plan_document("F003", "superseded"))

            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--type", "feature", "--write"]
            )
            self.assertEqual(code, 0)
            self.assertIn("F001\tstatus\tdone", output)
            self.assertIn("F002\tstatus\taccepted", output)
            self.assertIn("F003\tstatus\tproposed", output)
            migrated = path.read_text(encoding="utf-8")
            self.assertIn("## F001: Complete\n\n- status: done\n- created:", migrated)
            self.assertIn("## F002: Active\n\n- status: accepted\n- created:", migrated)
            self.assertIn("## F003: No delivery\n\n- status: proposed\n- created:", migrated)

    def test_migrate_legacy_created_uses_plan_before_git_history(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            write(
                path,
                "# Features\n\n"
                "## F001: Plan dated\n\n- status: accepted\n\n"
                "## F002: Git dated\n\n- status: proposed\n",
            )
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F001.md",
                plan_document("F001", "in_progress", created="2026-01-02"),
            )
            init_git(root, date="2026-01-05T12:00:00+00:00")

            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--type", "feature", "--check"]
            )
            self.assertEqual(code, 0)
            self.assertIn("F001\tcreated\t2026-01-02\tplan:F001", output)
            self.assertIn("F002\tcreated\t2026-01-05\tgit:first-appearance", output)

    def test_migrate_legacy_rejects_unresolved_or_blocking_state_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            feature_path = root / "docs" / "superplan" / "human" / "features.md"
            bug_path = root / "docs" / "superplan" / "human" / "bugs.md"
            feature_original = "# Features\n\n## F001: Resolvable\n\nlegacy\n"
            bug_original = "# Bugs\n\n## B001: Unresolved date\n\n- status: proposed\n"
            write(feature_path, feature_original)
            write(bug_path, bug_original)
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F001.md",
                plan_document("F001", "complete", created="2026-01-01"),
            )

            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--write"]
            )
            self.assertEqual(code, 1)
            self.assertIn("B001\tcreated\tunresolved\tno-plan-or-git-evidence", output)
            self.assertEqual(feature_path.read_text(encoding="utf-8"), feature_original)
            self.assertEqual(bug_path.read_text(encoding="utf-8"), bug_original)

            write(
                bug_path,
                "# Bugs\n\n"
                "## B001: Broken\n\n- status: mystery\n"
                "## B001: Duplicate\n",
            )
            code, output = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--check"]
            )
            self.assertEqual(code, 1)
            self.assertIn("unknown status 'mystery'", output)
            self.assertIn("duplicate id B001", output)
            self.assertEqual(feature_path.read_text(encoding="utf-8"), feature_original)

    def test_migrate_legacy_rolls_back_an_earlier_registry_on_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            feature_path = root / "features.md"
            bug_path = root / "bugs.md"
            write(feature_path, "feature original\n")
            write(bug_path, "bug original\n")
            migrations = [
                MODULE.RegistryMigration(feature_path, "feature original\n", "feature updated\n"),
                MODULE.RegistryMigration(bug_path, "bug original\n", "bug updated\n"),
            ]
            original_replace = os.replace
            failed = False

            def flaky_replace(source, destination):
                nonlocal failed
                if Path(destination) == bug_path and not failed:
                    failed = True
                    raise OSError("simulated second write failure")
                return original_replace(source, destination)

            with mock.patch("safe_writes.os.replace", side_effect=flaky_replace):
                with self.assertRaisesRegex(OSError, "simulated second write failure"):
                    MODULE.write_registry_migrations(migrations)

            self.assertEqual(feature_path.read_text(encoding="utf-8"), "feature original\n")
            self.assertEqual(bug_path.read_text(encoding="utf-8"), "bug original\n")

    def test_record_remains_strict_until_legacy_migration_completes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            path = root / "docs" / "superplan" / "human" / "features.md"
            write(path, "# Features\n\n## F001: Legacy\n\nbody\n")
            write(
                root / "docs" / "superplan" / "plans" / "features" / "F001.md",
                plan_document("F001", "complete", created="2026-01-01"),
            )

            code, output = self.run_cli(
                ["--root", str(root), "record", "--type", "feature", "--title", "Blocked"]
            )
            self.assertEqual(code, 1)
            self.assertIn("registry validation failed", output)

            code, _ = self.run_cli(
                ["--root", str(root), "migrate-legacy", "--write"]
            )
            self.assertEqual(code, 0)
            code, output = self.run_cli(
                ["--root", str(root), "record", "--type", "feature", "--title", "Allowed"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(output, "F002\n")

    def test_record_supports_qualified_numbering_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(root / "docs" / "superplan" / "human" / "features.md", registry())

            code, output = self.run_cli(
                [
                    "--root",
                    str(root),
                    "record",
                    "--type",
                    "feature",
                    "--title",
                    "Fourth",
                    "--status",
                    "accepted",
                    "--date",
                    "2026-01-04",
                ]
            )
            self.assertEqual(code, 0)
            self.assertEqual(output, "F004\n")
            self.assertIn("## F004: Fourth", (root / "docs" / "superplan" / "human" / "features.md").read_text(encoding="utf-8"))

    def test_competing_record_processes_preserve_both_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry_path = root / "docs" / "superplan" / "human" / "features.md"
            write(registry_path, "# Features\n")
            commands = [
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--root",
                    str(root),
                    "record",
                    "--type",
                    "feature",
                    "--title",
                    title,
                    "--date",
                    "2026-07-31",
                ]
                for title in ("Concurrent A", "Concurrent B")
            ]

            processes = [
                subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for command in commands
            ]
            results = [process.communicate(timeout=10) for process in processes]

            for process, (_, stderr) in zip(processes, results):
                self.assertEqual(process.returncode, 0, msg=stderr)
            self.assertEqual({stdout.strip() for stdout, _ in results}, {"F001", "F002"})
            content = registry_path.read_text(encoding="utf-8")
            self.assertIn("## F001:", content)
            self.assertIn("## F002:", content)
            self.assertIn("Concurrent A", content)
            self.assertIn("Concurrent B", content)

    def test_numbering_continues_past_three_digits(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                "# Features\n\n## F999: Existing\n\n"
                "- status: done\n- created: 2026-01-01\n",
            )
            code, output = self.run_cli(
                ["--root", str(root), "record", "--type", "feature", "--title", "Next"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(output, "F1000\n")

    def test_record_rejects_invalid_date_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            code, output = self.run_cli(
                [
                    "--root",
                    str(root),
                    "record",
                    "--type",
                    "feature",
                    "--title",
                    "Bad date",
                    "--date",
                    "tomorrow",
                ]
            )
            self.assertEqual(code, 1)
            self.assertIn("invalid date", output)
            self.assertFalse(
                (root / "docs" / "superplan" / "human" / "features.md").exists()
            )

    def test_large_registry_summary_output_does_not_scale_with_history_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            entries = ["# Features\n"]
            for index in range(1, 301):
                status = "accepted" if index == 300 else "done"
                entries.append(
                    f"\n## F{index:03d}: Item {index}\n\n"
                    f"- status: {status}\n- created: 2026-01-01\n\n"
                    + ("historical detail " * 200)
                    + "\n"
                )
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                "".join(entries),
            )

            code, output = self.run_cli(
                ["--root", str(root), "summary", "--type", "feature"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(
                output,
                "feature total=300 proposed=0 accepted=1 done=299 invalid=0 rfc_required=0\n",
            )


if __name__ == "__main__":
    unittest.main()
