---
id: "F010"
title: "Clarify Worktree Numbering Composition"
type: "feature"
status: "complete"
summary: "Make dirty-worktree isolation guidance compose correctly with branch-qualified request numbering."
source: "docs/superplan/human/features.md"
created: "2026-07-21"
depends_on: ["F003", "F005", "F009"]
parent: ""
---
# Clarify Worktree Numbering Composition Plan

**Goal:** Prevent agents from misclassifying an older committed worktree baseline as a request-id collision when branch-qualified intake already resolves the identity conflict.
**Scope:** Add one canonical clarification connecting Workspace Safety with linked-worktree intake, and add a behavior scenario covering both isolation and in-place continuation when the primary worktree contains an uncommitted next request id.
**Non-Goals:** Do not change request-numbering code, id grammar, worktree consent, merge-conflict handling, plan validation, or repeat the full intake contract outside `intake-spec.md`.
**Architecture:** Keep lifecycle composition in `delivery-loop.md` and executable scenario coverage in `tests/behavior/workflow.md`. Distinguish semantic request-id uniqueness from ordinary Git text conflicts: a linked worktree may reuse the numeric portion with `@branch`, while the primary worktree increments from its visible uncommitted entry.
**Baseline:** Workspace Safety correctly pauses before mutation when existing work could be overwritten, mixed into a commit, or conflict during integration. Intake separately generates branch-qualified ids in linked worktrees, but the runtime guidance and behavior scenarios do not explicitly cover their composition when the committed baseline lacks an uncommitted request entry.
**Exit Criteria:** The canonical workflow states that an older committed baseline does not by itself create an id collision; the behavior scenario expects `F044@branch` after accepting isolation and `F045` after declining it; the scenario still preserves the pre-mutation worktree-choice gate and distinguishes possible text merge conflicts; affected skill, plan-index, and diff checks pass.

## Task 1: Connect workspace isolation with request numbering

**Outcome:** Agents apply branch qualification after moving to a linked worktree instead of manually reserving the next primary-worktree number or reporting a false id collision.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- `delivery-loop.md` Workspace Safety: add one concise composition rule pointing linked-worktree intake back to the recorder's branch-qualified id behavior while keeping text-conflict risk separate.
- `tests/behavior/workflow.md`: add a combined fixture with committed `F043` and uncommitted primary-worktree `F044`, covering accepted isolation (`F044@branch`) and declined isolation (`F045`) plus forbidden false-collision reasoning.

**Verification:**
- `python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/using-superplan`
- Review the new combined scenario against `skills/using-superplan/references/delivery-loop.md` and `skills/using-superplan/references/intake-spec.md`.
- `git diff --check -- skills/using-superplan/references/delivery-loop.md tests/behavior/workflow.md`

- [x] Add only the minimum cross-reference needed to make the post-worktree numbering outcome explicit.
- [x] Cover both user choices without weakening the mandatory pre-mutation consent gate.
- [x] Distinguish request-id collision avoidance from possible Git text merge conflicts.

## Task 2: Verify and deliver F010 without absorbing unrelated state

**Outcome:** The clarified behavior is structurally valid, traceable through Superplan progress, and committed independently of the existing `AGENTS.md` timestamp noise.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F010-clarify-worktree-numbering-composition.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Review F003, F005, and F007-F010 together so numbering ownership, workspace consent, concise instruction ownership, behavior-test location, and the new composition clarification remain non-overlapping.
- Run final skill/reference, scenario, plan-index, and diff checks after wording stabilizes; then update progress metadata without rerunning unchanged checks.
- Stage only F010 files and leave the unrelated non-managed `AGENTS.md` timestamp change unstaged.

**Verification:**
- `python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/using-superplan`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [x] Confirm the clarification does not duplicate or alter the numbering algorithm contract.
- [x] Mark the plan complete and human entry done only after final evidence succeeds.
- [x] Create a dedicated commit whose message includes `F010`, excluding unrelated workspace changes.

## Implementation Evidence

- Runtime guidance: Workspace Safety gained one three-line clarification; request-id grammar and generation remain owned by `intake-spec.md` and `record_human_request.py`.
- Behavior contract: scenario 4a covers the pre-mutation consent gate, `F044@branch-slug` after isolation, `F045` in place, exact staging, and separate same-file merge risk.
- Structural validation: all four bundled skill folders passed `quick_validate.py` through an ephemeral `uv` environment providing PyYAML.
- Focused regression: the linked-worktree qualifier and branch-qualified next-id tests passed (`Ran 2 tests ... OK`).
- Final workflow metadata: plan-index generation, `git diff --check`, and exact task-path status inspection passed before delivery.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F003-worktree-aware-request-numbering.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/intake-spec.md`
- `tests/behavior/workflow.md`
