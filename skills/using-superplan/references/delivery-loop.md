# Delivery Loop

This reference is the single source of truth for the shared workflow used by all
Superplan skills (`$using-superplan`, `$project-bootstrap-from-prd`,
`$feature-plan-and-delivery`, `$bugfix-plan-and-delivery`).

Each specialized skill provides only its own settings (input doc, output
directory, plan type, and any extra steps) and otherwise follows this loop.

## Execution Model

All bundled script paths in this workflow are relative to the installed
`skills/using-superplan/` directory that contains this skill's `SKILL.md`,
`scripts/`, and `references/`.

Every script still detects the target repository root by walking up from the
**current working directory** (not from the script's own install location). If
the current directory is not inside the target repository, the script fails with
a clear error instead of writing elsewhere. Pass `--root <path>` to override
detection and point at a specific repository explicitly.

## Delivery Loop (9 steps)

1. Check `git status` and read current progress in `docs/superplan/plans`. Identify the exact request to work on.
2. Read the skill's input document under `docs/superplan/human/`. Respect any local bookkeeping rules in that file.
3. Refine the request with `brainstorming` until scope, constraints, acceptance criteria, and non-goals are explicit enough to plan. Run any extra discovery the skill requires (for example, `systematic-debugging` for bugs) before proposing a fix.
4. Read `plan-spec.md` before creating or revising any plan.
5. Use `writing-plans` to create plans in the skill's output directory. Set `created` (today's date). For feature/bugfix plans, the plan `id` encodes the source human entry (`F001` / `B001`, or `F001-01`, `F001-02` when split). Express real sequencing with `depends_on`. Split by independently deliverable slices, not by arbitrary size; if one request needs multiple plans, create a subdirectory first. New plans start at `status: draft`.
6. Review the full related plan set. Remove overlap, clarify boundaries, and make real dependencies explicit until each plan can stand on its own.
7. Present the plan set to the human and ask for approval. Stop here. Do not implement before approval. Approval is the `draft -> approved` gate: move a plan to `approved` only after the human explicitly approves it.
8. After approval, set the plan to `in_progress` and execute in order. Use `test-driven-development` for behavior changes, implement the minimal correct change, clean directly-related redundant code without widening scope, and confirm results with `verification-before-completion`. Mark `complete` only when its dependencies are already `complete`.
9. Update the input document per its local completion rules, update `docs/superplan/plans` progress, regenerate the index, and create a task-level commit covering only your own path set.

## Global Rules

- Never implement before a reviewed plan exists and the human explicitly approves execution.
- If requirements are unclear, stay in `brainstorming` before writing plans.
- Every plan file under `docs/superplan/plans/**` must follow `plan-spec.md`. Frontmatter must satisfy the README index generator, and the body must follow the required section layout.
- Plan status follows the `draft -> approved -> in_progress -> complete` state machine in `plan-spec.md`; `approved` is the human gate before any implementation.
- Feature and bugfix plan ids encode their source human entry (e.g. `F001` or `F001-01`); the index derives the source from the id and verifies it exists, so each plan traces back to a real entry.
- Plans must stay independent, clear, and non-overlapping; review the full related plan set after any change.
- The canonical project-level workflow guardrails live in `agents-guardrails.md`.
  - Install or refresh them with `python3 ../scripts/sync_agents_guardrails.py --write`.
  - Before claiming guardrails are current, run `python3 ../scripts/sync_agents_guardrails.py --check`.
- `docs/superplan/plans/README.md` is a generated index.
  - After any plan add, remove, rename, or metadata change, run `python3 ../scripts/generate_plans_readme.py --write`.
  - Before claiming plan work is up to date, run `python3 ../scripts/generate_plans_readme.py --check`.
- Use `test-driven-development` for behavior changes and `systematic-debugging` before any bug fix.
- Clean related redundant code while touching the area, but do not widen scope beyond what serves the approved plan.
- Before claiming completion, use `verification-before-completion`.
