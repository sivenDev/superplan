# Delivery Loop

This is the canonical workflow for all Superplan routes. Specialized skills only
define their input, output, plan type, and route-specific safeguards.

`<using-superplan-root>` means the installed `skills/using-superplan/` directory.
Existing-workspace commands prefer the Git top-level, then an existing
`docs/superplan` ancestor; initialization may fall back to its starting
directory. Use `--root <path>` to choose a target explicitly.

After Workspace Safety, run `init_workspace.py --check` before routed work.
Continue for a compatible schema, run `--migrate` for older/missing or stale
generated artifacts, and stop for a newer or malformed schema. Initialization
and migration are offline and never inspect user-level skill/profile state.

## Recovery Triage

Use fresh command evidence rather than an earlier narrative diagnosis.

1. When the current compatibility, registry, and plan checks pass, continue the
   active route. Do not widen scope to historical repair or propose an older
   Superplan version because a previous report named stale blockers.
2. When registry validation reports only legacy missing `status`/`created`, run
   `migrate-legacy --check`, apply `--write` after Workspace Safety when every
   value is evidence-backed, validate again, and continue without another
   decision prompt.
3. When compatible active work and a historical repair have disjoint write
   sets, an explicit current-task instruction to auto-recover or auto-isolate
   counts as worktree consent. If delegation is useful and available, isolate
   the repair under `worktrees.md`, keep its branch and commit separate, and do
   not wait for it before continuing the active route. If their artifacts
   overlap, defer the repair rather than racing both mutations.
4. Stop only when the current route requires migration and its preflight remains
   unsafe, the schema is newer or malformed, or continuation needs new
   authority. Report the current failing evidence and the one required decision
   concisely; provide historical detail only on request.

## Workspace Safety

Before intake, plan/status changes, or implementation edits:

1. In a Git workspace, inspect `git status` and enough staged, unstaged, and
   relevant untracked diff context to understand existing work.
2. Treat changes as important when the requested work could overwrite them, mix
   them into its commit, or conflict during integration. Ignore timestamp-only
   metadata, caches, logs, and safely reproducible noise unless consequential.
3. If important changes exist, explain the concrete risk and ask whether to move
   subsequent Superplan work to a new worktree. Resolve this before mutation;
   never infer consent or automatically stash, commit, or create a worktree.
   An explicit current-task instruction to auto-isolate or auto-recover is
   consent for that isolation, so do not ask again.
4. If accepted, read `worktrees.md`, create or reuse isolation from the committed
   baseline, leave the original worktree untouched, and resume the same route
   there. If declined, continue in place while preserving unrelated work and
   staging exact task paths or hunks.

An older committed baseline does not itself create a request-id collision:
linked-worktree intake uses the recorder's branch-qualified id. Treat possible
same-file merge conflicts as a separate risk.

Non-Git workspaces continue without this prompt. Unexpected Git inspection
failures must be resolved before workflow mutation.

Workspace-safety evidence may be reused during the same routed task while its
supporting state remains unchanged. Reinspect when the branch or worktree
changes, the human or an external tool makes relevant changes, unexpected
non-task Git changes appear, or files/environment facts supporting the earlier
decision change.

## Human-Decision Checkpoints

Immediately before returning control for a required human decision, inspect the
current task's persistent changes. When task changes exist:

1. Validate the changed artifacts enough to establish a safe handoff state,
   then inspect the diff and stage only current-task paths or hunks.
2. Create a checkpoint commit whose message includes the relevant plan or
   request id and identifies the decision gate. Keep it distinct from the final
   delivery commit.
3. Never include pre-existing, user-owned, unrelated, secret-bearing, or
   known-invalid state. If a safe checkpoint cannot be formed, do not fabricate
   one; report the failed validation or safety reason and the exact dirty paths.
4. Inspect status after the commit. Confirm the task-owned state is clean; when
   excluded dirty content remains, report its exact paths and do not claim the
   whole worktree is clean.
5. Treat a reported checkpoint as an immutable handoff baseline. Do not amend,
   rebase, or squash it after reporting it.

Do not create an empty checkpoint when no task changes exist. In particular, a
Workspace Safety question asked before mutation must not commit, stash, or alter
the existing work it is protecting. This checkpoint boundary applies to intake
review, plan approval, queued approval, blockers, and delivery follow-up only
when the active task has produced persistent changes since its last commit.

## Workflow Composition

For `docs/superplan/**` work, Superplan owns the persisted request, design, plan,
and progress artifacts.

- Resolve only ambiguity that could change scope, acceptance, architecture, or
  consequential behavior; precise work proceeds without a separate design step.
- Persist only the Superplan format from `plan-spec.md`; do not create parallel
  workflow plans or logs unless the human or repository requires them.
- Execute an approved plan by outcome, adapt mechanics without widening scope,
  and update the plan only when a material requirement, design, or verification
  strategy changes.
- Project instructions and the selected risk profile control test-first work,
  independent review, delegation, verification, and traceability depth.

## Risk Profiles

Risk is planning guidance, not plan frontmatter. Prefer the more conservative
profile when uncertainty could change required evidence.

- **Low:** Documentation, configuration, templates, or isolated mechanical work
  without meaningful runtime impact. Use the smallest validator or smoke check;
  new unit tests are not required by default. Use one agent unless work has truly
  independent slices.
- **Standard:** Bounded behavior changes with understood local impact. Test
  observable acceptance behavior, use focused checks while iterating, and run
  the relevant full regression once after implementation stabilizes. Default to
  one agent; delegate only independent slices with explicit verification.
- **High:** Security, concurrency, migration, data-integrity, public-contract,
  complex-defect, or broad uncertain work. Use test-first/debugging when a
  trustworthy focused failure distinguishes the change, run focused and full
  regression checks, and add independent review when separation improves
  evidence.

## Evidence and Verification

Reuse successful evidence when it still proves the same claim against unchanged
relevant state. Later mutations invalidate only evidence affected by those
mutations; metadata-only progress edits do not invalidate unchanged code-test
results. Recheck dependencies only for initialization, installation,
diagnostics, unresolved dependency state, or after the model, profile manifest,
skill locations, or other supporting environment changes.

Select focused and final checks from `verification-matrix.md`, combining rows
when a change spans artifact types and escalating for the selected risk profile.
Before completion, map every material claim to current command or inspection
evidence, inspect failures and meaningful warnings, and compare the final diff
with acceptance. Repeated commands that prove no changed claim add no value.

## Delivery

1. Establish or reuse still-fresh Workspace Safety evidence, inspect recent
   commits and `docs/superplan/plans`, and preserve unrelated work.
2. For feature/bug routes, validate the registry and use compact summary/list
   plus exact-entry retrieval; load the full registry only for repair or genuine
   cross-entry analysis. Read the PRD directly for project bootstrap.
3. Confirm scope, constraints, acceptance, non-goals, and risk. Bug routes apply
   their local debugging reference before planning when the cause is not proven.
4. Read `plan-spec.md`, create the smallest independently verifiable plan set,
   and start new plans at `status: draft`.
5. For structural plan changes, run exhaustive global validation, inspect the
   compact catalog, and search all statuses for source, dependency, scope, text,
   and artifact candidates. Read the changed plan and iteratively discovered
   related closure in full. Routine status, checkbox, or evidence updates use
   local plan/index validation. Present every new or structurally revised draft
   and stop for human approval.
6. Human approval is the gate out of `draft`; never implement before it. Persist
   `approved` when approved work will remain queued. If execution starts in the
   same continuation, persist `in_progress` directly and refresh the index once,
   then execute in dependency order.
7. During implementation, run focused checks for the selected risk profile. Bug
   fixes keep a behavior-level regression proving the reproduced failure. Clean
   directly related redundancy without widening scope.
8. After the implementation state is final, obtain current completion evidence
   selected from `verification-matrix.md` and run any relevant full regression
   once. Mark each delivered plan complete first. For a feature or bug, set its
   human entry to `done` only after at least one non-superseded related plan
   exists and every such plan is `complete`; `human_requests.py set-status`
   enforces this boundary. Then refresh the index with:

   `python3 <using-superplan-root>/scripts/generate_plans_readme.py --write --check`

   Do not rerun unchanged code tests after metadata-only progress updates.
9. Create a task-level commit whose message includes the plan id. Stage only task
   changes.
10. When delivery ran in a linked worktree, after development, verification, and
    the task commit are complete, state that development is complete and ask
    whether to merge the branch into the mainline branch and whether to remove
    the linked worktree directory. Treat merge and cleanup as separate follow-up
    authorizations; do neither implicitly.

The human entry records intent, the plan records outcomes and evidence, tests
record executable proof, and Git records the delivered diff.

## Managed Guardrails

Initialize or migrate the versioned workspace with:

`python3 <using-superplan-root>/scripts/init_workspace.py [--migrate]`

Verify compatibility without writes with `init_workspace.py --check`. The
lower-level `sync_agents_guardrails.py` command remains available for repository
development and exact generated-block validation.
