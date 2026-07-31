---
id: "F015"
title: "Automatically Resolve Non-Blocking Migration Conflicts"
type: "feature"
status: "complete"
summary: "Make Superplan revalidate migration blockers, recover safe cases automatically, and ask only when the active task cannot proceed safely."
source: "docs/superplan/human/features.md"
created: "2026-07-31"
depends_on: ["F014"]
parent: ""
---
# Automatically Resolve Non-Blocking Migration Conflicts Plan

**Goal:** Keep stale or unrelated Superplan migration diagnostics from turning routine work into a long user decision.
**Scope:** Add a canonical recovery triage that trusts fresh compatibility and registry evidence, continues compatible active work, applies existing safe legacy recovery automatically after workspace safety, and permits already-authorized independent migration to run in isolation without asking again. User-facing blocker reports become short and appear only when required migration cannot be completed safely.
**Non-Goals:** Do not weaken schema or registry validation, silently repair ambiguous history, fall back to an older Superplan version, automatically stash or commit user work, require subagents, or let a parallel migration modify the active task's worktree or artifacts.
**Architecture:** Keep the complete decision policy in `delivery-loop.md`, summarize only the route-entry rule in `using-superplan/SKILL.md`, retain isolation mechanics in `worktrees.md`, and specify observable behavior in repository scenarios. Fresh command evidence overrides stale diagnostic prose. Explicit authorization to auto-isolate or auto-recover the current task satisfies the existing consent gate; absent that authorization, current workspace-safety rules remain unchanged.
**Baseline:** Superplan already distinguishes compatible schemas, evidence-backed legacy metadata recovery, and important dirty-worktree risk, but it does not explicitly tell agents to discard stale migration diagnoses, continue when historical issues are unrelated to a compatible active task, reuse explicit automation authorization, or keep unavoidable blocker messages concise. This can produce unnecessary downgrade questions and broad historical-repair proposals even when current validation passes.
**Exit Criteria:** A fresh compatible check causes the active route to continue regardless of an earlier migration diagnosis; safe legacy omissions use the existing preview/write recovery without another decision; explicitly authorized independent migration may use isolated worktree/subagent execution without a repeated prompt and without blocking compatible active work; required unsafe migration still stops; no path suggests an older-version fallback; and focused behavior, package, plan-index, repository verification, diff, and status checks pass.

## Task 1: Add evidence-first automatic recovery triage

**Outcome:** Runtime guidance resolves common migration noise automatically and has one concise escalation boundary.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/worktrees.md`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `README.md`

**Change Map:**
- `delivery-loop.md`: define fresh-evidence precedence, compatible-work continuation, safe legacy recovery, authorized isolated delegation, forbidden version fallback, and the short true-blocker boundary.
- `worktrees.md`: recognize explicit current-task auto-isolation authorization and keep parallel repair separate from the active worktree and commit.
- `using-superplan/SKILL.md`: point route entry at recovery triage without duplicating it.
- `README.md`: summarize the user-visible automatic recovery behavior.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Inspect the changed references against the workspace-safety, migration, and delegation boundaries.
- `git diff --check -- skills/using-superplan README.md`

- [x] Make current read-only checks authoritative over earlier narrative diagnostics.
- [x] Continue compatible active work and automatically use only existing evidence-backed safe recovery.
- [x] Reuse explicit automation consent for isolated independent repair without weakening default workspace consent.
- [x] Stop only when required migration remains unsafe or needs new authority, using one concise blocker and no older-version fallback.

## Task 2: Prove concise automatic handling and deliver F015

**Outcome:** Fresh-context scenarios distinguish automatic recovery from genuine blocking and the feature is delivered independently.
**Files:**
- Modify: `tests/behavior/workflow.md`
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F015-automatically-resolve-non-blocking-migration-conflicts.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- `tests/behavior/workflow.md`: cover stale blocker revalidation, safe legacy recovery, explicitly authorized isolated migration, compatible active-task continuation, and concise refusal when migration is truly required and unsafe.
- Progress artifacts: capture evidence, complete the plan before the human entry, refresh the index once, and create a dedicated F015 commit while excluding unrelated `AGENTS.md` timestamp noise.

**Verification:**
- Execute the affected fresh-context workflow scenarios.
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Prove stale or unrelated historical diagnoses do not block compatible current work.
- [x] Prove explicit auto-handling authorization avoids a repeated worktree/delegation question while preserving isolation.
- [x] Prove malformed/newer schemas and structurally unsafe required migrations still stop with a concise explanation.
- [x] Complete F015, mark its human entry done, refresh the index, and create an isolated F015 commit.

## Implementation Evidence

- Runtime guidance now trusts fresh compatibility and integrity checks, automatically applies only evidence-backed legacy recovery, reuses explicit auto-isolation consent, defers overlapping repair, and forbids older-version fallback from stale diagnostics.
- Fresh-context review marked scenarios 8b, 8c, and 8d PASS and found no conflict with Workspace Safety, F005 consent, or B003 migration strictness.
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'` passed 6 tests. `python3 tools/verify_repo.py` passed 94 tests plus compilation, workspace, registry, guardrail, plan-index, and diff validation.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F012/01-bundled-superpowers-and-versioned-workspace.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `docs/superplan/plans/bugs/B003-add-safe-legacy-registry-migration.md`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/worktrees.md`
- `tests/behavior/workflow.md`
