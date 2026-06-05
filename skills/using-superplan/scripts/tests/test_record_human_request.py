from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "record_human_request.py"
SPEC = importlib.util.spec_from_file_location("record_human_request", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RecordHumanRequestTests(unittest.TestCase):
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

    def test_bug_numbering_is_independent_from_features(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            MODULE.run(["--root", str(root), "--type", "feature", "--title", "Feat"])
            MODULE.run(["--root", str(root), "--type", "bug", "--title", "Crash on save"])

            bugs = (root / "docs" / "superplan" / "human" / "bugs.md").read_text(encoding="utf-8")
            self.assertTrue(bugs.startswith("# Bugs"))
            self.assertIn("## B001: Crash on save", bugs)

    def test_empty_title_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / "docs").mkdir()

            self.assertEqual(
                MODULE.run(["--root", str(root), "--type", "feature", "--title", "   "]), 1
            )


if __name__ == "__main__":
    unittest.main()
