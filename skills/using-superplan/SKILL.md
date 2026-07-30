---
name: using-superplan
description: Use when a repository manages requests through docs/superplan/human and docs/superplan/plans and the user wants to start a new project, implement a feature, or fix a bug with reviewed plans and approval gates
---

# Using Superplan

Read `references/delivery-loop.md` before routed work. It owns workspace safety,
risk, approval, verification, progress, and delivery.

`<using-superplan-root>` means this skill's installed directory.

## Setup and Initialization

When the human asks to initialize Superplan, run:

`python3 <using-superplan-root>/scripts/init_workspace.py`

Use `--root <path>` for an explicit target. Initialization is offline and
workspace-only. It preserves existing human docs, refreshes managed guardrails,
and generates the plan index.

## Route Entry

1. Apply the delivery loop's Workspace Safety check; inspect recent commits and
   current plan progress before editing.
2. Run `init_workspace.py --check`. Continue when current; after workspace
   safety, use `--migrate` for an older/missing schema. Stop on newer or malformed
   schemas.
3. For features or bugs, use `human_requests.py validate`, then
   `summary`/`list` and `show --id <id>`; read a whole registry only for repair
   or cross-entry analysis. Read `prd.md` directly for first project development.
4. Before creating or structurally revising a plan, read
   `references/plan-spec.md`, validate all metadata, inspect `--catalog`, and
   search all statuses for related source, dependency, scope, or artifact
   candidates. Read the changed plan and discovered related closure in full.
5. If generated guardrails are stale, migrate through `init_workspace.py` after
   workspace safety rather than editing the managed block manually.

## Routing

- New project from a rough PRD: use `$project-bootstrap-from-prd`.
- New or recorded feature: use `$feature-plan-and-delivery`.
- New or recorded bug: use `$bugfix-plan-and-delivery`.

For new feature or bug intake, the route skill applies
`references/intake-spec.md` before planning.
