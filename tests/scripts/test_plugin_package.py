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

        self.assertEqual(version, "0.3.1")
        self.assertEqual(load_version_module().WORKSPACE_SCHEMA_VERSION, 1)
        self.assertNotIn("skills", codex)
        self.assertEqual(codex["version"], version)
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

    def test_using_superplan_metadata_covers_setup_and_delivery_triggers(self) -> None:
        metadata = skill_frontmatter(ROOT / "skills" / "using-superplan" / "SKILL.md")
        description = metadata["description"].lower()
        for intent in ("initialize", "check", "migrate", "project", "feature", "bug"):
            self.assertIn(intent, description)

        ui = (ROOT / "skills" / "using-superplan" / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("initialize", ui)
        self.assertIn("migrate", ui)

        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn("initialize", codex["interface"]["longDescription"].lower())
        self.assertIn("migrate", codex["interface"]["longDescription"].lower())

    def test_project_bootstrap_uses_the_versioned_workspace_entry(self) -> None:
        content = (ROOT / "skills" / "project-bootstrap-from-prd" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("delivery-loop.md", content)
        self.assertNotIn("sync_agents_guardrails.py", content)

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


if __name__ == "__main__":
    unittest.main()
