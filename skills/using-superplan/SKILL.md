---
name: using-superplan
description: Use when a repository manages requests through docs/superplan/human and docs/superplan/plans and the user wants to start a new project, implement a feature, or fix a bug with reviewed plans and approval gates
---

# Using Superplan

## Overview

Superplan routes human-authored requests into reviewed plans before any implementation starts. Use this as the entry skill when the workflow uses `docs/superplan/human/*` for input and `docs/superplan/plans/*` for execution planning and progress.
Scale planning, testing, verification, and delegation to the risk profiles in `references/delivery-loop.md`. Default small and medium work to one capable agent; use subagents only for genuinely independent slices or high-risk review where the extra boundary improves evidence.

## Path Convention

`<using-superplan-root>` means the installed `skills/using-superplan/` directory
that contains this skill's `scripts/` and `references/` folders.

## Initialization

Before doing anything else, verify the Superpowers prerequisite:

``` 
python3 <using-superplan-root>/scripts/check_superpowers.py
```

When the human asks to initialize (for example "$using-superplan 初始化一下", "初始化 superplan", "init"), bootstrap the workspace with:

```
python3 <using-superplan-root>/scripts/init_workspace.py
```

It is idempotent and:

- Creates `docs/superplan/human/{prd.md, features.md, bugs.md}` when missing (never overwrites existing human docs).
- Creates `docs/superplan/plans/` and generates `docs/superplan/plans/README.md`.
- Installs or refreshes the managed guardrails block in `AGENTS.md` (from `references/agents-guardrails.md`).

Pass `--root <path>` to target a repository other than the current directory. After init, route the actual request as usual.

## Entry Checks

1. Read `references/delivery-loop.md`, then run its Workspace Safety Check before
   intake, plan changes, or implementation edits. Inspect `git status` plus enough
   staged, unstaged, and relevant untracked diff context to decide whether
   meaningful Git changes could be overwritten, mixed into the task, or conflict
   with it. Ignore clearly insignificant or safely reproducible noise. If
   important changes exist, explain the risk and ask whether to move all
   subsequent Superplan work into a new worktree. Resolve the choice first: use
   `using-git-worktrees` when accepted, or continue in place with precise staging
   and unrelated-change preservation when declined. Never stash, commit, or
   create the worktree without consent.
2. Inspect recent commits and understand current progress in `docs/superplan/plans` before editing anything.
3. Read the matching human input:
   - `docs/superplan/human/prd.md` for first project development
   - `docs/superplan/human/features.md` for feature delivery
   - `docs/superplan/human/bugs.md` for bug fixing
4. Before creating or revising any plan, read `references/plan-spec.md`.
5. For greenfield repositories or repositories missing workflow guardrails, read `references/agents-guardrails.md` and sync it into `AGENTS.md` with `python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`.

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
- Use the approved Superplan plan as the persisted design and execution artifact. Invoke full brainstorming only for material ambiguity, and do not create parallel Superpowers specs or plans unless the human requests them.
- Apply the low, standard, or high risk guidance from `references/delivery-loop.md`. Default small and medium work to one agent; reserve subagents for independent slices or high-risk review.
- The canonical project-level workflow guardrails live in `references/agents-guardrails.md`. Install or refresh them with `python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`, and verify with `--check`.
- `docs/superplan/plans/README.md` is a generated index. After any plan add, remove, rename, or metadata change, run `python3 <using-superplan-root>/scripts/generate_plans_readme.py --write --check`.
- Task-level commit messages include the plan id when one exists so Git remains the source of truth for the delivered diff.
