---
id: "F019-01"
title: "RFC State Model and Enforcement"
type: "feature"
status: "complete"
summary: "Add backward-compatible RFC metadata, artifact validation, and enforced approval gates to the existing feature lifecycle."
source: "docs/superplan/human/features.md"
created: "2026-08-18"
depends_on: ["F014"]
parent: "F019"
---
# RFC State Model and Enforcement Plan

**Goal:** Give Superplan a machine-enforced optional RFC stage without creating a second request lifecycle or weakening existing feature and plan integrity.
**Scope:** Extend feature request metadata with optional `requires_rfc`, support transactional RFC selection during intake or before planning, parse versioned RFC documents at `docs/superplan/rfcs/<feature-id>.md`, and enforce request/RFC/plan state relationships through global validation and completion checks. The user-visible request remains a feature and existing features without the field continue through the direct path.
**Non-Goals:** Do not add `rfcs.md`, `R` ids, a new plan type, a root RFC skill, RFC body-section parsing, automatic translation, automatic plan generation, per-conversation revision logs, or changes to historical completed requests and plans. Do not publish the package version or agent-facing RFC guidance in this plan.
**Architecture:** Extend the canonical human registry model rather than parsing the field independently in each command. Add one focused RFC document model for flat-path discovery and frontmatter validation, then let the existing plan validator own cross-artifact invariants as established by F014. Treat `requires_rfc` as absent/false by default and provide a monotonic canonical command to enable it before any deliverable plan exists. Validate machine-stable metadata and state gates in code; leave language-specific body quality to the reviewed RFC reference so alternate documentation languages do not require brittle heading parsing.
**Baseline:** `human_registry.py` recognizes only feature/bug identity, status, and creation date; request recording has no RFC selector; compact summary/list output cannot expose RFC routing; every Markdown file under `plans/**` is parsed as an executable plan; no RFC artifact parser exists; and global plan validation currently enforces only human request, plan source, dependency, and completion invariants. F014 supplies shared registry parsing, atomic writes, and global lifecycle validation that this plan extends.
**Exit Criteria:** Existing registries and plans remain valid; new feature intake can persist `requires_rfc: true`; an existing proposed or accepted feature can be marked RFC-required transactionally before plans exist; compact discovery exposes the flag; RFC documents validate exact path/id/source/status/date and positive integer version; orphan, proposed-source, malformed, or mismatched RFCs fail; RFC-required plans fail unless the matching RFC is approved and referenced; RFC-backed completion requires an approved RFC; branch-qualified ids work; focused regressions and the full repository verifier pass; and F019-01 is committed separately while F019 remains accepted.

## Task 1: Extend the canonical feature request model and mutation interface

**Outcome:** RFC selection is backward-compatible, visible through progressive discovery, and written through the existing safe transaction boundary.
**Files:**
- Modify: `skills/using-superplan/scripts/human_registry.py`
- Modify: `skills/using-superplan/scripts/human_requests.py`
- Modify: `tests/scripts/test_record_human_request.py`
- Modify: `tests/scripts/test_human_requests.py`

**Change Map:**
- `human_registry.py`: parse at most one `requires_rfc` field on feature entries, default absence to false, reject invalid booleans or the field on bug entries, and expose the value on `HumanRequest` without changing existing status/date contracts.
- `human_requests.py`: add `record --requires-rfc`; add an idempotent feature-only command that enables RFC before any non-superseded related plan exists; insert or update the field through `safe_writes`; expose `rfc_required` counts in feature summary and a compact RFC marker in list output without emitting request or RFC bodies.
- Request tests: cover default false, explicit true, malformed/duplicate fields, bug rejection, branch-qualified intake, safe enablement for proposed/accepted features, refusal after plan creation, idempotency, exact output, and preservation of unrelated registry bytes.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_record_human_request.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- `python3 skills/using-superplan/scripts/human_requests.py --help`
- `git diff --check -- skills/using-superplan/scripts/human_registry.py skills/using-superplan/scripts/human_requests.py tests/scripts/test_record_human_request.py tests/scripts/test_human_requests.py`

- [x] Add one optional feature-only RFC field with absence-as-false compatibility and strict duplicate/value validation.
- [x] Persist RFC selection during recording and through one monotonic pre-plan mutation command using the existing workspace lock and atomic writes.
- [x] Make summary and list output expose RFC-required state compactly while keeping exact `show` behavior and request bodies unchanged.
- [x] Prove normal features, bugs, qualified ids, rejected mutations, idempotency, and unrelated Markdown preservation.

## Task 2: Validate RFC artifacts and enforce the RFC approval gate

**Outcome:** Repository validation rejects every contradictory feature/RFC/plan state and accepts the approved RFC-backed lifecycle.
**Files:**
- Create: `skills/using-superplan/scripts/rfc_documents.py`
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`
- Modify: `tests/scripts/test_generate_plans_readme.py`
- Modify: `tests/scripts/test_human_requests.py`

**Change Map:**
- `rfc_documents.py`: discover only flat `docs/superplan/rfcs/*.md` artifacts; parse required frontmatter; require exact filename/id matching including qualified ids, feature source, valid date, `draft|approved` status, and a positive integer version; return deterministic validation errors without interpreting language-specific body headings.
- `generate_plans_readme.py`: integrate RFC documents into global validation; reject unknown/orphan RFC ids, RFCs for non-feature or non-required requests, RFCs attached to proposed requests, and RFC-required plans without an approved matching RFC or exact RFC reference; allow accepted RFC-required requests to exist transiently before a plan; require approved RFC state for `done` requests.
- Completion boundary: ensure `human_requests.py set-status ... done` inherits the same RFC checks through canonical plan validation rather than duplicating source-id or artifact rules.
- Focused tests: cover missing/draft/approved RFCs, malformed metadata, zero/non-integer versions, mismatched filenames and sources, qualified ids, exact plan references, proposed/accepted/done combinations, normal-feature compatibility, and superseded plan behavior.

**Verification:**
- `python3 -m unittest discover -s tests/scripts -p 'test_generate_plans_readme.py'`
- `python3 -m unittest discover -s tests/scripts -p 'test_human_requests.py'`
- Disposable CLI fixtures for direct features and RFC-required draft/approved/completion states
- `git diff --check -- skills/using-superplan/scripts/rfc_documents.py skills/using-superplan/scripts/generate_plans_readme.py tests/scripts/test_generate_plans_readme.py tests/scripts/test_human_requests.py`

- [x] Parse the approved flat-file RFC contract without adding RFC files to the executable plan index.
- [x] Enforce feature ownership, exact ids and paths, positive integer versions, valid status/source/date metadata, and branch-qualified identity.
- [x] Block implementation plans until RFC approval and require each RFC-backed plan to reference the exact RFC document.
- [x] Keep accepted no-plan state valid, preserve direct-feature behavior, and enforce approved RFC state before feature completion.

## Task 3: Verify and deliver the core RFC boundary independently

**Outcome:** The state model is regression-safe and available as a stable dependency for agent-facing RFC workflow guidance.
**Files:**
- Modify: `docs/superplan/plans/features/F019/01-rfc-state-model-and-enforcement.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Run focused tests while the model stabilizes and `python3 tools/verify_repo.py` once against the final core implementation.
- Validate the real approved `docs/superplan/rfcs/F019.md` against the new parser while F019-02 remains draft and F019 remains accepted.
- Mark only F019-01 complete, refresh the plan index, inspect exact status/diff, and create an `F019-01` commit containing core scripts, tests, and progress artifacts.

**Verification:**
- `python3 tools/verify_repo.py`
- `python3 skills/using-superplan/scripts/human_requests.py --root . validate`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --root . --write --check`
- `git diff --check`
- `git status --short`

- [x] Obtain current focused, full-regression, registry, RFC, plan-index, diff, and status evidence.
- [x] Mark F019-01 complete without changing F019 to done or implementing F019-02 scope.
- [x] Create a dedicated commit whose message includes `F019-01` and excludes unrelated changes.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/rfcs/F019.md`
- `docs/superplan/plans/features/F012/02-progressive-state-discovery.md`
- `docs/superplan/plans/features/F014-harden-state-integrity-and-verification.md`
- `skills/using-superplan/scripts/human_registry.py`
- `skills/using-superplan/scripts/human_requests.py`
- `skills/using-superplan/scripts/generate_plans_readme.py`
