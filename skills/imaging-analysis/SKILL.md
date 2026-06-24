---
version: "1.0.0"
name: MSRA Medical Imaging Analysis
description: |
  影像组学分析：DICOM/NIfTI/NRRD 加载、预处理、分割、特征提取、特征选择。
  输出: 特征矩阵 (CSV) + 质量门闸报告 + 可视化 + 分析报告。
  触发: 影像 / 放射组学 / radiomics / DICOM / NIfTI / 影像分割 / 特征提取 / 医学影像 /
  imaging / medical-imaging / feature-extraction / segmentation
data_access_level: raw
task_type: open-ended
depends_on: []
works_with: [pipeline, analysis-exec]
author: "MSRA Team"
license: "CC-BY-NC-SA-4.0"
min_claude_version: "3.5"
tags: [medical-imaging, radiomics, dicom, nifti, segmentation, feature-extraction, quality-gate]
---

# 医学影像分析 (Medical Imaging Analysis)

## 角色定义

你是一位医学影像分析专家，负责执行从影像数据中提取定量放射组学特征的标准化分析流程。
你**永远先检查数据质量**，获得用户确认后才执行重计算分析。

> **IRON RULES**:
> - 🔑 关键项门闸检查不通过时**必须阻断**，不可条件通过
> - 影像预处理参数**必须**在 Phase 0 由用户确认，不可使用静默默认值
> - 特征提取结果**必须**经过质量验证，禁止输出未检查的原始特征
> - Phase 2 子 Agent 任务**必须**可独立重跑，不依赖 Phase 1 的中间状态
> - 参考：shared/quality_gates/ 的门闸框架，执行 Gate IMG-1 阻断检查

## 架构集成图

```
┌─────────────────────────────────────────────────────────────┐
│                  Medical Imaging Analysis 架构                │
│                                                              │
│  输入                                                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │ DICOM 序列 │  │ NIfTI 文件 │  │ NRRD 文件  │              │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘               │
│        │              │              │                      │
│        ▼              ▼              ▼                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 0: 数据源选择 + 分析目标确认 + 参数配置 (M)   │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 1: 数据加载 → Gate IMG-1 → 预处理            │   │
│  │  ├─ DICOMLoader / load_nifti / load_nrrd 加载       │   │
│  │  ├─ Gate IMG-1 数据质量门闸 (4项)                    │   │
│  │  └─ ImagePreprocessor 预处理                         │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 2: 重计算 (BACKGROUND - 子 Agent 并行)        │   │
│  │  ├─ Task A: 影像分割 (SegmentationPipeline)         │   │
│  │  ├─ Task B: 特征提取 (RadiomicsExtractor)           │   │
│  │  └─ Task C: 特征选择 (FeatureSelector)              │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 3: 结果审查 → 用户确认 (M)                    │   │
│  │  ├─ 特征矩阵审查                                     │   │
│  │  ├─ ImagingVisualizer 可视化                         │   │
│  │  └─ 用户确认 / 请求调整参数重跑                       │   │
│  └─────────────────────┬───────────────────────────────┘   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 4: 独立报告 或 接入主 Pipeline Stage 3        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**架构设计原则**:
1. 数据质量门闸 (Phase 1) 必须先于重计算 (Phase 2)
2. Phase 2 的子 Agent 任务可独立重跑，不依赖 Phase 1 的中间状态
3. 质量门闸复用 shared/quality_gates/ 框架
4. 特征选择独立于特征提取，遵循单一职责原则

## 快速开始

### 1. 完整流程示例

```
用户: "/msra-imaging --dicom /path/to/dicom/"

执行路径（5 步）:
Phase 0: 确认数据源、分析模式、参数
Phase 1: 数据加载 → Gate IMG-1 → 预处理
Phase 2: 分割 + 特征提取 + 特征选择 (并行)
Phase 3: 结果审查 → 用户确认
Phase 4: 导出特征矩阵

预计交互次数: 3-5 次（Phase 0 配置 + Phase 1 门闸 + Phase 3 确认）
```

### 2. 仅特征提取模式

```
用户: "/msra-imaging --nifti scan.nii.gz --roi mask.nii.gz --mode radiomics"

执行路径:
Phase 0: 确认数据路径、特征提取参数
Phase 1: 数据加载 → Gate IMG-1
Phase 2: 直接特征提取 (跳过分割，使用已有 ROI)
Phase 3: 特征矩阵审查
Phase 4: 导出特征矩阵 CSV
```

### 3. 仅分割模式

```
用户: "/msra-imaging --nifti scan.nii.gz --mode segmentation"

执行路径:
Phase 0: 确认分割模型、参数
Phase 1: 数据加载 → Gate IMG-1
Phase 2: 仅执行分割 (MONAI 3D U-Net)
Phase 3: 分割结果可视化 → 用户确认
Phase 4: 导出分割掩码 NIfTI
```

### 执行时间估算

| 模式 | 数据规模 | 预计时间 | 瓶颈 |
|------|---------|---------|------|
| 数据加载+门闸 | 512×512×200 CT | 10-30 秒 | DICOM 序列读取 |
| 预处理 | 512×512×200 | 30-60 秒 | 重采样 + 去噪 |
| 分割 (MONAI) | 256×256×128 | 1-5 分钟 | GPU/CPU 推理 |
| 特征提取 | 50×50×50 ROI | 30-120 秒 | GLCM 计算 |
| 特征选择 | 100 特征 | <5 秒 | sklearn 计算 |
| 质量门闸 | — | <10 秒 | 4 项检查 |

### 运行时错误处理

| 错误场景 | 症状 | 解决方案 |
|---------|------|---------|
| SimpleITK 未安装 | ImportError | 提示安装: `pip install SimpleITK` |
| nibabel 未安装 | ImportError | 提示安装: `pip install nibabel` |
| MONAI 未安装 | ImportError | 提示安装: `pip install monai`，或降级为阈值分割 |
| DICOM 目录为空 | FileNotFoundError | 提示检查 DICOM 目录路径 |
| ROI 维度不匹配 | ValueError | 提示重新提供匹配的掩膜 |

## 工作流程

```
原始影像 (DICOM/NIfTI/NRRD)
  │
  ▼
Phase 0: 用户交互配置 [MANDATORY] → 输入:影像路径 → 输出:配置参数
  │ ├─ 数据源选择 (DICOM / NIfTI / NRRD)
  │ ├─ 分析目标确认 (radiomics / segmentation / full)
  │ ├─ 分割模型选择 (如需要)
  │ └─ 参数配置 (预处理参数、特征提取参数)
  ▼
Phase 1: 数据预处理 [ADAPTIVE] → 输入:配置 → 输出:预处理后影像 + Gate IMG-1 报告
  │ ├─ Step 1.1: DICOMLoader / load_nifti / load_nrrd 加载数据
  │ ├─ Step 1.2: ▶ Gate IMG-1 数据质量门闸 (4 项)
  │ │   ├─ [🔑] 文件可读性检查
  │ │   ├─ [🔑] 体素间距合理性 (0.5-5mm)
  │ │   ├─ [🔑] ROI 掩膜与影像维度匹配
  │ │   └─ [ ] 信噪比 + NaN/Inf 异常检查
  │ │   → ❌ 关键项不通过 → 阻断并提示修复方案
  │ └─ Step 1.3: ImagePreprocessor 预处理
  ▼
Phase 2: 重计算 [BACKGROUND] → 输入:预处理后影像 → 输出:分析结果
  │ ├─ Task A: 影像分割 (SegmentationPipeline)
  │ ├─ Task B: 特征提取 (RadiomicsExtractor)
  │ └─ Task C: 特征选择 (FeatureSelector)
  ▼
Phase 3: 结果审查 [MANDATORY] → 输入:分析结果 → 输出:用户确认
  │ ├─ 特征矩阵审查 (维度、缺失值、异常值)
  │ ├─ ImagingVisualizer 可视化
  │ └─ 用户确认 / 请求调整参数重跑
  ▼
Phase 4: 整合与报告 [ADAPTIVE] → 输入:用户确认 → 输出:报告 + CSV
  │ ├─ 选项 A: 独立报告 (imaging_analysis_report.md)
  │ └─ 选项 B: 接入主 Pipeline Stage 3 (imaging_features_v1.csv)
```

## 质量门闸

### Gate IMG-1 — 数据质量门闸 (4 项)

> 在 Phase 1 执行，阻断不合格数据进入分析流程。
> 实现: `msra_modules/medical_imaging/quality_gates.py` → `ImagingQualityGateChecker`

| # | 检查项 | 关键项 | 检查方法 | 通过标准 |
|---|--------|--------|---------|---------|
| 1 | 文件可读性 | 🔑 | 尝试加载 DICOM/NIfTI 文件 | 文件可成功读取 |
| 2 | 体素间距合理性 | 🔑 | 检查 spacing 值范围 | spacing ∈ [0.5, 5.0] mm |
| 3 | ROI 掩膜维度匹配 | 🔑 | 比较 image.shape 和 mask.shape | 维度完全一致 |
| 4 | 影像质量 | | SNR + NaN/Inf 检查 | SNR > 5，无 NaN/Inf |

**判定规则**:
- PASS: 4/4 通过
- CONDITIONAL: 2-3/4 通过且 🔑 全通过
- BLOCKED: ≤ 1/4 通过 或 🔑 任一未通过

## 命令

| 命令 | 说明 |
|------|------|
| `/msra-imaging` | 启动完整医学影像分析流程 |
| `/msra-imaging --dicom path` | 指定 DICOM 目录 |
| `/msra-imaging --nifti path` | 指定 NIfTI 文件 |
| `/msra-imaging --roi mask_path` | 指定 ROI 掩膜 |
| `/msra-imaging --mode radiomics` | 仅特征提取模式 |
| `/msra-imaging --mode segmentation` | 仅分割模式 |
| `/msra-imaging --mode full` | 完整流程（默认） |

## Mode

### full（默认）
完整流程：数据加载 → 门闸 → 预处理 → 分割 → 特征提取 → 特征选择 → 可视化 → 报告

### radiomics
仅特征提取模式：数据加载 → 门闸 → 特征提取 → 特征选择 → 报告（跳过分割，需提供 ROI）

### segmentation
仅分割模式：数据加载 → 门闸 → 分割 → 分割结果可视化 → 导出掩码

## 反例与黑名单

### 🚫 数据质量禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 1 | 跳过 Gate IMG-1 直接分析 | 残缺数据导致特征不可靠 | Phase 1 必须通过门闸检查 |
| 2 | 默认预处理参数不告知用户 | 不同数据需要不同参数 | Phase 0 必须确认预处理参数 |
| 3 | 静默跳过无法加载的文件 | 可能导致分析结果不完整 | 报告加载失败的文件 |

### 🚫 分析禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 4 | 特征提取时使用错误的掩膜维度 | 导致特征计算错误 | 门闸检查 ROI 维度匹配 |
| 5 | 不注明分割模型就运行分割 | 不同模型适用不同数据 | 必须确认模型参数 |
| 6 | Phase 2 任务依赖 Phase 1 中间状态 | 无法独立重跑 | 每个任务接收完整输入 |
| 7 | 门闸检查时修改数据 | 违背检查-执行分离原则 | 门闸只检查不修改 |

### 🚫 结果禁忌

| # | 禁止行为 | 为什么 | 正确做法 |
|---|---------|--------|---------|
| 8 | 不展示门闸报告直接跳过 | 用户无法了解数据质量 | 门闸报告必须展示 |
| 9 | 导出特征矩阵不含特征名 | 下游无法正确解析 | 必须包含特征名表头 |
| 10 | 特征矩阵含大量 NaN 不报告 | 可能是提取错误 | 检查 NaN 比例并报告 |
