---
id: "B004"
title: "Accept Codex Cachebuster Build Metadata in Package Contract"
type: "bugfix"
status: "complete"
summary: "Allow the Codex manifest to append valid SemVer build metadata while preserving canonical base-version synchronization."
source: "docs/superplan/human/bugs.md"
created: "2026-08-18"
depends_on: ["F014"]
parent: ""
---
# Accept Codex Cachebuster Build Metadata in Package Contract Plan

**Goal:** Restore the authoritative repository verifier without removing the Codex plugin cachebuster or weakening shared version synchronization.
**Scope:** Update the package contract so `.codex-plugin/plugin.json` may use the canonical Superplan version with optional valid SemVer build metadata, while the runtime version, Claude manifest, and marketplace remain exact canonical matches.
**Non-Goals:** Do not change the current cachebuster, publish a new Superplan version, alter workspace schema or generated guardrails, relax non-version package checks, or modify F017 implementation artifacts.
**Architecture:** Keep the policy in the existing self-contained package test. Match the Codex manifest against the canonical version plus an optional SemVer build suffix; retain exact equality for every shared release surface that does not use cache invalidation metadata.
**Baseline:** Commit `ff5dac4` changed only the Codex manifest version from `0.4.0` to `0.4.0+codex.20260804101449`. The package contract still compares that field to `SUPERPLAN_VERSION` with exact equality, so its focused test and `tools/verify_repo.py` fail while the other 93 repository tests pass.
**Reproduction:** Run `python3 -m unittest tests.scripts.test_plugin_package.PluginPackageTests.test_manifests_share_version_and_use_default_skill_discovery`; it fails because `0.4.0+codex.20260804101449 != 0.4.0`.
**Root Cause:** The package contract models every manifest version as an identical release string, but the Codex manifest now deliberately uses SemVer build metadata as a cache key. Build metadata does not change version precedence or the canonical base release, so exact full-string equality rejects a valid packaging state.
**Exit Criteria:** The package contract accepts the current Codex cachebuster, rejects a different base version or invalid build suffix, keeps Claude and marketplace versions exact, and both the focused package test and `python3 tools/verify_repo.py` pass without changing any manifest version.

## Task 1: Correct the Codex version contract

**Outcome:** Package validation distinguishes the canonical release version from Codex-only cachebuster metadata without weakening other manifest checks.
**Files:**
- Modify: `tests/scripts/test_plugin_package.py`

**Change Map:**
- `PluginPackageTests.test_manifests_share_version_and_use_default_skill_discovery`: validate the Codex version as the canonical version with an optional valid SemVer build suffix; retain exact assertions for the Claude manifest and marketplace.
- Add focused negative coverage for a mismatched base version and malformed build metadata if the existing test boundary cannot express both guarantees directly.

**Verification:**
- `python3 -m unittest tests.scripts.test_plugin_package.PluginPackageTests.test_manifests_share_version_and_use_default_skill_discovery`
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `git diff --check -- tests/scripts/test_plugin_package.py`

- [x] Preserve the current Codex manifest and cachebuster unchanged.
- [x] Accept only the canonical version with optional valid SemVer build metadata.
- [x] Keep exact canonical equality for Claude and marketplace versions.
- [x] Capture invalid base and suffix behavior without adding a new version parser module.

## Task 2: Verify and deliver B004 separately from F017

**Outcome:** The repository contract is green and the repair is recorded in a dedicated B004 commit without absorbing F017 changes.
**Files:**
- Modify: `docs/superplan/human/bugs.md`
- Modify: `docs/superplan/plans/bugs/B004-accept-codex-cachebuster-build-metadata.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Run the focused contract while iterating and the authoritative repository verifier once after the test stabilizes.
- Complete B004 progress and stage only the test plus exact B004 registry/plan/index hunks, leaving every F017 path or hunk unstaged.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Obtain current focused and full repository evidence.
- [x] Complete the plan, mark B004 done, and refresh the plan index without rerunning unchanged tests.
- [x] Create a dedicated `B004` commit containing no F017 implementation or progress changes.

## Implementation Evidence

- Regression: the focused manifest contract reproduced `0.4.0+codex.20260804101449 != 0.4.0` before the fix and passes after validating the canonical version with an optional SemVer build suffix.
- Boundaries: the same test rejects a different base version and an empty build identifier, while Claude and marketplace assertions remain exact; no manifest, runtime version, workspace schema, or F017 implementation file changed.
- Verification: the focused test passed, all six package-contract tests passed, and `python3 tools/verify_repo.py` passed 94 tests plus compilation, workspace, registry, guardrail, plan-index, and diff checks.

## References
- `docs/superplan/human/bugs.md`
- `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `.codex-plugin/plugin.json`
- `skills/using-superplan/scripts/superplan_version.py`
- `tests/scripts/test_plugin_package.py`
- `tools/verify_repo.py`
