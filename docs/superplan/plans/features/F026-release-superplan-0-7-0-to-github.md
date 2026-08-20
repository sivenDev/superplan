---
id: "F026"
title: "Release Superplan 0.7.0 to GitHub"
type: "feature"
status: "complete"
summary: "Synchronize the Superplan 0.7.0 release, verify it, and push main to GitHub without force."
source: "docs/superplan/human/features.md"
created: "2026-08-20"
depends_on: ["F025"]
parent: ""
---
# Release Superplan 0.7.0 to GitHub Plan

**Goal:** Publish the completed F025 skill-routing architecture as one consistent Superplan `0.7.0` release on GitHub.
**Scope:** Change every active release surface from exact `0.6.0` to exact `0.7.0`, preserve workspace schema `1`, regenerate the managed workspace marker, verify the plugin and repository, create a dedicated F026 release commit, and push local `main` to `origin/main` only when a fresh remote check still matches the preflight commit `c5e8ad5efe224127bcfda322f0a2e1b72fb9d3c0`.
**Non-Goals:** Do not change runtime behavior or workspace schema; rewrite historical version evidence; modify unrelated plugin metadata; add Codex build metadata to the committed release; refresh the local Codex installation; edit marketplace configuration beyond the existing repository release version field; force-push, tag, or create a GitHub Release.
**Architecture:** Keep `SUPERPLAN_VERSION` as the canonical base release and synchronize the Codex manifest, Claude manifest, repository marketplace entry, package assertion, managed `AGENTS.md` marker, and current README marker example. Treat the verified F026 commit as the only push boundary. Immediately before pushing, compare the remote `main` SHA with the recorded preflight SHA and stop rather than overwrite if it changed.
**Baseline:** Local `main`, tracking `origin/main`, and a fresh `git ls-remote` all identify F025 commit `c5e8ad5efe224127bcfda322f0a2e1b72fb9d3c0`. Active release surfaces report exact `0.6.0`, workspace schema is `1`, the repository is otherwise clean, and the only excluded state is the user-owned untracked `.codex/config.toml`.
**Exit Criteria:** All active release surfaces report exact `0.7.0`; schema remains `1`; focused package and plugin validation plus `python3 tools/verify_repo.py` pass; F026 is complete and committed independently; `.codex/config.toml` remains untracked and excluded; a fresh pre-push remote check still matches the preflight SHA; a non-force push updates `origin/main` to the F026 release commit; and the final remote SHA equals local `HEAD`.

## Task 1: Synchronize and verify the 0.7.0 release

**Outcome:** Package, runtime, generated workspace, documentation, and validation surfaces share exact release identity `0.7.0` without changing schema or behavior.
**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `AGENTS.md` (managed marker only)
- Modify: `README.md` (current marker example only)

**Change Map:**
- Release sources: replace active exact `0.6.0` values with `0.7.0`, retaining B004's optional Codex build-metadata contract and exact Claude/marketplace equality.
- Managed workspace: regenerate only the Superplan-managed `AGENTS.md` block after changing the canonical version; keep schema `1` and non-managed content unchanged.
- Documentation and tests: update only the current README marker example and explicit canonical package assertion; preserve historical `0.6.0` requests, RFCs, and completed plan evidence.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python /Users/zhengxiwan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --root . --check`
- Search active release surfaces for stale `0.6.0` while preserving historical evidence.
- `python3 tools/verify_repo.py`

- [x] Set all committed current release surfaces to exact `0.7.0`.
- [x] Preserve workspace schema `1`, optional Codex build metadata support, and non-version package content.
- [x] Regenerate only the managed version marker and keep historical version evidence unchanged.
- [x] Pass focused plugin/package checks and one final authoritative repository verification.

## Task 2: Complete, commit, and push F026

**Outcome:** F026 progress is complete in a dedicated release commit and GitHub `main` points to that verified commit through a safe non-force push.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F026-release-superplan-0-7-0-to-github.md`
- Modify: `docs/superplan/plans/README.md`
- External: `origin/main`

**Change Map:**
- Progress and commit: after implementation evidence is final, mark the plan complete, set F026 done, refresh the plan index, inspect ownership, and commit only F026 release/progress paths.
- Remote safety: immediately before push, require `git ls-remote origin refs/heads/main` to equal the preflight SHA; push `main:main` without force and verify the remote SHA equals the release commit.

**Verification:**
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short --untracked-files=all`
- `git ls-remote origin refs/heads/main`

- [x] Complete F026 and create a dedicated release commit that excludes `.codex/config.toml`.
- [x] Refuse to push if remote `main` differs from the preflight SHA.
- [x] Push `main:main` without force and verify GitHub resolves to the F026 release commit.

## Implementation Evidence

- Release identity: the Codex manifest, Claude manifest, repository marketplace entry, `SUPERPLAN_VERSION`, package assertion, managed `AGENTS.md` marker, and current README marker report exact `0.7.0`; workspace schema remains `1` and historical `0.6.0` evidence is unchanged.
- Validation: all 7 focused package tests passed; the plugin-creator validator and managed guardrail check passed; `python3 tools/verify_repo.py` passed 109 tests, compiled 19 Python files, and passed workspace, registry, guardrail, plan-index, and diff checks.
- GitHub delivery: the pre-push remote SHA remained `c5e8ad5efe224127bcfda322f0a2e1b72fb9d3c0`; non-force push advanced `origin/main` to verified release commit `3f5b4c62310b963925c66def596a7609b66a8605`.
- Ownership: the user-owned `.codex/config.toml` remained untracked and excluded; no tag, GitHub Release, local plugin reinstall, force push, or schema change occurred.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F018-release-superplan-0-4-1.md`
- `docs/superplan/plans/features/F021-release-superplan-0-6-0-and-refresh-local-codex.md`
- `docs/superplan/plans/features/F025-streamline-skill-routing-and-instructions.md`
- `docs/superplan/plans/bugs/B004-accept-codex-cachebuster-build-metadata.md`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `skills/using-superplan/scripts/superplan_version.py`
- `tests/scripts/test_plugin_package.py`
- `AGENTS.md`
- `README.md`
