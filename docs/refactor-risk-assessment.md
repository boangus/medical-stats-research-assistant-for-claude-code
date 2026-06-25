# MSRA 重构风险评估文档

> 审查人: Cody (代码审查师) | 日期: 2026-06-25 | 基于对 5 个 SKILL.md (5628 行) + manifest.json + 14 个 skills/ + 13 个 commands/ + shared/ + agents/ + tests/ 的完整审查

---

## 1. 关键内容清单（绝对不能丢失的内容）

以下内容如果丢失或损坏，将直接导致 MSRA 的核心质量保障机制失效。按 SKILL.md 分列。

### 1.1 analysis-exec/SKILL.md (1344 行)

| # | 内容 | 行号范围 | 为什么不能丢 | 风险等级 |
|---|------|---------|-------------|---------|
| 1 | IRON RULES (方案遵循/变更管理/进度跟踪/四项一致性/随机种子/加权一致性/变量名确认/图表规范) | L22-46 | 定义分析执行的铁律，违反任何一条将导致分析结果不可靠或不可复现 | 🔴 |
| 2 | Phase 文件索引表 (7 个 phases 文件映射) | L187-197 | 主文件引用 phases/ 的唯一索引，损坏将导致 Phase 执行无入口 | 🔴 |
| 3 | 检查点汇总表 (7 个 Checkpoint, MANDATORY/ADAPTIVE/SLIM) | L208-218 | 定义何时暂停、何时自动推进，丢失将导致流程失控 | 🔴 |
| 4 | 反例与黑名单 (执行纪律/统计方法/代码/流程/ML 禁忌) | L253-345 | 25 条禁忌规则，防止常见统计错误。**注意 L1288-1344 是此内容的完全重复** | 🟡 |
| 5 | Hybrid Prompting 三层模板 (L1指令/L2推理/L3格式) | L521-615 | 统计推理准确性核心机制，包含完整 R 代码示例 | 🔴 |
| 6 | 自愈机制 5 层流程 (语法→数据→方法→用户→跳过) | L616-662 | 代码执行失败时的自动修复流程，丢失将导致分析中断无恢复机制 | 🔴 |
| 7 | 错误分类阈值表 (6 类错误的自愈成功率与处理) | L606-614 | 决定自愈策略的错误分类依据 | 🔴 |
| 8 | 统计约束追踪 (M-R/D-R/V-R/P-R 四张追踪表) | L794-1029 | 贯穿全流程的统计合规追踪，Phase 4 和 Stage 3.5 门闸依赖此数据 | 🔴 |
| 9 | 假设检验标准步骤 + S-R01~R08 违反处理 | L865-963 | 8 种统计原则违反的用户抉择模板，丢失将导致假设违反时无处理流程 | 🔴 |
| 10 | SAP 修正请求流程 (A/B/C/D 四类修正) | L964-1027 | 透明的方法变更管理流程，含最多 3 次修正限制 | 🔴 |
| 11 | Phase 4 质量检查清单 (8 维度) | L1030-1129 | 分析完成后的质量门闸，含统计约束合规 + 图表发表级质量 + 四项一致性核查 | 🔴 |
| 12 | Phase 6 审计日志结构 (JSON 格式 + 不可变性保障 + 合规映射) | L1158-1267 | FDA 21 CFR Part 11 / GCP / ICH E6 合规要求，丢失将导致不可审计 | 🔴 |

### 1.2 analysis-plan/SKILL.md (1191 行)

| # | 内容 | 行号范围 | 为什么不能丢 | 风险等级 |
|---|------|---------|-------------|---------|
| 1 | IRON RULES (研究类型决定方法论/预定义/EDA 不改 SAP) | L22-26 | 防止 RCT 方法误用于观察性研究（反之亦然） | 🔴 |
| 2 | Checkpoint Summary Table (CP-1~CP-8, 含 PASS/BLOCK 量化标准) | L155-167 | 8 个检查点的精确通过/阻断标准，硬阻断项 CP-4/CP-6/CP-7 | 🔴 |
| 3 | 审查收敛检查 (3 次退回→BLOCK) | L169-176 | 防止审查无限循环 | 🔴 |
| 4 | Phase 1.5 交互式数据要素确认 (Step 1.5.0-1.5.6) | L294-519 | 因果九项原则评估 + DAG 构建 + CIE 验证 + 三层分类汇总，丢失将导致协变量选择无依据 | 🔴 |
| 5 | Phase 2 方法选择决策树 (15-goal, 112-method) | L521-830 | 完整统计方法选择决策树，含假设不满足转换流水线 + 观察性高级方法 + 效应量要求 | 🔴 |
| 6 | Targeted-Context 机制 | L846-865 | 每个分析项最小必要上下文，防止 LLM 上下文过载 | 🟡 |
| 7 | SAP [SKIP] 预定义触发条件 | L866-876 | 5 种预定义 SKIP 条件，防止 LLM "硬做"不可行分析 | 🔴 |
| 8 | Phase 4.5 SAP 用户强制确认 (MANDATORY-PLAN-02) | L1010-1055 | 阻断式确认点，防止未经确认的 SAP 进入执行 | 🔴 |
| 9 | Phase 5 变量构造定义检查 (MANDATORY-PLAN-01) | L1057-1102 | 4 项检查确保变量构造可复现 | 🔴 |
| 10 | 反例与黑名单 (26 条禁忌) | L1125-1191 | 覆盖方法选择/EDA/Estimands/SAP/流程/变量构造/Targeted-Context | 🟡 |

### 1.3 report/SKILL.md (1247 行)

| # | 内容 | 行号范围 | 为什么不能丢 | 风险等级 |
|---|------|---------|-------------|---------|
| 1 | IRON RULES (P值格式/SKIP标注/临床意义/图表标准/变量命名) | L30-48 | 报告质量的底线规则 | 🔴 |
| 2 | Phase 5 一致性校验 (statcheck + 统计约束 + 图表质量) | L737-879 | 报告数值与分析结果的交叉验证，含 statcheck 重算 p 值机制 | 🔴 |
| 3 | Phase 5d 统计约束合规检查 (P-R/M-R/D-R/S-R/V-R) | L765-779 | report 层面的约束交叉验证 | 🔴 |
| 4 | statcheck 异常处理 (4 级不一致处理) | L867-874 | 跨显著性阈值反转时的强制修正流程 | 🔴 |
| 5 | ★ STAGE 4 CHECKPOINT (report_only vs full_paper 决策) | L1057-1088 | Pipeline 决策节点，决定是否进入论文写作 | 🔴 |
| 6 | 论文写作 12-Agent Team 定义 | L1110-1247 | 12 个 Agent 角色 + 11 种模式 + 8 Phase 工作流 + Generator-Evaluator 合同协议 | 🟡 |
| 7 | 图表类型→模板映射表 (20+ 种图表) | L529-557 | 分析类型到图表模板的完整映射 | 🟡 |
| 8 | 检查点量化标准 (6 个检查点) | L951-963 | Phase 2/5d/5e/6 的通过/阻断标准 | 🔴 |

### 1.4 calibration/SKILL.md (1061 行)

| # | 内容 | 行号范围 | 为什么不能丢 | 风险等级 |
|---|------|---------|-------------|---------|
| 1 | IRON RULES (金标准独立性/FP+FN 并重/改进建议) | L27-31 | 校准结果可信度的底线 | 🔴 |
| 2 | 门闸校验阈值 (TPR≥0.90/FPR≤0.10/MMR≥0.85/MAPE≤10%) | L398-420 | Pipeline Stage 3.5 动态门闸的判定依据 | 🔴 |
| 3 | 校准指标公式表 (Brier/ECE/HL/MMR/Δ/FPR/FNR/MSF/ESF) | L138-151 | 9 个校准指标的计算公式和阈值 | 🔴 |
| 4 | StatLLM 四任务分层评估 (T1-T4) | L642-678 | 外部基准评估框架，替代单一准确率 | 🔴 |
| 5 | MedHELM 全维度评估 (准确性/安全性/有效性/置信度/一致性/公平性) | L680-694 | 安全性=0有害结论是硬性门闸 | 🔴 |
| 6 | RWE-LLM 对抗性测试集 (5 个危险场景) | L696-718 | 小样本过度推断/多重比较/观察性当因果/数据泄露/零事件 | 🔴 |
| 7 | 校准系统自校验 (3 项自检) | L544-573 | 校准引擎自身的正确性验证 | 🔴 |
| 8 | 门闸联动详细规则 (Python 伪代码) | L752-795 | Stage 3.5 动态阈值判定的具体实现逻辑 | 🔴 |
| 9 | 公平性校准 (MSF/ESF/CC/SAC/PAT 5 个指标) | L891-1027 | 检测系统性偏见，ESF<0.80 或 CC<0.85 时强制人工审核 | 🔴 |
| 10 | 反例与黑名单 (金标准/校准执行/门闸联动/外部基准/公平性 共 23 条) | L514-541, L740-748, L1017-1027 | 防止校准失效的具体禁忌 | 🟡 |

### 1.5 pipeline/SKILL.md (785 行)

| # | 内容 | 行号范围 | 为什么不能丢 | 风险等级 |
|---|------|---------|-------------|---------|
| 1 | IRON RULE (纯调度架构，不做实质性工作) | L18-21 | 编排器的核心定位约束 | 🔴 |
| 2 | Pipeline Stages 流程图 (7 阶段 + 3 门闸) | L24-79 | 整个流水线的可视化定义 | 🔴 |
| 3 | Intent Detection & Mid-Entry 前置检查 | L83-111 | 用户入口阶段的自动检测和前置产物验证 | 🔴 |
| 4 | Stage 1.5 DATA QUALITY GATE (9 项阻断检查) | L196-231 | 数据质量门闸，含关键项定义(5/6/7/9) | 🔴 |
| 5 | Stage 2.5 SAP QUALITY GATE (8 项阻断检查) | L249-273 | SAP 质量门闸，含关键项定义(3/5/7) | 🔴 |
| 6 | Stage 3.5 RESULTS QUALITY GATE (14 项阻断检查) | L299-335 | 结果质量门闸，含校准联动 + 关键项定义(1/3/4/10/11/12/13) | 🔴 |
| 7 | Checkpoint Protocol 三级分层 (MANDATORY/SLIM/ADAPTIVE) | L363-461 | 6 个 MANDATORY + 4 个 SLIM + 5 个 ADAPTIVE 触发条件 | 🔴 |
| 8 | 收敛检测与回退循环控制 (3 次退回→BLOCK) | L633-660 | 防止同一环节无限循环 | 🔴 |
| 9 | Agent Dispatch Mode (角色切换规则 + Agent 速查表) | L533-594 | 5 个 Agent 的调度规则和禁止行为 | 🟡 |
| 10 | Error Handling & Rollback (错误处理优先级) | L598-660 | 3 级错误处理 + 多信号冲突处理 | 🔴 |
| 11 | Progress Tracking (Passport 初始化/状态/产物追踪) | L464-530 | 贯穿全流程的状态管理 | 🟡 |

---

## 2. 重构风险矩阵

### 🔴 高风险操作（可能导致核心功能失效）

| # | 操作 | 影响范围 | 具体风险 | 缓解措施 |
|---|------|---------|---------|---------|
| H1 | 删除 pipeline/SKILL.md 中的质量门闸内联定义 (L196-335) | 全 Pipeline | 3 个门闸共 31 项检查是 Pipeline 的核心阻断机制。如果 shared/quality_gates/*.md 中的内容与原文不完全一致，将导致门闸判定标准偏移 | 抽取后必须逐项 diff 对比；保留原文直到验证通过 |
| H2 | 删除 analysis-exec/SKILL.md 中的统计约束追踪表 (L794-1029) | Phase 3 + Phase 4 + Stage 3.5 | M-R/D-R/V-R/P-R 四张表是 Phase 4 质检和 Stage 3.5 门闸的输入。如果 phases/ 中的版本遗漏了任何一行，将导致约束追踪缺失 | 完整复制到 phases/03.2-constraint-tracking.md，然后 diff |
| H3 | 删除 analysis-exec/SKILL.md 中的反例与黑名单 (L253-345) | 全分析流程 | **L253-345 和 L1288-1344 是完全重复的内容**。删除时必须确保至少保留一份，且引用 shared/anti-patterns/ 的链接正确 | 保留一份引用，删除重复；验证 shared/anti-patterns/medical_stats_anti_patterns.md 包含对应内容 |
| H4 | report/SKILL.md 中论文写作 12-Agent Team 抽取 | report + paper-writing | L1110-1247 的 12 Agent 定义 + 11 Mode + 8 Phase + Generator-Evaluator 合同协议是一整套自洽系统。部分抽取可能导致 Agent 角色定义不完整。**注意：peer-review skill 已存在且职责是期刊同行评审（5 审稿人），与论文写作（12 Agent 生成论文）完全不同，不可合并** | Sprint 1：整体抽取为 `report/phases/07-paper-writing.md`（已实施）；Sprint 2/3 如需独立 skill，创建 `skills/paper-writing/`，不可复用 peer-review 名称。report/SKILL.md 仅保留引用链接 + 双模式入口 |
| H5 | 修改 manifest.json 中的 entry_point 路径 | 全命令系统 | manifest.json 定义了 17 个命令的入口。任何 entry_point 路径修改错误将导致命令无法触发 | 修改后逐个命令验证 entry_point 可达性 |
| H6 | 删除 calibration/SKILL.md 中的门闸联动伪代码 (L752-795) | Stage 3.5 门闸 | Python 伪代码定义了门闸校验的具体判定逻辑，如果抽取后逻辑有误，将导致门闸误判 | 抽取到 shared/calibration/ 后，与 shared/quality_gates/gate_runner.py 交叉验证 |
| H7 | 删除 pipeline/SKILL.md 中的 Checkpoint Protocol (L363-461) | 全 Pipeline | 6 个 MANDATORY checkpoint 的定义如果丢失或修改，将导致用户失去关键决策控制 | 抽取到 shared/ 后，主文件必须保留 MANDATORY checkpoint 汇总表 |

### 🟡 中风险操作（可能导致部分功能降级）

| # | 操作 | 影响范围 | 具体风险 | 缓解措施 |
|---|------|---------|---------|---------|
| M1 | analysis-plan/SKILL.md Phase 1.5 抽取到 phases/ | analysis-plan Phase 1.5 | Step 1.5.0-1.5.6 共 7 个 Step 是连续流程，抽取时如果 Step 间的引用断裂，将导致流程不连贯 | 抽取后验证 Step 间引用完整性 |
| M2 | analysis-plan/SKILL.md Phase 2 方法选择决策树抽取 | analysis-plan Phase 2 | 15-goal 112-method 决策树 + 假设转换流水线 + 效应量要求是一个整体，抽取时容易遗漏分支 | 抽取后用决策树覆盖测试验证 |
| M3 | shared/ 目录新增 INDEX.md 导航索引 | shared/ 163+ 文件 | 如果索引分类不当，将导致 LLM 无法找到正确的引用文件 | 按主题分类 + 按使用场景分类双索引 |
| M4 | agents/*.md 与 SKILL.md 中内联角色定义的单一化 | agents/ + 5 SKILL.md | pipeline/SKILL.md L533-594 的 Agent 速查表如果改为纯引用，LLM 可能不主动加载 agents/ 文件 | SKILL.md 保留 Agent 速查表摘要（1 行/Agent），完整定义引用 agents/ |
| M5 | commands/ 与 manifest.json 对齐 | commands/ + manifest.json | manifest.json 有 17 个命令，commands/ 有 13 个文件，5 个命令直接指向 skills/。对齐时可能遗漏 | 见第 4 节详细分析 |
| M6 | calibration/SKILL.md 中 7 个模式抽取到 shared/calibration/ | calibration 全模式 | 模式间的引用关系复杂（模式 5 的安全验证是模式 5 的子模块），抽取时可能破坏引用 | 保持模式编号一致性，抽取后验证交叉引用 |
| M7 | report/SKILL.md 中 statcheck 机制抽取 | report Phase 5 | statcheck 的正则模式、重算公式、4 级判定标准如果抽取不完整，将导致统计验证失效 | 抽取后运行 test_statcheck.py 验证 |

### 🟢 低风险操作（不太可能导致功能失效，但需注意）

| # | 操作 | 影响范围 | 具体风险 | 缓解措施 |
|---|------|---------|---------|---------|
| L1 | 删除 analysis-exec/SKILL.md 中的重复"命令"和"Mode"章节 | analysis-exec | L234-250 和 L1269-1287 是重复内容，删除安全 | 确认 L234-250 保留 |
| L2 | 删除各 SKILL.md 中的"执行时间估算"表 | 各 SKILL.md | 时间估算是参考信息，不影响功能 | 可移至 phases/ 或 quick reference |
| L3 | 删除各 SKILL.md 中的"常见错误与解决方案"表 | 各 SKILL.md | 参考信息，不影响核心逻辑 | 可移至 phases/ 对应文件 |
| L4 | pyproject.toml 依赖分层 | pyproject.toml | 分层不当可能导致扩展模块依赖缺失 | 分层后运行全部 319 测试验证 |
| L5 | shared/ 子目录重组 | shared/ | 文件移动后引用路径需同步更新 | 全局搜索引用路径 |

---

## 3. 引用路径变更影响评估

### 3.1 SKILL.md 内部引用（高影响）

phases/ 抽取后，以下 SKILL.md 中的内部引用需要同步更新：

| 文件 | 引用类型 | 当前形式 | 风险点 |
|------|---------|---------|--------|
| analysis-exec/SKILL.md | Phase 文件索引 | `phases/00-exec-precheck.md` 等 7 个 | ✅ 已有索引表，抽取后只需更新索引表内容 |
| analysis-plan/SKILL.md | Phase 文件索引 | `phases/01-deep-eda.md` (1 个已有) + 5 个待新建 | 🟡 新建 5 个 phases 文件后需更新索引表 |
| report/SKILL.md | Phase 文件索引 | `phases/00-result-interpretation.md` (1 个已有) + 6 个待新建 | 🟡 新建 6 个 phases 文件后需更新索引表 |
| calibration/SKILL.md | 无 phases/ | 无 | 🔴 完全新建 phases/ 目录，需添加索引表 |
| pipeline/SKILL.md | 无 phases/ | 无 | 🔴 完全新建 phases/ 目录，需添加索引表 |

### 3.2 跨文件引用（中影响）

以下文件引用了 SKILL.md 或 phases/ 路径，抽取后需同步更新：

| 引用方 | 被引用方 | 引用方式 | 风险点 |
|--------|---------|---------|--------|
| pipeline/SKILL.md L540-542 | agents/exec_runner_agent.md 等 | 相对路径 `../../agents/` | 🟢 不受 phases/ 抽取影响 |
| pipeline/SKILL.md L466 | shared/passport/passport.py | Python import | 🟢 不受影响 |
| analysis-exec/SKILL.md L36-45 | shared/ 多个文件 | 相对路径引用 | 🟢 不受 phases/ 抽取影响 |
| report/SKILL.md L288 | pipeline/SKILL.md §Stage 5 | 章节引用 | 🟡 如果 pipeline 拆分 phases/，§Stage 5 引用需更新 |
| commands/msra-exec.md | skills/analysis-exec/SKILL.md | entry_point | 🟢 不受影响（除非 manifest.json 修改） |
| tests/test_enhanced_deliverables.py | skills/report/SKILL.md | Path 引用 | 🟢 不受影响（文件名不变） |
| scripts/lint_skill_structure.py | 各 SKILL.md | Path 引用 | 🟢 不受影响 |
| scripts/lint_gate_counts.py | skills/pipeline/SKILL.md | 默认路径 | 🟢 不受影响 |
| scripts/check_pipeline_integrity.py | 各 SKILL.md | Path 引用 | 🟢 不受影响 |
| agents/implementations/hybrid_mode_bridge.py | SKILL.md Phase 2 | 文本引用 | 🟡 如果 Phase 2 抽取到 phases/，引用需更新 |
| shared/reproducibility/pipeline_auditor.py | data-prep/SKILL.md | 文本引用 | 🟢 不受影响 |

### 3.3 phases/ 文件间引用（低影响）

新建的 phases/ 文件之间的交叉引用需要确保一致性：

| 引用方 | 被引用方 | 风险点 |
|--------|---------|--------|
| phases/03-inferential-analysis.md | phases/03.1-observational-methods.md | 🟡 新建文件间引用 |
| phases/03-inferential-analysis.md | phases/03.2-constraint-tracking.md | 🟡 新建文件间引用 |
| phases/03-inferential-analysis.md | phases/03.3-hybrid-prompting.md | 🟡 新建文件间引用 |
| phases/03-inferential-analysis.md | phases/03.4-self-healing.md | 🟡 新建文件间引用 |

---

## 4. manifest.json 对齐风险

### 4.1 当前对齐状态

manifest.json 定义了 **17 个命令**，commands/ 目录有 **13 个命令文件**，skills/ 目录有 **14 个 skill 目录**。

| 命令 | entry_point 类型 | 指向 | commands/ 有对应文件？ | skills/ 有对应目录？ | 对齐状态 |
|------|-----------------|------|---------------------|---------------------|---------|
| /msra | skills/ | skills/pipeline/SKILL.md | ✅ msra.md | ✅ pipeline/ | ✅ 对齐 |
| /msra-paper | skills/ | skills/pipeline/SKILL.md | ❌ 无 | ✅ pipeline/ | 🟡 无独立 command 文件 |
| /msra-data | skills/ | skills/data-prep/SKILL.md | ❌ 无 | ✅ data-prep/ | 🟡 无独立 command 文件 |
| /msra-explore | skills/ | skills/exploratory-causal/SKILL.md | ❌ 无 | ✅ exploratory-causal/ | 🟡 无独立 command 文件 |
| /msra-plan | skills/ | skills/analysis-plan/SKILL.md | ❌ 无 | ✅ analysis-plan/ | 🟡 无独立 command 文件 |
| /msra-exec | skills/ | skills/analysis-exec/SKILL.md | ❌ 无 | ✅ analysis-exec/ | 🟡 无独立 command 文件 |
| /msra-report | skills/ | skills/report/SKILL.md | ❌ 无 | ✅ report/ | 🟡 无独立 command 文件 |
| /msra-calibrate | skills/ | skills/calibration/SKILL.md | ❌ 无 | ✅ calibration/ | 🟡 无独立 command 文件 |
| /msra-cross | skills/ | skills/cross-domain/SKILL.md | ❌ 无 | ✅ cross-domain/ | 🟡 无独立 command 文件 |
| /msra-bio | skills/ | skills/bioinformatics/SKILL.md | ❌ 无 | ✅ bioinformatics/ | 🟡 无独立 command 文件 |
| /msra-imaging | skills/ | skills/imaging-analysis/SKILL.md | ❌ 无 | ✅ imaging-analysis/ | 🟡 无独立 command 文件 |
| /msra-rt | skills/ | skills/realtime-monitor/SKILL.md | ❌ 无 | ✅ realtime-monitor/ | 🟡 无独立 command 文件 |
| /msra-write | commands/ | commands/msra-write.md | ✅ | ❌ 无独立 skill | 🟡 无独立 skill 目录 |
| /msra-full | commands/ | commands/msra-full.md | ✅ | ❌ 无独立 skill | 🟡 无独立 skill 目录 |
| /msra-reviewer | commands/ | commands/msra-reviewer.md | ✅ | ✅ peer-review/ | 🟡 command 名与 skill 名不一致 |
| /msra-modules | commands/ | commands/msra-modules.md | ✅ | ❌ 无独立 skill | 🟡 无独立 skill 目录 |
| /msra-status | commands/ | commands/msra-status.md | ✅ | ❌ 无独立 skill | 🟡 无独立 skill 目录 |

### 4.2 具体风险点

| # | 风险 | 严重度 | 说明 |
|---|------|--------|------|
| A1 | **12 个命令直接指向 skills/ 但无对应 commands/ 文件** | 🟡 | 如果 Claude Code 要求每个命令都有 commands/ 文件，这 12 个命令可能无法注册。但实际上 manifest.json 的 entry_point 直接指向 SKILL.md 也能工作 |
| A2 | **/msra-reviewer 指向 commands/msra-reviewer.md 但 skill 目录名为 peer-review/** | 🟡 | 命令名(msra-reviewer) 与 skill 目录名(peer-review) 不一致，可能导致混淆 |
| A3 | **/msra-paper 和 /msra 都指向 skills/pipeline/SKILL.md** | 🟢 | 同一 SKILL.md 被两个命令引用，Pipeline 内部需要根据命令区分行为。这不是重构引入的问题 |
| A4 | **stat-method-selector/ 和 systematic-survey/ 两个 skill 目录无对应命令** | 🟡 | 这两个 skill 被其他 skill 引用（analysis-plan 引用 stat-method-selector），但用户无法直接通过命令调用 |
| A5 | **重构后 report/SKILL.md 瘦身可能导致 /msra-report 的 entry_point 内容不完整** | 🔴 | 如果 entry_point 指向的 SKILL.md 被过度瘦身，LLM 加载时可能缺少关键上下文 |

### 4.3 对齐建议

1. **Sprint 2 中对齐 commands/ 与 manifest.json**：为每个指向 skills/ 的命令补充对应的 commands/ 路由文件（仅含一行引用），确保命令注册一致性
2. **保持 entry_point 不变**：除非有充分理由，不要修改 manifest.json 中的 entry_point 路径
3. **paper-writing 与 peer-review 职责分离**：peer-review skill 已存在且专注于期刊同行评审（5 审稿人 + ICMJE/CONSORT/STROBE 合规检查）。论文写作 12-Agent Team 已抽取为 `report/phases/07-paper-writing.md`。如 Sprint 2/3 需独立 skill，应创建 `skills/paper-writing/`，不可与 peer-review 合并。注意：report 的 `mock_reviewer` agent（模拟双盲审稿）与 peer-review skill 存在功能重叠，Sprint 2 可考虑合并

---

## 5. 回滚方案

### 5.0 已有备份

项目已在 `backups/pre-refactor-2026-06-25/` 目录中创建了以下备份：
- `analysis-exec-SKILL.md.bak` (68222 bytes)
- `analysis-plan-SKILL.md.bak` (68206 bytes)
- `calibration-SKILL.md.bak` (53604 bytes)
- `pipeline-SKILL.md.bak` (43575 bytes)
- `report-SKILL.md.bak` (66455 bytes)
- `manifest.json.bak` (8628 bytes)
- `analysis-exec-phases/` (7 个 phases 文件备份)
- `analysis-plan-phases/` (1 个 phases 文件备份)
- `report-phases/` (1 个 phases 文件备份)

### 5.1 Sprint 1 回滚（技能瘦身）

| 回滚步骤 | 操作 | 预计时间 |
|---------|------|---------|
| 1 | `git stash` 或 `git checkout -- skills/` 恢复所有 SKILL.md | <1 分钟 |
| 2 | 如果 git 不可用，从 backups/ 恢复：`cp backups/pre-refactor-2026-06-25/*-SKILL.md.bak skills/*/SKILL.md` | <2 分钟 |
| 3 | 删除新建的 phases/ 文件（仅删除 Sprint 1 新建的，保留已有的） | <1 分钟 |
| 4 | 验证：运行 `pytest tests/ -x` 确认 319 个测试全部通过 | ~5 分钟 |
| 5 | 验证：运行 `python scripts/lint_skill_structure.py` 确认结构一致性 | <1 分钟 |

**回滚触发条件**：
- 任何一个 SKILL.md 瘦身后测试失败
- 任何一个 phases/ 文件内容与原 SKILL.md 对应章节不一致
- 检查点汇总表信息丢失

### 5.2 Sprint 2 回滚（架构解耦）

| 回滚步骤 | 操作 | 预计时间 |
|---------|------|---------|
| 1 | `git revert` Sprint 2 的 commit | <1 分钟 |
| 2 | 恢复 manifest.json：`cp backups/pre-refactor-2026-06-25/manifest.json.bak manifest.json` | <1 分钟 |
| 3 | 恢复 shared/ 目录中的被修改文件 | <2 分钟 |
| 4 | 删除 shared/quality_gates/ 中新建的 .md 文件（保留 .py 文件） | <1 分钟 |
| 5 | 删除 shared/INDEX.md | <1 分钟 |
| 6 | 验证：运行全量测试 | ~5 分钟 |

**回滚触发条件**：
- 质量门闸抽取后，门闸检查结果与抽取前不一致
- commands/ 与 manifest.json 对齐后命令无法触发
- agents/ 角色单一化后 Agent 调度失败

### 5.3 Sprint 3 回滚（扩展性增强）

| 回滚步骤 | 操作 | 预计时间 |
|---------|------|---------|
| 1 | `git revert` Sprint 3 的 commit | <1 分钟 |
| 2 | 恢复 pyproject.toml | <1 分钟 |
| 3 | 恢复 contracts/ 中的 schema 文件 | <1 分钟 |
| 4 | 验证：运行全量测试 + E2E 测试 | ~10 分钟 |

**回滚触发条件**：
- 扩展模块接入门闸框架后门闸误判
- Schema 版本统一后旧数据不兼容
- 依赖分层后扩展模块导入失败

---

## 6. 数据安全建议

### 6.1 备份策略

| 策略 | 说明 | 状态 |
|------|------|------|
| **Git 快照** | 每个 Sprint 开始前创建 `git tag pre-sprint-{N}` | ⚠️ 尚未创建 |
| **文件备份** | 已有 `backups/pre-refactor-2026-06-25/` | ✅ 已完成 |
| **Phases 备份** | 已有 phases/ 子目录备份 | ✅ 已完成 |
| **manifest.json 备份** | 已有 .bak 文件 | ✅ 已完成 |

**建议补充**：
1. 每个 Sprint 开始前创建 git tag：`git tag pre-sprint-1`, `git tag pre-sprint-2`, `git tag pre-sprint-3`
2. 每个 SKILL.md 瘦身后、测试通过前，创建 `git stash` 作为临时回滚点
3. Sprint 2 修改 manifest.json 前，创建 `manifest.json.sprint2.bak`

### 6.2 Diff 审查策略

每个 SKILL.md 瘦身后，必须执行以下 diff 审查：

| 审查项 | 方法 | 通过标准 |
|--------|------|---------|
| **内容完整性** | `diff <(sed 's/[[:space:]]*$//' original.md) <(cat new.md phases/*.md)` | 所有非空白行差异均可解释为"移动"而非"删除" |
| **检查点完整性** | `grep -c "MANDATORY\|SLIM\|ADAPTIVE\|GATE" new.md` | 检查点数量 ≥ 原文 |
| **反例完整性** | `grep -c "禁止行为\|🚫" new.md phases/*.md` | 反例数量 ≥ 原文 |
| **引用完整性** | `grep -oP 'shared/[^\s)]+' new.md` | 所有 shared/ 引用路径可达 |
| **Phase 索引一致性** | 索引表中的文件名与 phases/ 目录中的实际文件名一致 | 100% 一致 |

### 6.3 测试验证策略

| 阶段 | 测试范围 | 通过标准 |
|------|---------|---------|
| **每个 SKILL.md 瘦身后** | `pytest tests/ -x --tb=short` | 319 个测试全部通过 |
| **Sprint 1 完成后** | `pytest tests/ -x + pytest tests/e2e/ -x` | 319 + 53 E2E 测试全部通过 |
| **Sprint 2 完成后** | 全量测试 + `python scripts/lint_skill_structure.py` + `python scripts/lint_gate_counts.py` + `python scripts/check_pipeline_integrity.py` | 全部通过 |
| **Sprint 3 完成后** | 全量测试 + E2E + 跨模块 Handoff 测试 | 全部通过 |

### 6.4 关键逻辑保护清单

以下逻辑在重构过程中**必须逐行验证**，不能仅靠测试覆盖：

| # | 逻辑 | 位置 | 验证方法 |
|---|------|------|---------|
| 1 | Stage 1.5 门闸 9 项检查的"关键项"定义 (5/6/7/9) | pipeline L230 | grep "关键项" 确认保留 |
| 2 | Stage 2.5 门闸 8 项检查的"关键项"定义 (3/5/7) | pipeline L272 | grep "关键项" 确认保留 |
| 3 | Stage 3.5 门闸 14 项检查的"关键项"定义 (1/3/4/10/11/12/13) | pipeline L335 | grep "关键项" 确认保留 |
| 4 | S-R01~R08 的 8 种统计原则违反处理 | analysis-exec L949-963 | 逐条对比 |
| 5 | P-R01~R07 的 P 值格式化规则 | 多处引用 | grep "P-R01" 确认引用可达 |
| 6 | 自愈机制 5 层流程的完整步骤 | analysis-exec L621-658 | 逐层对比 |
| 7 | 校准门闸 6 个阈值 (TPR/TNR/FPR/FNR/MMR/MAPE) | calibration L404-411 | 逐值对比 |
| 8 | 收敛检测 3 次退回规则 | pipeline L647-653 + analysis-plan L169-176 | 两处规则一致 |
| 9 | 审计日志不可变性保障 4 项机制 | analysis-exec L1211-1218 | 逐项对比 |
| 10 | 公平性硬门闸 (ESF<0.80 或 CC<0.85) | calibration L1027 | grep "IRON RULE" 确认保留 |

---

## 7. 额外发现

### 7.1 已确认的 P0-2 重复内容

analysis-exec/SKILL.md 中的反例与黑名单确实存在完全重复：
- **L253-345**: 反例与黑名单（执行纪律/统计方法/代码/流程/ML禁忌）
- **L1288-1344**: 与 L253-345 完全相同的内容

**建议**：删除 L1288-1344，保留 L253-345 并改为引用 `shared/anti-patterns/medical_stats_anti_patterns.md`。

### 7.2 analysis-exec/SKILL.md 的内联 Phase 与 phases/ 文件可能不一致

SKILL.md 中 L347-1267 包含 Phase 0.5/0.6/1/2/3/4/5/6 的详细内联规范，同时 phases/ 目录已有 7 个对应的 phases 文件。需要验证内联内容与 phases/ 文件内容是否一致：

- 如果一致：安全删除内联内容
- 如果不一致：需要确认哪个版本是权威版本，可能导致内容丢失

### 7.3 report/SKILL.md 的 Phase 索引表引用了不存在的 phases 文件

report/SKILL.md L296-306 的 Phase 文件索引表列出了 7 个 phases 文件，但 phases/ 目录中只有 1 个文件 (`00-result-interpretation.md`)。其余 6 个文件（`02-table-generation.md`、`03-figure-integration.md`、`04-methodology.md`、`05-consistency-check.md`、`06-report-assembly.md`、`07-paper-writing.md`）尚不存在。如果 LLM 尝试加载这些文件将失败。

### 7.4 calibration/SKILL.md 无 phases/ 目录

calibration/SKILL.md (1061 行) 完全没有 phases/ 目录，所有 7 个模式的详细规范都内联在主文件中。这是抽取工作量最大的一个 SKILL。

### 7.5 pipeline/SKILL.md 的 Agent Dispatch 引用了 agents/protocol.md

pipeline/SKILL.md L594 引用了 `agents/protocol.md`，但 agents/ 目录中只有 `AGENTS.md` 和 `multi_agent_specification.md`，没有 `protocol.md`。这是一个已存在的断链问题，重构时不应引入新的断链。

### 7.6 analysis-exec S-R01~R08 定义内部不一致（Sprint 1 审查发现 → 已修复 ✅）

`skills/analysis-exec/phases/03.2-constraint-tracking.md` 中曾存在两份互相矛盾的 S-R01~R08 定义：
- ~~L118-128（"统计原则违反用户抉择"节）：6 项，S-R01=正态性违反~~ → 已改为引用权威版本
- L163-171（"假设检验检查点标准"节）：8 项完整版，S-R01=比例风险假设违反（保留为权威版本）

**根因**：pre-existing 问题，原始 SKILL.md 不同章节就有两份不同定义，瘦身时被合并到同一文件。
**修复**：verifier-analysis-exec 已将第一份改为指向权威版本的引用（L120: "完整定义见下方'Phase 3 假设检验检查点标准'节"）。
**验证**：code-reviewer 于 2026-06-25 确认修复 — L118-123 不再列出冲突定义，L163-171 权威版本完整保留。
**Sprint 2 兜底**：architect 已在方案中新增 §2.5.1 编码系统单一权威定义审计。

### 7.7 analysis-exec IRON RULES 引用不存在的 M1-M6 反模式代码（Sprint 1 审查发现）

`skills/analysis-exec/SKILL.md` L41 IRON RULES 引用 `A1/A3/B1/E1/M1-M6`，但 `shared/anti-patterns/medical_stats_anti_patterns.md` 中不存在 M 系列代码（实际代码为 A-J 系列）。
**根因**：pre-existing 问题，M1-M6 可能是早期版本的反模式命名，后被重命名为 A-J 系列但 IRON RULES 引用未同步更新。
**状态**：标记为 IMPORTANT，建议 Sprint 2 修复。

### 7.8 三个门闸 Python 实现与文档定义全面不一致（Sprint 1 审查发现，2026-06-25 更新）

`shared/quality_gates/check_items.py` 与 `shared/quality_gates/gate-*.md` + `pipeline/SKILL.md` 在**三个门闸**中均存在不一致，不仅仅是 Gate 3.5：

**Gate 1.5（数据质量门闸）— 关键项编号匹配但内容不同**：
- 关键项编号：Python [5,6,7,9] = 文档 [5,6,7,9] ✅
- 但项 4-8 的描述完全不同：
  - Python 项 4 = "异常值处理记录" vs 文档项 4 = "盲态审核完成"
  - Python 项 5 = "数据完整性" vs 文档项 5 = "数据库锁定确认"
  - Python 项 6 = "变量类型一致性" vs 文档项 6 = "逻辑一致性验证"
  - Python 项 7 = "值范围合理性" vs 文档项 7 = "值规范化完成"
  - Python 项 8 = "盲态审核完成" vs 文档项 8 = "可重复性"

**Gate 2.5（SAP 质量门闸）— 关键项编号和内容均不同**：
- 关键项编号：Python [4,6,8] vs 文档 [3,5,7] ❌
- Python 项 3 = "分析方法适当性"（非关键） vs 文档项 3 = "估计目标完整"（关键）
- Python 项 4 = "样本量论证充分性"（关键） vs 文档项 4 = "方法选择合理"（非关键）
- 完全是两套不同的检查标准

**Gate 3.5（结果质量门闸）— 关键项编号和内容均不同**：
- 关键项编号：Python [1,2,7,8,9] vs 文档 [1,3,4,10,11,12,13] ❌
- Python 9 项 vs 文档 14 项
- 如前述分析

**根因**：pre-existing 架构债务。check_items.py 是早期简化版，gate-*.md 是后来扩展的完整版，两者从未同步。
**影响**：如果 gate_runner.py 调用 check_items.py 执行门闸检查，实际阻断逻辑与文档描述在三个门闸中都不一致。
**建议**：Sprint 3 以 gate-*.md 为权威版本，将 check_items.py 全部三个门闸重写为文档版本。Sprint 2 引用可达性扫描中标记为已知问题。
**严重等级**：🟡 IMPORTANT — 不阻塞 Sprint 1（pre-existing），但需在 Sprint 3 统一。

---

## 8. Sprint 1 审查结论（2026-06-25 更新）

### 审查结果

| SKILL | 审查结果 | 发现 |
|-------|---------|------|
| analysis-exec | ✅ 通过 (C-1 已修复) | I-2 (M1-M6 引用无效, 待 Sprint 2 修复) |
| pipeline | ⚠️ | I-1 (agents/protocol.md 断链, 已跟踪) — I-3 (MANDATORY ID, 已修复) |
| report | ✅ 通过 | 无问题 |
| calibration | ✅ 通过 | 无问题 |
| analysis-plan | ✅ 通过 | 无问题 |

### 10 项关键逻辑验证

| # | 验证项 | 结果 |
|---|--------|------|
| 1 | IRON RULES 保留在主文件 | ✅ 5/5 |
| 2 | 检查点汇总表保留在主文件 | ✅ 5/5 |
| 3 | 质量门闸关键项定义 | ✅ |
| 4 | S-R01~R08 存在性 + 一致性 | ✅ (C-1 已修复, 单一权威定义) |
| 5 | P-R01~R07 存在性 | ✅ |
| 6 | 自愈 5 层流程 | ✅ |
| 7 | 校准门闸 6 阈值 | ✅ |
| 8 | 收敛检测 3 次规则 | ✅ |
| 9 | 审计日志不可变性 | ✅ |
| 10 | 公平性硬门闸 | ✅ |

### Sprint 2 建议

1. **定义一致性审计**：对 S-R/P-R/M-R/D-R/V-R 等编码系统，确保每个编码在整个 skill 中只有一份权威定义
2. **引用可达性扫描**：对所有 SKILL.md 和 phases/ 中的 `shared/`、`agents/`、`../../` 引用做批量可达性验证
3. **反模式代码验证**：验证所有引用的反模式代码在 shared/anti-patterns/ 中实际存在
