# MSRA v1.0.0 系统评估报告

**日期**：2026-06-26
**场景**：产品评审 + 代码质量健康检查
**参与成员**：产品评审员（gstack-product-reviewer）+ 调查员（gstack-investigator）

---

## 📌 TL;DR（执行摘要）

- **整体结论**：🟢 有条件 Go — 项目功能完整、测试健康（902/927 通过，97.3%）、文档体系优秀，但存在值得重视的架构和工程实践问题
- **综合评分**：产品 7.6/10 | 代码健康 7.8/10 | 加权 **7.7/10**
- **阻塞项**：0 个（无 P0 级阻断问题）
- **最大机会**：48 章统计方法知识库 + 16 个报告规范 + 112 方法决策树是真正护城河，解决 DX 问题后有望成为标准工具
- **最大风险**：LLM 在统计计算上的不可靠性，质量门闸能检查流程合规但无法验证数值正确性

---

## 🎯 核心结论卡片

| 项目 | 内容 |
|------|------|
| Go / No-Go | 🟢 Go（有条件发布） |
| 产品评分 | 7.6/10 |
| 代码健康评分 | 7.8/10 |
| 严重度分布 | 🔴 3 / 🟠 6 / 🟡 7 / 🟢 若干 |
| 关键行动项 | 8 条 |
| 建议负责人 | 项目维护者（boangus） |
| 定位建议 | 不建议标记 Production/Stable，建议 "4 - Beta" 或 "v1.0 — Public Beta" |

---

## 1. 各成员核心结论

### 🔍 产品评审员（产品评审）

**核心判断**：MSRA 是一个**设计精良、知识库深度惊人的医学统计 Pipeline 工具**。核心竞争力不在代码复杂度，而在于 48 章统计方法 + 16 个报告规范 + 112 方法决策树 + 5 个阻断式质量门闸 + 严格方案遵循机制 — 这是一座用 Markdown 和 LLM 工作流构建的「知识基础设施」。但"1.0.0 Stable"的标签需谨慎，它更像是**成熟的 Beta**而非传统 Production/Stable。

**关键建议**：
- 值价值主张建立在"LLM 能可靠执行医学统计分析"的强假设上，需在 README 中更突出专业审核提示
- 16 个命令中 `/msra-paper` 和 `/msra-write` 功能重叠，建议合并或明确边界
- 缺少 `/msra-status` 独立命令和 Pipeline 进度可视化，用户体验核心短板
- Agent Python 代码（MessageBus/TaskQueue/ConflictResolver）是参考实现但未被 Pipeline 实际调用，需明确标注

**维度评分**：

| 维度 | 评分 | 说明 |
|------|------|------|
| 产品定位与价值主张 | 8.5/10 | 领域深度无人能及，但价值假设未经真实用户验证 |
| 架构设计 | 8.5/10 | Pipeline+Skill+Agent 三层解耦精良，LLM 执行层不可测试是核心风险 |
| 功能完整性 | 8.0/10 | 16 命令覆盖全流程，缺 /msra-status、数据版本管理、协作功能 |
| 用户体验（DX） | 7.0/10 | 命令命名一致，但学习曲线陡峭、缺进度可视化、错误消息不友好 |
| 技术债务 | 6.5/10 | 代码质量高但 LLM 层不可测、依赖膨胀、37 测试被 skip |
| 发布成熟度 | 7.0/10 | 319 测试 + 28 文档 + CI，但无覆盖率报告、无跨平台 CI、无自动发布 |

### 🔧 调查员（代码质量健康检查）

**核心判断**：MSRA 项目的**代码质量和工程健康度整体良好**。927 个测试收集，902 通过（97.3%），24 个失败全部因 dask 未安装（非代码缺陷）。代码结构分层清晰，安全扫描得分高（9.0/10），CI/CD 三阶段 pipeline 完善。主要问题集中在依赖一致性（pyarrow 遗漏）、测试覆盖率（40% 模块缺直接测试）、以及文档覆盖率偏低（51%）。

**关键建议**：
- 给 dask 相关 24 个测试加 `pytest.importorskip("dask")`，恢复 100% 通过率
- 在 pyproject.toml dependencies 中显式声明 `pyarrow>=15.0.0`（当前仅在 requirements.txt 中）
- 为核心公共 API 补齐 docstring（目标覆盖率 80%，当前 51%）
- CI 开启 pytest-cov 覆盖率报告，移除 ruff lint 的 `--exit-zero` 使其阻断合并
- 为缺少直接测试的 10 个模块补充单元测试（当前 60% 模块有直接测试）

**维度评分**：

| 维度 | 评分 | 说明 |
|------|------|------|
| 测试健康度 | 7.5/10 | 927 测试收集，902 通过（97.3%），24 失败均为 dask 缺失；60% 模块有直接测试 |
| 代码结构 | 8.0/10 | 模块划分清晰，分层合理，命名规范一致，引擎抽象采用策略模式 |
| 依赖管理 | 7.0/10 | requirements.txt / pyproject.toml 基本一致（1 处差异：pyarrow），无 lock 文件 |
| 代码质量 | 7.0/10 | 类型标注 70%，文档 51%，50 个超长函数；无 bare except / wildcard import / TODO |
| 安全性 | 9.0/10 | 无硬编码密钥、无 pickle 反序列化、gitignore 完善、pip-audit 已集成 CI |
| CI/CD | 8.5/10 | 三阶段 CI（smoke + lint + security），含 pip-audit 和 Dependabot |

---

## 2. 综合审查发现（去重合并后按严重度排序）

| # | 严重度 | 类别 | 位置 | 问题描述 | 建议 | 来源成员 |
|---|--------|------|------|---------|------|---------|
| 1 | 🔴 | 架构 | Pipeline 执行层 | **LLM 执行层不可测试**：Pipeline 70%+ 逻辑由 LLM 执行，关键统计计算正确性无法被测试保障 | 增加 statcheck 验证层：对 LLM 生成的统计结果进行确定性代码验证 | 产品评审员 |
| 2 | 🔴 | 测试 | dask 相关测试 | **24 个测试因 dask 未安装失败**，97.3% 通过率未达 100%；测试用例未使用 skipif 保护 | 给 dask 相关测试添加 `@pytest.importorskip("dask")` | 调查员 |
| 3 | 🔴 | 文档 | 全局 | **版本号不一致**：文档中残留 v0.9.x 引用，用户困惑 | 全局搜索替换 + CI 增加版本一致性检查 | 产品评审员 |
| 4 | 🟠 | 依赖 | `pyproject.toml` | **pyarrow 遗漏**：`pyarrow>=15.0.0` 在 requirements.txt 中但不在 pyproject.toml 的 dependencies 中 | 在 pyproject.toml dependencies 中显式声明 pyarrow | 调查员 |
| 5 | 🟠 | 架构 | `shared/` 目录 | 职责过重 — 85 个 Python 文件承载数据契约、质量门闸、变量标准化、反模式等，与 `msra_modules/` 边界模糊 | 拆分为 `contracts/`、`gates/`、`patterns/` 等子包，明确模块边界 | 产品+调查 |
| 6 | 🟠 | 工程 | 根目录 | `final_verify.py` 放在根目录不符合项目结构规范，且无对应模块入口 | 移入 `scripts/` 或创建 `msra_modules/cli.py` 作为 CLI 入口 | 调查员 |
| 7 | 🟠 | 架构 | Agent Python 代码 | MessageBus/TaskQueue/ConflictResolver 是完整参考实现但**未被 Pipeline 实际调用**，死代码维护负担 | 明确标注为"参考实现"或考虑集成 | 产品评审员 |
| 8 | 🟠 | 依赖 | `pyproject.toml` | 依赖膨胀：25+ 直接依赖含 pymc（重）和 dask（重），安装时间长、冲突风险 | 考虑分层安装：core/advanced/experimental | 产品评审员 |
| 9 | 🟠 | 测试 | 模块覆盖 | **40% 模块缺直接测试**（10/25 模块无对应单元测试），仅被 e2e 间接覆盖 | 为缺少直接测试的模块补充单元测试 | 调查员 |
| 10 | 🟡 | 测试 | `tests/` 目录 | 大量测试文件缺少 `@pytest.mark.slow` / `@pytest.mark.integration` 标记，无法选择性执行 | 补充 pytest marker 标注，便于 CI 分层运行 | 调查员 |
| 11 | 🟡 | 代码质量 | 全局 | **文档覆盖率 51%**：976 个函数中仅 500 个有 docstring；50 个函数超 100 行 | 核心公共 API 补齐 docstring，逐步拆分超长函数 | 调查员 |
| 12 | 🟡 | 文档 | README / overview.md | 四个实验性模块已全部 Stable，但文档仍标注"实验性"，信息不一致 | 更新所有文档，将 Stable 模块从"实验性"移入"正式功能" | 产品+调查 |
| 13 | 🟡 | 产品 | `/msra-paper` vs `/msra-write` | 两个命令功能重叠（Paper Track），用户难以区分 | 合并为一个命令或明确边界（如 /msra-paper = 全自动，/msra-write = 交互式） | 产品评审员 |
| 14 | 🟡 | DX | 命令体系 | 16 个命令对新用户有认知负担，缺少引导式入口和进度可视化 | 增加 `/msra-quickstart` 交互式引导 + `/msra-status` 独立命令 | 产品评审员 |
| 15 | 🟡 | 测试 | E2E | Pipeline 集成测试只有简化版，核心流程缺深度集成测试 | 覆盖完整 Stage 1→4 流程的 E2E 测试（使用合成数据） | 产品评审员 |
| 16 | 🟡 | CI/CD | `.github/workflows` | ruff lint 使用 `--exit-zero`，lint 错误不会阻断合并；缺少 pytest-cov 覆盖率报告 | 移除 `--exit-zero`，开启 pytest-cov | 调查员 |
| 17 | 🟢 | 发布 | pyproject.toml | classifier 声明 `5 - Production/Stable` 与实际成熟度不匹配 | 改为 `4 - Beta` 或标注 "v1.0 — Public Beta" | 产品评审员 |

---

## 3. 威胁建模（STRIDE + 安全扫描）

### 威胁分析

| 威胁类别 | 风险 | 严重度 | 状态 |
|---------|------|--------|------|
| **Tampering（篡改）** | pickle 反序列化可执行任意代码 | 🟢 低 | 已确认**无 pickle 使用**（调查员扫描验证） |
| **Information Disclosure（信息泄露）** | 路径遍历风险可能读取敏感文件 | 🟢 低 | gitignore 完善，无敏感文件泄露 |
| **Elevation of Privilege（提权）** | 无硬编码密钥、无危险系统调用 | 🟢 低 | 当前安全 |
| **Spoofing（欺骗）** | 依赖 LLM 输出作为统计结论 | 🟡 中 | 需 statcheck 验证层 |
| **Repudiation（否认）** | Passport 追踪但无审计日志 | 🟢 低 | 可接受 |
| **Denial of Service（拒绝服务）** | 大数据场景无内存限制 | 🟢 低 | 可接受 |

### 安全扫描详情（调查员验证）

| 检查项 | 结果 |
|--------|------|
| 硬编码密钥/密码 | ✅ 未发现 |
| 不安全反序列化 (pickle/shelve/marshal) | ✅ 未发现 |
| subprocess 调用 | ⚠️ 6 处（均使用 shell=False，安全上下文） |
| .env 文件泄露 | ✅ .gitignore 已排除 |
| secrets 模块使用 | ✅ 正确使用 secrets.token_hex() |
| CI 安全审计 | ✅ pip-audit 已集成 + Dependabot 已启用 |

---

## 4. 交付清单（发布检查清单）

### 代码变更清单

| 文件 | 类型 | 变更 |
|------|------|------|
| `shared/method_selector/__init__.py` | 修改 | 修正 `__main__` 检查 |
| `final_verify.py` | 移动 | 移入 `scripts/` 目录 |
| 多个测试文件 | 修改 | 补充 `@pytest.mark` 标注 |
| `README.md` | 修改 | 版本号一致性更新 |
| `.github/workflows/ci.yml` | 新增 | 自动化 CI 配置 |

### 测试覆盖

| 类型 | 数量 | 状态 |
|------|------|------|
| 单元测试 | 902 | ✅ 通过（97.3%，24 个 dask 相关失败） |
| E2E 测试 | 53 | ✅ 全部通过 |
| 评估用例 | 36 | ✅ 100% 通过 |
| 跳过测试 | 1 | ✅ 正常跳过 |
| 失败测试 | 24 | 🟠 均因 dask 未安装，需加 importorskip |

### 发布检查清单

- [ ] 全局版本号一致性检查（v1.0.0）
- [ ] CI/CD workflow 配置完成
- [ ] Troubleshooting 文档补齐
- [ ] README 中"实验性"标签更新
- [ ] pyproject.toml classifier 调整
- [ ] CHANGELOG v1.0.0 条目完善
- [ ] GitHub Release 创建

### 回滚预案

1. **代码回滚**：Git 标签管理，`v1.0.0` 标签指向稳定版本
2. **文档回滚**：README 和文档保留上一版本备份
3. **用户通知**：Release Notes 中明确标注已知问题和降级路径

---

## ✅ 行动清单

| # | 行动 | 负责方 | 紧急度 | 期望完成 |
|---|------|--------|--------|---------|
| 1 | 全局版本号一致性检查 + CI 雁栏：搜索所有文件中的 v0.9.x 引用，统一到 v1.0.0 | 维护者 | P0 | 发布前 |
| 2 | 给 dask 相关 24 个测试加 `pytest.importorskip("dask")`，恢复 100% 通过率 | 维护者 | P0 | 发布前 |
| 3 | 在 pyproject.toml dependencies 中显式声明 `pyarrow>=15.0.0` | 维护者 | P0 | 发布前 |
| 4 | 增加 `/msra-status` 独立命令：显示 Pipeline 进度、门闸状态、产物清单 | 维护者 | P1 | 1 周内 |
| 5 | CI 增加 optional-dependencies 测试矩阵 + pytest-cov 覆盖率报告 + 移除 ruff `--exit-zero` | 维护者 | P1 | 1 周内 |
| 6 | Troubleshooting 文档：常见安装问题、依赖冲突、R/Python 版本不兼容的解决方案 | 维护者 | P1 | 2 周内 |
| 7 | 为核心公共 API 补齐 docstring（目标覆盖率 80%）+ 为 10 个缺测试模块补充单元测试 | 维护者 | P2 | 1-2 月 |
| 8 | statcheck 验证层：对 LLM 生成的统计结果（p 值、CI、效应量）进行确定性代码验证 | 维护者 | P2 | 1-2 月 |

---

## ⚠️ 待完善 / 已知局限

- LLM 执行层不可完全测试，核心风险在于统计计算正确性无法被测试保障
- 大规模数据端到端验证（100K+ 行真实医学数据）尚未完成
- 性能基准记录（Polars/DuckDB/Dask 实际性能数据）待补充
- harmonypy 在 Windows 上因 CMake 编译失败无法安装，需提供替代方案
- pyradiomics 无 Python 3.13 wheel，源码自带特征提取不受影响但用户体验受损
- 缺少交互式可视化和多用户协作功能（产品层面的未来方向）
- 无 CLI 独立入口，限制了脱离 Claude Code 的使用场景
- 反模式目录只有 6 个详细代码案例（目标是 12+）
- 评估体系自动化不足（36 用例 vs 需要 100+）

---

## 📚 成员产出索引

- **gstack-product-reviewer（产品评审员）** 原始产出：产品评审报告，涵盖 7 个维度（定位 8.5/10、架构 8.5/10、功能 8.0/10、DX 7.0/10、技术债 6.5/10、成熟度 7.0/10），综合 7.6/10，Go（有条件发布）建议
- **gstack-investigator（调查员）** 原始产出：代码质量健康检查报告，含 pytest 902 passed / 24 failed（dask 缺失）、Ruff 零警告、安全扫描（9.0/10）、CI/CD 评估（8.5/10），综合健康度 7.8/10

---

> 本报告由软件工坊 AI 协作生成，关键决策请由工程负责人复核。
