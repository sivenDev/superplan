---
id: "F009"
title: "Optimize Superplan Runtime Skill Structure"
type: "feature"
status: "complete"
summary: "Fix workspace and template inconsistencies while separating runtime skill resources from setup details and development tests."
source: "docs/superplan/human/features.md"
created: "2026-07-21"
depends_on: ["F008"]
parent: ""
---
# Optimize Superplan Runtime Skill Structure Plan

**Goal:** Make Superplan's installed skills smaller and more coherent while correcting root targeting and newly initialized human documentation.
**Scope:** Deliver the approved P0/P1 set: centralize existing-workspace versus initialization root resolution; move generated human and guardrail templates into skill assets; align new human docs with adaptive accepted intake; move GPT-5.6 setup detail behind a conditional reference; remove generic AI guidance from managed guardrails; and relocate unit and behavior tests outside the runtime skill tree.
**Non-Goals:** Do not add P2 human-plan status enforcement, change plan or request schemas, delete the historical Superpowers transition spec, merge route skills, create a new core/setup skill, split the plan generator or profile installer by file size, add another profile, or change profile activation behavior.
**Architecture:** Treat this as a standard-risk workspace behavior and packaging change. Keep all user-facing CLI entry scripts at their current paths. Add one small shared `workspace_paths.py` module with explicit existing-workspace and initialization-target contracts, and make tests load the scripts directory consistently. Treat generated Markdown as `assets`, runtime decision material as `references`, and repository-only validation material as root `tests`. Keep `using-superplan/SKILL.md` focused on initialization and routing; load `profile-setup.md` only for installation, dependency diagnosis, or profile-sensitive initialization. Preserve the four-skill route architecture and exact managed-block synchronization.
**Baseline:** `init_workspace.py` embeds three large Markdown templates that still imply every request must pause at `proposed`; root detection differs across four scripts and two scripts accept any ancestor containing `docs`; `using-superplan/SKILL.md` carries profile replacement details during normal routing; the injected guardrail template includes three generic development rules; `agents-guardrails.md` and behavior tests are stored as runtime references even though they are generated/development artifacts; and 2,170 lines of unit tests ship inside `skills/using-superplan/scripts/tests`.
**Exit Criteria:** Every workspace-targeting CLI resolves the Git top-level or existing `docs/superplan` root consistently and initialization alone can target a new directory; nested unrelated `docs` directories cannot capture writes; generated feature/bug templates describe both conservative proposed intake and explicitly authorized direct acceptance; human and guardrail templates live under assets; normal routing does not load profile installation detail; managed guardrails contain only Superplan-specific policy; all unit and behavior tests live under root `tests`; documented commands and references use the new locations; user-owned non-managed `AGENTS.md` content remains unstaged; focused tests, the relocated full suite, skill validation, behavior scenarios, guardrail sync, plan-index validation, and diff checks pass.

## Task 1: Correct workspace targeting and asset-backed initialization

**Outcome:** Workspace scripts share one explicit root contract, and initialization renders current human documentation from editable assets rather than embedded Python strings.
**Files:**
- Create: `skills/using-superplan/scripts/workspace_paths.py`
- Modify: `skills/using-superplan/scripts/init_workspace.py`
- Modify: `skills/using-superplan/scripts/record_human_request.py`
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `skills/using-superplan/scripts/sync_agents_guardrails.py`
- Create: `skills/using-superplan/assets/human/prd.md`
- Create: `skills/using-superplan/assets/human/features.md`
- Create: `skills/using-superplan/assets/human/bugs.md`
- Create: `tests/scripts/test_workspace_paths.py`
- Move/Modify: `tests/scripts/test_init_workspace.py`
- Move/Modify: `tests/scripts/test_record_human_request.py`
- Move/Modify: `tests/scripts/test_generate_plans_readme.py`
- Move/Modify: `tests/scripts/test_sync_agents_guardrails.py`

**Change Map:**
- `workspace_paths.py`: resolve an existing workspace through Git top-level first and an existing `docs/superplan` ancestor second; resolve initialization to an explicit/Git/existing root and otherwise the requested start directory.
- Workspace CLIs: retain their public arguments while replacing inconsistent `detect_repo_root` behavior with the shared contract.
- `init_workspace.py`: load human templates from skill assets and keep idempotent no-overwrite behavior.
- Human assets: document adaptive `accepted` capture only for explicit, faithful, unambiguous requests while retaining `proposed` as the default/manual review path.
- Focused tests: cover nested unrelated `docs`, linked Git/worktree roots, non-Git existing Superplan roots, new initialization targets, and unchanged CLI output locations.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_workspace_paths.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_record_human_request.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_sync_agents_guardrails.py'`
- `git diff --check -- skills/using-superplan/scripts skills/using-superplan/assets/human tests/scripts`

- [x] Define one tested root resolver without changing current CLI paths or explicit `--root` authority.
- [x] Prevent nested generic `docs` directories from capturing request, plan-index, or guardrail writes.
- [x] Move the three human templates into assets and align feature/bug guidance with F008 adaptive intake.
- [x] Preserve initialization idempotency and existing human-file no-overwrite behavior.

## Task 2: Reduce runtime instruction and guardrail load

**Outcome:** Normal Superplan routing loads only workflow decisions, while setup detail and generated guardrails live behind accurate conditional/resource boundaries.
**Files:**
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/project-bootstrap-from-prd/SKILL.md`
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Create: `skills/using-superplan/references/profile-setup.md`
- Move/Modify: `skills/using-superplan/assets/agents-guardrails.md`
- Remove: `skills/using-superplan/references/agents-guardrails.md`
- Modify: `skills/using-superplan/scripts/sync_agents_guardrails.py`
- Modify: `AGENTS.md` (managed block only)
- Modify: `README.md`

**Change Map:**
- `using-superplan/SKILL.md`: keep dependency/setup routing and initialization entry commands concise; point to `profile-setup.md` only when setup, profile replacement, or dependency diagnosis is relevant.
- `profile-setup.md`: own dry-run, replacement approval, dependency-check freshness, supported model, and restart guidance without duplicating the human-facing install guide.
- `delivery-loop.md`: correct the blanket root-detection statement and remove repeated setup/guardrail explanations where a named resource owns them.
- Guardrail asset: retain only Superplan-specific workspace, progress, structural-plan, verification, and commit policy; remove generic correctness/performance/model-capability prose.
- Project bootstrap and sync script: invoke synchronization without loading the output template as decision context.
- `AGENTS.md`: update only the managed block and preserve the user's `# 第一规范` and memory-context changes unstaged.
- `README.md`: reflect the asset/reference boundary and keep the short install flow consistent.

**Verification:**
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `for skill in skills/*; do python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"; done`
- `git diff --check -- skills/*/SKILL.md skills/using-superplan/references skills/using-superplan/assets README.md AGENTS.md`

- [x] Move profile-specific detail out of the entry body while keeping installation and diagnosis discoverable at the decision point.
- [x] Make the guardrail template an output asset and remove all generic AI development advice from its managed block.
- [x] Shorten the always-loaded delivery/entry path without removing approval, workspace safety, evidence, or routing behavior.
- [x] Synchronize only the managed `AGENTS.md` hunk and leave all non-managed user changes untouched and unstaged.

## Task 3: Separate repository validation from the installed skill

**Outcome:** Runtime skill folders contain runtime resources only, and repository tests remain discoverable, isolated, and behaviorally equivalent at their new root paths.
**Files:**
- Move/Modify: `tests/scripts/test_check_superpowers.py`
- Move/Modify: `tests/scripts/test_install_superpowers_profile.py`
- Move/Modify: remaining script tests from `skills/using-superplan/scripts/tests/`
- Move/Modify: `tests/behavior/workflow.md`
- Remove: `skills/using-superplan/references/workflow-behavior-tests.md`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `README.md`

**Change Map:**
- Root tests: preserve direct script/module coverage while resolving production paths from the repository root and keeping state/skills fixtures isolated.
- Behavior scenarios: retain the existing prompt/fixture/expected/forbidden contract under repository development tests rather than runtime references.
- Verification matrix and README: use the relocated focused/full-suite and behavior-test paths.
- Runtime tree: remove empty test/reference development directories only after all references and commands point to the new locations.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- Follow the applicable scenarios in `tests/behavior/workflow.md` with fresh contexts for normal feature routing, profile setup routing, workspace-root safety, and asset-backed initialization.
- `find skills/using-superplan -path '*/tests/*' -o -name 'workflow-behavior-tests.md'`
- `git diff --check -- tests skills/using-superplan README.md`

- [x] Relocate all six script test modules without weakening their 84-test behavioral coverage.
- [x] Relocate behavior scenarios and update every command/reference to the new development-only path.
- [x] Confirm the installed skill tree no longer contains repository-only test artifacts.

## Task 4: Verify and deliver F009 without absorbing user state

**Outcome:** The P0/P1 restructuring is internally consistent, preserves runtime behavior, and is delivered as one traceable commit with unrelated workspace state intact.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Review F007-F009 together so instruction reduction, state-aware workflow, and resource-layer restructuring remain independent and do not reopen excluded P2 work.
- Run focused checks during implementation and one relocated full regression after code and paths stabilize; reuse that evidence across metadata-only completion updates.
- Record fresh-context behavior results, mark F009 and its human entry complete, refresh the index once, and stage the managed `AGENTS.md` hunk separately from user-owned content.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `for skill in skills/*; do python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"; done`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [x] Confirm F009 changes only the approved P0/P1 boundaries and keeps F007/F008 guarantees intact.
- [x] Obtain current evidence from focused tests, the relocated 84-test suite, skill validation, behavior scenarios, guardrail sync, index validation, and diff checks.
- [x] Mark progress complete and create a dedicated F009 commit containing only task files plus the managed `AGENTS.md` hunk.

## Implementation Evidence

- Root-resolution TDD: the focused test first failed because `workspace_paths.py` was absent; the final module passed 6 tests covering Git precedence, linked worktrees, non-Git Superplan ancestors, failure outside a workspace, new initialization targets, and all four CLI write locations.
- Script regression: `python3 -m unittest discover -s tests/scripts` passed 90 tests, preserving the relocated 84-test suite and adding 6 root-resolution tests.
- Structure and instructions: all four bundled skills passed `quick_validate.py`; current runtime references use `tests/behavior/workflow.md` and `tests/scripts`; no test or workflow-behavior artifact remains in the installed skill tree.
- Generated assets: disposable initialization matched all human assets byte-for-byte, preserved an existing human file on rerun, and synchronized only the four Superplan-specific guardrails.
- Fresh-context behavior: direct feature intake produced an `accepted` entry and `draft` plan then stopped for approval; a conflicting profile dry-run stopped before replacement authorization; nested workspace commands wrote only to the Git top-level.
- Final implementation checks: guardrail `--check`, CLI help smoke paths, `git diff --check`, plan-index generation, and user-owned `AGENTS.md` preservation passed.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/intake-spec.md`
- `skills/using-superplan/references/plan-spec.md`
- `skills/using-superplan/references/verification-matrix.md`
