---
id: "F013"
title: "Integrate Effective Workflow Guidance into Superplan"
type: "feature"
status: "complete"
summary: "Fold the useful GPT-5.6 workflow rules into conditional Superplan references and remove the redundant bundled dependency layer."
source: "docs/superplan/human/features.md"
created: "2026-07-30"
depends_on: ["F012-02"]
parent: ""
---
# Integrate Effective Workflow Guidance into Superplan Plan

**Goal:** Keep the GPT-5.6-specific workflow decisions that materially improve Superplan while removing redundant independent skills and their global routing cost.
**Scope:** Curate the current 13 bundled skills into route-owned Superplan references: preserve concise systematic debugging and worktree execution guidance, merge test-first, high-risk verification, review, ambiguity, execution, and delivery boundaries into their existing canonical owners, and remove the remaining dependency tree, lock, visual companion, supplemental plugin discovery, and obsolete package wording. Keep exactly the existing four Superplan skills discoverable.
**Non-Goals:** Do not copy all 13 skill bodies into `using-superplan`; expose generic helper skills outside Superplan routes; preserve the brainstorming visual companion; change request/plan schemas, approval gates, workspace-safety consent, or observable feature/bug delivery behavior; rewrite completed human entries, plans, or implementation evidence; add installation/download logic; or retain a renamed Superworkflow dependency layer.
**Architecture:** Use conditional references rather than more top-level skills. `bugfix-plan-and-delivery` owns a compact debugging reference covering reproduction, falsifiable root cause, discriminating checks, source fixes, regression capture, and condition-based waiting. `using-superplan` owns a compact worktree reference loaded only after the human accepts isolation; Workspace Safety remains in `delivery-loop.md`. The delivery loop and verification matrix absorb only the non-obvious cross-route boundaries from brainstorming, execution, TDD, review, and completion verification. Remove `using-superpowers`, writing/logging helpers, generic review/branch helpers, and all bundled support files because their remaining guidance is native capability, duplicate policy, or outside Superplan's product boundary. Remove the custom Codex `skills` manifest field so default discovery exposes only root `skills/`. Publish the public package contraction as Superplan `0.3.0` while retaining workspace schema `1`.
**Baseline:** Superplan `0.2.0` exposes four root route skills plus 13 skills under `deps/superpowers`. The bundled `SKILL.md` files total about 290 lines, but all 13 descriptions participate in skill discovery even when only a small subset changes Superplan decisions. Current Superplan guidance directly invokes `brainstorming`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, and `writing-plans`; F004-F010 and F012 already make delivery-loop, route, verification, and workspace-safety documents authoritative for most of those behaviors. The dependency also carries a visual companion and stale upstream-root assumptions that are not required by Superplan.
**Exit Criteria:** The installed plugin discovers exactly the four existing Superplan skills with no supplemental dependency path; `deps/superpowers`, its lock, and its package test are absent; bug routes retain evidence-based root-cause diagnosis and focused regression behavior through a local conditional reference; accepted worktree isolation retains safe creation/reuse guidance through a local conditional reference; delivery, TDD, high-risk review, verification, and completion rules have one concise canonical owner without creating a large always-loaded skill; current manifests, README, installation docs, tests, and examples no longer claim a bundled Superpowers/Superworkflow runtime; `SUPERPLAN_VERSION` and all plugin manifests report `0.3.0`, workspace schema remains `1`, and existing workspaces remain compatible; historical records and deliberate negative compatibility assertions remain unchanged; the full script suite, four skill validations, behavior scenarios, guardrail/index checks, and diff/status checks pass.

## Task 1: Preserve valuable behavior in conditional Superplan references

**Outcome:** Bug diagnosis and approved worktree isolation retain their useful safeguards without exposing generic workflow skills globally.
**Files:**
- Create: `skills/bugfix-plan-and-delivery/references/debugging.md`
- Create: `skills/using-superplan/references/worktrees.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- Bugfix debugging: replace external skill invocation with one concise conditional reference that requires reliable reproduction or bounded evidence, a falsifiable root-cause hypothesis, the cheapest discriminating check, a source-level fix, a focused behavior regression when practical, and condition-based waiting for asynchronous flakiness.
- Worktree execution: keep semantic dirty-state classification and human consent in Workspace Safety; load the new worktree reference only after acceptance to cover reuse, branch/path choice, original-work preservation, setup restraint, and a cheap attributable baseline.
- Canonical delivery policy: replace the named Superpowers composition section with direct ambiguity, plan ownership, execution, evidence, test-first, and independent-review boundaries already owned by Superplan.
- Behavior scenarios: prove bug and worktree routes load the local conditional guidance at the correct decision point and no longer require external workflow skills.

**Verification:**
- Validate `skills/using-superplan` and `skills/bugfix-plan-and-delivery` with `quick_validate.py`
- Review applicable bug and worktree scenarios in `tests/behavior/workflow.md`
- `git diff --check -- skills/using-superplan skills/bugfix-plan-and-delivery tests/behavior/workflow.md`

- [x] Add only the debugging and worktree details that change route behavior or safety decisions.
- [x] Integrate cross-route workflow boundaries into their existing canonical owners without bloating top-level skills.
- [x] Prove conditional loading preserves bugfix and worktree outcomes without external Skill invocation.

## Task 2: Remove the bundled dependency and simplify the plugin package

**Outcome:** Superplan ships as one focused four-skill plugin with synchronized metadata, documentation, and package validation.
**Files:**
- Delete: `deps/superpowers/`
- Delete: `deps/superpowers.lock.json`
- Delete: `tests/scripts/test_bundled_superpowers.py`
- Create: `tests/scripts/test_plugin_package.py`
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `tests/scripts/test_init_workspace.py`
- Modify: `README.md`
- Modify: `docs/install.md`
- Modify: `AGENTS.md` (managed generator-version marker only)

**Change Map:**
- Dependency removal: delete all 13 bundled skill directories, support resources, visual companion, and integrity lock after Task 1 owns the retained behavior.
- Plugin contract: remove custom supplemental skill discovery and Superpowers/Superworkflow descriptions; verify default discovery contains exactly the four root Superplan skills with no duplicate or dependency-layer assumptions.
- Package/version tests: replace dependency integrity coverage with manifest/version/default-skill/package-boundary coverage; retain the negative initialization assertion that obsolete profile options do not return.
- Version and docs: publish `0.3.0`, keep workspace schema `1`, refresh only the managed generator marker, and document the conditional-reference architecture and four-skill installation/validation flow.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `git diff --check -- deps .codex-plugin .claude-plugin skills/using-superplan/scripts tests/scripts README.md docs/install.md AGENTS.md`

- [x] Delete the dependency only after all retained behavior has a concise Superplan owner.
- [x] Make default four-skill discovery and synchronized `0.3.0` metadata executable package contracts.
- [x] Keep schema compatibility and user-owned `AGENTS.md` content intact while removing obsolete runtime documentation.

## Task 3: Verify and deliver the focused Superplan package

**Outcome:** The consolidation is regression-safe, structurally valid, progress-complete, and committed without unrelated workspace state.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Run focused checks during implementation and one full script regression after instruction ownership, package structure, manifests, tests, and docs stabilize.
- Validate all four remaining skills, execute the applicable fresh-context behavior scenarios, and verify workspace compatibility, managed guardrails, plan integrity, current-reference cleanup, and exact status.
- Mark F013 and its human request complete only after current evidence passes; regenerate the index and create one F013-qualified commit while leaving the existing `AGENTS.md` memory timestamp unstaged.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- Run `quick_validate.py` for all four directories under `skills/`
- Execute the applicable scenarios from `tests/behavior/workflow.md`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- Review an allowlisted search proving old dependency terms remain only in completed history and deliberate negative compatibility assertions
- `git diff --check`
- `git status --short`

- [x] Obtain current script, skill, behavior, workspace, guardrail, plan, cleanup, and diff evidence.
- [x] Mark F013 complete and update the generated index without rerunning unchanged implementation checks.
- [x] Create a dedicated F013 commit that excludes unrelated user-owned state.

## Implementation Evidence

- Conditional ownership: bug diagnosis now loads `bugfix-plan-and-delivery/references/debugging.md`; accepted isolation loads `using-superplan/references/worktrees.md`. The delivery loop and verification matrix own the remaining ambiguity, execution, test-first, review, and claim-to-evidence boundaries without adding top-level skills.
- Fresh-context behavior: independent reasoning passes for the accepted-bug and accepted-worktree scenarios loaded only local Superplan references, preserved root-cause/approval and original-worktree safeguards, and required no external workflow skill.
- Package contraction: the new package test first failed against `0.2.0`, the supplemental manifest path, and the existing dependency tree. It now passes with exactly four root skills, no `deps`, no supplemental `skills` field, synchronized `0.3.0` manifests, and workspace schema `1`.
- Final verification: `python3 -m unittest discover -s tests/scripts` passed 68 tests; all four skills passed `quick_validate.py`; the plugin validator, workspace compatibility, managed guardrail, human registry, plan index, current-package stale-reference allowlist, and `git diff --check` passed. No installed plugin cache, marketplace configuration, user profile, or `~/.superplan` state was changed.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F010-clarify-worktree-numbering-composition.md`
- `docs/superplan/plans/features/F012/01-bundled-superpowers-and-versioned-workspace.md`
- `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- `skills/bugfix-plan-and-delivery/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/verification-matrix.md`
