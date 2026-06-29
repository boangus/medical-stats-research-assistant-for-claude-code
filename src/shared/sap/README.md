# SAP 标准格式化机制

> MSRA 项目专用。解决 analysis-plan 到 analysis-exec 的 SAP 衔接问题。

---

## 问题背景

在 MSRA 流水线中，存在以下 SAP 衔接问题：

1. **格式不统一**：analysis-plan 输出 Markdown 格式，analysis-exec 需要解析
2. **缺乏验证**：没有检查 SAP 是否被正确解析和执行
3. **传递不明确**：没有定义 SAP 的标准格式和传递方式

## 解决方案

### 1. SAP 标准格式定义

**文件**: `sap_standard.md`

定义了 SAP 的标准格式，包括：
- Frontmatter 规范（study_id, version, status, study_type）
- 章节结构（Section 1-8）
- 变量构造定义格式
- 分析规范表格式

### 2. SAP 验证脚本

**文件**: `validate_sap.py`

功能：
- 验证 SAP 格式完整性
- 验证变量构造定义
- 验证分析规范表
- 生成验证报告

### 3. 阶段间 SAP 传递机制

```
Stage 2 (analysis-plan)
    ↓ 生成 sap_{study_id}_v1.0.md
    ↓ 进入 Stage 2.5 质量门闸
Stage 2.5 (SAP 质量门闸)
    ↓ 调用 validate_sap.py 验证
    ↓ 检查 SAP 完整性
    ↓ 标记 status: "approved"
    ↓ 进入 Stage 3
Stage 3 (analysis-exec)
    ↓ 调用 validate_sap.py 验证
    ↓ 读取 sap_{study_id}_v1.0.md
    ↓ 按 SAP 执行分析
```

## 使用方法

### 1. 生成 SAP（Stage 2）

在 `analysis-plan` 技能中，按标准格式生成 SAP：

```markdown
---
study_id: "RCT001"
version: "1.0"
status: "approved"
study_type: "RCT"
---

# 统计分析计划

## 1. 研究概述
...

## 7. 变量构造定义
| 变量名 | 类型 | 构造公式 | 切点/分类 | 依据 | 缺失处理 |
|--------|------|---------|----------|------|---------|
| age | 连续 | 入组日期 - 出生日期（年） | - | 标准人口学 | 删除 |

## 8. 分析规范表
| 分析ID | 分析名称 | 人群 | 方法 | 主要变量 | 调整变量 | 缺失处理 | 假设检验 |
|--------|---------|------|------|---------|---------|---------|---------|
| A1 | 主要终点分析 | ITT | ANCOVA | hba1c_change | baseline_hba1c, age | 多重插补 | F-test |
```

### 2. 验证 SAP（Stage 2.5 & Stage 3）

```python
from validate_sap import SAPValidator

validator = SAPValidator()
result = validator.validate_sap("sap_RCT001_v1.0.md")

if result["valid"]:
    print("SAP 验证通过")
else:
    print("SAP 验证失败")
    for issue in result["issues"]:
        print(f"  {issue['severity']}: {issue['message']}")
```

### 3. 执行 SAP（Stage 3）

在 `analysis-exec` 技能中：

1. Phase 0 首先验证 SAP 格式
2. 读取 SAP 分析规范表
3. 按 SAP 执行分析
4. 记录偏差（如有）

## 验证规则

### 格式验证
- Frontmatter 必须包含 study_id, version, status, study_type
- 章节必须包含 Section 1-8
- Section 7 必须包含变量构造定义表格
- Section 8 必须包含分析规范表

### 内容验证
- study_type 必须是 RCT/observational/diagnostic/bayesian/nmpa 之一
- status 必须是 draft/under_review/approved/locked 之一
- 变量构造定义必须包含所有分析变量
- 分析规范表必须包含所有分析

### 一致性验证
- SAP 中变量名与数据字典一致
- 所有方法在当前环境下可执行
- SAP 计划样本量与实际数据匹配

## 相关文件

| 文件 | 说明 |
|------|------|
| `sap_standard.md` | SAP 标准格式定义 |
| `templates/sap_template_rct.md` | RCT 统计分析计划模板 |
| `templates/sap_template_observational.md` | 观察性研究 SAP 模板 |
| `templates/sap_template_diagnostic.md` | 诊断试验 SAP 模板（含STARD/QUADAS-2整合） |
| `templates/sap_template_bayesian.md` | 贝叶斯分析 SAP 模板（PyMC/Stan） |
| `templates/sap_template_nmpa.md` | NMPA 申报专用 SAP 模板（含中国法规要求） |
| `validate_sap.py` | SAP 验证脚本 |
| `sap_to_code.py` | SAP 到代码转换（待实现） |
| `track_execution.py` | SAP 执行追踪（待实现） |

## 更新日志

### v0.2.0 (2026-06-19)
- 新增贝叶斯分析 SAP 模板 (`sap_template_bayesian.md`)
- 新增 NMPA 申报专用 SAP 模板 (`sap_template_nmpa.md`)
- 增强诊断试验 SAP 模板（整合 STARD 2015、QUADAS-2、估计目标框架）
- study_type 扩展支持: RCT/observational/diagnostic/bayesian/nmpa

### v0.1.0 (2026-05-30)
- 初始版本
- 定义 SAP 标准格式
- 实现 SAP 验证脚本
- 集成到 analysis-exec Phase 0

---

*维护者: MSRA开发团队*
*最后更新: 2026-06-19*