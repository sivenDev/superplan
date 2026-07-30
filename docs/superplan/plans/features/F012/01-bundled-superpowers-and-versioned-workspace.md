---
id: "F012-01"
title: "Bundled Superpowers and Versioned Workspace Initialization"
type: "feature"
status: "complete"
summary: "Bundle the pinned Superpowers profile with the plugin and replace installation checks with versioned workspace checks and migrations."
source: "docs/superplan/human/features.md"
created: "2026-07-30"
depends_on: ["F009", "F010"]
parent: "F012"
---
# Bundled Superpowers and Versioned Workspace Initialization Plan

**Goal:** Make Superplan self-contained for Codex and keep initialized repositories compatible without probing or mutating user-level Superpowers installations.
**Scope:** Track the verified GPT-5.6 Superpowers skill snapshot under `deps/superpowers`, expose it through the Codex plugin alongside the default Superplan skills, record pinned provenance, remove the profile installation/check pipeline, and change `init_workspace.py` into a workspace-only initializer with read-only compatibility checking and explicit safe migration. Add workspace schema and generator version metadata to the managed guardrail block. Route entry automatically runs the read-only check; an older or missing schema enters the workspace-safety-controlled migration path, while a newer workspace schema stops and requires a newer Superplan version.
**Non-Goals:** Do not install, replace, back up, or inspect user-level skills; dynamically switch models; preserve the F006 profile installer as an alternative path; run network access during initialization; silently downgrade a newer workspace; overwrite human files or non-managed `AGENTS.md` content; treat every plugin version change as a schema migration; or edit installed plugin caches directly.
**Architecture:** Replace F006's runtime activation model with a vendored, pinned runtime dependency. The repository's `skills/` directory remains the default Superplan skill source, while the Codex manifest adds `deps/superpowers` as the supplemental skills path. Keep only runtime skill directories in the dependency snapshot and store repository URL, pinned revision, inventory, and integrity data in a committed lock artifact; validate that artifact during repository tests and plugin packaging rather than target initialization. Define `SUPERPLAN_VERSION` and `WORKSPACE_SCHEMA_VERSION` once in installed runtime code and test all plugin manifests against it. Preserve the existing managed start/end markers and add an interior machine-readable version marker for backward-compatible parsing. `init_workspace.py --check` performs no writes; normal initialization and `--migrate` update only missing templates, the managed guardrail block, and the generated plan index after workspace-safety evidence permits mutation.
**Baseline:** Superplan 0.1.0 clones and activates a pinned external profile into user skills, carries five profile/dependency Python modules plus setup guidance, and makes initialization fail when that installation is absent or drifted. Commit `5aa0ba6` added `deps/superpowers` as a 156 KB ordinary-file snapshot whose 13 skill files match pinned revision `aa973775906c8761a78019aaa21e4f0ccd987925` byte-for-byte; it still lacks committed provenance metadata and includes repository-only shell scripts with upstream-root assumptions. The Codex plugin currently points explicitly at `./skills/`; its manifest contract supplements custom skill paths on top of default discovery. Guardrail synchronization already detects exact stale content but cannot distinguish an older workspace schema from a newer incompatible one.
**Exit Criteria:** Installing the repository plugin exposes all four Superplan skills and the exact 13 bundled Superpowers skills without a separate profile installation; `init_workspace.py` has no Superpowers discovery, profile, model, state-root, installation, backup, or network behavior; the obsolete profile scripts, tests, and setup guidance are removed; the dependency snapshot is committed with reproducible provenance and inventory checks; plugin manifests share one semantic version source and pass validation; generated guardrails record workspace schema and generator version; read-only checks distinguish current, legacy/older, newer, malformed, and stale-generated states; migration preserves human files and non-managed content; initialization remains idempotent; and focused tests, the full script suite, plugin/skill validation, workspace migration scenarios, plan-index validation, and diff checks pass.

## Task 1: Package the pinned Superpowers skills as a verified plugin dependency

**Outcome:** The installed Codex plugin discovers the repository's pinned Superpowers snapshot directly and its provenance can be verified without a live user profile or network access.
**Files:**
- Add/Modify: `deps/superpowers/`
- Create: `deps/superpowers.lock.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Create: `tests/scripts/test_bundled_superpowers.py`
- Modify: `README.md`
- Modify: `docs/install.md`

**Change Map:**
- `deps/superpowers/`: retain the exact runtime skill directories from the pinned GPT-5.6 source; remove upstream repository-only synchronization/validation scripts that are not valid inside the Superplan root.
- Dependency lock and tests: record source repository, revision, expected inventory, and deterministic integrity evidence; reject missing, added, or changed runtime skill files.
- Plugin manifests: expose `deps/superpowers` as the supplemental Codex skills path while preserving default discovery of root `skills/`; keep version metadata synchronized and document the plugin-root installation requirement.
- Installation docs: remove the user-profile clone/activation/restart sequence and state that initialization is offline and workspace-only.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_bundled_superpowers.py'`
- Run the plugin-creator validator against the repository root
- Validate all 17 discovered skill folders with `quick_validate.py`
- `git diff --check -- deps .codex-plugin .claude-plugin README.md docs/install.md tests/scripts`

- [x] Commit only the pinned runtime dependency content and prove it matches the recorded source revision and inventory.
- [x] Verify plugin discovery includes both Superplan and bundled Superpowers skills without duplicate names.
- [x] Remove installation documentation and package claims that still describe Superpowers as non-vendored.

## Task 2: Remove the obsolete user-profile installation and dependency pipeline

**Outcome:** Initialization and normal Superplan operation no longer depend on user-level skill discovery, manifests, backups, clones, or profile checks.
**Files:**
- Delete: `skills/using-superplan/scripts/check_superpowers.py`
- Delete: `skills/using-superplan/scripts/install_superpowers_profile.py`
- Delete: `skills/using-superplan/scripts/superpowers_dependency.py`
- Delete: `skills/using-superplan/scripts/superpowers_profile_installer.py`
- Delete: `skills/using-superplan/scripts/superpowers_profiles.py`
- Delete/Modify: corresponding modules under `tests/scripts/`
- Delete: `skills/using-superplan/references/profile-setup.md`
- Modify: `skills/using-superplan/scripts/init_workspace.py`
- Modify: `tests/scripts/test_init_workspace.py`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/using-superplan/references/delivery-loop.md`

**Change Map:**
- Runtime scripts: remove the five profile/dependency responsibilities instead of relocating them; leave only commands that operate on Superplan workspaces and generated artifacts.
- `init_workspace.py`: remove Superpowers-related options and checks, preserve explicit root selection, and perform no user-home or network access.
- Runtime guidance and tests: delete setup-only routing and fixtures, update standalone/help behavior, and prove initialization succeeds in an isolated environment without any installed Superpowers profile.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- `python3 skills/using-superplan/scripts/init_workspace.py --help`
- `rg -n "check_superpowers|install_superpowers_profile|superpowers_profile|superpowers-state|profile-setup" skills tests README.md docs/install.md`
- `git diff --check -- skills/using-superplan tests/scripts README.md docs/install.md`

- [x] Remove all user-profile setup and validation entry points without leaving stale routing references.
- [x] Prove initialization works offline and does not inspect or mutate home-level skills or state.
- [x] Reduce the top-level runtime Python inventory by deleting obsolete responsibilities rather than merging them into a monolith.

## Task 3: Add workspace schema checks and safe migration

**Outcome:** Every routed task can detect stale or incompatible workspace artifacts before relying on them, with deterministic and bounded migration behavior.
**Files:**
- Create: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `skills/using-superplan/scripts/init_workspace.py`
- Modify: `skills/using-superplan/scripts/sync_agents_guardrails.py`
- Modify: `skills/using-superplan/assets/agents-guardrails.md`
- Modify: `tests/scripts/test_init_workspace.py`
- Modify: `tests/scripts/test_sync_agents_guardrails.py`
- Modify: `tests/behavior/workflow.md`
- Modify: `AGENTS.md` (managed block only)

**Change Map:**
- Version contract: define semantic plugin version and integer workspace schema once; repository tests keep Codex, Claude, and marketplace versions synchronized.
- Managed block: retain stable outer markers and add an interior `workspace-schema` plus `generated-by` marker.
- Initialization: add no-write `--check` and explicit `--migrate`; report current, older/missing, newer, malformed, and stale-generated states with distinct exit behavior; migrate only managed/generated artifacts and create missing templates without replacing human content.
- Route behavior: run the compatibility check automatically after workspace-safety inspection; current work proceeds, older work enters migration, and newer schema blocks until the plugin is upgraded.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_sync_agents_guardrails.py'`
- Migration behavior scenarios from `tests/behavior/workflow.md`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`

- [x] Keep plugin-version differences informational when workspace schema is compatible.
- [x] Never write during `--check`, downgrade a newer schema, or alter non-managed/human content during migration.
- [x] Make route-triggered migration obey the existing workspace-safety and exact-staging rules.

## Task 4: Verify and deliver the bundled-runtime transition

**Outcome:** The new dependency and initialization model is traceable, packaging-valid, and delivered independently of unrelated local state.
**Files:**
- Modify: `docs/superplan/plans/features/F012/01-bundled-superpowers-and-versioned-workspace.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Review F006, F008-F010, and F012-01 together so the historical profile delivery remains understandable while the current architecture deliberately replaces it.
- Run focused checks during implementation and one full regression after dependency, initialization, version, and packaging behavior stabilizes.
- Record evidence and commit the dependency snapshot, runtime removals, managed guardrail hunk, and F012-01 progress without unrelated memory metadata.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- Validate the plugin and all bundled skills
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [x] Obtain current dependency-integrity, packaging, initialization, migration, skill, and full script evidence.
- [x] Mark F012-01 complete only after the bundled plugin works without user-profile setup.
- [x] Create a dedicated F012-01 commit with exact task paths.

## Implementation Evidence

- Dependency packaging: `test_bundled_superpowers.py` passed and the bundled 25-file runtime tree matched the pinned GPT-5.6 source byte-for-byte after excluding the two invalid repository-root helper scripts. The committed lock records all 13 skills, every file hash, and the deterministic tree hash.
- Offline initialization TDD: focused tests first failed for the missing version module, lock, schema marker, and migration behavior; the final suite covers current, legacy/older, newer, malformed, stale, generator-version-only, idempotent, subprocess, no-home-access, preservation, and preflight-without-partial-write cases.
- Regression and validation: `python3 -m unittest discover -s tests/scripts` passed 51 tests; all four Superplan and 13 bundled Superpowers skills passed `quick_validate.py`; workspace compatibility, guardrail sync, plan-index write/check, stale-reference search, and `git diff --check` passed.
- Plugin contract: repository tests verify the spec-defined supplemental `./deps/superpowers/` path, default four-skill discovery, bundled 13-skill discovery, no duplicate names, and synchronized `0.2.0` manifests. The locally installed plugin-creator validator reported only its known hard-coded rejection of any `skills` value other than `./skills/`, despite its own current spec explicitly allowing custom supplemental paths; no other manifest error was reported.
- Runtime cleanup: five profile/dependency modules, two profile test modules, setup guidance, Git download/activation paths, and the two invalid dependency-root shell scripts were removed without touching existing `~/.superplan` state.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F006-gpt56-superpowers-profile-installation.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F010-clarify-worktree-numbering-composition.md`
- `.codex-plugin/plugin.json`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/verification-matrix.md`
