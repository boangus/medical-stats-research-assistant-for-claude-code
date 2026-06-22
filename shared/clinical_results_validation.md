# 临床结果验证规范

**Status**: v1.0.0 — 医学研究结果验证的综合规范

---

## § 1 — 概述

本规范定义了医学研究结果验证的完整框架，涵盖三个核心领域：
1. **金标准隔离** — 确保评估过程中ground truth的正确处理
2. **基准对比** — 与已发表结果的系统性比较
3. **可复现性验证** — 确保研究结果可被独立验证

本规范适用于临床研究、系统评价和循证医学分析。

---

## § 2 — 金标准隔离 (Gold Standard Isolation)

### 2.1 为什么金标准隔离重要

当评估代理在生成候选输出时能够读取评估答案键，它会直接针对评分标准而非底层任务进行优化。这导致分数膨胀，无法转移到保留数据上——这是典型的奖励黑客行为。

在医学研究中，这种失败模式可能导致：
- **偏倚的统计推断** — 模型学会预测评估者期望的答案而非真实结果
- **不可靠的验证结果** — 分数看起来很高但对新患者群体无效
- **伦理风险** — 可能影响临床决策和患者安全

### 2.2 三层思维模型

医学研究中的每个工件属于三个层次之一，流动方向严格单向：

**第一层 — 原始输入**
- 患者查询、主要研究来源
- 未经验证的文献和数据库检索结果
- 默认不信任，可能存在偏倚、错误或过时信息

**第二层 — 验证工件**
- 通过完整性检查的输出
- Semantic Scholar API确认存在性
- 反泄漏检查确认声明来自会话材料
- 引用存在性证明

**第三层 — 金标准和评估标准**
- 金标签、评审评分标准
- 校准集、预期输出
- **关键规则**：处理第一层或第二层输入并产生相应输出的代理，绝不能在其上下文窗口中包含第三层材料

### 2.3 医学研究实施规则

**DO：**
- 在SKILL.md中如实声明`data_access_level`
- 将评分标准文件与技能输入包分离
- 通过持有私有标准的评审代理传递分数

**DON'T：**
- 在代理读取的任何文件中嵌入答案键、评分标准或测试集标签
- 向生成候选输出的同一代理传递包含预期输出的评估提示
- 使用同一模型会话进行输出生成和输出评分

### 2.4 数据访问级别映射

| 级别 | 层次 | 含义 |
|---|---|---|
| `raw` | 第一层 | 操作于未验证来源；必须假设对抗性或幻觉输入 |
| `redacted` | 边界1→2 | 操作于无新原始摄入的净化材料 |
| `verified_only` | 第二层 | 仅在上游完整性检查通过后运行 |

---

## § 3 — 基准对比 (Benchmark Comparison)

### 3.1 为什么需要基准对比

在医学研究中，基准对比至关重要：
- **验证有效性** — 与已发表结果比较以确认方法的有效性
- **建立可信度** — 提供客观证据支持研究发现
- **识别偏差** — 发现可能影响结论的系统性差异

### 3.2 对比维度

#### 3.2.1 任务定义
- **描述**：研究任务的具体说明
- **任务类型**：结果可评分 vs 开放式
- **结果可分级**：是否可以使用标量度量评估

#### 3.2.2 人类基线
- **样本量**：基线研究的参与者数量
- **作者独立性**：作者是否独立于基准创建者
- **时间投入**：完成任务所需的小时数
- **工具允许**：允许使用的辅助工具

#### 3.2.3 系统运行
- **时间投入**：系统完成任务所需时间
- **成本**：运行系统的成本（美元）
- **技能使用**：使用的具体技能
- **数据访问级别声明**：raw/redacted/verified_only

#### 3.2.4 度量指标
- **主要指标**：核心评估指标
- **指标值**：主要指标的数值
- **评分独立性**：评分者的独立程度

### 3.3 医学研究基准对比实践

**标准流程：**
1. 选择相关文献作为基准
2. 提取关键性能指标
3. 使用相同数据集运行系统
4. 计算指标差异
5. 评估差异的统计显著性
6. 讨论差异的临床意义

**质量标准：**
- 基准选择必须具有代表性
- 数据集必须是公开可用的
- 评估方法必须透明可复现
- 必须报告差异的置信区间

---

## § 4 — 可复现性验证 (Reproducibility Verification)

### 4.1 可复现性原则

医学研究结果的可复现性是科学有效性的基石：

- **计算可复现性** — 使用相同数据和代码产生相同结果
- **方法可复现性** — 使用不同数据但相同方法产生一致结果
- **复制性** — 独立研究团队使用独立数据产生相似结果

### 4.2 验证要素

#### 4.2.1 数据层面
- 原始数据来源和获取方式
- 数据处理和清洗步骤
- 缺失数据处理方法
- 数据质量控制措施

#### 4.2.2 分析层面
- 统计方法的完整描述
- 软件版本和参数设置
- 随机种子和初始化条件
- 计算环境规范

#### 4.2.3 报告层面
- 结果呈现的标准化格式
- 补充材料的完整性
- 代码和数据的可获得性
- 利益冲突声明

### 4.3 验证检查清单

| 检查项 | 必需 | 说明 |
|---|---|---|
| 数据字典完整 | 是 | 每个变量都有明确定义 |
| 分析代码可运行 | 是 | 从原始数据到结果的完整流程 |
| 环境依赖声明 | 是 | 软件版本和硬件要求 |
| 随机种子记录 | 是 | 确保结果可精确复现 |
| 结果验证独立 | 强烈建议 | 由独立团队验证关键发现 |
| 敏感性分析 | 推荐 | 评估结果对方法假设的稳健性 |

---

## § 5 — 临床基准报告 JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "./shared/clinical_benchmark_report.schema.json",
  "title": "临床基准报告",
  "type": "object",
  "required": [
    "study_metadata",
    "validation_framework",
    "gold_standard_isolation",
    "benchmark_comparison",
    "reproducibility_verification",
    "caveats"
  ],
  "properties": {
    "study_metadata": {
      "type": "object",
      "required": ["study_id", "study_type", "sponsor", "irb_approval", "publication_date"],
      "properties": {
        "study_id": {
          "type": "string",
          "pattern": "^NCT\\d{8}$",
          "description": "ClinicalTrials.gov identifier"
        },
        "study_type": {
          "enum": ["randomized_controlled_trial", "cohort", "case_control", "cross_sectional", "systematic_review", "meta_analysis"],
          "description": "研究设计类型"
        },
        "sponsor": {
          "type": "string",
          "minLength": 1,
          "description": "研究资助方"
        },
        "irb_approval": {
          "type": "object",
          "required": ["approved", "irb_name", "approval_date"],
          "properties": {
            "approved": { "type": "boolean" },
            "irb_name": { "type": "string", "minLength": 1 },
            "approval_date": { "type": "string", "format": "date" },
            "approval_number": { "type": "string" }
          }
        },
        "publication_date": {
          "type": "string",
          "format": "date"
        },
        "registry_id": {
          "type": "string",
          "description": "研究注册号（如NCT编号）"
        }
      }
    },
    "validation_framework": {
      "type": "object",
      "required": ["data_access_level", "verification_method", "integrity_gates"],
      "properties": {
        "data_access_level": {
          "enum": ["raw", "redacted", "verified_only"],
          "description": "数据访问级别"
        },
        "verification_method": {
          "type": "string",
          "description": "验证方法说明"
        },
        "integrity_gates": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["gate_id", "gate_name", "passed", "timestamp"],
            "properties": {
              "gate_id": { "type": "string" },
              "gate_name": { "type": "string" },
              "passed": { "type": "boolean" },
              "timestamp": { "type": "string", "format": "date-time" },
              "details": { "type": "string" }
            }
          }
        }
      }
    },
    "gold_standard_isolation": {
      "type": "object",
      "required": ["isolation_implemented", "layer_mapping", "compliance_checks"],
      "properties": {
        "isolation_implemented": {
          "type": "boolean",
          "description": "是否实施了金标准隔离"
        },
        "layer_mapping": {
          "type": "object",
          "required": ["layer_1", "layer_2", "layer_3"],
          "properties": {
            "layer_1": {
              "type": "array",
              "items": { "type": "string" },
              "description": "原始输入层工件"
            },
            "layer_2": {
              "type": "array",
              "items": { "type": "string" },
              "description": "验证工件层"
            },
            "layer_3": {
              "type": "array",
              "items": { "type": "string" },
              "description": "金标准层工件"
            }
          }
        },
        "compliance_checks": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["check_name", "passed", "details"],
            "properties": {
              "check_name": { "type": "string" },
              "passed": { "type": "boolean" },
              "details": { "type": "string" }
            }
          }
        }
      }
    },
    "benchmark_comparison": {
      "type": "object",
      "required": ["reference_studies", "metrics_comparison", "statistical_analysis"],
      "properties": {
        "reference_studies": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["citation", "doi", "key_findings"],
            "properties": {
              "citation": { "type": "string" },
              "doi": { "type": "string" },
              "key_findings": { "type": "string" }
            }
          }
        },
        "metrics_comparison": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["metric_name", "current_value", "reference_value", "difference", "clinical_significance"],
            "properties": {
              "metric_name": { "type": "string" },
              "current_value": { "type": "number" },
              "reference_value": { "type": "number" },
              "difference": { "type": "number" },
              "confidence_interval": {
                "type": "object",
                "properties": {
                  "lower": { "type": "number" },
                  "upper": { "type": "number" }
                }
              },
              "clinical_significance": {
                "enum": ["superior", "equivalent", "inferior", "uncertain"]
              }
            }
          }
        },
        "statistical_analysis": {
          "type": "object",
          "properties": {
            "test_used": { "type": "string" },
            "p_value": { "type": "number" },
            "effect_size": { "type": "number" },
            "sample_size_calculation": { "type": "string" }
          }
        }
      }
    },
    "reproducibility_verification": {
      "type": "object",
      "required": ["computational_reproducibility", "methodological_reproducibility", "reporting_completeness"],
      "properties": {
        "computational_reproducibility": {
          "type": "object",
          "required": ["code_available", "data_available", "environment_specified"],
          "properties": {
            "code_available": { "type": "boolean" },
            "code_repository": { "type": "string" },
            "data_available": { "type": "boolean" },
            "data_repository": { "type": "string" },
            "environment_specified": { "type": "boolean" },
            "dependencies": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "version": { "type": "string" },
                  "type": { "enum": ["software", "library", "package"] }
                }
              }
            }
          }
        },
        "methodological_reproducibility": {
          "type": "object",
          "required": ["methods_described", "parameters_documented", "sensitivity_analyses"],
          "properties": {
            "methods_described": { "type": "boolean" },
            "parameters_documented": { "type": "boolean" },
            "random_seed_recorded": { "type": "boolean" },
            "sensitivity_analyses": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "reporting_completeness": {
          "type": "object",
          "required": ["data_dictionary", "supplementary_materials", "conflict_of_interest"],
          "properties": {
            "data_dictionary": { "type": "boolean" },
            "supplementary_materials": { "type": "boolean" },
            "conflict_of_interest": { "type": "boolean" },
            "funding_disclosure": { "type": "boolean" }
          }
        }
      }
    },
    "caveats": {
      "type": "array",
      "items": { "type": "string", "minLength": 1 },
      "minItems": 1,
      "description": "已知限制和注意事项。空数组不允许——需要诚实披露。"
    }
  }
}
```

---

## § 6 — 实施指南

### 6.1 数据流控制

```
原始数据 → 验证检查 → 隔离存储 → 评估时加载 → 结果输出
   ↓           ↓           ↓           ↓           ↓
 第一层    边界检查    第二层      第三层隔离    验证报告
```

### 6.2 评估工作流程

1. **准备阶段**：确认数据访问级别，隔离金标准材料
2. **执行阶段**：运行分析，记录所有参数和中间结果
3. **验证阶段**：与基准比较，评估可复现性
4. **报告阶段**：生成结构化报告，包含所有验证证据

### 6.3 质量保证检查点

| 检查点 | 检查内容 | 通过标准 |
|---|---|---|
| 数据完整性 | 原始数据未被篡改 | 哈希校验一致 |
| 方法合规 | 分析方法符合方案 | 预注册方案一致 |
| 结果有效 | 统计检验有效 | 假设检验条件满足 |
| 可复现性 | 代码和数据可获取 | 独立运行产生相同结果 |

---

## § 7 — 参考资源

- `shared/handoff_schemas.md` — 声明式注解
- `shared/passport/` — 材料护照管理
- `shared/calibration/` — 度量校准框架
- `shared/statistics-methods/` — 统计方法目录
- `shared/anti-patterns/` — 反模式目录

---

## 版本历史

- v1.0.0 (2026-06-21): 初始版本，合并金标准隔离、基准对比、可复现性验证三个模式
