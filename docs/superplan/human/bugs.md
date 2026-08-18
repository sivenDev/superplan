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

- status: done
- created: 2026-07-07

Screenshot symptom: a feature record was generated, but the recorder wrote body newlines as literal \n text in docs/superplan/human/features.md. Expected behavior: recorded feature body text should contain real Markdown line breaks so downstream planning tools can read it normally.

## B002: Resolve Superplan skill routing and validation gaps

- status: done
- created: 2026-07-30

修复审查确认的四项问题：多计划请求不得提前标记 done；PRD 路由不得绕过版本化 workspace 迁移；using-superplan 元数据必须覆盖初始化、检查和迁移触发；仓库 Skill 验证必须在无外部 PyYAML 假设下可重复执行。

## B003: Add safe legacy registry migration

- status: done
- created: 2026-07-31

为旧版 Superplan human registry 增加显式、可预览的迁移流程：只处理缺失 status/created 的历史条目，dry-run 展示建议值和证据，无法可靠推断时拒绝写入；不让 init_workspace 自动修改 human 数据，不放宽正常 record 的严格校验。

## B004: Accept Codex Cachebuster Build Metadata in Package Contract

- status: done
- created: 2026-08-18

The committed Codex plugin manifest uses SemVer build metadata (0.4.0+codex.20260804101449) to refresh the plugin cache, while the package contract requires exact equality with the canonical 0.4.0 version and therefore breaks focused and repository verification. Preserve exact canonical versions for the shared version module, Claude manifest, and marketplace; allow only the Codex manifest to append valid build metadata whose base version matches the canonical version. Do not remove or regenerate the current cachebuster. Acceptance: the focused package contract and full repository verifier pass.
