---
name: using-superplan
description: Use to initialize, check, or migrate a Superplan workspace, or as the explicitly invoked fallback dispatcher for an otherwise unclassified Superplan request
---

# Using Superplan

Read `references/delivery-loop.md` before routed work. It is the shared
lifecycle authority.

`<using-superplan-root>` means this skill's installed directory.

## Workspace Entry

Run `python3 <using-superplan-root>/scripts/init_workspace.py` to initialize a
workspace. Add `--check` to inspect compatibility without writes, or `--migrate`
after Workspace Safety when the check reports an older or missing schema. Stop
on a newer or malformed schema.

Initialization is offline and workspace-only. Use `--root <path>` for an
explicit target.

## Fallback Routing

When the human explicitly invokes `$using-superplan`, or asks to use Superplan
without identifying a request type, apply the delivery loop and dispatch to:

- PRD-based first project development: `$project-bootstrap-from-prd`
- New or recorded feature: `$feature-plan-and-delivery`
- New, diagnosed, or recorded bug: `$bugfix-plan-and-delivery`

Natural-language requests for those types should select the specialized skill
directly; they do not need this entry skill first.
