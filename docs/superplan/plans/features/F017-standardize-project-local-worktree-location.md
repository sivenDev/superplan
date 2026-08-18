---
id: "F017"
title: "Standardize Project-Local Worktree Location"
type: "feature"
status: "complete"
summary: "Default Superplan-controlled linked worktrees to the primary project root's ignored .worktrees directory without constraining names."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F005", "F013"]
parent: ""
---
# Standardize Project-Local Worktree Location Plan

**Goal:** Make Superplan-created linked worktrees easy to find and clean up through one predictable project-local default.
**Scope:** When Superplan controls placement, default linked worktrees beneath the primary project root's `.worktrees/` directory, while honoring an explicit user path first and requiring the project-local directory to be Git-ignored. Reuse suitable current isolation instead of nesting another worktree.
**Non-Goals:** Do not constrain Git branch names, worktree child-directory names, merge strategy, cleanup timing, or harness-native placement when the harness cannot accept a path.
**Architecture:** Keep placement mechanics in the conditionally loaded `worktrees.md` reference. Preserve Workspace Safety consent in `delivery-loop.md` and delivery cleanup authorization in its existing owner. Add one adjacent behavior scenario so the default, override, ignore, reuse, and unsupported-harness boundaries remain observable without expanding top-level skills.
**Baseline:** The worktree reference follows explicit path preferences and repository conventions but has no stable fallback, allowing AI-created worktrees to appear in inconsistent external locations. This repository already ignores `.worktrees/`.
**Exit Criteria:** Superplan-controlled worktree creation uses `<primary-project-root>/.worktrees/` when no explicit path is supplied; a suitable current linked worktree is reused; the directory is confirmed ignored before use; branch and child-directory naming remain unconstrained; a harness that cannot honor the location reports its actual path without moving it; and focused instruction, behavior, plan-index, repository, diff, and status checks pass.

## Task 1: Define and prove the project-local placement default

**Outcome:** The conditional worktree guidance and behavior contract consistently place controllable worktrees under the primary project's ignored `.worktrees/` directory without adding naming policy.
**Files:**
- Modify: `skills/using-superplan/references/worktrees.md`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- `worktrees.md`: define path precedence and the primary-root `.worktrees/` fallback; retain reuse, ignore verification, original-checkout preservation, and harness limitation reporting.
- `tests/behavior/workflow.md`: extend the accepted-worktree scenario with the default path, explicit override, no branch/child naming constraint, no nested creation, and unsupported-harness reporting.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Review all four Superplan skills and execute the affected worktree scenarios from `tests/behavior/workflow.md` against the shared delivery loop and local worktree reference.
- `git diff --check -- skills/using-superplan/references/worktrees.md tests/behavior/workflow.md`

- [x] Use the primary project root's `.worktrees/` directory only as the default when Superplan controls placement and no explicit path was supplied.
- [x] Require ignore verification before project-local use without granting implicit authorization to edit `.gitignore`.
- [x] Reuse suitable current isolation and avoid nested worktree creation.
- [x] Leave branch and child-directory naming unconstrained, and report an uncontrollable harness path without moving it.
- [x] Prove the behavior through the adjacent accepted-worktree scenario without duplicating policy across route skills.

## Task 2: Verify and deliver F017 independently

**Outcome:** The placement rule is regression-safe, progress-complete, and recorded in one F017-qualified task commit.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F017-standardize-project-local-worktree-location.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Run focused checks while wording stabilizes and the repository contract once against the final instruction state.
- Mark the plan complete before marking F017 done, refresh the generated index, and stage only F017 changes.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Capture current instruction, behavior, package, and repository evidence before metadata-only completion updates.
- [x] Complete the plan, mark the human request done, and refresh the generated plan index without rerunning unchanged implementation checks.
- [x] Create a dedicated commit whose message includes `F017` and contains only the feature's implementation and progress artifacts.

## Implementation Evidence

- Instruction ownership: only `worktrees.md` now defines the controllable-location precedence; the four route skills continue to delegate workspace safety and execution details to the shared delivery loop and conditional reference.
- Behavior: a fresh read-only agent context, without reading the expected scenario, selected reuse before creation, explicit user path before `<primary-project-root>/.worktrees/`, ignore verification before project-local use, unconstrained branch/child naming, and actual-path reporting when the harness controls placement.
- Focused checks: `git diff --check -- skills/using-superplan/references/worktrees.md tests/behavior/workflow.md` passed. The package contract's pre-existing cachebuster-version failure was repaired separately in commit `0ebff1c` (`B004`), after which all six package tests passed without further F017 changes.
- Repository check: `python3 tools/verify_repo.py` passed 94 tests plus compilation, workspace, registry, guardrail, plan-index, and diff checks against the stabilized F017 implementation. B004's progress and repair were committed independently before F017 resumed.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- `docs/superplan/plans/features/F016-require-post-worktree-delivery-handoff.md`
- `skills/using-superplan/references/worktrees.md`
- `skills/using-superplan/references/delivery-loop.md`
- `tests/behavior/workflow.md`
