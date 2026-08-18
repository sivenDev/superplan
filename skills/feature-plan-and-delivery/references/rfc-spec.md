# Feature RFC

RFC 是 feature 的可选设计阶段，不是独立需求类型。仅在以下情况启用：

- 人类明确要求 RFC；
- feature 已包含 `requires_rfc: true`；
- 直接规划会依赖未确认的架构、跨模块归属、公共契约、迁移、安全、并发、数据完整性、发布或回滚决策。

自主选择 RFC 时，先向人类说明具体风险，再运行：

```bash
python3 <using-superplan-root>/scripts/human_requests.py require-rfc --id <feature-id>
```

不能只因代码量、任务数量或对代码不熟悉而启用 RFC。人类明确拒绝时走直接 feature 流程；若仍存在重大风险，说明风险并重新请求确认，不得静默覆盖。

## 文档契约

单 RFC 是默认形式，路径为 `docs/superplan/rfcs/<feature-id>.md`，`id` 与 feature id 一致。仅当设计主题需要独立审批、版本或计划引用时，使用多 RFC 目录：

```text
docs/superplan/rfcs/<feature-id>/01-<slug>.md
docs/superplan/rfcs/<feature-id>/02-<slug>.md
```

同一 feature 的平铺文件与目录互斥。目录 RFC 使用 `id: "F001-R01"`、`feature: "F001"`，序号必须与文件名前缀一致；branch-qualified feature id 原样保留。默认使用中文；人类或项目文档规范明确要求其他语言时可覆盖。

必需 frontmatter：

```yaml
---
id: "F001"
title: "设计主题"
status: "draft"
version: 1
source: "docs/superplan/human/features.md"
created: "YYYY-MM-DD"
---
```

正文至少包含：摘要、背景或问题、目标、非目标、决策、已考虑的重要替代方案、风险与缓解措施、可观察的批准条件。兼容性、迁移、发布、回滚、安全或数据影响仅在相关时增加。不要写逐文件任务、实现代码、聊天记录或机械步骤。

## 状态、版本与留痕

- 状态只使用 `draft -> approved`；离开 `draft` 必须获得人类批准。
- 新 RFC 从 `version: 1` 开始；首次批准前修改不递增。
- approved RFC 的实质修改先恢复 `draft`，版本递增一次，再重新审批；纯文字或排版修正不递增。
- Git 是默认修订历史。保留影响当前决策的重要替代方案，不保存逐轮对话；仅在明确审计要求下增加简短的已批准版本记录。

展示 draft RFC 后停止，等待 RFC 审批。只有该 feature 的所有 RFC 都为 `approved` 后才能创建开发计划。平铺模式的每个计划引用唯一 RFC；目录模式的每个计划至少引用一份直接相关 RFC 的准确路径。RFC 审批不授权编码，开发计划仍需独立审批。
