# Integration Guide

> 完整 pipeline 使用示例
> 适用: 全部审稿人 | v0.9.0

---

## 1. 上下游关系总览

```
systematic-survey --> report(论文模式) --> [完整性检查] --> peer-review
      (研究)             (写作)              (审查)          (评审)

peer-review --> report(修订模式) --> peer-review(re-review) --> [最终验证]
    (评审)          (修订)                (复审)                  (验证)
```

### 集成方式

| 集成方向 | 说明 |
|---------|------|
| report -> peer-review | 接收 report 完整论文输出，直接进入 Phase 1 |
| pipeline -> peer-review | Pipeline Stage 5.4 调度本 skill 进行评审 |
| peer-review -> report | 修订路线图格式可直接作为 report (revision mode) 输入 |
| peer-review (re-review) -> final | 复审完成后，进入最终完整性验证 |

---

## 2. 完整流程示例

### 示例 1: 首次投稿前评审

```
Step 1: 论文输入
  用户: "审稿这篇论文：[粘贴论文内容]"
  系统: 自动识别研究类型 (如 RCT)

Step 2: 审稿人配备 (Phase 1)
  系统: 生成 5 位审稿人配置卡
  用户: [确认/调整审稿人配置]

Step 3: 独立评审 (Phase 2)
  系统: 5 位审稿人并行评审
  ├── 主编: 评估学术价值、创新性
  ├── 方法学: 评估研究设计、偏倚风险
  ├── 临床专家: 评估临床意义、外部效度
  ├── 统计审稿人: 评估统计方法正确性
  └── 伦理审查员: 评估伦理合规性

Step 4: 编辑决定 (Phase 3)
  系统: 综合 5 份报告
  ├── 识别共识项 vs 分歧项
  ├── 争议问题仲裁
  ├── 生成编辑决定 (如 Major Revision)
  └── 生成修订路线图
```

### 示例 2: 修改稿复审

```
Step 1: 复审输入
  用户: "复审这篇修改稿：[论文 + 审稿意见 + 作者回复]"

Step 2: 逐条验证
  系统: 加载修订验证矩阵
  ├── 逐条核对每个问题的回应
  ├── 验证修改稿中的具体位置
  ├── 评估修改是否充分
  └── 记录残留问题

Step 3: 复审决定
  系统: 生成复审报告
  ├── 修订验证矩阵 (完整)
  ├── 残留问题清单
  └── 新编辑决定 (如 Accept / Minor Revision)
```

### 示例 3: 报告规范专项检查

```
Step 1: 触发
  用户: "检查这篇 RCT 的 CONSORT 合规性"

Step 2: 清单加载
  系统: 识别研究类型 → RCT
  系统: 加载 CONSORT 2025 清单

Step 3: 逐项检查
  系统: 按 CONSORT 清单逐项评估
  ├── 流程图: 是否提供
  ├── 随机化: 描述是否充分
  ├── 盲法: 设置是否合理
  ├── ITT: 是否遵守
  └── ... (全部清单项)

Step 4: 输出
  系统: 生成 CONSORT 合规性报告
```

---

## 3. 与其他 Skill 的协作

### report (论文写作模式)

| 协作点 | 说明 |
|--------|------|
| 输入 | report 输出的完整论文 → peer-review Phase 1 |
| 输出 | peer-review 修订路线图 → report revision mode |
| 格式 | 修订路线图格式兼容 report revision 输入要求 |

### systematic-survey

| 协作点 | 说明 |
|--------|------|
| 输入 | systematic-survey 输出的文献综述 → 论文的背景部分 |
| 评审 | peer-review 检查文献检索的完整性 |

### pipeline

| 协作点 | 说明 |
|--------|------|
| 调度 | Pipeline Stage 5.4 自动调度 peer-review |
| 数据 | Pipeline Stage 1-4 的分析结果 → 论文的方法/结果部分 |
| 质量 | peer-review 质量评估反馈给 pipeline |

---

## 4. 最佳实践

### 投稿前评审

| 建议 | 说明 |
|------|------|
| 使用 full 模式 | 首次投稿前建议完整评审 |
| 关注报告规范 | 确保对应研究类型的清单项完成 > 80% |
| 统计独立审查 | 统计审稿人和临床专家独立评估 |
| 伦理完整性 | 确保 IRB + 知情同意 + 利益冲突三项齐全 |

### 修改后复审

| 建议 | 说明 |
|------|------|
| 使用 re-review 模式 | 专门验证修改稿的充分性 |
| 提供作者回复 | 逐条回复信可加速验证 |
| 逐条验证 | 不可跳过任何原始问题 |

### 快速质量评估

| 建议 | 说明 |
|------|------|
| 使用 quick 模式 | 15 分钟快速评估 |
| 关注 Top-5 问题 | 聚焦最关键的问题 |
| 作为初筛工具 | 评估是否需要完整评审 |

---

## 5. 输出文件管理

| 输出文件 | 格式 | 保存位置 |
|----------|------|---------|
| 审稿人配置卡 | Markdown | `peer_review_output/reviewer_config.md` |
| 审稿报告 (x5) | Markdown | `peer_review_output/reviewer_reports.md` |
| 编辑决定信 | Markdown | `peer_review_output/editorial_decision.md` |
| 修订路线图 | Markdown | `peer_review_output/revision_roadmap.md` |
| 复审验证矩阵 | Markdown | `peer_review_output/re_review_matrix.md` |

---

## 引用

- SKILL.md 完整定义: `skills/peer-review/SKILL.md`
- Pipeline Stage 5.4: `skills/pipeline/SKILL.md`
- Report 论文写作模式: `skills/report/SKILL.md`
- Systematic Survey: `skills/systematic-survey/SKILL.md`
