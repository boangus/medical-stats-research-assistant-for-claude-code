# CLAIM AI 医学影像报告规范

> **CLAIM**: Checklist for Artificial Intelligence in Medical Imaging
> 适用于 AI 在医学影像中的研究报告
> 参考: Mongan J, et al. (2020) Radiology
> 更新日期: 2026-06-24

---

## Title and Abstract

### Item 1. 标题
- [ ] 标题中标识 AI/ML 方法和影像模态

### Item 2. 摘要
- [ ] 包含 AI 方法、数据集、主要性能指标

## Introduction

### Item 3. 研究背景
- [ ] AI 在该临床场景中的应用背景
- [ ] 与现有方法的比较

## Methods

### Item 4. 研究设计
- [ ] 回顾性/前瞻性设计
- [ ] 验证策略

### Item 5. 数据集 🆕 **CLAIM**
- [ ] **数据来源**:
  - [ ] 数据库/机构名称
  - [ ] 数据采集时间范围
  - [ ] 样本量确定依据
- [ ] **纳入/排除标准**
- [ ] **数据划分**:
  - [ ] 训练集/验证集/测试集比例
  - [ ] 划分方法（随机/时间/机构分层）

### Item 6. 标注 🆕 **CLAIM**
- [ ] **参考标准**:
  - [ ] 金标准类型（病理/随访/专家共识）
  - [ ] 标注者数量和资质
- [ ] **标注过程**:
  - [ ] 标注工具
  - [ ] 标注一致性评估（ICC/Kappa）
  - [ ] 争议解决机制

### Item 7. 预处理
- [ ] 影像预处理步骤
- [ ] 数据增强方法

### Item 8. 模型 🆕 **CLAIM**
- [ ] **模型架构**:
  - [ ] 模型类型（CNN/ViT/GAN 等）
  - [ ] 架构细节（层数、参数量）
  - [ ] 预训练权重（如有）
- [ ] **训练细节**:
  - [ ] 损失函数
  - [ ] 优化器和学习率
  - [ ] 训练轮次和早停策略
  - [ ] 超参数搜索方法
- [ ] **代码可用性**:
  - [ ] 代码仓库链接
  - [ ] 环境依赖

### Item 9. 评估 🆕 **CLAIM**
- [ ] **性能指标**:
  - [ ] 主要指标（AUC/Accuracy/F1/Dice 等）
  - [ ] 次要指标
  - [ ] 置信区间
- [ ] **统计检验**:
  - [ ] 与基准方法的比较检验
  - [ ] 多重比较校正
- [ ] **亚组分析**:
  - [ ] 按设备/机构/患者特征分层
  - [ ] 公平性评估

## Results

### Item 10. 数据集特征
- [ ] 训练/验证/测试集的患者特征
- [ ] 标签分布

### Item 11. 性能
- [ ] 主要性能指标和 CI
- [ ] 混淆矩阵
- [ ] ROC/PR 曲线

### Item 12. 可解释性
- [ ] 注意力图/Grad-CAM
- [ ] 特征重要性
- [ ] 失败案例分析

## Discussion

### Item 13. 局限性
- [ ] 数据偏倚
- [ ] 外部验证缺失
- [ ] 临床适用性限制

### Item 14. 临床影响
- [ ] 对临床工作流的影响
- [ ] 与人类专家的比较

## 参考文献

1. Mongan J, Moy L, Kahn CE Jr. Checklist for Artificial Intelligence in Medical Imaging (CLAIM): A Guide for Authors and Reviewers. Radiol Artif Intell. 2020;2(2):e200029.
