---
id: "F022"
title: "Support Multiple RFCs per Feature"
type: "feature"
status: "complete"
summary: "Support backward-compatible single and multi-RFC feature layouts with deterministic identity, approval, and plan-reference validation."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F019-02"]
parent: ""
---
# Support Multiple RFCs per Feature Plan

**Goal:** Let one RFC-backed feature use multiple independently versioned design documents without breaking existing flat RFCs or weakening feature-level approval and traceability gates.
**Scope:** Add mutually exclusive flat and feature-directory RFC layouts; give directory RFCs stable `RNN` identities and explicit feature ownership; validate directory, filename, metadata, branch-qualified identity, approval sets, completion, and exact plan references; update route-owned RFC guidance, shared plan consequences, workspace guidance, README, behavior scenarios, and regression coverage. Existing flat RFCs and their plan references remain valid without migration.
**Non-Goals:** Do not require multiple RFCs, migrate existing RFCs, add RFC dependency graphs or partial-approval implementation, create an RFC catalog or request type, change feature/plan lifecycle states, bump the package version, publish a release, push a remote, or refresh a local installation.
**Architecture:** Replace the one-RFC-per-feature lookup with an RFC document model carrying `feature_id` and a validator-produced mapping from feature id to an ordered RFC set. Preserve the flat parser branch exactly for backward compatibility. Directory RFCs live one level below `rfcs/<feature-id>/`, require `NN-<slug>.md`, `id: <feature-id>-RNN`, and `feature: <feature-id>`, and cannot coexist with `<feature-id>.md`. Cross-artifact validation requires all discovered RFCs for an RFC-backed feature to be approved before any non-superseded plan or feature completion; flat plans retain their exact single reference, while directory-mode plans must contain at least one exact member reference. Keep selection and document-shape guidance in the feature route reference and only shared plan consequences in `plan-spec.md`.
**Baseline:** F019 introduced a flat RFC contract at `docs/superplan/rfcs/<feature-id>.md`. `rfc_documents.py` rejects every nested Markdown file, requires RFC id to equal the filename stem, and returns a flat document list. `generate_plans_readme.py` collapses that list into one RFC per feature and requires every RFC-backed plan to reference the one computed flat path. Package guidance, initialized feature instructions, README text, and tests lock this one-to-one behavior. F022's approved RFC defines a backward-compatible dual-layout replacement.
**Exit Criteria:** Existing flat and branch-qualified RFC fixtures still pass unchanged; valid feature directories with one or more `NN-<slug>.md` RFCs validate; directory RFC id, feature, number, path, source, status, version, and ownership mismatches fail deterministically; flat/directory conflicts and deeper nesting fail; all RFCs must be approved before plans or completion; each directory-mode plan has at least one exact direct RFC reference; guidance consistently describes when and how to use multi-RFC mode; focused tests, behavior scenarios, workspace compatibility, complete repository verification, plan-index validation, and diff/status checks pass; F022 is committed separately and marked done without publishing a release.

## Task 1: Generalize RFC discovery and document identity

**Outcome:** RFC discovery accepts the approved dual layout and returns deterministic feature-grouped documents while preserving every valid flat RFC behavior.
**Files:**
- Modify: `skills/using-superplan/scripts/rfc_documents.py`
- Modify: `tests/scripts/test_generate_plans_readme.py`

**Change Map:**
- `RFCDocument` and parsing helpers: expose canonical `feature_id`, layout, sequence, and path identity needed by cross-artifact validation without duplicating request ownership rules.
- Flat parsing: preserve `id == feature id == filename stem`, existing required keys, statuses, version/source/date validation, and branch-qualified ids.
- Directory parsing: accept only `rfcs/<feature-id>/NN-<slug>.md`; require one-level nesting, lowercase kebab-case slug, positive two-or-more-digit sequence, exact `<feature-id>-RNN` RFC id, explicit matching `feature`, and all shared metadata.
- Discovery: reject mixed flat/directory layouts, deeper Markdown nesting, duplicate RFC ids or sequences, and inconsistent feature directories with deterministic path-first errors; return stable path ordering.
- Parser tests: retain existing flat fixtures and cover valid multi-document, single-member directory staging, branch-qualified ids, bad names, mismatched numbers/features/ids, duplicate identities, layout conflicts, and deeper nesting.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- Disposable flat and directory RFC fixtures through `generate_plans_readme.py --catalog`
- `git diff --check -- skills/using-superplan/scripts/rfc_documents.py tests/scripts/test_generate_plans_readme.py`

- [x] Extend the document model and parser without changing valid flat RFC inputs.
- [x] Discover only the two approved layouts and reject ambiguous or malformed directory structures.
- [x] Enforce directory RFC feature identity, `RNN` identity, filename sequence, and branch-qualified ownership.
- [x] Add focused compatibility and invalid-state regression coverage.

## Task 2: Enforce feature-level approval sets and direct plan references

**Outcome:** Global validation applies complete RFC approval gates while letting each directory-mode plan reference only its direct design inputs.
**Files:**
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `tests/scripts/test_generate_plans_readme.py`
- Modify: `tests/scripts/test_human_requests.py`

**Change Map:**
- RFC ownership validation: group RFCs by `feature_id`; reject orphan, direct-feature, proposed-owner, and duplicate/mixed states across the complete set.
- Plan gate: require at least one matching RFC and require every matching RFC to be approved before accepting any non-superseded plan.
- Reference gate: keep the exact flat-path requirement for flat mode; in directory mode require every non-superseded plan to reference at least one exact member path inside its `References` section without requiring unrelated RFCs.
- Completion boundary: reuse grouped approval validation when `set-status ... done` checks RFC-backed features; preserve accepted no-plan transitional states and superseded-plan behavior.
- Tests: cover missing, mixed draft/approved, all-approved, unrelated/malformed references, plans referencing different direct RFC subsets, branch-qualified sets, and done-state refusal/acceptance.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- Disposable CLI completion fixtures for flat and directory RFC modes
- `git diff --check -- skills/using-superplan/scripts/generate_plans_readme.py tests/scripts/test_generate_plans_readme.py tests/scripts/test_human_requests.py`

- [x] Replace the singular RFC lookup with deterministic feature-grouped validation.
- [x] Require all matching RFCs to be approved before plans and completion.
- [x] Preserve flat exact-reference behavior and add directory direct-reference validation.
- [x] Prove normal features, flat RFCs, qualified ids, superseded plans, and atomic completion remain compatible.

## Task 3: Align concise guidance and shipped workspace behavior

**Outcome:** Agents and new workspaces select and author multi-RFC layouts consistently without adding ceremony to ordinary single-RFC features.
**Files:**
- Modify: `skills/feature-plan-and-delivery/references/rfc-spec.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `skills/using-superplan/assets/human/features.md`
- Modify: `README.md`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `tests/scripts/test_init_workspace.py`
- Modify: `tests/behavior/workflow.md`

**Change Map:**
- RFC spec: state that flat single RFC remains default; allow directory mode only for independently approved/versioned/referenced design boundaries; define paths, directory frontmatter, mutual exclusion, all-approved gate, and plan direct-reference rule concisely.
- Shared references: replace singular exact-path language with layout-aware approval/reference consequences and artifact verification without duplicating the route-owned document contract.
- Workspace asset and README: teach the compatible dual layout and two approval gates while keeping migration byte-preserving for user-maintained human files.
- Package/init tests: lock the authoritative reference, key dual-layout contracts, unchanged four-skill inventory, workspace schema compatibility, preservation, and idempotency.
- Behavior scenarios: cover single-RFC default, justified multi-RFC selection, over-splitting avoidance, draft set approval pause, exact direct plan references, mixed-layout rejection, and approved RFC revision blocking.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- Execute applicable RFC scenarios from `tests/behavior/workflow.md` in fresh contexts
- Inspect all four root skills for unchanged routing boundaries and concise reference ownership
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `git diff --check -- skills/feature-plan-and-delivery skills/using-superplan/references skills/using-superplan/assets/human/features.md README.md tests`

- [x] Keep multi-RFC selection conditional on independent design boundaries and preserve single RFC as the default.
- [x] Synchronize route, shared plan, verification, workspace, and user documentation contracts without repetition.
- [x] Add package, initialization, and behavior coverage for dual layouts and approval pauses.
- [x] Confirm workspace schema `1`, root skill inventory, preservation, and idempotency remain valid.

## Task 4: Verify, complete, and deliver F022

**Outcome:** The multi-RFC capability is regression-safe, traceable, and committed without release or installation side effects.
**Files:**
- Modify: `docs/superplan/plans/features/F022-support-multiple-rfcs-per-feature.md`
- Modify: `docs/superplan/plans/README.md`
- Modify: `docs/superplan/human/features.md`

**Change Map:**
- Run focused tests while each boundary stabilizes, then run `python3 tools/verify_repo.py` once against the final implementation state.
- Validate registry, RFC groups, workspace compatibility, generated plan index, applicable fresh-context scenarios, diff, and exact Git status.
- Mark F022 complete, set its human entry to done through the canonical command, refresh the index without rerunning unchanged implementation tests, and create a dedicated final F022 commit.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/human_requests.py --root . validate`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `git diff --check`
- `git status --short`

**Completion Evidence:** `python3 tools/verify_repo.py` passed 108 tests, compiled 19 Python files, and passed workspace, registry, guardrail, plan-index, and diff checks. Focused RFC/plan, human-request, package, and initialization suites passed; the four root skills and applicable RFC behavior scenarios were inspected against the approved contract.

- [x] Obtain current focused, behavior, full-regression, registry, RFC, workspace, plan-index, diff, and status evidence.
- [x] Mark the plan complete and F022 done only after implementation evidence is final.
- [x] Create a separate final commit containing only F022 delivery changes and no release, remote, or installation mutations.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/rfcs/F022.md`
- `docs/superplan/rfcs/F019.md`
- `docs/superplan/plans/features/F019/01-rfc-state-model-and-enforcement.md`
- `docs/superplan/plans/features/F019/02-rfc-workflow-guidance-and-release.md`
- `skills/using-superplan/scripts/rfc_documents.py`
- `skills/using-superplan/scripts/generate_plans_readme.py`
- `skills/feature-plan-and-delivery/references/rfc-spec.md`
- `skills/using-superplan/references/plan-spec.md`
