---
name: project-bootstrap-from-prd
description: Use when first-time project development starts from docs/superplan/human/prd.md and needs clarified, reviewed, approved mainline plans before implementation
---

# Project Bootstrap from PRD

Read `../using-superplan/references/delivery-loop.md`, then apply:

- Input: `docs/superplan/human/prd.md`
- Output: ordered mainline plans under `docs/superplan/plans/`
- Plan type: `required`; use `future` only for explicitly deferred extensions

Keep the PRD as the source of intent. Resolve material ambiguity before planning;
plans translate the accepted intent rather than replace it.

If the managed workflow block is missing or stale, run:

`python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`

Follow `../using-superplan/references/plan-spec.md` for ids, ordering,
dependencies, content, and verification.
