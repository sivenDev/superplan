---
name: using-superplan
description: Use when a repository manages requests through docs/superplan/human and docs/superplan/plans and the user wants to start a new project, implement a feature, or fix a bug with reviewed plans and approval gates
---

# Using Superplan

Read `references/delivery-loop.md` before routed work. It owns workspace safety,
risk, approval, verification, progress, and delivery.

`<using-superplan-root>` means this skill's installed directory.

## Setup and Initialization

For installation, dependency diagnosis, profile replacement, or
profile-sensitive initialization, read `references/profile-setup.md`.

When the human asks to initialize Superplan, run:

`python3 <using-superplan-root>/scripts/init_workspace.py`

Use `--model gpt-5.6` when initialization must validate the active profile. Use
`--root <path>` for an explicit target. Initialization preserves existing human
docs, refreshes managed guardrails, and generates the plan index.

## Route Entry

1. Apply the delivery loop's Workspace Safety check; inspect recent commits and
   current plan progress before editing.
2. Read the matching human input:
   - `docs/superplan/human/prd.md` for first project development
   - `docs/superplan/human/features.md` for feature delivery
   - `docs/superplan/human/bugs.md` for bug fixing
3. Before creating or structurally revising a plan, read
   `references/plan-spec.md`.
4. If the managed guardrails are missing or stale, run
   `python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`.

## Routing

- New project from a rough PRD: use `$project-bootstrap-from-prd`.
- New or recorded feature: use `$feature-plan-and-delivery`.
- New or recorded bug: use `$bugfix-plan-and-delivery`.

For new feature or bug intake, the route skill applies
`references/intake-spec.md` before planning.
