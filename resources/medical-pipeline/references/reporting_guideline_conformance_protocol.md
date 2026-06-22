---
protocol: reporting_guideline_conformance
version: "1.0"
domain: Medical Research
license: CC-BY-NC-SA-4.0
---

# 报告规范符合性协议

**Status**: v1.0 (introduced 2026-06-22)
**Purpose**: 确保统计报告和论文符合国际报告规范（CONSORT/STROBE/PRISMA 等）。

---

## 1. 报告规范选择

### 1.1 研究类型 → 报告规范映射

| 研究类型 | 主要规范 | 补充规范 |
|---------|---------|---------|
| RCT | CONSORT 2025 | SPIRIT（方案）|
| 队列研究 | STROBE | — |
| 病例对照 | STROBE | — |
| 横断面 | STROBE | — |
| 系统综述 | PRISMA 2020 | PRISMA-S（检索）|
| 诊断准确性 | STARD | — |
| 预测模型 | TRIPOD | — |
| 病例报告 | CARE | — |
| 动物实验 | ARRIVE | — |
| 经济评估 | CHEERS | — |
| 质性研究 | COREQ | — |
| AI/ML 诊断 | TRIPOD+AI | — |
| LLM 应用 | TRIPOD-LLM | — |

### 1.2 规范版本验证
- 使用最新版本的报告规范
- 注明规范的发表年份和 PMC ID
- 如果使用旧版本，说明原因

## 2. 条目完整性检查

### 2.1 检查流程
1. 根据研究类型选择对应的检查清单
2. 逐条检查论文是否满足每个条目
3. 标记满足/部分满足/不满足/不适用
4. 生成合规性报告

### 2.2 合规性等级
- **完全合规**: 所有适用条目均满足
- **基本合规**: ≥90% 条目满足，无 CRITICAL 缺失
- **部分合规**: 70-89% 条目满足
- **不合规**: <70% 条目满足

## 3. 流程图规范

### 3.1 CONSORT 流程图
- 受试者筛选、入组、随机化、随访、分析
- 每个阶段的受试者数量
- 排除原因分类

### 3.2 PRISMA 流程图
- 识别、筛选、资格评估、纳入
- 每个阶段的文献数量
- 排除原因分类

## 4. 检查清单集成

### 4.1 自动化检查
- `shared/reporting-guidelines/` 目录下的检查清单
- `shared/reporting-guidelines/statcheck_patterns.py` 统计结果检查
- 合规性报告自动生成

### 4.2 人工审核
- 方法学审稿人审核报告规范符合性
- 临床专家审核临床相关内容的完整性
- 统计审稿人审核统计报告的准确性
