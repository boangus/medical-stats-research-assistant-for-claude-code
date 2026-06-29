# TRIPOD-LLM 报告规范检查清单

> 适用于**使用或开发大语言模型（LLM）**的临床预测/生成/推理研究
> 基于 **TRIPOD-LLM 声明**（Collins GS, et al., Nature Medicine 2024, PMC12104976）
> **19 项主条目 + 50 项子条目**，是 TRIPOD+AI (2024) 的 LLM 专用扩展
> 更新日期: 2026-06-14

> **与 TRIPOD+AI 的区别**:
> - **TRIPOD+AI** (27 项): 传统回归 + 通用机器学习预测模型（XGBoost、随机森林等）
> - **TRIPOD-LLM** (19+50 项): **LLM 专用**，补充提示工程、基础模型版本、上下文窗口、幻觉控制、人在回路、对齐方法等 LLM 特有问题
> - 当研究**使用或开发 LLM**（如 GPT、Claude、LLaMA、医领域专用 LLM）时，**必须用 TRIPOD-LLM 而非 TRIPOD+AI**

> **IRON RULES**:
> - 严格对齐官方 19 主项 + 50 子项编号
> - LLM 特有项以 **🆕 LLM** 标注（区别于 TRIPOD+AI 已有内容）
> - **基础模型版本、提示词、上下文窗口必须完整报告** — 这是 LLM 研究可复现性的核心
> - 参考: resources/anti-patterns/medical_stats_anti_patterns.md（E1/E2/E3 LLM 特有反模式）

---

## Title and Abstract

### Item 1. 标题
- [ ] 标题标识研究使用或开发了 LLM
- [ ] 标识研究类型（开发/验证/更新/评估）

### Item 2. 摘要
- [ ] 结构化摘要（背景/目的/方法/结果/结论）
- [ ] 🆕 **LLM** 报告所用的基础模型名称和版本（如 GPT-4-0613、Claude-3.5-Sonnet）
- [ ] 🆕 **LLM** 报告任务类型（分类/生成/抽取/推理/摘要）

## Introduction

### Item 3. 背景与原理
- [ ] 科学背景和临床问题
- [ ] 为何使用 LLM（vs 传统统计/ML 方法）的理由
- [ ] 🆕 **LLM** LLM 在该任务的预期优势和已知局限

### Item 4. 研究目的
- [ ] 明确研究目的（开发/验证/更新/比较）
- [ ] 明确目标人群和临床应用场景
- [ ] 🆕 **LLM** 明确 LLM 的预期用途（辅助决策/自动决策/信息提取）

## Methods

### Item 5. 数据来源
- [ ] 数据来源（单中心/多中心/EHR/公开数据集/众包）
- [ ] 数据收集时间范围
- [ ] 纳入/排除标准
- [ ] 参考标准的定义和判定方法（避免 LLM 评估循环引用）

### Item 6. 结局定义
- [ ] 主要结局定义和测量方法
- [ ] 结局的时间窗和评估时点
- [ ] 🆕 **LLM** 对 LLM 输出的人工判定协议（多人独立判定、一致性评估）

### Item 7. 模型架构与基础模型 🆕 **LLM**
- [ ] **基础模型名称、版本、参数规模**（如 LLaMA-3-70B、GPT-4o）
- [ ] **模型访问方式**（API/开源权重/本地部署）
- [ ] **是否微调**（fine-tuning/RAG/in-context learning/zero-shot），若是描述方法
- [ ] **对齐方法**（RLHF/DPO/无对齐），影响输出风格
- [ ] 训练数据来源（若微调，描述数据集和规模）

### Item 8. 提示工程 🆕 **LLM**
- [ ] **完整提示词模板**（系统提示+用户提示+少样本示例）须公开（附录或仓库）
- [ ] **上下文窗口大小**和实际使用长度
- [ ] **温度/采样参数**（temperature、top-p、max_tokens）
- [ ] **提示词稳定性评估**（同输入多次运行的输出方差）
- [ ] 提示词迭代和版本管理（迭代轮次、变更原因）

### Item 9. 评估协议 🆕 **LLM**
- [ ] **零样本/少样本/思维链**等推理策略的明确说明
- [ ] **人在回路**（human-in-the-loop）的角色和介入点
- [ ] **幻觉控制**策略（自洽性检查、引用验证、置信度阈值）
- [ ] **输出结构化**方法（JSON schema、函数调用、正则解析）
- [ ] **失败处理**：LLM 拒答/格式错误/超时时的回退策略

### Item 10. 性能评估
- [ ] 评估指标（按任务类型：分类用 AUC/F1，生成用 BLEU/ROUGE/专家评分）
- [ ] 🆕 **LLM** **校准评估**（预测置信度与实际准确率匹配，ECE）
- [ ] 🆕 **LLM** **公平性评估**（跨人口学亚组的性能差异）
- [ ] 与基线方法（传统统计/ML/人类专家）的对比
- [ ] 样本量计算或事后功效分析

### Item 11. 统计分析
- [ ] 性能指标的 95% 置信区间计算方法
- [ ] 模型比较的统计检验（DeLong、bootstrap）
- [ ] 🆕 **LLM** **LLM 输出方差**的统计建模（多次运行的不确定性量化）
- [ ] 亚组分析和敏感性分析

### Item 12. 验证策略
- [ ] 内部验证方法（交叉验证/bootstrap/hold-out）
- [ ] 外部验证数据集（若有）
- [ ] 🆕 **LLM** **时间外部验证**（基础模型升级后的性能变化，如 GPT-4 → GPT-4o）
- [ ] 🆕 **LLM** **提示词泛化性**（不同提示词表述下的性能稳定性）

## Open Science Practices

### Item 13. 代码与数据可用性
- [ ] 🆕 **LLM** **提示词和代码**的公开获取途径（GitHub/补充材料）
- [ ] 训练/评估数据集的可用性（含去标识化方法）
- [ ] 🆕 **LLM** **基础模型版本锁定**的复现指南（API 快照/本地权重哈希）
- [ ] 推断日志的保存（用于审计和错误分析）

### Item 14. 模型可用性
- [ ] 🆕 **LLM** **微调权重/RAG 索引**的获取途径（若适用）
- [ ] 推断 API 或部署指南
- [ ] 使用许可证和商业使用限制

## Results

### Item 15. 参与者和数据
- [ ] 数据集流程图（入组→分析）
- [ ] 基线特征（按亚组）
- [ ] 🆕 **LLM** **缺失/无效 LLM 输出**的数量和处理

### Item 16. 模型开发与调整
- [ ] 提示词最终版本和迭代历史
- [ ] 超参数最终值
- [ ] 🆕 **LLM** **token 使用量**和成本估算

### Item 17. 性能结果
- [ ] 主要性能指标（点估计 + 95%CI）
- [ ] 校准曲线和判别能力
- [ ] 🆕 **LLM** **多次运行的输出方差**（均值±SD 或全分布）
- [ ] 亚组性能差异
- [ ] 错误分析（典型失败案例和原因）

### Item 18. 模型比较
- [ ] 与基线/对照模型的对比表
- [ ] 与人类专家的对比（若有）
- [ ] 🆕 **LLM** **不同基础模型/版本的对比**（如 GPT-4 vs Claude vs LLaMA）

## Discussion

### Item 19. 解释与局限
- [ ] 主要发现的临床意义（vs 统计显著性）
- [ ] 🆕 **LLM** **LLM 特有局限**：幻觉风险、知识截止、提示词敏感性、不可解释性
- [ ] 🆕 **LLM** **伦理考量**：偏见放大、隐私泄漏（训练数据记忆）、责任归属
- [ ] 外部效度（不同医院/人群/基础模型版本的适用性）
- [ ] 与既往证据的一致性
- [ ] 注册和数据共享声明

---

## TRIPOD-LLM vs TRIPOD+AI 关键差异（速查）

| 维度 | TRIPOD+AI | TRIPOD-LLM 新增 |
|------|-----------|----------------|
| **模型架构** | 通用 ML 算法 | 基础模型+版本+访问方式+对齐方法 |
| **输入构造** | 特征工程 | **提示工程**（完整提示词+上下文窗口+温度） |
| **不确定性** | 模型方差 | **多次运行方差** + 幻觉风险 |
| **复现性** | 代码+数据 | + **提示词** + **基础模型版本锁定** + token 日志 |
| **评估** | AUC/校准 | + **置信度校准** + **公平性** + 跨版本稳定性 |
| **伦理** | 一般 | **偏见放大** + **训练数据记忆** + 责任归属 |

## 关键提示

1. **必须报告基础模型版本**：LLM 输出强依赖具体版本（GPT-4-0314 ≠ GPT-4-0613），不报告版本的研究无法复现
2. **提示词必须公开**：提示词是 LLM 研究的"超参数"，藏在论文中等于隐藏关键方法 — Item 8 + Item 13 强制要求
3. **多次运行方差必须报告**：LLM 在同输入下输出不确定，单次运行的指标无意义 — Item 11 + Item 17
4. **幻觉风险必须讨论**：LLM 可能编造参考文献/数字/患者信息，Item 9 须有控制策略，Item 19 须有限讨论
5. **使用 MSRA 辅助 LLM 研究**：若用户用 MSRA 做基于 LLM 的临床研究，report skill 应推荐 TRIPOD-LLM 而非 TRIPOD+AI
6. **资料来源**: Collins GS, et al. The TRIPOD-LLM reporting guideline for studies using large language models. Nat Med 2024. PMC12104976.

## 参考文献

1. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models. BMJ 2024;385:e078378.
2. Celi LA, Celli LA, Mjoli L, et al. The TRIPOD-LLM reporting guideline for studies using large language models. Nat Med 2024;30:2435-2444.
3. Roy PM, et al. TRIPOD-LLM for abstracts. (companion checklist for conference/journal abstracts)
4. EQUATOR Network TRIPOD-LLM record. https://www.equator-network.org/reporting-guidelines/the-tripod-llm-reporting-guideline-for-studies-using-large-language-models/
