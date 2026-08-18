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

## F012: Progressive Superplan state discovery and script organization

- status: done
- created: 2026-07-30

优化大型 Superplan 工作区的上下文、初始化和运行时脚本结构：将固定版本的 GPT-5.6 Superpowers skills 作为仓库内 `deps/superpowers` 依赖由插件直接暴露，移除 `init_workspace.py` 的用户级 Superpowers 安装检查及对应安装器；在 managed guardrail 中记录 workspace schema 与生成版本，路由自动执行只读兼容检查，并在旧 schema 上进入安全迁移流程。正常任务通过确定性命令读取紧凑 human/plan 目录并按 ID、依赖、source、范围或搜索结果加载相关全文，保留全局元数据验证和完整相关计划审查，避免默认读取累积历史全文。整理 `using-superplan/scripts` 时优先删除失去职责的 profile 脚本，保留仍有价值的公开 CLI，避免用巨型单文件换取表面文件数减少。当前仓库历史中的 F011 已使用后撤销，本条保留该编号并从 F012 继续。

## F013: Integrate effective workflow guidance into Superplan

- status: done
- created: 2026-07-30

审计当前 `deps/superpowers` 的 13 个 GPT-5.6 workflow skills，将真正改变 Superplan 行为边界的调试、worktree、测试和高风险验证规则精简后并入现有 route-owned references；删除重复于 GPT-5.6、项目 guardrails 或 Superplan delivery loop 的独立 skills、visual companion、依赖目录、lock 和 supplemental plugin discovery。最终只暴露现有四个 Superplan skills，详细规则按场景条件加载；已完成的 human/plan 历史记录保持不变。

## F014: Harden Superplan state integrity and verification

- status: done
- created: 2026-07-31

目标：优先解决高收益的正确性与交付风险。

范围：统一校验 human registry 与 plan 状态关系；为 registry、workspace migration、guardrail 和 plan index 写入增加并发变化检测、原子替换与多文件失败恢复；提供一个标准库实现的仓库验证入口并接入最小 CI。

验收：非法 human/plan 组合会被全局校验拒绝；关键写入不会静默覆盖并发修改或留下可避免的半完成状态；贡献者和 CI 使用同一条权威命令运行完整检查。

非目标：不增加数据库或向量搜索，不继续压缩 skill 文案，不按文件大小机械拆分脚本，不在本次建设完整的模型行为评测平台。

## F015: Automatically resolve non-blocking Superplan migration conflicts

- status: done
- created: 2026-07-31

When compatibility or migration checks surface historical consistency problems, Superplan should verify current state and classify whether they affect the active task. Continue automatically when the workspace is compatible or the problems are unrelated. When an independent migration is useful, isolate it from the active task and delegate it when safe. Ask the user only when isolation is unsafe, the active-task baseline would change, or new authority is required. Preserve approval, workspace-safety, verification, and separate-commit boundaries.

## F016: Require post-worktree delivery handoff

- status: done
- created: 2026-08-04

当 Superplan 在 linked worktree 中完成开发、验证和任务提交后，必须明确说明开发已完成，并询问用户是否将该分支合并到主干、是否删除对应 worktree 工作目录。未经明确确认，不自动合并或删除。

## F017: Standardize Project-Local Worktree Location

- status: done
- created: 2026-08-18

When Superplan controls linked-worktree placement, use the primary project root .worktrees directory by default and require that directory to be Git-ignored. An explicit user path overrides the default. Reuse a suitable current linked worktree instead of nesting another one. Do not constrain branch names or worktree child-directory names; if a harness cannot honor the location, report the actual path without moving it.

## F018: Release Superplan 0.4.1

- status: done
- created: 2026-08-18

Publish Superplan version 0.4.1 by replacing the Codex manifest cachebuster version with the exact release version 0.4.1 and synchronizing every current version source, plugin manifest, marketplace entry, managed generator marker, documentation example, and package-contract assertion. Preserve workspace schema 1 and historical request/plan evidence. Acceptance: all active version surfaces report 0.4.1, generated workspace artifacts are current, and focused plus full repository verification pass.

## F019: Add Optional RFC Stage to Feature Delivery

- status: done
- created: 2026-08-18

- requires_rfc: true

Add an optional RFC design stage inside the existing feature lifecycle. The feature remains the sole human request and completion entity. Enter the RFC stage when the human explicitly requests it or when the agent identifies material architectural ambiguity, cross-module boundaries, public contracts, data migration, security, or complex dependencies; the agent must state its reasoning. Do not require an RFC solely because a task is large. If the human explicitly declines an RFC, respect that choice unless material risk requires renewed confirmation. RFC documents default to Chinese unless the human explicitly requests another language or the project defines a different documentation language. For RFC-required features, create an RFC at docs/superplan/rfcs/<feature-id>.md and obtain human approval before creating implementation plans under docs/superplan/plans/features/<feature-id>/. Define one concise RFC authoring specification with a required positive-integer version: new RFCs start at version 1, draft edits before first approval do not increment it, and material changes to an approved RFC increment it before reapproval. Drafts retain the current authoritative decisions and important alternatives, while Git history is the default revision record and per-conversation logs are omitted unless explicitly required for audit. Do not add human/rfcs.md, a separate RFC request type, plan type, or root skill.

## F020: Create safe checkpoint commits before human-decision pauses

- status: done
- created: 2026-08-18

When a Superplan workflow must pause for human confirmation after the current task has produced persistent changes, validate the changed artifacts, stage only current-task paths or hunks, and create a checkpoint commit before returning control so concurrent worktrees do not inherit avoidable dirty state. Do not commit when there are no changes, do not include pre-existing, user-owned, or unrelated changes, and do not checkpoint a known invalid or unsafe state. Keep final delivery commits distinct, and do not rewrite checkpoint commits once another worktree or branch may depend on them.

## F021: Release Superplan 0.6.0 and refresh local Codex installation

- status: done
- created: 2026-08-18

Publish the completed F020 workflow as Superplan 0.6.0 while keeping workspace schema 1. Synchronize all active version surfaces and validation expectations, create a dedicated release commit, and push main to git@github.com:sivenDev/superplan.git only after confirming the remote main head has not moved. Then update the existing local Codex installation from the confirmed local superplan-dev marketplace using the plugin-creator cachebuster and reinstall flow, verify the installed plugin loads the new F020 checkpoint guidance, restore the repository manifest to the exact release version, and leave the worktree clean. Do not edit marketplace configuration by hand or create a new marketplace.

## F022: Support Multiple RFCs per Feature

- status: done
- created: 2026-08-18
- requires_rfc: true

允许一个 feature 在确有独立设计审批边界时拥有多个 RFC，同时保留现有单 RFC 平铺路径。单 RFC 继续使用 docs/superplan/rfcs/<feature-id>.md；多 RFC 使用 docs/superplan/rfcs/<feature-id>/NN-<slug>.md，且两种布局对同一 feature 互斥。多 RFC 使用独立 RFC id（例如 F022-R01）和显式 feature 归属，避免与 F022-01 形式的 plan id 混淆。所有 RFC 必须获批后才能创建非 superseded 开发计划；每个计划只引用其直接依赖的 RFC，并至少引用一个匹配 RFC。现有平铺 RFC 无需迁移，branch-qualified feature id 必须继续工作。更新解析、跨产物校验、skill/reference、workspace guidance、README、行为场景和自动化测试。

## F023: Raise the Automatic RFC Trigger Threshold

- status: accepted
- created: 2026-08-18

收紧 feature 流程中 AI 自动启用 RFC 的门槛，避免仅因命中架构、跨模块或风险关键词就增加 RFC。只有同时存在具体未决设计问题、多个会实质改变方案的选项或单个难以逆转的决策、错误选择会改变验收或形成公共契约/迁移/安全/并发/数据完整性/发布回滚风险，并且无法通过一次澄清、保守默认或普通开发计划安全解决时，AI 才能自动设置 requires_rfc: true。可逆内部实现选择、任务规模、文件/模块数量、代码不熟悉和一般不确定性不触发 RFC；边界情况先提出一个简短澄清问题。人类显式要求或已持久化 requires_rfc: true 的行为保持不变。更新 feature skill、RFC reference、行为场景和包契约测试；不改变运行时脚本、workspace schema 或版本。
