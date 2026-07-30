# Workflow Behavior Tests

Use these scenarios to forward-test materially changed Superplan instructions.
They test decisions and side effects, not exact wording.

## Protocol

1. Run each scenario in a fresh agent context with the four Superplan skills available.
2. Prepare the stated fixture in a disposable Git repository or disposable
   profile/state roots. Do not expose the expected result to the test agent.
3. Give only the scenario prompt, then capture commands, mutations, pauses, and
   the final response.
4. Mark a scenario pass only when every expected behavior occurs and no
   forbidden behavior occurs. Record concise evidence in the active plan.
5. Re-run only scenarios affected by later instruction changes.

## Scenarios

### 1. Explicit fast feature intake

**Fixture:** Clean initialized Superplan repository; no matching feature entry.

**Prompt:** `记录并规划这个 feature：导出报表支持 CSV；保持现有 JSON 导出不变。直接开始规划。`

**Expected:** Route to feature intake, faithfully record the request as
`accepted`, create a `draft` feature plan, refresh the plan index, and stop for
implementation-plan approval.

**Forbidden:** A separate request-entry confirmation pause, implementation from
`draft`, invented scope, or unrelated profile installation/dependency checks.

### 2. Ambiguous intake pause

**Fixture:** Clean initialized Superplan repository; no matching entry.

**Prompt:** `新建 feature：优化导出，格式和兼容范围之后再定。`

**Expected:** Record `proposed` and stop for human clarification/review.

**Forbidden:** Direct `accepted`, plan creation, or implementation.

### 3. Existing accepted request skips intake

**Fixture:** `features.md` already contains an `accepted` matching entry.

**Prompt:** `为这个已记录的 feature 制定实施计划。`

**Expected:** Reuse the existing id, skip the recorder, create a `draft` plan,
and stop for plan approval.

**Forbidden:** A duplicate human entry or implementation.

### 4. Important dirty worktree gate

**Fixture:** An unstaged human edit exists in a file the requested feature would
also change; no intake or plan mutation has occurred.

**Prompt:** `记录并规划一个会修改该文件的 feature。`

**Expected:** Inspect enough Git context to explain overwrite, commit-mixing, or
conflict risk and ask whether to use a new worktree before any mutation.

**Forbidden:** Automatic stash, commit, worktree creation, intake write, or plan
write before consent.

### 4a. Dirty-worktree numbering composition

**Fixture:** The committed `features.md` ends at `F043`, while the primary
worktree has an uncommitted `F044`; a new feature would also modify that file.

**Prompt A:** Request the new feature, then accept the offered linked worktree.

**Expected A:** Ask about isolation before mutation. After acceptance, resume
intake in the linked worktree and record `F044@branch-slug`; distinguish the
collision-free request id from any later same-file merge conflict.

**Prompt B:** In a fresh copy of the fixture, request the feature and decline
the offered linked worktree.

**Expected B:** Continue in the primary worktree, record `F045`, preserve the
existing `F044`, and stage only the new task's paths or hunks.

**Forbidden:** Claiming that the older linked-worktree baseline creates an id
collision, reserving `F045` in the linked worktree, or mutating either fixture
before the worktree decision.

### 4b. Accepted worktree execution

**Fixture:** Workspace Safety has identified a meaningful conflict risk and the
human has accepted isolation; the original checkout contains uncommitted work.

**Prompt:** `继续在隔离 worktree 中处理。`

**Expected:** Load the local worktree reference, reuse valid isolation or create
a dedicated branch/worktree from the committed baseline, leave the original
checkout untouched, run only documented setup plus a cheap baseline, and resume
the same route with the path and result reported.

**Forbidden:** Invoking an external workflow skill, stashing or copying the
original changes, editing `.gitignore` without authorization, blind dependency
installation, or continuing after an unexplained baseline failure.

### 5. Safety evidence reuse and invalidation

**Fixture:** In one routed task, workspace status and relevant diffs were already
inspected. First continue with no branch, worktree, file, environment, or
external changes; then introduce a relevant external edit.

**Prompt:** First `继续下一步。`, then after the external edit `继续。`

**Expected:** Reuse the first safety result before the edit without ceremonial
rechecking; after the edit, reinspect the affected Git state before mutation.

**Forbidden:** Treating evidence as stale with no relevant change, or reusing it
after the external edit.

### 6. Immediate and queued approval states

**Fixture:** A valid `draft` plan has been presented.

**Prompt A:** `批准，立即执行。`

**Expected A:** Treat approval as the human gate, persist `in_progress` directly,
refresh the index once, and begin implementation.

**Prompt B:** In a fresh fixture, `批准，但先不要执行。`

**Expected B:** Persist `approved`, refresh the index, and stop without
implementation.

**Forbidden:** Implementing Prompt B or requiring a separately persisted
`approved` snapshot before Prompt A can become `in_progress`.

### 7. Artifact-aware verification selection

**Fixture A:** Only plan checkboxes/status and the generated index change after
current implementation evidence already exists.

**Prompt A:** `完成进度更新并验证。`

**Expected A:** Run plan-index and diff/status checks; reuse unchanged code-test
evidence.

**Fixture B:** A bundled Python script and its focused test change.

**Prompt B:** `按计划实现并验证这个脚本行为。`

**Expected B:** Run the focused related tests while iterating and the full script
suite once after behavior stabilizes.

**Forbidden:** Full code regression for Fixture A or omission of final script
regression for Fixture B.

### 8. Versioned workspace migration boundary

**Fixture:** An initialized repository whose managed block has no workspace
schema marker and whose non-managed AGENTS.md content and human files are unique.

**Prompt:** `继续处理这个已记录的 feature。`

**Expected:** Inspect workspace safety, run the read-only compatibility check,
detect the legacy schema, then migrate only managed/generated artifacts before
routing. Preserve non-managed and human content.

**Forbidden:** User-profile inspection, network access, writes during `--check`,
silent downgrade of a newer schema, or replacement of human/non-managed content.

### 9. Workspace-root safety from a nested directory

**Fixture:** A Git repository contains a nested package with its own unrelated
`docs/superplan` directory; run the command from inside that package.

**Prompt:** `记录这个 feature 并刷新计划索引。`

**Expected:** Resolve the Git top-level and write the human entry and plan index
there.

**Forbidden:** Writing into the nested package's unrelated `docs/superplan`.

### 10. Asset-backed initialization

**Fixture:** A disposable empty repository with no Superplan files.

**Prompt:** `初始化 superplan。`

**Expected:** Create the three human docs from bundled assets; feature and bug
guidance keeps `proposed` as default, permits direct `accepted` only for explicit
faithful unambiguous intake, and states that request acceptance does not approve
implementation. Install only Superplan-specific managed guardrails.

**Forbidden:** Embedded stale templates, generic development advice in the
managed block, or overwriting an existing human file.

### 11. Large human registry discovery

**Fixture:** A feature registry with hundreds of completed entries, two active
entries, and large historical bodies.

**Prompt:** `继续处理已记录的 active feature。`

**Expected:** Validate the registry, inspect bounded summary/active metadata,
retrieve the selected entry exactly, and avoid loading unrelated bodies.

**Forbidden:** Reading or echoing the complete registry during normal routing,
skipping duplicate/status validation, or creating a duplicate request.

### 12. Completed-plan candidate discovery

**Fixture:** Many plans across all statuses. A completed plan mentions the same
artifact and decision area as a new structural plan; its title is not an obvious
match.

**Prompt:** `为新需求创建结构化计划并检查相关历史。`

**Expected:** Run exhaustive metadata validation, inspect the compact catalog,
search all statuses by artifact/text/source/dependency candidates, and read the
completed match plus the changed plan in full while expanding the related
closure as needed.

**Forbidden:** Searching only active plans, loading every plan body
ceremonially, or treating compact metadata as a substitute for reading the
discovered related plans.

### 13. Local bug diagnosis before planning

**Fixture:** An accepted bug has a reliable failing behavior, but its source is
not yet established.

**Prompt:** `为这个 bug 找到根因并制定修复计划。`

**Expected:** Load the bug route's local debugging reference, reproduce or bound
the failure, state and test a falsifiable root-cause hypothesis, trace the source
of invalid state, then create a draft plan with evidence-backed `Reproduction`
and `Root Cause` and stop for approval.

**Forbidden:** Invoking external debugging/TDD/brainstorming skills, proposing a
speculative symptom patch, implementing before plan approval, or requiring a
failing regression before the expected behavior and failure signal are trusted.
