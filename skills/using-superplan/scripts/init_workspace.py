#!/usr/bin/env python3
"""Initialize a Superplan workspace.

Idempotently scaffolds the docs structure, installs the managed AGENTS.md
guardrails, and generates the plans index:

- docs/superplan/human/{prd.md, features.md, bugs.md} (created only when missing)
- docs/superplan/plans/ directory and docs/superplan/plans/README.md (generated)
- AGENTS.md managed guardrails block (created or refreshed in place)

Existing human docs are never overwritten, so running this on an established
repository is safe.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


SCRIPTS_DIR = Path(__file__).resolve().parent

HUMAN_FILES = {
    "prd.md": (
        "# PRD\n\n"
        "> 项目需求来源。描述目标、范围、约束、验收标准与非目标。\n"
        "> 由 $project-bootstrap-from-prd 读取并拆分为 docs/superplan/plans 下的执行计划。\n"
    ),
    "features.md": (
        "# Features\n\n"
        "> 功能需求清单（人工维护）。每条需求一个 `## ` 小节，编号 `F001`、`F002` … 顺序递增、不复用。\n"
        ">\n"
        "> 录入方式（二选一）：\n"
        "> - 对 AI 说“新建 feature: <标题>”，由 `$feature-plan-and-delivery` 的 intake 自动追加并编号；\n"
        "> - 或手动复制下方模板，自行填下一个编号。\n"
        ">\n"
        "> 字段说明：\n"
        "> - `status`：`proposed`(待人工复核) → `accepted`(已确认、可规划) → `done`(已交付)\n"
        "> - `created`：创建日期，格式 `YYYY-MM-DD`\n"
        ">\n"
        "> 确认某条无误后，把它的 `status` 改为 `accepted`，再交给 skill 规划实现。\n\n"
        "<!-- 新增条目模板（把 F<NNN> 替换为下一个编号，例如 F001）：\n"
        "\n"
        "## F<NNN>: 简短标题\n"
        "\n"
        "- status: proposed\n"
        "- created: YYYY-MM-DD\n"
        "\n"
        "可选详细描述：目标 / 范围 / 验收标准 / 非目标。\n"
        "-->\n"
    ),
    "bugs.md": (
        "# Bugs\n\n"
        "> 缺陷清单（人工维护）。每条缺陷一个 `## ` 小节，编号 `B001`、`B002` … 顺序递增、不复用。\n"
        ">\n"
        "> 录入方式（二选一）：\n"
        "> - 对 AI 说“新建 bug: <标题>”，由 `$bugfix-plan-and-delivery` 的 intake 自动追加并编号；\n"
        "> - 或手动复制下方模板，自行填下一个编号。\n"
        ">\n"
        "> 字段说明：\n"
        "> - `status`：`proposed`(待人工复核) → `accepted`(已确认、可规划) → `done`(已修复)\n"
        "> - `created`：创建日期，格式 `YYYY-MM-DD`\n"
        ">\n"
        "> 建议在描述里写清：复现步骤 / 期望结果 / 实际结果 / 影响范围。确认无误后把 `status` 改为 `accepted`。\n\n"
        "<!-- 新增条目模板（把 B<NNN> 替换为下一个编号，例如 B001）：\n"
        "\n"
        "## B<NNN>: 简短标题\n"
        "\n"
        "- status: proposed\n"
        "- created: YYYY-MM-DD\n"
        "\n"
        "复现步骤：\n"
        "1. ...\n"
        "期望：... ／ 实际：...\n"
        "-->\n"
    ),
}


def _load(name: str) -> ModuleType:
    cached = sys.modules.get(name)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Register before exec: dataclasses in the loaded module resolve string
    # annotations via sys.modules[cls.__module__], which would otherwise be None.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def detect_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists() or (candidate / "docs").exists():
            return candidate
    return Path.cwd()


def scaffold_human_docs(root: Path) -> list[str]:
    created: list[str] = []
    human_dir = root / "docs" / "superplan" / "human"
    human_dir.mkdir(parents=True, exist_ok=True)
    for filename, template in HUMAN_FILES.items():
        path = human_dir / filename
        if not path.exists():
            path.write_text(template, encoding="utf-8")
            created.append(path.as_posix())
    return created


def sync_agents(root: Path) -> str:
    sync = _load("sync_agents_guardrails")
    agents_path = root / "AGENTS.md"
    existing = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    synced = sync.render_synced(existing, sync.load_reference())
    changed = synced != existing
    agents_path.write_text(synced, encoding="utf-8")
    return "updated" if changed else "unchanged"


def generate_plans_index(root: Path) -> str:
    readme = _load("generate_plans_readme")
    plans_dir = root / "docs" / "superplan" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    generated = readme.generate_readme(root, plans_dir)
    readme_path = plans_dir / "README.md"
    current = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    readme_path.write_text(generated, encoding="utf-8")
    return "updated" if generated != current else "unchanged"


def ensure_superpowers_installed(
    *,
    superpowers_roots: list[str],
    superpowers_skills_dirs: list[str],
    include_default_search: bool,
) -> int:
    dependency = _load("superpowers_dependency")
    result = dependency.check_installation(
        skills_dirs=[Path(path) for path in superpowers_skills_dirs],
        superpowers_roots=[Path(path) for path in superpowers_roots],
        include_defaults=include_default_search,
    )
    print(dependency.format_result(result))
    return 0 if result.ok else 1


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(detect_repo_root(Path.cwd())),
        help="Repository root. Defaults to the nearest ancestor of the cwd containing .git or docs/.",
    )
    parser.add_argument(
        "--skip-superpowers-check",
        action="store_true",
        help="Skip the bundled Superpowers dependency check.",
    )
    parser.add_argument(
        "--superpowers-root",
        action="append",
        default=[],
        help="Explicit Superpowers plugin/repository root containing a skills/ directory.",
    )
    parser.add_argument(
        "--superpowers-skills-dir",
        action="append",
        default=[],
        help="Explicit Superpowers skills directory to check. Can be passed multiple times.",
    )
    parser.add_argument(
        "--no-default-superpowers-search",
        action="store_true",
        help="Only check explicitly provided Superpowers locations.",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    if not args.skip_superpowers_check:
        status = ensure_superpowers_installed(
            superpowers_roots=args.superpowers_root,
            superpowers_skills_dirs=args.superpowers_skills_dir,
            include_default_search=not args.no_default_superpowers_search,
        )
        if status != 0:
            return status

    created_docs = scaffold_human_docs(root)
    agents_state = sync_agents(root)
    plans_state = generate_plans_index(root)

    print(f"root: {root}")
    if created_docs:
        for path in created_docs:
            print(f"created {path}")
    else:
        print("human docs: already present")
    print(f"AGENTS.md: {agents_state}")
    print(f"docs/superplan/plans/README.md: {plans_state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
