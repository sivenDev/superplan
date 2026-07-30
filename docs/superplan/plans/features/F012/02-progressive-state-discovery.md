---
id: "F012-02"
title: "Progressive Human and Plan State Discovery"
type: "feature"
status: "approved"
summary: "Add token-efficient human and plan discovery while preserving global validation and complete related-plan understanding."
source: "docs/superplan/human/features.md"
created: "2026-07-30"
depends_on: ["F012-01"]
parent: "F012"
---
# Progressive Human and Plan State Discovery Plan

**Goal:** Keep Superplan accurate in large repositories without loading cumulative human and plan history into every agent context.
**Scope:** Add deterministic human-request summary, listing, exact-entry, status-update, and validation commands; add compact plan catalog and candidate-discovery modes that preserve global metadata validation and full-text review of genuinely related plans; revise route and guardrail guidance to use progressive discovery; and finish organizing the reduced workspace script set around clear public responsibilities while retaining the existing recorder path as a compatibility adapter.
**Non-Goals:** Do not archive or migrate existing human entries, convert requests or plans to one-file-per-entry storage, add vector search or another database, remove historical completed plans from discovery, weaken approval or workspace-safety gates, change plan frontmatter, merge remaining scripts into a monolith, or remove the current recorder CLI in this release.
**Architecture:** Make local scripts scan complete registries and plan metadata without emitting their full contents into agent context. Keep global integrity checks deterministic across every plan, then let agents inspect a compact catalog, search all statuses for source/dependency/scope/artifact candidates, and read the full changed plan plus the resulting related closure. Add `human_requests.py` as the canonical request interface while retaining `record_human_request.py` as a thin compatibility entry point. Keep the remaining top-level scripts aligned to distinct workspace responsibilities; F012-01's removal of profile/install scripts supplies the primary inventory reduction, so do not introduce an internal package solely to reduce visible file count.
**Baseline:** `layout-doctor` has about 121 KB of human registries and 1.26 MB of plan Markdown, while normal Superplan guidance still says to read the matching human source. The generated plan index exposes ID, title, status, date, and path but not enough compact source/dependency/summary context to select related plans reliably. The request recorder only appends and numbers entries, and plan validation only extracts human IDs, so malformed or stale human statuses are not surfaced deterministically. After F012-01, runtime scripts no longer carry the profile installation subsystem, leaving a small workspace-focused set that should be clarified rather than mechanically re-split.
**Exit Criteria:** Normal feature and bug routing can understand current progress and select an existing request without reading an entire registry; plan creation inspects a complete compact catalog, runs global integrity validation, searches all statuses for related candidates, and loads full text only for the changed and related closure; large-fixture tests prove bounded output and exact retrieval; human validation reports missing/unknown statuses and duplicate IDs without silently rewriting history; status updates and worktree-qualified numbering retain existing contracts; existing recorder calls continue to work; remaining scripts have one clear workspace responsibility each; the managed guardrail and route references state the progressive discovery contract concisely; and focused tests, the full script suite, skill validation, behavior scenarios, guardrail synchronization, plan-index validation, and diff checks pass.

## Task 1: Add deterministic progressive access to human requests

**Outcome:** Agents and humans can inspect active request state, retrieve one exact entry, update its status, and validate registry structure without loading or manually editing the complete Markdown file.
**Files:**
- Create: `skills/using-superplan/scripts/human_requests.py`
- Modify: `skills/using-superplan/scripts/record_human_request.py`
- Modify: `tests/scripts/test_record_human_request.py`
- Create: `tests/scripts/test_human_requests.py`
- Modify: `skills/using-superplan/references/intake-spec.md`
- Modify: `skills/feature-plan-and-delivery/SKILL.md`
- Modify: `skills/bugfix-plan-and-delivery/SKILL.md`

**Change Map:**
- `human_requests.py`: own parsing and expose concise `summary`, filtered `list`, exact `show`, `record`, `set-status`, and `validate` operations with stable plain-text output suitable for agent context.
- Request updates: preserve bodies byte-for-byte outside the explicitly updated entry, support qualified IDs, and report duplicate IDs, missing fields, and unknown statuses precisely.
- Compatibility recorder: retain its current arguments and output while delegating record behavior to the canonical request module.
- Intake and route guidance: require summary/exact retrieval for normal routing and reserve complete-file reads for registry repair or genuinely cross-entry analysis.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_record_human_request.py'`
- Human request CLI help plus large-registry summary/show/validate smoke fixtures
- `git diff --check -- skills/using-superplan/scripts skills/feature-plan-and-delivery skills/bugfix-plan-and-delivery tests/scripts`

- [ ] Cover active and all-status listing, exact qualified-ID retrieval, status transitions, validation errors, duplicate detection, and unchanged unrelated Markdown.
- [ ] Keep large-registry summary output proportional to active metadata rather than total historical body size.
- [ ] Preserve current numbering and linked-worktree qualification behavior through the compatibility recorder.

## Task 2: Preserve plan understanding through compact global discovery and related-plan closure

**Outcome:** Structural plan work retains global integrity and semantic context without treating all plan bodies as mandatory context.
**Files:**
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `tests/scripts/test_generate_plans_readme.py`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/references/plan-spec.md`
- Modify: `skills/using-superplan/assets/agents-guardrails.md`
- Modify: `tests/scripts/test_sync_agents_guardrails.py`
- Modify: `tests/behavior/workflow.md`
- Modify: `AGENTS.md` (managed block only)

**Change Map:**
- Plan tooling: add compact catalog and filters for active status, source ID, dependencies, and text/artifact candidates while continuing to validate all plan metadata, dependencies, cycles, source IDs, and completion ordering.
- Delivery and plan specifications: define related plans as the changed plan plus source siblings, dependency closure, overlapping scope/artifact/search candidates, expanding when newly read plans reveal more relationships; search all statuses rather than only active plans.
- Managed guardrail: require complete catalog inspection and deterministic global validation for structural changes, followed by full-text review of the discovered related closure; retain local validation for routine progress edits and keep the F012-01 schema marker intact.
- Behavior scenarios: prove that large completed history is searched through compact metadata/candidates, relevant completed plans are still read, and unrelated plan bodies are not loaded ceremonially.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_sync_agents_guardrails.py'`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- Applicable large-plan behavior scenarios from `tests/behavior/workflow.md`

- [ ] Emit enough compact metadata to identify source, dependency, summary, status, and path relationships without emitting every plan body.
- [ ] Keep global validation exhaustive and semantic full-text review iterative over the complete related closure.
- [ ] Make the injected guardrail concise while leaving operational detail in canonical references.

## Task 3: Verify and deliver F012-02 as a focused workspace change

**Outcome:** Progressive discovery is regression-safe, installed-skill valid, and committed independently after the bundled runtime transition.
**Files:**
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Review F007-F010 and both F012 plans together so concise instruction ownership, workflow-state reuse, numbering composition, bundled initialization, and progressive discovery remain compatible.
- Run focused checks during implementation and one full script regression after behavior stabilizes; then update human/plan progress and regenerate the index without rerunning unchanged implementation checks.
- Stage only F012-02 paths and the managed `AGENTS.md` hunk, preserving unrelated memory metadata.

**Verification:**
- `python3 -m unittest discover -s tests/scripts`
- Validate all bundled skill folders with `quick_validate.py`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`
- `git status --short`

- [ ] Obtain current script, skill, progressive-discovery, guardrail, and plan-integrity evidence.
- [ ] Mark F012-02 and its human entry complete only after both F012 plans have passed their exit criteria.
- [ ] Create a dedicated F012-02 commit with exact task paths.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F007-streamline-superplan-skills.md`
- `docs/superplan/plans/features/F008-optimize-workflow-state-and-verification.md`
- `docs/superplan/plans/features/F009-optimize-runtime-skill-structure.md`
- `docs/superplan/plans/features/F010-clarify-worktree-numbering-composition.md`
- `docs/superplan/plans/features/F012/01-bundled-superpowers-and-versioned-workspace.md`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/intake-spec.md`
- `skills/using-superplan/references/plan-spec.md`
- `skills/using-superplan/references/verification-matrix.md`
