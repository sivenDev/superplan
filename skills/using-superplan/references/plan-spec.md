# Plan Document Spec

This reference defines the canonical plan format for repositories that use
`docs/superplan/plans/**` as the execution-plan workspace.

It applies to executable project plans, not to derived index files such as
`docs/superplan/plans/README.md`.

Bundled script paths are relative to the `skills/using-superplan/` directory.

## Scope

Applies to:

- `docs/superplan/plans/*.md`
- `docs/superplan/plans/features/**/*.md`
- `docs/superplan/plans/bugs/**/*.md`

Does not apply to:

- `docs/superplan/plans/README.md`
- human input docs such as `docs/superplan/human/*.md`
- one-off discussion notes

## Core Principles

- One plan serves one clear delivery boundary.
- Once approved, a plan must be directly executable.
- Plans should stay independent whenever possible; real dependencies must be explicit.
- Plan documents exist to guide execution, not to preserve historical logs.
- Keep only information that affects current decisions.

## File Naming

- Mainline plans at the root use ordered prefixes such as `01-*.md`, `02-*.md`
- Feature plans live under `docs/superplan/plans/features/`
- Bugfix plans live under `docs/superplan/plans/bugs/`
- If one feature or bug needs multiple plans, create a subdirectory first, then continue using ordered filenames inside it

## Frontmatter

Every plan must include frontmatter:

```md
---
id: "01"
title: "Minimal Local Kernel"
type: "required"
status: "complete"
summary: "One sentence describing what this plan delivers."
source: "docs/superplan/human/prd.md"
created: "2026-05-29"
order: 1
depends_on: []
parent: ""
---
```

Field rules:

- `id`
  Stable, unique plan identifier. The format depends on type:
  - `required`/`future` (PRD-derived): ordered numeric ids matching the filename prefix, e.g. `01`, `02`.
  - `feature`/`bugfix`: the id encodes its source human entry. Use `F001` / `B001` for a single plan, or `F001-01`, `F001-02` when one entry is split into several plans. The source entry is the leading `F<NNN>` / `B<NNN>` prefix; there is no separate `source_id` field. The prefix must match an existing entry in the matching human doc.
- `title`
  Human-readable plan title. Do not use empty labels such as "plan 1".
- `type`
  Allowed values:
  - `required`
  - `future`
  - `feature`
  - `bugfix`
- `status`
  Allowed values (exact; the index generator fails on unknown variants such as `completed`):
  - `draft`
  - `approved`
  - `in_progress`
  - `blocked`
  - `complete`
  - `superseded`
  See the status state machine below.
- `summary`
  One sentence for index display.
- `source`
  Requirement source file, typically under `docs/superplan/human/*.md`.
- `created`
  Creation date in `YYYY-MM-DD`. Required. Stable once set; do not rewrite on later edits.
- `order`
  Required when the plan participates in ordered execution. Mainline plans must set it. Used as a tiebreaker for execution order; real sequencing is expressed with `depends_on`.
- `depends_on`
  List of plan ids this plan truly depends on. Empty list when there is none. Referenced ids must exist, the graph must be acyclic, and a `complete` plan may not depend on a non-`complete` plan.
- `parent`
  Used only when a feature or bug plan belongs to a parent topic directory.

## Status State Machine

Normal flow:

```
draft -> approved -> in_progress -> complete
```

- `draft` — written but not yet approved by the human.
- `approved` — the human approved execution. This is the gate: do not move a plan to `in_progress` unless it was `approved` first.
- `in_progress` — actively being implemented.
- `complete` — delivered and verified.
- `blocked` — cannot proceed; record why in the plan body. Returns to `in_progress` once unblocked.
- `superseded` — replaced by another plan; kept for history. Reference the replacement.

The index generator validates allowed values and dependency-status consistency, but it cannot observe the human approval event. Treat the `draft -> approved` transition as a hard process gate.

## Required Body Structure

All project plans use one body template:

```md
# <Title> Plan

**Goal:** ...
**Scope:** ...
**Non-Goals:** ...
**Architecture:** ...
**Baseline:** ...
**Exit Criteria:** ...

## Task 1: <result-oriented title>

**Outcome:** ...
**Files:**
- Modify: `...`
- Create: `...`
- Test: `...`

**Verification:**
- `...`

- [ ] Step 1 ...
- [ ] Step 2 ...

## References
- `...`
```

## Section Rules

### Goal

One sentence describing what the project gains when this plan is complete.

### Scope

State the exact boundary owned by this plan. If one sentence cannot explain it,
the plan likely still needs splitting.

### Non-Goals

Mandatory section. It prevents scope growth by naming what this plan will not do.

### Architecture

Describe only the design decisions that affect boundaries, decomposition, or
implementation direction. Do not turn this section into step-by-step execution prose.

### Baseline

Describe the current facts that matter to this plan. Do not dump full history or
checkpoint logs.

### Exit Criteria

State completion criteria, not process. They should be verifiable.

### References

List only references that directly influence this plan.

## Task Rules

Each task must include:

- clear `Outcome`
- explicit `Files`
- executable `Verification`
- checkbox steps

Additional requirements:

- task titles describe results, not vague actions
- one task serves one delivery boundary
- if a task requires too much hidden context, split it further
- if a task cannot be independently verified, split it further

## Type-Specific Rules

### required

- For current mainline project capabilities
- Must set `order`
- Must be ready for sequential execution

### future

- For future extensions
- Can be slightly coarser than `required`
- Still must define `Goal`, `Non-Goals`, and `Exit Criteria`

### feature

Must make the user-visible result or acceptance explicit in `Scope` or `Exit Criteria`.

### bugfix

In addition to the common template, include:

- `**Reproduction:** ...`
- `**Root Cause:** ...`

Place them after `Baseline` and before `Exit Criteria`.

## Independence Rules

- If two plans share many files and the boundary is unclear, the split failed.
- If a plan cannot be executed directly after approval, it is not ready.
- When a real sequencing dependency exists, express it with `depends_on` instead of hiding it in prose.
- Split by delivery boundary, not by trying to equalize change size.

## Content to Avoid

Do not put these into plans:

- long checkpoint histories
- status matrices already covered by README
- implementation lists unrelated to the plan boundary
- brainstorming transcripts
- process-maintenance documents disguised as project plans

## Workflow Rules

- New or updated plans must follow this reference.
- After writing a plan, review the full related plan set for independence and clarity.
- After changing plan metadata, refresh the generated index:
  - `python3 ../scripts/generate_plans_readme.py --write`
  - `python3 ../scripts/generate_plans_readme.py --check`
