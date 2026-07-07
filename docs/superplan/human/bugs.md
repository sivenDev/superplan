# Bugs

> 缺陷清单（人工维护）。每条缺陷一个 `## ` 小节，编号 `B001`、`B002` … 顺序递增、不复用。
>
> 录入方式（二选一）：
> - 对 AI 说“新建 bug: <标题>”，由 `$bugfix-plan-and-delivery` 的 intake 自动追加并编号；
> - 或手动复制下方模板，自行填下一个编号。
>
> 字段说明：
> - `status`：`proposed`(待人工复核) → `accepted`(已确认、可规划) → `done`(已修复)
> - `created`：创建日期，格式 `YYYY-MM-DD`
>
> 建议在描述里写清：复现步骤 / 期望结果 / 实际结果 / 影响范围。确认无误后把 `status` 改为 `accepted`。

<!-- 新增条目模板（把 B<NNN> 替换为下一个编号，例如 B001）：

## B<NNN>: 简短标题

- status: proposed
- created: YYYY-MM-DD

复现步骤：
1. ...
期望：... ／ 实际：...
-->

## B001: Feature intake body writes literal newline escapes

- status: proposed
- created: 2026-07-07

Screenshot symptom: a feature record was generated, but the recorder wrote body newlines as literal \n text in docs/superplan/human/features.md. Expected behavior: recorded feature body text should contain real Markdown line breaks so downstream planning tools can read it normally.
