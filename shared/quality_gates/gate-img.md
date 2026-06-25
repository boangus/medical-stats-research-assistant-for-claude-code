# Gate: IMG QUALITY (Imaging Module)

## 元数据
- gate_id: "img_quality"
- module: "imaging"
- blocking: true
- skill_source: "imaging-analysis"
- checkpoint_id: "GATE-IMG / IMG-1"
- extension_adapter: "ExtensionGateAdapter('img').run_module_gate('img_feature_gate', inputs)"

## 输入

| 参数 | 类型 | 来源 | 必填 |
|------|------|------|------|
| image_files | file (dicom/nifti/nrrd) | DICOMLoader/load_nifti/load_nrrd | ✅ |
| roi_mask | file (nifti/nrrd) | 用户提供或分割输出 | 否（radiomics 模式必填） |
| segmentation_result | file (nifti) | Phase 2 SegmentationPipeline | 否（segmentation 模式必填） |
| feature_matrix | file (csv) | Phase 2 RadiomicsExtractor | 否（特征提取后必填） |
| preprocessing_log | file (md) | Phase 1 ImagePreprocessor | ✅ |
| feature_selection_log | file (md) | Phase 2 FeatureSelector | 否 |

## 检查清单 (4 项)

| # | 检查项 | 通过标准 | 关键项 |
|---|--------|---------|--------|
| 1 | DICOM 完整性 | 文件可成功读取；体素间距 spacing ∈ [0.5, 5.0] mm；SNR > 5 且无 NaN/Inf | ✅ 硬阻断 |
| 2 | 分割质量 | ROI 掩膜与影像维度完全一致；分割掩码非空；Dice ≥ 0.5（有参考标准时） | ✅ 硬阻断 |
| 3 | 特征提取覆盖率 | 特征矩阵无大量 NaN（NaN 比例 < 10%）；特征名表头完整；样本数 ≥ 1 | 否 |
| 4 | 特征稳定性 | 重复提取方差 CV < 0.2；不同 ROI 切片特征 ICC > 0.7；异常特征已标记 | 否 |

### 检查项 1（DICOM 完整性）详细标准
- DICOM/NIfTI/NRRD 文件可成功读取（无 IOError）
- 体素间距 spacing ∈ [0.5, 5.0] mm（物理意义合理）
- 影像信噪比 SNR > 5
- 影像数据无 NaN/Inf 异常值
- 通过标准：以上全部满足

### 检查项 2（分割质量）详细标准
- ROI 掩膜与影像维度完全一致（image.shape == mask.shape）
- 分割掩码非空（非零体素数 > 0）
- 如有参考标准分割，Dice 系数 ≥ 0.5
- 通过标准：以上全部满足

### 检查项 3（特征提取覆盖率）详细标准
- 特征矩阵 NaN 比例 < 10%
- 特征矩阵包含特征名表头（下游可正确解析）
- 样本数 ≥ 1（至少 1 例可分析样本）
- 通过标准：以上全部满足

### 检查项 4（特征稳定性）详细标准
- 重复提取（同影像同参数）特征方差 CV < 0.2
- 不同 ROI 切片间特征 ICC > 0.7（稳定性）
- 异常特征（离群值）已标记并报告
- 通过标准：以上全部满足

## 判定规则

- **PASS**: 全部通过 (4/4) → ✅ 进入下一阶段
- **CONDITIONAL**: 2-3/4 通过且关键项全通过 → ⚠️ 记录风险后继续
- **BLOCK**: < 2/4 通过 **或** 关键项 1/2 任一未通过 → ❌ **强制退回 Phase 1/2 修订**

> **关键项定义**：项 1（DICOM 完整性）、项 2（分割质量）为硬阻断项，不可条件通过。

## 输出 (gate_result schema)

```json
gate_result: {
  "gate": "img_quality",
  "module": "imaging",
  "passed": bool,
  "total": 4,
  "passed_count": int,
  "failed_items": ["IG-0X", ...],
  "conditional": bool,
  "blocking_items": ["IG-01" | "IG-02"],
  "timestamp": "ISO8601"
}
```

## 与模块的联动

- **BLOCK** → 退回 Phase 1 修订数据加载/预处理，或退回 Phase 2 修订分割/特征提取
- **回退 ≥ 2 次** → 触发收敛检测（见 pipeline/SKILL.md §7.3）
- **CONDITIONAL** → 记录风险后继续 Phase 3 结果审查
- **Checkpoint**: [GATE-IMG] 门闸通过后方可进入 Phase 3 用户确认
- **Skill 模式**：`imaging-analysis` 复用，Mode=`quality-gate`（只检查，不修改）
- **Agent 模式**：通过 `ExtensionGateAdapter("img")` 调用
- 参考实现：`shared/quality_gates/gate_runner.py` + `check_items.py`
