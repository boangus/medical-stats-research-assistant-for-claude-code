# Phase 1: 变量构造（Variable Construction）

**输入**: 清洗后数据 + 变量构造定义 + 标准化变量映射
**输出**: 分析数据集 + 变量构造日志
**检查点**: 🟡 SLIM（构造完成后展示摘要）

---

## 变量构造流程

### Step 1.1: 加载变量构造定义

```python
def load_construction_definitions(passport):
    """从 passport 加载变量构造定义"""

    # 从 analysis-plan Phase 5 输出
    definitions = passport.get_artifact("variable_construction_definitions")

    # 分类
    derived_vars = [v for v in definitions if v.type == "derived"]
    interaction_vars = [v for v in definitions if v.type == "interaction"]
    time_vars = [v for v in definitions if v.type == "time_dependent"]

    return {
        "derived": derived_vars,
        "interaction": interaction_vars,
        "time_dependent": time_vars,
    }
```

### Step 1.2: 执行变量构造

```python
def construct_variables(df, definitions):
    """执行变量构造"""

    construction_log = []

    # 1. 派生变量
    for var in definitions["derived"]:
        try:
            df[var.name] = eval(var.formula, {"df": df, "np": np})
            construction_log.append({
                "variable": var.name,
                "type": "derived",
                "formula": var.formula,
                "status": "success",
                "missing_rate": df[var.name].isna().mean(),
            })
        except Exception as e:
            construction_log.append({
                "variable": var.name,
                "type": "derived",
                "formula": var.formula,
                "status": "failed",
                "error": str(e),
            })

    # 2. 交互项
    for var in definitions["interaction"]:
        df[var.name] = df[var.var1] * df[var.var2]
        construction_log.append({...})

    # 3. 时间依赖变量
    for var in definitions["time_dependent"]:
        df = create_time_dependent_variable(df, var)
        construction_log.append({...})

    return df, construction_log
```

### Step 1.3: 变量构造质量检查

```python
def validate_construction(df, construction_log):
    """构造后质量检查"""

    issues = []

    for entry in construction_log:
        if entry["status"] == "failed":
            issues.append(f"❌ {entry['variable']}: 构造失败 - {entry['error']}")
        elif entry["missing_rate"] > 0.5:
            issues.append(f"⚠️ {entry['variable']}: 缺失率 {entry['missing_rate']:.1%} > 50%")
        elif df[entry["variable"]].nunique() == 1:
            issues.append(f"⚠️ {entry['variable']}: 常量变量（仅一个唯一值）")

    return issues
```

---

## 检查点

```markdown
--- Phase 1 变量构造完成 ---

构造结果:
- 派生变量: {derived_count} 个（成功 {success} / 失败 {failed}）
- 交互项: {interaction_count} 个
- 时间依赖变量: {time_count} 个

质量检查:
- 常量变量: {constant_count} 个
- 高缺失变量 (>50%): {high_missing_count} 个

{issues_list}

通过 → 进入 Phase 2
不通过 → 修复后重新构造
```

---

## 产物记录

| 产物 | 格式 | 消费方 |
|------|------|--------|
| analysis_dataset.csv | CSV | Phase 2-3 |
| variable_construction_log.md | Markdown | 质量审计 |
