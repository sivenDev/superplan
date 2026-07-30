---
name: bugfix-plan-and-delivery
description: Use for new or recorded bugs managed through docs/superplan/human/bugs.md that require intake when needed, root-cause analysis, reviewed bugfix plans, approval, and regression-safe delivery
---

# Bugfix Plan and Delivery

Read `../using-superplan/references/delivery-loop.md`, then apply:

- Input: `docs/superplan/human/bugs.md`
- Output: `docs/superplan/plans/bugs/`
- Plan type: `bugfix`

For an unrecorded bug, execute the adaptive decision in
`../using-superplan/references/intake-spec.md`: stop when it records `proposed`,
or continue to debugging and planning when its direct-accept conditions record
`accepted`. Use the canonical summary/list/show commands to select existing
state. Plan only an accepted entry; skip intake when it already exists.

Before proposing a fix, read [`references/debugging.md`](references/debugging.md)
to confirm the symptom, reproduction path, and root cause. Stay in diagnosis if
the cause cannot yet be explained; resolve only material repair choices before
planning.

Plans include `Reproduction` and `Root Cause` per
`../using-superplan/references/plan-spec.md`. During approved execution, capture
a focused failing behavior regression first when it is practical and reliable,
then deliver the smallest correct root-cause fix. Increase review and regression
depth using the shared risk profile.
