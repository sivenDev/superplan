---
id: "F003"
title: "Worktree-Aware Human Request Numbering"
type: "feature"
status: "draft"
summary: "Qualify generated feature and bug request ids with the current branch when intake runs from a linked git worktree."
source: "docs/superplan/human/features.md"
created: "2026-07-01"
depends_on: []
parent: ""
---
# Worktree-Aware Human Request Numbering Plan

**Goal:** Prevent human feature and bug request id collisions when multiple linked worktrees record new requests before merging back together.
**Scope:** Update Superplan intake numbering so `record_human_request.py` emits branch-qualified ids such as `F004@feature-x` or `B001@fix-y` only when the target repository is a linked git worktree, while preserving existing `F004` / `B001` ids in the main worktree or non-git fallback path.
**Non-Goals:** Do not rename existing human entries or plans, do not change the status lifecycle, do not vendor Superpowers dependencies, and do not alter unrelated plan execution behavior.
**Architecture:** Keep numbering ownership in `record_human_request.py`, adding a small git-worktree detector and branch slug formatter beside the existing `next_id` logic. Extend plan README validation to recognize branch-qualified source ids so future plans can still trace back to worktree-created human entries. Update the workflow reference docs and generated workspace templates so manual entries and generated entries share the same documented id grammar.
**Baseline:** Request ids are currently parsed with `^##\s+([A-Za-z])(\d+):` and generated as `F001`, `F002`, `B001`, `B002` regardless of whether intake runs in the primary checkout or a linked worktree. `generate_plans_readme.py` only accepts feature/bugfix plan source ids that look like `F001` / `B001`, with optional split suffixes such as `F001-01`.
**Exit Criteria:** Running intake from a linked worktree produces a request heading with the current branch slug in the id, running intake from the main worktree preserves the current numeric-only id format, plan README generation accepts plans whose source entry is branch-qualified, and the script unittest suite passes.

## Task 1: Add branch-qualified intake ids

**Outcome:** `record_human_request.py` detects linked git worktrees and appends a sanitized branch qualifier to generated feature and bug ids without changing main-worktree behavior.
**Files:**
- Modify: `skills/using-superplan/scripts/record_human_request.py`
- Modify: `skills/using-superplan/scripts/tests/test_record_human_request.py`

**Verification:**
- `python3 -m unittest skills.using-superplan.scripts.tests.test_record_human_request`

- [ ] Review the current `ENTRY_PATTERN`, `next_id`, and `run` flow so the change stays inside intake numbering.
- [ ] Add a helper that runs `git rev-parse --git-dir` and `git rev-parse --git-common-dir` from the target root, treating differing paths as a linked worktree and equal paths as the main worktree.
- [ ] Add a helper that reads `git branch --show-current`, falls back to `git rev-parse --short HEAD` for detached HEAD, replaces non-`[A-Za-z0-9._-]` characters with `-`, trims separator runs, and appends `-branch` when the slug would otherwise end in `-\d+`.
- [ ] Extend request id parsing to recognize both numeric ids and branch-qualified ids like `F004@feature-x`; keep the next numeric value based on the maximum numeric suffix in the whole file so existing ordering remains monotonic.
- [ ] Render ids as `{prefix}{number:03d}{qualifier}` where `qualifier` is empty in the main worktree and `@{branch_slug}` in a linked worktree.
- [ ] Add unit tests for unchanged first/second feature behavior, branch-qualified feature ids in a mocked linked worktree, branch-qualified bug ids, unsafe branch slug sanitization, and the `-\d+` slug suffix guard.
- [ ] Run the task verification command and confirm the focused record-human-request tests pass.

## Task 2: Teach plan validation about branch-qualified source ids

**Outcome:** Plans created from worktree-qualified human entries validate and appear in `docs/superplan/plans/README.md` without weakening existing numeric id checks.
**Files:**
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `skills/using-superplan/scripts/tests/test_generate_plans_readme.py`

**Verification:**
- `python3 -m unittest skills.using-superplan.scripts.tests.test_generate_plans_readme`

- [ ] Review `SOURCE_FROM_ID`, `HUMAN_ENTRY_PATTERN`, `PlanMetadata.source_id`, and source-entry validation.
- [ ] Update the human entry regex to collect ids shaped as `F001`, `B001`, `F001@feature-x`, and `B001@fix-y`.
- [ ] Update feature/bugfix plan id validation so numeric ids keep accepting `F001` and `F001-01`, and branch-qualified ids accept `F001@feature-x` plus split ids that remain unambiguous because generated branch slugs never end in `-\d+`.
- [ ] Keep invalid lowercase or malformed ids failing with clear errors.
- [ ] Add tests proving a branch-qualified feature plan validates against a matching human entry and that a branch-qualified plan still fails when the matching human entry is missing.
- [ ] Run the task verification command and confirm the focused README generator tests pass.

## Task 3: Update workflow docs and templates

**Outcome:** The documented numbering rule matches the new behavior for generated intake entries and for humans manually adding entries.
**Files:**
- Modify: `skills/using-superplan/references/intake-spec.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`
- Modify: `skills/using-superplan/scripts/init_workspace.py`
- Modify: `skills/using-superplan/scripts/tests/test_init_workspace.py`

**Verification:**
- `python3 -m unittest skills.using-superplan.scripts.tests.test_init_workspace`
- `rg -n "@branch|worktree|branch-qualified|F001@|B001@" skills/using-superplan skills/feature-plan-and-delivery skills/bugfix-plan-and-delivery`

- [ ] Update intake docs to state that normal ids remain `F001` / `B001`, linked worktree ids become `F001@branch-slug` / `B001@branch-slug`, and the numeric portion is still zero-padded.
- [ ] Update plan docs and delivery-loop examples so feature/bugfix plans may encode source entries such as `F001@feature-x` in addition to existing `F001` and `F001-01` forms.
- [ ] Update feature and bugfix skill type-specific rules to mention branch-qualified source ids when the accepted human entry came from a linked worktree.
- [ ] Update `init_workspace.py` human-doc boilerplate and its tests so newly initialized repositories explain the branch-qualified id form.
- [ ] Run the task verification commands and confirm docs/tests reflect the same id grammar.

## Task 4: Run full regression checks and finish the feature

**Outcome:** The work is verified through the repository's script test suite, generated plan index, and human progress updates.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F003-worktree-aware-request-numbering.md`
- Modify: `docs/superplan/plans/README.md`

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`

- [ ] Run the full script unittest suite and fix any regressions in intake, README generation, or workspace initialization behavior.
- [ ] Run the plan README generator with `--write --check`.
- [ ] Mark this plan `complete` only after implementation and verification are done.
- [ ] Mark `F003` in `docs/superplan/human/features.md` as `done` only after the plan is complete.
- [ ] Create a task-level commit containing only the F003 implementation, tests, docs, and progress/index updates.

## References
- `docs/superplan/human/features.md`
- `skills/using-superplan/scripts/record_human_request.py`
- `skills/using-superplan/scripts/generate_plans_readme.py`
- `skills/using-superplan/references/intake-spec.md`
- `skills/using-superplan/references/plan-spec.md`
