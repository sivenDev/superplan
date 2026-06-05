#!/usr/bin/env python3
"""Generate and verify docs/superplan/plans/README.md from plan metadata.

Also validates cross-plan integrity: known status/type values, present
`created`, well-formed ids (feature/bugfix ids encode their source human entry,
e.g. `F001` or `F001-01`), existing and acyclic `depends_on`, that each
feature/bugfix plan's source entry exists in the human docs, and the rule that a
`complete` plan cannot depend on a plan that is not yet `complete`.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


SCRIPT_COMMAND = (
    "python3 <using-superplan-root>/scripts/generate_plans_readme.py"
)
TYPE_ORDER = ["required", "future", "feature", "bugfix"]
TYPE_TITLES = {
    "required": "Required Plans",
    "future": "Future Plans",
    "feature": "Feature Plans",
    "bugfix": "Bugfix Plans",
}
STATUS_ORDER = [
    "draft",
    "approved",
    "in_progress",
    "blocked",
    "complete",
    "superseded",
]
STATUS_TITLES = {
    "draft": "Draft",
    "approved": "Approved",
    "in_progress": "In Progress",
    "blocked": "Blocked",
    "complete": "Complete",
    "superseded": "Superseded",
}
ORDERED_TYPES = {"required", "future"}
# Feature/bugfix plan ids encode their source human entry: F001 (single plan) or
# F001-01, F001-02 (when one entry is split into several plans). The source id is
# the leading prefix.
SOURCE_ID_TYPES = {"feature": "F", "bugfix": "B"}
SOURCE_FROM_ID = re.compile(r"^([FB]\d{3})(?:-\d+)?$")
CREATED_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HUMAN_ENTRY_PATTERN = re.compile(r"^##\s+([FB]\d{3}):", re.MULTILINE)
HUMAN_FILES = {"F": "features.md", "B": "bugs.md"}


def detect_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "docs" / "superplan" / "plans").is_dir():
            return candidate
    raise ValueError(f"unable to locate repository root from {start}")


@dataclass(frozen=True)
class PlanMetadata:
    id: str
    title: str
    plan_type: str
    status: str
    summary: str
    created: str
    path: Path
    order: int | None = None
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    parent: str = ""

    @property
    def source_id(self) -> str:
        """Source human entry id derived from the plan id (feature/bugfix only)."""
        if self.plan_type not in SOURCE_ID_TYPES:
            return ""
        match = SOURCE_FROM_ID.match(self.id)
        return match.group(1) if match else ""


def parse_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")

    end = content.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")

    metadata: dict[str, str] = {}
    for raw_line in content[4:end].splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid metadata line '{raw_line}'")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{path}: empty metadata key")
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        metadata[key] = value

    return metadata


def parse_id_list(raw: str) -> tuple[str, ...]:
    text = raw.strip()
    if not text or text == "[]":
        return ()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    items: list[str] = []
    for part in text.split(","):
        cleaned = part.strip().strip('"').strip("'").strip()
        if cleaned:
            items.append(cleaned)
    return tuple(items)


def load_plan(path: Path) -> PlanMetadata:
    metadata = parse_frontmatter(path)
    required_keys = {"id", "title", "type", "status", "summary", "created"}
    missing = sorted(required_keys - metadata.keys())
    if missing:
        raise ValueError(f"{path}: missing metadata keys: {', '.join(missing)}")

    order_text = metadata.get("order")
    order = None
    if order_text:
        try:
            order = int(order_text)
        except ValueError as exc:
            raise ValueError(f"{path}: invalid order '{order_text}'") from exc

    plan_type = metadata["type"]
    if plan_type not in TYPE_TITLES:
        valid = ", ".join(TYPE_ORDER)
        raise ValueError(f"{path}: unknown type '{plan_type}', expected one of: {valid}")

    status = metadata["status"]
    if status not in STATUS_TITLES:
        valid = ", ".join(STATUS_ORDER)
        raise ValueError(f"{path}: unknown status '{status}', expected one of: {valid}")

    created = metadata["created"]
    if not CREATED_PATTERN.match(created):
        raise ValueError(f"{path}: invalid created '{created}', expected YYYY-MM-DD")

    plan_id = metadata["id"]
    expected_prefix = SOURCE_ID_TYPES.get(plan_type)
    if expected_prefix:
        match = SOURCE_FROM_ID.match(plan_id)
        if not match or not plan_id.startswith(expected_prefix):
            raise ValueError(
                f"{path}: {plan_type} plan id must look like {expected_prefix}001 or "
                f"{expected_prefix}001-01, got '{plan_id}'"
            )

    return PlanMetadata(
        id=plan_id,
        title=metadata["title"],
        plan_type=plan_type,
        status=status,
        summary=metadata["summary"],
        created=created,
        order=order,
        depends_on=parse_id_list(metadata.get("depends_on", "")),
        parent=metadata.get("parent", ""),
        path=path,
    )


def discover_plans(plans_dir: Path) -> list[PlanMetadata]:
    plans: list[PlanMetadata] = []
    for path in sorted(plans_dir.rglob("*.md")):
        if path.name == "README.md":
            continue
        plans.append(load_plan(path))
    return sorted(
        plans,
        key=lambda plan: (
            TYPE_ORDER.index(plan.plan_type),
            plan.order if plan.order is not None else 1_000_000,
            plan.id,
            plan.path.as_posix(),
        ),
    )


def load_human_ids(root: Path) -> dict[str, set[str]]:
    human_dir = root / "docs" / "superplan" / "human"
    result: dict[str, set[str]] = {}
    for prefix, filename in HUMAN_FILES.items():
        path = human_dir / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        result[prefix] = {match.group(1) for match in HUMAN_ENTRY_PATTERN.finditer(content)}
    return result


def topological_order(plans: list[PlanMetadata]) -> list[PlanMetadata]:
    by_id = {plan.id: plan for plan in plans}
    state: dict[str, int] = {}
    result: list[PlanMetadata] = []

    def visit(plan: PlanMetadata, stack: list[str]) -> None:
        current = state.get(plan.id, -1)
        if current == 1:
            return
        if current == 0:
            cycle = " -> ".join(stack + [plan.id])
            raise ValueError(f"dependency cycle detected: {cycle}")
        state[plan.id] = 0
        for dep in sorted(plan.depends_on):
            if dep in by_id:
                visit(by_id[dep], stack + [plan.id])
        state[plan.id] = 1
        result.append(plan)

    seed = sorted(
        plans,
        key=lambda plan: (plan.order if plan.order is not None else 1_000_000, plan.id),
    )
    for plan in seed:
        visit(plan, [])
    return result


def validate_plans(plans: list[PlanMetadata], root: Path) -> None:
    by_id: dict[str, PlanMetadata] = {}
    for plan in plans:
        if plan.id in by_id:
            raise ValueError(
                f"duplicate plan id '{plan.id}': {by_id[plan.id].path} and {plan.path}"
            )
        by_id[plan.id] = plan

    for plan in plans:
        for dep in plan.depends_on:
            if dep not in by_id:
                raise ValueError(f"{plan.path}: depends_on references unknown plan id '{dep}'")

    # Raises on cycles.
    topological_order(plans)

    for plan in plans:
        if plan.status == "complete":
            for dep in plan.depends_on:
                if by_id[dep].status != "complete":
                    raise ValueError(
                        f"{plan.path}: complete plan depends on non-complete plan '{dep}' "
                        f"(status '{by_id[dep].status}')"
                    )

    human_ids = load_human_ids(root)
    for plan in plans:
        prefix = SOURCE_ID_TYPES.get(plan.plan_type)
        if not prefix:
            continue
        known = human_ids.get(prefix)
        if known is not None and plan.source_id not in known:
            human_file = f"docs/superplan/human/{HUMAN_FILES[prefix]}"
            raise ValueError(
                f"{plan.path}: source entry '{plan.source_id}' (from id '{plan.id}') "
                f"not found in {human_file}"
            )


def render_status_summary(plans: Iterable[PlanMetadata]) -> list[str]:
    grouped: dict[str, Counter[str]] = {plan_type: Counter() for plan_type in TYPE_ORDER}
    totals: Counter[str] = Counter()
    for plan in plans:
        grouped[plan.plan_type][plan.status] += 1
        totals[plan.status] += 1

    lines = ["## Status", ""]
    if not totals:
        lines.append("No plans yet.")
        return lines

    statuses = [status for status in STATUS_ORDER if totals.get(status, 0) > 0]
    header = "| Type | Plans | " + " | ".join(STATUS_TITLES[status] for status in statuses) + " |"
    separator = "| --- | --- | " + " | ".join("---" for _ in statuses) + " |"
    lines.extend([header, separator])
    for plan_type in TYPE_ORDER:
        counter = grouped[plan_type]
        total = sum(counter.values())
        if total == 0:
            continue
        counts = " | ".join(str(counter.get(status, 0)) for status in statuses)
        lines.append(f"| `{plan_type}` | {total} | {counts} |")
    return lines


def render_execution_order(plans: list[PlanMetadata], readme_dir: Path) -> list[str]:
    ordered = topological_order([plan for plan in plans if plan.plan_type in ORDERED_TYPES])
    if not ordered:
        return []

    lines = ["## Execution Order", ""]
    for index, plan in enumerate(ordered, start=1):
        rel_path = plan.path.relative_to(readme_dir).as_posix()
        lines.append(
            f"{index}. `{plan.id}` [{plan.title}]({rel_path}) - `{plan.status}` ({plan.created})"
        )
    return lines


def render_group(plan_type: str, plans: Iterable[PlanMetadata], readme_dir: Path) -> list[str]:
    group = [plan for plan in plans if plan.plan_type == plan_type]
    if not group:
        return []

    lines = [
        f"### {TYPE_TITLES[plan_type]}",
        "",
        "| ID | Plan | Status | Created |",
        "| --- | --- | --- | --- |",
    ]
    for plan in group:
        rel_path = plan.path.relative_to(readme_dir).as_posix()
        lines.append(
            f"| `{plan.id}` | [{plan.title}]({rel_path}) | `{plan.status}` | {plan.created} |"
        )
    return lines


def generate_readme(root: Path, plans_dir: Path) -> str:
    plans = discover_plans(plans_dir)
    validate_plans(plans, root)
    readme_dir = plans_dir

    lines = [
        "# Plans Index",
        "",
        f"<!-- Auto-generated by `{SCRIPT_COMMAND} --write`; verify with `--check`. Do not edit. -->",
        "",
    ]
    lines.extend(render_status_summary(plans))
    lines.append("")

    execution_lines = render_execution_order(plans, readme_dir)
    if execution_lines:
        lines.extend(execution_lines)
        lines.append("")

    group_lines: list[str] = []
    for plan_type in TYPE_ORDER:
        group = render_group(plan_type, plans, readme_dir)
        if group:
            group_lines.extend(group)
            group_lines.append("")
    if group_lines:
        lines.extend(["## Plan Groups", ""])
        lines.extend(group_lines)

    return "\n".join(lines).rstrip() + "\n"


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the nearest ancestor of the current directory containing docs/superplan/plans.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Write docs/superplan/plans/README.md")
    mode.add_argument("--check", action="store_true", help="Fail if docs/superplan/plans/README.md is stale")
    args = parser.parse_args(argv)

    try:
        root = Path(args.root).resolve() if args.root else detect_repo_root(Path.cwd())
    except ValueError as exc:
        print(exc)
        return 1
    plans_dir = root / "docs" / "superplan" / "plans"
    readme_path = plans_dir / "README.md"
    try:
        generated = generate_readme(root, plans_dir)
    except ValueError as exc:
        print(exc)
        return 1

    if args.write:
        readme_path.write_text(generated, encoding="utf-8")
        print(f"updated {readme_path}")
        return 0

    if args.check:
        current = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
        if current != generated:
            print(f"stale {readme_path}")
            return 1
        print(f"ok {readme_path}")
        return 0

    print(generated, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
