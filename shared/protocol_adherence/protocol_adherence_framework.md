---
title: 协议执行规范与变更管理框架
version: 1.0.0
applies_to:
  - skills/analysis-exec/SKILL.md
  - skills/pipeline/SKILL.md
  - skills/report/SKILL.md
  - shared/sap/sap_standard.md
  - shared/compliance_checkpoint_protocol.md
scope: "Stage 2 SAP 确认 → Stage 3 分析执行 → Stage 4 报告生成全周期"
---

# 协议执行规范与变更管理框架

> 本文档定义统计分析方案（SAP）从确认到执行全流程的规范化管理机制，
> 涵盖方案执行纪律、变更流程、进度跟踪、质量控制及特殊分析要求。
> 所有 MSRA Pipeline Stage 2-4 的分析活动必须遵循本框架。

---

## 目录

1. [方案执行规范](#1-方案执行规范)
2. [方案变更流程](#2-方案变更流程)
3. [进度跟踪机制](#3-进度跟踪机制)
4. [统计分析方案完成情况报告](#4-统计分析方案完成情况报告)
5. [质量控制标准](#5-质量控制标准)
6. [特殊分析项目要求](#6-特殊分析项目要求)
7. [集成指南](#7-集成指南)

---

## 1. 方案执行规范

### 1.1 核心原则

| # | 原则 | 说明 |
|---|------|------|
| P1 | **SAP 唯一性** | SAP 一经确认即为执行唯一依据，不得口头约定或非正式调整 |
| P2 | **偏离必记录** | 任何偏离必须通过变更管理流程（§2）记录并获得用户确认 |
| P3 | **代码可追溯** | 代码必须可追溯到 SAP 条目 |
| P4 | **可复现性** | 随机种子、数据版本、软件环境必须完整记录 |
| P5 | **透明性** | 未执行 SAP 条目必须有明确跳过理由 |

**适用范围**: 本框架适用于 Stage 2（分析计划确认后）至 Stage 4（统计报告完成）的所有分析活动。Stage 1 数据准备阶段和 Stage 5 论文写作阶段有各自独立的规范。

### 1.2 SAP 与代码映射要求

#### 1.2.1 映射格式规范

每段分析代码必须标注对应 SAP 条目编号：

```python
# SAP §3.2: 主要结局 — Kaplan-Meier 生存分析
from lifelines import KaplanMeierFitter
kmf = KaplanMeierFitter()
for group in [0, 1]:
    mask = df['treatment'] == group
    kmf.fit(df.loc[mask, 'follow_up_days'], df.loc[mask, 'overall_survival'], label=f"Group {group}")
    kmf.plot_survival_function()
```

```r
# SAP §4.1: 敏感性分析 — Cox 回归（排除失访病例）
library(survival)
cox_sensitivity <- coxph(Surv(follow_up_days, overall_survival) ~ treatment + age + sex, data = analysis_sensitivity)
```

#### 1.2.2 映射完整性要求

- **全覆盖**: SAP 每条分析必须有对应代码
- **无遗漏**: 不得存在 SAP 有但代码无的条目
- **无多余**: 不得存在代码有但 SAP 无的条目（探索性除外）
- **编号一致**: 代码标注的 SAP 编号必须是 SAP 中实际存在的

#### 1.2.3 探索性分析标记

未经 SAP 预设的探索性分析必须使用 `# [EXPLORATORY]` 标记，且不得与确证性分析在同一数据集上交叉执行。

### 1.3 禁止行为清单

以下行为在分析执行过程中**严格禁止**：

| # | 禁止行为 | 原因 | 违反后果 |
|---|---------|------|---------|
| F1 | 未记录更换统计方法 | 破坏可追溯性 | 变更请求 + 偏差日志 |
| F2 | 删除预设敏感性分析 | 降低完整性 | 变更请求 + 用户确认 |
| F3 | 修改主要结局定义 | 影响有效性 | A 类变更 + 重新确认 |
| F4 | 分析完成后反向调整 SAP | 研究诚信违规 | 变更无效 + 重新分析 |
| F5 | 同一数据上探索+确证分析 | selection bias | 分离数据集 |
| F6 | 选择性报告分析结果 | reporting bias | 必须报告全部 SAP 条目 |
| F7 | 隐瞒假设违反情况 | 影响可靠性 | 必须记录并报告 |
| F8 | 未经确认跳过预设分析 | 降低完整性 | 变更请求 + 理由记录 |
| F9 | 多中心使用中心特异性标准 | 系统性偏倚 | 统一标准 |
| F10 | 分析后调整样本量或亚组 | P-hacking 嫌疑 | 完整记录 + 用户确认 |

**监控**: Stage 3.5 质量门闸自动检查上述行为，违规触发 FAIL 循环。

---

## 2. 方案变更流程

### 2.1 触发条件

以下三种情况必须暂停并请求用户确认：

| 触发条件 | 场景 | 处理方式 |
|---------|------|---------|
| **(a) 理解歧义** | SAP 条目内容存在多种理解 | 暂停 → 列出歧义点 → 请求澄清 |
| **(b) 数据与假设冲突** | 分布假设不满足、样本量不足 | 暂停 → 报告诊断 → 请求调整 |
| **(c) 方法/范围调整** | 需要更换统计方法或增减分析 | 暂停 → 提出变更请求 → 等待确认 |

场景示例：(a) SAP 未明确协变量或亚组分层标准；(b) 正态性 P<0.01、样本量不足、缺失>20%；(c) parametric→non-parametric

### 2.2 变更请求模板

```markdown
## 方案变更请求

**请求编号**: CR-{YYYY-MM-DD}-{序号} | **请求日期**: {YYYY-MM-DD}
**请求人**: {角色} | **影响 SAP 条目**: §{编号}

### 变更类型
- [ ] 方法变更  [ ] 变量变更  [ ] 分析范围变更  [ ] 结局定义变更  [ ] 其他

### 变更原因
{详细描述触发变更的数据特征或问题}

### 建议变更内容
| 项目 | 原方案 | 建议修改 | 理由 |
|------|--------|---------|------|
| {分析方法} | {原 SAP} | {修改后} | {为什么改} |

### 影响评估
- 对主要结论的潜在影响: {高 / 中 / 低}
- 是否影响样本量: {是 / 否}

### 用户确认
- [ ] 用户已审阅并书面确认同意
- 确认日期: ___ | 确认方式: {邮件 / 会议纪要}
```

变更请求编号格式: `CR-{YYYY-MM-DD}-{三位序号}`（如 `CR-2026-06-21-001`）

### 2.3 变更分类与审批级别

| 类别 | 示例 | 审批 | 记录 |
|------|------|------|------|
| **A 类: 主要结局** | 更换主要终点 | 书面确认 + 更新 SAP | SAP 修订 + CR + 偏差日志 |
| **B 类: 方法变更** | t检验→Wilcoxon | 书面确认 | 变更请求 + 偏差日志 |
| **C 类: 次要调整** | 小数位数、表格格式 | 口头确认 | 偏差日志 |
| **D 类: 编码修正** | Bug 修复、变量名统一 | 无需确认 | 代码注释 |

#### 各类别详细说明

- **A 类**: 正式变更请求 + SAP 修订 + 通知协作者 + 重新执行所有受影响分析；若涉及已提交伦理审查，可能需补充审查
- **B 类**: 须说明原方法不适用原因 + 提供诊断证据（如正态性/方差齐性检验）+ 重新执行受影响分析
- **C 类**: 不影响结论的格式调整（表格对齐、P 值精度等），记录偏差日志即可
- **D 类**: 代码 Bug 修复，不影响分析逻辑，仅需代码注释

### 2.4 变更后同步更新

变更确认后必须按顺序更新：①SAP 文档（修订版本+日期）②偏差日志（偏离内容+审批）③进度表（受影响图表状态）④分析代码（变更注释+CR 编号）

#### SAP 修订记录格式

```markdown
| 版本 | 日期 | CR 编号 | 变更内容 | 审批人 |
|------|------|---------|---------|--------|
| v1.0 | 2026-06-01 | — | 初始版本 | — |
| v1.1 | 2026-06-21 | CR-2026-06-21-001 | §3.2: t检验→Wilcoxon | 用户 |
```

#### 偏差日志格式

```markdown
| 编号 | 日期 | SAP 条目 | 类型 | 描述 | 审批 | 状态 |
|------|------|---------|------|------|------|------|
| DV-001 | 2026-06-21 | §3.2 | B 类 | 正态性 P<0.01，改用 Wilcoxon | 用户确认 | 已关闭 |
```

---

## 3. 进度跟踪机制

### 3.1 进度表格式规范

进度表每条分析条目包含三行：编号、标题、状态。状态选项：

| 状态 | 含义 | 允许操作 |
|------|------|---------|
| **未开始** | 尚未开始执行 | 可调整顺序，不可跳过 |
| **进行中** | 正在执行 | 可暂停（需记录原因） |
| **已完成** | 执行完毕且通过自检 | 可进入质量核查 |
| **需修订** | 执行完毕但存在问题 | 必须附修订原因，修订后重新标记 |

### 3.2 进度表示例

```
分析进度表 — {研究名称} | 更新日期: 2026-06-21 | SAP: v1.1

编号  | 标题                                    | 状态
------|-----------------------------------------|--------
表1   | 研究对象基线资料比较                     | 已完成
表2   | 主要结局指标单因素分析                   | 进行中
表3   | 多因素回归分析结果                       | 未开始
表4a  | 倾向性评分模型（Logistic 回归）         | 未开始
表4b  | 匹配前后协变量平衡性检验（SMD < 0.1）   | 未开始
表4c  | 匹配后样本特征描述                       | 未开始
表5   | 匹配后 Kaplan-Meier 生存分析             | 未开始
表6   | 匹配后 Cox 回归分析                      | 未开始
图1   | 倾向性评分分布（匹配前后对比）           | 未开始
图2   | 协变量 SMD 蝴蝶图                        | 未开始
图3   | 匹配后生存曲线                           | 未开始
```

### 3.3 进度表更新规则

- **即时更新**: 每完成一个图表/表格必须立即更新状态
- **修订附因**: "需修订"状态必须附修订原因
- **100% 对应**: 进度表与实际图表必须 100% 对应
- **顺序一致**: 编号顺序应与 SAP 分析步骤顺序一致
- **无"幽灵条目"**: 不得出现进度表有但 SAP 没有的图表

### 3.4 进度表与 SAP 的对应关系

```
§3.1 描述性统计  →  表1 基线资料比较    →  tables/baseline.xlsx
§3.2 主要结局    →  表2 单因素分析      →  tables/primary_univariate.xlsx
§3.3 多因素分析  →  表3 Cox回归          →  tables/cox_regression.xlsx
§4.1 敏感性分析  →  表8 敏感性分析       →  tables/sensitivity.xlsx
```

### 3.5 进度表文件管理

- 文件路径: `MSRA/progress_tracker.md`
- 由 analysis-exec 在 Stage 3 启动时自动创建
- Stage 3.5 质量门闸时自动与 SAP 交叉验证
- Stage 4 报告生成时自动纳入完成情况报告

---

## 4. 统计分析方案完成情况报告

### 4.1 报告模板

```markdown
# 统计分析方案完成情况报告

## 基本信息
- 研究名称: {标题} | SAP 版本: v{X.Y} | 确认日期: {日期}
- 报告日期: {日期} | 执行期间: {起始} — {结束} | 分析师: {姓名}

## 版本历史
| 版本 | 日期 | 变更请求 | 变更内容 | 审批人 |
|------|------|---------|---------|--------|
| v1.0 | YYYY-MM-DD | — | 初始版本 | — |

## 图表清单
| 编号 | 标题 | SAP 条目 | 生成日期 | 状态 | 备注 |
|------|------|---------|---------|------|------|
| 表1 | {标题} | §{编号} | YYYY-MM-DD | 已审核 | — |

## 完成统计
- 总图表数: {N} | 已完成: {n1} ({p1}%) | 进行中: {n2} | 未开始: {n3} | 需修订: {n4}

## 偏差记录汇总
| 编号 | 日期 | SAP 条目 | 类型 | 说明 | 审批 |
|------|------|---------|------|------|------|
| DV-001 | YYYY-MM-DD | §3.2 | B 类 | {描述} | 已确认 |

## 随机种子记录
| 步骤 | 种子值 | 用途 | 文件名 |
|------|--------|------|--------|
| {步骤} | {值} | {用途} | {文件名} |

## 方案遵循声明
本报告确认所有已完成的分析均严格遵循 SAP v{X.Y}。
所有偏离均已记录并获得用户书面确认。所有代码均可追溯到 SAP 条目。
**声明人**: {姓名} | **日期**: {YYYY-MM-DD}
```

### 4.2 报告生成时机

- **中期报告**: Stage 3 完成 50% 时
- **完成报告**: Stage 3 全部完成时
- **门闸报告**: Stage 3.5 质量门闸时

### 4.3 报告审核流程

```
生成报告 → 自动核查(SAP↔进度表↔实际文件) → 通过/修正 → 用户确认 → 归档
```

---

## 5. 质量控制标准

### 5.1 四项一致性核查

| # | 核查项 | 核查内容 | 不一致处理 |
|---|--------|---------|-----------|
| QC1 | **SAP <-> 进度表** | 分析内容、条目编号一致 | 暂停，更新进度表对齐 SAP |
| QC2 | **进度表 <-> 实际图表** | 标题、编号、文件匹配 | 修正不匹配项 |
| QC3 | **图表内容 <-> SAP** | 方法、指标、统计量符合 | 退回重做 |
| QC4 | **完成状态 <-> 实际状态** | 标记准确反映实际情况 | 更新状态标记 |

#### 核查执行频率

- QC1: 每次分析开始前（analysis-exec）
- QC2: 每个图表完成后（analysis-exec）
- QC3/QC4: Stage 3.5 质量门闸时（pipeline）

### 5.2 核查清单

```markdown
## 质量核查清单

### SAP 一致性
- [ ] 所有预设分析均已执行或有跳过理由
- [ ] 未执行 SAP 未规定的分析（除标记为探索性）
- [ ] 主要结局/统计方法/样本量/协变量/校正方法/敏感性场景与 SAP 一致

### 进度表一致性
- [ ] 所有图表均在进度表中有记录，标题完全一致
- [ ] 状态标记与实际完成情况一致，无遗漏或多余条目

### 数据完整性
- [ ] 中位数附 [Q1, Q3]；效应量附 95% CI
- [ ] P 值格式统一（无 P=0.000）；分类变量展示频数和百分比
- [ ] 缺失数据已报告

### 可复现性
- [ ] 分析代码设置随机种子；代码可独立运行
- [ ] 输出文件名与进度表编号一致；软件/数据集版本已记录

### 偏差记录
- [ ] 所有偏离 SAP 的操作均有偏差日志记录和用户确认
- [ ] 偏差分类准确，与 SAP 修订历史一致
```

### 5.3 统计报告格式标准

#### 5.3.1 描述性统计格式

| 变量类型 | 报告格式 | 示例 |
|---------|---------|------|
| 正态分布连续变量 | Mean ± SD | 52.3 ± 12.1 |
| 非正态分布连续变量 | Median [Q1, Q3] | 48.0 [35.0, 62.0] |
| 分类变量 | n (%) | 120 (45.2%) |

#### 5.3.2 推断性统计格式

| 统计量 | 报告格式 | 示例 |
|--------|---------|------|
| P 值 | P = 0.023 或 P < 0.001 | 不报告 P = 0.000 |
| 置信区间 | 95% CI [下限, 上限] | 95% CI [1.02, 3.45] |
| 效应量 | OR/HR (95% CI) | OR 2.15 (95% CI 1.34-3.45) |

#### 5.3.3 多重比较校正

- 主要结局不校正（除非 SAP 明确规定）；次要结局按 SAP 校正方法执行
- 亚组分析需报告未校正和校正后两种结果
- 校正方法必须与 SAP 一致（Bonferroni、Holm、FDR 等）

---

## 6. 特殊分析项目要求

### 6.1 倾向性评分匹配（PSM）生存分析

#### 6.1.1 进度表子分析条目

PSM 相关分析必须在进度表中单独列出，不得合并为单一条目：

```
表4a  | 倾向性评分模型（Logistic 回归）        | 未开始
表4b  | 匹配前后协变量平衡性检验（SMD < 0.1）  | 未开始
表4c  | 匹配后样本特征描述                      | 未开始
表5   | 匹配后 Kaplan-Meier 生存分析            | 未开始
表6   | 匹配后 Cox 回归分析                     | 未开始
图1-3 | 倾向性评分分布/SMD 蝴蝶图/生存曲线      | 未开始
```

#### 6.1.2 PSM 分析质量标准

- **SMD < 0.1**（否则调整 caliper 或增加匹配变量）
- **匹配率 >= 70%**（否则记录并考虑替代方法）
- **报告匹配后样本量变化**
- **标准化差异图完整展示**

#### 6.1.3 PSM 代码模板

```python
# SAP §5.1: 倾向性评分模型
SEED = 2024; np.random.seed(SEED)
from sklearn.linear_model import LogisticRegression
ps_model = LogisticRegression(max_iter=1000, random_state=SEED)
ps_model.fit(X_baseline, treatment)
df['propensity_score'] = ps_model.predict_proba(X_baseline)[:, 1]

# SAP §5.2: PSM 匹配（最近邻，caliper = 0.2 * SD）
from sklearn.neighbors import NearestNeighbors
caliper = 0.2 * df['propensity_score'].std()
nn = NearestNeighbors(n_neighbors=1, radius=caliper, random_state=SEED)
nn.fit(df[['propensity_score']])

# SAP §5.3: 平衡性检验
def calculate_smd(data, var, treat_col):
    t, c = data.loc[data[treat_col]==1, var], data.loc[data[treat_col]==0, var]
    return abs((t.mean() - c.mean()) / np.sqrt((t.var() + c.var()) / 2))
```

### 6.2 随机种子管理

所有涉及随机过程的分析步骤必须设置固定随机种子：

```python
import numpy as np, random
SEED = 2024  # 固定的、有意义的种子值
np.random.seed(SEED); random.seed(SEED)
# PSM: NearestNeighbors(random_state=SEED)
# 插补: IterativeImputer(random_state=SEED)
# CV:   KFold(n_splits=5, shuffle=True, random_state=SEED)
```

种子记录格式：`{分析步骤} | {种子值} | {用途} | {文件名}`

原则：固定性（同分析同种子）、可记录性、可追溯性（变更需 CR）、一致性（同项目同种子）

### 6.3 多重插补分析

#### 6.3.1 强制记录项

- **插补次数**: 推荐 m >= 20
- **插补变量列表**: 所有参与插补的变量
- **插补方法**: MICE / PMM / 2l
- **合并规则**: Rubin 合并规则

#### 6.3.2 插补代码模板

```python
# SAP §6.1: 多重插补（m=20, MICE）
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

SEED = 2024; M_IMPUTE = 20
imp_datasets = []
for i in range(M_IMPUTE):
    imp = IterativeImputer(random_state=SEED+i, max_iter=20, initial_strategy='median')
    imp_datasets.append(pd.DataFrame(imp.fit_transform(df[vars]), columns=vars))

# SAP §6.2: Rubin 合并规则
def rubin_combine(imp_results, m):
    Q_bar = np.mean(imp_results, axis=0)
    B = np.var(imp_results, axis=0, ddof=1)
    return Q_bar, np.var(imp_results, axis=0, ddof=1) + (1+1/m)*B
```

#### 6.3.3 插补质量核查

- 比较插补前后变量分布；报告缺失比例和覆盖率
- 检查插补收敛性；与完整案例分析结果对比

#### 6.3.3 插补质量核查

- 比较插补前后变量分布；报告缺失比例和覆盖率
- 检查插补收敛性；与完整案例分析结果对比

### 6.4 亚组分析

- **预定义亚组**: SAP 中明确列出 → 必须全部执行，不得选择性报告
- **探索性亚组**: 分析过程中发现 → 必须明确标注为探索性

报告模板：

```markdown
## 亚组分析结果（SAP §7.x）

| 亚组 | 分层变量 | N | HR (95% CI) | P 值 | 交互 P 值 |
|------|---------|---|------------|------|----------|
| 年龄 <65 vs >=65 | age_group | 120/80 | 1.23 (0.89-1.70) | 0.21 | 0.04 |
| 性别 男 vs 女 | sex | 150/50 | 0.87 (0.62-1.22) | 0.42 | 0.31 |

### 探索性亚组（非 SAP 预设）— 仅供参考，不纳入主要结论
```

质量标准：预定义完整性、交互作用报告、标注清晰、样本量充足（n >= 30）

---

## 7. 集成指南

### 7.1 与 MSRA Pipeline 的集成

| Stage | 集成点 | 具体操作 | 产物 |
|-------|--------|---------|------|
| Stage 2 | SAP 确认后 | 生成初始进度表 | `MSRA/progress_tracker.md` |
| Stage 3.0 | 分析开始前 | 加载 SAP，建立代码-SAP 映射 | 代码注释模板 |
| Stage 3.x | 每个图表完成后 | 更新进度表状态 | 进度表更新 |
| Stage 3.5 | 质量门闸 | 四项一致性核查 | 质控报告 |
| Stage 4 | 报告生成 | 生成完成情况报告 | `MSRA/protocol_adherence_report.md` |

### 7.2 与 SAP 工具的集成

| 工具 | 路径 | 集成方式 |
|------|------|---------|
| SAP 标准 | `shared/sap/sap_standard.md` | SAP 条目编号规范 |
| SAP 一致性检查 | `shared/sap/sap_consistency_check.py` | 自动验证代码-SAP 映射 |

### 7.3 与质量门闸的集成

| 门闸 | 时机 | 检查内容 |
|------|------|---------|
| Stage 2.5 | SAP 定稿后 | 验证 SAP 符合本框架 §1 |
| Stage 3.5 | 分析完成后 | 执行本框架 §5 四项一致性核查 |
| Stage 4.5 | 报告完成后 | 验证报告符合本框架 §4 |

### 7.4 与 Handoff 协议的集成

| Handoff | 时机 | 产物传递 |
|---------|------|---------|
| Stage 4 -> 5.0 | 统计报告完成 | 完成情况报告 + 偏差日志 + 种子记录 |
| Stage 3.5 门闸 | 分析完成后 | 质控报告 + 一致性核查结果 |

### 7.5 产物清单

```
MSRA/
├── progress_tracker.md              # 进度表（§3）
├── protocol_adherence_report.md     # 完成情况报告（§4）
├── sap_v{X.Y}.md                    # SAP 文档（含修订记录）
├── change_requests/                 # 变更请求目录（§2）
├── deviation_log.md                 # 偏差日志（§2.4）
├── seed_record.md                   # 随机种子记录（§6.2）
└── quality_checklist.md             # 质控核查清单（§5.2）
```

### 7.6 自动化检查脚本

```python
#!/usr/bin/env python3
"""协议执行一致性检查: python protocol_adherence_check.py --sap SAP.md --progress progress_tracker.md"""
import re, argparse
from pathlib import Path

def extract_sap(path):
    c = Path(path).read_text(encoding='utf-8')
    return {m.group(1): c[m.start():m.start()+200] for m in re.finditer(r'§(\d+\.\d+)', c)}

def extract_progress(path):
    items = {}
    for line in Path(path).read_text(encoding='utf-8').split('\n'):
        if '|' in line and ('表' in line or '图' in line):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3:
                items[parts[0]] = {'title': parts[1], 'status': parts[2]}
    return items

def check(sap, progress):
    issues = []
    for sid in sap:
        if not any(sid in iid for iid in progress):
            issues.append(f"[QC1] SAP §{sid} 在进度表中无对应条目")
    for iid in progress:
        m = re.search(r'§(\d+\.\d+)', iid)
        if m and m.group(1) not in sap:
            issues.append(f"[QC1] 进度表 {iid} 在 SAP 中无对应条目")
    return issues

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--sap', required=True); p.add_argument('--progress', required=True)
    args = p.parse_args()
    issues = check(extract_sap(args.sap), extract_progress(args.progress))
    print("发现问题:" + "\n  ".join(issues) if issues else "SAP 与进度表一致性检查通过")
```

---

## 附录 A: 变更请求流程图

```
发现变更 → 暂停分析 → 评估类别
  ├── A/B 类: 生成变更请求 → 用户确认 → 更新 SAP + 进度表 + 代码 + 偏差日志
  ├── C 类: 口头确认 → 记录偏差日志
  └── D 类: 代码注释 → 修正后继续
```

## 附录 B: 四项一致性核查决策树

```
QC1: SAP ↔ 进度表 → 不一致则暂停更新
  ↓
QC2: 进度表 ↔ 实际图表 → 不一致则修正文件
  ↓
QC3: 图表内容 ↔ SAP → 不一致则退回重做
  ↓
QC4: 完成状态 ↔ 实际状态 → 不一致则更新标记
```

## 附录 C: 常见偏差场景与处理

| 场景 | 偏差类别 | 处理方式 |
|------|---------|---------|
| 数据不满足正态性假设 | B 类 | 变更请求 → 非参数替代 |
| 样本量低于检验效能 | B 类 | 变更请求 → 报告效能不足 |
| 缺失数据超阈值 | B 类 | 变更请求 → 缺失机制分析 |
| 未预期异常值 | B 类 | 变更请求 → 异常值处理 + 敏感性分析 |
| 亚组样本量过小 | C 类 | 记录偏差 → 合并或标注 |
| 图表格式不规范 | C 类 | 记录偏差 → 格式调整 |
| 代码/SAP 笔误 | D 类 | 代码注释 → 修正 |

---

> **文档维护**: 本框架由 MSRA Pipeline 维护团队负责更新。任何修订必须通过变更管理流程（§2）记录。
>
> **生效日期**: 2026-06-21
>
> **下次评审日期**: 2026-12-21（半年度评审）
