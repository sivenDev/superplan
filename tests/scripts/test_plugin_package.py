from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
VERSION_PATH = SCRIPTS_DIR / "superplan_version.py"
EXPECTED_SKILLS = {
    "bugfix-plan-and-delivery",
    "feature-plan-and-delivery",
    "project-bootstrap-from-prd",
    "using-superplan",
}


def load_version_module():
    spec = importlib.util.spec_from_file_location("superplan_version", VERSION_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def skill_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", content, re.DOTALL)
    if match is None:
        raise AssertionError(f"missing or malformed frontmatter in {path}")

    metadata: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line:
            raise AssertionError(f"malformed frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            raise AssertionError(f"duplicate frontmatter key in {path}: {key}")
        metadata[key] = value.strip().strip('"\'')
    return metadata


class PluginPackageTests(unittest.TestCase):
    def test_manifests_share_version_and_use_default_skill_discovery(self) -> None:
        version = load_version_module().SUPERPLAN_VERSION
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        codex_version_pattern = re.compile(
            rf"\A{re.escape(version)}(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z"
        )

        self.assertEqual(version, "0.6.0")
        self.assertEqual(load_version_module().WORKSPACE_SCHEMA_VERSION, 1)
        self.assertNotIn("skills", codex)
        self.assertRegex(codex["version"], codex_version_pattern)
        self.assertNotRegex("999.0.0+codex.1", codex_version_pattern)
        self.assertNotRegex(f"{version}+codex..1", codex_version_pattern)
        self.assertEqual(claude["version"], version)
        self.assertEqual(marketplace["plugins"][0]["version"], version)
        self.assertIn(
            f"generated-by={version}",
            (ROOT / "README.md").read_text(encoding="utf-8"),
        )

    def test_package_exposes_exactly_four_root_superplan_skills(self) -> None:
        skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual({path.parent.name for path in skill_paths}, EXPECTED_SKILLS)
        metadata = {path.parent.name: skill_frontmatter(path) for path in skill_paths}
        self.assertEqual({values["name"] for values in metadata.values()}, EXPECTED_SKILLS)
        for folder, values in metadata.items():
            self.assertEqual(set(values), {"name", "description"})
            self.assertEqual(values["name"], folder)
            self.assertTrue(values["description"])
        self.assertFalse((ROOT / "deps" / "superpowers").exists())
        self.assertFalse((ROOT / "deps" / "superpowers.lock.json").exists())

        feature_skill = ROOT / "skills" / "feature-plan-and-delivery" / "SKILL.md"
        rfc_reference = feature_skill.parent / "references" / "rfc-spec.md"
        feature_skill_content = feature_skill.read_text(encoding="utf-8")
        normalized_feature_skill = " ".join(feature_skill_content.split())
        self.assertIn("references/rfc-spec.md", feature_skill_content)
        self.assertTrue(rfc_reference.is_file())
        rfc_spec = rfc_reference.read_text(encoding="utf-8")
        for duplicated_procedure in (
            "full cumulative test",
            "category or keyword matches are insufficient",
            "borderline cases ask one concise clarification",
            "human_requests.py require-rfc",
        ):
            self.assertNotIn(duplicated_procedure, normalized_feature_skill)
        for contract in (
            "docs/superplan/rfcs/<feature-id>.md",
            "docs/superplan/rfcs/<feature-id>/01-<slug>.md",
            'id: "F001-R01"',
            'feature: "F001"',
            "平铺文件与目录互斥",
            "所有 RFC 都为 `approved`",
            "默认使用中文",
            "version: 1",
            "draft -> approved",
            "Git 是默认修订历史",
            "不保存逐轮对话",
            "自主启用 RFC 必须同时满足",
            "具体、未解决的设计决策",
            "难以逆转的选择",
            "错误选择会改变验收",
            "一次澄清、保守默认或普通开发计划",
            "类别或关键词命中",
            "可逆的内部实现选择",
            "边界情况先提出一个简短澄清问题",
        ):
            self.assertIn(contract, rfc_spec)

    def test_skill_metadata_partitions_setup_and_delivery_triggers(self) -> None:
        skill_paths = {
            path.parent.name: path for path in (ROOT / "skills").glob("*/SKILL.md")
        }
        descriptions = {
            name: skill_frontmatter(path)["description"].lower()
            for name, path in skill_paths.items()
        }

        using_description = descriptions["using-superplan"]
        for intent in ("initialize", "check", "migrate", "explicit", "fallback"):
            self.assertIn(intent, using_description)
        self.assertIn("prd", descriptions["project-bootstrap-from-prd"])
        self.assertIn("feature", descriptions["feature-plan-and-delivery"])
        self.assertIn("bug", descriptions["bugfix-plan-and-delivery"])

        using_content = skill_paths["using-superplan"].read_text(encoding="utf-8")
        self.assertIn("## Fallback Routing", using_content)
        self.assertNotIn("## Route Entry", using_content)
        for route in EXPECTED_SKILLS - {"using-superplan"}:
            self.assertIn(f"${route}", using_content)
            self.assertIn("delivery-loop.md", skill_paths[route].read_text(encoding="utf-8"))

        ui_path = ROOT / "skills" / "using-superplan" / "agents" / "openai.yaml"
        ui = ui_path.read_text(encoding="utf-8")
        self.assertIn("$using-superplan", ui)
        self.assertNotIn("allow_implicit_invocation: false", ui)
        for line in ui.splitlines():
            if line.startswith("  ") and ":" in line:
                self.assertRegex(line, r'^  [a-z_]+: ".*"$')

        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("initialize", codex["interface"]["longDescription"].lower())
        self.assertIn("migrate", codex["interface"]["longDescription"].lower())

    def test_project_bootstrap_uses_the_versioned_workspace_entry(self) -> None:
        content = (ROOT / "skills" / "project-bootstrap-from-prd" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("delivery-loop.md", content)
        self.assertNotIn("sync_agents_guardrails.py", content)

    def test_shared_references_keep_process_depth_proportional(self) -> None:
        references = ROOT / "skills" / "using-superplan" / "references"
        delivery = (references / "delivery-loop.md").read_text(encoding="utf-8")
        state_machine = delivery.split("## Delivery State Machine", 1)[1].split(
            "## Managed Guardrails", 1
        )[0]
        phases = re.findall(r"^\d+\. \*\*(.+?):\*\*", state_machine, re.MULTILINE)
        self.assertEqual(
            phases,
            [
                "Safety and compatibility",
                "Intake or diagnosis",
                "Draft and approval",
                "Implementation",
                "Verification and progress completion",
                "Commit and optional worktree handoff",
            ],
        )

        plan_spec = (references / "plan-spec.md").read_text(encoding="utf-8")
        for required in (
            "`Goal`",
            "`Scope`",
            "`Non-Goals`",
            "`Exit Criteria`",
            "`Outcome`",
            "`Files`",
            "`Verification`",
        ):
            self.assertIn(required, plan_spec)
        for conditional in ("`Architecture`", "`Baseline`", "`Change Map`"):
            self.assertIn(conditional, plan_spec)
        self.assertIn("Existing plans remain valid", plan_spec)
        self.assertIn("`Reproduction` and `Root Cause`", plan_spec)

        verification = (references / "verification-matrix.md").read_text(
            encoding="utf-8"
        )
        for phase in ("Focused", "Final", "Metadata-only"):
            self.assertIn(f"**{phase}:**", verification)
        self.assertEqual(verification.count("python3 tools/verify_repo.py"), 1)
        self.assertIn("do not list or rerun", verification)

    def test_current_package_surfaces_do_not_claim_external_runtime(self) -> None:
        paths = [
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / "README.md",
            ROOT / "docs" / "install.md",
        ]
        paths.extend((ROOT / "skills").rglob("*.md"))

        stale = {
            path.relative_to(ROOT).as_posix(): line
            for path in paths
            for line in path.read_text(encoding="utf-8").splitlines()
            if "superpowers" in line.lower() or "superworkflow" in line.lower()
        }
        self.assertEqual(stale, {})

    def test_repository_verification_entry_is_authoritative(self) -> None:
        command = "python3 tools/verify_repo.py"
        self.assertTrue((ROOT / "tools" / "verify_repo.py").is_file())
        self.assertIn(command, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn(
            command,
            (ROOT / "skills" / "using-superplan" / "references" / "verification-matrix.md").read_text(
                encoding="utf-8"
            ),
        )
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count(command), 1)
        self.assertIn('python-version: ["3.10", "3.14"]', workflow)


if __name__ == "__main__":
    unittest.main()
