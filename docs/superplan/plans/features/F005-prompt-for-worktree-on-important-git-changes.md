---
id: "F005"
title: "Prompt for Worktree on Important Git Changes"
type: "feature"
status: "complete"
summary: "Require Superplan to identify meaningful dirty-worktree risk and ask before moving subsequent work into an isolated worktree."
source: "docs/superplan/human/features.md"
created: "2026-07-20"
depends_on: ["F003"]
parent: ""
---
# Prompt for Worktree on Important Git Changes Plan

**Goal:** Protect meaningful in-progress Git work by making Superplan offer an isolated worktree before intake, planning, or implementation continues.
**Scope:** Update the shared Superplan guidance so entry checks inspect Git status and relevant diffs, use model judgment to distinguish consequential changes from noise, and ask the human whether to create a new worktree before any later Superplan mutation when important changes are present.
**Non-Goals:** Do not add a deterministic change-classification script, prompt for every dirty status, automatically stash or commit existing work, move uncommitted changes into the new worktree, create a worktree without explicit consent, or duplicate the canonical rule in every route skill.
**Architecture:** Treat this as a standard-risk workflow behavior change even though the persisted edits are documentation and templates. Keep the complete decision policy in `delivery-loop.md`, summarize it in the entry skill, and inject one concise project guardrail so direct route use inherits the same safety boundary. An important change is one whose content could be overwritten, accidentally staged, or create a merge conflict with the requested work; timestamp-only metadata, caches, and safely reproducible generated noise do not trigger the prompt. If the human accepts isolation, use the installed `using-git-worktrees` workflow and resume from the repository's committed baseline while leaving the original worktree untouched; if the human declines, continue in place with explicit preservation and precise staging. F003 remains responsible for branch-qualified intake ids after execution moves into a linked worktree.
**Baseline:** Superplan currently requires `git status` inspection and preservation of unrelated work, but it does not require agents to assess whether dirty state is consequential, explain the risk, or ask the human about worktree isolation before intake and planning mutate the repository. The managed guardrails only require workspace inspection, and the entry skill does not define what happens after important changes are found.
**Exit Criteria:** Every Superplan route inherits one canonical rule that checks meaningful Git changes before later workflow mutations; important changes cause a human worktree-choice prompt with no automatic stash, commit, or worktree creation; insignificant noise and non-Git workspaces continue without the prompt; declining isolation preserves unrelated changes and constrains staging; accepting isolation delegates creation to `using-git-worktrees` and resumes the route in the new worktree; managed guardrails synchronize without overwriting unrelated `AGENTS.md` content; and repository validation passes.

## Task 1: Establish the semantic dirty-worktree decision policy

**Outcome:** The canonical workflow and public entry guidance consistently define when Superplan pauses for a worktree decision and how each response affects subsequent execution.
**Files:**
- Modify: `skills/using-superplan/references/delivery-loop.md`
- Modify: `skills/using-superplan/SKILL.md`
- Modify: `skills/using-superplan/references/agents-guardrails.md`
- Modify: `README.md`

**Change Map:**
- `delivery-loop.md`: add the authoritative pre-mutation decision flow, semantic importance criteria, consent boundary, current-worktree continuation rules, non-Git behavior, and unexpected Git-inspection failure handling.
- `using-superplan/SKILL.md`: make the Entry Checks section require the important-change assessment and worktree question before reading or writing route artifacts that would advance the workflow.
- `agents-guardrails.md`: extend the workspace-inspection guardrail with a concise Superplan-specific isolation prompt while keeping detailed classification rules in the delivery loop.
- `README.md`: document the user-visible dirty-worktree safety behavior and its relationship to the existing adaptive workflow.

**Verification:**
- `rg -n -i "important|meaningful|git status|diff|worktree|consent|stash|noise|unrelated|non-git" skills/using-superplan/SKILL.md skills/using-superplan/references/delivery-loop.md skills/using-superplan/references/agents-guardrails.md README.md`
- `git diff --check -- skills/using-superplan/SKILL.md skills/using-superplan/references/delivery-loop.md skills/using-superplan/references/agents-guardrails.md README.md`

- [x] Define important changes by semantic risk to preservation, staging, and merge safety rather than by a fixed file list or any-dirty rule.
- [x] Require the agent to inspect enough status and diff context to explain why isolation is being offered, while ignoring clearly insignificant or reproducible noise.
- [x] Place the human question before intake, plan creation, approval-state changes, or implementation edits; never infer consent or create a worktree automatically.
- [x] Specify that accepting isolation uses `using-git-worktrees`, starts from the committed repository baseline, leaves original changes untouched, and resumes the selected Superplan route in the new worktree.
- [x] Specify that declining isolation continues in the current worktree with unrelated-change preservation and exact staging, while non-Git workspaces bypass the worktree prompt and unexpected inspection failures are surfaced before mutation.
- [x] Align the entry skill, managed guardrail, and README summary with the canonical rule without copying the full policy into route-specific skills.

## Task 2: Synchronize guardrails, verify behavior documentation, and finish F005

**Outcome:** Generated workspace guidance, project progress, and regression evidence all reflect the approved worktree-choice policy without absorbing unrelated user edits.
**Files:**
- Modify: `AGENTS.md` (managed guardrails block only)
- Modify: `docs/superplan/human/features.md`
- Modify: `docs/superplan/plans/features/F005-prompt-for-worktree-on-important-git-changes.md`
- Modify: `docs/superplan/plans/README.md`

**Change Map:**
- Synchronize only the managed `AGENTS.md` block and preserve the existing memory-context timestamp change outside that block unstaged.
- Review F001–F005 together so F005 extends F003 worktree support and F004 adaptive workflow policy without reopening their delivered boundaries.
- Run the final repository regression suite after all skill and reference edits stabilize, then update F005 and the generated plan index without rerunning unchanged tests for metadata-only status changes.
- Commit the delivered files with an F005-qualified message while excluding the unrelated `AGENTS.md` memory-context hunk.

**Verification:**
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --write`
- `python3 skills/using-superplan/scripts/sync_agents_guardrails.py --check`
- `python3 -m unittest discover -s skills/using-superplan/scripts/tests`
- `python3 skills/using-superplan/scripts/generate_plans_readme.py --write --check`
- `git diff --check`

- [x] Synchronize and inspect the managed guardrail diff, confirming the pre-existing non-managed `AGENTS.md` change remains preserved and unstaged.
- [x] Review the complete feature-plan set for independent boundaries, explicit F003 dependency, and consistency with F004's canonical-policy structure.
- [x] Run the full script unittest suite once against the final skill/reference state and capture successful output.
- [x] After verification succeeds, mark this plan `complete`, mark F005 `done`, regenerate the plan index, and avoid rerunning unchanged code tests after metadata-only edits.
- [x] Create a dedicated F005 implementation commit containing only the feature's implementation, progress, generated index, and managed guardrail hunk.

## References
- `docs/superplan/human/features.md`
- `docs/superplan/plans/features/F003-worktree-aware-request-numbering.md`
- `docs/superplan/plans/features/F004-adaptive-superplan-workflow.md`
- `skills/using-superplan/SKILL.md`
- `skills/using-superplan/references/delivery-loop.md`
- `skills/using-superplan/references/agents-guardrails.md`
