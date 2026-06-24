# Phase 3: 推断分析（代码生成与执行）

> **Hybrid Prompting 策略**（借鉴 Frontiers AI 2025）：
> 统计推理准确性通过组合三层提示策略显著提升：
> 1. **明确指令层**：方法选择规则、假设检验顺序、效应量报告要求
> 2. **推理脚手架层**：分步推理模板、假设-检验-结论结构化流程
> 3. **格式约束层**：输出格式模板、数值精度要求、标记规范
>
> 三层策略必须同时应用于代码生成和结果解读，缺一不可。

**代码结构**（R/Python）：

```r
# 环境设置 → 数据准备(按SAP人群) → 描述性统计(Table1)
# → 主要分析 → 假设检验 → 敏感性分析 → 结果汇总
```

**执行原则**：
- 严格遵循 SAP，不擅自更改方法
- 所有假设必须检验
- 所有计划的分析必须执行
- 任何偏差必须记录

---

## Hybrid Prompting 代码生成模板

> 每段分析代码必须遵循三层结构，确保统计推理的严谨性。

```markdown
### [分析名称] — Hybrid Prompting 模板

#### Layer 1: 明确指令 (Explicit Instructions)
- 方法: [从SAP引用具体方法，如"ANCOVA调整基线HbA1c"]
- 假设: [列出必须检验的假设，如"正态性、方差齐性、线性"]
- 效应量: [预定义效应量类型，如"Cohen's d + 95%CI"]
- 偏差处理: [假设违反时的降级路径，如"→ Welch's t → Mann-Whitney"]

#### Layer 2: 推理脚手架 (Reasoning Scaffold)
代码必须按以下结构组织：
1. 假设检验代码（先于主分析）
2. 假设结果解读（通过/违反 + 证据）
3. 方法选择决策（基于假设结果选择方法）
4. 主分析代码（使用选定方法）
5. 效应量计算（预定义类型）
6. 结果摘要（效应量+CI+p值+临床解读）

#### Layer 3: 格式约束 (Format Constraints)
- P值格式: 遵循 statistical_constraints.md P-R01~R07（P<0.001展示为"P < 0.001"，禁止P=0.000）
- 数值精度: p值3位小数, 效应量2位小数, CI 2位小数
- 变量命名: 遵循 variable_naming_conventions.md 三列命名体系（代码变量名/规范显示名/英文显示名）
- 标记规范: [SKIP:原因] / [DEVIATION:描述] / [EXPLORATORY]
- 输出格式: 表格必须含列名、单位、注释行
```

---

## Hybrid Prompting 应用示例（R - 两组连续变量比较）

```r
# === Layer 1: 明确指令 ===
# 方法: 独立样本t检验（如正态）或 Mann-Whitney U（如非正态）
# 假设: 1) Shapiro-Wilk正态性 2) Levene方差齐性
# 效应量: Cohen's d (正态) 或 r = Z/sqrt(N) (非参数)
# 降级路径: t检验 → Welch's t → Mann-Whitney U

# === Layer 2: 推理脚手架 ===
# Step 1: 假设检验
shapiro_ctrl <- shapiro.test(data$outcome[data$group == "control"])
shapiro_trt <- shapiro.test(data$outcome[data$group == "treatment"])
cat(sprintf("正态性检验: 对照组 P=%.4f, 治疗组 P=%.4f\n",
            shapiro_ctrl$p.value, shapiro_trt$p.value))

# Step 2: 假设结果解读 + 方法决策
normal_ok <- shapiro_ctrl$p.value > 0.05 & shapiro_trt$p.value > 0.05
if (normal_ok) {
  # Step 3: 方差齐性检验
  levene_result <- car::leveneTest(outcome ~ group, data = data)
  var_equal <- levene_result$`Pr(>F)`[1] > 0.05
  method_used <- if(var_equal) "Student's t" else "Welch's t"

  # Step 4: 主分析
  test_result <- t.test(outcome ~ group, data = data, var.equal = var_equal)

  # Step 5: 效应量
  d <- effsize::cohen.d(outcome ~ group, data = data)
  cat(sprintf("方法: %s | 均差=%.2f [%.2f, %.2f] | p=%.4f | d=%.2f\n",
              method_used, diff(test_result$estimate),
              test_result$conf.int[1], test_result$conf.int[2],
              test_result$p.value, d$estimate))
} else {
  # 降级: 非参数方法
  method_used <- "Mann-Whitney U"
  test_result <- wilcox.test(outcome ~ group, data = data, conf.int = TRUE)

  # Step 5: 效应量 (r = Z/sqrt(N))
  z <- qnorm(test_result$p.value / 2)
  r_eff <- abs(z) / sqrt(nrow(data))
  cat(sprintf("方法: %s | 中位数差=%.2f [%.2f, %.2f] | p=%.4f | r=%.2f\n",
              method_used,
              diff(tapply(data$outcome, data$group, median)),
              test_result$conf.int[1], test_result$conf.int[2],
              test_result$p.value, r_eff))
}

# === Layer 3: 格式约束 ===
# 输出必须包含: 方法名 | 效应量[95%CI] | p值 | 假设检验结果
# 如假设违反且降级: 标记 [DEVIATION: 非正态→非参数]
```

---

## 自愈机制详细流程

> **错误诊断参考**: shared/error-diagnostics/error_patterns.md — 常见错误模式与诊断流程
> **自动修复参考**: shared/error-diagnostics/auto_fix_suggestions.py (Python) / .R (R) — 自动修复建议

```
代码执行失败
    │
    ▼
Layer 1: 语法修复 (0-1轮)
├── ImportError → 添加缺失import
├── SyntaxError → 修正语法
├── NameError → 修正变量名
└── 修复后重试 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 2: 数据适配 (1-2轮)
├── ValueError → 类型转换(pd.to_numeric/errors='coerce')
├── KeyError → 列名映射/模糊匹配
├── IndexError → 边界检查/空值处理
└── 修复后重试 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 3: 方法降级 (1-2轮)
├── 不收敛 → 减少变量/增加迭代次数
├── 完全分离 → Firth惩罚回归
├── PH违反 → 分层Cox/时依协变量
├── 多重共线性 → 岭回归/剔除VIF>10变量
└── 修复后重试 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 4: 用户介入 (1轮)
├── 展示错误详情+已尝试方案
├── 请求用户: 修改SAP/提供数据/手动编码
└── 用户响应 → 执行 → 成功？→ 是 → 完成
    │ 否
    ▼
Layer 5: 标记跳过
├── 标记 [SKIP: code_execution_failed]
├── 记录偏差到审计日志
├── 继续执行其他分析项
└── 在报告中标注未完成分析
```

> **自愈原则**: 自愈仅修复代码错误，不改变SAP预定义的分析方法。需修改方法时走Phase 3 SAP修正流程。
> **自愈上限**: 最多5轮，每轮记录修复详情。超过5轮标记[SKIP]。

---

## 错误分类阈值

| 错误类型 | 示例 | 自愈成功率 | 达第5轮后的处理 |
|---------|------|-----------|---------------|
| 语法错误 | 缺少括号、拼写错误 | 90%+ | 标记 [SKIP: syntax] → 展示错误详情，用户选择：[A] 手动修复代码 / [B] 跳过此分析项 / [C] 简化分析方法 |
| 运行时错误 | 缺失包、数据列名不符 | 70-80% | 标记 [SKIP: runtime] → 展示错误详情，用户选择：[A] 安装缺失包/修正数据 / [B] 跳过此分析项 / [C] 使用替代包/方法 |
| 逻辑错误 | 变量类型错误、索引越界 | 50-60% | 标记 [SKIP: logic] → 展示错误详情，用户选择：[A] 检查数据质量问题 / [B] 跳过此分析项 / [C] 调整分析逻辑 |
| 统计错误 | 共线性、分离问题、样本量不足 | 40-50% | 标记 [SKIP: statistical] → 展示错误详情，用户选择：[A] 降级到替代方法 / [B] 跳过此分析项 / [C] 转为探索性分析 |
| 数据错误 | 缺失数据过多、异常值极端 | 30-40% | 标记 [SKIP: data] → 展示错误详情，用户选择：[A] 数据清洗/插补处理 / [B] 跳过此分析项 / [C] 排除问题数据子集 |
| 环境错误 | 内存不足、包版本冲突 | 60-70% | 标记 [SKIP: environment] → 展示错误详情，用户选择：[A] 调整计算资源/更新包 / [B] 跳过此分析项 / [C] 简化模型规模 |

---

## 常见错误处理代码示例

> 完整可执行代码（Firth Logistic / VIF 诊断 / Cox PH 违反处理，含 R 和 Python 双语言）见 [`shared/error-diagnostics/code_fixes_reference.md`](../../shared/error-diagnostics/code_fixes_reference.md)。
> 简要诊断规则见 [`shared/error-diagnostics/error_patterns.md`](../../shared/error-diagnostics/error_patterns.md)（S1-S4 / D1-D3 / E1-E3 / C1-C3）。

| 错误类型 | 诊断信号 | 一线修复 | 仍失败兜底 |
|---------|---------|---------|-----------|
| 完全分离 (S2) | `"X matrix singular"` / `"Perfect separation"` | Firth 惩罚 Logistic (`logistf` / `fit_regularized`) | 合并类别 / 贝叶斯 Logistic |
| 多重共线性 (S1) | VIF > 10 | 删除高 VIF 变量 / 合并变量 | PCA 降维 / 岭回归 |
| PH 假设违反 (S4) | Schoenfeld p < 0.05 | 分层 Cox (`strata()`) | 时依系数 `tt()` / 分段 Cox / 参数生存模型 |

**错误诊断增强**：

**统计错误诊断**：
- **共线性诊断**：计算VIF，VIF > 10提示严重共线性，应删除/合并变量
- **分离问题检测**：Logistic回归中检测perfect separation，应采用精确Logit或Firth校正
- **样本量不足警告**：主要分析样本量 < SAP计划的70%，应转为exploratory
- **缺失数据影响评估**：主要变量缺失率 > 30%，应采用多重插补或敏感性分析

**数据错误诊断**：
- **极端异常值检测**：使用IQR方法检测异常值，提供处理方案
- **缺失模式分析**：评估MCAR/MAR/MNAR，指定处理策略
- **数据分布检查**：检查偏态、峰度，应做数据变换

**环境错误诊断**：
- **内存不足**：应改用数据子采样或流式处理
- **包版本冲突**：应创建虚拟环境或更新包版本
- **计算超时**：应简化模型或增加计算资源

---

## [SKIP] 诚实标记机制

> 借鉴 YH-SAP

- 如果数据不足以执行某项分析，输出 `[SKIP: 原因]` 而非编造结果
- SKIP 标记必须在最终报告中高亮标注 `[REVIEW NEEDED]`
- SAP 中预定义的 SKIP 触发条件：样本量不足、数据缺失率过高、假设检验严重违反且转换失败

> 🔴 [ADAPTIVE] 代码执行完成后：展示 [SKIP] 标记数量和类型。如自愈 3 轮后仍有 ≥2 个 [SKIP]：
>   - **一线处理**: 讨论是否降低分析复杂度或回退修改 SAP
>   - **仍失败兜底**: 用户确认接受 [SKIP] 结果 → 标记为 "分析受限 [LIMITED ANALYSIS]"，在报告中高亮标注 `[REVIEW NEEDED]`

---

## Step 3.1: 观察性研究高级分析方法 🆕

> 当 SAP 中包含 IPTW、双重稳健估计、RCS、E-value 等方法时，在 Phase 3 主分析之后执行此子步骤。
> **参数已在 Stage 2 SAP 中确认**，此处直接使用 SAP 预定义的参数，无需再次确认。
> 参考：shared/statistics-methods/observational-study-methods.md — 方法详解与代码模板

### Step 3.1.1: 参数来源

所有参数来自 SAP（Stage 2 已确认），直接使用：

| 方法 | 参数 | 默认值（SAP 未指定时） |
|------|------|----------------------|
| **IPTW** | 权重截断百分位 | 95th |
| **IPTW** | 倾向性评分模型 | Logistic (logit) |
| **IPTW** | 是否稳定化权重 | 是 |
| **RCS** | 节点数量 | 3 |
| **RCS** | 节点位置 | 百分位数(10/50/90) |
| **双重稳健** | Bootstrap 次数 | 500 |
| **双重稳健** | 结局模型 | Cox |
| **E-value** | 是否需要 | 是(观察性研究) |
| **亚组分析** | 亚组变量 | SAP 定义 |
| **亚组分析** | 模型复杂度 | 3级(crude/age-adjusted/full) |

> **参数使用默认值，无需逐项确认**。用户如需修改特定参数，在 SAP 文档中调整后说"重新执行"即可。

### Step 3.1.2: IPTW（逆概率处理加权）

**关键步骤**：
1. 使用 `WeightIt::weightit()` 计算倾向性评分权重
2. 截断极端权重（默认 95th 百分位）
3. 使用 `cobalt::bal.tab()` 评估协变量平衡性（SMD <0.1 为优秀）
4. 使用 `survey::svydesign()` 创建加权设计对象
5. 使用 `survey::svycoxph()` 进行加权 Cox 回归

**必须报告**：权重分布(min/median/max)、Love plot、所有协变量 SMD

### Step 3.1.3: 双重稳健估计（AIPW）

**关键步骤**：
1. 拟合 PS 模型（Logistic 回归）
2. 拟合结局模型（含/不含处理变量的 Cox 回归）
3. 计算 AIPW 估计量
4. Bootstrap 验证置信区间（默认 500 次）

**必须报告**：PS 模拟合优度、Bootstrap CI、C-index

### Step 3.1.4: 限制性立方样条（RCS）

**关键步骤**：
1. 使用 `rms::datadist()` 设置数据分布
2. 使用 `rms::rcs()` 指定节点（默认 3 个，百分位数 10/50/90）
3. 使用 `rms::cph()` 拟合 RCS 模型
4. `anova()` 检验非线性项显著性
5. `rms::Predict()` 预测并绘图

**必须报告**：节点位置、非线性检验 p 值、RCS 曲线、PH 假设检验

### Step 3.1.5: E-value（未测量混杂敏感性分析）

**关键步骤**：
1. HR 转换为 RR：`RR ≈ (1 - 0.5^√HR) / (1 - 0.5^(1/√HR))`
2. 计算 E-value：`E = RR + √(RR × (RR-1))`（RR>1 时）
3. 对 95% CI 最接近 null 的边界计算 E-value

**必须报告**：点估计 E-value、CI 边界 E-value、解释（需要多强的未测量混杂才能解释掉关联）

### Step 3.1.6: 亚组分析

**关键步骤**：
1. 按 SAP 定义的亚组变量分层
2. 每个亚组拟合 3 级模型（crude / age-adjusted / fully-adjusted）
3. 检验亚组间异质性（交互作用 p 值）
4. 森林图可视化

**必须报告**：各亚组 HR+95%CI、交互作用 p 值、森林图

---

## 内置机制: 统计约束追踪 🆕

> 参考：shared/statistics-methods/statistical_constraints.md — 统计约束规则全文
> 参考：shared/chart-styles/variable_naming_conventions.md — 变量命名规范

在 Phase 3 分析执行过程中，必须同步维护以下三张约束追踪表，供 Phase 4 质检和 Stage 3.5 门闸消费。

### 3.2.1 方法一致性追踪表

> 约束规则 M-R01~R08：加权分析链中不得混用非加权数据；参数/非参数方法不得随意切换。

每项分析执行时必须填写：

| 分析编号 | 分析名称 | 数据集类型 | 方法类型 | 加权状态 | 与主分析一致性 | 备注 |
|---------|---------|-----------|---------|---------|--------------|------|
| A01 | 主分析 | 加权数据集 | 参数 | IPTW加权 | — (基准) | — |
| A02 | Table 1 | 加权数据集 | 描述性 | IPTW加权 | ✅ 一致 | — |
| A03 | 敏感性分析 | 加权数据集 | 参数 | IPTW加权 | ✅ 一致 | — |
| A04 | 非加权补充 | 原始数据集 | 参数 | 非加权 | ⚠️ 已标注 | 补充分析 |

**违反处理**：
- M-R01/M-R02 违反（加权混用且未标注）→ 🛑 质检不通过，强制重跑
- M-R07 违反（方法族切换且未说明）→ ⚠️ 质检警告，需补充理由

### 3.2.2 数据集一致性追踪表

> 约束规则 D-R01~R05：每项分析标注数据集；不同数据集需提醒用户抉择。

| 分析编号 | 分析名称 | 数据集 | 人群定义 | 样本量 | 与主分析一致性 |
|---------|---------|-------|---------|-------|---------------|
| A01 | 主分析 | ITT 人群 | 所有随机化受试者 | N=200 | — (基准) |
| A02 | Table 1 | ITT 人群 | 所有随机化受试者 | N=200 | ✅ 一致 |
| A03 | 安全性分析 | Safety 人群 | 至少接受1次给药 | N=195 | ⚠️ SAP预定义 |
| A04 | 敏感性分析 | 完整病例 | 无缺失值 | N=170 | 🛑 需用户确认 |

**违反处理**：
- D-R02 触发（数据集不一致且不在 SAP 预定义中）→ 🛑 STOP，展示数据集差异清单，由用户抉择：
  - [A] 统一使用同一数据集（推荐）
  - [B] 接受差异，在报告中明确标注
  - [C] 修改 SAP 以纳入此数据集定义

### 3.2.3 变量命名一致性检查

> 约束规则 V-R01~R07：变量名在 SAP/代码/表格/图表/正文中必须一致。

分析代码中使用的变量名必须与 SAP 变量构造规格书完全一致。输出结果中的变量展示名必须使用规范显示名（含单位）。

**检查清单**：
- [ ] 代码变量名与 SAP 定义一致（V-R01）
- [ ] 输出表格使用规范显示名（V-R02）
- [ ] 输出图表标签使用规范显示名（V-R03）
- [ ] 单位标注完整且一致（V-R05）

### 3.2.4 P 值格式化执行

> 约束规则 P-R01~R07：P<0.001 统一展示为 "P < 0.001"。

所有分析代码中 P 值输出必须调用格式化函数：

```python
# Python
from shared.templates.publication_figure_template import format_p_value
p_str = format_p_value(p_value)  # P<0.001 → "P < 0.001"
```

```r
# R
source("shared/templates/publication_figure_template.R")
p_str <- format_p_value(p_value)
```

---

## 标准步骤: 假设检验

> 参考：shared/statistics-methods/methods_catalog.md — 假设检验方法速查
> 参考：shared/statistics-methods/INDEX.md — 各统计方法对应的统计指南章节（LOGIT/COX/PSM等）
> 参考：shared/error-diagnostics/ — 错误诊断知识库（用于假设违反时的修复方案）

根据 SAP 中计划的内容，执行所有诊断检验：

| 分析类型 | 必检假设 | 检验方法 | 违反时的处理 |
|---------|---------|---------|------------|
| t检验/ANOVA | 正态性 | Shapiro-Wilk, Q-Q图 | 非参数替代 |
| t检验/ANOVA | 方差齐性 | Levene检验 | Welch校正 |
| **ANCOVA** | **回归斜率齐性** | **Treatment × Covariate 交互** | **分层分析或放弃协变量调整** |
| 线性回归 | 线性关系 | 残差图 | 变换/多项式 |
| 线性回归 | 残差正态 | Q-Q图 | 稳健标准误 |
| Logistic回归 | 线性(连续预测) | Box-Tidwell | 分类/样条 |
| Cox回归 | 比例风险 | Schoenfeld残差 | 分层/时依系数 |
| 所有回归 | 多重共线性 | VIF | 删除/合并变量 |
| 所有回归 | 影响点 | Cook距离 | 敏感性分析 |

---

## 自动化假设检验流程

1. **预检验检查**
   - 验证样本量是否足够进行假设检验
   - 检查变量类型是否适合检验方法
   - 确认数据完整性

2. **假设检验执行**
   - 按SAP计划执行所有假设检验
   - 记录检验统计量、p值、结论
   - 生成假设检验报告

3. **假设违反处理**
   - 自动检测假设违反情况
   - 查询错误诊断知识库获取修复方案
   - 生成降级方案（如参数→非参数）

4. **统计原则违反用户抉择**（S-R01~R08）🆕
   - 参考：shared/statistics-methods/statistical_constraints.md 第四节
   - 检测到以下违反时必须 🛑 STOP，展示用户抉择模板：
     - S-R01: 正态性违反但 SAP 预设参数方法 → 提供参数→非参数降级方案
     - S-R03: 比例风险假设违反 → 提供分层 Cox / 时依系数方案
     - S-R04: 多重共线性严重（VIF>10）→ 提供变量删除/合并方案
     - S-R06: 样本量不足（EPV<10）→ 提供简化模型/转探索性方案
     - S-R07: 回归斜率齐性违反（ANCOVA）→ 提供分层分析方案
     - S-R08: 缺失率过高（>30%）→ 提供多重插补/敏感性分析方案
   - 用户抉择选项：[A] 降级方法（推荐）/ [B] 数据变换 / [C] 维持原方法标注局限性 / [D] 修改SAP
   - 处理结果记录在统计原则违反日志中

5. **SAP一致性检查**
   - 比较SAP预设方法与数据特征
   - 如不匹配，自动推荐替代方法
   - 记录偏差并征得用户同意

---

## 假设检验报告模板

```
假设检验报告
├── 正态性检验
│   ├── Shapiro-Wilk W = 0.98, p = 0.45 → 满足正态性 ✅
│   └── 推荐: 使用参数检验 (t检验/ANOVA)
├── 方差齐性检验
│   ├── Levene F = 2.34, p = 0.13 → 满足方差齐性 ✅
│   └── 推荐: 使用标准t检验
├── 多重共线性检查
│   ├── VIF: age=1.2, gender=1.1, bmi=2.3 → 无严重共线性 ✅
│   └── 推荐: 可继续回归分析
└── 总体结论: 数据满足参数检验假设，推荐使用SAP预设方法
```

> [SLIM] 假设检验执行完成后：展示假设违反清单（如正态失败/方差齐性失败/PH 违反），确认后进入质量检查。
> 
> **自动化升级规则**：
> - 如发现严重假设违反（如正态性p<0.01且样本量<30），自动触发ADAPTIVE Checkpoint
> - 如假设检验结果与SAP预设方法不匹配，自动推荐替代方法并记录偏差

---

## 假设检验检查点

> 🔴 [MANDATORY-EXEC-03] 假设检验完成后，必须展示以下内容给用户确认：
> 1. 假设检验报告（正态性、方差齐性、多重共线性等）
> 2. 假设违反清单及处理方案
> 3. SAP一致性检查结果
>
> 用户确认后才能进入质量检查。

**Phase 3 假设检验检查点标准**:

> 🔴 [MANDATORY-EXEC-03] 以下情况必须暂停等待用户决策：
> 1. S-R01: 比例风险假设违反（Schoenfeld P<0.05）→ 选择: 分层Cox / 时依协变量 / RMST
> 2. S-R02: 正态性违反（Shapiro-Wilk P<0.01）且转换无效 → 选择: 非参数方法 / Bootstrap / 继续参数方法(记录风险)
> 3. S-R03: 方差齐性违反（Levene P<0.05）→ 选择: Welch校正 / 变换 / 非参数
> 4. S-R04: 完全分离（Logistic回归）→ 选择: Firth惩罚回归 / 精确Logistic / 合并类别
> 5. S-R05: 多重共线性（VIF>10）→ 选择: 剔除变量 / 岭回归 / PCA降维
> 6. S-R06: 权重极端值（IPTW weight>20）→ 选择: 截断 / 重新指定PS模型 / 放弃IPTW
> 7. S-R07: 信息分离（事件数<10/变量）→ 选择: 减少变量 / 惩罚回归 / 标记[SKIP]
> 8. S-R08: 竞争风险存在 → 选择: 起因特异性Cox / Fine-Gray子分布 / 复合终点
>
> 用户决策记录格式:
> | 违反规则 | 检测值 | 用户选择 | 理由 | 时间戳 |

---

## 异常处理分支: SAP 修正请求（SAP Amendment Request） 🆕

> 目的：当 Phase 3 假设检验发现 SAP 预设方法与数据特征不一致时，提供透明的修正流程。

**触发条件**：

| 条件 | 检测方式 | 示例 |
|------|---------|------|
| 正态性严重违反 | Shapiro-Wilk p < 0.05 但 SAP 预设参数方法 | 需切换非参数方法 |
| 多重共线性 | VIF > 10 但 SAP 预设包含全部协变量 | 需移除高共线性变量 |
| 样本量严重不足 | 实际样本量 < SAP 预设的 70% | 需调整分析策略 |

**修正分类**：

| 类别 | 说明 | 审批级别 | 记录方式 |
|------|------|---------|---------|
| A-Method Swap | 方法替换（参数→非参数） | MANDATORY checkpoint | SAP amendment log + audit log |
| B-Covariate Adjust | 协变量增删 | SLIM checkpoint | SAP amendment log |
| C-Cutpoint Revise | 切点修改 | MANDATORY checkpoint（仅非预设切点） | SAP amendment log + 标注"事后分析" |
| D-Sample Restriction | 人群重新定义 | MANDATORY checkpoint | SAP amendment log + 标注"事后分析" |

**修正记录格式**：
```json
{
  "amendment_id": "AMD-001",
  "original_spec": "ANCOVA with 5 covariates",
  "amended_spec": "Kruskal-Wallis (non-parametric)",
  "trigger": "Shapiro-Wilk p < 0.01, Box-Cox failed",
  "justification": "正态性严重违反且转换无效",
  "user_approval": true,
  "timestamp": "2026-06-18T10:30:00Z",
  "post_hoc_flag": true
}
```

**防护措施**：
- 整个 Stage 3 最多 3 次 Amendment
- D 类修正（人群重定义）需要 2 次 MANDATORY checkpoint
- 所有修正在审计日志中标记为 `post_hoc_amendment`

---

## 条件子步骤: 多中心汇总分析 🆕（仅 multi-dataset 模式）

> 触发条件：passport 中 multi_dataset_mode artifact 存在且 SAP 含"中心效应处理策略"章节

- **目的**：执行多中心汇总分析，评估中心间效应一致性
- **输入**：各中心分析结果 + SAP 中心效应策略
- **执行内容**：
  1. 中心间森林图（基线特征）：
     - 各中心主要基线特征森林图
     - 使用 shared/templates/forest_plot_template.py
  2. 汇总分析（按 SAP 策略执行）：
     - 固定效应模型：中心作为协变量的回归模型
     - 随机效应模型：混合效应模型（中心随机截距）
     - 两步法 meta-analysis：逐中心效应量 + meta 汇总
  3. 异质性检验：
     - I²、τ²、Cochran's Q
     - 使用 shared/templates/multicenter_template.py 的 heterogeneity_report()
  4. leave-one-out 敏感性分析：
     - 逐一排除各中心，重新汇总
     - 使用 shared/templates/multicenter_template.py 的 leave_one_out()
- **输出**：multicenter_analysis_report.md + forest_plots/*.png
- **Checkpoint**: [SLIM] 展示汇总结果后继续
- **Anti-pattern**: 不得忽略高异质性（I²>75%）直接报告汇总效应量
