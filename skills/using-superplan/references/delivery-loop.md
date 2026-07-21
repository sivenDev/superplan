# Delivery Loop

This is the canonical workflow for all Superplan routes. Specialized skills only
define their input, output, plan type, and route-specific safeguards.

`<using-superplan-root>` means the installed `skills/using-superplan/` directory.
Existing-workspace commands prefer the Git top-level, then an existing
`docs/superplan` ancestor; initialization may fall back to its starting
directory. Use `--root <path>` to choose a target explicitly.

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
4. If accepted, use `using-git-worktrees`, start from the committed baseline,
   leave the original worktree untouched, and resume the same route there. If
   declined, continue in place while preserving unrelated work and staging exact
   task paths or hunks.

Non-Git workspaces continue without this prompt. Unexpected Git inspection
failures must be resolved before workflow mutation.

Workspace-safety evidence may be reused during the same routed task while its
supporting state remains unchanged. Reinspect when the branch or worktree
changes, the human or an external tool makes relevant changes, unexpected
non-task Git changes appear, or files/environment facts supporting the earlier
decision change.

## Superpowers Composition

For `docs/superplan/**` work, Superplan owns the persisted request, design, plan,
and progress artifacts.

- Use `brainstorming` only for material ambiguity in scope, constraints,
  acceptance, non-goals, or architecture.
- Use `writing-plans` reasoning, but write only the Superplan format from
  `plan-spec.md`; do not create parallel Superpowers specs or plans unless asked.
- Project instructions and the selected risk profile control testing,
  verification, delegation, and traceability depth.

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
  complex-defect, or broad uncertain work. Keep strict test-first/debugging where
  applicable, run focused and full regression checks, and add independent review
  when separation improves evidence.

## Evidence and Verification

Reuse successful evidence when it still proves the same claim against unchanged
relevant state. Later mutations invalidate only evidence affected by those
mutations; metadata-only progress edits do not invalidate unchanged code-test
results. Recheck dependencies only for initialization, installation,
diagnostics, unresolved dependency state, or after the model, profile manifest,
skill locations, or other supporting environment changes.

Select focused and final checks from `verification-matrix.md`, combining rows
when a change spans artifact types and escalating for the selected risk profile.
Before completion, every material claim must have current evidence, but repeated
commands that prove no changed claim add no value.

## Delivery

1. Establish or reuse still-fresh Workspace Safety evidence, inspect recent
   commits and `docs/superplan/plans`, and preserve unrelated work.
2. Read the route's source under `docs/superplan/human/` and apply its bookkeeping
   rules.
3. Confirm scope, constraints, acceptance, non-goals, and risk. Run required
   route discovery such as `systematic-debugging` before planning a bugfix.
4. Read `plan-spec.md`, create the smallest independently verifiable plan set,
   and start new plans at `status: draft`.
5. For structural plan changes, review the full related plan set for overlap,
   boundaries, and real `depends_on` relationships. For routine status,
   checkbox, or evidence-note updates, validate only the affected plan and
   generated index. Present every new or structurally revised draft and stop for
   human approval.
6. Human approval is the gate out of `draft`; never implement before it. Persist
   `approved` when approved work will remain queued. If execution starts in the
   same continuation, persist `in_progress` directly and refresh the index once,
   then execute in dependency order.
7. During implementation, run focused checks for the selected risk profile. Bug
   fixes keep a behavior-level regression proving the reproduced failure. Clean
   directly related redundancy without widening scope.
8. After the implementation state is final, obtain current completion evidence
   selected from `verification-matrix.md` and run any relevant full regression
   once. Then mark the human entry and plan complete and refresh the index with:

   `python3 <using-superplan-root>/scripts/generate_plans_readme.py --write --check`

   Do not rerun unchanged code tests after metadata-only progress updates.
9. Create a task-level commit whose message includes the plan id. Stage only task
   changes.

The human entry records intent, the plan records outcomes and evidence, tests
record executable proof, and Git records the delivered diff.

## Managed Guardrails

Install or refresh the bundled project guardrails with:

`python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`

Verify with the same command using `--check`.
