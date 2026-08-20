# Verification Matrix

Use this matrix with the risk profile in `delivery-loop.md`. Select the union of
rows matching changed artifacts and add project-required checks only when they
prove an additional claim.

- **Focused:** cheap feedback during implementation; repeat after relevant
  edits.
- **Final:** evidence for the stabilized implementation state. When selected,
  run `python3 tools/verify_repo.py` once for this repository. It already runs
  the full script suite, compilation, workspace/registry/guardrail/plan-index
  checks, and `git diff --check`; do not list or rerun those as separate final
  commands.
- **Metadata-only:** progress or catalog edits after implementation evidence is
  current. Validate only the affected state and ownership boundary.

| Changed artifacts | Focused iteration | Final or metadata-only evidence |
| --- | --- | --- |
| Skill metadata or instructions | Run `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`; validate changed skills and inspect trigger/reference ownership. | For cross-route or packaged behavior, run the authoritative repository command once. A later plan-status update needs only plan-index and ownership checks. |
| Shared workflow references | Inspect all affected route skills and execute applicable fresh-context scenarios from `tests/behavior/workflow.md`. | Run the authoritative repository command once when repository behavior changed; do not separately repeat its package or script checks. |
| Bundled Python scripts | Run the directly related unittest module and a CLI help/smoke path when public arguments change. | Run the authoritative repository command once after behavior stabilizes. |
| Plugin manifests or packaged skill inventory | Run the focused package-contract test and inspect the discovered root skill set. | Run the authoritative repository command once; it owns the full suite and package validation. |
| Managed guardrail template | Run `sync_agents_guardrails.py --write`, inspect only the managed hunk, then run `--check`; add focused tests if behavior changed. | Use the authoritative repository command for stabilized behavior. Preserve unrelated `AGENTS.md` content. |
| Workspace initialization or migration | Use disposable workspaces and run focused init/sync tests plus the no-write compatibility check. | Run the authoritative repository command once when generated behavior changed. |
| RFC document or RFC-backed feature plan | Validate the registry and plan catalog; inspect RFC identity, layout, status/version, required sections, language, and direct plan references. | Require all matching RFCs to be approved before plan creation or completion, then refresh/check the plan index. No code regression is needed for metadata-only wording changes. |
| Human entries, plans, or generated plan index only | Run `generate_plans_readme.py --write --check` and inspect the affected source/plan relationship. | Reuse current implementation evidence; rerun the generator and ownership checks only. |
| Metadata-only completion updates | Refresh the plan index and inspect registry, diff, and status ownership. | Do not rerun unchanged implementation, code, or skill regression. |

Evidence becomes stale only for claims affected by later changes. Re-run the
matching focused check after relevant edits; re-run final evidence only if the
stabilized implementation it proved changes. `git status` may be repeated at
commit boundaries because it checks ownership rather than implementation
behavior.
