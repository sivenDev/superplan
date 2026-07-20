# Features

> 功能需求清单（人工维护）。每条需求一个 `## ` 小节，编号 `F001`、`F002` … 顺序递增、不复用；linked worktree 中自动编号会追加分支限定，如 `F001@branch-slug`。
>
> 录入方式（二选一）：
> - 对 AI 说“新建 feature: <标题>”，由 `$feature-plan-and-delivery` 的 intake 自动追加并编号；
> - 或手动复制下方模板，自行填下一个编号。
>
> 字段说明：
> - `status`：`proposed`(待人工复核) → `accepted`(已确认、可规划) → `done`(已交付)
> - `created`：创建日期，格式 `YYYY-MM-DD`
>
> 确认某条无误后，把它的 `status` 改为 `accepted`，再交给 skill 规划实现。

<!-- 新增条目模板（把 F<NNN> 替换为下一个编号，例如 F001）：

## F<NNN>: 简短标题

- status: proposed
- created: YYYY-MM-DD

可选详细描述：目标 / 范围 / 验收标准 / 非目标。
-->

## F001: Prefer subagent-based plan decomposition and execution when safe

- status: done
- created: 2026-06-16

Update Superplan guidance so plan generation should prefer subagent-assisted decomposition when task boundaries are clear, and execution should prefer multiple subagents for independent work when correctness is not put at risk. This is a preference, not a hard requirement; correctness must take priority over efficiency. Apply this only in Superplan skills/references, not in injected `AGENTS.md` guardrails.

## F002: Support combined README write and check flags

- status: done
- created: 2026-06-16

Current behavior errors when `generate_plans_readme.py` is invoked with both `--write` and `--check`. Change it so this combination is supported instead: when both flags are present, run the equivalent of `--write` first and then `--check`, so callers do not need to serialize the two operations manually.

## F003: Worktree-aware feature and bug numbering

- status: done
- created: 2026-07-01

优化生成 bug 和 feature 编号逻辑：当处于 git worktree 时，生成的编号需要包含分支名称，避免多个 worktree 并行开发后合并时出现编号冲突。

## F004: Optimize Superplan for high-capability models

- status: done
- created: 2026-07-17

Refactor the Superplan workflow for high-capability models: add low, standard, and high risk profiles; use behavior-level rather than function-level testing; run focused verification during iteration and one final full verification; prefer single-agent execution for small and medium tasks; reserve subagents for truly independent or high-risk work; shorten plans and avoid embedding implementation code; use combined plan-index write and check; preserve human plan approval, bug root-cause analysis, and final evidence.

## F005: Prompt for worktree when important Git changes exist

- status: done
- created: 2026-07-20

开始 Superplan 流程时，先检查当前项目是否存在重要的 Git 变更；若存在，在继续 intake、规划或实现前询问用户是否要在当前项目中新建 worktree 执行后续流程。需要明确“重要变更”的判定、用户选择留在当前工作区时的行为，以及不重要的噪声变更不应触发询问。
