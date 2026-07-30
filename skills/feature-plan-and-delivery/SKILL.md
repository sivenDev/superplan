---
name: feature-plan-and-delivery
description: Use for new or recorded feature requests managed through docs/superplan/human/features.md that require intake when needed, reviewed feature plans, approval, and verified delivery
---

# Feature Plan and Delivery

Read `../using-superplan/references/delivery-loop.md`, then apply:

- Input: `docs/superplan/human/features.md`
- Output: `docs/superplan/plans/features/`
- Plan type: `feature`

For an unrecorded feature, execute the adaptive decision in
`../using-superplan/references/intake-spec.md`: stop when it records `proposed`,
or continue to planning when its direct-accept conditions record `accepted`.
Use the canonical summary/list/show commands to select existing state. Plan only
an accepted entry; skip intake when the request already exists.

Use a feature-specific subdirectory only when one request needs multiple
independently deliverable plans. Make user-visible acceptance explicit and name
shared infrastructure boundaries rather than hiding them inside feature prose.

Follow `../using-superplan/references/plan-spec.md` for ids, content,
dependencies, and verification.
