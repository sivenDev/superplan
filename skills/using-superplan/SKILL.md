---
name: using-superplan
description: Use when a repository manages requests through docs/superplan/human and docs/superplan/plans and the user wants to start a new project, implement a feature, or fix a bug with reviewed plans and approval gates
---

# Using Superplan

## Overview

Superplan routes human-authored requests into reviewed plans before any implementation starts. Use this as the entry skill when the workflow uses `docs/superplan/human/*` for input and `docs/superplan/plans/*` for execution planning and progress.

## Path Convention

All bundled paths below are relative to this skill directory. Resolve `scripts/`
and `references/` from the installed `skills/using-superplan/` directory before
running commands.

## Initialization

Before doing anything else, verify the Superpowers prerequisite:

``` 
python3 scripts/check_superpowers.py
```

When the human asks to initialize (for example "$using-superplan 初始化一下", "初始化 superplan", "init"), bootstrap the workspace with:

```
python3 scripts/init_workspace.py
```

It is idempotent and:

- Creates `docs/superplan/human/{prd.md, features.md, bugs.md}` when missing (never overwrites existing human docs).
- Creates `docs/superplan/plans/` and generates `docs/superplan/plans/README.md`.
- Installs or refreshes the managed guardrails block in `AGENTS.md` (from `references/agents-guardrails.md`).

Pass `--root <path>` to target a repository other than the current directory. After init, route the actual request as usual.

## Entry Checks

1. Inspect `git status` and understand current progress in `docs/superplan/plans` before editing anything.
2. Read the matching human input:
   - `docs/superplan/human/prd.md` for first project development
   - `docs/superplan/human/features.md` for feature delivery
   - `docs/superplan/human/bugs.md` for bug fixing
3. Read `references/delivery-loop.md`. It defines the shared delivery loop and global rules that every Superplan skill follows.
4. Before creating or revising any plan, read `references/plan-spec.md`.
5. For greenfield repositories or repositories missing workflow guardrails, read `references/agents-guardrails.md` and sync it into `AGENTS.md` with `python3 scripts/sync_agents_guardrails.py --write`.

## Routing

- New project from a rough PRD: use `$project-bootstrap-from-prd`.
- Requested feature from a feature list or feature note: use `$feature-plan-and-delivery`.
- Reported defect or failing behavior: use `$bugfix-plan-and-delivery`.

For a brand-new feature or bug (for example "新建 feature", "feature: ...", "新建 bug", "bug: ..."), the feature and bugfix skills run intake first: they record the item into `docs/superplan/human/features.md` or `docs/superplan/human/bugs.md` with a stable id, pause for human review, then continue once accepted. See `references/intake-spec.md`.

## Global Rules

The canonical delivery loop and global rules live in `references/delivery-loop.md`. Always follow them. In short:

- Never implement before a reviewed plan exists and the human explicitly approves execution.
- Every plan file under `docs/superplan/plans/**` must follow `references/plan-spec.md`.
- Keep plans independent, clear, and non-overlapping; review the full related plan set after any change.
- The canonical project-level workflow guardrails live in `references/agents-guardrails.md`. Install or refresh them with `python3 scripts/sync_agents_guardrails.py --write`, and verify with `--check`.
- `docs/superplan/plans/README.md` is a generated index. After any plan add, remove, rename, or metadata change, run `python3 scripts/generate_plans_readme.py --write`, and verify with `--check`.
