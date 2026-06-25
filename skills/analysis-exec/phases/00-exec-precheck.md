# Phase 0: SAP 验证与执行前检查 + Phase 0.5: 进度跟踪初始化 + Phase 0.6: 变量名标准化确认

## Phase 0: SAP 验证与执行前检查（SAP Validation & Pre-Execution Check）

**输入**: SAP + 变量构造定义 + 锁定数据
**输出**: 验证报告 + 执行状态摘要
**检查点**: 🔴 MANDATORY-EXEC-01

### Gate 0: SAP 合法性检查

```python
def validate_sap(sap_document):
    """SAP 必须包含以下必需章节"""
    required_sections = [
        "研究目标",           # 研究问题和假设
        "分析人群",           # ITT/PP/安全性人群定义
        "主要终点",           # 主要结局指标
        "统计方法",           # 每个终点的统计方法
        "缺失数据处理",       # 缺失数据策略
        "样本量计算",         # 样本量依据
        "多重比较校正",       # 如适用
    ]

    # 检查每个必需章节是否存在且非空
    for section in required_sections:
        if not sap_document.has_section(section):
            raise SAPValidationError(f"SAP 缺少必需章节: {section}")

    # 检查统计方法与终点的对应关系
    for endpoint in sap_document.endpoints:
        if not endpoint.has_statistical_method():
            raise SAPValidationError(f"终点 '{endpoint.name}' 未指定统计方法")
```

### Gate 1: 研究问题 → 估计目标 → 统计方法一致性

```python
def validate_rq_estimand_method_consistency(sap, estimands, analysis_plan):
    """三重一致性检查"""

    # 1. RQ ↔ Estimand 一致性
    for rq in sap.research_questions:
        if not estimands.has_estimand_for(rq):
            raise ConsistencyError(f"研究问题 '{rq.id}' 无对应估计目标")

    # 2. Estimand ↔ Method 一致性
    for estimand in estimands:
        method = analysis_plan.get_method_for(estimand)
        if not method:
            raise ConsistencyError(f"估计目标 '{estimand.id}' 无对应统计方法")

        # 检查方法是否匹配估计目标的类型
        if estimand.is_survival and not method.is_survival_method:
            raise ConsistencyError(f"生存分析估计目标 '{estimand.id}' 使用了非生存分析方法")
```

### Gate 2: 数据集合法性检查

```python
def validate_dataset(lockfile_path):
    """检查数据集是否已锁定"""
    lock_status = check_lock_status(lockfile_path)
    if not lock_status.locked:
        raise DatasetNotLockedError(
            "数据集未锁定，请先完成 Stage 1.5（数据质量门闸）"
        )
    return lock_status
```

### 检查点: MANDATORY-EXEC-01

```markdown
--- MANDATORY-EXEC-01: SAP 验证 ---

SAP 验证结果:
- [必需章节]: {section_check}
- [RQ-Estimand-Method 一致性]: {consistency_check}
- [数据集锁定]: {lock_check}

通过 → 进入 Phase 0.5
不通过 → 修复后重新验证
```

### 产物记录

| 产物 | 格式 | 消费方 |
|------|------|--------|
| sap_validation_report.md | Markdown | 执行参考 |
| consistency_check_log.md | Markdown | 质量审计 |

---

## Phase 0.5: 进度跟踪初始化

**输入**: passport + SAP
**输出**: execution_progress.json
**检查点**: 🟡 ADAPTIVE（仅异常时暂停）

```python
def init_progress_tracking(passport, sap):
    """初始化执行进度跟踪"""

    # 从 SAP 中提取所有需要执行的分析
    analyses = extract_analyses_from_sap(sap)

    # 创建进度跟踪结构
    progress = {
        "total_analyses": len(analyses),
        "completed": 0,
        "failed": 0,
        "skipped": 0,
        "analyses": [
            {
                "id": analysis.id,
                "name": analysis.name,
                "status": "pending",  # pending → running → completed/failed/skipped
                "start_time": None,
                "end_time": None,
                "error": None,
            }
            for analysis in analyses
        ],
    }

    # 保存到 passport
    passport.set_artifact("execution_progress", progress)
    return progress
```

### 产物记录

| 产物 | 格式 | 消费方 |
|------|------|--------|
| execution_progress.json | JSON | Phase 3-6 消费 |

---

## Phase 0.6: 变量名标准化确认

**输入**: SAP 变量名 + analysis-plan Phase 2 输出
**输出**: standardized_variable_mapping.json
**检查点**: 🟡 SLIM

### 变量名标准化流程

```python
def standardize_variable_names(sap_variables, analysis_plan_output):
    """变量名标准化确认"""

    # 1. 从 analysis-plan Phase 2 获取标准化变量名
    standardized = analysis_plan_output.get_standardized_variables()

    # 2. 与 SAP 中的变量名比对
    mismatches = []
    for var in sap_variables:
        if var.name != standardized.get(var.name):
            mismatches.append({
                "sap_name": var.name,
                "standard_name": standardized.get(var.name),
                "source": "analysis-plan Phase 2",
            })

    # 3. 如有不一致，展示给用户确认
    if mismatches:
        print("⚠️ 变量名不一致:")
        for m in mismatches:
            print(f"  SAP: {m['sap_name']} → 标准: {m['standard_name']}")

        # ADAPTIVE: 需要用户确认
        if len(mismatches) > 5:
            raise VariableNameMismatchError(
                f"发现 {len(mismatches)} 个变量名不一致，请确认"
            )

    # 4. 生成标准化映射
    mapping = {var.name: standardized.get(var.name, var.name) for var in sap_variables}
    return mapping
```

### 检查点

```markdown
--- 变量名标准化确认 ---

变量名映射: {mapping_count} 个变量
不一致项: {mismatch_count} 个

如无不一致 → 自动继续
如有不一致 → 展示给用户确认
```

### 产物记录

| 产物 | 格式 | 消费方 |
|------|------|--------|
| standardized_variable_mapping.json | JSON | Phase 1-3 消费 |
