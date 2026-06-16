---
id: "F002"
title: "Support Combined README Write and Check Flags"
type: "feature"
status: "complete"
summary: "Allow generate_plans_readme.py to accept --write and --check together by running write first and then validating the written README."
source: "docs/superplan/human/features.md"
created: "2026-06-16"
depends_on: []
parent: ""
---
# Support Combined README Write and Check Flags Plan

**Goal:** Let callers invoke `generate_plans_readme.py` with both `--write` and `--check` without manual sequencing.
**Scope:** Update the README generator CLI so `--write --check` is a supported combination with deterministic write-then-check behavior, and add regression tests for the combined mode.
**Non-Goals:** Do not change the behavior of standalone `--write` or standalone `--check`, and do not add automatic writeback when only `--check` is passed.
**Architecture:** Remove the current mutual-exclusion restriction between `--write` and `--check`, keep a single generated README snapshot per run, and make the combined path write that snapshot before checking the resulting file content. Tests should cover both stale-readme recovery in combined mode and preservation of existing single-flag behavior.
**Baseline:** `generate_plans_readme.py` currently parses `--write` and `--check` as mutually exclusive options, so a combined invocation errors before any validation logic runs. Existing tests cover separate `--write` and `--check` flows, but there is no coverage for a combined invocation.
**Exit Criteria:** Running `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check` succeeds when the README can be regenerated, still fails on real validation errors, and the script test suite contains explicit coverage for the combined mode.

## Task 1: Support combined write and check execution in the generator CLI

**Outcome:** The generator accepts `--write --check` and executes them in deterministic write-then-check order without changing single-flag semantics.
**Files:**
- Modify: `skills/using-superplan/scripts/generate_plans_readme.py`

**Verification:**
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`

- [x] Review the current argument parsing and run-path branching for `--write` and `--check`.
- [x] Replace the mutual-exclusive flag handling with logic that allows both flags to be present in one invocation.
- [x] Implement the combined branch so it writes the generated README first, then checks the on-disk file state produced by that write.
- [x] Preserve the current standalone `--write` and standalone `--check` behavior, including existing failure paths for invalid plans.
- [x] Run the verification command from the repository root and confirm the combined invocation exits successfully.

## Task 2: Add regression coverage for the combined mode

**Outcome:** The test suite proves combined `--write --check` works for stale README input and does not weaken validation guarantees.
**Files:**
- Modify: `skills/using-superplan/scripts/tests/test_generate_plans_readme.py`

**Verification:**
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`

- [x] Add a test that starts from a stale README, invokes the script with both `--write` and `--check`, and asserts a successful result.
- [x] Add a test that exercises the combined mode alongside invalid plan metadata and confirms the run still fails instead of masking validation errors.
- [x] Keep the existing single-flag tests intact so the original behavior remains covered.
- [x] Run the full script test suite and confirm it passes.

## References
- `docs/superplan/human/features.md`
- `skills/using-superplan/scripts/generate_plans_readme.py`
- `skills/using-superplan/scripts/tests/test_generate_plans_readme.py`
