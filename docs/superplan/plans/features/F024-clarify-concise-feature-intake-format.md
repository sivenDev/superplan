---
id: "F024"
title: "Clarify Concise Feature Intake Format"
type: "feature"
status: "draft"
summary: "Make feature intake record concise request intent without expanding ordinary entries into RFC-style design documents."
source: "docs/superplan/human/features.md"
created: "2026-08-20"
depends_on: []
parent: ""
---
# Clarify Concise Feature Intake Format Plan

**Goal:** Keep feature registration compact and clearly separated from optional RFC design work.
**Scope:** Update the canonical intake guidance and feature template so a feature body normally uses one concise paragraph covering the requested outcome, main scope, acceptance, and key constraints; when a paragraph is sufficient, it must not be expanded into RFC-style sections or design analysis. Align the current repository example and focused behavior/test coverage with that contract.
**Non-Goals:** Do not change request ids, statuses, recorder behavior, RFC triggers, RFC document structure, plan structure, workspace schema, or runtime code.
**Architecture:** Keep the rule in `intake-spec.md`, which already owns request capture. Keep the initialized `features.md` asset as the human-facing example, without duplicating the rule into `feature-plan-and-delivery/SKILL.md`. Preserve RFC decisions, alternatives, risks, and approval conditions in the existing route-owned RFC specification.
**Baseline:** Feature entries require only title, status, created date, and an optional body, but the current template merely lists goal/scope/acceptance/non-goals and the intake reference does not explicitly discourage RFC-style expansion. The recorder writes the supplied body verbatim, so agents can turn ordinary request capture into a mini-RFC even though no such structure is required.
**Exit Criteria:** Canonical intake guidance explicitly prefers one concise paragraph when it can faithfully capture the request; the feature template demonstrates that granularity; feature entries exclude design decisions, alternatives, risk arguments, and implementation steps unless they are themselves part of the requested constraint; RFC and plan contracts remain unchanged; focused initialization/package checks, applicable behavior review, repository verification, registry/index validation, and diff checks pass.

## Task 1: Establish and verify the concise feature-intake boundary

**Outcome:** Agents and newly initialized workspaces record ordinary features at request granularity while retaining RFC and plan separation.
**Files:**
- Modify: `skills/using-superplan/references/intake-spec.md`
- Modify: `skills/using-superplan/assets/human/features.md`
- Modify: `docs/superplan/human/features.md`
- Modify: `tests/behavior/workflow.md`
- Modify: `tests/scripts/test_init_workspace.py`

**Change Map:**
- `intake-spec.md`: require a short title and the smallest faithful body; prefer one paragraph covering outcome, scope, acceptance, and key constraints; prohibit unnecessary RFC-style design sections, alternatives, risk analysis, or implementation steps.
- Feature asset and current registry guidance: replace the ambiguous optional-description hint with a compact one-paragraph example and an explicit handoff of design decisions to RFC and executable work to plans.
- Behavior scenario: make explicit fast feature intake expect a concise request body rather than RFC-style expansion while preserving direct acceptance and plan-approval gates.
- Initialization test: lock the concise template guidance and continue proving existing human registries remain byte-preserved.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Inspect applicable feature-intake scenarios in `tests/behavior/workflow.md` and all four root skills for unchanged routing/reference ownership.
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/human_requests.py --root . validate`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [ ] Define the smallest faithful feature body and keep the rule in the intake authority.
- [ ] Update the initialized and current human guidance without changing recorder or migration behavior.
- [ ] Cover concise intake in focused initialization and behavior contracts.
- [ ] Verify, mark F024 complete, set the feature done, refresh the index, and create a dedicated F024 delivery commit.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F019/02-rfc-workflow-guidance-and-release.md`
- `docs/superplan/plans/features/F023-raise-automatic-rfc-trigger-threshold.md`
- `skills/using-superplan/references/intake-spec.md`
- `skills/feature-plan-and-delivery/references/rfc-spec.md`
