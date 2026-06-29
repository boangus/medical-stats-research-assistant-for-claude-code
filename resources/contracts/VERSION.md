# Schema 版本管理规范

## 版本号规则

所有 `resources/contracts/` 下的 JSON Schema 文件以及 `shared/` 根目录下的
`compliance_report.schema.json`、`sprint_contract.schema.json` 统一采用语义化版本号
（Semantic Versioning），通过顶层 `"version"` 字段标识：

- **MAJOR**: 不兼容的 Schema 结构变更（如字段删除 / 重命名 / 类型变更）
- **MINOR**: 向后兼容的新增字段
- **PATCH**: 文档 / 描述修正

版本号字段位置：紧跟 `$id`（有 `$id` 时）或 `$schema`（无 `$id` 时）之后，
位于 `title` / `contract_id` / `description` 等其他元数据之前。

## 当前版本: 1.0.0

Sprint 3 首次统一引入 `version` 字段，所有文件初始版本号为 `1.0.0`。

## 标准格式

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://msra.dev/schemas/{category}/{name}.schema.json",
  "version": "1.0.0",
  "title": "...",
  ...
}
```

## 文件清单

| 文件 | 版本 |
|------|------|
| resources/shared/compliance_report.schema.json | 1.0.0 |
| resources/shared/sprint_contract.schema.json | 1.0.0 |
| resources/contracts/audit/audit_jsonl.schema.json | 1.0.0 |
| resources/contracts/audit/audit_sidecar.schema.json | 1.0.0 |
| resources/contracts/audit/audit_verdict.schema.json | 1.0.0 |
| resources/contracts/evaluator/full.json | 1.0.0 |
| resources/contracts/reviewer/full.json | 1.0.0 |
| resources/contracts/reviewer/methodology_focus.json | 1.0.0 |
| resources/contracts/passport/analysis_execution.json | 1.0.0 |
| resources/contracts/passport/analysis_plan.json | 1.0.0 |
| resources/contracts/passport/calibration_result.json | 1.0.0 |
| resources/contracts/passport/data_preparation.json | 1.0.0 |
| resources/contracts/passport/data_quality_gate.json | 1.0.0 |
| resources/contracts/passport/exploratory_causal.json | 1.0.0 |
| resources/contracts/passport/manuscript_draft.json | 1.0.0 |
| resources/contracts/passport/report_generation.json | 1.0.0 |
| resources/contracts/passport/results_quality_gate.json | 1.0.0 |
| resources/contracts/passport/sap_quality_gate.json | 1.0.0 |

共 18 个文件，全部统一为 `1.0.0`。

## 版本兼容性策略

1. Passport 加载时检查 Schema 版本
2. 版本不匹配时自动迁移（`resources/contracts/migrations/`）
3. 迁移日志记录到 audit_log

## 维护说明

- 新增 Schema 文件时**必须**包含 `"version": "1.0.0"` 字段
- 修改 Schema 结构时按语义化版本规则递增版本号
- 修改完成后更新本文件的「文件清单」表格
