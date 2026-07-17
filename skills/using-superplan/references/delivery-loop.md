# Delivery Loop

This reference is the single source of truth for the shared workflow used by all
Superplan skills (`$using-superplan`, `$project-bootstrap-from-prd`,
`$feature-plan-and-delivery`, `$bugfix-plan-and-delivery`).

Each specialized skill provides only its input document, output directory, plan
type, and route-specific safeguards.

## Execution Model

Bundled script paths use the `<using-superplan-root>` placeholder for the
installed `skills/using-superplan/` directory.

Every script detects the target repository root by walking up from the current
working directory. If the current directory is not inside the target repository,
the script fails instead of writing elsewhere. Pass `--root <path>` to target a
repository explicitly.

## Superpowers Composition

For work routed through `docs/superplan/**`, Superplan owns the persisted request,
design, execution plan, and progress artifacts.

- Use `brainstorming` only when material ambiguity remains in scope,
  constraints, acceptance criteria, non-goals, or architecture. Do not repeat a
  full design cycle when the human input is already explicit enough to plan.
- Use the reasoning discipline from `writing-plans`, but write only the approved
  Superplan plan format from `plan-spec.md`. Do not create parallel
  `docs/superpowers/specs` or `docs/superpowers/plans` artifacts unless the human
  explicitly requests them.
- Project instructions and the selected Superplan risk profile determine the
  required testing, verification, and delegation depth when generic process
  defaults would add work without improving evidence.

## Risk Profiles

Risk profiles are planning guidance, not frontmatter fields and not
generator-enforced schema. When the correct profile is not obvious, explain the
choice in the plan's Architecture or Verification text. Prefer the more
conservative profile when uncertainty is material.

### Low risk

Use for documentation, configuration, templates, and isolated mechanical
changes with no meaningful runtime behavior impact.

- Do not require new unit tests by default.
- Use the smallest relevant validator, structural check, smoke check, or
  existing focused test.
- Use one capable agent unless the work contains genuinely independent slices.

### Standard risk

Use for bounded behavior changes and normal features with local, understood
impact.

- Test observable acceptance behavior rather than every new function or method.
- Run focused verification while iterating.
- Run the relevant full regression command once after the implementation state
  is final.
- Default to one capable agent. Use subagents only for multiple independent
  slices with explicit ownership and verification boundaries.

### High risk

Use for security, concurrency, migrations, data integrity, public API
compatibility, complex defects, or broad changes with uncertain impact.

- Keep strict test-first development where applicable.
- Use systematic root-cause investigation for defects.
- Run focused and full regression checks.
- Add independent review or subagents when separation improves evidence quality.

## Delivery Loop

1. Check `git status`, recent commits, and current progress in
   `docs/superplan/plans`. Identify the exact request and preserve unrelated work.
2. Read the route's input document under `docs/superplan/human/` and respect its
   bookkeeping rules.
3. Confirm scope, constraints, acceptance criteria, non-goals, and the risk
   profile. Invoke `brainstorming` only for material unresolved choices. Run
   route-specific discovery such as `systematic-debugging` before planning a bug
   fix.
4. Read `plan-spec.md`, then use `writing-plans` to create the route's Superplan
   plan. Plans use result-oriented tasks, a traceable change map, and executable
   verification without copying complete implementation code or mechanical
   2–5 minute steps. New plans start at `status: draft`.
5. Review the full related plan set. Remove overlap, clarify boundaries, and
   express real sequencing with `depends_on` until every plan can stand on its
   own.
6. Present the plan set to the human and stop for approval. Human approval is the
   `draft -> approved` gate; never implement before it.
7. After approval, move the plan through `approved -> in_progress` and execute in
   dependency order. Default small and medium work to one capable agent. Use
   `subagent-driven-development` only for genuinely independent slices or
   high-risk review where the extra boundary improves evidence.
8. During implementation, run focused checks appropriate to the selected risk
   profile. For defects, keep a behavior-level regression that proves the
   reproduced failure. Clean directly related redundancy without widening scope.
9. After the implementation state is final, run the relevant full regression and
   completion checks once. Then update the human input, plan status, and generated
   plan index with
   `python3 <using-superplan-root>/scripts/generate_plans_readme.py --write --check`.
   Do not rerun unchanged code tests solely because plan status or generated
   index files changed. Create a task-level commit whose message includes the plan
   id when one exists.

## Traceability

Traceability is layered rather than duplicated inside plans:

- the human entry records why the work exists;
- the plan records intended outcomes, boundaries, files, important symbols, and
  verification;
- tests and validators record executable evidence;
- Git records the actual implementation through diffs, history, and blame.

Task-level commit messages include the plan id, for example
`feat(F004): apply adaptive verification policy`, so future agents can use
`git log --grep F004` and `git show` to recover the delivered change.

## Global Rules

- Never implement before a reviewed plan exists and the human explicitly
  approves execution.
- Every executable plan under `docs/superplan/plans/**` follows `plan-spec.md`.
- Plans stay independent, clear, and non-overlapping; review the full related
  plan set after every plan change.
- Feature and bugfix plan ids encode their source human entry, including any
  branch qualifier and split suffix.
- The canonical project guardrails live in `agents-guardrails.md`. Install or
  refresh them with
  `python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`, then
  verify with the same command using `--check`.
- Before claiming completion, obtain fresh evidence for the final implementation
  state. Reuse that evidence after metadata-only progress updates when the tested
  code state has not changed.
