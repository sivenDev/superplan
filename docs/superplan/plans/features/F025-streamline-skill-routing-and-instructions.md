---
id: "F025"
title: "Streamline Skill Routing and Instruction Ownership"
type: "feature"
status: "complete"
summary: "Make Superplan skill selection and instruction ownership concise while preserving every approval, safety, and state-integrity boundary."
source: "docs/superplan/human/features.md"
created: "2026-08-20"
depends_on: []
parent: ""
---
# Streamline Skill Routing and Instruction Ownership Plan

**Goal:** Make Superplan route requests through concise, discriminating skills and one authoritative instruction layer per workflow rule.
**Scope:** Implement the approved F025 RFC across the four root skills, UI-facing skill metadata where routing meaning changes, shared delivery/plan/verification references, the initialized and current feature guidance, human-facing architecture documentation, and focused structural/behavior coverage. Add the approved compact-plan contract for low-risk single-boundary work while retaining complete plans for material architecture, baseline, migration, contract, or bug information.
**Non-Goals:** Do not add, remove, rename, or merge root skills; change CLI behavior, request/RFC/plan metadata, identifiers, statuses, workspace schema, scripts, release versions, installation state, approval gates, checkpoint behavior, worktree consent, bug root-cause requirements, or historical plan validity.
**Architecture:** Treat this as a standard-risk cross-route instruction change. Keep the four-skill package and existing conditional references. Narrow `using-superplan` to setup/check/migrate plus explicit fallback dispatch, let the three specialized skills own natural-language PRD/feature/bug triggers, and make every `SKILL.md` contain only selection, inputs/outputs, reference-loading points, and route-specific deltas. Keep `delivery-loop.md` as the cross-route lifecycle authority but replace its repeated ten-step expansion with a compact state machine. Let `plan-spec.md` define conditional compact/full body requirements, and let `verification-matrix.md` distinguish focused, final, and metadata-only evidence without duplicating checks already owned by `tools/verify_repo.py`. Human assets remain minimal output templates; README remains human-facing rather than workflow authority.
**Baseline:** The repository exposes exactly four valid skills and all current workflow validations pass, but `using-superplan` overlaps the specialized route descriptions and repeats delivery, registry, plan-discovery, and recovery rules. Feature and bugfix skills restate their conditional references; `delivery-loop.md` defines thematic policies and then repeats them in Delivery; every new plan requires Architecture, Baseline, and Change Map even when those fields carry no decision value; the feature template includes detailed RFC layout and language rules; and package tests intentionally require the broad entry trigger established before the specialized-route architecture was clarified.
**Exit Criteria:** Natural-language PRD, feature, and bug requests have discriminating specialized descriptions while explicit `$using-superplan` remains a valid setup and fallback entry; the four root bodies contain no duplicated reference procedures; shared lifecycle rules have one owner and a compact execution state machine; new low-risk plans may omit only conditionally irrelevant Architecture, Baseline, and Change Map while core scope, non-goals, files, exit criteria, verification, and bug-specific evidence remain mandatory; feature templates keep only minimal RFC meaning; final verification avoids nested duplicate commands; package/initialization tests and applicable fresh-context scenarios prove routing, progressive disclosure, compact-plan, approval, safety, and completion behavior; `python3 tools/verify_repo.py` passes once against the stabilized implementation; F025 progress is completed and delivered in a separate task commit without the local `.codex/config.toml`.

## Task 1: Make root skills discriminating and progressively disclosed

**Outcome:** Skill selection chooses the specialized project, feature, or bug route directly, while explicit `using-superplan` remains a concise workspace/setup and fallback dispatcher.
**Files:**
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/project-bootstrap-from-prd/SKILL.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`
- Modify: `skills/using-superplan/agents/openai.yaml`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- Root skill frontmatter and bodies: partition natural-language triggers, remove Route Entry and route-level reference restatements, retain exact inputs/outputs and conditional load points, and preserve implicit invocation for all four skills.
- `using-superplan/agents/openai.yaml`: keep quoted UI fields and an explicit `$using-superplan` default prompt while aligning the short description with setup/check/migrate and fallback dispatch.
- Package and behavior coverage: replace the obsolete broad-entry trigger requirement with discriminating description and progressive-disclosure invariants; exercise direct specialized routing and explicit total-entry dispatch without keyword-only brittle assertions.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Run `/Users/zhengxiwan/.codex/skills/.system/skill-creator/scripts/quick_validate.py` for each of the four root skill directories.
- Execute the applicable routing and reference-loading scenarios from `tests/behavior/workflow.md` in fresh contexts.

- [x] Partition automatic trigger intent between the total entry and the three specialized routes without disabling implicit invocation.
- [x] Reduce each root skill to non-obvious routing and route-specific decisions while retaining every required reference load.
- [x] Keep UI metadata consistent with explicit `$using-superplan` invocation and validate all four skill packages.
- [x] Prove specialized requests do not require the redundant total-entry layer and explicit total-entry requests still dispatch correctly.

## Task 2: Consolidate shared authorities and add risk-proportionate plan bodies

**Outcome:** Shared references express each rule once, low-risk plans stay compact, and human-facing templates do not carry runtime RFC implementation detail.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `skills/using-superplan/assets/human/features.md`
- Modify: `docs/superplan/human/features.md`
- Modify: `README.md`
- Modify: `tests/scripts/test_init_workspace.py`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- `delivery-loop.md`: retain workspace safety, recovery, checkpoint, risk, evidence, approval, completion, commit, and worktree-handoff invariants; replace duplicated detailed Delivery prose with the approved six-stage state machine and ownership links.
- `plan-spec.md`: preserve metadata and cross-artifact enforcement while defining core required fields plus conditional Architecture, Baseline, and Change Map rules; keep full detail for material boundaries and bugfix Reproduction/Root Cause.
- `verification-matrix.md`: distinguish focused iteration, one final authoritative regression, and metadata-only follow-up; state that `tools/verify_repo.py` subsumes its listed repository sub-checks.
- Feature assets/current guidance and README: reduce the registry template to request-level RFC meaning, preserve initialized output clarity, and document the human-facing architecture without making README a runtime authority.
- Tests and scenarios: cover minimal initialized guidance, compact versus full plan decisions, retained approval/safety boundaries, and the absence of verification ceremony that proves no changed claim.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- Inspect all four root skills and every directly changed reference together for one authority per rule.
- Execute applicable compact/full plan, verification-selection, RFC, approval, checkpoint, and completion scenarios from `tests/behavior/workflow.md`.

- [x] Replace the repeated Delivery expansion with a compact lifecycle state machine without losing recovery or handoff behavior.
- [x] Make plan body detail conditional on material information while preserving mandatory scope, evidence, files, non-goals, exit criteria, and bug-specific proof.
- [x] Prevent final verification from listing or rerunning checks already contained in the authoritative repository command.
- [x] Keep feature human guidance concise and synchronize generated/current examples without migrating unrelated user-maintained content.

## Task 3: Verify, complete, and deliver F025

**Outcome:** The approved instruction architecture is behaviorally preserved, progress-complete, and committed independently from its RFC and plan checkpoints.
**Files:**
- Modify: `docs/superplan/plans/features/F025-streamline-skill-routing-and-instructions.md`
- Modify: `docs/superplan/plans/README.md`
- Modify: `docs/superplan/human/features.md`

**Change Map:**
- Final verification: after skill, reference, template, metadata, and behavior changes stabilize, run the authoritative repository contract once and inspect relevant fresh-context scenarios and warnings.
- Progress: record concise completion evidence, mark the F025 plan complete, then set the F025 human entry to done and refresh the generated index without rerunning unchanged implementation checks.
- Delivery: inspect exact task diffs, stage only F025 implementation/progress paths, preserve `.codex/config.toml`, and create a separate F025-qualified task commit.

**Verification:**
- `python3 tools/verify_repo.py`
- After metadata-only completion updates, run `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check` and inspect `git status --short`.

- [x] Obtain current structural, behavior, initialization, skill-package, repository, plan-index, diff, and ownership evidence.
- [x] Mark the plan complete before transitioning F025 to done, without rerunning unchanged implementation regression after metadata-only edits.
- [x] Create a dedicated F025 delivery commit that excludes `.codex/config.toml` and preserves the RFC/plan approval checkpoints.

## Completion Evidence

- Focused package and initialization suites passed with 7 and 12 tests. All four root skills passed `quick_validate.py` using the existing Python environment with PyYAML.
- Routing, progressive disclosure, compact/full plan, verification selection, approval, checkpoint, completion, bug, and RFC behavior scenarios were updated or inspected against the approved ownership boundaries.
- `python3 tools/verify_repo.py` passed 109 tests, compiled 19 Python files, and passed workspace compatibility, human registry, managed guardrail, plan-index, and diff checks.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/rfcs/F025.md`
- `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `docs/superplan/plans/features/F019/02-rfc-workflow-guidance-and-release.md`
- `docs/superplan/plans/features/F020-safe-checkpoint-commits-before-human-decision-pauses.md`
- `docs/superplan/plans/features/F023-raise-automatic-rfc-trigger-threshold.md`
- `docs/superplan/plans/features/F024-clarify-concise-feature-intake-format.md`
