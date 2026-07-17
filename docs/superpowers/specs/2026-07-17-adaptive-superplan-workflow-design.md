# Adaptive Superplan Workflow Design

**Feature:** F004 — Optimize Superplan for high-capability models
**Date:** 2026-07-17
**Source:** `docs/superplan/human/features.md`

## Goal

Reduce planning, testing, verification, and delegation overhead for small and
medium work while preserving the approval, root-cause, traceability, and final
evidence guarantees that make Superplan reliable.

## Chosen Approach

Use one cohesive guidance layer across Superplan. Update the shared delivery
loop, plan format, entry and route skills, injected guardrails, and human-facing
README guidance without adding plan schema fields, risk classifiers, or new
verification scripts.

This is preferred over:

- a minimal core-doc patch, which would leave route skills and injected
  guardrails inconsistent;
- an automation-heavy design, which would add the schema, tests, and maintenance
  burden that this feature is intended to reduce.

## Superpowers Composition

Superplan owns the persisted request, design, and execution artifacts for work
routed through `docs/superplan/**`.

- Use brainstorming to resolve material ambiguity, not to repeat requirements
  that are already explicit.
- The approved Superplan plan is the persisted design and implementation guide.
  Do not create parallel `docs/superpowers/specs` or `docs/superpowers/plans`
  artifacts unless the human explicitly requests them.
- Adapt `writing-plans` to the Superplan plan format. Its planning discipline is
  useful, but its default code-heavy template and 2–5 minute microsteps are not
  required in a Superplan plan.

This document is a one-time transition artifact produced under the pre-F004
workflow. Future Superplan work should use the approved plan as the sole
persisted design artifact.

## Risk-Proportional Workflow

Risk profiles are guidance, not frontmatter fields and not generator-enforced
schema.

### Low risk

Examples include documentation, configuration, templates, and isolated
mechanical changes with no meaningful runtime behavior impact.

- Do not require new unit tests by default.
- Use the smallest relevant validator, structural check, smoke check, or
  existing focused test.
- Use a single capable agent unless the change contains genuinely independent
  workstreams.

### Standard risk

Examples include normal local behavior changes and features with bounded impact.

- Test observable acceptance behavior rather than every new function or method.
- Run focused verification while iterating.
- Run the relevant full regression command once after the implementation state
  is final.
- Default to a single capable agent; use subagents only for multiple independent
  slices with explicit ownership and verification boundaries.

### High risk

Examples include security, concurrency, migrations, data integrity, public API
compatibility, and complex defects.

- Keep strict test-first development where applicable.
- Use systematic root-cause investigation for defects.
- Run focused and full regression checks.
- Add independent review or subagents when separation improves evidence quality.

## Plan Granularity

Plans continue to require Goal, Scope, Non-Goals, Architecture, Baseline, Exit
Criteria, result-oriented tasks, explicit files, and executable verification.

Plans no longer need to embed complete implementation or test code, repeat the
same verification command in several steps, or split test writing and production
implementation into separate delivery tasks.

Each task instead carries a change map:

- the outcome the task delivers;
- exact file paths;
- important symbols, boundaries, or policy sections when they matter;
- behavior-level steps;
- the focused and final evidence required for completion.

## Traceability

Traceability is layered instead of duplicating code inside plans:

- the human entry records why the change exists;
- the plan records intended boundaries, decisions, files, and verification;
- tests and validators record executable behavior evidence;
- Git records the actual implementation through diffs, history, and blame.

Task-level commits should include the plan id, for example
`feat(F004): apply adaptive verification policy`, so future agents can locate the
implementation with `git log --grep F004` and inspect it with `git show`.

## Verification Deduplication

- Run focused checks during implementation and one relevant full regression
  after the code state is final.
- Do not rerun an unchanged verification command when only plan status or
  generated index files changed afterward.
- After plan metadata changes, use the combined plan-index command
  `generate_plans_readme.py --write --check`.
- Fresh evidence is still required before a completion claim; deduplication does
  not permit claims based on stale or unrelated output.

## Preserved Guarantees

F004 does not remove:

- the `draft -> approved` human execution gate;
- explicit scope and non-goals;
- bug reproduction and root-cause analysis;
- regression coverage for fixed observable defects;
- final verification evidence;
- independent, task-level commits.

## Expected File Scope

- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/plan-spec.md`
- `skills/using-superplan/references/agents-guardrails.md`
- `skills/project-bootstrap-from-prd/SKILL.md`
- `skills/feature-plan-and-delivery/SKILL.md`
- `skills/bugfix-plan-and-delivery/SKILL.md`
- `README.md`
- synchronized managed block in `AGENTS.md`

No script behavior or plan metadata schema should change.

## Verification Strategy

- Review all Superplan skills and related references for conflicting or repeated
  instructions.
- Run `sync_agents_guardrails.py --write` followed by `--check`, and confirm
  non-managed `AGENTS.md` content is preserved.
- Run `generate_plans_readme.py --write --check` after F004 plan metadata changes.
- Run the existing script unit suite once after the final repository state is
  assembled.
- Do not add tests solely to assert documentation wording unless existing tests
  expose a concrete generated-template contract that changed.
