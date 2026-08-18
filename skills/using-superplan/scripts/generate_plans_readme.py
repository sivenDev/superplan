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

from human_registry import CONFIG as HUMAN_CONFIG
from human_registry import HumanRequest, load_kind
from rfc_documents import RFCDocument, discover_rfcs
from safe_writes import TextUpdate, commit_text_updates, workspace_lock
from workspace_paths import resolve_existing_workspace


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
ACTIVE_STATUSES = {"draft", "approved", "in_progress", "blocked"}
ORDERED_TYPES = {"required", "future"}
# Feature/bugfix plan ids encode their source human entry: F001 (single plan),
# F001-01, F001-02 (when one entry is split into several plans), or
# branch-qualified equivalents such as F001@feature-x.
SOURCE_ID_TYPES = {"feature": "F", "bugfix": "B"}
SOURCE_FROM_ID = re.compile(r"^([FB]\d{3,})(?:-\d+)?$")
QUALIFIED_SOURCE_FROM_ID = re.compile(r"^([FB]\d{3,})@([A-Za-z0-9._-]+)$")
CREATED_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LEGACY_MISSING_HUMAN_FIELD = re.compile(r": missing (status|created)$")
HUMAN_FILES = {config["prefix"]: config["filename"] for config in HUMAN_CONFIG.values()}
HUMAN_KINDS = {config["prefix"]: kind for kind, config in HUMAN_CONFIG.items()}


def source_id_from_plan_id(plan_id: str) -> str:
    match = SOURCE_FROM_ID.match(plan_id)
    if match:
        return match.group(1)

    match = QUALIFIED_SOURCE_FROM_ID.match(plan_id)
    if not match:
        return ""

    source_prefix = match.group(1)
    qualifier = match.group(2)
    split_match = re.match(r"^(.+)-\d+$", qualifier)
    if split_match:
        qualifier = split_match.group(1)
    return f"{source_prefix}@{qualifier}"


@dataclass(frozen=True)
class PlanMetadata:
    id: str
    title: str
    plan_type: str
    status: str
    summary: str
    source: str
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
        return source_id_from_plan_id(self.id)


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
    required_keys = {"id", "title", "type", "status", "summary", "source", "created"}
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
        source_id = source_id_from_plan_id(plan_id)
        if not source_id or not plan_id.startswith(expected_prefix):
            raise ValueError(
                f"{path}: {plan_type} plan id must look like {expected_prefix}001, "
                f"{expected_prefix}001-01, or {expected_prefix}001@branch-slug, got '{plan_id}'"
            )

    return PlanMetadata(
        id=plan_id,
        title=metadata["title"],
        plan_type=plan_type,
        status=status,
        summary=metadata["summary"],
        source=metadata["source"],
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


def load_human_requests(
    root: Path,
    *,
    allow_legacy_missing: bool = False,
) -> dict[str, dict[str, HumanRequest]]:
    result: dict[str, dict[str, HumanRequest]] = {}
    for prefix, kind in HUMAN_KINDS.items():
        path, _, entries, issues = load_kind(root, kind)
        if not path.exists():
            continue
        blocking = issues
        if allow_legacy_missing:
            blocking = [issue for issue in issues if not LEGACY_MISSING_HUMAN_FIELD.search(issue)]
        if blocking:
            raise ValueError("\n".join(blocking))
        result[prefix] = {entry.request_id: entry for entry in entries}
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


def plan_references_rfc(plan: PlanMetadata, rfc_path: str) -> bool:
    in_references = False
    for line in plan.path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## References":
            in_references = True
            continue
        if in_references and stripped.startswith("## "):
            return False
        if in_references and stripped in {f"- `{rfc_path}`", f"- {rfc_path}"}:
            return True
    return False


def validate_plans(
    plans: list[PlanMetadata],
    root: Path,
    *,
    enforce_request_states: bool = True,
    allow_legacy_missing: bool = False,
) -> None:
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

    human_requests = load_human_requests(
        root,
        allow_legacy_missing=allow_legacy_missing,
    )
    rfcs = discover_rfcs(root)
    rfc_by_id: dict[str, RFCDocument] = {rfc.id: rfc for rfc in rfcs}
    features = human_requests.get("F", {})
    for rfc in rfcs:
        request = features.get(rfc.id)
        if request is None:
            raise ValueError(f"{rfc.path}: RFC id '{rfc.id}' has no matching feature request")
        if not request.requires_rfc:
            raise ValueError(f"{rfc.path}: feature '{rfc.id}' is not marked requires_rfc")
        if request.status == "proposed":
            raise ValueError(f"{rfc.path}: proposed feature '{rfc.id}' cannot have an RFC")
    plans_by_source: dict[str, list[PlanMetadata]] = {}
    for plan in plans:
        prefix = SOURCE_ID_TYPES.get(plan.plan_type)
        if not prefix:
            continue
        human_file = f"docs/superplan/human/{HUMAN_FILES[prefix]}"
        if plan.source != human_file:
            raise ValueError(
                f"{plan.path}: {plan.plan_type} source must be '{human_file}', "
                f"got '{plan.source}'"
            )
        known = human_requests.get(prefix)
        if known is None:
            raise ValueError(f"{plan.path}: source registry '{human_file}' does not exist")
        if plan.source_id not in known:
            raise ValueError(
                f"{plan.path}: source entry '{plan.source_id}' (from id '{plan.id}') "
                f"not found in {human_file}"
            )
        plans_by_source.setdefault(plan.source_id, []).append(plan)

    for request in features.values():
        if not request.requires_rfc:
            continue
        deliverable = [
            plan
            for plan in plans_by_source.get(request.request_id, [])
            if plan.status != "superseded"
        ]
        rfc = rfc_by_id.get(request.request_id)
        if deliverable and rfc is None:
            raise ValueError(
                f"{request.request_id}: RFC-required feature has non-superseded plans but no RFC"
            )
        if deliverable and rfc is not None and rfc.status != "approved":
            raise ValueError(
                f"{request.request_id}: RFC-required feature has non-superseded plans but RFC is {rfc.status}"
            )
        if deliverable and rfc is not None:
            expected_path = f"docs/superplan/rfcs/{request.request_id}.md"
            missing = [
                plan.id for plan in deliverable if not plan_references_rfc(plan, expected_path)
            ]
            if missing:
                raise ValueError(
                    f"{request.request_id}: RFC-required plans missing exact References entry "
                    f"'{expected_path}': {', '.join(sorted(missing))}"
                )

    if not enforce_request_states:
        return

    for requests in human_requests.values():
        for request in requests.values():
            related = plans_by_source.get(request.request_id, [])
            deliverable = [plan for plan in related if plan.status != "superseded"]
            if request.status == "proposed" and deliverable:
                details = ", ".join(
                    f"{plan.id} ({plan.status})" for plan in sorted(deliverable, key=lambda item: item.id)
                )
                raise ValueError(
                    f"{request.request_id}: proposed request has non-superseded plans: {details}"
                )
            if request.status != "done":
                continue
            if request.requires_rfc:
                rfc = rfc_by_id.get(request.request_id)
                if rfc is None or rfc.status != "approved":
                    state = "missing" if rfc is None else rfc.status
                    raise ValueError(
                        f"{request.request_id}: done RFC-required feature has RFC state '{state}'"
                    )
            if not deliverable:
                raise ValueError(
                    f"{request.request_id}: done request has no non-superseded related plans"
                )
            blockers = [plan for plan in deliverable if plan.status != "complete"]
            if blockers:
                details = ", ".join(
                    f"{plan.id} ({plan.status})" for plan in sorted(blockers, key=lambda item: item.id)
                )
                raise ValueError(
                    f"{request.request_id}: done request has incomplete related plans: {details}"
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


def filter_plans(
    plans: list[PlanMetadata],
    *,
    active: bool = False,
    statuses: set[str] | None = None,
    source_id: str | None = None,
    depends_on: str | None = None,
    search: str | None = None,
    artifact: str | None = None,
) -> list[PlanMetadata]:
    selected = plans
    if active:
        selected = [plan for plan in selected if plan.status in ACTIVE_STATUSES]
    if statuses:
        selected = [plan for plan in selected if plan.status in statuses]
    if source_id:
        selected = [
            plan
            for plan in selected
            if plan.source_id == source_id or plan.source == source_id
        ]
    if depends_on:
        selected = [plan for plan in selected if depends_on in plan.depends_on]
    if search:
        needle = search.casefold()
        selected = [
            plan
            for plan in selected
            if needle in plan.path.read_text(encoding="utf-8").casefold()
        ]
    if artifact:
        needle = artifact.replace("\\", "/").casefold()
        selected = [
            plan
            for plan in selected
            if needle
            in plan.path.read_text(encoding="utf-8").replace("\\", "/").casefold()
        ]
    return selected


def render_catalog(plans: Iterable[PlanMetadata], plans_dir: Path) -> str:
    lines = ["ID\tSTATUS\tTYPE\tSOURCE_ID\tSOURCE\tDEPENDS_ON\tSUMMARY\tPATH"]
    for plan in plans:
        relative = plan.path.relative_to(plans_dir).as_posix()
        dependencies = ",".join(plan.depends_on)
        lines.append(
            f"{plan.id}\t{plan.status}\t{plan.plan_type}\t{plan.source_id}\t"
            f"{plan.source}\t{dependencies}\t{plan.summary}\t{relative}"
        )
    return "\n".join(lines) + "\n"


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the Git top-level or nearest existing Superplan ancestor.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write docs/superplan/plans/README.md. Can be combined with --check.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if docs/superplan/plans/README.md is stale. When combined with --write, checks the freshly written file.",
    )
    discovery = parser.add_mutually_exclusive_group()
    discovery.add_argument(
        "--catalog",
        action="store_true",
        help="Print compact metadata for all matching plans without plan bodies.",
    )
    discovery.add_argument(
        "--search",
        help="Search full plan text across all statuses and print compact candidates.",
    )
    discovery.add_argument(
        "--artifact",
        help="Find plans mentioning an artifact path across all statuses.",
    )
    parser.add_argument(
        "--active",
        action="store_true",
        help="Filter discovery to draft, approved, in-progress, or blocked plans.",
    )
    parser.add_argument(
        "--status",
        action="append",
        choices=STATUS_ORDER,
        help="Filter discovery by status. Can be repeated.",
    )
    parser.add_argument("--source-id", help="Filter discovery by human source id or source path.")
    parser.add_argument("--depends-on", help="Filter plans with a direct dependency on this id.")
    args = parser.parse_args(argv)

    try:
        root = Path(args.root).resolve() if args.root else resolve_existing_workspace(Path.cwd())
    except ValueError as exc:
        print(exc)
        return 1
    plans_dir = root / "docs" / "superplan" / "plans"
    readme_path = plans_dir / "README.md"
    discovery_requested = bool(
        args.catalog
        or args.search
        or args.artifact
        or args.active
        or args.status
        or args.source_id
        or args.depends_on
    )
    if discovery_requested and (args.write or args.check):
        print("discovery options cannot be combined with --write or --check")
        return 2

    if discovery_requested:
        try:
            plans = discover_plans(plans_dir)
            validate_plans(plans, root)
            selected = filter_plans(
                plans,
                active=args.active,
                statuses=set(args.status or []),
                source_id=args.source_id,
                depends_on=args.depends_on,
                search=args.search,
                artifact=args.artifact,
            )
        except (OSError, ValueError) as exc:
            print(exc)
            return 1
        print(render_catalog(selected, plans_dir), end="")
        return 0

    if args.write:
        try:
            with workspace_lock(root):
                generated = generate_readme(root, plans_dir)
                original = (
                    readme_path.read_text(encoding="utf-8")
                    if readme_path.exists()
                    else None
                )
                commit_text_updates([TextUpdate(readme_path, original, generated)])
        except (OSError, ValueError) as exc:
            print(exc)
            return 1
        print(f"updated {readme_path}")

        if args.check:
            current = readme_path.read_text(encoding="utf-8")
            if current != generated:
                print(f"stale {readme_path}")
                return 1
            print(f"ok {readme_path}")
        return 0

    try:
        generated = generate_readme(root, plans_dir)
    except (OSError, ValueError) as exc:
        print(exc)
        return 1

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
