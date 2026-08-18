from __future__ import annotations

import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
MODULE_PATH = SCRIPTS_DIR / "record_human_request.py"
SPEC = importlib.util.spec_from_file_location("record_human_request", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RecordHumanRequestTests(unittest.TestCase):
    def test_module_is_a_compatibility_adapter(self) -> None:
        import human_requests

        self.assertIs(MODULE.next_id, human_requests.next_id)
        self.assertIs(MODULE.render_entry, human_requests.render_entry)

    def make_linked_worktree(self, tempdir: str, branch: str = "feature/safe-01") -> Path:
        root = Path(tempdir) / "repo"
        linked = Path(tempdir) / "linked"
        root.mkdir()
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "user.email", "tests@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Tests"], cwd=root, check=True)
        (root / "docs").mkdir()
        (root / "docs" / ".keep").write_text("", encoding="utf-8")
        subprocess.run(["git", "add", "docs/.keep"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(linked)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return linked

    def test_first_feature_gets_f001_with_heading_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            code = MODULE.run(
                ["--root", str(root), "--type", "feature", "--title", "Dark mode", "--date", "2026-05-29"]
            )
            self.assertEqual(code, 0)

            content = (root / "docs" / "superplan" / "human" / "features.md").read_text(encoding="utf-8")
            self.assertTrue(content.startswith("# Features"))
            self.assertIn("## F001: Dark mode", content)
            self.assertIn("- status: proposed", content)
            self.assertIn("- created: 2026-05-29", content)

    def test_explicit_accepted_status_is_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--type",
                    "feature",
                    "--title",
                    "Approved intake",
                    "--status",
                    "accepted",
                    "--date",
                    "2026-07-21",
                ]
            )
            self.assertEqual(code, 0)

            content = (root / "docs" / "superplan" / "human" / "features.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## F001: Approved intake", content)
            self.assertIn("- status: accepted", content)
            self.assertNotIn("- status: proposed", content)

    def test_feature_can_be_recorded_as_rfc_required(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--type",
                    "feature",
                    "--title",
                    "Risky feature",
                    "--requires-rfc",
                ]
            )

            self.assertEqual(code, 0)
            content = (root / "docs" / "superplan" / "human" / "features.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("- requires_rfc: true", content)

    def test_bug_rejects_requires_rfc_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            code = MODULE.run(
                [
                    "--root",
                    str(root),
                    "--type",
                    "bug",
                    "--title",
                    "Crash",
                    "--requires-rfc",
                ]
            )

            self.assertEqual(code, 1)
            self.assertFalse((root / "docs" / "superplan" / "human" / "bugs.md").exists())

    def test_unsupported_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            with redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as context:
                    MODULE.run(
                        [
                            "--root",
                            str(root),
                            "--type",
                            "feature",
                            "--title",
                            "Invalid status",
                            "--status",
                            "done",
                        ]
                    )

            self.assertEqual(context.exception.code, 2)
            self.assertFalse((root / "docs" / "superplan" / "human" / "features.md").exists())

    def test_second_feature_increments_to_f002(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            MODULE.run(["--root", str(root), "--type", "feature", "--title", "One"])
            MODULE.run(["--root", str(root), "--type", "feature", "--title", "Two", "--body", "details"])

            content = (root / "docs" / "superplan" / "human" / "features.md").read_text(encoding="utf-8")
            self.assertIn("## F001: One", content)
            self.assertIn("## F002: Two", content)
            self.assertIn("details", content)
            self.assertLess(content.index("## F001"), content.index("## F002"))

    def test_body_escaped_newlines_render_as_markdown_lines(self) -> None:
        cases = [
            ("first line\\nsecond line", "first line\nsecond line"),
            ("first line\\r\\nsecond line", "first line\nsecond line"),
        ]
        for raw_body, expected_body in cases:
            with self.subTest(raw_body=raw_body):
                with tempfile.TemporaryDirectory() as tempdir:
                    root = Path(tempdir)
                    (root / "docs").mkdir()

                    code = MODULE.run(
                        [
                            "--root",
                            str(root),
                            "--type",
                            "feature",
                            "--title",
                            "Multi-line",
                            "--body",
                            raw_body,
                            "--date",
                            "2026-07-07",
                        ]
                    )
                    self.assertEqual(code, 0)

                    content = (
                        root / "docs" / "superplan" / "human" / "features.md"
                    ).read_text(encoding="utf-8")
                    self.assertIn(expected_body, content)
                    self.assertNotIn(raw_body, content)

    def test_bug_numbering_is_independent_from_features(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            MODULE.run(["--root", str(root), "--type", "feature", "--title", "Feat"])
            MODULE.run(["--root", str(root), "--type", "bug", "--title", "Crash on save"])

            bugs = (root / "docs" / "superplan" / "human" / "bugs.md").read_text(encoding="utf-8")
            self.assertTrue(bugs.startswith("# Bugs"))
            self.assertIn("## B001: Crash on save", bugs)

    def test_linked_worktree_feature_id_includes_branch_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = self.make_linked_worktree(tempdir, branch="feature/safe-01")

            code = MODULE.run(
                ["--root", str(root), "--type", "feature", "--title", "Worktree feature", "--date", "2026-05-29"]
            )
            self.assertEqual(code, 0)

            content = (root / "docs" / "superplan" / "human" / "features.md").read_text(encoding="utf-8")
            self.assertIn("## F001@feature-safe-01-branch: Worktree feature", content)

    def test_linked_worktree_bug_id_includes_branch_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = self.make_linked_worktree(tempdir, branch="fix/crash")

            code = MODULE.run(
                ["--root", str(root), "--type", "bug", "--title", "Crash", "--date", "2026-05-29"]
            )
            self.assertEqual(code, 0)

            content = (root / "docs" / "superplan" / "human" / "bugs.md").read_text(encoding="utf-8")
            self.assertIn("## B001@fix-crash: Crash", content)

    def test_next_id_counts_branch_qualified_entries(self) -> None:
        content = "# Features\n\n## F001@feature-safe-01-branch: Existing\n"

        self.assertEqual(MODULE.next_id(content, "F"), "F002")

    def test_empty_title_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            self.assertEqual(
                MODULE.run(["--root", str(root), "--type", "feature", "--title", "   "]), 1
            )


if __name__ == "__main__":
    unittest.main()
