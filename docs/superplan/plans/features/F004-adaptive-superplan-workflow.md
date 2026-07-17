---
id: "F004"
title: "Adaptive Superplan Workflow for High-Capability Models"
type: "feature"
status: "draft"
summary: "Make Superplan planning, testing, verification, and delegation proportional to task risk while preserving approval and traceability guarantees."
source: "docs/superplan/human/features.md"
created: "2026-07-17"
depends_on: []
parent: ""
---
# Adaptive Superplan Workflow for High-Capability Models Plan

**Goal:** Reduce low-value planning, testing, verification, and delegation overhead while preserving Superplan's human approval, root-cause, traceability, and final evidence guarantees.
**Scope:** Update the Superplan guidance layer so planning and execution use low, standard, and high risk profiles; plans retain a file/symbol-level change map without embedded implementation code; small and medium tasks default to one capable agent; and verification is focused during iteration with one relevant final regression run.
**Non-Goals:** Do not add plan frontmatter fields, modify generator schema, add risk-classification or verification scripts, remove the human approval gate, weaken bug root-cause requirements, or eliminate regression evidence for observable defects.
**Architecture:** Keep `delivery-loop.md` as the canonical adaptive policy, express plan-document consequences in `plan-spec.md`, inject a concise project-level precedence rule through `agents-guardrails.md`, and align the entry and route skills without duplicating the full policy. Git commits carrying the plan id provide the implementation trace, while the plan records intent, boundaries, and verification.
**Baseline:** The current workflow always routes creative work through full brainstorming and code-heavy `writing-plans`, prefers subagents for safely separable work, applies strict TDD to all behavior changes, and repeats focused plus full verification across task and completion boundaries. F001 established the current subagent preference; F004 intentionally replaces that default for small and medium work without removing subagents for independent or high-risk work.
**Exit Criteria:** All Superplan entry, route, reference, and injected guardrail guidance consistently describes risk-proportional planning and verification; plans require traceable change maps but not embedded code or microsteps; small and medium work defaults to a single agent; bug reproduction and final evidence remain explicit; the managed `AGENTS.md` block is synchronized without absorbing unrelated edits; and the existing script test suite and plan-index checks pass.

## Task 1: Establish the canonical adaptive workflow policy

**Outcome:** The shared Superplan policy and plan format define one consistent risk-proportional workflow with explicit traceability and verification boundaries.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Modify: `skills/using-superplan/references/agents-guardrails.md`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `README.md`

**Change Map:**
- `delivery-loop.md`: define Superpowers composition, low/standard/high risk profiles, single-agent defaults, behavior-level testing, and verification deduplication.
- `plan-spec.md`: require outcome-oriented change maps, exact files and important symbols, executable verification, and plan-id commit traceability without embedded implementation code or 2–5 minute microsteps.
- `agents-guardrails.md`: give downstream repositories concise project-level rules that take precedence over generic process defaults.
- `using-superplan/SKILL.md` and `README.md`: summarize the adaptive policy and point to the canonical references without repeating their full contents.

**Verification:**
- `rg -n "risk|low|standard|high|behavior|single agent|subagent|change map|plan id|write --check" skills/using-superplan/SKILL.md skills/using-superplan/references README.md`
- `git diff --check -- README.md skills/using-superplan/SKILL.md skills/using-superplan/references`

- [ ] Replace unconditional full brainstorming and generic code-heavy planning with a Superplan composition rule that escalates only material ambiguity and keeps the approved Superplan plan as the sole persisted design artifact.
- [ ] Define low, standard, and high risk guidance, including the required testing, verification, and review depth for each profile.
- [ ] Make focused iteration plus one relevant final regression run the default, while preserving fresh completion evidence and stricter high-risk checks.
- [ ] Define layered traceability through human entry, plan change map, executable evidence, and commits carrying the plan id.
- [ ] Update the injected guardrails, entry skill, and README summary so downstream agents receive the same policy with no new schema or automation.

## Task 2: Align project, feature, and bugfix routes

**Outcome:** Every routed workflow specializes the canonical policy without reintroducing unconditional subagents, function-level testing, or duplicate verification.
**Files:**
- Modify: `skills/project-bootstrap-from-prd/SKILL.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`

**Change Map:**
- `project-bootstrap-from-prd`: select verification depth per independently deliverable slice and reserve subagents for genuinely independent work or valuable review.
- `feature-plan-and-delivery`: test observable acceptance behavior and default bounded feature work to one capable agent.
- `bugfix-plan-and-delivery`: retain systematic root-cause analysis and a failing behavior-level regression test, while reserving broader strict TDD and review expansion for higher-risk fixes.

**Verification:**
- `rg -n "risk|behavior|regression|single agent|subagent|root cause|verification" skills/project-bootstrap-from-prd/SKILL.md skills/feature-plan-and-delivery/SKILL.md skills/bugfix-plan-and-delivery/SKILL.md`
- `git diff --check -- skills/project-bootstrap-from-prd/SKILL.md skills/feature-plan-and-delivery/SKILL.md skills/bugfix-plan-and-delivery/SKILL.md`

- [ ] Remove route wording that makes subagent-assisted planning or execution the default for small and medium work.
- [ ] Align feature verification with observable acceptance boundaries instead of per-function test requirements.
- [ ] Preserve bug reproduction, root-cause explanation, and a regression test that proves the defect while making additional verification proportional to risk.
- [ ] Review the entry skill, shared references, and all three route skills together and remove contradictory or repeated instructions.

## Task 3: Synchronize guardrails, verify the repository, and finish F004

**Outcome:** The repository and generated workflow artifacts reflect the approved policy, all existing behavior checks pass, and F004 is traceable through a dedicated implementation commit.
**Files:**
- Modify: `AGENTS.md` (managed guardrails block only)
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Synchronize only the managed guardrails block and preserve the existing unrelated memory-context modification in `AGENTS.md` without staging it.
- Review F001–F004 as the related feature-plan set and confirm F004 deliberately revises, rather than accidentally duplicates, the earlier subagent policy.
- Run one final script regression suite after the skill/reference state is assembled, then update F004 progress and regenerate the plan index without rerunning unchanged code tests.
- Commit the implementation with an `F004`-qualified message so `git log --grep F004` locates the delivered policy.

**Verification:**
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`

- [ ] Synchronize the managed `AGENTS.md` block, inspect the diff, and ensure the pre-existing non-managed modification remains unstaged.
- [ ] Review the full feature plan set for independence, intentional policy replacement, and explicit boundaries.
- [ ] Run the full existing script suite once after all skill and reference edits are final.
- [ ] After verification succeeds, mark this plan `complete`, mark F004 `done`, and regenerate the plan index with the combined command.
- [ ] Create a task-level implementation commit containing only F004 paths and the managed `AGENTS.md` hunk, using an `F004`-qualified commit message.

## References
- `docs/superplan/human/features.md`
- `docs/superpowers/specs/2026-07-17-adaptive-superplan-workflow-design.md`
- `docs/superplan/plans/features/F001-prefer-safe-subagent-defaults.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/plan-spec.md`
- `skills/using-superplan/references/agents-guardrails.md`
