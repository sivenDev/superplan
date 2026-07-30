# Plan Document Spec

This is the canonical format for executable plans under
`docs/superplan/plans/**`; it does not apply to the generated plan index or human
input files.

## Placement and Identity

- Mainline plans use ordered filenames such as `01-*.md` under
  `docs/superplan/plans/`.
- Feature and bugfix plans live under `plans/features/` and `plans/bugs/`.
- Use a topic subdirectory before splitting one request into multiple plans.
- One plan owns one independently verifiable delivery boundary. Express real
  sequencing with `depends_on`; do not hide it in prose.

## Frontmatter

Every plan starts with:

```yaml
---
id: "01"
title: "Minimal Local Kernel"
type: "required"
status: "draft"
summary: "One sentence describing the delivered result."
source: "docs/superplan/human/prd.md"
created: "2026-05-29"
order: 1
depends_on: []
parent: ""
---
```

- `id`: Stable and unique. Mainline `required`/`future` ids match their numeric
  filename prefix. Feature/bugfix ids encode the matching human entry: `F001`,
  `B001`, branch-qualified `F001@feature-x`, or split forms such as `F001-01`
  and `F001@feature-x-01`.
- `title`: Specific human-readable title.
- `type`: `required`, `future`, `feature`, or `bugfix`.
- `status`: `draft`, `approved`, `in_progress`, `blocked`, `complete`,
  or `superseded`.
- `summary`: One sentence used by the generated index.
- `source`: Requirement source, normally under `docs/superplan/human/`.
- `created`: Stable `YYYY-MM-DD` creation date.
- `order`: Required for ordered mainline execution.
- `depends_on`: Existing plan ids only; the graph must be acyclic, and a
  `complete` plan cannot depend on an incomplete plan.
- `parent`: Topic parent when a feature or bugfix uses a subdirectory; otherwise
  empty.

Feature and bugfix ids must match an existing source entry in the corresponding
human file.

## Status Flow

Normal flow is:

`draft -> approved -> in_progress -> complete`

- Human approval is required to leave `draft`; never implement from `draft`.
- Persist `approved` when approved work is queued. When execution starts in the
  same continuation as approval, persist `in_progress` directly and regenerate
  the index once; the human approval event remains required even when its
  transient status is not separately written.
- Use `blocked` only while execution cannot proceed; return to `in_progress`
  when resolved and explain the blocker in the plan.
- Use `superseded` for a retained plan replaced by another plan and name the
  replacement.

## Required Body

```markdown
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

**Change Map:**
- `path/to/file`: boundary, symbol, or policy section that changes

**Verification:**
- `...`

- [ ] Result-oriented step ...

## References
- `...`
```

Body fields describe only current execution decisions:

- `Goal`: one-sentence project gain.
- `Scope`: exact delivery boundary and user-visible result where applicable.
- `Non-Goals`: explicit scope exclusions; required.
- `Architecture`: decisions affecting boundaries or implementation direction,
  not mechanical steps.
- `Baseline`: current facts required to execute the plan.
- `Exit Criteria`: observable completion conditions.
- `References`: only direct inputs to this plan.

## Task Contract

Each task must have a result-oriented title, `Outcome`, explicit `Files`, a
`Change Map`, executable `Verification`, and checkboxes. Name important symbols
or policy boundaries when file paths alone are insufficient.

- Split work by independently verifiable delivery boundaries, not equal size.
- Keep dependency order explicit.
- Test observable acceptance behavior; do not require a test per function.
- Apply the risk profile from `delivery-loop.md` to testing and verification.
- Omit implementation bodies, brainstorming transcripts, checkpoint history,
  unrelated lists, artificial microsteps, and repeated checks against unchanged
  implementation state.
- Let Git record the exact delivered diff; the plan records intended outcomes,
  boundaries, and evidence.

## Type Rules

- `required`: current mainline capability; set `order`, `created`, and executable
  sequencing.
- `future`: deferred extension; still define goal, non-goals, and exit criteria.
- `feature`: make user-visible acceptance explicit in Scope or Exit Criteria.
- `bugfix`: add `Reproduction` and `Root Cause` after Baseline, and name the
  behavior-level regression or verification proving the defect is fixed.

## Plan-Set Validation

When plans are added, removed, renamed, split, or structurally changed, first
run exhaustive global validation and inspect the complete compact catalog:

`python3 <using-superplan-root>/scripts/generate_plans_readme.py --catalog`

Use `--active`, `--status`, `--source-id`, and `--depends-on` filters plus
`--search <text>` or `--artifact <path>` candidate discovery. Searches include
completed and superseded plans unless explicitly filtered. Read the changed plan
and every discovered related plan in full; expand the closure when those plans
reveal further source, dependency, scope, or artifact relationships. Review that
closure for overlap, independence, clarity, and accurate dependencies.

Checkboxes, routine status/progress updates, and evidence notes require only
validation of the affected plan plus the generated index. Do not reopen the full
related set when delivery structure is unchanged.

After either class of plan change, run:

`python3 <using-superplan-root>/scripts/generate_plans_readme.py --write --check`
