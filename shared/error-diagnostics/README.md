# 错误诊断知识库 (Error Diagnostics Knowledge Base)

> MSRA 项目专用。为 Exec Runner 的自愈 Debug 提供错误诊断和修复建议支持。

## 概述

本知识库包含医学统计分析中常见的错误模式、诊断方法和解决方案。当分析代码执行失败时，Exec Runner 会使用本知识库进行错误诊断，并生成修复建议。

## 目录结构

```
error-diagnostics/
├── README.md                    # 本文件
├── error_patterns.md            # 错误模式详细文档
├── auto_fix_suggestions.py      # Python自动修复建议生成器
└── auto_fix_suggestions.R       # R自动修复建议生成器
```

## 错误类型分类

### 1. 统计错误 (Statistical Errors)
- **S1. 多重共线性**: VIF > 10
- **S2. 分离问题**: Logistic回归中perfect separation
- **S3. 样本量不足**: 实际样本量 < SAP计划的70%
- **S4. 比例风险假设违反**: Cox回归中PH假设不满足

### 2. 数据错误 (Data Errors)
- **D1. 缺失数据模式**: MCAR/MAR/MNAR
- **D2. 极端异常值**: IQR方法检测
- **D3. 数据分布偏态**: 偏度/峰度异常

### 3. 环境错误 (Environment Errors)
- **E1. 内存不足**: 系统内存不足
- **E2. 包版本冲突**: R/Python包版本不兼容
- **E3. 计算超时**: 运行时间过长

### 4. 代码错误 (Code Errors)
- **C1. 语法错误**: 代码语法问题
- **C2. 运行时错误**: 变量不存在、数据类型不匹配
- **C3. 逻辑错误**: 分析逻辑错误

## 错误严重程度分级

| 级别 | 描述 | 处理方式 |
|------|------|----------|
| **P0** | 阻断式错误 | 必须立即修复，否则无法继续 |
| **P1** | 严重错误 | 需要修复，但可暂时继续其他工作 |
| **P2** | 警告 | 建议修复，但不影响主要结果 |
| **P3** | 信息 | 供参考，无需立即处理 |

## 使用方法

### 在 Exec Runner 中使用

当分析代码执行失败时，Exec Runner 会：

1. **错误检测**: 识别错误类型和位置
2. **知识库查询**: 在本知识库中查找匹配的错误模式
3. **诊断生成**: 根据错误详情生成诊断报告
4. **修复建议**: 提供具体的修复方案和代码示例
5. **风险评估**: 评估修复的风险和影响
6. **自愈尝试**: 应用修复建议并重新执行代码

### Python 使用示例

```python
from auto_fix_suggestions import AutoFixSuggestions

# 创建修复建议生成器
fix_generator = AutoFixSuggestions()

# 诊断错误
diagnosis = fix_generator.diagnose_and_suggest(
    "multicollinearity",
    {"vif_value": 12.5}
)

# 生成修复代码
fix_code = fix_generator.generate_fix_code(
    "multicollinearity",
    {"dataframe_name": "cleaned_data"}
)

# 评估风险
risk = fix_generator.assess_risk("multicollinearity", fix_applied=True)
```

### R 使用示例

```r
source("auto_fix_suggestions.R")

# 诊断错误
diagnosis <- generate_fix_suggestions("multicollinearity", list(vif_value = 12.5))

# 生成修复代码
fix_code <- generate_fix_code("multicollinearity", list(dataframe_name = "cleaned_data"))

# 评估风险
risk <- assess_fix_risk("multicollinearity", fix_applied = TRUE)
```

## 集成到 MSRA 流水线

### Stage 3: 分析执行

在 `analysis-exec` 技能的 Phase 6 中，自愈 Debug 流程已集成本知识库：

```
生成代码 → 执行 → 成功？→ 输出结果
                ↓ 失败
           DebugAgent 介入（最多5轮）
           ├── 第1轮: 分析错误类型 + 根因 + 修复
           ├── 第2轮: 上下文传递 + 增强修复
           ├── 第3轮: 统计诊断 + 方法降级
           ├── 第4轮: 数据检查 + 数据修复
           └── 第5轮: 仍失败 → 标记为 [SKIP]
```

### Stage 1.5/2.5/3.5: 质量门闸

质量门闸会检查错误诊断的完整性：
- 所有错误是否已诊断
- 修复建议是否合理
- 风险评估是否完整

## 扩展知识库

### 添加新的错误模式

1. 在 `error_patterns.md` 中添加新的错误模式文档
2. 在 `auto_fix_suggestions.py` 和 `auto_fix_suggestions.R` 中添加对应的修复建议
3. 更新本 README 的错误类型分类

### 修复建议模板

```markdown
### [错误类型名称]

**诊断方法**：
- [诊断方法描述]

**解决方案**：
1. [解决方案1]
2. [解决方案2]
3. [解决方案3]

**代码示例**：
```r
# R代码示例
```

**风险提示**：
- [风险描述]
```

## 质量保证

### 测试用例

- 每个错误类型至少一个测试用例
- 测试诊断准确性
- 测试修复建议有效性
- 测试风险评估合理性

### 文档完整性

- 所有错误类型必须有完整文档
- 所有修复建议必须有代码示例
- 所有风险必须有评估说明

## 更新日志

### v0.1.0 (2026-05-30)
- 初始版本
- 支持4类错误诊断
- 提供Python和R实现
- 集成到MSRA流水线

---

*维护者: MSRA开发团队*
*最后更新: 2026-05-30*