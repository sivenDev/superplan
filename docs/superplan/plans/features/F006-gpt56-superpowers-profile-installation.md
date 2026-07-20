---
id: "F006"
title: "GPT-5.6 Superpowers Profile Installation"
type: "feature"
status: "approved"
summary: "Install, activate, and verify the pinned GPT-5.6 Superpowers skill profile without vendoring it into Superplan."
source: "docs/superplan/human/features.md"
created: "2026-07-20"
depends_on: []
parent: ""
---
# GPT-5.6 Superpowers Profile Installation Plan

**Goal:** Give Superplan a safe, reproducible installation path for the GPT-5.6-specific Superpowers profile and make dependency checks and workspace initialization understand that active profile.
**Scope:** Add one explicit `gpt56` profile for `gpt-5.6` model ids, clone and pin `eagleagentic/superpowers-gpt-5.6`, transactionally activate its 13 Codex skills in one user skills directory, validate the active installation from Superplan, and document the install-to-init flow. The user-visible entry point requires `--model gpt-5.6`; it does not guess the current interactive `/model` selection.
**Non-Goals:** Do not support non-GPT-5.6 models, dynamically switch profiles while Codex is running, modify Codex model configuration, fall back from an unsupported model to obra/superpowers, vendor external skills into this repository, update the external dependency automatically, replace Codex-native delegation with a bundled dispatch skill, or delete a pre-existing skill without a recoverable backup.
**Architecture:** Treat this as high-risk local-state work because activation changes a user-level Codex skills directory and executes a pinned external validation script. Define the single supported profile once, including accepted model ids, repository URL, pinned revision `aa973775906c8761a78019aaa21e4f0ccd987925`, exact skill inventory, and manifest schema. The default state layout is `<state-root>/dependencies/superpowers-gpt-5.6/<commit>`, `<state-root>/backups/<timestamp>/skills`, and `<state-root>/active-superpowers-profile.json`, with `<state-root>` defaulting to `$HOME/.superplan`. The installer uses `resolve -> clone/verify -> preflight -> backup/activate -> verify/commit manifest`; persistent writes begin only after the complete preflight succeeds, and every move or link is journaled for rollback. An explicit `--skills-dir` wins; otherwise the installer reuses the one discovered user skills directory already containing `using-superpowers`, defaults to Codex's documented `$HOME/.agents/skills` only when no installation exists, and stops on ambiguous or duplicate installations. Existing no-argument dependency checks remain compatible when no profile manifest exists, while an active manifest or explicit GPT-5.6 selection triggers strict provenance, revision, inventory, and link validation. Codex's current-session model remains user-controlled through `/model` or `--model`; the installer cannot reliably infer that session-local choice from static configuration.
**Baseline:** Superplan currently checks one obra-oriented list of 12 required skills, requires `subagent-driven-development`, searches legacy Codex and Claude locations but not `$HOME/.agents/skills`, and has no profile, manifest, dependency installer, backup transaction, or model-aware initialization. The external repository is locally verified at commit `aa973775906c8761a78019aaa21e4f0ccd987925`; its context-budget validator passes and its 13 skills are `brainstorming`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-implementation-logs`, `writing-plans`, and `writing-skills`. It intentionally omits `subagent-driven-development` in favor of Codex-native subagents.
**Exit Criteria:** Running the documented installer with `--model gpt-5.6` activates exactly the pinned 13-skill profile or exits without changing user skills; unsupported models are rejected before filesystem mutation; all conflicts are reported before replacement; approved replacements are backed up and automatically restored after any failed activation; repeated installation of the same revision is a no-op; the active manifest and symlinks pass model-aware dependency checks and Superplan initialization; stale or tampered manifests and links fail explicitly; the legacy no-manifest check remains usable; documentation tells the user to restart Codex and select GPT-5.6 separately; and focused tests, the full script suite, the external context-budget validator, plan-index validation, and diff checks pass.

## Task 1: Establish the single GPT-5.6 profile contract and model-aware dependency checks

**Outcome:** Superplan has one authoritative GPT-5.6 profile definition, recognizes only the requested model family, and can distinguish a verified active profile from the existing legacy dependency check.
**Files:**
- Create: `skills/using-superplan/scripts/superpowers_profiles.py`
- Modify: `skills/using-superplan/scripts/superpowers_dependency.py`
- Modify: `skills/using-superplan/scripts/check_superpowers.py`
- Modify: `skills/using-superplan/scripts/tests/test_check_superpowers.py`

**Change Map:**
- `superpowers_profiles.py`: define the immutable `gpt56` profile, accepted model matcher (`gpt-5.6` and `gpt-5.6-*`), repository and pinned revision, exact 13-skill tuple, context-budget script path, removed legacy orchestration skill, manifest filename/schema version, and profile/model resolution errors.
- `superpowers_dependency.py`: parameterize required skills by resolved profile, add `$HOME/.agents/skills` to user discovery, detect ambiguous `using-superpowers` installations, report the selected profile in `CheckResult`, and strictly validate a GPT-5.6 manifest plus every recorded symlink target and source revision while retaining the current no-manifest legacy path.
- `check_superpowers.py`: accept `--model gpt-5.6`, `--profile gpt56`, and `--state-root`; reject unsupported or conflicting selectors before checking paths; print the detected profile, revision, skills directory, missing inventory, duplicate installations, or manifest drift precisely.
- `test_check_superpowers.py`: cover bare and suffixed GPT-5.6 ids, unsupported models, profile/model disagreement, exact missing-skill reporting, official and legacy search locations, ambiguous installations, valid manifests, wrong revisions, moved link targets, and unchanged no-argument legacy behavior.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests -p 'test_check_superpowers.py'`
- `python3 skills/using-superplan/scripts/check_superpowers.py --help`
- `git diff --check -- skills/using-superplan/scripts/superpowers_profiles.py skills/using-superplan/scripts/superpowers_dependency.py skills/using-superplan/scripts/check_superpowers.py skills/using-superplan/scripts/tests/test_check_superpowers.py`

- [ ] Define the only supported profile from the pinned external repository facts, including its complete skill inventory and Codex-native delegation boundary.
- [ ] Resolve explicit model and profile selectors without fallback, and make unsupported values fail before path or manifest mutation can occur.
- [ ] Extend discovery to the documented Codex user skills directory while preserving existing search compatibility and blocking ambiguous duplicate installations.
- [ ] Validate active GPT-5.6 provenance, revision, inventory, and link targets through the manifest while preserving the existing no-manifest dependency behavior.
- [ ] Add behavior-level tests for successful selection, missing or duplicated installations, unsupported models, and every manifest-drift failure surfaced to users.

## Task 2: Deliver a transactional GPT-5.6 clone and activation installer

**Outcome:** One command can acquire the pinned external profile, validate it, back up replaceable conflicts, activate all 13 skills, and leave the original installation recoverable if any step fails.
**Files:**
- Create: `skills/using-superplan/scripts/superpowers_profile_installer.py`
- Create: `skills/using-superplan/scripts/install_superpowers_profile.py`
- Create: `skills/using-superplan/scripts/tests/test_install_superpowers_profile.py`

**Change Map:**
- `superpowers_profile_installer.py`: implement destination resolution, fixed-revision clone caching under the state root, repository and skill validation, complete conflict classification, dry-run rendering, journaled backup/link operations, rollback, idempotency, and atomic manifest publication. Keep repository execution and filesystem operations injectable so tests use local temporary repositories only.
- `install_superpowers_profile.py`: expose only `--model`, `--skills-dir`, `--state-root`, `--replace-existing`, and `--dry-run`; require GPT-5.6; summarize the resolved revision, target directory, conflicts, backup directory, activation result, recovery location, and restart requirement without exposing a generic arbitrary-repository option.
- `test_install_superpowers_profile.py`: build local fake Git repositories containing the exact profile structure and validator, then exercise clean install, cached clone reuse, dry-run, conflict refusal, approved backup, unknown-path blocking, duplicate-location blocking, `subagent-driven-development` removal, validator failure, malformed frontmatter, wrong inventory, failure injection at each mutation phase, manifest atomicity, exact rollback, and same-revision idempotency.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests -p 'test_install_superpowers_profile.py'`
- `python3 skills/using-superplan/scripts/install_superpowers_profile.py --help`
- `git diff --check -- skills/using-superplan/scripts/superpowers_profile_installer.py skills/using-superplan/scripts/install_superpowers_profile.py skills/using-superplan/scripts/tests/test_install_superpowers_profile.py`

- [ ] Resolve one unambiguous target directory, default state root, versioned dependency directory, timestamped backup directory, and manifest path without modifying them during resolution or dry-run.
- [ ] Clone into a temporary sibling, detach at the pinned commit, reject an unexpected `HEAD`, and publish the dependency cache only after the external context-budget check, exact directory inventory, regular-file boundaries, and frontmatter names all validate.
- [ ] Preflight every profile skill plus the obsolete `subagent-driven-development` path, list all conflicts at once, permit replacement only with `--replace-existing`, and block entries that cannot be safely identified and moved as complete recoverable paths.
- [ ] Move approved conflicts into one backup, create links for exactly the 13 validated source directories, remove the obsolete dispatch skill from the active set, verify all final targets, and atomically publish a manifest containing schema, profile, model, repository, revision, source, target, inventory, and backup provenance.
- [ ] Journal every mutation and restore the prior filesystem plus prior manifest in reverse order after any failure; retain successful backups for manual recovery and make a repeated identical activation report an idempotent no-op.
- [ ] Prove the transaction entirely with temporary directories and local Git fixtures so the unit suite never touches the network or real user skills.

## Task 3: Integrate the active profile with initialization and Superplan guidance

**Outcome:** Superplan initialization accepts the GPT-5.6 selection, refuses drifted activations, and routes delegation and installation guidance consistently with the external Codex-native profile.
**Files:**
- Modify: `skills/using-superplan/scripts/init_workspace.py`
- Modify: `skills/using-superplan/scripts/tests/test_init_workspace.py`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `README.md`
- Modify: `docs/install.md`

**Change Map:**
- `init_workspace.py`: add `--model`, `--superpowers-profile`, and `--superpowers-state-root` forwarding to the dependency check; auto-validate an existing active profile when selectors are omitted; stop before scaffolding when the manifest, revision, inventory, or links disagree; preserve `--skip-superpowers-check` as the explicit escape hatch.
- `test_init_workspace.py`: add valid GPT-5.6 initialization, model/profile mismatch, unsupported model, active-manifest auto-detection, drift rejection before workspace writes, and legacy compatibility cases.
- `using-superplan/SKILL.md`: document the profile-aware prerequisite check and installation command while preserving `<using-superplan-root>` path conventions.
- `delivery-loop.md`: replace the remaining hard-coded `subagent-driven-development` execution instruction with platform-native delegation selected only when the risk profile benefits from independent work.
- `README.md` and `docs/install.md`: document `install Superplan -> install GPT-5.6 profile -> restart Codex/new chat -> select or launch with GPT-5.6 -> check dependency -> initialize repository`, the fixed revision and external-dependency boundary, backups and recovery, dry-run and replacement semantics, and explicit refusal of other models.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests -p 'test_init_workspace.py'`
- `rg -n "gpt-5\.6|gpt56|install_superpowers_profile|active-superpowers-profile|native.*delegat|subagent-driven-development" skills/using-superplan README.md docs/install.md`
- `git diff --check -- skills/using-superplan/scripts/init_workspace.py skills/using-superplan/scripts/tests/test_init_workspace.py skills/using-superplan/SKILL.md skills/using-superplan/references/delivery-loop.md README.md docs/install.md`

- [ ] Forward explicit or active-profile selection through initialization and ensure every dependency failure occurs before human docs, guardrails, or the plan index are written.
- [ ] Keep legacy initialization compatible when no active profile exists, while rejecting unsupported selectors and manifest/link drift without silently reinstalling or repairing user state.
- [ ] Remove the workflow's dependency on the missing dispatch skill and describe Codex-native delegation without requiring subagents for small or medium tasks.
- [ ] Explain the exact installation, replacement, backup, restart, model-selection, verification, and initialization sequence, including why the installer requires an explicit model instead of inferring the current `/model` session.
- [ ] Cover the profile-aware initialization boundary with temporary-workspace tests that prove both success and pre-write refusal behavior.

## Task 4: Prove the pinned end-to-end flow and finish F006

**Outcome:** The real pinned repository, transactional activation, dependency check, workspace initialization, rollback coverage, project progress, and generated index are verified together before delivery.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F006-gpt56-superpowers-profile-installation.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Exercise the real GitHub revision only in a disposable state root and skills directory; do not install into the developer's live user directory during repository verification.
- Run the installed external `check-context-budget.sh`, model-aware dependency check, temporary Git workspace initialization, and a second identical activation to prove the real inventory and idempotency.
- Use the installer unit suite's injected failures as rollback evidence, then run the complete Superplan script regression suite once after implementation stabilizes.
- Review F001-F006 together for independent boundaries and accurate dependency metadata, mark F006 and its human entry complete only after all evidence passes, regenerate the plan index, and create an F006-qualified implementation commit without staging unrelated workspace changes.

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `git diff --check`
- Disposable real-repository smoke flow: create a `mktemp -d` root; install with `--model gpt-5.6 --state-root <temp>/state --skills-dir <temp>/skills --replace-existing`; run the cached `skills/superpowers/check-context-budget.sh`; run `check_superpowers.py --model gpt-5.6 --state-root <temp>/state --skills-dir <temp>/skills --no-default-search`; initialize a temporary Git repository with `init_workspace.py --model gpt-5.6 --superpowers-state-root <temp>/state --superpowers-skills-dir <temp>/skills --no-default-superpowers-search`; and rerun the same installer command expecting an idempotent no-op.

- [ ] Run the focused profile, installer, and initialization tests, including injected failures that prove the original skill tree and manifest are restored exactly.
- [ ] Run the real pinned repository smoke flow entirely under a disposable directory and confirm all 13 activated links resolve into the pinned dependency cache.
- [ ] Run the full script suite, guardrail check, plan-index write/check, and repository diff validation against the final implementation state.
- [ ] Review the complete feature-plan set, then mark F006 `complete`, mark its human entry `done`, and regenerate the plan index without rerunning unchanged code tests after metadata-only updates.
- [ ] Commit only the F006 implementation, tests, documentation, progress, and generated index with a plan-qualified commit message.

## References
- `docs/superplan/human/features.md`
- `skills/using-superplan/scripts/superpowers_dependency.py`
- `skills/using-superplan/scripts/check_superpowers.py`
- `skills/using-superplan/scripts/init_workspace.py`
- `skills/using-superplan/references/delivery-loop.md`
- `https://github.com/eagleagentic/superpowers-gpt-5.6/tree/aa973775906c8761a78019aaa21e4f0ccd987925`
- `https://learn.chatgpt.com/docs/models`
- `https://learn.chatgpt.com/docs/customization/skills`
- `https://learn.chatgpt.com/docs/agent-configuration/subagents`
