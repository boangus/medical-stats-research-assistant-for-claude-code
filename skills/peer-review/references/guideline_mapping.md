# Guideline Mapping

> 研究类型与报告规范映射表
> 适用: 方法学审稿人, 全部审稿人 | v0.9.0

---

## 核心映射表

| 研究类型 | 报告规范 | 清单位置 | 核心检查项 |
|----------|---------|---------|-----------|
| 随机对照试验 (RCT) | **CONSORT 2025** | `src/shared/reporting-guidelines/consort/` | 流程图、随机化、盲法、ITT |
| 队列研究 | **STROBE** | `src/shared/reporting-guidelines/strobe/` | 设计、参与者、变量、偏倚、混杂 |
| 病例对照研究 | **STROBE** | `src/shared/reporting-guidelines/strobe/` | 同上 + 匹配策略 |
| 横断面研究 | **STROBE** | `src/shared/reporting-guidelines/strobe/` | 同上 + 抽样方法 |
| 诊断准确性研究 | **STARD 2015** | `src/shared/reporting-guidelines/stard/` | 金标准、流程图、诊断性能 |
| 系统综述 (含/不含 Meta) | **PRISMA 2020** | `src/shared/reporting-guidelines/prisma/` | 检索策略、筛选、偏倚评估、GRADE |
| Meta 分析 | **PRISMA 2020** | `src/shared/reporting-guidelines/prisma/` | 异质性、模型选择、发表偏倚 |
| 预测模型 | **TRIPOD+AI** | `src/shared/reporting-guidelines/tripod/` | 开发/验证、性能指标、可及性 |
| 病例报告 | **CARE** | `src/shared/reporting-guidelines/care/` | 患者信息、时间线、教育意义 |
| 动物实验 | **ARRIVE 2.0** | `src/shared/reporting-guidelines/arrive/` | 3R 原则、随机化、盲法 |

---

## 扩展映射表

| 研究类型 | 报告规范 | 适用场景 |
|----------|---------|---------|
| RCT (非药物干预) | **CONSORT-NPT** | 手术/器械/行为干预 RCT |
| 整群随机试验 | **CONSORT-Cluster** | 以社区/医院为随机单位 |
| 非劣效性试验 | **CONSORT-NI** | 非劣效性/等效性设计 |
| 患者报告结局 | **PRO** | PRO 作为主要结局 |
| 因果推断 (观察性) | **STROBE + 因果推断补充** | 使用 DAG/MR 等方法 |
| 真实世界研究 | **RECORD / STROBE** | 使用电子健康记录 |
| 质量改进研究 | **SQUIRE** | 临床质量改进项目 |
| 定性研究 | **SRQR / COREQ** | 定性/混合方法研究 |
| 经济评价 | **CHEERS** | 成本-效果/成本-效用分析 |
| 悖论/现象报告 | **RIGHT** | 健康政策与系统研究 |
| 临床实践指南 | **RIGHT** | 临床指南制定 |

---

## 选择流程

```
Step 1: 识别研究类型
  ├── 有干预 + 随机分组 → RCT
  ├── 无干预 + 前瞻性随访 → 队列
  ├── 无干预 + 回顾性对照 → 病例对照
  ├── 无干预 + 横断面 → 横断面
  ├── 诊断性能评估 → 诊断准确性
  ├── 综合多个研究 → 系统综述/Meta 分析
  ├── 预测模型开发/验证 → 预测模型
  └── 单个病例 → 病例报告

Step 2: 匹配报告规范
  └── 查阅上方映射表选择对应规范

Step 3: 加载清单
  └── 从 src/shared/reporting-guidelines/ 加载对应清单

Step 4: 逐项检查
  └── 按清单逐项评估论文完成度
```

---

## 清单项严重性判定

| 完成情况 | 严重性 | 说明 |
|----------|--------|------|
| 核心项缺失 | CRITICAL | 流程图/随机化描述/检索策略等核心项 |
| 重要项缺失 | MAJOR | 参与者描述/统计方法/偏倚讨论等 |
| 补充项缺失 | MINOR | 图表格式/参考文献等 |
| 清单项完成 < 50% | MAJOR | 整体报告质量严重不足 |
| 清单项完成 > 80% | MINOR | 仅个别补充项缺失 |

---

## 偏倚风险评估工具映射

| 研究类型 | 推荐工具 | 位置 |
|----------|---------|------|
| RCT | **RoB 2** | `resources/risk-of-bias/` |
| 非随机干预研究 | **ROBINS-I** | `resources/risk-of-bias/` |
| 队列/病例对照 | **NOS (Newcastle-Ottawa)** | `resources/risk-of-bias/` |
| 系统综述 | **ROBIS** | `resources/risk-of-bias/` |
| 诊断准确性 | **QUADAS-2** | `resources/risk-of-bias/` |

---

## 引用

- `src/shared/reporting-guidelines/` — 全部报告规范清单
- `resources/risk-of-bias/` — 偏倚风险评估工具
- EQUATOR Network: https://www.equator-network.org/
