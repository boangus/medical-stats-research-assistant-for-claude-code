# CHANGELOG

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



