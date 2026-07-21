---
name: using-superplan
description: Use when a repository manages project, feature, or bug work through docs/superplan/human and reviewed plans under docs/superplan/plans with explicit approval before implementation
---

# Using Superplan

Use this as the entry skill. Read `references/delivery-loop.md` before intake,
plan changes, or implementation; it owns workspace safety, risk, approval,
execution, verification, progress, and commit rules.

## Prerequisite and Initialization

Verify Superpowers:

```bash
python3 <using-superplan-root>/scripts/check_superpowers.py
```

For GPT-5.6, install the pinned profile when needed, then restart Codex or open a
new chat:

```bash
python3 <using-superplan-root>/scripts/install_superpowers_profile.py \
  --model gpt-5.6 --replace-existing
```

The installer supports `gpt-5.6` and `gpt-5.6-*` only.

When asked to initialize Superplan, run:

```bash
python3 <using-superplan-root>/scripts/init_workspace.py
```

Use `--model gpt-5.6` to enforce the active profile and `--root <path>` to target
another repository. Initialization is idempotent and creates the human docs,
plan index, and managed `AGENTS.md` guardrails without overwriting human input.

## Route

After the delivery-loop entry checks, inspect recent progress and choose one:

- Rough first-project PRD: `project-bootstrap-from-prd`
- New or recorded feature: `feature-plan-and-delivery`
- New or recorded bug: `bugfix-plan-and-delivery`

Before creating or revising a plan, read `references/plan-spec.md`. Feature and
bug routes use `references/intake-spec.md` for unrecorded requests.
