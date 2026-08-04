---
id: "F016"
title: "Require Post-Worktree Delivery Handoff"
type: "feature"
status: "complete"
summary: "Require linked-worktree delivery to report completion and request explicit merge and cleanup decisions."
source: "docs/superplan/human/features.md"
created: "2026-08-04"
depends_on: ["F005", "F013"]
parent: ""
---
# Require Post-Worktree Delivery Handoff Plan

**Goal:** Make every completed Superplan delivery from a linked worktree end with a clear completion report and explicit integration and cleanup choices.
**Scope:** Add one canonical delivery rule requiring the agent, after development, verification, and the task commit complete in a linked worktree, to state that development is complete and ask whether to merge the branch into the mainline branch and whether to remove the linked worktree directory.
**Non-Goals:** Do not automatically merge branches, delete worktrees, change worktree creation or intake behavior, prescribe one merge strategy, or duplicate the rule across route-specific skills.
**Architecture:** Keep the post-delivery decision in `delivery-loop.md`, which is loaded by every Superplan route. Keep `worktrees.md` focused on isolation setup and execution mechanics. Add one adjacent behavior scenario so the completion, authorization, and cleanup boundaries remain observable without expanding runtime instructions.
**Baseline:** The delivery loop currently ends after creating a task-level commit. It does not define the handoff when that commit was produced in a linked worktree, so completion may be reported without asking how the user wants to integrate the branch or clean up the worktree.
**Exit Criteria:** A completed linked-worktree delivery explicitly reports development completion, asks whether to merge into mainline, separately asks whether to remove the worktree directory when safe, and performs neither action without explicit authorization; the instruction has one canonical owner and the affected workflow checks pass.

## Task 1: Add the linked-worktree completion handoff

**Outcome:** The shared delivery loop and behavior contract make integration and cleanup user decisions after linked-worktree development completes.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- `delivery-loop.md` Delivery: append one concise post-commit rule for linked-worktree completion reporting, mainline merge authorization, and worktree-directory cleanup authorization.
- `tests/behavior/workflow.md`: add an adjacent worktree-delivery scenario that requires both questions and forbids implicit merge or removal.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Review all four Superplan skills and execute the new linked-worktree completion scenario against the shared delivery loop.
- `git diff --check -- skills/using-superplan/references/delivery-loop.md tests/behavior/workflow.md`

- [x] State that development, verification, and the task commit are complete before asking for follow-up actions.
- [x] Ask whether to merge the completed branch into mainline and whether to remove the linked worktree directory.
- [x] Require explicit authorization for each state-changing follow-up and avoid prescribing an automatic merge strategy.
- [x] Keep the rule only in the canonical delivery loop and prove it through one behavior scenario.

## Task 2: Verify and deliver F016 independently

**Outcome:** The instruction change is validated, progress-complete, and committed without absorbing unrelated workspace state.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F016-require-post-worktree-delivery-handoff.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Run the focused package contract and applicable worktree behavior review after wording stabilizes.
- Mark the plan complete before marking F016 done, regenerate the plan index, and create one F016-qualified commit while excluding the unrelated `AGENTS.md` memory timestamp.

**Verification:**
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Capture current instruction and behavior evidence before metadata-only completion updates.
- [x] Complete the plan, mark the human request done, and refresh the generated plan index.
- [x] Create a dedicated commit whose message includes `F016` and excludes unrelated changes.

## Implementation Evidence

- Canonical ownership: the shared Delivery section now reports completed linked-worktree development and requests separate merge and cleanup authorization; no route-specific skill or independent skill duplicates the rule.
- Behavior contract: scenario 4c requires both questions after a verified task commit and forbids implicit merge, removal, premature cleanup claims, or treating one authorization as both.
- Fresh-context verification: a read-only independent Codex run reported the required completion statement and both separate questions, and performed no merge, deletion, or file mutation.
- Final checks: the six-test plugin package contract, generated plan-index check, and `git diff --check` passed against the stabilized instruction state.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F010-clarify-worktree-numbering-composition.md`
- `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/worktrees.md`
- `tests/behavior/workflow.md`
