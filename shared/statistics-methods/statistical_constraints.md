# 统计分析约束规则

> MSRA 项目专用。定义统计分析全流程中必须遵守的约束规则，覆盖 P 值格式化、方法一致性、
> 数据集一致性、统计原则违反检测四大维度。各 SKILL 的约束执行节引用本文件。
>
> 参考：shared/anti-patterns/medical_stats_anti_patterns.md（D1/D2/M1-M5）
> 参考：shared/reporting-guidelines/statcheck_rules.md — NHST 结果一致性校验

---

## 设计初衷

医学统计分析中，以下四类问题最为常见且危害最大：

1. **P 值展示不规范**：报告 P=0.000 而非 P<0.001，或仅写 P<0.05 不给精确值
2. **方法一致性破坏**：加权分析中途混用非加权数据，参数/非参数方法在同一分析链中随意切换
3. **数据集混淆**：不同分析使用不同分析人群或数据子集而不标注，导致结果不可比较
4. **统计原则违反**：忽略假设检验结果强行使用预设方法，或事后更改方法不记录

本文件为每个维度定义**硬约束规则**和**用户抉择触发条件**。

---

## 一、P 值格式化约束

### 1.1 硬约束规则

| 规则编号 | 规则内容 | 违反后果 |
|---------|---------|---------|
| P-R01 | P 值实际值 < 0.001 时，统一展示为 `P < 0.001`，禁止写 `P = 0.000` 或 `P = 0.0001` | 质检不通过，强制修正 |
| P-R02 | P 值在 0.001 ≤ P < 0.05 区间时，报告精确到小数点后 3 位（如 `P = 0.037`） | 质检警告 |
| P-R03 | P 值在 0.05 ≤ P < 1.0 区间时，报告精确到小数点后 3 位（如 `P = 0.124`） | 质检警告 |
| P-R04 | 禁止仅用 `P < 0.05` 或 `P > 0.05` 二元化表述，必须给出精确 P 值 | 质检不通过，强制修正 |
| P-R05 | 禁止用星号（`*`、`**`、`***`）替代精确 P 值；星号仅可作为辅助标记，精确值必须同时给出 | 质检不通过 |
| P-R06 | 同一报告中 P 值精度必须统一：要么全部 3 位小数，要么全部 4 位小数，不可混用 | 质检警告 |
| P-R07 | 表格、图表注释、正文解读中的 P 值必须完全一致（statcheck 交叉验证） | 质检不通过 |

### 1.2 P 值格式化函数

```python
def format_p_value(p, precision=3):
    """
    格式化 P 值，遵循 MSRA 约束规则 P-R01 ~ P-R07。

    Parameters
    ----------
    p : float
        原始 P 值
    precision : int
        小数位数（默认 3 位）

    Returns
    -------
    str
        格式化后的 P 值字符串
    """
    if p < 0.001:
        return "P < 0.001"
    elif p < 0.05:
        return f"P = {p:.{precision}f}"
    elif p < 1.0:
        return f"P = {p:.{precision}f}"
    else:
        return "P = 1.000"


def format_p_value_table(p_values, precision=3):
    """
    批量格式化 P 值，确保同一表格内精度统一（P-R06）。
    """
    return [format_p_value(p, precision) for p in p_values]
```

### 1.3 R 版 P 值格式化

```r
format_p_value <- function(p, precision = 3) {
  if (p < 0.001) {
    return("P < 0.001")
  } else {
    return(sprintf(paste0("P = %.", precision, "f"), p))
  }
}

# 批量应用
format_p_vector <- function(p_values, precision = 3) {
  sapply(p_values, format_p_value, precision = precision)
}
```

### 1.4 P 值展示规范速查

| P 值范围 | 正确展示 | 错误展示 | 规则 |
|---------|---------|---------|------|
| p = 0.0003 | `P < 0.001` | ~~P = 0.000~~, ~~P = 0.0003~~ | P-R01 |
| p = 0.008 | `P = 0.008` | ~~P < 0.01~~ | P-R02 |
| p = 0.037 | `P = 0.037` | ~~P < 0.05~~, ~~*~~ | P-R04, P-R05 |
| p = 0.052 | `P = 0.052` | ~~P > 0.05~~, ~~NS~~ | P-R04 |
| p = 0.124 | `P = 0.124` | ~~P > 0.05~~, ~~NS~~ | P-R04 |

---

## 二、方法一致性约束

### 2.1 加权数据一致性规则

> **核心原则**：一旦在分析链中采用了加权方法（IPTW、OW、PSM 加权等），
> 后续所有相关分析（描述性统计、推断分析、敏感性分析、亚组分析）必须使用同一加权数据集，
> 不得在加权与非加权之间随意切换。

| 规则编号 | 规则内容 | 违反后果 |
|---------|---------|---------|
| M-R01 | 加权描述性统计必须使用加权后的数据集，不得混用非加权 Table 1 | 质检不通过，强制重跑 |
| M-R02 | 加权推断分析（如 svycoxph）必须使用加权设计对象，不得切换到非加权模型 | 质检不通过 |
| M-R03 | 敏感性分析若基于加权框架，必须保持加权一致；若切换为非加权，必须明确标注为"非加权敏感性分析"并说明理由 | 质检警告 |
| M-R04 | 亚组分析必须与主分析使用相同的加权/非加权策略 | 质检不通过 |
| M-R05 | 加权前后协变量平衡评估（SMD）必须使用加权后数据，不得用非加权 SMD 替代 | 质检不通过 |

### 2.2 加权一致性检查清单

分析执行前和执行后必须逐项确认：

```
加权一致性检查清单
├── [ ] 主分析使用加权设计对象（如 svydesign / svycoxph）
├── [ ] Table 1 使用加权描述性统计（如 svytable / weighted means）
├── [ ] 敏感性分析与主分析加权策略一致
├── [ ] 亚组分析与主分析加权策略一致
├── [ ] 协变量平衡评估（SMD/Love plot）使用加权后数据
├── [ ] 效应量报告基于加权模型输出
├── [ ] 如有非加权补充分析，已明确标注"非加权补充分析"
└── [ ] 所有加权/非加权切换点已记录在偏差日志中
```

### 2.3 参数/非参数方法一致性规则

| 规则编号 | 规则内容 | 违反后果 |
|---------|---------|---------|
| M-R06 | 同一分析链中，主要分析和敏感性分析的方法类型（参数/非参数）应保持一致；如需切换，必须说明理由 | 质检警告 |
| M-R07 | 假设检验结果决定方法选择后，后续相关分析必须使用同一方法族（如主分析用 Mann-Whitney U，敏感性分析不得突然切回 t 检验） | 质检不通过 |
| M-R08 | 多个相关终点使用同一方法族（如所有连续变量终点统一用 ANCOVA 或统一用 Kruskal-Wallis），不得逐变量随意选择 | 质检警告 |

### 2.4 方法一致性追踪表

每项分析执行时必须填写方法一致性追踪表，供质检阶段核验：

```markdown
| 分析编号 | 分析名称 | 数据集类型 | 方法类型 | 加权状态 | 与主分析一致性 |
|---------|---------|-----------|---------|---------|--------------|
| A01 | 主分析（Cox回归） | 加权数据集 | 参数 | IPTW加权 | — (基准) |
| A02 | Table 1 基线特征 | 加权数据集 | 描述性 | IPTW加权 | ✅ 一致 |
| A03 | 敏感性分析1 | 加权数据集 | 参数 | IPTW加权 | ✅ 一致 |
| A04 | 非加权补充分析 | 原始数据集 | 参数 | 非加权 | ⚠️ 已标注 |
| A05 | 亚组分析 | 加权数据集 | 参数 | IPTW加权 | ✅ 一致 |
```

---

## 三、数据集一致性约束

### 3.1 数据集一致性规则

> **核心原则**：同一研究中的所有分析必须明确标注所使用的数据集（分析人群），
> 不同分析使用不同数据集时必须提醒用户并说明理由。

| 规则编号 | 规则内容 | 违反后果 |
|---------|---------|---------|
| D-R01 | 每项分析必须标注使用的数据集（ITT / PP / Safety / 加权数据集 / 完整病例数据集等） | 质检不通过 |
| D-R02 | 主分析和敏感性分析使用不同数据集时，必须提醒用户并征得同意 | 🛑 STOP 用户抉择 |
| D-R03 | 亚组分析使用的数据集范围必须与主分析一致或为主分析的子集 | 质检不通过 |
| D-R04 | 不同终点的分析使用不同数据集时（如安全性用 Safety 人群，有效性用 ITT 人群），必须在方法学中明确说明 | 质检警告 |
| D-R05 | 多中心研究中，各中心分析必须使用统一的数据集定义，不得逐中心自定义 | 质检不通过 |

### 3.2 数据集一致性检查流程

```
分析执行 → 记录每项分析的数据集 → 汇总数据集使用情况
  │
  ├── 所有分析使用同一数据集 → ✅ 通过
  │
  └── 不同分析使用不同数据集
       │
       ├── 数据集差异在 SAP 中已预定义（如 ITT + Safety） → ✅ 通过（标注差异）
       │
       └── 数据集差异不在 SAP 预定义中
            │
            ├── 🛑 STOP: 提醒用户数据集不一致
            │   展示:
            │   - 各分析使用的数据集清单
            │   - 数据集差异的具体情况
            │   - 差异对结果可比性的影响评估
            │   决策:
            │   - [A] 统一使用同一数据集（推荐）
            │   - [B] 接受差异，在报告中明确标注
            │   - [C] 修改 SAP 以纳入此数据集定义
            │
            └── 用户确认后继续，记录在偏差日志中
```

### 3.3 数据集一致性追踪表

```markdown
| 分析编号 | 分析名称 | 数据集 | 人群定义 | 样本量 | 与主分析数据集一致性 |
|---------|---------|-------|---------|-------|-------------------|
| A01 | 主分析 | ITT 人群 | 所有随机化受试者 | N=200 | — (基准) |
| A02 | Table 1 | ITT 人群 | 所有随机化受试者 | N=200 | ✅ 一致 |
| A03 | 安全性分析 | Safety 人群 | 至少接受1次给药 | N=195 | ⚠️ SAP预定义 |
| A04 | PP 分析 | PP 人群 | 完成方案要求 | N=180 | ⚠️ SAP预定义 |
| A05 | 敏感性分析 | 完整病例 | 无缺失值 | N=170 | 🛑 需用户确认 |
```

---

## 四、统计原则违反检测

### 4.1 统计原则违反检测规则

> **核心原则**：当检测到统计原则违反时，系统必须暂停并提醒用户，
> 由用户决定处理方案。不得静默绕过或自行调整。

| 规则编号 | 触发条件 | 检测方式 | 处理方式 |
|---------|---------|---------|---------|
| S-R01 | 正态性违反但 SAP 预设参数方法 | Shapiro-Wilk P < 0.05 | 🛑 STOP: 提醒用户，提供参数→非参数降级方案 |
| S-R02 | 方差齐性违反 | Levene P < 0.05 | ⚠️ 自动切换 Welch 校正（SAP 预定义），记录偏差 |
| S-R03 | 比例风险假设违反 | Schoenfeld P < 0.05 | 🛑 STOP: 提醒用户，提供分层 Cox / 时依系数方案 |
| S-R04 | 多重共线性严重 | VIF > 10 | 🛑 STOP: 提醒用户，提供变量删除/合并方案 |
| S-R05 | 完全分离问题 | Logistic 回归警告 | ⚠️ 自动切换 Firth 惩罚（SAP 预定义），记录偏差 |
| S-R06 | 样本量不足（事件数 < 10/变量） | EPV 检查 | 🛑 STOP: 提醒用户，提供简化模型/转探索性方案 |
| S-R07 | 回归斜率齐性违反（ANCOVA） | 交互项 P < 0.05 | 🛑 STOP: 提醒用户，提供分层分析/放弃协变量调整方案 |
| S-R08 | 缺失率过高（> 30%） | 缺失率统计 | 🛑 STOP: 提醒用户，提供多重插补/敏感性分析方案 |
| S-R09 | RCS 非线性不显著 | anova P-nonlinear > 0.05 | ⚠️ 提醒用户：非线性不显著时 RCS 曲线可能过拟合，建议报告线性趋势 + 备注 |
| S-R10 | RCS 节点数过多 | AIC 选节点 ≥ 6 | ⚠️ 提醒用户：节点数过多可能导致过拟合，建议限制 ≤ 4 或使用惩罚样条 |
| S-R11 | RCS 样本量不足 | n < 10 × knot | ⚠️ 提醒用户：每个节点至少需要 10 个事件，建议减少节点数或增加样本 |

### 4.2 用户抉择触发模板

当检测到统计原则违反时，按以下模板向用户展示：

```markdown
## ⚠️ 统计原则违反提醒

**检测到问题**：[问题描述，如"正态性检验未通过"]

**详细证据**：
- 检验方法：Shapiro-Wilk
- 检验结果：W = 0.92, P = 0.003
- 影响变量：[变量名]
- 影响分析：[分析名称]

**对结果的影响**：
[说明违反假设对结果可靠性的影响]

**可选处理方案**：
  [A] 降级为非参数方法（推荐）
      - 替换为：Mann-Whitney U 检验
      - 效应量：r = Z/√N
      - 优点：不依赖正态性假设
      - 缺点：检验效能略低

  [B] 数据变换后重新检验
      - 变换方法：对数变换 / Box-Cox
      - 变换后需重新检验正态性
      - 如仍不满足，建议回到方案 A

  [C] 维持参数方法（需标注局限性）
      - 在报告中标注"正态性假设未满足"
      - 在局限性中讨论对结论的影响
      - ⚠️ 不推荐，可能影响审稿

  [D] 修改 SAP（事后分析）
      - 记录为事后分析
      - 需在报告中明确标注

请选择处理方案（A/B/C/D）：
```

### 4.3 统计原则违反日志

每次检测到违反并处理后，必须记录：

```json
{
  "violation_id": "V-001",
  "timestamp": "2026-06-18T10:30:00Z",
  "analysis_id": "A01",
  "violation_type": "normality",
  "test_method": "Shapiro-Wilk",
  "test_statistic": 0.92,
  "p_value": 0.003,
  "affected_variable": "blood_pressure",
  "affected_analysis": "两组比较",
  "severity": "moderate",
  "user_decision": "A",
  "action_taken": "降级为 Mann-Whitney U 检验",
  "post_hoc_flag": false,
  "recorded_in_deviation_log": true
}
```

---

## 五、约束执行集成点

### 5.1 在 analysis-exec 中的集成

| Phase | 集成的约束 | 执行方式 |
|-------|----------|---------|
| Phase 6 代码生成 | P-R01~R07 | 代码中调用 `format_p_value()` 格式化所有 P 值输出 |
| Phase 6 代码生成 | M-R01~R08 | 代码中统一使用加权设计对象，方法一致性追踪表随代码输出 |
| Phase 6 代码生成 | D-R01~R05 | 每段代码注释标注数据集来源，数据集一致性追踪表随代码输出 |
| Phase 7 假设检验 | S-R01~R08 | 假设检验结果触发用户抉择模板 |
| Phase 8 质量检查 | 全部约束 | 质检清单中增加约束检查项 |

### 5.2 在 report 中的集成

| Phase | 集成的约束 | 执行方式 |
|-------|----------|---------|
| Phase 1 结果解读 | P-R01~R07 | 解读文本中 P 值格式化 |
| Phase 3 表格生成 | P-R01~R07 | 表格中 P 值格式化 |
| Phase 4 图表生成 | P-R01~R07 | 图表注释中 P 值格式化 |
| Phase 5 方法学描述 | M-R01~R08, D-R01~R05 | 方法学段落中说明加权策略和数据集定义 |
| Phase 6 统计质量检查 | 全部约束 | statcheck + 约束一致性检查 |

### 5.3 在 pipeline 质量门闸中的集成

| 门闸 | 检查内容 | 阻断条件 |
|------|---------|---------|
| Stage 3.5 门闸 | P 值格式化合规 | P-R01/P-R04/P-R05 违反 → 阻断 |
| Stage 3.5 门闸 | 方法一致性 | M-R01/M-R02/M-R04 违反 → 阻断 |
| Stage 3.5 门闸 | 数据集一致性 | D-R02 触发且未确认 → 阻断 |
| Stage 3.5 门闸 | 统计原则违反处理 | S-R01/S-R03/S-R04/S-R06/S-R07 触发且未确认 → 阻断 |

---

## 六、约束检查自动化脚本接口

```python
def check_p_value_formatting(p_value_strings):
    """
    检查 P 值字符串是否符合格式化约束。

    Returns
    -------
    list[dict]
        每个不合规项的详细信息
    """
    violations = []
    for i, s in enumerate(p_value_strings):
        # P-R01: 禁止 P = 0.000
        if "P = 0.000" in s or "p = 0.000" in s:
            violations.append({
                "rule": "P-R01",
                "location": i,
                "value": s,
                "issue": "P值<0.001应展示为 P < 0.001，禁止 P = 0.000",
                "fix": "P < 0.001"
            })
        # P-R04: 禁止仅用二元化表述
        if s.strip() in ["P < 0.05", "P > 0.05", "p < 0.05", "p > 0.05", "NS", "ns"]:
            violations.append({
                "rule": "P-R04",
                "location": i,
                "value": s,
                "issue": "禁止二元化表述，必须给出精确P值",
                "fix": "报告精确P值（如 P = 0.037）"
            })
    return violations


def check_method_consistency(analysis_log):
    """
    检查方法一致性。

    Parameters
    ----------
    analysis_log : list[dict]
        方法一致性追踪表数据

    Returns
    -------
    list[dict]
        不一致项列表
    """
    violations = []
    if not analysis_log:
        return violations

    main_analysis = analysis_log[0]
    main_weighted = main_analysis.get("weighted", False)
    main_method_type = main_analysis.get("method_type", "parametric")

    for entry in analysis_log[1:]:
        # M-R01/M-R02: 加权一致性
        if main_weighted and not entry.get("weighted", False):
            if not entry.get("explicitly_noted", False):
                violations.append({
                    "rule": "M-R01/M-R02",
                    "analysis": entry.get("name"),
                    "issue": "主分析使用加权数据，但此分析使用非加权数据且未标注"
                })
        # M-R07: 方法族一致性
        if entry.get("method_type") != main_method_type:
            if not entry.get("justification"):
                violations.append({
                    "rule": "M-R07",
                    "analysis": entry.get("name"),
                    "issue": f"主分析为{main_method_type}方法，此分析为{entry.get('method_type')}方法，未说明理由"
                })
    return violations


def check_dataset_consistency(analysis_log, sap_defined_datasets):
    """
    检查数据集一致性。

    Parameters
    ----------
    analysis_log : list[dict]
        数据集一致性追踪表数据
    sap_defined_datasets : list[str]
        SAP 中预定义的数据集列表

    Returns
    -------
    list[dict]
        不一致项列表（需用户抉择的项）
    """
    violations = []
    if not analysis_log:
        return violations

    main_dataset = analysis_log[0].get("dataset")
    for entry in analysis_log[1:]:
        dataset = entry.get("dataset")
        if dataset != main_dataset:
            if dataset not in sap_defined_datasets:
                violations.append({
                    "rule": "D-R02",
                    "analysis": entry.get("name"),
                    "main_dataset": main_dataset,
                    "this_dataset": dataset,
                    "issue": "数据集与主分析不一致且不在SAP预定义中，需用户确认"
                })
    return violations
```

---

## 各 SKILL IRON RULE 补充

```yaml
analysis-exec:
  - "P值<0.001统一展示为 P < 0.001，禁止 P = 0.000（P-R01）"
  - "加权分析链中不得混用非加权数据，切换必须标注（M-R01~R05）"
  - "不同分析使用不同数据集时必须提醒用户抉择（D-R02）"
  - "统计原则违反时必须暂停并让用户抉择处理方案（S-R01~R11）"
  - "RCS分析必须报告：节点数、非线性P值、参考值、AIC选节点过程（S-R09~R11）"
  - "RCS非线性P>0.05时必须提醒用户考虑线性替代方案"

report:
  - "报告中所有P值格式必须统一且符合约束（P-R01~R07）"
  - "方法学描述必须说明加权策略和数据集定义（M-R01~R08, D-R01~R05）"
  - "图表注释中的P值与表格、正文必须完全一致（P-R07）"
```
