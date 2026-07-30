---
id: "B003"
title: "Add Safe Legacy Registry Migration"
type: "bugfix"
status: "complete"
summary: "Add an explicit evidence-backed migration for legacy human requests missing status or created metadata."
source: "docs/superplan/human/bugs.md"
created: "2026-07-31"
depends_on: ["B002"]
parent: ""
---
# Add Safe Legacy Registry Migration Plan

**Goal:** Let older Superplan registries become valid without weakening normal validation or silently inventing request history.
**Scope:** Add `human_requests.py migrate-legacy --check` and `--write` for feature and bug entries that are missing only `status` and/or `created`; preview every proposed value with its evidence, write only when every selected entry is resolvable, and preserve all existing registry bytes outside the inserted metadata.
**Non-Goals:** Do not make `record` tolerate invalid registries, automatically migrate during `init_workspace`, change request or workspace schemas, repair duplicate IDs or malformed/unknown fields, rewrite request titles or bodies, add another runtime script, or infer dates without repository evidence.
**Architecture:** Treat this as a high-risk data-integrity repair. Keep the canonical parser strict and add a migration-specific preflight that classifies missing `status`/`created` as repairable while rejecting every other registry issue. Reuse validated plan metadata for status and date evidence, then fall back to Git only for the first appearance date. Build all edits in memory before either registry is written so unresolved evidence or a write precondition cannot leave a partial migration. Keep workspace initialization structural and keep human-history migration explicit.
**Baseline:** `record_request()` validates the complete target registry before appending. A historical entry without `status` or `created` therefore blocks every later request with only `registry validation failed; run human_requests.py validate`. `init_workspace.py --migrate` deliberately preserves human files, and no current command can safely preview or repair the legacy metadata.
**Reproduction:** Create a valid feature registry except for one historical entry missing `status` and `created`, then run `human_requests.py record --type feature ...`; validation reports both missing fields and the recorder exits without adding the new request. The only available recovery is manual registry editing.
**Root Cause:** F012-02 correctly made registry validation strict but provided no bounded migration path for entries created before the metadata contract. The recorder consequently treats recoverable legacy omissions and unsafe structural corruption as the same blocking state.
**Exit Criteria:** A no-write check reports each affected ID, proposed field value, and evidence source; status inference follows related non-superseded plan state; created inference uses the earliest related plan date and otherwise the Git first-appearance date; unresolved evidence or any non-legacy validation issue blocks all writes; successful migration changes only missing metadata and makes strict validation and subsequent recording pass; current registries remain unchanged; normal record and workspace migration behavior remain strict; version metadata reports `0.3.2` with workspace schema `1`; focused migration tests, full script regression, behavior scenarios, workspace/package/plan validation, diff review, and an isolated B003 commit pass.

## Task 1: Add an atomic evidence-backed legacy migration command

**Outcome:** Historical missing metadata can be previewed and repaired without masking unrelated corruption or changing existing request content.
**Files:**
- Modify: `skills/using-superplan/scripts/human_requests.py`
- Modify: `tests/scripts/test_human_requests.py`

**Change Map:**
- `human_requests.py`: add the `migrate-legacy` command with explicit `--check` and `--write` modes; separate repairable missing-field findings from blocking validation issues while leaving `validate`, `record`, `show`, and `set-status` strict.
- Evidence inference: derive `done` when all related non-superseded plans are complete, `accepted` when any such plan is active, and `proposed` when no deliverable plan exists; derive `created` from the earliest related plan date, then the Git date when that exact request heading first appeared, otherwise report unresolved.
- Write boundary: validate plan metadata, preflight all selected feature/bug edits, report deterministic field/value/evidence rows, reject ambiguous or unresolved migrations without writing, and insert only missing metadata while preserving every pre-existing byte.
- Focused tests: cover dry-run immutability, current registries, mixed missing fields, each status branch, plan-date and Git-date evidence, unavailable Git evidence, blocking registry errors, multiple registries, atomic failure, idempotent write, byte preservation, and strict post-migration record behavior.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- Run `migrate-legacy --check` and `--write` against isolated legacy Git and non-Git fixtures.
- `git diff --check -- skills/using-superplan/scripts/human_requests.py tests/scripts/test_human_requests.py`

- [x] Capture the current blocked-record behavior and no-safe-repair gap as focused failing tests.
- [x] Implement one preflight/inference/edit pipeline with no partial writes.
- [x] Prove existing metadata, bodies, headings, unrelated entries, and strict commands are unchanged.

## Task 2: Document the explicit recovery path at its decision points

**Outcome:** Agents and users can recover a legacy registry without confusing semantic human-history repair with workspace artifact migration.
**Files:**
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/using-superplan/references/intake-spec.md`
- Modify: `tests/behavior/workflow.md`
- Modify: `README.md`

**Change Map:**
- Route and intake guidance: when strict validation fails only because legacy entries lack `status`/`created`, preview with `migrate-legacy --check` and use the explicit write mode after workspace safety; keep all other validation failures in manual repair.
- Boundary wording: state concisely that `init_workspace --migrate` never performs this semantic migration and `record` never invokes it automatically.
- Behavior and user docs: add exact recovery commands plus actionable, unresolved, blocking-error, and successful-post-validation scenarios without duplicating the inference algorithm across skill files.

**Verification:**
- Exercise the legacy-registry behavior scenarios in `tests/behavior/workflow.md`.
- `python3 -m unittest discover -s tests/scripts -p 'test_plugin_package.py'`
- `git diff --check -- skills/using-superplan/SKILL.md skills/using-superplan/references/intake-spec.md tests/behavior/workflow.md README.md`

- [x] Make the repair command discoverable only where legacy validation failure is handled.
- [x] Keep the runtime guidance concise and preserve the strict initialization/request boundaries.

## Task 3: Publish and deliver B003 as a patch release

**Outcome:** The migration ships with synchronized package metadata, current generated artifacts, complete evidence, and no unrelated user state.
**Files:**
- Modify: `.codex-plugin/plugin.json`
- Modify: `.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `skills/using-superplan/scripts/superplan_version.py`
- Modify: `tests/scripts/test_plugin_package.py`
- Modify: `AGENTS.md` (managed generator-version marker only)
- Modify: `docs/superplan/human/bugs.md`
- Modify: `docs/superplan/plans/bugs/B003-add-safe-legacy-registry-migration.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Version contract: synchronize plugin surfaces at `0.3.2`, retain workspace schema `1`, and refresh only the managed generator marker required by exact workspace validation.
- Final evidence: run the focused tests during implementation, one full script regression after behavior stabilizes, package/version validation, workspace compatibility, behavior scenarios, plan/index checks, and exact diff/status review.
- Progress and delivery: complete the B003 plan before setting its human entry to `done`, regenerate the index, stage only B003 paths and the managed `AGENTS.md` hunk, preserve the memory timestamp, and create a dedicated B003 commit.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- `python3 skills/using-superplan/scripts/init_workspace.py --check --root .`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [x] Synchronize patch-version metadata without changing workspace schema or non-managed guardrails.
- [x] Obtain current focused, regression, behavior, package, compatibility, plan, diff, and status evidence.
- [x] Complete progress and create an isolated B003 commit that excludes the user-owned memory timestamp.

## Implementation Evidence

- Migration TDD: five new CLI scenarios initially failed because `migrate-legacy` was absent. The final focused module passes 18 tests covering dry-run immutability, exact byte preservation, plan-state status inference, plan/Git date evidence, unresolved and malformed registries, cross-registry no-write behavior, rollback after a simulated later write failure, idempotency, and strict recording before repair.
- Integrity boundaries: migration preflights the complete selected registry set, rejects every non-missing-field issue, validates the plan set before using it as evidence, validates the fully rendered registries before writing, rechecks source bytes, and rolls back earlier writes if a later registry write fails. `init_workspace` remains structural and `record` remains strict while pointing legacy failures to the preview command.
- Documentation and release: the route entry, intake reference, README, and behavior scenarios document the explicit recovery path without duplicating the inference algorithm. Codex, Claude, marketplace, runtime, README, and managed workspace markers report `0.3.2`; workspace schema remains `1`, and only the managed AGENTS marker belongs to B003.
- Final evidence: `python3 -m unittest discover -s tests/scripts` passed 79 tests; `py_compile`, current-registry preview, strict registry validation, workspace compatibility, guardrail sync, plan-index write/check, repository plugin validation under the existing Python 3.12 PyYAML environment, all four skill validations, and `git diff --check` passed.

## References
- `docs/superplan/human/bugs.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F012/01-bundled-superpowers-and-versioned-workspace.md`
- `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- `docs/superplan/plans/bugs/B002-resolve-skill-routing-and-validation-gaps.md`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/intake-spec.md`
- `skills/using-superplan/references/plan-spec.md`
- `skills/using-superplan/scripts/human_requests.py`
- `skills/using-superplan/scripts/generate_plans_readme.py`
