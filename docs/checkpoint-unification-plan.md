# MSRA 检查点编号体系统一计划书

> **版本**: v1.0
> **日期**: 2026-06-20
> **状态**: 待评审
> **影响范围**: 6 个 SKILL.md + 3 个 test-prompts.json + 1 个 lint 脚本 + passport 文档

---

## 1. 现状诊断

### 1.1 问题概述

当前 MSRA 项目存在两套检查点编号体系共用 `S` 前缀，导致跨 Skill 引用时语义歧义：

| 体系 | 位置 | 编号范围 | 语义 |
|------|------|---------|------|
| **Pipeline 全局 SLIM** | `pipeline/SKILL.md` | S1-S4 | 流水线级轻量检查点，控制 Stage 间流转 |
| **Skill 内部 MANDATORY** | 各 `*/SKILL.md` | S0-S8 | 阶段级强制检查点，控制 Phase 内决策 |

### 1.2 冲突实例

| 编号 | pipeline 含义 | analysis-exec 含义 | report 含义 |
|------|--------------|-------------------|------------|
| **S2** | Stage 3 Phase 3 后（主分析完成） | — | — |
| **S3** | Stage 4 Phase 1 后（结果解读） | Phase 2 描述统计后 | Phase 2 表格生成后 |
| **S4** | Stage 4 Phase 4 后（方法学描述） | — | Phase 1 结果解读（SLIM） |
| **S5** | — | — | Phase 4 方法学描述 |
| **S7** | — | Phase 3 假设检验（已改为 EXEC7） | Phase 6 报告组装 |

**核心矛盾**: `S3` 在 pipeline 中指向"Stage 4 结果解读"，在 analysis-exec 中指向"描述统计完成"，在 report 中指向"表格生成完成"——三个完全不同的检查点共用同一编号。

### 1.3 根因分析

1. **历史演进**: Pipeline 的 SLIM 检查点（S1-S4）先于各 Skill 的 MANDATORY 检查点（S0-S8）定义，后者在独立开发时未考虑前缀冲突
2. **命名空间缺失**: 两套体系未使用命名空间隔离（如 `PIPE-S1` vs `EXEC-S3`）
3. **文档分散**: 检查点定义分散在 6 个文件中，无统一注册表

---

## 2. 目标

建立**单一、无歧义、可扩展**的检查点编号体系，满足：

- **唯一性**: 每个检查点编号全局唯一，跨文件引用无歧义
- **可读性**: 编号自解释，一眼看出所属 Skill 和阶段
- **可扩展**: 新增检查点不破坏现有编号，支持未来 Skill 扩展
- **可验证**: CI 可自动检测编号冲突和引用断裂
- **向后兼容**: 过渡期内旧编号仍可解析（带 deprecation 警告）

---

## 3. 方案选型

### 3.1 推荐方案：分层命名空间（Hierarchical Namespace）

采用 `{SCOPE}-{ID}` 格式，将检查点按作用域分层：

```
{SCOPE}-{ID}
  │       │
  │       └── 数字或字母，作用域内唯一
  │
  └── 作用域标识符
      ├── PIPE   → Pipeline 全局检查点（原 S1-S4）
      ├── PREP   → data-prep 内部检查点（原 S0/S2/S4/S5/M1）
      ├── PLAN   → analysis-plan 内部检查点（原 S5）
      ├── EXEC   → analysis-exec 内部检查点（原 S0/S3/EXEC7/S8/ME1）
      ├── REPT   → report 内部检查点（原 S3/S4/S5/S7/M4）
      ├── CAL    → calibration 内部检查点
      └── GATE   → 质量门闸检查点（原 M1-M5）
```

#### 映射表（当前 → 新编号）

**Pipeline 全局 SLIM（原 S1-S4）**

| 旧编号 | 位置 | 新编号 | 说明 |
|--------|------|--------|------|
| S1 | Stage 2 后（Estimands+方法确认） | `PIPE-01` | 方法确认后才能进入 SAP 制定 |
| S2 | Stage 3 Phase 3 后（主分析完成） | `PIPE-02` | 主分析结果确认 |
| S3 | Stage 4 Phase 1 后（结果解读） | `PIPE-03` | 结果解读完成 |
| S4 | Stage 4 Phase 4 后（方法学描述） | `PIPE-04` | 方法学描述完成 |

**data-prep 内部（原 S0/S2/S4/S5 + M1）**

| 旧编号 | 位置 | 新编号 | 说明 |
|--------|------|--------|------|
| S0 | Phase 1 Step 0 快速画像 | `PREP-01` | 数据画像展示 |
| S2 | Phase 2 清洗策略确认 | `PREP-02` | 清洗策略必须用户确认 |
| S4 | Phase 4 EDA 质量检查 | `PREP-03` | EDA 异常发现确认 |
| S5 | Phase 4 盲态审核 | `PREP-04` | 盲态审核质疑解决 |
| M1 | Phase 5 数据库锁定 | `GATE-01` | 数据质量门闸（原 M1 升级为全局门闸） |

**analysis-plan 内部（原 S5）**

| 旧编号 | 位置 | 新编号 | 说明 |
|--------|------|--------|------|
| S5 | Phase 5 变量构造定义 | `PLAN-01` | 变量构造 4 项检查 |

**analysis-exec 内部（原 S0/S3/EXEC7/S8/ME1）**

| 旧编号 | 位置 | 新编号 | 说明 |
|--------|------|--------|------|
| S0 | Phase 0 SAP 验证 | `EXEC-01` | SAP 格式+样本量验证 |
| S3 | Phase 2 描述统计 | `EXEC-02` | Table 1 基线特征确认 |
| EXEC7 | Phase 3 假设检验 | `EXEC-03` | 假设检验结果确认 |
| S8 | Phase 4 质量检查 | `EXEC-04` | 质检结果确认 |
| ME1 | Phase 3 主要分析 | `EXEC-05` | 主要分析结果确认（原 ME1） |

**report 内部（原 S3/S4/S5/S7/M4）**

| 旧编号 | 位置 | 新编号 | 说明 |
|--------|------|--------|------|
| S3 | Phase 2 表格生成 | `REPT-01` | 表格数值一致性确认 |
| S4 | Phase 3 图表生成 | `REPT-02` | 图表发表级质量确认 |
| S5 | Phase 4 方法学描述 | `REPT-03` | 方法学描述完整性 |
| S7 | Phase 6 报告组装 | `REPT-04` | 最终报告组装确认 |
| M4 | Phase 5 统计质量检查 | `GATE-04` | 报告质量门闸（原 M4） |

**质量门闸（原 M1-M5）**

| 旧编号 | 位置 | 新编号 | 说明 |
|--------|------|--------|------|
| M1 | Stage 1.5 数据门闸 | `GATE-01` | 9 项数据质量阻断检查 |
| M2 | Stage 2.5 SAP 门闸 | `GATE-02` | 8 项 SAP 质量阻断检查 |
| M3 | Stage 3.5 结果门闸 | `GATE-03` | 14 项结果质量阻断检查 |
| M4 | Stage 4 统计质检 | `GATE-04` | 统计合规检查 |
| M4' | Stage 4 A/B 决策 | `GATE-05` | 结束 vs Paper Track 决策 |
| M5 | 收敛失败检测 | `GATE-06` | 回退≥3 次触发收敛检测 |
| ME1 | Stage 3 主要分析确认 | `EXEC-05` | 已合并到 EXEC 体系 |

---

### 3.2 替代方案对比

| 方案 | 格式示例 | 优点 | 缺点 | 推荐度 |
|------|---------|------|------|--------|
| **分层命名空间** | `EXEC-03` | 清晰分层、可扩展、自解释 | 需要批量替换 | ★★★★★ |
| 纯数字全局 | `CP-001` ~ `CP-050` | 最简单 | 无自解释性、难以扩展 | ★★★☆☆ |
| 保留 S 前缀+Skill 后缀 | `S3-EXEC` | 兼容旧编号 | 仍依赖上下文、不够直观 | ★★☆☆☆ |
| 完全描述性 | `[EXEC-SAP-VALIDATE]` | 完全自解释 | 过长、影响可读性 | ★★☆☆☆ |

---

## 4. 实施计划

### 4.1 批次划分

为避免单次改动过大导致难以 review，分三批实施：

#### 批次 1：质量门闸（影响最小，可独立验证）

| 任务 | 文件 | 工作量 | 验证方式 |
|------|------|--------|---------|
| 将 M1-M5/ME1 改为 GATE-01~GATE-06 | `pipeline/SKILL.md` | ~15 处替换 | lint_gate_counts.py |
| 更新 M-table 引用 | `pipeline/SKILL.md` | ~5 处 | 手动检查 |
| 更新反例中的 M 编号 | `pipeline/SKILL.md` | ~3 处 | 手动检查 |

**风险**: 低。门闸编号仅在 pipeline 中使用，不涉及跨 Skill 引用。

#### 批次 2：Pipeline 全局 SLIM（S1-S4 → PIPE-01~04）

| 任务 | 文件 | 工作量 | 验证方式 |
|------|------|--------|---------|
| 替换 pipeline 中 S1-S4 | `pipeline/SKILL.md` | ~8 处 | grep 确认 |
| 更新所有 Skill 中对 S1-S4 的引用 | 5 个 SKILL.md | ~12 处 | grep 确认 |
| 更新 test-prompts.json | 3 个 JSON 文件 | ~5 处 | JSON 解析验证 |

**风险**: 中。涉及跨文件引用，需确保所有引用同步更新。

#### 批次 3：各 Skill 内部 MANDATORY（S0-S8 → {SCOPE}-XX）

| 任务 | 文件 | 工作量 | 验证方式 |
|------|------|--------|---------|
| data-prep: S0/S2/S4/S5 → PREP-01~04 | `data-prep/SKILL.md` | ~10 处 | grep 确认 |
| analysis-plan: S5 → PLAN-01 | `analysis-plan/SKILL.md` | ~3 处 | grep 确认 |
| analysis-exec: S0/S3/EXEC7/S8/ME1 → EXEC-01~05 | `analysis-exec/SKILL.md` | ~12 处 | grep 确认 |
| report: S3/S4/S5/S7 → REPT-01~04 | `report/SKILL.md` | ~8 处 | grep 确认 |
| 更新所有交叉引用 | 6 个 SKILL.md | ~20 处 | grep 确认 |

**风险**: 中。涉及大量内部引用重命名。

### 4.2 时间线

```
Week 1: 批次 1（门闸编号）
  Day 1-2: 修改 pipeline/SKILL.md
  Day 3:   验证 + PR
  Day 4-5: Review + 合并

Week 2: 批次 2（Pipeline 全局）
  Day 1-2: 修改所有文件中的 S1-S4
  Day 3:   验证 + PR
  Day 4-5: Review + 合并

Week 3: 批次 3（Skill 内部）
  Day 1-3: 修改 4 个 Skill 的内部编号
  Day 4:   验证 + PR
  Day 5:   Review + 合并

Week 4: 收尾
  Day 1-2: 更新文档（passport_schema、agents 文档）
  Day 3:   添加 CI 检查脚本
  Day 4-5: 最终验证 + 合并
```

### 4.3 CI 增强

新增 `lint_checkpoint_registry.py` 脚本，功能：

1. **注册表校验**: 读取所有 SKILL.md，提取所有 `{SCOPE}-{ID}` 格式检查点，确保全局唯一
2. **引用完整性**: 检查所有 `[{SCOPE}-{ID}]` 引用是否指向已注册的检查点
3. **废弃检测**: 检测残留的 `[MANDATORY-SX]` / `[SLIM-SX]` 旧格式（过渡期后升级为错误）
4. **文档同步**: 检查 `docs/checkpoint-registry.md` 是否与代码中的检查点一致

```python
# lint_checkpoint_registry.py 伪代码
CHECKPOINT_PATTERN = re.compile(r'\b([A-Z]{2,6})-(\d{2,3})\b')

def scan_all_checkpoints(repo_root):
    """扫描所有 SKILL.md，返回 {checkpoint: [file, line]} 映射"""
    ...

def validate_uniqueness(checkpoints):
    """确保每个编号全局唯一"""
    ...

def validate_references(checkpoints):
    """确保所有引用指向已定义的编号"""
    ...

def detect_legacy_markers(files):
    """检测旧格式 [MANDATORY-SX] / [SLIM-SX]"""
    ...
```

---

## 5. 过渡策略

### 5.1 向后兼容（过渡期 4 周）

| 阶段 | 行为 | 时间 |
|------|------|------|
| 并行期 | 旧编号和新编号同时存在，文档中标注 `(原 S3)` | Week 1-2 |
|  deprecation 期 | 旧编号保留但标注 `[DEPRECATED: 使用 EXEC-02]` | Week 3-4 |
| 清理期 | 删除所有旧编号，仅保留新编号 | Week 5+ |

### 5.2 文档更新

1. **新增 `docs/checkpoint-registry.md`**: 全局检查点注册表，包含所有 `{SCOPE}-{ID}` 的定义、位置、说明
2. **更新 `shared/passport/passport_schema.md`**: 将 passport 中的 checkpoint 字段从 `S3` 改为 `EXEC-02`
3. **更新 `agents/AGENTS.md`**: Agent 角色卡中的检查点引用同步更新

---

## 6. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 批量替换误伤 | 中 | 高 | 每批次单独 PR，逐行 review；使用精确匹配而非正则批量替换 |
| 遗漏引用 | 中 | 中 | 新增 CI 脚本自动检测；过渡期保留旧编号兼容性 |
| 测试用例失效 | 低 | 中 | 同步更新 test-prompts.json；CI 中增加 JSON 格式校验 |
| 文档不同步 | 中 | 低 | 将 checkpoint-registry.md 纳入 CI 同步检查 |
| 用户习惯中断 | 低 | 低 | 过渡期保留旧编号；文档中提供对照表 |

---

## 7. 验收标准

- [ ] 所有 6 个 SKILL.md 中无 `[MANDATORY-SX]` / `[SLIM-SX]` 旧格式（过渡期后）
- [ ] 所有检查点编号全局唯一（通过 `lint_checkpoint_registry.py`）
- [ ] 所有检查点引用指向已定义的编号（通过 `lint_checkpoint_registry.py`）
- [ ] `docs/checkpoint-registry.md` 与代码一致（通过 CI）
- [ ] test-prompts.json 全部通过 JSON 解析验证
- [ ] lint_gate_counts.py 仍然通过
- [ ] 所有反例编号连续无跳号

---

## 8. 附录

### 8.1 完整新旧对照表

| 旧编号 | 所属 Skill | 位置 | 新编号 | 说明 |
|--------|-----------|------|--------|------|
| S1 | pipeline | Stage 2 后 | `PIPE-01` | 方法确认检查点 |
| S2 | pipeline | Stage 3 Phase 3 后 | `PIPE-02` | 主分析结果检查点 |
| S3 | pipeline | Stage 4 Phase 1 后 | `PIPE-03` | 结果解读检查点 |
| S3 | analysis-exec | Phase 2 描述统计 | `EXEC-02` | Table 1 确认 |
| S3 | report | Phase 2 表格生成 | `REPT-01` | 表格一致性确认 |
| S4 | pipeline | Stage 4 Phase 4 后 | `PIPE-04` | 方法学描述检查点 |
| S4 | report | Phase 1 结果解读(SLIM) | `REPT-05` | 结果解读(SLIM) |
| S5 | data-prep | Phase 4 盲态审核 | `PREP-04` | 盲态审核确认 |
| S5 | analysis-plan | Phase 5 变量构造 | `PLAN-01` | 变量构造检查 |
| S5 | report | Phase 4 方法学描述 | `REPT-03` | 方法学描述确认 |
| S7 | report | Phase 6 报告组装 | `REPT-04` | 报告组装确认 |
| S0 | analysis-exec | Phase 0 SAP 验证 | `EXEC-01` | SAP 验证确认 |
| S8 | analysis-exec | Phase 4 质量检查 | `EXEC-04` | 质检结果确认 |
| EXEC7 | analysis-exec | Phase 3 假设检验 | `EXEC-03` | 假设检验确认 |
| ME1 | analysis-exec | Phase 3 主要分析 | `EXEC-05` | 主要分析确认 |
| M1 | pipeline | Stage 1.5 门闸 | `GATE-01` | 数据质量门闸 |
| M2 | pipeline | Stage 2.5 门闸 | `GATE-02` | SAP 质量门闸 |
| M3 | pipeline | Stage 3.5 门闸 | `GATE-03` | 结果质量门闸 |
| M4 | pipeline | Stage 4 统计质检 | `GATE-04` | 报告质量门闸 |
| M4' | pipeline | Stage 4 A/B 决策 | `GATE-05` | 结束/Paper Track 决策 |
| M5 | pipeline | 收敛失败检测 | `GATE-06` | 收敛检测门闸 |

### 8.2 命名空间预留

为未来扩展预留以下命名空间：

| 命名空间 | 用途 | 预留范围 |
|---------|------|---------|
| `PAPER` | Paper Track 检查点 | PAPER-01~99 |
| `REVU` | 评审流程检查点 | REVU-01~99 |
| `CAL` | 校准模式检查点 | CAL-01~99 |
| `META` | 元数据/Passport 检查点 | META-01~99 |
| `GATE` | 质量门闸（已启用） | GATE-01~99 |
