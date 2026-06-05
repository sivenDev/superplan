
# Workflow Guardrails
1. Before starting any new task, inspect the current workspace and recent progress; when the task is done, create a separate commit for that task's changes.
2. At the start of every task, understand the current progress first; when the task is complete, update the progress accordingly. Plans live under `./docs/superplan/plans`.
3. Whenever a plan changes, review the entire related plan set until the plans are independent, the structure is clear, and dependencies are explicit.

# Development Rules
1. When implementing a code change, inspect the directly related code in the same area, and clean up directly related redundancy or bloat, but do not expand it into unrelated refactoring.
2. Correctness comes first; once correctness is ensured, performance must be considered, then balanced against memory usage.
3. Always choose the correct implementation. Do not avoid it just because the change is large; if key assumptions are unclear, clarify them before continuing.
