---
id: "F020"
title: "Safe Checkpoint Commits Before Human-Decision Pauses"
type: "feature"
status: "complete"
summary: "Require safe task-scoped checkpoint commits before mutation-bearing workflow pauses that await human decisions."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F008"]
parent: ""
---
# Safe Checkpoint Commits Before Human-Decision Pauses Plan

**Goal:** Keep Superplan worktrees clean and recoverable whenever an active workflow must pause for a human decision after producing persistent changes.
**Scope:** Add one canonical rule requiring Superplan to validate changed artifacts, stage only current-task paths or hunks, and create a plan- or request-qualified checkpoint commit immediately before a required human-decision pause when the current task has persistent changes. Apply the rule to intake, draft-plan approval, queued approval, blockers, and delivery follow-up pauses while preserving the existing pre-mutation worktree-consent boundary. Make the behavior visible in initialized workspace guardrails and cover both commit and no-commit cases in the behavior scenarios.
**Non-Goals:** Do not commit when the task made no persistent change; commit pre-existing, user-owned, unrelated, secret-bearing, or known-invalid state; add a Git helper command or new workflow status; replace worktree isolation or merge-conflict handling; combine checkpoint and final delivery commits; automatically amend, squash, merge, or delete branches or worktrees; or duplicate the detailed rule across route-specific skills.
**Architecture:** Keep the complete decision-pause policy in `delivery-loop.md`, adjacent to workspace safety and lifecycle gates. Inject one concise project guardrail from `agents-guardrails.md` so direct route use inherits the checkpoint boundary without reproducing its exceptions. Treat checkpoint commits as durable handoff baselines, distinct from the final delivery commit; once another branch or worktree may depend on a checkpoint, its history is not rewritten. Extend the workflow behavior scenarios rather than adding brittle wording tests.
**Baseline:** The delivery loop currently requires precise staging and one task-level commit only after delivery is complete. Intake review, draft-plan approval, queued approval, and blocker pauses can therefore return control with task-owned registry, plan, index, or implementation changes still dirty. F005 prevents automatic commits of pre-existing dirty work before mutation, F008 keeps approval and verification state-aware, and F016 assumes a completed task commit before linked-worktree merge and cleanup decisions; none defines a safe commit boundary for earlier mutation-bearing pauses.
**Exit Criteria:** Every required human-decision pause creates a validated, current-task-only checkpoint commit when persistent task changes exist; pre-mutation and no-change pauses create no commit; user-owned, unrelated, secret-bearing, and known-invalid changes are never included; an unsafe checkpoint is reported explicitly instead of fabricated; checkpoint and final delivery commits remain distinct and referenced checkpoints are not rewritten; initialized managed guardrails carry the concise rule; the applicable behavior scenarios, guardrail synchronization, package contract, repository verification, plan validation, diff review, and dedicated F020 delivery commit pass.

## Task 1: Establish the safe human-decision checkpoint boundary

**Outcome:** The shared workflow and initialized workspace guidance consistently produce a clean, durable task baseline before mutation-bearing human pauses without absorbing unsafe or unrelated state.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/assets/agents-guardrails.md`
- Modify: `AGENTS.md` (managed guardrails block only)
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- `delivery-loop.md`: define the pause trigger, changed-artifact validation, exact staging, checkpoint identity, no-op and unsafe-state exceptions, dirty-state reporting, final-commit separation, and no-rewrite boundary.
- `agents-guardrails.md`: add one concise checkpoint requirement beside workspace safety and task commit ownership while leaving detailed exceptions in the delivery loop.
- `AGENTS.md`: synchronize only the managed block generated from the updated asset.
- `tests/behavior/workflow.md`: cover a draft-plan approval pause with task-owned changes, a no-change or pre-mutation decision, unsafe/unrelated changes, and later continuation from the committed checkpoint.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- Execute the F020 checkpoint scenarios from `tests/behavior/workflow.md` in fresh contexts.
- `git diff --check -- skills/using-superplan/references/delivery-loop.md skills/using-superplan/assets/agents-guardrails.md AGENTS.md tests/behavior/workflow.md`

- [x] Require a checkpoint only when a mandatory human-decision pause follows persistent current-task mutations.
- [x] Validate affected artifacts and stage only current-task paths or hunks before committing with the plan or request id and decision gate in the message.
- [x] Skip commits for pre-mutation and no-change pauses, and forbid pre-existing, user-owned, unrelated, secret-bearing, or known-invalid content.
- [x] Report any unavoidable dirty state and its exact paths when a safe checkpoint cannot be formed instead of creating a misleading commit.
- [x] Keep checkpoint commits separate from final delivery and prohibit rewriting a checkpoint after another branch or worktree may rely on it.
- [x] Synchronize the concise managed guardrail and verify both positive and negative behavior boundaries without duplicating the full policy in route skills.

## Task 2: Verify and deliver F020 independently

**Outcome:** The checkpoint policy is regression-safe, progress-complete, and recorded through distinct approval-checkpoint and final-delivery commits containing only F020 work.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F020-safe-checkpoint-commits-before-human-decision-pauses.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Review F005, F008, F013, F014, F015, and F016 alongside F020 so checkpoint commits extend workspace safety and lifecycle traceability without weakening isolation, transactional writes, concise blocker handling, or post-worktree authorization.
- Run focused checks while editing and `python3 tools/verify_repo.py` once after the instruction, guardrail, and behavior state stabilizes; reuse that evidence after metadata-only completion updates.
- Mark F020 complete before setting its human request to `done`, refresh the plan index, inspect exact staged content, and create a dedicated final delivery commit distinct from the draft-approval checkpoint.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`
- `git log --oneline --grep F020`

- [x] Confirm the related plan closure has accurate dependencies and one canonical checkpoint-policy owner.
- [x] Obtain current package, behavior, guardrail, repository, plan-index, diff, and status evidence against the stabilized implementation.
- [x] Complete the plan, mark F020 done, regenerate the index, and create an F020-qualified final delivery commit without rewriting the approval checkpoint.

## Implementation Evidence

- Approval checkpoint: `96e94d6 plan(F020): checkpoint draft for approval` contains only the accepted request, draft plan, and generated index; the worktree was clean before approval, and execution preserved the checkpoint unchanged.
- Canonical behavior: `delivery-loop.md` now owns validation, exact staging, excluded-state handling, post-commit status reporting, final-commit separation, and immutable reported checkpoints; all four root Superplan skills load that shared reference.
- Managed guidance and scenarios: the synchronized guardrail carries one concise checkpoint requirement, while scenarios 1-4c and 6-6b cover mutation-bearing pauses, pre-mutation/no-change exclusions, queued approval, unrelated or invalid state, and continuation from the committed baseline.
- Independent behavior review: a fresh read-only agent review first found the missing excluded-path report, then passed all affected boundaries after the correction, including post-commit task-state confirmation and the no-rewrite rule.
- Final verification: `python3 tools/verify_repo.py` passed 105 tests, compilation of 19 Python files, workspace compatibility, strict request validation, guardrail synchronization, plan-index validation, and `git diff --check` against the stabilized implementation.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `docs/superplan/plans/features/F015-automatically-resolve-non-blocking-migration-conflicts.md`
- `docs/superplan/plans/features/F016-require-post-worktree-delivery-handoff.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/assets/agents-guardrails.md`
- `tests/behavior/workflow.md`
