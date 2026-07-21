
# Workflow Guardrails
1. Before starting any new task, establish fresh workspace-safety evidence and inspect recent progress. Reuse that evidence only while the branch/worktree and relevant Git state remain unchanged. For Superplan-routed work, ask whether to use a new worktree before any mutation when meaningful Git changes risk overwrite, commit mixing, or conflicts; ignore insignificant noise. When the task is done, create a separate commit for that task's changes.
2. At the start of every task, understand the current progress first; when the task is complete, update the progress accordingly. Plans live under `./docs/superplan/plans`.
3. Review the entire related plan set when plans are added, removed, renamed, split, or structurally changed; use local plan/index validation for routine status, checkbox, and evidence updates.
4. For work routed through Superplan, the approved plan, delivery-loop risk profile, and artifact-aware verification matrix are the project-level authority for persisted artifacts, testing, verification, delegation, and task-level traceability. Reuse unaffected evidence instead of rerunning unchanged checks.

# Development Rules
1. When implementing a code change, inspect the directly related code in the same area, and clean up directly related redundancy or bloat, but do not expand it into unrelated refactoring.
2. Correctness comes first; once correctness is ensured, performance must be considered, then balanced against memory usage.
3. Always choose the correct implementation. Do not avoid it just because the change is large; if key assumptions are unclear, clarify them before continuing.
