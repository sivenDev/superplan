# Worktree Execution

Read this reference only after Workspace Safety has identified meaningful risk
and the human has accepted isolation, including explicit current-task standing
authorization to auto-isolate or auto-recover.

1. Check whether the current checkout already provides a valid linked worktree;
   reuse suitable isolation instead of creating another copy.
2. Prefer a harness-native worktree mechanism. Otherwise use `git worktree` with
   a dedicated branch from the committed baseline.
3. Follow an explicit path preference, then an established repository
   convention. Verify a project-local worktree directory is ignored; do not edit
   `.gitignore` without authorization.
4. Leave the original checkout and its uncommitted work untouched. Do not stash,
   commit, copy, or move those changes into the new worktree.
5. Run only repository-documented setup and a cheap relevant baseline check.
   Stop on overlapping changes, unsafe attribution, conflicts, or an unexplained
   baseline failure.
6. For parallel recovery, require a write set independent from the active task,
   keep its branch, worktree, verification, and commit separate, and do not merge
   it into the active task implicitly. Defer overlapping repair instead of
   running concurrent mutations against shared workflow artifacts.

Report the worktree path, branch, setup performed, baseline result, and any
pre-existing failure before resuming the same Superplan route.
