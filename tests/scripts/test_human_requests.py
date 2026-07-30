from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


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
                "feature total=300 proposed=0 accepted=1 done=299 invalid=0\n",
            )


if __name__ == "__main__":
    unittest.main()
