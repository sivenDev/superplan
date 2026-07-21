# Verification Matrix

Use this matrix with the risk profile in `delivery-loop.md`. Select the union of
rows matching the changed artifacts, add project-required checks, and escalate
when uncertainty or impact warrants it. Focused checks support iteration; final
checks prove the stabilized implementation state once.

| Changed artifacts | Focused iteration | Final evidence |
| --- | --- | --- |
| Skill or reference metadata/instructions | Run `quick_validate.py` for each affected skill folder; inspect trigger boundaries and reference ownership against the changed behavior. | Re-run structural validation for affected skills after final edits. When shared references change cross-route behavior, validate all bundled route skills and execute the applicable scenarios from `tests/behavior/workflow.md`. |
| Bundled Python scripts | Run the directly related unittest module and a CLI help/smoke path when its public arguments change. | Run `python3 -m unittest discover -s tests/scripts` once after script behavior stabilizes. |
| Managed guardrail template | Run `sync_agents_guardrails.py --write`, inspect only the managed hunk, then run `--check`; run its focused tests if sync behavior changed. | Require a clean `--check` result and preserve unrelated `AGENTS.md` content. |
| Human entries, plans, or generated plan index only | Run `generate_plans_readme.py --write --check` and inspect the affected plan/source relationship. | Re-run the generator check after final metadata updates; unchanged code tests are not required. |
| Profile installer, dependency checks, or initialization | Use disposable state and skills roots; run focused installer/check/init tests and a no-write dry-run. Exercise rollback and idempotency when activation behavior changes. | Run the full script suite and verify the resolved profile target, manifest, backup/rollback, and no-write guarantees relevant to the change. Never mutate a live user profile as verification. |
| Metadata-only completion updates after verified implementation | Refresh the plan index and run diff/status checks. | Reuse still-current implementation evidence; do not rerun unchanged code or skill tests. |

Evidence becomes stale only for claims affected by later changes. Re-run the
matching row when relevant files change, external tools or the human alter the
tested state, branch/worktree context changes, or supporting environment facts
no longer match. Always finish with `git diff --check` and inspect `git status`
for unrelated changes before delivery.
