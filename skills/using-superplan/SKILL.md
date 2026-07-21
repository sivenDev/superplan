---
name: using-superplan
description: Use when a repository manages project, feature, or bug work through docs/superplan/human and reviewed plans under docs/superplan/plans with explicit approval before implementation
---

# Using Superplan

Use this as the entry skill. Read `references/delivery-loop.md` before intake,
plan changes, or implementation; it owns workspace safety, risk, approval,
execution, verification, progress, and commit rules.

## Prerequisite and Initialization

Verify Superpowers during installation, initialization, diagnostics, or when no
still-fresh dependency evidence exists:

```bash
python3 <using-superplan-root>/scripts/check_superpowers.py
```

Do not repeat this check for every routed task while the active profile,
manifest, skill locations, and relevant environment remain unchanged.

For GPT-5.6, inspect the resolved installation before any activation:

```bash
python3 <using-superplan-root>/scripts/install_superpowers_profile.py \
  --model gpt-5.6 --dry-run
```

If replacement is required, show the resolved target and conflicts and obtain
explicit human approval before running:

```bash
python3 <using-superplan-root>/scripts/install_superpowers_profile.py \
  --model gpt-5.6 --replace-existing
```

For a conflict-free install, rerun without `--replace-existing`. The installer
supports `gpt-5.6` and `gpt-5.6-*` only; after activation, restart Codex or open
a new chat.

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
