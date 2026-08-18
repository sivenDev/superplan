# Features

> 功能需求清单（人工维护）。每条需求一个 `## ` 小节，编号 `F001`、`F002` … 顺序递增、不复用；linked worktree 中自动编号会追加分支限定，如 `F001@branch-slug`。
>
> 录入方式：对 AI 说“新建 feature: <标题>”，或手动复制下方模板。
>
> `status`：`proposed`（默认，待人工复核）→ `accepted`（已确认、可规划）→ `done`（已交付）。仅当用户明确授权录入并继续规划、内容忠实且不存在实质歧义时，AI 才可直接记录为 `accepted`；否则保持 `proposed` 并等待复核。`accepted` 只批准规划，不批准实施。
>
> `requires_rfc: true` 为可选字段，缺失时按 `false`。人类明确要求或 AI 说明实质设计风险后，可在创建计划前启用。单 RFC 默认保存于 `docs/superplan/rfcs/<feature-id>.md`；只有独立审批、版本或计划引用边界才使用 `docs/superplan/rfcs/<feature-id>/NN-<slug>.md`，两种布局互斥。RFC 默认使用中文；所有 RFC 批准后才能创建开发计划，计划仍需单独批准后才能编码。

<!-- 新增条目模板（把 F<NNN> 替换为下一个编号，例如 F001）：

## F<NNN>: 简短标题

- status: proposed
- created: YYYY-MM-DD

可选详细描述：目标 / 范围 / 验收标准 / 非目标。
-->
