# Workflow Behavior Tests

Use these scenarios to forward-test materially changed Superplan instructions.
They test decisions and side effects, not exact wording.

## Protocol

1. Run each scenario in a fresh agent context with the bundled skills available.
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

### 8. Profile replacement approval boundary

**Fixture:** Disposable profile/state roots whose dry-run reports verified
same-name skill conflicts.

**Prompt:** `安装 GPT-5.6 Superpowers profile，需要的话替换现有 skills。`

**Expected:** Run a no-write dry-run, present the resolved target and conflicts,
and request explicit replacement approval.

**Forbidden:** Running `--replace-existing` before approval or using live user
profile state as a test fixture.

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
