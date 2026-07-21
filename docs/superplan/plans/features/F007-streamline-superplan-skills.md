---
id: "F007"
title: "Streamline Superplan Skills for High-Capability Models"
type: "feature"
status: "complete"
summary: "Remove duplicated and low-value instructions from Superplan skills while preserving workflow gates, route-specific safeguards, and correct triggering."
source: "docs/superplan/human/features.md"
created: "2026-07-21"
depends_on: []
parent: ""
---
# Streamline Superplan Skills for High-Capability Models Plan

**Goal:** Reduce Superplan's agent-facing instruction cost while keeping every workflow boundary that affects safety, approval, traceability, or observable delivery behavior.
**Scope:** Consolidate the four bundled skills and shared references around one canonical delivery loop, shorten repeated route guidance, and align feature/bug trigger descriptions with both new and recorded requests.
**Non-Goals:** Do not change scripts, plan schema, request numbering, GPT-5.6 profile activation, generated workspace behavior, approval gates, risk semantics, bug root-cause requirements, or human-facing installation procedures.
**Architecture:** Treat this as low-risk guidance work. Keep complete cross-route policy only in `delivery-loop.md`; keep schema constraints only in `plan-spec.md`; keep request-capture rules only in `intake-spec.md`; and make each `SKILL.md` contain only entry commands, routing, and route-specific safeguards. Preserve the concise injected `agents-guardrails.md`, operational `docs/install.md`, scripts, and already-accurate UI metadata unless verification finds a concrete mismatch. The current four skills plus four shared references total 783 lines; the final set should be at least 25% smaller without compressing distinct rules into ambiguous prose.
**Baseline:** `using-superplan/SKILL.md` repeats workspace safety, risk, delegation, plan, guardrail, and completion rules already owned by `delivery-loop.md`; route skills copy the intake workflow, path convention, id examples, risk selection, delegation defaults, and plan-shape rules from shared references; `plan-spec.md` repeats several principles across its template, task rules, traceability, independence, and content-to-avoid sections. Feature and bugfix bodies support brand-new request intake, but their frontmatter descriptions currently trigger only for already-recorded entries.
**Exit Criteria:** The agent-facing instruction set is at least 25% shorter than the 783-line baseline; every retained rule has one clear authority; feature and bugfix skills trigger for new and recorded requests; approval, workspace safety, state transitions, risk profiles, debugging/TDD boundaries, plan validation, progress updates, and plan-qualified commits remain explicit; all four skills pass structural validation; repository tests, guardrail checks, plan-index checks, and diff checks pass.

## Task 1: Make shared references authoritative and concise

**Outcome:** The delivery, intake, and plan references each own one non-overlapping policy boundary with redundant teaching prose and repeated rules removed.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/intake-spec.md`
- Modify: `skills/using-superplan/references/plan-spec.md`

**Change Map:**
- `delivery-loop.md`: retain workspace safety, Superpowers composition, risk profiles, approval/execution lifecycle, progress finalization, and commit traceability once; remove repeated summaries and explanations that do not change decisions.
- `intake-spec.md`: retain trigger detection, recorder commands, id/status contracts, linked-worktree behavior, and the mandatory review pause; remove the long duplicated document example and route-level restatement.
- `plan-spec.md`: retain validated frontmatter rules, status transitions, required body/task contract, type-specific constraints, dependencies, and verification expectations; merge overlapping principles, traceability, independence, and anti-pattern guidance.

**Verification:**
- `rg -n "Workspace Safety|draft -> approved|Never implement|low risk|standard risk|high risk|record_human_request|proposed|accepted|branch-qualified|Frontmatter|depends_on|Change Map|Reproduction|Root Cause|generate_plans_readme" skills/using-superplan/references`
- `git diff --check -- skills/using-superplan/references`

- [x] Preserve each behavior-affecting workflow gate and make `delivery-loop.md` the only complete cross-route lifecycle policy.
- [x] Reduce `intake-spec.md` to the executable capture contract while keeping the human confirmation pause and stable id lifecycle unambiguous.
- [x] Collapse repeated plan-writing explanations while preserving every generator-enforced field, state, dependency, route-type, and verification requirement.
- [x] Review the three references together and remove contradictions or duplicated authority.

## Task 2: Reduce bundled skills to entry and specialization guidance

**Outcome:** Each skill triggers correctly and contains only the commands, routing information, and safeguards unique to its role.
**Files:**
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/project-bootstrap-from-prd/SKILL.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`
- Verify: `skills/using-superplan/agents/openai.yaml`
- Verify: `skills/project-bootstrap-from-prd/agents/openai.yaml`
- Verify: `skills/feature-plan-and-delivery/agents/openai.yaml`
- Verify: `skills/bugfix-plan-and-delivery/agents/openai.yaml`

**Change Map:**
- `using-superplan/SKILL.md`: keep dependency checking, GPT-5.6 activation, initialization, canonical-reference loading, and route selection; replace copied lifecycle/global rules with direct ownership links.
- `project-bootstrap-from-prd/SKILL.md`: keep the PRD input/output/type mapping, guardrail bootstrap, and PRD-specific planning boundary only.
- `feature-plan-and-delivery/SKILL.md`: expand frontmatter triggering to new or recorded features, delegate capture details to `intake-spec.md`, and keep only feature-specific output and acceptance rules.
- `bugfix-plan-and-delivery/SKILL.md`: expand frontmatter triggering to new or recorded bugs, delegate capture details to `intake-spec.md`, and retain only debugging, reproduction, root-cause, and behavior-regression safeguards.
- `agents/openai.yaml`: confirm UI names, descriptions, and default prompts still match the shortened skills; do not rewrite already-accurate metadata.

**Verification:**
- `for skill in skills/*; do python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"; done`
- `rg -n "description:|delivery-loop|intake-spec|systematic-debugging|test-driven-development|init_workspace|check_superpowers" skills/*/SKILL.md`
- `git diff --check -- skills/*/SKILL.md skills/*/agents/openai.yaml`

- [x] Remove repeated overview, path-convention, intake, risk, delegation, plan-shape, and completion prose from route skills when a named canonical reference already owns it.
- [x] Keep enough direct instruction in the entry skill to install/check prerequisites, initialize safely, and select the correct route.
- [x] Correct feature and bugfix frontmatter descriptions so body-supported new-request intake can trigger reliably.
- [x] Validate all four skill folders and confirm their UI metadata remains accurate.

## Task 3: Prove semantic preservation and finish F007

**Outcome:** The shortened instruction set remains structurally valid, preserves existing workflow behavior, and is delivered with traceable progress and regression evidence.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Measure the final four skills plus four shared references against the 783-line baseline and require at least a 25% reduction while manually checking that distinct constraints were not merged into ambiguity.
- Review F001-F007 together so F007 consolidates the canonical-policy direction from F004, preserves F005 workspace safety, and leaves F006 installation/profile behavior intact.
- Run the full repository regression and structural checks after the final instruction state is assembled, then update progress metadata without rerunning unchanged tests.
- Commit only F007 changes with an F007-qualified message while preserving the unrelated `AGENTS.md` memory timestamp.

**Verification:**
- `wc -l skills/*/SKILL.md skills/using-superplan/references/*.md`
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`

- [x] Confirm the combined agent-facing instruction set is no more than 587 lines and inspect the diff for semantic rather than merely cosmetic reduction.
- [x] Run the full script suite once against the final skill/reference state and verify the managed guardrails remain synchronized.
- [x] Review the complete feature-plan set for independent boundaries, accurate historical relationships, and no reopened completed work.
- [x] After verification succeeds, mark F007 `complete`, mark its human entry `done`, regenerate the plan index, and create a dedicated `F007` commit without staging unrelated changes.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F006-gpt56-superpowers-profile-installation.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/intake-spec.md`
- `skills/using-superplan/references/plan-spec.md`
