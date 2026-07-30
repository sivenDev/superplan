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


def skill_name(path: Path) -> str:
    match = re.search(r"^name:\s*([^\n]+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing skill name in {path}")
    return match.group(1).strip().strip('"\'')


class PluginPackageTests(unittest.TestCase):
    def test_manifests_share_version_and_use_default_skill_discovery(self) -> None:
        version = load_version_module().SUPERPLAN_VERSION
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

        self.assertEqual(version, "0.3.0")
        self.assertNotIn("skills", codex)
        self.assertEqual(codex["version"], version)
        self.assertEqual(claude["version"], version)
        self.assertEqual(marketplace["plugins"][0]["version"], version)

    def test_package_exposes_exactly_four_root_superplan_skills(self) -> None:
        skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual({path.parent.name for path in skill_paths}, EXPECTED_SKILLS)
        self.assertEqual({skill_name(path) for path in skill_paths}, EXPECTED_SKILLS)
        self.assertFalse((ROOT / "deps" / "superpowers").exists())
        self.assertFalse((ROOT / "deps" / "superpowers.lock.json").exists())

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
