---
id: "F008"
title: "Optimize Superplan Workflow State and Verification"
type: "feature"
status: "complete"
summary: "Reduce avoidable Superplan state transitions and repeated checks while preserving approval, workspace-safety, verification, and traceability gates."
source: "docs/superplan/human/features.md"
created: "2026-07-21"
depends_on: ["F004", "F005", "F006", "F007"]
parent: ""
---
# Optimize Superplan Workflow State and Verification Plan

**Goal:** Make Superplan's workflow proportionate to actual state changes and artifact risk without weakening human approval, workspace safety, regression evidence, or delivery traceability.
**Scope:** Add an explicitly authorized fast intake path, batch transient plan-status/index writes, narrow full plan-set review to structural changes, reuse still-fresh safety and dependency evidence, select verification from changed artifact types, require dry-run plus explicit approval before GPT-5.6 profile replacement, and validate the resulting skill behavior with deterministic tests and fresh-context scenarios.
**Non-Goals:** Do not remove implementation-plan approval, automatically accept ambiguous requests, infer worktree or profile-replacement consent, change request or plan identifiers, weaken bug root-cause/regression requirements, vendor Superpowers, alter the pinned GPT-5.6 profile, or reopen F007's completed prose-reduction work without a behavior reason.
**Architecture:** Treat this as a standard-risk workflow and bounded script change. Keep `delivery-loop.md` authoritative for lifecycle, evidence freshness, and plan-review decisions; keep `intake-spec.md` authoritative for request capture; add a dedicated artifact-aware verification matrix referenced by the delivery loop; keep route skills limited to route-specific application. Preserve human events as gates while coalescing purely mechanical persisted transitions. Test deterministic CLI behavior in unit tests and exercise instruction-following decisions through a versioned scenario protocol in fresh contexts rather than brittle keyword-presence assertions.
**Baseline:** Intake always records `proposed`, even when the human explicitly authorizes faithful capture and planning; execution persists both `approved` and `in_progress` plus separate index refreshes even when work starts immediately; every plan edit requests a full related-plan review; workspace/dependency checks lack explicit reuse and invalidation rules; verification selection is described only by broad risk profiles; the short GPT-5.6 install flow invokes `--replace-existing` without a preceding dry-run; and some dependency tests can observe the developer's live `~/.superplan/active-superpowers-profile.json` when they omit an isolated state root.
**Exit Criteria:** Explicit, unambiguous requests can be recorded directly as `accepted` only under documented authorization conditions; ambiguous intake still pauses at `proposed`; immediate execution writes `in_progress` and refreshes the plan index once while queued approval remains representable as `approved`; structural plan changes trigger full related-set review while metadata/progress changes use local validation; reusable evidence has explicit invalidation conditions; changed artifacts map to deterministic checks; profile replacement is preceded by a no-write dry-run and explicit approval of resolved targets/conflicts; tests are isolated from live user profile state; documented behavior scenarios pass in fresh contexts; and all repository, skill, guardrail, plan-index, and diff validations succeed.

## Task 1: Add explicitly authorized adaptive intake

**Outcome:** The recorder and route contract support direct `accepted` capture for faithful, unambiguous requests while retaining `proposed` as the safe default and mandatory pause state.
**Files:**
- Modify: `skills/using-superplan/scripts/record_human_request.py`
- Modify: `skills/using-superplan/scripts/tests/test_record_human_request.py`
- Modify: `skills/using-superplan/references/intake-spec.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`

**Change Map:**
- `record_human_request.render_entry` and `run`: accept a validated `proposed|accepted` status with `proposed` as the CLI default and render the selected status without changing numbering or worktree qualification.
- `intake-spec.md`: define direct acceptance only when the human explicitly authorized capture and planning, title/body faithfully represent the request, and no material ambiguity or unresolved workspace decision remains; otherwise record `proposed` and stop for review.
- Feature and bug routes: apply the adaptive intake decision while preserving accepted-entry planning, bug discovery, and implementation-plan approval boundaries.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests -p 'test_record_human_request.py'`
- `python3 skills/using-superplan/scripts/record_human_request.py --help`
- `git diff --check -- skills/using-superplan/scripts/record_human_request.py skills/using-superplan/scripts/tests/test_record_human_request.py skills/using-superplan/references/intake-spec.md skills/feature-plan-and-delivery/SKILL.md skills/bugfix-plan-and-delivery/SKILL.md`

- [x] Keep omitted `--status` behavior backward-compatible as `proposed` and reject unsupported status values through the CLI contract.
- [x] Cover explicit `accepted`, default `proposed`, numbering, linked-worktree ids, and unchanged body rendering with deterministic tests.
- [x] Make the direct-accept decision observable and conservative for both feature and bug intake without merging request acceptance with plan approval.

## Task 2: Make lifecycle, evidence, plan review, and verification state-aware

**Outcome:** Canonical policy performs only the state transitions, reviews, and checks justified by the current change while retaining fresh evidence for every material claim.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Create: `skills/using-superplan/references/verification-matrix.md`
- Modify: `skills/using-superplan/references/agents-guardrails.md`
- Modify: `AGENTS.md` (managed guardrails block only)

**Change Map:**
- `delivery-loop.md`: preserve approval as a human event; persist `approved` for queued work, but move directly from approved draft to persisted `in_progress` with one index refresh when execution starts immediately; define freshness and invalidation rules for workspace-safety and dependency evidence.
- `plan-spec.md`: require full related-plan review for add/remove/rename/split operations and changes to Scope, Architecture, Exit Criteria, Files, or `depends_on`; allow checkbox and routine status/progress updates to use local validation and one index refresh.
- `verification-matrix.md`: map skill/reference metadata, bundled scripts, guardrail templates, plan/human/index files, profile installation, and metadata-only updates to focused and final checks.
- `agents-guardrails.md`: synchronize the generated workspace rule with structural plan-review and evidence-reuse boundaries without copying the full matrix.
- `AGENTS.md`: refresh only the managed block while preserving the unrelated memory timestamp hunk.

**Verification:**
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `for skill in skills/*; do python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"; done`
- `git diff --check -- skills/using-superplan/references`

- [x] Define queued and immediate execution paths so the human approval event remains explicit while redundant persisted status/index writes disappear.
- [x] Reuse safety and dependency evidence only while branch/worktree, relevant files/environment, external changes, and unexpected Git state remain unchanged.
- [x] Keep `check_superpowers.py` for initialization, installation, diagnostics, or unresolved dependency evidence rather than requiring it for every routed task.
- [x] Make structural review and artifact-aware verification choices deterministic enough to apply consistently without turning normal progress updates into full regressions.
- [x] Synchronize and inspect the managed `AGENTS.md` block without staging or rewriting its unrelated memory-context change.

## Task 3: Harden replacement safety and behavior-level workflow validation

**Outcome:** Profile replacement cannot proceed from the documented short flow without a reviewed dry-run, tests ignore live user profile state, and core routing/safety decisions have reusable behavior scenarios.
**Files:**
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `README.md`
- Verify: `docs/install.md`
- Modify: `skills/using-superplan/scripts/tests/test_check_superpowers.py`
- Modify: `skills/using-superplan/scripts/tests/test_init_workspace.py`
- Create: `skills/using-superplan/references/workflow-behavior-tests.md`

**Change Map:**
- `using-superplan/SKILL.md` and `README.md`: require `install_superpowers_profile.py --dry-run` first and explicit human approval of the resolved target and conflicts before `--replace-existing`; keep the existing no-write installer semantics, and summarize the state-aware workflow without duplicating its matrix.
- Dependency tests: isolate both skills and state roots so a live default manifest cannot change legacy test outcomes.
- `workflow-behavior-tests.md`: define fixture state, prompts, expected actions, forbidden actions, and evidence for explicit fast intake, ambiguous intake pause, recorded-request routing, important dirty-worktree consent, evidence reuse/invalidation, verification selection, and installer replacement approval.
- `docs/install.md`: confirm the detailed installation flow remains consistent; change it only if a concrete mismatch is found.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests -p 'test_check_superpowers.py'`
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests -p 'test_init_workspace.py'`
- `python3 skills/using-superplan/scripts/install_superpowers_profile.py --help`
- Follow `skills/using-superplan/references/workflow-behavior-tests.md` in fresh contexts and record the scenario results in the F008 plan before completion.
- `git diff --check -- skills/using-superplan/SKILL.md README.md docs/install.md skills/using-superplan/scripts/tests skills/using-superplan/references/workflow-behavior-tests.md`

- [x] Make dry-run output the approval boundary for any replacement while leaving non-conflicting installation behavior accurate.
- [x] Remove ambient-home dependence from dependency and initialization tests without weakening manifest validation coverage.
- [x] Cover trigger, intake, worktree, evidence, verification, and replacement decisions with behavior-level scenarios that test actions and pauses rather than wording.

## Task 4: Verify and deliver F008 as one traceable workflow change

**Outcome:** The optimized workflow is internally consistent, regression-safe, reflected in progress artifacts, and committed without unrelated workspace changes.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Review F004-F008 together so adaptive workflow, worktree consent, profile safety, instruction ownership, and the new state-aware rules remain independent and non-contradictory.
- Run focused checks during implementation and the full script regression once after the implementation state stabilizes; do not rerun unchanged code tests after metadata-only completion updates.
- Record behavior-scenario evidence, mark F008 and its human entry complete, refresh the plan index once, and create an F008-qualified commit that includes only the managed `AGENTS.md` hunk while excluding its unrelated memory timestamp change.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `for skill in skills/*; do python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"; done`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [x] Confirm the complete related plan set has clear boundaries and accurate dependencies without reopening completed predecessor scope.
- [x] Obtain fresh final evidence from the full regression, guardrail sync, skill validation, plan-index validation, behavior scenarios, and diff checks.
- [x] Update only F008 progress artifacts after validation and create a dedicated commit whose message includes `F008`.

## Implementation Evidence

- Recorder TDD: the new accepted-status test first failed because `--status` was unknown; the focused module then passed 10 tests after the CLI implementation.
- Script regression: `python3 -m unittest discover -s skills/using-superplan/scripts/tests` passed 84 tests against isolated profile state.
- Skill behavior: all eight fresh-context scenarios passed for fast and ambiguous intake, recorded-request reuse, dirty-worktree consent, evidence invalidation, immediate/queued approval, artifact-aware verification, and profile replacement approval.
- Structure and generated artifacts: all four bundled skills passed `quick_validate.py`; managed guardrails, the plan index, and `git diff --check` passed against the final implementation state.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F006-gpt56-superpowers-profile-installation.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/intake-spec.md`
- `skills/using-superplan/references/plan-spec.md`
