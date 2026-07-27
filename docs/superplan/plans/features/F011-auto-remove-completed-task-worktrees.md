---
id: "F011"
title: "Auto-Remove Completed Task Worktrees"
type: "feature"
status: "complete"
summary: "Authorize concise automatic cleanup of task-created worktrees while preserving their branches."
source: "docs/superplan/human/features.md"
created: "2026-07-27"
depends_on: ["F005", "F009"]
parent: ""
---
# Auto-Remove Completed Task Worktrees Plan

**Goal:** Remove completed task worktrees without an extra confirmation.
**Scope:** Add one concise managed guardrail covering task-created worktree cleanup when nothing must be preserved, while keeping the branch.
**Non-Goals:** Do not delete branches, force-remove dirty worktrees, or change worktree creation consent.
**Architecture:** Extend the existing workspace-safety guardrail and synchronize its managed `AGENTS.md` block.
**Baseline:** Worktree cleanup currently requires separate user authorization through `finishing-a-development-branch`; Superplan has no standing project authorization.
**Exit Criteria:** The managed guardrail authorizes cleanup without repeated confirmation, limits it to completed task worktrees with nothing to preserve, keeps the branch, and synchronization checks pass.

## Task 1: Add and synchronize the cleanup guardrail

**Outcome:** Superplan-managed projects receive the concise cleanup authorization.
**Files:**
- Modify: `skills/using-superplan/assets/agents-guardrails.md`
- Modify: `AGENTS.md` (managed block only)

**Change Map:**
- Guardrail item 1: add the worktree cleanup and branch-retention rule without expanding unrelated workflow guidance.

**Verification:**
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `git diff --check`

- [x] Add one concise cleanup sentence.
- [x] Synchronize only the managed `AGENTS.md` block and preserve unrelated changes.
- [x] Verify the synchronized guardrail and final diff.

## Task 2: Complete progress and delivery

**Outcome:** F011 is traceable through Superplan progress and a dedicated commit.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F011-auto-remove-completed-task-worktrees.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Mark F011 complete only after guardrail verification, regenerate the index, and commit only task files.

**Verification:**
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git status --short`

- [x] Record verification evidence and complete F011 progress.
- [x] Create an F011-qualified commit without unrelated files.

## Implementation Evidence

- Added one cleanup sentence to the managed guardrail template and synchronized the current project block without changing its unrelated memory timestamp.
- `sync_agents_guardrails.py --check` and `git diff --check` passed against the final guardrail state.
- The task commit preserves the existing `deps/` directory and non-managed `AGENTS.md` timestamp change outside its staged paths/hunk.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `skills/using-superplan/assets/agents-guardrails.md`
