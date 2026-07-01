---
name: feature-plan-and-delivery
description: Use when a feature is recorded in docs/superplan/human/features.md and the work must be translated into reviewed plans under docs/superplan/plans/features before implementation begins
---

# Feature Plan and Delivery

## Overview

Turn a requested feature into a reviewed implementation plan, then execute only after approval. This skill is for feature work that starts from `docs/superplan/human/features.md` or an equivalent feature note in the same workflow.

Bundled script paths are resolved relative to this skill directory.

## Intake

When the human proposes a brand-new feature (for example "新建 feature", "feature: ...", "新增功能 ...") instead of pointing at an already-recorded entry, run intake first. Read `../using-superplan/references/intake-spec.md`, then:

1. Extract a short title (and optional description) from the request.
2. Record it into `docs/superplan/human/features.md` with the next id and `status: proposed`:
   - `python3 ../using-superplan/scripts/record_human_request.py --type feature --title "<title>" [--body "<description>"]`
3. Stop and ask the human to review the recorded entry. Do not start planning.
4. After the human confirms (entry becomes `status: accepted`), continue with the delivery loop below using that entry as the source.

If the human references an existing entry, skip intake and go straight to the delivery loop.

## Specialization

This skill specializes the shared delivery loop. Read `../using-superplan/references/delivery-loop.md` first, then apply these settings:

- Input: `docs/superplan/human/features.md`
- Output: `docs/superplan/plans/features/` (create a feature-specific subdirectory when the feature needs multiple plans)
- Plan type: `feature`
- Extra steps: run intake first when the request is a new feature (see Intake above).

## Type-Specific Rules

- Feature plans belong in `docs/superplan/plans/features/`.
- Every feature plan id must encode its source entry: use `F001` for a single plan, `F001@branch-slug` when the accepted entry is branch-qualified from a linked worktree, or `F001-01`, `F001@branch-slug-01` when split. Set `created` to today's date.
- Prefer one plan per independently testable slice.
- When one feature can be split into independent slices with clear ownership and verification boundaries, prefer subagent-assisted decomposition during planning and multiple subagents during execution.
- If shared context or correctness would suffer, keep the plan or execution more serialized.
- Make the user-visible result or acceptance explicit in `Scope` or `Exit Criteria`.
- If a feature touches shared infrastructure, call out the shared boundary explicitly instead of hiding it inside a feature-only plan.
- If feature scope is still fuzzy, stay in `brainstorming` before continuing.
