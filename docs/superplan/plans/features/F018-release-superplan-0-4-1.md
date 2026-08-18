---
id: "F018"
title: "Release Superplan 0.4.1"
type: "feature"
status: "complete"
summary: "Publish exact Superplan 0.4.1 metadata across current plugin, runtime, workspace, documentation, and validation surfaces."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F017", "B004"]
parent: ""
---
# Release Superplan 0.4.1 Plan

**Goal:** Publish one consistent `0.4.1` release identity after F017 and B004 without changing runtime behavior or workspace compatibility.
**Scope:** Replace the Codex cachebuster version with exact `0.4.1` and synchronize the canonical runtime version, Claude manifest, marketplace entry, managed workspace marker, README example, and package-contract assertion. Users and tooling should observe `0.4.1` on every current release surface.
**Non-Goals:** Do not change workspace schema `1`, rewrite historical human entries or completed plan evidence, add another cachebuster, modify feature behavior, or broaden package discovery.
**Architecture:** Keep `SUPERPLAN_VERSION` as the runtime source used by workspace generation. Synchronize all package manifests and the explicit test expectation to the same release, use the existing guardrail synchronizer for the managed `AGENTS.md` marker, and update only the current README example; retain B004's support for optional future Codex build metadata.
**Baseline:** Current release surfaces report canonical `0.4.0`; the Codex manifest alone reports `0.4.0+codex.20260804101449`. Workspace schema remains `1`, and exact `0.4.0` text inside completed requests and plans is historical evidence rather than an active version surface.
**Exit Criteria:** `.codex-plugin/plugin.json`, both Claude package entries, `SUPERPLAN_VERSION`, the managed workspace marker, README example, and the package test report `0.4.1`; workspace schema stays `1`; active-surface searches find no stale `0.4.0`; focused package checks and the authoritative repository verifier pass.

## Task 1: Synchronize current release surfaces

**Outcome:** Every active package, runtime, generated-workspace, documentation, and validation surface identifies the release as exact `0.4.1`.
**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `AGENTS.md` (managed generator-version marker only)
- Modify: `README.md` (current workspace-marker example only)

**Change Map:**
- Version sources and manifests: replace the current canonical/cachebuster values with exact `0.4.1` while preserving workspace schema and all non-version metadata.
- Managed workspace marker: regenerate only the Superplan-managed `AGENTS.md` block after the canonical version changes.
- Documentation and contract: update the current README marker example and the explicit package-test release assertion; preserve historical `0.4.0` evidence under `docs/superplan/human/` and completed plans.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check --root .`
- Search current release surfaces for `0.4.0` and confirm only historical request/plan evidence remains.
- `git diff --check -- .codex-plugin .claude-plugin skills/using-superplan/scripts/superplan_version.py tests/scripts/test_plugin_package.py AGENTS.md README.md`

- [x] Set the Codex, Claude, marketplace, and runtime versions to exact `0.4.1`.
- [x] Refresh only the managed workspace marker and current README example.
- [x] Keep schema `1`, B004's optional-build validation, and non-version package content unchanged.
- [x] Preserve historical version evidence rather than mechanically rewriting completed records.

## Task 2: Verify and deliver F018 independently

**Outcome:** The `0.4.1` release metadata is repository-valid, progress-complete, and recorded in a dedicated F018 commit.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F018-release-superplan-0-4-1.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Run focused checks while version surfaces stabilize and `python3 tools/verify_repo.py` once against the final implementation state.
- Complete the plan, mark F018 done, refresh the generated plan index, and stage only F018 release and progress artifacts.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Obtain current focused, version-search, workspace, and full repository evidence.
- [x] Complete the plan, mark F018 done, and refresh the plan index without rerunning unchanged checks.
- [x] Create a dedicated commit whose message includes `F018` and contains only this release's changes.

## Implementation Evidence

- Version synchronization: the Codex manifest cachebuster, Claude manifest, marketplace entry, `SUPERPLAN_VERSION`, package assertion, managed `AGENTS.md` marker, and README example now report exact `0.4.1`; workspace schema remains `1`.
- Scope control: an active-surface search found only `0.4.1`. Historical `0.4.0` text remains unchanged in completed request and plan evidence, and B004's optional SemVer build-metadata validation remains intact.
- Verification: all six focused package-contract tests passed; guardrail synchronization and workspace compatibility checks passed; `python3 tools/verify_repo.py` passed 94 tests plus compilation, registry, guardrail, plan-index, and diff checks.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `docs/superplan/plans/features/F017-standardize-project-local-worktree-location.md`
- `docs/superplan/plans/bugs/B004-accept-codex-cachebuster-build-metadata.md`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `skills/using-superplan/scripts/superplan_version.py`
- `tests/scripts/test_plugin_package.py`
- `AGENTS.md`
- `README.md`
