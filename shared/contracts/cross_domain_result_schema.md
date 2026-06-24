# Schema Contract: msra/cross_domain_result/v1

> **版本**: v1.0 | **日期**: 2026-06-25 | **状态**: Active
> **项目**: MSRA (Medical Statistics Research Assistant)

---

## 1. 概述

`msra/cross_domain_result/v1` 是 cross_domain 跨领域融合模块的标准化输出 Schema。
该 Schema 定义了跨模态融合分析（关联分析、预测模型、多模态可视化）结果的文件结构和字段规范。

---

## 2. 输出目录结构

```
output_dir/
├── correlation_results.csv     # 关联分析结果表
├── model_metrics.json           # 模型评估指标
├── visualization_bundle/        # 可视化文件包
│   ├── linked_view.png          # 四象限联动视图
│   └── summary_dashboard.png    # 摘要仪表盘
└── cross_domain_report.md       # 综合报告
```

---

## 3. 字段定义

### 3.1 correlation_results.csv

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `feature` | str | ✅ | 影像组学特征名 |
| `gene` | str | ✅ | 基因名 |
| `correlation` | float | ✅ | 相关系数 [-1.0, 1.0] |
| `p_value` | float | ✅ | 原始 p 值 [0.0, 1.0] |
| `p_adj` | float | ✅ | FDR 校正后 p 值 [0.0, 1.0] |
| `significant` | bool | ✅ | 是否显著 (p_adj < 0.05 & \|r\| ≥ 0.3) |
| `method` | str | ✅ | 相关方法 (pearson/spearman/kendall) |

### 3.2 model_metrics.json

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `accuracy` | float | ✅ | 准确率 [0.0, 1.0] |
| `precision` | float | ✅ | 精确率 [0.0, 1.0] |
| `recall` | float | ✅ | 召回率 [0.0, 1.0] |
| `f1` | float | ✅ | F1 分数 [0.0, 1.0] |
| `auroc` | float | ✅ | AUROC [0.0, 1.0] |
| `model_type` | str | ✅ | 模型类型 (logistic/random_forest) |
| `n_samples` | int | ✅ | 训练样本数 |
| `n_features` | int | ✅ | 特征数 (固定 10) |

### 3.3 visualization_bundle/

| 文件 | 格式 | 必填 | 说明 |
|------|------|------|------|
| `linked_view.png` | PNG | ✅ | 四象限联动视图 (影像+表达+临床+实时) |
| `summary_dashboard.png` | PNG | ✅ | 摘要仪表盘 |

### 3.4 cross_domain_report.md

| 章节 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `# Cross-Domain Analysis Report` | markdown | ✅ | 综合报告标题 |
| `## 1. Summary` | markdown | ✅ | 摘要（含关联分析/模型/可视化结果） |
| `## 2. Output Files` | markdown | ✅ | 输出文件路径列表 |
| `## 3. Quality Gate` | markdown | ✅ | 质量门闸结果引用 |

---

## 4. 元数据字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `schema_version` | str | ✅ | 固定值 `"msra/cross_domain_result/v1"` |
| `study_id` | str | ✅ | 研究编号 |
| `scenario` | str | ✅ | 场景类型 (`correlation` / `prediction` / `visualization` / `full`) |
| `timestamp` | str (ISO 8601) | ✅ | 生成时间戳 (UTC) |

---

## 5. 与其他 Schema 的关系

| Schema | 方向 | 说明 |
|--------|------|------|
| `msra/imaging_features/v1` | 输入 | medical_imaging 模块的特征矩阵作为 radiomics 数据源 |
| `msra/bioinformatics_result/v1` | 输入 | bioinformatics 模块的表达矩阵作为 expression 数据源 |
| `msra/realtime_metrics/v1` | 输入 | realtime_analytics 模块的时序数据作为 realtime 数据源 |
| `msra/cross_domain_result/v1` | 输出 | 本 Schema，可接入主 Pipeline Stage 3 |

---

## 6. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-06-25 | 初始版本，定义 correlation_results.csv + model_metrics.json + visualization_bundle/ + cross_domain_report.md |

---

**文档结束**
