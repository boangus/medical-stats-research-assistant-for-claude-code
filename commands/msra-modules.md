---
description: MSRA Modules — manage experimental modules (medical imaging, bioinformatics, realtime analytics, cross-domain)
argument-hint: "list|info <module>|check <module>"
---

# MSRA Modules

管理 MSRA 扩展模块，传入用户参数 `$ARGUMENTS`。

## 参数解析

- `list` — 列出所有模块
- `info <module>` — 查看模块详情
- `check <module>` — 检查模块依赖

## 可用模块

| 模块 | 说明 | 入口命令 |
|------|------|---------|
| medical_imaging | 医学影像处理（DICOM/分割/分类） | `/msra-imaging` |
| bioinformatics | 生物信息分析（scRNA-seq/DE） | `/msra-bio` |
| realtime_analytics | 实时数据处理（流分析/异常检测） | `/msra-rt` |
| cross_domain | 跨域融合（radiomics-DEG/实时预测/多模态可视化） | `/msra-cross` |

## 调度

- `list` → 调用 `msra_modules.list_modules()`
- `info <module>` / `check <module>` → 调用 `msra_modules.check_module_dependencies(module)`

模块详细规格、门闸定义、依赖清单均在各模块 `skills/*/SKILL.md` 中定义。
