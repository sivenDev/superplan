from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
MODULE_PATH = SCRIPTS_DIR / "sync_agents_guardrails.py"
SPEC = importlib.util.spec_from_file_location("sync_agents_guardrails", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class SyncAgentsGuardrailsTests(unittest.TestCase):
    def test_write_creates_agents_file_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)

            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn(MODULE.START_MARKER, content)
            self.assertRegex(
                content,
                r"<!-- superplan-workspace: schema=\d+; generated-by=\d+\.\d+\.\d+ -->",
            )
            self.assertIn("# Workflow Guardrails", content)
            self.assertIn("compact human summaries/exact entries", content)
            self.assertIn("search all statuses", content)
            self.assertNotIn("# Development Rules", content)
            self.assertIn(MODULE.END_MARKER, content)

    def test_write_prepends_managed_block_without_destroying_existing_content(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(root / "AGENTS.md", "## Custom Notes\nkeep me\n")

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)

            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertTrue(content.startswith(MODULE.START_MARKER))
            self.assertIn("## Custom Notes\nkeep me\n", content)

    def test_write_updates_existing_managed_block_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "AGENTS.md",
                f"{MODULE.START_MARKER}\nold\n{MODULE.END_MARKER}\n\n## Custom Notes\nkeep me\n",
            )

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)

            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("\nold\n", content)
            self.assertIn("## Custom Notes\nkeep me\n", content)
            self.assertEqual(content.count(MODULE.START_MARKER), 1)
            self.assertEqual(content.count(MODULE.END_MARKER), 1)

    def test_check_detects_stale_file_and_passes_after_write(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(root / "AGENTS.md", "stale\n")

            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 1)
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)
            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
