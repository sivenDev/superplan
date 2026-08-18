---
id: "F019-02"
title: "RFC Workflow Guidance and Release"
type: "feature"
status: "approved"
summary: "Integrate the approved RFC workflow into feature guidance, behavior coverage, documentation, and a compatible Superplan release."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F013", "F019-01"]
parent: "F019"
---
# RFC Workflow Guidance and Release Plan

**Goal:** Make agents and users consistently apply the enforced RFC stage only when needed, with concise Chinese-first documents, separate RFC and plan approvals, and no additional top-level workflow route.
**Scope:** Add one route-owned RFC specification, conditionally load it from the existing feature skill, align shared plan and verification rules, update new-workspace/user documentation, add behavior scenarios for explicit and autonomous RFC selection, and publish the backward-compatible feature as Superplan `0.5.0` while keeping workspace schema `1`.
**Non-Goals:** Do not duplicate the RFC specification across skills, add another root skill or plan type, require RFC for ordinary features, add a general RFC catalog/search/translation tool, preserve conversation transcripts, rewrite existing user-maintained feature registries during migration, or change the state/parser implementation delivered by F019-01 except for defects found during integration.
**Architecture:** Follow F013's conditional-reference model: `feature-plan-and-delivery` remains the discoverable route and loads one concise `rfc-spec.md` only for explicit RFC requests or `requires_rfc: true`. Keep selection, default language, document shape, version semantics, approval, and revision guidance in that reference; keep shared executable-plan consequences in `plan-spec.md` and artifact-aware checks in `verification-matrix.md`. Use behavior scenarios for judgment and pause semantics that should not be encoded as brittle text parsers. Publish a minor release because this adds a backward-compatible public workflow and CLI contract; retain schema `1` because old workspaces and entries remain valid and RFC directories are lazy.
**Baseline:** The package exposes exactly four root skills and uses conditional references for specialized behavior; feature routing currently moves accepted requests directly to draft plans; the new F019-01 model can enforce RFC metadata and approval but agents and users lack shipped selection, writing, language, revision, and review instructions. Current active release surfaces report `0.4.1`, and workspace schema `1` supports compatible generated-artifact updates.
**Exit Criteria:** The feature skill conditionally loads one concise RFC specification; explicit requests always use RFC; autonomous selection states consequential reasons; size alone does not trigger RFC; explicit refusal is respected unless material risk requires confirmation; RFCs default to Chinese, use flat feature-id filenames and positive integer approval versions, omit conversation logs, and follow required sections; RFC approval precedes plan creation and plan approval precedes coding; new workspace guidance and README are accurate; exactly four root skills remain; all applicable behavior scenarios and repository verification pass; all release surfaces report `0.5.0` with schema `1`; both F019 plans complete before F019 becomes done; and F019-02 is committed separately.

## Task 1: Add the concise conditional RFC specification

**Outcome:** The existing feature route has one authoritative, conditionally loaded RFC workflow contract.
**Files:**
- Create: `skills/feature-plan-and-delivery/references/rfc-spec.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `tests/scripts/test_plugin_package.py`

**Change Map:**
- `rfc-spec.md`: define explicit and autonomous selection, consequential-risk criteria, explicit-decline handling, flat feature-id path, Chinese default and overrides, required frontmatter including positive integer version, minimum body sections, draft/approved and version-increment rules, Git-based revision history, prohibited chat logs, RFC approval pause, and the exact handoff to feature plan drafting.
- `feature-plan-and-delivery/SKILL.md`: add only the conditional loading trigger and stop boundary; keep general intake, delivery, and plan content delegated to existing references.
- Shared references: require an approved exact RFC reference for RFC-backed feature plans and add focused/final verification guidance for RFC metadata, language/section review, approval gates, and metadata-only RFC updates without duplicating the route specification.
- Package contract: prove the feature skill references the shipped conditional file and the package still exposes exactly four root skills with concise frontmatter.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- Inspect all four root skills and the new conditional reference for ownership and trigger clarity
- `git diff --check -- skills/feature-plan-and-delivery skills/using-superplan/references tests/scripts/test_plugin_package.py`

- [ ] Write the smallest complete RFC contract covering selection, Chinese default, artifact format, versioning, revisions, approvals, and plan handoff.
- [ ] Load the reference only for explicit RFC intent or persisted RFC-required features and stop after presenting each draft RFC for human approval.
- [ ] Keep plan and verification consequences in their existing shared owners without copying the RFC body contract.
- [ ] Preserve exact four-skill discovery and validate the new reference path as a package contract.

## Task 2: Align user guidance, workspace assets, and behavior scenarios

**Outcome:** New workspaces and fresh-context agents apply the optional RFC path consistently without adding ceremony to direct features.
**Files:**
- Modify: `skills/using-superplan/assets/human/features.md`
- Modify: `README.md`
- Verify: `docs/install.md`
- Modify: `tests/behavior/workflow.md`
- Modify: `tests/scripts/test_init_workspace.py`

**Change Map:**
- Feature asset: document optional `requires_rfc`, exact flat RFC path, and the two approval gates for newly initialized workspaces while preserving existing user-owned registries during migration.
- README: explain direct and RFC-backed feature flows, selection precedence, Chinese default, version meaning, Git revision history, and the separation between RFC approval and plan approval without expanding installation instructions unnecessarily.
- Behavior scenarios: cover explicit RFC request, autonomous high-risk selection with stated reasons, large-but-bounded direct feature, explicit decline with material-risk reconfirmation, Chinese default and language override, flat qualified-id path, draft approval pause, plan gate, approved material revision with version increment, and omission of per-conversation logs.
- Initialization tests: prove fresh workspaces receive updated feature guidance while compatible existing human files remain byte-for-byte preserved and schema `1` remains current.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- Execute the applicable RFC scenarios from `tests/behavior/workflow.md` in fresh contexts
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `git diff --check -- skills/using-superplan/assets/human/features.md README.md docs/install.md tests/behavior/workflow.md tests/scripts/test_init_workspace.py`

- [ ] Teach new workspaces the optional field and two-stage approval without modifying established registries during migration.
- [ ] Document only user-visible RFC behavior and keep setup documentation unchanged unless inspection finds a concrete mismatch.
- [ ] Prove agent judgment, language, path, version, revision, pause, and direct-feature behavior through action-based scenarios.
- [ ] Preserve workspace schema and initialization idempotency.

## Task 3: Publish, verify, and complete F019

**Outcome:** The optional RFC workflow ships as one compatible minor release with complete state and isolated delivery evidence.
**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `AGENTS.md` (managed generator-version marker only)
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F019/02-rfc-workflow-guidance-and-release.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Release surfaces: synchronize the canonical runtime, Codex/Claude manifests, marketplace, package assertion, managed workspace marker, and current README example to exact base version `0.5.0`, preserving B004's optional Codex build-metadata rule and workspace schema `1`.
- Final evidence: run focused checks during integration and `python3 tools/verify_repo.py` once after scripts, skills, references, assets, docs, scenarios, versions, and generated artifacts stabilize.
- Completion: mark F019-02 complete only after F019-01 is complete; confirm RFC version 1 remains approved; then transition F019 to done, refresh the index, inspect exact status/diff, and create an `F019-02` commit containing only the remaining feature and progress paths.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- Search current release surfaces for stale `0.4.1` while preserving historical evidence
- `git diff --check`
- `git status --short`

- [ ] Synchronize active release surfaces at `0.5.0` while preserving schema `1`, historical records, and optional Codex build metadata.
- [ ] Obtain current package, behavior, workspace, RFC, plan, full-regression, diff, and status evidence.
- [ ] Complete F019-02 after F019-01, set F019 done only when both plans are complete, and refresh the generated index.
- [ ] Create a dedicated commit whose message includes `F019-02` and excludes unrelated changes.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/rfcs/F019.md`
- `docs/superplan/plans/features/F013-integrate-workflow-guidance-into-superplan.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `docs/superplan/plans/features/F018-release-superplan-0-4-1.md`
- `docs/superplan/plans/features/F019/01-rfc-state-model-and-enforcement.md`
- `skills/feature-plan-and-delivery/SKILL.md`
- `skills/using-superplan/references/plan-spec.md`
- `skills/using-superplan/references/verification-matrix.md`
