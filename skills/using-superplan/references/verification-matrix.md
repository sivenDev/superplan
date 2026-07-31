# Verification Matrix

Use this matrix with the risk profile in `delivery-loop.md`. Select the union of
rows matching the changed artifacts, add project-required checks, and escalate
when uncertainty or impact warrants it. Focused checks support iteration; final
checks prove the stabilized implementation state once.

| Changed artifacts | Focused iteration | Final evidence |
| --- | --- | --- |
| Skill or reference metadata/instructions | Run `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`; inspect trigger boundaries and reference ownership against the changed behavior. | Re-run the self-contained package contract after final edits. When shared references change cross-route behavior, inspect all four Superplan skills and execute the applicable scenarios from `tests/behavior/workflow.md`. |
| Bundled Python scripts | Run the directly related unittest module and a CLI help/smoke path when its public arguments change. | For this repository, run `python3 tools/verify_repo.py` once after script behavior stabilizes. |
| Plugin manifests or packaged skill inventory | Run the focused package-contract test and inspect the discovered root skill set. | Run the full script suite once, validate every shipped skill, and verify synchronized versions plus the absence of stale package paths. |
| Managed guardrail template | Run `sync_agents_guardrails.py --write`, inspect only the managed hunk, then run `--check`; run its focused tests if sync behavior changed. | Require a clean `--check` result and preserve unrelated `AGENTS.md` content. |
| Human entries, plans, or generated plan index only | Run `generate_plans_readme.py --write --check` and inspect the affected plan/source relationship. | Re-run the generator check after final metadata updates; unchanged code tests are not required. |
| Workspace initialization or migration | Use disposable workspaces; run focused init/sync tests and the no-write compatibility check. Exercise preservation and idempotency when generated behavior changes. | Run the full script suite and verify schema compatibility, managed-content preservation, idempotency, and no-write guarantees relevant to the change. |
| Metadata-only completion updates after verified implementation | Refresh the plan index and run diff/status checks. | Reuse still-current implementation evidence; do not rerun unchanged code or skill tests. |

Evidence becomes stale only for claims affected by later changes. Re-run the
matching row when relevant files change, external tools or the human alter the
tested state, branch/worktree context changes, or supporting environment facts
no longer match. Always finish with `git diff --check` and inspect `git status`
for unrelated changes before delivery.

Repository development and CI use `python3 tools/verify_repo.py` as the complete
contract; focused commands do not replace it.
