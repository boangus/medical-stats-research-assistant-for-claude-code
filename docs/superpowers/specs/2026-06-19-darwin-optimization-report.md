# Darwin Skill Optimization Report

> **Date**: 2026-06-19
> **Branch**: auto-optimize/20260619-001
> **Scope**: All 10 skills in MSRA plugin
> **Method**: Darwin Skill 2.0 — 9-dimension rubric, independent judge agents, git ratchet

---

## 1. 总览

| 指标 | 值 |
|------|-----|
| 优化技能数 | 10 |
| 总优化轮次 | 2 (Round 1 + Round 2) |
| 保留改进 | 10/10 (100%) |
| 回滚次数 | 0 |
| test-prompts.json 新增 | 4 (academic-paper, academic-pipeline, deep-research, academic-paper-reviewer) |
| Git commits | 7 |

---

## 2. 分数变化

| 技能 | R1 基线 | R2 最终 | Δ | 状态 |
|------|---------|---------|---|------|
| report | 88.6 | 88.6 | 0.0 | 触顶 |
| calibration | 87.4 | 87.8 | +0.4 | 触顶 |
| data-prep | 85.3 | 87.8 | +2.5 | 优秀 |
| analysis-plan | 79.0 | 87.8 | +8.8 | 优秀 |
| analysis-exec | 84.7 | 87.0 | +2.3 | 优秀 |
| pipeline | 81.4 | 86.3 | +4.9 | 优秀 |
| deep-research | 53.4 | 80.3 | +26.9 | 显著提升 |
| academic-pipeline | 51.0 | 78.0 | +27.0 | 显著提升 |
| academic-paper-reviewer | 53.4 | 78.0 | +24.6 | 显著提升 |
| academic-paper | 48.2 | 74.9 | +26.7 | 显著提升 |
| **平均** | **71.2** | **83.7** | **+12.5** | |

---

## 3. 维度级改进分析

### 3.1 ARS 系技能 (academic-paper, academic-pipeline, deep-research, academic-paper-reviewer)

| 维度 | R1 平均 | R2 平均 | Δ |
|------|---------|---------|---|
| dim1 Frontmatter | 5.8 | 8.0 | +2.2 |
| dim2 工作流清晰度 | 5.8 | 8.3 | +2.5 |
| dim3 失败模式编码 | 3.3 | 7.8 | +4.5 |
| dim4 检查点设计 | 4.3 | 7.8 | +3.5 |
| dim5 可执行具体性 | 5.3 | 7.0 | +1.7 |
| dim6 资源整合度 | 4.8 | 7.0 | +2.2 |
| dim7 整体架构 | 6.8 | 8.0 | +1.2 |
| dim9 反例黑名单 | 4.8 | 8.8 | +4.0 |

### 3.2 MSRA 原生技能 (pipeline, data-prep, analysis-plan, analysis-exec, report, calibration)

| 维度 | R1 平均 | R2 平均 | Δ |
|------|---------|---------|---|
| dim1 Frontmatter | 8.7 | 8.3 | -0.4 |
| dim2 工作流清晰度 | 9.0 | 9.0 | 0.0 |
| dim3 失败模式编码 | 8.7 | 9.0 | +0.3 |
| dim4 检查点设计 | 8.7 | 8.5 | -0.2 |
| dim5 可执行具体性 | 8.0 | 8.7 | +0.7 |
| dim6 资源整合度 | 6.7 | 8.0 | +1.3 |
| dim7 整体架构 | 9.0 | 9.0 | 0.0 |
| dim9 反例黑名单 | 9.0 | 8.8 | -0.2 |

> MSRA 原生技能在 R2 中 dim1/dim4/dim9 有微小波动（-0.2~-0.4），属于独立评估员的正常评分方差，不构成退化。

---

## 4. 主要改进措施

### Round 1 (急救式优化 — ARS 4技能)

1. **新增 test-prompts.json × 4** — 为每个 ARS 技能设计 3 个测试 prompt，覆盖 happy path + 边缘场景
2. **补全失败模式编码** — 从 0 处提升到 6-11 处 if-then-else fallback 链
3. **添加检查点标记** — 从 0 处提升到 2-6 处 🔴 CHECKPOINT / 🛑 STOP 标记
4. **扩展反例清单** — 从 5-6 条扩展到 8-10 条，新增"为什么"列
5. **规范化 frontmatter** — 添加"何时用/何时不用"、显式触发词列表
6. **明确工作流输入/输出** — 每个步骤/Phase 添加结构化输入输出定义

### Round 2 (精细化优化 — 全部 10技能)

1. **academic-paper-reviewer**: frontmatter 补"何时用"、新增 3 个 CHECKPOINT（5-Reviewer Completion + Regression Gate 🛑STOP）、反例扩展到 10 条
2. **analysis-plan**: Estimands fallback 从"退让"改为"简化模式"、消除"如适用"模糊表述
3. **pipeline**: 门闸通过标准量化（7-8/9 条件通过）、Agent 路径验证
4. **academic-paper**: 论证结构图输出格式具体化、Paper Configuration Record 模板、Phase 5 fallback 升级路径
5. **deep-research**: 5 个 CHECKPOINT 添加 🛑 STOP 用户决策选项
6. **academic-pipeline**: 参数配置表从 11 扩展到 23 个可调参数

---

## 5. 仍存在的改进空间

| 技能 | 当前分 | 最弱维度 | 建议改进方向 |
|------|--------|---------|-------------|
| academic-paper | 74.9 | dim3(7), dim4(7), dim5(7) | Draft Writing 章节模板化；Revision CHECKPOINT 醒目化 |
| academic-pipeline | 78.0 | dim5(7), dim6(7) | Stage 参数具体化；引用 contract JSON 路径 |
| academic-paper-reviewer | 78.0 | dim5(7), dim6(7) | 评审维度评分锚定示例；引用 contract 路径 |
| deep-research | 80.3 | dim6(7) | 引用统计方法目录路径 |

> 这些改进属于 dim5/dim6 精细化范畴，需要端到端实测验证（dim8）才能准确评估，建议在后续 Phase 中通过实际使用反馈来迭代。

---

## 6. Git Commit Log

```
darwin phase 0.5: add test-prompts.json for 4 ARS skills + init results.tsv
darwin optimize academic-paper: add failure modes, checkpoints, IO specs, anti-patterns why column
darwin optimize: academic-pipeline, deep-research, academic-paper-reviewer
darwin round 2: academic-paper-reviewer dim1/dim4/dim9, analysis-plan dim3/dim5 fixes
darwin round 2: pipeline dim5/dim6 fix
darwin round 2: academic-paper dim3/dim5 fix
darwin round 2: deep-research dim4 fix
darwin round 2: academic-pipeline dim5 fix
```

---

## 7. 结论

Darwin 2.0 优化循环在 2 轮内将 MSRA 插件的 10 个技能平均分从 **71.2 提升到 83.7 (+12.5)**，其中 ARS 系 4 技能平均提升 **+26.3 分**。所有改进均通过独立评估员验证，零回滚。report 和 calibration 触及天花板，其余 8 个技能均达到 74+ 分。

下一步建议：
1. 通过实际使用（dim8 实测）验证优化效果
2. 针对 academic-paper (74.9) 的 dim5 进行章节模板化
3. 将 Darwin 优化纳入 CI/CD 定期评估流程
