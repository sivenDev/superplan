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

## F006: Support GPT-5.6 Superpowers profile installation

- status: done
- created: 2026-07-20

为 Superplan 增加 GPT-5.6 专用 Superpowers profile 的安装与兼容流程：从 eagleagentic/superpowers-gpt-5.6 克隆外部依赖，在安装 Superplan 时选择并激活该 profile，使依赖检查、初始化和后续工作流能够使用其 13 个 skills 与 Codex 原生子代理能力。当前范围只支持 gpt-5.6；obra 官方 Superpowers、其他模型、运行时热切换和多 profile 通用化均延后。外部仓库不 vendoring 到 Superplan。

## F007: 精简高能力模型下的 Superplan skills

- status: done
- created: 2026-07-21

基于当前 Codex/GPT-5.6 的原生能力，整体审计 bundled skills、共享 references 与必要的界面元数据；删除无效、重复、解释性过强且模型已具备的说明，合并重复规则，保留 Superplan 的人工审批、工作区安全、风险分级、可追踪计划、验证和交付门禁。必要时同步测试与文档，确保精简后触发边界和脚本行为不退化。

## F008: 优化 Superplan 流程状态与验证逻辑

- status: done
- created: 2026-07-21

在保留实施计划审批、重要 Git 变更 worktree 授权、bug 根因/回归以及 human-plan-test-Git 追踪的前提下，优化流程逻辑：对明确且无歧义的新请求支持自适应 intake，减少 proposed/accepted 往返；批处理 approved 到 in_progress 及计划索引写入；仅在新增、拆分、范围或依赖变化时审查完整计划集；在工作区状态未变化时复用安全与依赖检查证据；按变更文件类型选择确定性验证矩阵；GPT-5.6 profile 替换必须先 dry-run 并取得明确授权；增加针对触发、intake、worktree、安全门和验证选择的行为级 skill 测试。

## F009: 优化 Superplan P0/P1 结构与运行时说明

- status: done
- created: 2026-07-21

处理已确认的 P0/P1：将初始化 human 模板资产化并与自适应 intake 对齐；统一已有工作区与初始化目标的 root 解析规则；把 GPT-5.6 profile 安装细节改为按需 reference；删除 managed guardrails 中通用 AI 开发原则；将脚本单元测试和 workflow behavior 场景移出运行时 skill 目录。继续在当前 worktree，保留并精确隔离 AGENTS.md 非 managed 用户改动。非目标：P2 human-plan 状态强校验、安装器/计划生成器大规模拆分、历史 spec 清理。

## F010: Clarify worktree numbering composition

- status: done
- created: 2026-07-21

补充 dirty-worktree 安全门与 linked-worktree 编号规则的组合场景：当主工作区存在未提交 F044、隔离 worktree 从 F043 基线开始时，新需求应使用 F044@branch，而不是误判为编号冲突；继续原工作区时才使用 F045。增加最小权威说明和行为测试，不修改现有编号算法，不重复扩写规则。
