# Changelog

> MSRA Peer Review 完整版本历史
> 适用: 全部审稿人 | v0.9.0

---

## v0.9.2 (2026-06-22)

### 变更

- **文档更新**: 同步 documentation 到实际项目状态
- **引用修复**: 修正测试断言匹配实际报告结构
- **CI 修复**: 补充门闸结果修复 Stage 3 前置条件测试

### 修复

- 修正测试方法名 `get_consistency_report` → `generate_consistency_report`

---

## v0.9.0 (2026-06-21)

### 新增

- **完整 skill 定义**: 从 `peer-review v1.10.0` 迁移并重构
- **5 位审稿人体系**: 主编 + 方法学审稿人 + 临床专家 + 统计审稿人 + 伦理审查员
- **6 种操作模式**: full / quick / methodology-focus / re-review / guideline / ethics
- **3 阶段工作流**: Phase 1 (论文接收) → Phase 2 (独立评审) → Phase 3 (综合决定)
- **7 个检查点**: CP0-CP6 完整质量门闸
- **7 个报告规范清单**: CONSORT 2025 / STROBE / PRISMA 2020 / STARD 2015 / TRIPOD+AI / CARE / ICMJE
- **10 个失败模式**: 完整故障处理与兜底方案
- **10 个反模式**: 常见错误与正确做法对照

### 参考文件

- `references/review_criteria_framework.md` — 按论文类型区分的结构化评审标准
- `references/icmje_recommendations.md` — ICMJE 推荐标准速查
- `references/editorial_decision_standards.md` — Accept/Minor/Major/Reject 判定标准
- `references/statistical_review_standards.md` — 统计审查标准
- `references/ethics_review_standards.md` — 伦理审查标准
- `references/guideline_mapping.md` — 研究类型与报告规范映射表
- `references/re_review_mode_protocol.md` — 复审验证逻辑
- `references/integration_guide.md` — 完整 pipeline 使用示例
- `references/changelog.md` — 版本历史 (本文件)

### 模板

- `templates/peer_review_report_template.md` — 审稿报告模板
- `templates/editorial_decision_template.md` — 编辑决定信模板
- `templates/revision_response_template.md` — 作者回复模板
- `templates/guideline_checklist_template.md` — 报告规范检查模板

### Agent 文件

- `agents/field_analyst_agent.md` — 领域分析师
- `agents/eic_agent.md` — 主编
- `agents/methodology_reviewer_agent.md` — 方法学审稿人
- `agents/clinical_expert_agent.md` — 临床专家
- `agents/statistical_reviewer_agent.md` — 统计审稿人
- `agents/ethics_reviewer_agent.md` — 伦理审查员
- `agents/editorial_synthesizer_agent.md` — 编辑综合者

### 集成

- 上游: 接收 `report` (论文写作模式) 和 `pipeline` Stage 5.4 的输出
- 下游: 修订路线图输出兼容 `report` (revision mode)
- 共享资源: `shared/reporting-guidelines/`, `shared/risk-of-bias/`, `shared/statistics-methods/`

---

## v1.10.0 (已弃用)

> 此版本已被 v0.9.0 完全取代。

### 原始特性

- 基础审稿流程
- 简化的审稿人配置
- 基本报告格式

---

## 版本说明

| 版本号 | 状态 | 说明 |
|--------|------|------|
| v0.9.2 | **当前** | 文档同步与 CI 修复 |
| v0.9.0 | 稳定 | 完整 skill 定义与参考文件 |
| v1.10.0 | 已弃用 | 被 v0.9.0 完全取代 |

---

## 引用

- SKILL.md: `skills/peer-review/SKILL.md`
- 共享资源: `shared/`
