---
name: project-bootstrap-from-prd
description: Use when first-time project development starts from docs/superplan/human/prd.md and the work must be clarified, split into progressive plans, reviewed, approved, and only then implemented
---

# Project Bootstrap from PRD

## Overview

Turn a rough `docs/superplan/human/prd.md` into a clear, approved execution path. This skill owns the first-project flow from requirement clarification through reviewed plans and gated implementation.

Bundled script paths are resolved relative to this skill directory.

## Specialization

This skill specializes the shared delivery loop. Read `../using-superplan/references/delivery-loop.md` first, then apply these settings:

- Input: `docs/superplan/human/prd.md`
- Output: `docs/superplan/plans/` (mainline plans with ordered prefixes such as `01-*.md`, `02-*.md`)
- Plan type: `required` (use `future` for clearly deferred extensions)
- Extra steps:
  - Before planning, read `../using-superplan/references/agents-guardrails.md`. If `AGENTS.md` is missing the managed workflow guardrails, run `python3 ../using-superplan/scripts/sync_agents_guardrails.py --write`.
  - The PRD stays as the source of intent. If scope, constraints, acceptance criteria, or non-goals are unclear, keep refining `prd.md` with `brainstorming` until it is explicit enough to plan.

## Type-Specific Rules

- The PRD stays as the source of intent. Plans translate it into executable steps; they do not replace it.
- First-project setup should install the canonical workflow guardrails into `AGENTS.md` unless the repository already has an explicitly stronger policy.
- Each plan must have a single clear goal, explicit files, verification steps, and a meaningful completion boundary.
- If a plan cannot be executed and verified independently, split it further.
- Mainline `required` plans use ordered numeric ids (`01`, `02`), must set `order` and `created`, and be ready for sequential execution. Express real ordering with `depends_on`.
