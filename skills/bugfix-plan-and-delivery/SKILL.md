---
name: bugfix-plan-and-delivery
description: Use for new or recorded bugs managed through docs/superplan/human/bugs.md that require intake when needed, root-cause analysis, reviewed bugfix plans, approval, and regression-safe delivery
---

# Bugfix Plan and Delivery

Read `../using-superplan/references/delivery-loop.md`, then apply:

- Input: `docs/superplan/human/bugs.md`
- Output: `docs/superplan/plans/bugs/`
- Plan type: `bugfix`

For an unrecorded bug, execute `../using-superplan/references/intake-spec.md` and
stop for review. Plan only an accepted entry; skip intake when it already exists.

Before proposing a fix, use `systematic-debugging` to confirm the symptom,
reproduction path, and root-cause area. Stay in debugging if the root cause cannot
yet be explained; use `brainstorming` only for material repair choices.

Plans include `Reproduction` and `Root Cause` per
`../using-superplan/references/plan-spec.md`. During execution, first capture a
failing behavior-level regression, then use `test-driven-development` to deliver
the smallest correct root-cause fix. Increase review and regression depth using
the shared risk profile.
