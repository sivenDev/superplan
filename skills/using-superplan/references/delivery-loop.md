# Delivery Loop

This is the canonical workflow for all Superplan routes. Specialized skills only
define their input, output, plan type, and route-specific safeguards.

`<using-superplan-root>` means the installed `skills/using-superplan/` directory.
Bundled scripts detect the repository root from the current directory and fail
outside it; use `--root <path>` to target another repository explicitly.

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

## Delivery

1. Run Workspace Safety, inspect recent commits and `docs/superplan/plans`, and
   preserve unrelated work.
2. Read the route's source under `docs/superplan/human/` and apply its bookkeeping
   rules.
3. Confirm scope, constraints, acceptance, non-goals, and risk. Run required
   route discovery such as `systematic-debugging` before planning a bugfix.
4. Read `plan-spec.md`, create the smallest independently verifiable plan set,
   and start new plans at `status: draft`.
5. Review the full related plan set for overlap, boundaries, and real
   `depends_on` relationships. Present it and stop for human approval.
6. Human approval is the `draft -> approved` gate. Never implement before it.
   After approval, move plans through `approved -> in_progress` and execute in
   dependency order.
7. During implementation, run focused checks for the selected risk profile. Bug
   fixes keep a behavior-level regression proving the reproduced failure. Clean
   directly related redundancy without widening scope.
8. After the implementation state is final, obtain fresh completion evidence and
   run the relevant full regression once. Then mark the human entry and plan
   complete and refresh the index with:

   `python3 <using-superplan-root>/scripts/generate_plans_readme.py --write --check`

   Do not rerun unchanged code tests after metadata-only progress updates.
9. Create a task-level commit whose message includes the plan id. Stage only task
   changes.

The human entry records intent, the plan records outcomes and evidence, tests
record executable proof, and Git records the delivered diff.

## Managed Guardrails

The canonical project guardrails live in `agents-guardrails.md`. Install or
refresh them with:

`python3 <using-superplan-root>/scripts/sync_agents_guardrails.py --write`

Verify with the same command using `--check`.
