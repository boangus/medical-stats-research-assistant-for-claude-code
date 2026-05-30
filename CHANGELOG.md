# CHANGELOG

## [0.6.0] — 2026-05-30

### Added
- **SAP 标准化与验证机制**：`shared/sap/sap_standard.md` 定义标准格式，`validate_sap.py` 自动验证
- **变量选择与方法推荐指南**：`shared/sap/variable_selection_guide.md`（基线筛选原则、方法选择决策树、变量构建公式）
- **观察性研究高级方法集成**（Phase 6.1）：IPTW、双重稳健估计(AIPW)、限制性立方样条(RCS)、E-value、亚组分析
- **错误诊断知识库**：`shared/error-diagnostics/`（错误模式分类、自动修复建议）
- **假设检验自动化**（Phase 7）：预检验检查、自动化流程、报告模板
- **SAP 一致性检查器**：比较 SAP 预设方法与数据特征，检测不匹配
- **报告模板扩展**：新增 AIM、CMJ_v2、CJE 期刊模板（共 7 个）
- **报告规范扩展**：新增 TRIPOD+AI、CARE、REMARK、ARRIVE、**CONSORT**、**STROBE** 检查清单（共 6 个）
- **图表样式库**：期刊配色方案、图表类型规范、字体尺寸规范
- **方法学描述模板**：自动生成描述性统计、推断性统计、敏感性分析方法段落
- **SAP 到方法学描述转换**：`shared/sap/sap_to_methods.py` 自动从 SAP 生成方法学描述
- **可重复性验证**：pipeline auditor、3 次重跑验证、复现报告生成
- **存档包生成器**：产物收集、清单生成、完整性验证
- **数据共享**：去标识化、代码包、结果包生成
- **度量校准框架**：金标准对比、准确率报告（实验性功能）
- **观察性研究方法参考文档**：`shared/statistics-methods/observational-study-methods.md`

### Changed
- **流程精简优化**：
  - MANDATORY 检查点 6→4，SLIM 检查点 4→1，ADAPTIVE 检查点 5→3
  - 高效模式暂停次数 8→4（减半）
  - 交互模式 3→2（移除极速模式，与高效模式合并）
- **analysis-plan**：合并 Phase 2+3（Estimands + 方法选择 + 参数确认合并为单一确认点），参数使用默认值
- **analysis-exec**：合并 Phase 1+2、Phase 3-5、Phase 7-9，唯一 MANDATORY 确认点为 Phase 6 完成后
- **analysis-exec**：新增 Phase 6.1（观察性研究高级方法，SAP 参数直接使用）
- **analysis-exec**：新增反模式 #21-25（观察性研究因果推断禁忌）
- **analysis-plan**：Phase 3 新增观察性研究高级方法选择章节
- **version**: 0.5.0 → 0.6.0
- **目录结构优化**：
  - 合并 `statistical-methods/` → `statistics-methods/`（消除命名混淆）
  - 合并 SAP 三目录 → `shared/sap/`（consistency + standardization + to_methods）
  - 移动 `checklists/` → `reporting-guidelines/`
  - 移动 `collaboration/` → `statistics-methods/`

### Fixed
- 路径引用修正：`shared/methods/` → `shared/statistics-methods/`（10+ 处）
- `code_executor_agent.md` 标记 DEPRECATED（已被 exec_runner + exec_inference 替代）
- Stage 3.5 检查项数统一为 8 项

### Removed
- `agents/code_executor_agent.md`（DEPRECATED，功能已拆分）
- `docs/optimization-roadmap.md`（已完成的路线图）
- `shared/templates/survival_analysis_template.R`（保留 ggsurvfit 版，删除 survminer 版）
- `tests/healthcare_dataset.csv` 从 git 跟踪中移除（8.4MB，已在 .gitignore）
- `.msra/results.tsv` 从 git 跟踪中移除

---

## [0.5.0] — 2026-05-29

### Added
- 反幻觉机制（IRON RULE + Anti-Pattern）：嵌入各 SKILL，防止模型在长流水线中漂移
- 医学统计反模式目录：`shared/anti-patterns/medical_stats_anti_patterns.md`
- exec-inference Agent：从 analysis-exec 拆出的独立推断/质检角色
- Passport 版本兼容检查：`passport_schema_version` 字段 + 加载时版本校验
- **PATTERN PROTECTION**（G6）：exec-runner 7 条 + exec-inference 7 条靶向性加固规则
- **Gold Evaluation Set**（G9）：21 个结构化黄金评估元组，覆盖所有数据坑
- **Collaboration Depth Rubric**（G13）：轻量版协作深度评估框架，嵌入 MANDATORY Checkpoint

### Changed
- `analysis-exec/SKILL.md`：重构为双 Agent 编排（exec-runner + exec-inference），第 0-6 阶段与第 7-9 阶段明确隔离
- `pipeline/SKILL.md`：§6 Agent Dispatch 更新，添加 exec-runner/exec-inference 引用
- `passport.py`：`_load_or_create()` 增加版本兼容性检查
- `agents/exec_runner_agent.md`：添加 PATTERN PROTECTION 节（P1-P7）
- `agents/exec_inference_agent.md`：添加 PATTERN PROTECTION 节（P1-P7）

---

## [0.4.0] — 2026-05-29

### 流水线架构定型
- 4 个核心 SKILL：pipeline / data-prep / analysis-plan / analysis-exec / report
- 4 个 Agent：Data Validator / Method Consultant / Code Executor / QC Inspector
- 3 个阻断式质量门闸（Stage 1.5/2.5/3.5）
- 三级 Checkpoint 机制（MANDATORY / SLIM / ADAPTIVE）
- 三种交互模式（详细引导 / 高效 / 极速）

### 新增功能
- Material Passport 跨阶段产物追踪（`shared/passport/passport.py`）
- 值规范化模块（TCM 术语 + 数值格式变体，`shared/value-normalization/`）
- 统计方法指南 41 章（`shared/methods/`）
- 12 种方法降级决策树（`shared/statistics-methods/methods_catalog.md`）
- 16 个代码模板（R + Python）
- 5 个期刊输出模板（NEJM / JAMA / Lancet / BMJ / CMJ）
- 6 个研究类型分支（RCT / 观察性 / 诊断试验）
- 21 个数据"坑"测试集
- 收敛检测与回退循环控制

### 技术基础设施
- 多 Agent 架构（`agents/AGENTS.md` + `agents/protocol.md` + 4 个 Agent 定义文件）
- Material Passport 持久化
- GitHub Actions CI（smoke + lint）
- MIT License

---

## [0.3.0] — 2026-05-28

### 项目初始化
- 基础流水线框架
- 意图检测 + 研究类型识别
- `manifest.json` 注册 5 个 Slash Command
- 3 个阻断式质量门闸
- 基本反例与黑名单



