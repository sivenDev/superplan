---
id: "F021"
title: "Release Superplan 0.6.0 and Refresh Local Codex Installation"
type: "feature"
status: "complete"
summary: "Publish Superplan 0.6.0 to GitHub and reinstall the local Codex plugin from the existing development marketplace."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F020"]
parent: ""
---
# Release Superplan 0.6.0 and Refresh Local Codex Installation Plan

**Goal:** Publish the F020 checkpoint workflow as a consistent Superplan `0.6.0` release and make the existing local Codex installation load that release.
**Scope:** Synchronize every active release surface and package assertion to exact base version `0.6.0`, keep workspace schema `1`, regenerate the managed workspace marker, verify and commit the release, confirm the GitHub `main` head has not moved from the preflight commit, push local `main`, and reinstall `superplan@superplan-dev` through the plugin-creator cachebuster flow. Use the cachebuster only for local installation, restore the repository Codex manifest to exact `0.6.0`, verify the installed cache contains F020 guidance, and finish with a clean worktree.
**Non-Goals:** Do not change workspace schema; add feature behavior beyond F020; rewrite historical version evidence; create or edit marketplace configuration; use the missing personal marketplace; publish a cachebuster suffix as the GitHub release version; force-push, tag, create a GitHub release, amend earlier commits, or overwrite a remotely advanced branch; install global Python dependencies; or update unrelated Codex plugins.
**Architecture:** Keep `SUPERPLAN_VERSION` as the canonical base release and synchronize the Codex manifest, Claude manifest, development marketplace entry, package assertion, and generated `AGENTS.md` marker. Preserve B004's allowance for Codex-only SemVer build metadata, but keep committed release metadata exact. Treat the repository release commit as the push boundary. After the push succeeds, use `update_plugin_cachebuster.py` to create one temporary local suffix, reinstall from the already configured local `superplan-dev` marketplace, inspect the new installed cache, then restore the source manifest to exact `0.6.0` without another repository commit.
**Baseline:** Active release surfaces and the local Codex installation report `0.5.0`; workspace schema is `1`; `main` is clean and 11 commits ahead of `origin/main`; both the local tracking ref and a fresh `git ls-remote` identify remote `main` as `31eba55afa43d9d5061807c6146e944d0a74f067`; `codex plugin list` confirms `superplan@superplan-dev` is installed from this repository and no personal marketplace file exists. The plugin validator's default Python lacks PyYAML, so validation must use an isolated `uv --with pyyaml` invocation rather than modifying global Python.
**Exit Criteria:** All committed current release surfaces report exact `0.6.0`; schema remains `1`; package and repository verification pass; F021 is complete and committed separately; remote `main` points at the F021 release commit after a non-force push performed only if the remote preflight head is unchanged; the local Codex cache contains a `0.6.0+codex.*` installation whose delivery loop includes `Human-Decision Checkpoints`; the repository Codex manifest is restored to exact `0.6.0`; marketplace files remain unchanged except for the committed version field already owned by the release; and final Git status is clean.

## Task 1: Synchronize and verify the 0.6.0 release

**Outcome:** Repository package, runtime, validation, and generated workspace surfaces share one exact `0.6.0` identity without changing schema or historical evidence.
**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `AGENTS.md` (managed generator-version marker only)
- Modify: `README.md` (current workspace-marker example only)

**Change Map:**
- Release sources: replace active `0.5.0` values with exact `0.6.0` while preserving all non-version manifest content and workspace schema `1`.
- Package contract: update only the explicit canonical release expectation while retaining optional valid Codex build metadata and exact Claude/marketplace equality.
- Managed workspace and documentation: regenerate the guardrail block and update the current README marker example so both report `0.6.0`, without changing the F020 checkpoint rule, non-managed instructions, or historical evidence.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `uv run --with pyyaml python /Users/zhengxiwan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --root . --check`
- Search active release surfaces for stale `0.5.0` while preserving historical request and plan evidence.
- `git diff --check -- .codex-plugin .claude-plugin skills/using-superplan/scripts/superplan_version.py tests/scripts/test_plugin_package.py AGENTS.md README.md`

- [x] Set every committed current release surface to exact base version `0.6.0`.
- [x] Preserve workspace schema `1`, optional Codex build-metadata validation, and all non-version package content.
- [x] Regenerate only the managed workspace marker and keep historical version evidence unchanged.
- [x] Pass focused package and plugin validation before final repository verification.

## Task 2: Commit, push, and refresh the local Codex plugin

**Outcome:** GitHub and the local Codex installation both expose the verified F020 release while the repository finishes clean at exact `0.6.0`.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F021-release-superplan-0-6-0-and-refresh-local-codex.md`
- Modify: `docs/superplan/plans/README.md`
- Temporarily modify and restore: `.codex-plugin/plugin.json` after the release commit and push
- External: `origin/main`
- External: local Codex plugin cache for `superplan@superplan-dev`

**Change Map:**
- Release delivery: run `python3 tools/verify_repo.py`, complete F021, update the human entry and plan index, stage exact release paths, and create one F021-qualified release commit.
- Remote safety: immediately before pushing, compare `git ls-remote origin refs/heads/main` with the preflight remote head; push `main:main` without force only when unchanged, then verify the remote resolves to the release commit.
- Local Codex refresh: confirm `superplan-dev` still points at this repository, use the plugin-creator cachebuster helper, run `codex plugin add superplan@superplan-dev`, verify the new cached delivery loop and version, restore `.codex-plugin/plugin.json` to exact `0.6.0`, and confirm no source or marketplace drift remains.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`
- `git ls-remote origin refs/heads/main`
- `codex plugin list`
- Inspect `/Users/zhengxiwan/.codex/plugins/cache/superplan-dev/superplan/` for the installed `0.6.0+codex.*` cache and F020 checkpoint guidance.

- [x] Obtain current full repository, release-surface, plugin, plan-index, diff, and status evidence.
- [x] Complete F021 and create a dedicated release commit containing only release and progress artifacts.
- [x] Refuse a non-fast-forward overwrite if remote `main` changes; otherwise push the complete local `main` and verify the remote release commit.
- [x] Reinstall from the confirmed local `superplan-dev` marketplace using one temporary cachebuster without hand-editing marketplace configuration.
- [x] Verify the installed cache includes F020, restore the source manifest to exact `0.6.0`, and leave the repository clean.

## Implementation Evidence

- Release identity: `.codex-plugin/plugin.json`, both Claude package surfaces, `SUPERPLAN_VERSION`, the package assertion, the managed workspace marker, and the current README example report exact `0.6.0`; workspace schema remains `1` and historical `0.5.0` evidence was not rewritten.
- Validation: the six focused package tests passed; the plugin-creator validator passed through isolated `uv --with pyyaml`; `python3 tools/verify_repo.py` passed 105 tests, compilation of 19 Python files, workspace compatibility, request, guardrail, plan-index, and diff checks.
- GitHub delivery: fresh pre-push evidence kept remote `main` at `31eba55afa43d9d5061807c6146e944d0a74f067`; `git push origin main:main` fast-forwarded it to release implementation commit `3b9e6bf94ea3f0170747d6c502a58becc5b29326` without force.
- Local Codex refresh: the existing local `superplan-dev` marketplace reinstalled `superplan` as `0.6.0+codex.20260818123736` under `/Users/zhengxiwan/.codex/plugins/cache/superplan-dev/superplan/0.6.0+codex.20260818123736`; the cached delivery loop contains `Human-Decision Checkpoints` and matches the repository SHA-256 `3051e2a411645d6d890399fd3c78426e5f43dbeb69e2825b85c57d8fa5423ff8`.
- Source restoration: after installation, `.codex-plugin/plugin.json` was restored to exact `0.6.0`; `codex plugin list` still reports the enabled cachebuster installation, marketplace configuration is unchanged, and the repository returned to a clean state before completion metadata.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F018-release-superplan-0-4-1.md`
- `docs/superplan/plans/features/F019/02-rfc-workflow-guidance-and-release.md`
- `docs/superplan/plans/features/F020-safe-checkpoint-commits-before-human-decision-pauses.md`
- `docs/superplan/plans/bugs/B004-accept-codex-cachebuster-build-metadata.md`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `skills/using-superplan/scripts/superplan_version.py`
- `tests/scripts/test_plugin_package.py`
- `README.md`
