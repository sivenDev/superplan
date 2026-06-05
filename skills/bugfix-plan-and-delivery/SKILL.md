---
name: bugfix-plan-and-delivery
description: Use when a bug is recorded in docs/superplan/human/bugs.md and the fix must go through root-cause analysis, reviewed plans under docs/superplan/plans/bugs, approval, and regression-safe implementation
---

# Bugfix Plan and Delivery

## Overview

Take a reported bug from `docs/superplan/human/bugs.md` through root-cause analysis, repair planning, and approved execution. This skill is for bug work that must preserve review gates instead of jumping straight to code changes.

Bundled script paths are resolved relative to this skill directory.

## Intake

When the human reports a brand-new bug (for example "新建 bug", "bug: ...", "报个缺陷 ...") instead of pointing at an already-recorded entry, run intake first. Read `../using-superplan/references/intake-spec.md`, then:

1. Extract a short title (and optional reproduction/symptom notes) from the report.
2. Record it into `docs/superplan/human/bugs.md` with the next id and `status: proposed`:
   - `python3 ../using-superplan/scripts/record_human_request.py --type bug --title "<title>" [--body "<symptom / reproduction>"]`
3. Stop and ask the human to review the recorded entry. Do not start debugging or planning.
4. After the human confirms (entry becomes `status: accepted`), continue with the delivery loop below using that entry as the source.

If the human references an existing entry, skip intake and go straight to the delivery loop.

## Specialization

This skill specializes the shared delivery loop. Read `../using-superplan/references/delivery-loop.md` first, then apply these settings:

- Input: `docs/superplan/human/bugs.md`
- Output: `docs/superplan/plans/bugs/` (create a bug-specific subdirectory when the fix needs multiple independent plans)
- Plan type: `bugfix`
- Extra steps:
  - Run intake first when the report is a new bug (see Intake above).
  - Before proposing any fix, use `systematic-debugging` to confirm the symptom, reproduction path, and likely root-cause area. Then refine the bug with `brainstorming` until it is explicit enough to plan.
  - Each bugfix plan must include `Reproduction` and `Root Cause` (per `plan-spec.md`).
  - During execution, write the failing regression test first with `test-driven-development`, then implement the minimal fix for the root cause.

## Type-Specific Rules

- Bugfix plans belong in `docs/superplan/plans/bugs/`.
- Every bugfix plan id must encode its source entry: use `B001` for a single plan, or `B001-01`, `B001-02` when split. Set `created` to today's date.
- Every bugfix plan must name the reproduction or verification path that proves the bug existed and is now fixed.
- Prefer the smallest root-cause fix that keeps behavior correct and measurable.
- If the issue is not understood well enough to explain the root cause, stay in debugging and do not write implementation steps yet.
