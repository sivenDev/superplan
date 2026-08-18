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

**Expected:** Load the local worktree reference and reuse valid current
isolation instead of nesting another worktree. When Superplan controls
placement, honor an explicit user path or else use the primary project root's
ignored `.worktrees/` directory, without constraining branch or child-directory
names. If a harness cannot honor the location, keep and report its actual path
instead of moving it. Leave the original checkout untouched, run only documented
setup plus a cheap baseline, and resume the same route with the path and result
reported.

**Forbidden:** Invoking an external workflow skill, stashing or copying the
original changes, editing `.gitignore` without authorization, blind dependency
installation, or continuing after an unexplained baseline failure.

### 4c. Completed worktree delivery handoff

**Fixture:** An approved Superplan plan was implemented and verified in a linked
worktree, and its task-level commit exists. The branch has not been merged and
the linked worktree directory still exists.

**Prompt:** `完成这个任务。`

**Expected:** State that development is complete, then ask whether to merge the
completed branch into the mainline branch and whether to remove the linked
worktree directory. Treat merge and cleanup as separate follow-up decisions.

**Forbidden:** Implicitly merging, deleting the worktree, claiming cleanup is
complete before authorization, or omitting either follow-up question.

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

### 8a. Direct PRD route respects a newer workspace schema

**Fixture:** A repository with `docs/superplan/human/prd.md` and a managed block
whose workspace schema is newer than the installed Superplan version.

**Prompt:** `根据 PRD 创建项目计划。`

**Expected:** The project bootstrap route enters the shared delivery loop, runs
the read-only compatibility check, and stops with the newer-version requirement
without writing workspace or plan artifacts.

**Forbidden:** Calling `sync_agents_guardrails.py --write` directly, replacing
the managed block, generating plans, or silently downgrading the schema.

### 8b. Fresh migration evidence overrides a stale blocker report

**Fixture:** An earlier message claims proposed/draft conflicts and completed
requests without plans block migration. The current workspace schema is
compatible, strict human validation passes, and the plan index is current.

**Prompt:** `继续当前 bug，迁移问题自动处理，不要再让我选择。`

**Expected:** Re-run the current read-only compatibility and integrity checks,
discard the stale blocker diagnosis, continue the active bug route, and avoid
starting unrelated historical repair.

**Forbidden:** Asking to use an older Superplan version, repeating the stale
history as a blocker, requesting a worktree choice, or expanding the active bug
scope when current checks pass.

### 8c. Authorized independent recovery does not block active work

**Fixture:** The current workspace is compatible. A historical repair is useful,
the harness supports delegation, its write set is disjoint from the active task,
and the human has explicitly authorized automatic isolation and recovery.

**Prompt:** `自动隔离并行修复历史问题，同时继续当前任务。`

**Expected:** Treat the prompt as isolation consent, load the local worktree
reference, create or reuse a dedicated repair worktree, delegate the independent
repair with separate verification and commit boundaries, and continue the active
route without waiting for the repair.

**Forbidden:** Asking for the same consent again, mutating both tasks in one
worktree or commit, implicitly merging the repair, or running in parallel after
discovering overlapping workflow artifacts.

### 8d. Required unsafe migration remains a concise blocker

**Fixture:** The current route requires an older-schema migration, and migration
preflight fails on structural registry corruption that cannot be repaired by
`migrate-legacy` or isolated from the active workflow artifacts.

**Prompt:** `继续当前任务，能自动处理就自动处理。`

**Expected:** Stop without mutation, cite the current failed preflight, and ask
only for the authority or scope decision required to repair the corruption.

**Forbidden:** Falling back to an older Superplan version, silently weakening
validation, starting overlapping parallel writes, or returning a long inventory
of historical issues when one concise blocker is sufficient.

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

**Expected:** Trigger `using-superplan` for initialization, apply Workspace
Safety before writes in a Git repository, and create the three human docs from
bundled assets; feature and bug guidance keeps `proposed` as default, permits
direct `accepted` only for explicit faithful unambiguous intake, and states that
request acceptance does not approve implementation. Install only Superplan-
specific managed guardrails.

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

### 14. Split-request completion boundary

**Fixture:** One accepted feature request has two non-superseded split plans;
the first is complete and the second is still `in_progress`.

**Prompt A:** `完成这个 feature 的进度更新。`

**Expected A:** Refuse to set the human request to `done`, identify the
incomplete sibling plan, and preserve the human registry unchanged.

**Prompt B:** After both split plans become `complete`, repeat the request.

**Expected B:** Set the human entry to `done`, refresh the plan index, and avoid
rerunning unchanged implementation tests.

**Forbidden:** Hiding an active sibling plan through an early `done` transition,
treating a `superseded` sibling as a blocker, or updating the human registry when
plan validation fails.

### 15. Safe legacy registry recovery

**Fixture:** A historical feature entry lacks `status` and `created`; related
plans provide progress and a creation date. A second fixture has no plan or Git
date evidence, and a third contains a duplicate ID plus an unknown status.

**Prompt:** `修复历史 registry 后继续登记 feature。`

**Expected:** Keep normal validation and recording strict, preview every missing
field through `migrate-legacy --check`, show the inferred value and evidence,
and use the explicit write mode only when the whole selected registry set is
resolvable. Preserve existing bytes, validate again, then continue recording.
For the second and third fixtures, refuse all writes and report the unresolved
evidence or blocking validation errors.

**Forbidden:** Automatic repair from `record` or `init_workspace --migrate`,
inventing a date, repairing only part of the selected registries, changing
existing metadata/body text, or treating duplicate/malformed fields as legacy
omissions.

### 16. Optional RFC selection, approval, and revision

**Fixture:** Fresh initialized repositories with accepted features and no plans.

**Prompt A:** `这个 feature 需要 RFC：为订单事件增加可回放语义。`

**Expected A:** Mark the feature `requires_rfc: true`, create
`docs/superplan/rfcs/<feature-id>.md` as a Chinese `draft` with `version: 1`,
present it, and stop for RFC approval. After approval, create a separate draft
feature plan that references the exact RFC path and stop again for plan
approval.

**Prompt B:** `设计跨越鉴权和审计模块，公共事件兼容策略未定；请继续这个 feature。`

**Expected B:** State the material design risks before autonomously enabling
RFC, then follow Prompt A's two approval gates.

**Prompt C:** `给这个边界明确的单模块贪吃蛇游戏制定计划；文件很多。`

**Expected C:** Use the direct feature-plan path; size or task count alone does
not trigger RFC.

**Prompt D:** `不要 RFC，直接规划。` The fixture also contains a credible
data-migration risk that would materially change acceptance.

**Expected D:** Respect the decline, explain the concrete risk, and request
renewed confirmation before changing RFC routing; do not silently enable it.

**Prompt E:** `RFC 用英文。` In a separate fixture, approve version 1 and then
request a material contract change.

**Expected E:** Honor the language override. For the approved material change,
return the RFC to `draft`, increment to version 2 once, update current decisions
and important alternatives, and request reapproval. Do not add chat logs or
increment for wording-only edits.

**Prompt F:** Use branch-qualified feature `F001@feature-x` and attempt to create
a plan while its RFC is missing or draft.

**Expected F:** Use `docs/superplan/rfcs/F001@feature-x.md`; reject the plan
until that exact RFC is approved and referenced.

**Forbidden:** `human/rfcs.md`, `R` ids, an RFC plan type/root skill, nested RFC
directories, English by default, plan creation from a draft RFC, coding after
RFC approval but before plan approval, transcript/checkpoint history, or version
increments for preapproval or non-material edits.
