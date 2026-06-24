# MSRA v1.0 优化评估报告

> **评估日期**: 2026-06-24
> **评估范围**: 全项目代码、测试、文档、模板、流水线设计
> **评估方法**: 系统性代码审查 + 已有 OPTIMIZATION_PLAN 交叉比对 + 行业对标
> **状态**: 待实施（按优先级排序）

---

## 一、评估总结

MSRA v1.0.0 是一个功能完整的医学统计分析插件，涵盖从数据准备到论文写作的全链路。经过全面审查，我发现以下 **5 大类 23 项优化点**，按实施优先级分为 P0（关键）、P1（重要）、P2（改进）三级。

### 项目优势（已完成）

| 维度 | 状态 | 说明 |
|------|------|------|
| 流水线架构 | ✅ 优秀 | 7 阶段 + 5 个阻断式门闸，调度器不做实质性工作的设计非常干净 |
| 质量门闸 | ✅ 优秀 | GateRunner 统一接口，PASS/CONDITIONAL/BLOCKED 三级判定 |
| 统计方法覆盖 | ✅ 优秀 | 56 章统计方法指南，从基础 t 检验到孟德尔随机化 |
| 报告规范 | ✅ 优秀 | 21 个报告规范 + 5 个偏倚评估工具 |
| 扩展模块 | ✅ Stable | 4 个模块全部 Stable，319 测试全通过 |
| 大规模处理 | ✅ 优秀 | Polars/DuckDB/Dask 三级引擎 + 自动降级 |
| 模板体系 | ✅ 优秀 | 27 个 Python 模板 + 对应 R 模板，双语言覆盖 |

---

## 二、优化建议（23 项）

### P0 — 关键优化（建议立即实施）

#### O-01: 测试覆盖不足 — 核心模板缺少单元测试

**现状**: `shared/templates/` 下有 27 个 Python 模板，但 `tests/` 中仅覆盖了 `data_profile`、部分 passport 和 quality gate 测试。核心统计模板（cox_template、logistic_template、prediction_model_template、ml_analysis_template 等）缺少独立单元测试。

**影响**: 模板代码的正确性完全依赖 LLM 执行时的临时验证，无法在 CI 中自动捕获回归。

**建议**:
- 为每个模板创建 `tests/test_templates/test_{name}.py`，至少覆盖：正常输入、空输入、缺失值输入
- 在 CI 中添加 `pytest tests/test_templates/` 步骤
- 优先覆盖：prediction_model_template、ml_analysis_template、cox_template、logistic_template

**预估工作量**: 3-5 天

---

#### O-02: SKILL.md 文件过于臃肿

**现状**: `skills/pipeline/SKILL.md` 和 `skills/analysis-exec/SKILL.md` 等主 SKILL.md 文件体积庞大（pipeline SKILL.md 单文件可能超过 1000 行），包含大量内联示例、角色定义、检查清单。这导致：
1. LLM 上下文窗口浪费严重（每次调用都加载完整 SKILL.md）
2. 维护困难（修改一个检查项需要在多个位置同步）
3. 版本漂移风险（同一信息在 SKILL.md 和 shared/ 中重复）

**建议**:
- 采用 OPTIMIZATION_PLAN.md 中已规划的「Phase 详细规范抽取到 phases/ 目录」模式
- 主 SKILL.md 保留架构图 + 索引表 + 检查点汇总（< 300 行）
- 详细规范抽取到 `skills/{name}/phases/` 目录
- 通过 `works_with` 引用而非内联

**预估工作量**: 2-3 天

---

#### O-03: TemplateManager 注册不完整

**现状**: `shared/templates/template_manager.py` 的 `TEMPLATE_MAPPING` 仅注册了 12 种模板类型（BASELINE、FOREST_PLOT、COX、LOGISTIC、ROC、GEE、BLAND_ALTMAN、SAMPLE_SIZE、SURVIVAL、REGRESSION、CORRELATION、ANOVA），但实际模板文件有 27 个。

**缺失注册的模板**:
- prediction_model_template（预测模型）
- ml_analysis_template（机器学习）
- shap_plot_template（SHAP 可解释性）
- instrumental_variable_template（工具变量）
- regression_discontinuity_template（断点回归）
- synthetic_control_template（合成控制）
- bayesian_analysis_template（贝叶斯分析）
- adaptive_interim_analysis_template（适应性设计）
- multicenter_template（多中心分析）
- rmst_template（限制性平均生存时间）
- effect_size_template（效应量计算）
- bland_altman_template（Python 版）
- variable_dag_template（变量 DAG）
- data_profile_template（数据画像）
- publication_figure_template（发表级图表）
- extended_figure_templates（扩展图表）

**影响**: 用户通过 TemplateManager 接口无法调用 56% 的模板，只能直接 import 模块。

**建议**:
- 扩展 `TemplateType` 枚举，注册所有 27 个模板
- 添加 `get_template_by_name()` 方法支持按名称查找
- 考虑动态注册机制（扫描 templates/ 目录自动发现）

**预估工作量**: 1 天

---

#### O-04: R 模板与 Python 模板不对等

**现状**: `shared/templates/` 下有 27 个 Python 模板，但对应的 R 模板（`.R` 文件）数量不匹配。TemplateManager 中的映射假设每个 Python 模板都有对应 R 版本，但实际并非如此。

**影响**: 双语言验证（Python 结果 vs R 结果交叉验证）无法完整执行，这是 MSRA 可重复性承诺的缺口。

**建议**:
- 生成模板对等清单：标记哪些模板有 Python-only、R-only、双版本
- 优先为核心统计模板（Cox、Logistic、ANOVA、Meta-analysis）补齐 R 版本
- 在 TemplateManager 中对单语言模板标记 `[SINGLE-LANG]`

**预估工作量**: 2-3 天

---

### P1 — 重要优化（建议在 v1.1 中实施）

#### O-05: 缺少 CLI 入口点

**现状**: `pyproject.toml` 中注释掉了 CLI 入口点（`# msra = "msra_modules.cli:main"`），`msra_modules/cli.py` 存在但未被激活。用户必须通过 Claude Code 的斜杠命令使用，无法在终端中直接运行。

**影响**: 限制了非 Claude Code 用户的使用场景，也无法集成到 CI/CD 流水线中。

**建议**:
- 激活 CLI 入口点，支持 `msra --status`、`msra --profile data.csv`、`msra --gate 1.5` 等命令
- 保持 Claude Code 斜杠命令为主入口，CLI 为辅助入口

**预估工作量**: 1-2 天

---

#### O-06: 缺少 CHANGELOG 自动化

**现状**: CHANGELOG.md 是手动维护的，v1.0.0 的条目非常详细（约 60 行），但 v0.9.x 的条目逐渐简化。随着版本迭代，手动维护 CHANGELOG 的成本会越来越高。

**建议**:
- 引入 `git-cliff` 或 `conventional-commits` 自动生成 CHANGELOG
- 在 CI 中添加 CHANGELOG 生成步骤
- 保留手动编辑权（自动生成 + 人工审核）

**预估工作量**: 0.5 天

---

#### O-07: 缺少依赖版本锁定

**现状**: `requirements.txt` 和 `pyproject.toml` 使用宽松版本约束（如 `pandas>=1.5`），没有 `requirements.lock` 或 `poetry.lock`。

**影响**: 不同用户的安装结果可能不同（依赖版本差异），导致不可复现的行为。

**建议**:
- 生成 `requirements.lock`（pip-compile 或 poetry lock）
- 在 CI 中使用锁定版本测试
- 定期更新锁定版本（dependabot 或 renovate）

**预估工作量**: 0.5 天

---

#### O-08: 缺少健康检查 / 环境验证命令

**现状**: `install.ps1` 和 `install.sh` 做了安装，但没有独立的 `msra --doctor` 或 `msra --check-env` 命令来验证运行环境。

**建议**:
- 创建 `scripts/check_environment.py`，检查：
  - Python 版本 ≥ 3.9
  - R 版本 ≥ 4.0（可选）
  - 核心依赖是否安装（pandas、numpy、scipy、statsmodels、lifelines）
  - 可选依赖状态（dask、polars、duckdb、scanpy、SimpleITK）
  - 输出目录权限
- 注册为 `/msra-doctor` 命令

**预估工作量**: 1 天

---

#### O-09: Gate 1.5 检查项数量不一致

**现状**: README.md 和 pipeline SKILL.md 中的流程图标注 Gate 1.5 为 "9 项检查"，但 pipeline SKILL.md §3 的 Stage 1.5 描述中写的是 "8 项检查"。CHANGELOG v0.7.4 修复过一次数量不一致，但似乎仍有残留。

**建议**:
- 统一所有文档中 Gate 1.5 的检查项数量
- 考虑使用 lint 脚本（已有 `scripts/lint_gate_counts.py`）在 CI 中自动验证

**预估工作量**: 0.5 天

---

#### O-10: exploratory-causal 模块与 analysis-plan 的衔接不够紧密

**现状**: Stage 1.8（exploratory-causal）产出的因果发现（PC/FCI 算法结果、混杂分析）在 Stage 2（analysis-plan）中没有自动传递机制。用户需要手动将探索性发现带入统计计划。

**建议**:
- 在 passport 中注册 `causal_discovery_results` artifact
- 在 analysis-plan Phase 2（Estimands）中增加自动引用 exploratory-causal 结果的逻辑
- 当 exploratory-causal 发现潜在混杂因子时，自动提醒用户在 SAP 中包含这些变量

**预估工作量**: 1-2 天

---

#### O-11: 缺少数据脱敏 / 假数据生成工具

**现状**: 虽然有 HIPAA Safe Harbor 标识符检测，但没有配套的数据脱敏工具。演示和测试时需要手动创建假数据。

**建议**:
- 创建 `shared/templates/data_anonymizer.py`，支持：
  - 日期偏移（保持时间间隔）
  - ID 替换（保持映射关系）
  - 数值加噪（保持分布特征）
  - 地址/姓名替换
- 创建标准演示数据集（demo_data.csv）用于教程和测试

**预估工作量**: 1-2 天

---

#### O-12: 缺少分析结果的可重复性验证

**现状**: 虽然有 `shared/reproducibility/reproducibility_guide.md`，但没有自动化的可重复性验证机制。执行分析后无法自动验证"用相同数据 + 相同 SAP 是否得到相同结果"。

**建议**:
- 创建 `scripts/verify_reproducibility.py`：
  - 记录分析执行的随机种子、环境变量、依赖版本
  - 支持重跑分析并与历史结果对比（数值容差范围内）
  - 输出可重复性验证报告
- 在 Stage 3.5 Gate 中增加可重复性检查项

**预估工作量**: 2-3 天

---

### P2 — 改进建议（v1.2+ 规划）

#### O-13: 缺少 Web UI / Dashboard

**现状**: 所有交互通过 Claude Code 对话完成，没有可视化 Dashboard 来展示 Pipeline 进度、门闸状态、分析结果。

**建议**:
- 创建轻量级本地 Web Dashboard（Flask/FastAPI + HTMX）
- 功能：Pipeline 进度可视化、门闸状态面板、分析结果预览、报告下载
- 可选：集成到 `reports/` 目录下的 HTML 报告中

**预估工作量**: 5-7 天

---

#### O-14: 缺少插件市场的发布机制

**现状**: 项目通过 GitHub 仓库分发，没有发布到 Claude Code 插件市场或 npm/PyPI。

**建议**:
- 准备 PyPI 发布（`pyproject.toml` 已就绪，需要完善 classifiers）
- 考虑 Claude Code 插件市场的发布流程
- 添加 `pip install medical-stats-research-assistant` 支持

**预估工作量**: 1-2 天

---

#### O-15: 缺少国际化（i18n）支持

**现状**: SKILL.md 和报告输出混合使用中英文。虽然 README 有双语版本，但 SKILL.md 内部的提示词、检查清单、错误消息没有统一的语言切换机制。

**建议**:
- 定义 `lang` 配置项（zh-CN / en）
- 将用户可见的提示词和消息抽取到 `shared/i18n/` 目录
- SKILL.md 中使用 `{i18n:key}` 占位符

**预估工作量**: 3-5 天

---

#### O-16: 缺少版本迁移指南

**现状**: 从 v0.9.x 到 v1.0.0 有大量变更（passport schema 新增字段、SKILL.md 重构、模块状态变更），但没有 MIGRATION.md 指导用户升级。

**建议**:
- 创建 `MIGRATION.md`，覆盖：
  - v0.9.x → v1.0.0 的破坏性变更
  - passport.json schema 变更（新增字段的默认值）
  - 新增依赖项
  - 命令变更

**预估工作量**: 0.5 天

---

#### O-17: 缺少性能基准测试

**现状**: `scripts/benchmark_large_scale.py` 存在，但没有集成到 CI 中，也没有标准基准结果。

**建议**:
- 定义标准基准数据集（100K / 1M / 10M 行）
- 在 CI 中定期运行基准测试（非每次提交）
- 记录性能基线，检测性能回归

**预估工作量**: 1 天

---

#### O-18: 缺少错误恢复指南

**现状**: 虽然有 `shared/error_diagnostics/` 目录（推测存在 error_patterns.md），但没有面向用户的错误恢复指南。

**建议**:
- 创建 `docs/troubleshooting.md`（如果不存在）或扩展现有内容
- 覆盖常见错误场景：
  - 依赖缺失（dask、harmonypy、pyradiomics）
  - 数据格式不兼容
  - 内存溢出（大数据集处理）
  - 质量门闸失败后的恢复步骤

**预估工作量**: 1 天

---

#### O-19: 缺少贡献者指南的实操性

**现状**: `CONTRIBUTING.md` 存在但内容可能偏理论。

**建议**:
- 确保 CONTRIBUTING.md 包含：
  - 开发环境搭建步骤
  - 测试运行方法
  - PR 流程
  - 代码风格要求（ruff 配置）
  - 新增模板的规范

**预估工作量**: 0.5 天

---

#### O-20: 缺少统计方法的自动选择建议

**现状**: analysis-plan SKILL.md 中有方法选择的指导，但没有基于数据特征的自动推荐机制。

**建议**:
- 创建 `shared/templates/method_recommender.py`：
  - 输入：数据特征（样本量、变量类型、分布特征、研究设计）
  - 输出：推荐的统计方法列表 + 理由
  - 基于 decision tree 逻辑（类似 stat-method-selector）

**预估工作量**: 2-3 天

---

#### O-21: 缺少报告模板的版本控制

**现状**: 期刊模板（`shared/journal-templates/*.json`）没有版本号，修改后无法追溯。

**建议**:
- 在每个 JSON 模板中添加 `version` 和 `last_updated` 字段
- 创建 `shared/journal-templates/CHANGELOG.md` 记录模板变更

**预估工作量**: 0.5 天

---

#### O-22: 缺少安全审计

**现状**: 虽然有 `SECURITY.md`，但没有定期的安全审计机制。依赖项中包含多个数据处理库，可能存在已知漏洞。

**建议**:
- 在 CI 中集成 `pip-audit`（已在 dev 依赖中）
- 定期运行 `pip-audit` 并记录结果
- 对用户数据处理路径进行安全审查

**预估工作量**: 0.5 天

---

#### O-23: 缺少端到端集成测试的覆盖

**现状**: `tests/e2e/` 有 53 个测试覆盖 10 个场景，但主要覆盖 cross_domain 模块。核心流水线（data-prep → analysis-plan → analysis-exec → report）缺少完整的端到端测试。

**建议**:
- 创建 `tests/e2e/test_full_pipeline.py`：
  - 场景 1：RCT 数据 → 完整分析 → 报告生成
  - 场景 2：观察性数据 → PSM 分析 → 报告生成
  - 场景 3：生存数据 → Cox 分析 → 报告生成
  - 场景 4：诊断数据 → ROC 分析 → 报告生成
- 使用标准演示数据集

**预估工作量**: 3-5 天

---

## 三、与 OPTIMIZATION_PLAN.md 的交叉比对

OPTIMIZATION_PLAN.md 中规划的 8 项优化，当前实施状态：

| 优化项 | 状态 | 说明 |
|--------|------|------|
| #1 数据画像 | ✅ 已实施 | `data_profile_template.py` 已创建，passport 中已注册 |
| #2 文献种子 | ✅ 已实施 | `lit_seeding_guide.md` 已创建，passport 中已注册 |
| #3 变量 DAG | ✅ 已实施 | `variable_dag_template.py` 已创建 |
| #4 Enhanced Handoff | ⚠️ 部分实施 | `generate_msra_handoff_bundle.py` 存在，但缺少 key_findings/safety_findings/limitations/methods 的提取函数 |
| #5 结果解读会话 | ✅ 已实施 | Stage 3.7 已定义，`interpretation_priorities` 已注册到 passport |
| #6 期刊定制评审 | ⚠️ 部分实施 | journal-template JSON 存在，但 `review_profile` 字段是否已添加需验证 |
| #7 SAP Amendment | ✅ 已实施 | `sap_amendment` 已注册到 passport，SAP 修正上限已定义 |
| #8 多中心支持 | ✅ 已实施 | `multicenter_template.py` 已创建，passport 中已注册 |

**未覆盖的优化点**（OPTIMIZATION_PLAN 之外）:
- 测试覆盖（O-01）
- SKILL.md 瘦身（O-02）
- TemplateManager 注册（O-03）
- CLI 入口点（O-05）
- 依赖锁定（O-07）
- 环境验证（O-08）
- 可重复性验证（O-12）
- 端到端测试（O-23）

---

## 四、建议实施路线图

### Sprint 1（v1.0.1 — 1 周）
- O-03: TemplateManager 注册补全
- O-06: CHANGELOG 自动化
- O-07: 依赖版本锁定
- O-08: 环境验证命令
- O-09: Gate 检查项数量统一
- O-16: 版本迁移指南

### Sprint 2（v1.1.0 — 2 周）
- O-01: 核心模板单元测试
- O-02: SKILL.md 瘦身
- O-05: CLI 入口点激活
- O-10: exploratory-causal → analysis-plan 衔接
- O-11: 数据脱敏工具

### Sprint 3（v1.2.0 — 3 周）
- O-04: R 模板补齐
- O-12: 可重复性验证
- O-20: 统计方法自动推荐
- O-23: 端到端集成测试

### Sprint 4（v2.0.0 — 长期）
- O-13: Web Dashboard
- O-14: 插件市场发布
- O-15: 国际化支持

---

## 五、结论

MSRA v1.0.0 的架构设计和功能覆盖已经非常扎实。主要的优化空间集中在 **测试覆盖**、**模板管理完整性**、**开发工具链** 三个方面，而非功能缺失。建议按上述路线图逐步实施，每个 Sprint 都有明确的交付物和验收标准。

---

*报告生成于 2026-06-24，基于 MSRA v1.0.0 代码库全面审查。*
