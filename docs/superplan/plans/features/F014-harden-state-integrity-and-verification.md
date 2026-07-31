---
id: "F014"
title: "Harden Superplan State Integrity and Verification"
type: "feature"
status: "complete"
summary: "Enforce canonical human-plan invariants, make workflow mutations transaction-safe, and provide one automated repository verification path."
source: "docs/superplan/human/features.md"
created: "2026-07-31"
depends_on: ["F012-02", "B003"]
parent: ""
---
# Harden Superplan State Integrity and Verification Plan

**Goal:** Prevent valid-looking but contradictory workflow state and make repository mutations and release checks fail safely.
**Scope:** Reuse one strict human-registry model from plan and request tooling; reject invalid human/plan lifecycle combinations during global validation; protect registry, workspace, guardrail, and plan-index writes with a shared mutation lock, source preconditions, atomic replacement, and multi-file recovery; and add one standard-library repository verification command used by CI and documentation.
**Non-Goals:** Do not change request or plan schemas, add statuses, introduce a database or vector search, build a full model-behavior evaluation harness, shorten skills without a behavioral reason, or split scripts merely by file size.
**Architecture:** Extract only the human-registry parsing/model boundary needed to remove the current plan/request validation asymmetry. Keep plan parsing in `generate_plans_readme.py` and make its global validator enforce cross-artifact invariants: a `proposed` request may have no non-superseded plan, while a `done` request must have at least one non-superseded plan and all such plans must be `complete`; `accepted` remains valid before, during, or immediately after plan execution. Add one standard-library safe-write module that owns a per-worktree mutation lock, compares every preflight source, stages UTF-8 content beside its destination, atomically replaces files while preserving existing modes, and restores earlier replacements when a later batch write fails. Repository verification remains development-only under `tools/` and invokes public CLIs instead of duplicating their rules.
**Baseline:** Registry validation is strict but isolated inside `human_requests.py`; plan validation reads only matching human IDs, so malformed registries or manual lifecycle drift can still pass plan-index checks. `record`, `set-status`, workspace migration, guardrail sync, and plan-index generation use direct `write_text()` calls; B003 alone has source rechecks and rollback for its two-registry migration. The full 79-test suite passes, but the repository has no CI and contributors must compose several validation commands manually.
**Exit Criteria:** Global plan/index validation rejects malformed source registries, non-superseded plans for `proposed` requests, and `done` requests with no deliverable plan or any incomplete sibling while allowing valid transient `accepted` state; all public workflow mutations reject changed preflight sources, avoid torn single-file writes, and recover earlier files after an injected later write failure; concurrent intake cannot silently overwrite another request; initialization remains idempotent and preserves human/non-managed content; one documented command runs the complete repository contract locally and in GitHub Actions on the supported Python range; version metadata is synchronized for the feature release; and focused tests, full verification, plan/index checks, diff review, and an isolated F014 commit pass.

## Task 1: Enforce one canonical human-plan state model

**Outcome:** Every global plan check validates both registry structure and the lifecycle relationship between a request and all related deliverable plans.
**Files:**
- Create: `skills/using-superplan/scripts/human_registry.py`
- Modify: `skills/using-superplan/scripts/human_requests.py`
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `tests/scripts/test_human_requests.py`
- Modify: `tests/scripts/test_generate_plans_readme.py`

**Change Map:**
- `human_registry.py`: own request status constants, entry parsing/data, date validation, and strict registry loading without importing plan tooling.
- `human_requests.py`: consume the shared model while retaining current CLI output, byte-preserving entry edits, migration inference, and compatibility behavior.
- `generate_plans_readme.py`: replace regex-only source lookup with strict registry loading and validate the proposed/accepted/done invariants against all non-superseded plans sharing a source id.
- Focused tests: capture malformed-source, proposed-with-plan, done-without-plan, incomplete-sibling, superseded-only, valid accepted, and all-complete cases without weakening existing id/dependency checks.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- Disposable CLI checks for each cross-artifact status combination

- [x] Preserve the existing request CLI and legacy-migration contracts while moving only the shared parsing boundary.
- [x] Make global validation reject contradictory persisted state with exact request and plan identifiers.
- [x] Keep `accepted` as the valid transitional state around approved plan execution and completion metadata updates.

## Task 2: Make workflow mutations concurrency- and failure-safe

**Outcome:** Public Superplan write commands either apply their complete preflighted update or fail without silently discarding external work.
**Files:**
- Create: `skills/using-superplan/scripts/safe_writes.py`
- Modify: `skills/using-superplan/scripts/human_requests.py`
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `skills/using-superplan/scripts/init_workspace.py`
- Modify: `skills/using-superplan/scripts/sync_agents_guardrails.py`
- Create: `tests/scripts/test_safe_writes.py`
- Modify: `tests/scripts/test_human_requests.py`
- Modify: `tests/scripts/test_generate_plans_readme.py`
- Modify: `tests/scripts/test_init_workspace.py`
- Modify: `tests/scripts/test_sync_agents_guardrails.py`

**Change Map:**
- `safe_writes.py`: provide the shared lock and text-update transaction boundary with missing-file preconditions, atomic same-directory replacement, mode preservation, deterministic cleanup, and rollback reporting.
- Request mutations: hold the lock across read/validate/id-or-status calculation/write so competing intake or lifecycle commands cannot lose an update; delegate legacy migration to the same batch boundary.
- Workspace and generated artifacts: precompute missing human assets, managed `AGENTS.md`, and plan index content before one batch write; route generator and guardrail writes through the same single-file transaction behavior.
- Failure tests: simulate source changes after preflight, competing record operations, second-file replacement failure, rollback failure reporting, and idempotent no-op paths while proving no tracked lock/temp artifacts remain.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_safe_writes.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_init_workspace.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_sync_agents_guardrails.py'`

- [x] Serialize mutation decisions at the workspace boundary instead of checking only after IDs or content have been calculated.
- [x] Make all replacements atomic and detect any source that changed after preflight.
- [x] Preserve current content, permissions, idempotency, and actionable rollback errors across injected failures.

## Task 3: Add one authoritative repository verification path

**Outcome:** Local contributors and CI run the same deterministic contract without remembering or silently omitting individual checks.
**Files:**
- Create: `tools/verify_repo.py`
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `skills/using-superplan/references/verification-matrix.md`
- Modify: `tests/scripts/test_plugin_package.py`

**Change Map:**
- `tools/verify_repo.py`: run the full script suite, Python compilation, workspace compatibility, human registry validation, guardrail synchronization check, plan-index check, and Git whitespace validation with clear fail-fast command reporting.
- GitHub Actions: invoke only the canonical verification command on the declared minimum and current Python versions without adding third-party runtime dependencies.
- Documentation/package contract: make the single command authoritative, state the supported Python range, and test that CI and docs reference the repository-owned entry point.

**Verification:**
- `python3 tools/verify_repo.py`
- Inspect the workflow command and Python matrix against the documented contract

- [x] Keep verification standard-library-only and read-only except inside disposable test fixtures.
- [x] Ensure a missing test subtree or failed sub-check cannot report success.
- [x] Use the same command in README, the verification matrix, and CI.

## Task 4: Verify, publish, and deliver F014

**Outcome:** The integrity hardening ships as one traceable feature without absorbing unrelated workspace state.
**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `AGENTS.md` (managed generator-version marker only if required)
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Release metadata: publish the feature as `0.4.0`, keep workspace schema `1`, synchronize manifests/tests, and change only the managed `AGENTS.md` marker if exact generated validation requires it.
- Final evidence: run focused tests during implementation and the canonical full verification once after behavior stabilizes; then update plan/human/index metadata without rerunning unchanged implementation checks.
- Delivery: review exact diffs, preserve the existing non-managed memory timestamp, stage only F014 paths and any required managed hunk, and create a dedicated commit containing `F014` in its message.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Synchronize `0.4.0` metadata without changing workspace schema or unrelated instructions.
- [x] Complete the plan before transitioning F014 to `done` and refresh the index once.
- [x] Commit only the approved F014 implementation, tests, documentation, and progress artifacts.

## Implementation Evidence

- Canonical registry parsing and global lifecycle validation reject malformed or contradictory request/plan state while preserving accepted transitional state and legacy recovery compatibility.
- Shared locking and preconditioned atomic transactions cover request recording/status changes, legacy migration, initialization, guardrail synchronization, and plan-index generation; injected concurrency, replacement, rollback, and staging-window failures have regression coverage.
- `python3 tools/verify_repo.py` passed on Python 3.14 with 94 tests, isolated compilation of 18 Python files, workspace/registry/guardrail/index validation, and `git diff --check`; CI runs the same command on Python 3.10 and 3.14.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F003-worktree-aware-request-numbering.md`
- `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- `docs/superplan/plans/bugs/B002-resolve-skill-routing-and-validation-gaps.md`
- `docs/superplan/plans/bugs/B003-add-safe-legacy-registry-migration.md`
- `skills/using-superplan/scripts/human_requests.py`
- `skills/using-superplan/scripts/generate_plans_readme.py`
- `skills/using-superplan/scripts/init_workspace.py`
- `skills/using-superplan/references/verification-matrix.md`
