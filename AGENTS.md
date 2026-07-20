<!-- managed-by: superplan:start -->
# Workflow Guardrails
1. Before starting any new task, inspect the current workspace and recent progress. For Superplan-routed work, ask whether to use a new worktree before any mutation when meaningful Git changes risk overwrite, commit mixing, or conflicts; ignore insignificant noise. When the task is done, create a separate commit for that task's changes.
2. At the start of every task, understand the current progress first; when the task is complete, update the progress accordingly. Plans live under `./docs/superplan/plans`.
3. Whenever a plan changes, review the entire related plan set until the plans are independent, the structure is clear, and dependencies are explicit.
4. For work routed through Superplan, the approved plan and the Superplan delivery-loop risk profile are the project-level authority for persisted artifacts, testing, verification, delegation, and task-level traceability.

# Development Rules
1. When implementing a code change, inspect the directly related code in the same area, and clean up directly related redundancy or bloat, but do not expand it into unrelated refactoring.
2. Correctness comes first; once correctness is ensured, performance must be considered, then balanced against memory usage.
3. Always choose the correct implementation. Do not avoid it just because the change is large; if key assumptions are unclear, clarify them before continuing.
<!-- managed-by: superplan:end -->

# Superplan Repository

- This repository packages `superplan` as a Codex/Claude-compatible plugin bundle with skills under `skills/`.
- `skills/using-superplan` is the main entry skill. The other bundled skills are required companions and should ship together.
- Superplan depends on `superpowers`. Keep the dependency explicit in docs and scripts; do not vendor Superpowers skills into this repository.
- In skill and reference docs, use the placeholder `<using-superplan-root>` for bundled script paths instead of hard-coding local install paths.
- Validate script behavior with `python3 -m unittest discover -s skills/using-superplan/scripts/tests`.


<claude-mem-context>
# Memory Context

# [superplan] recent context, 2026-07-01 7:53pm GMT+8

No previous sessions found.
</claude-mem-context>
