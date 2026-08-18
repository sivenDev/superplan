---
id: "F023"
title: "Raise the Automatic RFC Trigger Threshold"
type: "feature"
status: "complete"
summary: "Require a concrete, consequential, unresolved, and non-trivially-resolvable decision before AI autonomously enables an RFC."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F022"]
parent: ""
---
# Raise the Automatic RFC Trigger Threshold Plan

**Goal:** Prevent ordinary features from entering the RFC workflow merely because they mention architecture, multiple modules, or a general risk category.
**Scope:** Tighten only the AI-autonomous RFC selection rule. Require all four conditions: a concrete unresolved design decision; materially different viable options or one difficult-to-reverse choice; a wrong choice that changes acceptance or creates hard-to-reverse public-contract, migration, security, concurrency, data-integrity, release, or rollback impact; and inability to resolve the issue through one clarification, a conservative default, or a normal development plan. Direct human requests and persisted `requires_rfc: true` remain authoritative. Borderline cases ask one concise clarification instead of silently enabling RFC.
**Non-Goals:** Do not change RFC artifacts, multi-RFC layouts, request metadata, parsers, validators, state transitions, approval gates, workspace assets, schema, package version, release state, remote state, or local installation. Do not introduce a score or category-counting system.
**Architecture:** Keep the complete autonomous-selection test in the route-owned `rfc-spec.md`. Keep `feature-plan-and-delivery/SKILL.md` concise by referring to that full test and naming only the decisive stop behavior: keyword/category matches are insufficient, and borderline cases ask one clarification. Express observable judgment examples in behavior scenarios, and lock the minimal package contract with the existing plugin-package test.
**Baseline:** The feature skill currently says material design risk can make an RFC necessary, while the RFC reference lists broad categories such as architecture, cross-module ownership, contracts, migration, security, concurrency, data integrity, release, and rollback. It excludes size and unfamiliarity but does not explicitly require every consequential-decision condition, so an agent can over-trigger RFC by matching a category keyword.
**Exit Criteria:** Explicit human RFC requests and persisted RFC routing remain unchanged; autonomous RFC selection requires all four approved conditions; reversible internal choices, task/file/module count, unfamiliarity, and general uncertainty are explicit non-triggers; borderline cases request one concise clarification; feature skill and RFC reference remain concise and non-duplicative; behavior scenarios distinguish qualifying, non-qualifying, and borderline cases; package-contract, registry, plan-index, workspace, diff, and status checks pass; F023 is committed separately without release or installation changes.

## Task 1: Tighten the route-owned autonomous RFC decision

**Outcome:** Agents use RFC automatically only when a concrete unresolved decision has consequential and hard-to-reverse planning impact that cannot be resolved more cheaply.
**Files:**
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/feature-plan-and-delivery/references/rfc-spec.md`
- Modify: `tests/behavior/workflow.md`
- Modify: `tests/scripts/test_plugin_package.py`

**Change Map:**
- `SKILL.md`: replace the broad material-risk trigger sentence with a concise requirement to satisfy the full reference test; reject keyword/category matching and route borderline cases to one clarification question.
- `rfc-spec.md`: preserve explicit and persisted triggers, define the four cumulative autonomous conditions, list reversible/scale/unfamiliarity/general-uncertainty non-triggers, and keep explicit-decline behavior unchanged.
- Behavior scenario 16: retain explicit RFC, qualifying high-risk, direct feature, decline, language, path, multi-RFC, and revision cases; add category-only and borderline prompts with direct-plan and clarification expectations.
- Package contract: assert the cumulative threshold, non-trigger, and clarification language without testing prose mechanically beyond the stable decision boundary.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Inspect `feature-plan-and-delivery/SKILL.md` and `references/rfc-spec.md` for concise ownership and unchanged explicit/persisted triggers
- Inspect the applicable scenario 16 prompts against the accepted F023 request
- `git diff --check -- skills/feature-plan-and-delivery tests/behavior/workflow.md tests/scripts/test_plugin_package.py`

- [x] Require every consequential-decision condition before autonomous RFC enablement.
- [x] Make category keywords and reversible internal choices explicit non-triggers.
- [x] Route borderline cases through one concise clarification question.
- [x] Preserve explicit requests, persisted routing, declines, artifact rules, and approval gates.

## Task 2: Verify, complete, and deliver F023

**Outcome:** The stricter threshold is shipped as a small, reviewed workflow change with no unrelated runtime or release effects.
**Files:**
- Modify: `docs/superplan/plans/features/F023-raise-automatic-rfc-trigger-threshold.md`
- Modify: `docs/superplan/plans/README.md`
- Modify: `docs/superplan/human/features.md`

**Change Map:**
- Run the focused package contract after final skill/reference/scenario edits; inspect all four root skills to confirm routing ownership remains unchanged.
- Validate the human registry, workspace compatibility, guardrails, generated plan index, diff, and exact Git status.
- Mark F023 complete, set its human entry to done through the canonical command, refresh the index without rerunning unchanged checks, and create a dedicated final commit.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python3 skills/using-superplan/scripts/human_requests.py --root . validate`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check --root .`
- `git diff --check`
- `git status --short`

- [x] Obtain focused package, behavior, workspace, registry, guardrail, plan-index, diff, and status evidence.
- [x] Mark the plan complete and F023 done only after the workflow contract is final.
- [x] Create one final F023 commit without runtime-script, version, release, remote, or installation changes.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F019/02-rfc-workflow-guidance-and-release.md`
- `docs/superplan/plans/features/F022-support-multiple-rfcs-per-feature.md`
- `skills/feature-plan-and-delivery/SKILL.md`
- `skills/feature-plan-and-delivery/references/rfc-spec.md`
- `tests/behavior/workflow.md`
