---
id: "B002"
title: "Resolve Superplan Skill Routing and Validation Gaps"
type: "bugfix"
status: "complete"
summary: "Close completion-state, workspace-migration, trigger-discovery, and self-contained skill-validation gaps in the four-skill package."
source: "docs/superplan/human/bugs.md"
created: "2026-07-30"
depends_on: ["F013"]
parent: ""
---
# Resolve Superplan Skill Routing and Validation Gaps Plan

**Goal:** Make the focused four-skill package preserve correct request state, use one safe workspace migration entry, trigger for initialization reliably, and validate without undeclared external Python packages.
**Scope:** Prevent a feature or bug request from becoming `done` until every deliverable plan for its source id is complete; make the PRD route rely on the canonical versioned workspace check/migration flow; broaden `using-superplan` metadata to cover initialization, compatibility checks, migration, and routed delivery; replace the repository's required external `quick_validate.py` check with a self-contained package metadata contract while retaining semantic trigger/reference inspection.
**Non-Goals:** Do not change request or plan schemas, add a new request status, modify plan-id/source-id rules, alter workspace schema `1`, install PyYAML or another development dependency, add another runtime script, change approval gates, or expand the four-skill public inventory.
**Architecture:** Reuse `generate_plans_readme.py` plan discovery and source-id parsing from `human_requests.py` before the forward `accepted -> done` transition, so one plan parser owns split and branch-qualified ids. Require at least one non-superseded related plan and reject any such plan that is not `complete`; update the delivery loop to complete plans before the human entry. Remove the PRD route's direct guardrail writer because every route already enters through `init_workspace.py --check` and guarded `--migrate`. Treat frontmatter and trigger metadata as a repository package contract in `test_plugin_package.py`, keeping verification deterministic with the standard library. Publish the corrections as patch version `0.3.1` while leaving workspace schema unchanged.
**Baseline:** A split request can be moved to `done` while sibling plans remain active because `set-status` validates only the human lifecycle. `project-bootstrap-from-prd` can invoke `sync_agents_guardrails.py --write` directly even though that command does not reject a newer workspace schema. `using-superplan` owns initialization but its frontmatter and UI prompt describe only already-managed routed work. The verification matrix and README require `quick_validate.py`, which currently fails under the documented `python3` environment with `ModuleNotFoundError: No module named 'yaml'`, while the repository's 68 standard-library tests pass.
**Reproduction:** Create an accepted request with one complete and one in-progress split plan, then run `human_requests.py set-status --status done`; it currently succeeds. Trigger `project-bootstrap-from-prd` directly against a newer-schema managed block and its documented fallback can call the unconditional guardrail writer. Inspect the `using-superplan` description for an empty-workspace initialization trigger. Run the documented skill validator with the current `python3`; it fails before validating any skill because PyYAML is absent.
**Root Cause:** Completion, migration, discovery, and validation are each enforced at the wrong boundary: the human status command has no plan-state awareness; one specialized route retained a pre-versioning synchronization shortcut; initialization intent is present only in the loaded body/manifest prompt rather than the trigger metadata; and project verification delegates its structural contract to an environment-owned script with an undeclared dependency.
**Exit Criteria:** `accepted -> done` is rejected when no deliverable plan exists or any related non-superseded plan is incomplete and succeeds when all deliverable plans are complete; the delivery guidance states the correct completion order; the PRD route has no direct guardrail-write bypass; automatic metadata covers initialize/check/migrate and routed project/feature/bug work consistently; the package test validates all four skill frontmatters and trigger coverage using only the standard library; required docs and verification guidance provide exact runnable repository commands; version metadata reports `0.3.1` with workspace schema `1`; focused tests, all 68+ script tests, behavior scenarios, package/manifest validation, plan/index checks, and diff/status checks pass.

## Task 1: Enforce request completion against the complete related plan set

**Outcome:** Human progress cannot hide unfinished split plans or claim delivery without a deliverable completed plan.
**Files:**
- Modify: `skills/using-superplan/scripts/human_requests.py`
- Modify: `tests/scripts/test_human_requests.py`
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- `human_requests.py`: reuse canonical plan discovery/source-id logic before `accepted -> done`; reject zero deliverable plans and list non-complete blockers without writing the registry.
- `test_human_requests.py`: cover no-plan, incomplete single/split, superseded, and all-complete transitions while proving rejected transitions preserve bytes.
- Delivery/behavior guidance: complete and validate the relevant plan set first, then set the human entry to `done` only when all deliverable sibling plans are complete.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- Execute the multi-plan completion scenario from `tests/behavior/workflow.md`
- `git diff --check -- skills/using-superplan/scripts/human_requests.py tests/scripts/test_human_requests.py skills/using-superplan/references/delivery-loop.md tests/behavior/workflow.md`

- [x] Capture the currently accepted premature `done` transition as a failing focused regression.
- [x] Add one canonical plan-state gate without duplicating split-id parsing.
- [x] Align delivery instructions and behavior evidence with the enforced completion order.

## Task 2: Align workspace routing, trigger metadata, and repository-owned validation

**Outcome:** Every entry route uses version-aware workspace handling, initialization can trigger from metadata, and skill validation is executable in a clean standard-library environment.
**Files:**
- Modify: `skills/project-bootstrap-from-prd/SKILL.md`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/using-superplan/agents/openai.yaml`
- Modify: `.codex-plugin/plugin.json`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `README.md`

**Change Map:**
- PRD route: remove the lower-level `sync_agents_guardrails.py --write` path and rely on the canonical delivery-loop compatibility check and migration boundary.
- Trigger surfaces: include initialization, compatibility checking, migration, resume, and project/feature/bug routing in the frontmatter and UI/plugin descriptions without duplicating workflow prose.
- Package contract: parse each root `SKILL.md` frontmatter with the standard library, enforce only `name` and `description`, folder/name consistency, non-empty descriptions, and required `using-superplan` trigger intents; make this test the documented structural validation command.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Run the repository plugin validator
- Inspect the direct PRD/new-workspace behavior scenarios in `tests/behavior/workflow.md`
- `git diff --check -- skills/project-bootstrap-from-prd skills/using-superplan/SKILL.md skills/using-superplan/agents .codex-plugin tests/scripts/test_plugin_package.py skills/using-superplan/references/verification-matrix.md README.md`

- [x] Remove the unsafe migration bypass and prove the specialized route has one workspace authority.
- [x] Make every automatic trigger surface cover initialization and existing-workspace delivery consistently.
- [x] Replace the undeclared PyYAML-dependent project check with an exact self-contained validation contract.

## Task 3: Publish, verify, and deliver B002

**Outcome:** The four corrections ship as a regression-safe patch release with complete progress and an isolated task commit.
**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `AGENTS.md` (managed generator-version marker only)
- Modify: `docs/superplan/human/bugs.md`
- Modify: `docs/superplan/plans/bugs/B002-resolve-skill-routing-and-validation-gaps.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Version contract: synchronize all plugin surfaces at `0.3.1`, retain workspace schema `1`, and refresh only the managed generator-version marker required by the repository's exact guardrail check.
- Final evidence: run focused tests during implementation, one full script regression after stabilization, package/plugin validation, applicable behavior scenarios, compatibility and index checks, and exact diff/status review.
- Progress/delivery: mark the B002 plan complete before transitioning its human entry to `done`, regenerate the index, and commit only B002 paths while preserving the unrelated `AGENTS.md` memory timestamp.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [x] Synchronize patch-version metadata without changing the workspace schema or managed guardrails unnecessarily.
- [x] Obtain current script, metadata, behavior, compatibility, plan, diff, and status evidence.
- [x] Complete B002 progress and create a dedicated B002 commit that excludes user-owned state.

## Implementation Evidence

- Completion TDD: the new split-plan regression first failed because `set-status` returned success with an `in_progress` sibling. The final 12-test human-request module covers missing, incomplete single/split, complete, and superseded plan states while preserving rejected registries byte-for-byte.
- Live completion boundary: against the real B002 state, `human_requests.py set-status --id B002 --status done` rejected the transition with `B002 (in_progress)` and left the human entry `accepted`.
- Routing and discovery: the package contract proves `using-superplan` metadata covers initialize/check/migrate plus project/feature/bug intents and the PRD skill contains no direct guardrail writer. A fresh-context forward test selected `using-superplan` for empty-workspace initialization and stopped the PRD route on a newer schema without mutation.
- Self-contained validation: `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'` passes using only the standard library and validates all four root frontmatters, names, descriptions, trigger intents, package inventory, and synchronized versions. Supplemental plugin and four-skill validators also pass through an isolated PyYAML tool environment.
- Final regression: `python3 -m unittest discover -s tests/scripts` passed 73 tests; workspace compatibility, exact guardrail sync, plan-index write/check, plugin validation, four structural skill validations, `py_compile`, stale-command searches, and `git diff --check` passed. All plugin surfaces report `0.3.1`, workspace schema remains `1`, and only the managed `AGENTS.md` version marker belongs to B002.

## References
- `docs/superplan/human/bugs.md`
- `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F012/01-bundled-superpowers-and-versioned-workspace.md`
- `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/verification-matrix.md`
- `skills/using-superplan/scripts/human_requests.py`
- `skills/using-superplan/scripts/generate_plans_readme.py`
