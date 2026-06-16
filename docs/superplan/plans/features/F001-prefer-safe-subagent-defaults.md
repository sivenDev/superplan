---
id: "F001"
title: "Prefer Safe Subagent Defaults in Planning and Execution"
type: "feature"
status: "complete"
summary: "Update Superplan guidance to prefer subagent-assisted decomposition and independent execution only when it is safe and correctness remains the priority."
source: "docs/superplan/human/features.md"
created: "2026-06-16"
depends_on: []
parent: ""
---
# Prefer Safe Subagent Defaults in Planning and Execution Plan

**Goal:** Make Superplan prefer subagent-assisted plan decomposition and independent multi-subagent execution when that improves throughput without weakening correctness.
**Scope:** Update the shared Superplan workflow guidance and the PRD/feature/bugfix route skills so they recommend subagent use for clearly bounded independent work while keeping correctness and verification above efficiency.
**Non-Goals:** Do not change generated `AGENTS.md` guardrails, add script-level enforcement, or require subagents in environments that do not support them.
**Architecture:** Put the policy in the shared delivery loop first, then echo it in the entry skill and the three route skills so every Superplan path inherits the same preference without turning it into a hard environment constraint.
**Baseline:** The current workflow already depends on `subagent-driven-development`, but the Superplan docs do not explicitly tell planners to prefer subagent-assisted decomposition during plan creation or tell executors to fan out independent work to multiple subagents only when verification boundaries are clear.
**Exit Criteria:** The shared workflow docs and route skills all state that subagent use is preferred for clearly bounded independent work, explicitly note that it is optional, and explicitly state that correctness outranks efficiency.

## Task 1: Add shared subagent preference to core workflow guidance

**Outcome:** The shared workflow reference and entry skill describe when plan writing should use subagent-assisted decomposition and when execution should use multiple subagents, without promoting unsafe parallelism.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/SKILL.md`

**Verification:**
- `rg -n "subagent|correctness|efficiency" skills/using-superplan/references/delivery-loop.md skills/using-superplan/SKILL.md`

- [x] Review the current shared workflow wording around planning and execution handoffs.
- [x] Add plan-writing guidance that prefers subagent-assisted decomposition only when task boundaries are clear and independent.
- [x] Add execution guidance that prefers multiple subagents only for independent work with clear verification boundaries, and state that correctness is the tie-breaker over efficiency.
- [x] Mirror the shared guidance in the entry skill so routed sessions see the same default at the top level.
- [x] Run the verification command and confirm the wording is consistent between the reference and the entry skill.

## Task 2: Align route-specific skills with the shared rule

**Outcome:** The PRD bootstrap, feature delivery, and bugfix delivery skills all reinforce the shared subagent preference without weakening their existing planning, debugging, or review gates.
**Files:**
- Modify: `skills/project-bootstrap-from-prd/SKILL.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`

**Verification:**
- `rg -n "subagent|correctness|efficiency" skills/project-bootstrap-from-prd/SKILL.md skills/feature-plan-and-delivery/SKILL.md skills/bugfix-plan-and-delivery/SKILL.md`

- [x] Review the current route-specific guidance for where planning and execution preferences belong.
- [x] Add PRD planning guidance that prefers subagent-assisted decomposition for clearly independent slices while keeping sequencing explicit.
- [x] Add feature guidance that prefers subagent-assisted planning and multi-subagent execution for independent slices without making it mandatory.
- [x] Add bugfix guidance that allows subagent use only after debugging has established the reproduction and root-cause boundaries clearly enough to preserve correctness.
- [x] Run the verification command and confirm the route skills are consistent with the shared workflow wording.

## References
- `docs/superplan/human/features.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/project-bootstrap-from-prd/SKILL.md`
- `skills/feature-plan-and-delivery/SKILL.md`
- `skills/bugfix-plan-and-delivery/SKILL.md`
