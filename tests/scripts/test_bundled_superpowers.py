from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
VERSION_PATH = SCRIPTS_DIR / "superplan_version.py"


def load_version_module():
    spec = importlib.util.spec_from_file_location("superplan_version", VERSION_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(entries: list[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for relative, sha256 in entries:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256.encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


class BundledSuperpowersTests(unittest.TestCase):
    def test_lock_matches_exact_bundled_runtime_tree(self) -> None:
        lock = json.loads((ROOT / "deps" / "superpowers.lock.json").read_text(encoding="utf-8"))
        dependency = ROOT / "deps" / "superpowers"
        actual_paths = sorted(
            path.relative_to(dependency).as_posix()
            for path in dependency.rglob("*")
            if path.is_file()
        )
        locked_paths = [entry["path"] for entry in lock["files"]]
        self.assertEqual(actual_paths, locked_paths)
        entries = [(path, file_hash(dependency / path)) for path in actual_paths]
        self.assertEqual([sha for _, sha in entries], [entry["sha256"] for entry in lock["files"]])
        self.assertEqual(tree_hash(entries), lock["tree_sha256"])
        self.assertEqual(
            sorted(path.parent.name for path in dependency.glob("*/SKILL.md")),
            lock["skills"],
        )
        self.assertEqual(lock["revision"], "aa973775906c8761a78019aaa21e4f0ccd987925")

    def test_dependency_contains_only_skill_runtime_content(self) -> None:
        dependency = ROOT / "deps" / "superpowers"
        self.assertFalse((dependency / "sync-skills.sh").exists())
        self.assertFalse((dependency / "check-context-budget.sh").exists())
        self.assertEqual(len(list(dependency.glob("*/SKILL.md"))), 13)

    def test_plugin_discovers_default_and_bundled_skills_with_one_version(self) -> None:
        version = load_version_module().SUPERPLAN_VERSION
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

        self.assertEqual(codex["skills"], "./deps/superpowers/")
        self.assertEqual(codex["version"], version)
        self.assertEqual(claude["version"], version)
        self.assertEqual(marketplace["plugins"][0]["version"], version)

        default_names = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        bundled_names = {path.parent.name for path in (ROOT / "deps" / "superpowers").glob("*/SKILL.md")}
        self.assertEqual(len(default_names), 4)
        self.assertEqual(len(bundled_names), 13)
        self.assertFalse(default_names & bundled_names)


if __name__ == "__main__":
    unittest.main()
