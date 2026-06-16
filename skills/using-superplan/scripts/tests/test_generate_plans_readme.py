from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "generate_plans_readme.py"
SPEC = importlib.util.spec_from_file_location("generate_plans_readme", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def plan(
    *,
    plan_id: str,
    title: str,
    plan_type: str = "required",
    status: str = "draft",
    order: int | None = None,
    created: str = "2026-01-01",
    depends_on: str = "[]",
    summary: str = "Summary.",
) -> str:
    lines = [
        "---",
        f'id: "{plan_id}"',
        f'title: "{title}"',
        f'type: "{plan_type}"',
        f'status: "{status}"',
        f'created: "{created}"',
        f'summary: "{summary}"',
    ]
    if order is not None:
        lines.append(f"order: {order}")
    lines.append(f"depends_on: {depends_on}")
    lines.append("---")
    lines.append(f"# {title}")
    lines.append("")
    return "\n".join(lines)


class GeneratePlansReadmeTests(unittest.TestCase):
    def _plans_dir(self, root: Path) -> Path:
        return root / "docs" / "superplan" / "plans"

    def test_generate_readme_includes_groups_order_and_created(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First Plan", status="complete", order=1, created="2026-01-01", summary="First summary."))
            write(plans_dir / "09-future.md", plan(plan_id="09", title="Future Plan", plan_type="future", status="in_progress", order=9, created="2026-02-02", summary="Future summary."))

            generated = MODULE.generate_readme(root, plans_dir)

            # Only statuses with counts appear (Draft/Approved/Blocked/Superseded omitted).
            self.assertIn("| Type | Plans | In Progress | Complete |", generated)
            self.assertIn("| `required` | 1 | 0 | 1 |", generated)
            self.assertIn("| `future` | 1 | 1 | 0 |", generated)
            self.assertIn(
                "| `01` | [First Plan](01-first.md) | `complete` | 2026-01-01 |",
                generated,
            )
            self.assertNotIn("First summary.", generated)
            self.assertIn(
                "1. `01` [First Plan](01-first.md) - `complete` (2026-01-01)",
                generated,
            )

    def test_check_detects_and_fixes_stale_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "README.md", "# stale\n")
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First Plan", status="draft", order=1))

            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 1)
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)
            self.assertEqual(MODULE.run(["--root", str(root), "--check"]), 0)

    def test_combined_write_and_check_fixes_stale_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "README.md", "# stale\n")
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First Plan", status="draft", order=1))

            self.assertEqual(MODULE.run(["--root", str(root), "--write", "--check"]), 0)

    def test_combined_write_and_check_still_fails_on_invalid_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First Plan", status="completed", order=1))

            self.assertEqual(MODULE.run(["--root", str(root), "--write", "--check"]), 1)

    def test_check_fails_on_unknown_status(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First Plan", status="completed", order=1))

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_missing_created_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                plans_dir / "01-first.md",
                """---
id: "01"
title: "First Plan"
type: "required"
status: "draft"
summary: "Summary."
order: 1
---
# First Plan
""",
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_feature_id_must_encode_source(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "features" / "01-x.md", plan(plan_id="f01", title="Feat", plan_type="feature", status="draft"))

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_source_derived_from_id_must_exist_in_human_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, "# Features\n\n## F001: Known\n")
            write(plans_dir / "features" / "F001-01.md", plan(plan_id="F001-01", title="Feat", plan_type="feature", status="draft"))
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)

            write(plans_dir / "features" / "F999-01.md", plan(plan_id="F999-01", title="Feat2", plan_type="feature", status="draft"))
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_depends_on_unknown_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First", order=1, depends_on='["99"]'))

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_depends_on_cycle_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-a.md", plan(plan_id="01", title="A", order=1, depends_on='["02"]'))
            write(plans_dir / "02-b.md", plan(plan_id="02", title="B", order=2, depends_on='["01"]'))

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_complete_cannot_depend_on_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-a.md", plan(plan_id="01", title="A", status="in_progress", order=1))
            write(plans_dir / "02-b.md", plan(plan_id="02", title="B", status="complete", order=2, depends_on='["01"]'))

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_execution_order_respects_depends_on(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-b.md", plan(plan_id="01", title="B", status="draft", order=1, depends_on='["02"]'))
            write(plans_dir / "02-a.md", plan(plan_id="02", title="A", status="draft", order=2))

            generated = MODULE.generate_readme(root, plans_dir)
            self.assertLess(
                generated.index("1. `02` [A]"),
                generated.index("2. `01` [B]"),
            )

    def test_split_feature_plans_share_one_source(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, "# Features\n\n## F001: Known\n")
            write(plans_dir / "features" / "f001" / "F001-01.md", plan(plan_id="F001-01", title="A", plan_type="feature", status="complete"))
            write(plans_dir / "features" / "f001" / "F001-02.md", plan(plan_id="F001-02", title="B", plan_type="feature", status="draft"))

            # Both ids resolve to source F001 and validate against the human doc.
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)
            generated = MODULE.generate_readme(root, plans_dir)
            self.assertIn("| `F001-01` |", generated)
            self.assertIn("| `F001-02` |", generated)

    def test_no_traceability_section(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, "# Features\n\n## F001: Known\n")
            write(plans_dir / "features" / "F001-01.md", plan(plan_id="F001-01", title="A", plan_type="feature", status="draft"))

            generated = MODULE.generate_readme(root, plans_dir)
            self.assertNotIn("Traceability", generated)


if __name__ == "__main__":
    unittest.main()
