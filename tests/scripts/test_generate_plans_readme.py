from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
MODULE_PATH = SCRIPTS_DIR / "generate_plans_readme.py"
SPEC = importlib.util.spec_from_file_location("generate_plans_readme", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def registry(
    request_id: str,
    status: str = "accepted",
    *,
    requires_rfc: bool = False,
) -> str:
    noun = "Features" if request_id.startswith("F") else "Bugs"
    rfc_field = "- requires_rfc: true\n" if requires_rfc else ""
    return (
        f"# {noun}\n\n"
        f"## {request_id}: Known\n\n"
        f"- status: {status}\n"
        "- created: 2026-01-01\n"
        f"{rfc_field}"
    )


def rfc(
    rfc_id: str,
    *,
    status: str = "approved",
    version: str = "1",
    source: str = "docs/superplan/human/features.md",
) -> str:
    return (
        "---\n"
        f'id: "{rfc_id}"\n'
        f'title: "RFC {rfc_id}"\n'
        f'status: "{status}"\n'
        f"version: {version}\n"
        f'source: "{source}"\n'
        'created: "2026-01-01"\n'
        "---\n"
        "# RFC\n"
    )


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
    source: str | None = None,
    body: str = "",
) -> str:
    if source is None:
        source = {
            "feature": "docs/superplan/human/features.md",
            "bugfix": "docs/superplan/human/bugs.md",
        }.get(plan_type, "docs/superplan/human/prd.md")
    lines = [
        "---",
        f'id: "{plan_id}"',
        f'title: "{title}"',
        f'type: "{plan_type}"',
        f'status: "{status}"',
        f'created: "{created}"',
        f'summary: "{summary}"',
        f'source: "{source}"',
    ]
    if order is not None:
        lines.append(f"order: {order}")
    lines.append(f"depends_on: {depends_on}")
    lines.append("---")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


class GeneratePlansReadmeTests(unittest.TestCase):
    def _plans_dir(self, root: Path) -> Path:
        return root / "docs" / "superplan" / "plans"

    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = MODULE.run(argv)
        return code, output.getvalue()

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

    def test_write_rejects_readme_changed_after_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            readme = plans_dir / "README.md"
            write(readme, "original\n")
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First", order=1))
            real_commit = MODULE.commit_text_updates

            def conflicting_commit(updates):
                readme.write_text("external\n", encoding="utf-8")
                return real_commit(updates)

            with mock.patch.object(MODULE, "commit_text_updates", side_effect=conflicting_commit):
                code, output = self.run_cli(["--root", str(root), "--write"])

            self.assertEqual(code, 1)
            self.assertIn("changed since preflight", output)
            self.assertEqual(readme.read_text(encoding="utf-8"), "external\n")

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
source: "docs/superplan/human/prd.md"
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
            write(human, registry("F001"))
            write(plans_dir / "features" / "F001-01.md", plan(plan_id="F001-01", title="Feat", plan_type="feature", status="draft"))
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)

            write(plans_dir / "features" / "F999-01.md", plan(plan_id="F999-01", title="Feat2", plan_type="feature", status="draft"))
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_feature_plan_rejects_malformed_source_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                "# Features\n\n## F001: Missing metadata\n",
            )
            write(
                plans_dir / "features" / "F001.md",
                plan(plan_id="F001", title="Feat", plan_type="feature"),
            )

            code, output = self.run_cli(["--root", str(root), "--catalog"])

            self.assertEqual(code, 1)
            self.assertIn("features.md: F001: missing status", output)
            self.assertIn("features.md: F001: missing created", output)

    def test_proposed_request_rejects_non_superseded_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F001", "proposed"),
            )
            write(
                plans_dir / "features" / "F001.md",
                plan(plan_id="F001", title="Feat", plan_type="feature"),
            )

            code, output = self.run_cli(["--root", str(root), "--catalog"])

            self.assertEqual(code, 1)
            self.assertIn("F001: proposed request has non-superseded plans: F001 (draft)", output)

    def test_done_request_requires_complete_deliverable_plans(self) -> None:
        cases = [
            ([], "no non-superseded related plans"),
            (["complete", "in_progress"], "incomplete related plans: F001-02 (in_progress)"),
        ]
        for statuses, expected in cases:
            with self.subTest(statuses=statuses), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                plans_dir = self._plans_dir(root)
                write(
                    root / "docs" / "superplan" / "human" / "features.md",
                    registry("F001", "done"),
                )
                for index, status in enumerate(statuses, start=1):
                    write(
                        plans_dir / "features" / f"F001-{index:02d}.md",
                        plan(
                            plan_id=f"F001-{index:02d}",
                            title=f"Slice {index}",
                            plan_type="feature",
                            status=status,
                        ),
                    )

                code, output = self.run_cli(["--root", str(root), "--catalog"])

                self.assertEqual(code, 1)
                self.assertIn(f"F001: done request has {expected}", output)

    def test_valid_transitional_and_terminal_request_states(self) -> None:
        cases = [
            ("accepted", ["complete"]),
            ("done", ["complete", "complete"]),
            ("proposed", ["superseded"]),
        ]
        for request_status, plan_statuses in cases:
            with self.subTest(request_status=request_status), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                plans_dir = self._plans_dir(root)
                write(
                    root / "docs" / "superplan" / "human" / "features.md",
                    registry("F001", request_status),
                )
                for index, status in enumerate(plan_statuses, start=1):
                    write(
                        plans_dir / "features" / f"F001-{index:02d}.md",
                        plan(
                            plan_id=f"F001-{index:02d}",
                            title=f"Slice {index}",
                            plan_type="feature",
                            status=status,
                        ),
                    )

                self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 0)

    def test_rfc_required_plan_waits_for_approval_and_exact_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F001", requires_rfc=True),
            )
            plan_path = plans_dir / "features" / "F001.md"
            write(
                plan_path,
                plan(plan_id="F001", title="Feat", plan_type="feature"),
            )

            code, output = self.run_cli(["--root", str(root), "--catalog"])
            self.assertEqual(code, 1)
            self.assertIn("non-superseded plans but no RFC", output)

            rfc_path = root / "docs" / "superplan" / "rfcs" / "F001.md"
            write(rfc_path, rfc("F001", status="draft"))
            code, output = self.run_cli(["--root", str(root), "--catalog"])
            self.assertEqual(code, 1)
            self.assertIn("RFC is draft", output)

            write(rfc_path, rfc("F001"))
            code, output = self.run_cli(["--root", str(root), "--catalog"])
            self.assertEqual(code, 1)
            self.assertIn("missing exact References entry", output)

            write(
                plan_path,
                plan(
                    plan_id="F001",
                    title="Feat",
                    plan_type="feature",
                    body="## References\n- `docs/superplan/rfcs/F001.md`",
                ),
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 0)

    def test_rfc_documents_validate_metadata_ownership_and_flat_paths(self) -> None:
        cases = [
            ("version-zero", "F001.md", rfc("F001", version="0"), "positive integer"),
            ("version-text", "F001.md", rfc("F001", version="one"), "positive integer"),
            ("filename", "F002.md", rfc("F001"), "filename must match"),
            (
                "source",
                "F001.md",
                rfc("F001", source="docs/superplan/human/prd.md"),
                "RFC source must be",
            ),
        ]
        for name, filename, document, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                write(
                    root / "docs" / "superplan" / "human" / "features.md",
                    registry("F001", requires_rfc=True),
                )
                write(root / "docs" / "superplan" / "rfcs" / filename, document)

                code, output = self.run_cli(["--root", str(root), "--catalog"])

                self.assertEqual(code, 1)
                self.assertIn(expected, output)

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F001", requires_rfc=True),
            )
            write(root / "docs" / "superplan" / "rfcs" / "F001" / "rfc.md", rfc("F001"))
            code, output = self.run_cli(["--root", str(root), "--catalog"])
            self.assertEqual(code, 1)
            self.assertIn("RFC documents must use", output)

    def test_rfc_rejects_orphan_non_required_and_proposed_owners(self) -> None:
        cases = [
            (registry("F002", requires_rfc=True), "F001", "no matching feature request"),
            (registry("F001"), "F001", "not marked requires_rfc"),
            (
                registry("F001", "proposed", requires_rfc=True),
                "F001",
                "proposed feature 'F001' cannot have an RFC",
            ),
        ]
        for registry_text, rfc_id, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tempdir:
                root = Path(tempdir)
                write(
                    root / "docs" / "superplan" / "human" / "features.md",
                    registry_text,
                )
                write(root / "docs" / "superplan" / "rfcs" / f"{rfc_id}.md", rfc(rfc_id))

                code, output = self.run_cli(["--root", str(root), "--catalog"])

                self.assertEqual(code, 1)
                self.assertIn(expected, output)

    def test_qualified_rfc_and_superseded_plan_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            request_id = "F001@feature-safe"
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry(request_id, requires_rfc=True),
            )
            write(
                root / "docs" / "superplan" / "rfcs" / f"{request_id}.md",
                rfc(request_id),
            )
            write(
                self._plans_dir(root) / "features" / f"{request_id}-01.md",
                plan(
                    plan_id=f"{request_id}-01",
                    title="Qualified",
                    plan_type="feature",
                    body=f"## References\n- `docs/superplan/rfcs/{request_id}.md`",
                ),
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 0)

        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F001", requires_rfc=True),
            )
            write(
                self._plans_dir(root) / "features" / "F001.md",
                plan(
                    plan_id="F001",
                    title="Old",
                    plan_type="feature",
                    status="superseded",
                ),
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 0)

    def test_feature_source_file_must_match_type_and_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F001"),
            )
            write(
                plans_dir / "features" / "F001.md",
                plan(
                    plan_id="F001",
                    title="Wrong source",
                    plan_type="feature",
                    source="docs/superplan/human/prd.md",
                ),
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 1)

            write(
                plans_dir / "features" / "F001.md",
                plan(plan_id="F001", title="Missing registry", plan_type="feature"),
            )
            (root / "docs" / "superplan" / "human" / "features.md").unlink()
            self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 1)

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
            write(human, registry("F001"))
            write(plans_dir / "features" / "f001" / "F001-01.md", plan(plan_id="F001-01", title="A", plan_type="feature", status="complete"))
            write(plans_dir / "features" / "f001" / "F001-02.md", plan(plan_id="F001-02", title="B", plan_type="feature", status="draft"))

            # Both ids resolve to source F001 and validate against the human doc.
            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)
            generated = MODULE.generate_readme(root, plans_dir)
            self.assertIn("| `F001-01` |", generated)
            self.assertIn("| `F001-02` |", generated)

    def test_feature_ids_continue_past_three_digits(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F1000"),
            )
            write(
                plans_dir / "features" / "F1000.md",
                plan(plan_id="F1000", title="Large id", plan_type="feature"),
            )
            self.assertEqual(MODULE.run(["--root", str(root), "--catalog"]), 0)

    def test_branch_qualified_feature_plan_validates_against_human_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, registry("F001@feature-safe-01-branch"))
            write(
                plans_dir / "features" / "F001@feature-safe-01-branch.md",
                plan(
                    plan_id="F001@feature-safe-01-branch",
                    title="Branch Feat",
                    plan_type="feature",
                    status="draft",
                ),
            )

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)
            generated = MODULE.generate_readme(root, plans_dir)
            self.assertIn("| `F001@feature-safe-01-branch` |", generated)

    def test_split_branch_qualified_feature_plan_uses_branch_qualified_source(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, registry("F001@feature-safe-01-branch"))
            write(
                plans_dir / "features" / "F001@feature-safe-01-branch-01.md",
                plan(
                    plan_id="F001@feature-safe-01-branch-01",
                    title="Branch Feat Slice",
                    plan_type="feature",
                    status="draft",
                ),
            )

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 0)

    def test_branch_qualified_feature_plan_requires_matching_human_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, registry("F001@other-branch"))
            write(
                plans_dir / "features" / "F001@feature-safe-01-branch.md",
                plan(
                    plan_id="F001@feature-safe-01-branch",
                    title="Branch Feat",
                    plan_type="feature",
                    status="draft",
                ),
            )

            self.assertEqual(MODULE.run(["--root", str(root), "--write"]), 1)

    def test_no_traceability_section(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            human = root / "docs" / "superplan" / "human" / "features.md"
            write(human, registry("F001"))
            write(plans_dir / "features" / "F001-01.md", plan(plan_id="F001-01", title="A", plan_type="feature", status="draft"))

            generated = MODULE.generate_readme(root, plans_dir)
            self.assertNotIn("Traceability", generated)

    def test_catalog_emits_compact_relationship_metadata_without_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-first.md", plan(plan_id="01", title="First", status="complete", order=1, summary="First summary", body="SECRET BODY"))
            write(plans_dir / "02-second.md", plan(plan_id="02", title="Second", status="in_progress", order=2, depends_on='["01"]', summary="Second summary"))

            code, output = self.run_cli(["--root", str(root), "--catalog"])
            self.assertEqual(code, 0)
            self.assertIn("ID\tSTATUS\tTYPE\tSOURCE_ID\tSOURCE\tDEPENDS_ON\tSUMMARY\tPATH", output)
            self.assertIn("02\tin_progress\trequired\t\tdocs/superplan/human/prd.md\t01\tSecond summary\t02-second.md", output)
            self.assertNotIn("SECRET BODY", output)

    def test_catalog_filters_active_source_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(
                root / "docs" / "superplan" / "human" / "features.md",
                registry("F001"),
            )
            write(plans_dir / "features" / "F001-01.md", plan(plan_id="F001-01", title="Done slice", plan_type="feature", status="complete", source="docs/superplan/human/features.md"))
            write(plans_dir / "features" / "F001-02.md", plan(plan_id="F001-02", title="Active slice", plan_type="feature", status="in_progress", depends_on='["F001-01"]', source="docs/superplan/human/features.md"))

            code, active = self.run_cli(["--root", str(root), "--catalog", "--active"])
            self.assertEqual(code, 0)
            self.assertIn("F001-02", active)
            self.assertNotIn("F001-01\tcomplete", active)

            code, source = self.run_cli(["--root", str(root), "--catalog", "--source-id", "F001"])
            self.assertEqual(code, 0)
            self.assertIn("F001-01", source)
            self.assertIn("F001-02", source)

            code, dependency = self.run_cli(["--root", str(root), "--catalog", "--depends-on", "F001-01"])
            self.assertEqual(code, 0)
            self.assertNotIn("F001-01\tcomplete", dependency)
            self.assertIn("F001-02", dependency)

    def test_search_and_artifact_discovery_include_completed_plans(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-old.md", plan(plan_id="01", title="Old", status="complete", order=1, body="Historical tokenizer decision\n- Modify: `src/token.py`"))
            write(plans_dir / "02-new.md", plan(plan_id="02", title="New", status="draft", order=2, body="Unrelated"))

            code, searched = self.run_cli(["--root", str(root), "--search", "tokenizer"])
            self.assertEqual(code, 0)
            self.assertIn("01\tcomplete", searched)
            self.assertNotIn("02\tdraft", searched)

            code, artifact = self.run_cli(["--root", str(root), "--artifact", "src/token.py"])
            self.assertEqual(code, 0)
            self.assertIn("01\tcomplete", artifact)

    def test_discovery_still_runs_global_validation_before_filtering(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            write(plans_dir / "01-good.md", plan(plan_id="01", title="Good", status="draft", order=1))
            write(plans_dir / "02-bad.md", plan(plan_id="02", title="Bad", status="completed", order=2))

            code, output = self.run_cli(["--root", str(root), "--catalog", "--status", "draft"])
            self.assertEqual(code, 1)
            self.assertIn("unknown status 'completed'", output)

    def test_large_search_emits_only_matching_compact_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            plans_dir = self._plans_dir(root)
            for index in range(1, 151):
                marker = "needle-in-history" if index == 149 else "unrelated historical body"
                write(
                    plans_dir / f"{index:03d}-plan.md",
                    plan(
                        plan_id=f"{index:03d}",
                        title=f"Plan {index}",
                        status="complete",
                        order=index,
                        summary=f"Summary {index}",
                        body=marker + "\n" + ("detail " * 100),
                    ),
                )

            code, output = self.run_cli(
                ["--root", str(root), "--search", "needle-in-history"]
            )
            self.assertEqual(code, 0)
            self.assertIn("149\tcomplete", output)
            self.assertNotIn("148\tcomplete", output)
            self.assertNotIn("detail detail", output)


if __name__ == "__main__":
    unittest.main()
