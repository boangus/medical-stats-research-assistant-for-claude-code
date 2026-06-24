# MSRA 项目目录清理评估报告

**日期**：2026-06-25
**工作流**：文件清理评估（非标准工作流，按用户需求定制）
**评估范围**：`D:\开发\medical-stats-research-assistant` 全目录
**评估方式**：只读扫描，未删除任何文件

---

## 📌 TL;DR（执行摘要）

- **项目总大小**：53 MB（含 `.git` 7.8 MB），工作区净占 45 MB
- **git 跟踪文件**：814 个（389 .md / 237 .py / 88 .json / 57 .R）
- **可删除冗余**：🔴 严重冗余约 **29 MB**（主要为 Sphinx 构建产物 + Python 缓存 + 未跟踪大 PDF）
- **核心保留**：约 16 MB（源码、Skill 定义、文档、配置、测试）
- **严重度分布**：🔴严重 4 项 / 🟠高 5 项 / 🟡中 6 项 / 🟢低 3 项
- **关键风险**：`skills/pipeline/image/SKILL/1781797150979.pdf`（7.7 MB 未跟踪大文件）+ 3 个内容完全相同的 PNG 已被 git 跟踪

---

## 🎯 核心结论卡片

| 项目 | 内容 |
|------|------|
| 整体评级 | 🟡 有条件通过（工作区存在大量可清理冗余，但不影响核心功能） |
| 阻塞项数量 | 0（均为非阻塞清理项） |
| 可释放空间 | 约 29 MB（删除冗余后工作区可瘦身至 ~16 MB） |
| 建议下一步 | 先清理缓存类（零风险），再处理未跟踪大文件，最后评估边界文件 |

---

## 🔍 分类清单（按严重度排序）

### 🔴 严重冗余（建议立即清理，零风险）

| # | 路径 | 类型 | 大小 | git 跟踪 | 分类理由 |
|---|------|------|------|---------|---------|
| 1 | `docs/sphinx/build/` | 构建产物 | 13 MB | ❌ 未跟踪 | Sphinx 文档构建输出，可由 `sphinx-build` 重新生成。`.gitignore` 第 101 行已排除 |
| 2 | `skills/pipeline/image/SKILL/1781797150979.pdf` | 未跟踪大文件 | 7.7 MB | ❌ 未跟踪 | 命名为时间戳的 PDF，疑似误放的临时文件，未被 git 跟踪，可安全删除 |
| 3 | 所有 `__pycache__/` 目录（34 个） | Python 字节码缓存 | 3.6 MB | ❌ 未跟踪 | 174 个 `.pyc` 文件，Python 自动生成。`.gitignore` 已排除 `__pycache__/` 和 `*.py[cod]` |
| 4 | `tests/healthcare_dataset.csv` | 测试数据 | 8.4 MB | ❌ 未跟踪 | 大型 Kaggle 数据集，`.gitignore` 第 46 行已明确排除 |

### 🟠 高冗余（建议清理，需确认）

| # | 路径 | 类型 | 大小 | git 跟踪 | 分类理由 |
|------|------|------|------|---------|---------|
| 5 | `reports/` | 运行时输出 | 160 KB | ❌ 未跟踪 | 36 个 `monitoring_report_*.html` 监控报告，运行时生成，非核心产物 |
| 6 | `.pytest_cache/` | 测试缓存 | ~小型 | ❌ 未跟踪 | pytest 运行缓存，`.gitignore` 第 42 行已排除 |
| 7 | `.ruff_cache/` | Linter 缓存 | ~小型 | ❌ 未跟踪 | Ruff linter 缓存，可随时重建 |
| 8 | `.test_cache/` | 自定义测试缓存 | 6 KB | ❌ 未跟踪 | `.gitignore` 第 111 行已排除 |
| 9 | `debug.log` | 日志文件 | 4.3 KB | ❌ 未跟踪 | 内容为搜狗输入法渲染日志，与项目无关，`.gitignore` 第 32 行已排除 `*.log` |

### 🟡 中冗余（本地工作文件，按需保留）

| # | 路径 | 类型 | 大小 | git 跟踪 | 分类理由 |
|------|------|------|------|---------|---------|
| 10 | `.msra/` | 运行时缓存 | 4 KB | ❌ 未跟踪 | MSRA 运行时状态，`.gitignore` 第 66 行已排除 |
| 11 | `.msra_cache/` | 运行时缓存 | 0 | ❌ 未跟踪 | 空目录，可删除 |
| 12 | `.sdd/` | 任务跟踪 | 4 KB | ❌ 未跟踪 | SDD 任务跟踪本地文件，`.gitignore` 第 86 行已排除 |
| 13 | `.coverage` | 测试覆盖率 | 52 KB | ❌ 未跟踪 | pytest-cov 生成，`.gitignore` 第 43 行已排除 |
| 14 | `overview.md` | 旧版报告 | 5 KB | ❌ 未跟踪 | v0.9.3 优化报告，已过时（当前 v1.0.0） |
| 15 | `final_verify.py` | 一次性脚本 | 1.8 KB | ❌ 未跟踪 | 一次性验证脚本，非核心工具 |

### 🟢 低冗余（工具数据，保留无害）

| # | 路径 | 类型 | 大小 | git 跟踪 | 分类理由 |
|------|------|------|------|---------|---------|
| 16 | `.workbuddy/` | WorkBuddy 数据 | 81 KB | ❌ 未跟踪 | WorkBuddy 工具数据（automations + memory），`.gitignore` 第 69 行已排除。含记忆文件，建议保留 |
| 17 | `.claude/skills/darwin-skill/results.tsv` | 优化结果 | 小型 | ❌ 未跟踪 | Darwin 优化结果，`.gitignore` 第 63 行已排除 |
| 18 | `evals/gold/results/eval_report_*.json` | 评估结果 | 14 KB | ❌ 未跟踪 | 流水线评估运行结果，`.gitignore` 第 72 行已排除 |

---

## 🏗️ 需用户决策的边界情况

以下文件/目录状态特殊，**不建议自动清理**，需用户确认：

| # | 路径 | 状态 | 问题 | 建议 |
|---|------|------|------|------|
| B1 | `docs/dev/` (33 个文件，512 KB) | ✅ **已强制 git add** | `.gitignore` 第 104 行写了 `docs/dev/`，但实际已被 `git add -f` 强制跟踪（见 memory 记录 commit 7319625） | 若希望公开仓库不含开发文档，应 `git rm --cached -r docs/dev/`；若希望保留，应从 `.gitignore` 移除该行避免矛盾 |
| B2 | `output/` (README.md + phase1-completion-summary.md) | ✅ 已跟踪 | 内容为阶段总结，像是工作产物而非核心代码 | 确认是否需要长期保留；若不需要，`git rm` |
| B3 | `deliverables/engineering-assurance/phase1-optimization-msra-2026-06-24.md` | ✅ 已跟踪 | `.gitignore` 第 109 行写了 `deliverables/`，但此文件已被跟踪 | 与 B1 同类问题，需统一策略 |
| B4 | `references/literature/` (804 KB) | ❌ 未跟踪 | `.gitignore` 第 108 行排除，属个人研究文献 | 保留本地，不上传 |
| B5 | `skills/pipeline/image/SKILL/1781774046143.png` 等 3 个 PNG | ✅ 已跟踪 | 3 个文件 md5 完全相同（`293f450f...`），内容重复 | 保留 1 个，删除其余 2 个，或确认是否本应不同 |
| B6 | `OPTIMIZATION_PLAN.md` (26 KB) | ❌ 未跟踪 | `.gitignore` 第 79 行排除，本地工作文件 | 保留本地即可 |

---

## ✅ 核心保留文件清单（Claude Code Skill 项目必需）

### 项目元配置（根目录）

| 文件 | 用途 | 必要性 |
|------|------|--------|
| `manifest.json` | Claude Code 插件清单（定义 16 个命令入口） | 🔴 必需 |
| `pyproject.toml` | Python 项目配置（依赖、构建、工具配置） | 🔴 必需 |
| `.gitignore` / `.gitattributes` | Git 忽略规则 / 行尾规范 | 🔴 必需 |
| `README.md` / `CHANGELOG.md` / `CONTRIBUTING.md` / `SECURITY.md` / `LICENSE` | 项目文档与许可证 | 🔴 必需 |
| `requirements.txt` / `requirements-dev.txt` | 依赖锁定 | 🔴 必需 |
| `pytest.ini` | 测试配置 | 🔴 必需 |
| `icon.png` | 插件图标 | 🟠 建议 |
| `config.local.yaml.example` | 本地配置示例 | 🟠 建议 |
| `install.sh` / `install.ps1` / `uninstall.sh` / `uninstall.ps1` | 安装卸载脚本 | 🔴 必需 |
| `push-public.sh` | 发布辅助脚本 | 🟢 可选 |

### Claude Code 插件配置

| 路径 | 用途 | 必要性 |
|------|------|--------|
| `.claude/CLAUDE.md` | Claude Code 项目指令 | 🔴 必需 |
| `.claude-plugin/marketplace.json` | 插件市场元数据 | 🔴 必需 |
| `.claude-plugin/plugin.json` | 插件配置 | 🔴 必需 |

### CI/CD 与协作

| 路径 | 用途 | 必要性 |
|------|------|--------|
| `.github/workflows/ci.yml` | GitHub Actions CI 流水线 | 🔴 必需 |
| `.github/dependabot.yml` | 依赖更新机器人 | 🟠 建议 |

### 源代码（Python 模块）

| 路径 | 用途 | 大小 | 必要性 |
|------|------|------|--------|
| `msra_modules/` | 核心 Python 模块（含 4 个实验性子模块） | 835 KB | 🔴 必需 |
| `shared/` | 共享资源库（27 个子模块：统计方法、模板、质量门闸等） | 5.3 MB | 🔴 必需 |
| `agents/` | Agent 框架（core + implementations + 定义文档） | 580 KB | 🔴 必需 |
| `scripts/` | 辅助脚本（评估、迁移、检查等） | 186 KB | 🔴 必需 |
| `resources/external/` | 外部集成资源 | 小型 | 🟠 建议 |

### Skill 与命令定义

| 路径 | 用途 | 大小 | 必要性 |
|------|------|------|--------|
| `skills/` | 14 个 Skill 定义（pipeline、data-prep、analysis 等） | 11 MB | 🔴 必需 |
| `commands/` | 13 个命令定义（/msra-* 系列） | 50 KB | 🔴 必需 |
| `evals/gold/` | 评估金标准数据（end-to-end / method-selection / pipeline） | 192 KB | 🔴 必需 |

### 文档（已跟踪部分）

| 路径 | 用途 | 必要性 |
|------|------|--------|
| `docs/system_design.md` / `docs/system_design_cross_domain.md` | 架构设计 | 🔴 必需 |
| `docs/api/` / `docs/user_guide/` / `docs/prd/` | API 参考 / 用户教程 / PRD | 🔴 必需 |
| `docs/troubleshooting.md` / `docs/release-workflow.md` 等 | 运维文档 | 🟠 建议 |

### 测试

| 路径 | 用途 | 大小 | 必要性 |
|------|------|------|--------|
| `tests/test_*/` | 单元测试（5 个模块） | ~1 MB | 🔴 必需 |
| `tests/e2e/` | 端到端测试（53 个，10 场景） | 324 KB | 🔴 必需 |
| `tests/msra_test_data.csv` | 测试数据 | 100 KB | 🔴 必需 |
| `tests/msra_test_data_dictionary.md` | 数据字典 | 4.6 KB | 🔴 必需 |

### 示例

| 路径 | 用途 | 必要性 |
|------|------|--------|
| `examples/example_workflow.md` | 工作流示例 | 🟠 建议 |
| `examples/*.png` | 演示图片 | 🟢 可选 |

---

## ✅ 行动清单（按优先级排序）

| # | 行动 | 负责角色 | 紧急度 | 预期完成 |
|---|------|---------|--------|---------|
| 1 | 删除 `docs/sphinx/build/`（13 MB 构建产物，可重建） | 开发者 | P0 | 立即 |
| 2 | 删除未跟踪大文件 `skills/pipeline/image/SKILL/1781797150979.pdf`（7.7 MB，疑似误放） | 开发者 | P0 | 立即 |
| 3 | 清理所有 `__pycache__/` 目录：`find . -type d -name __pycache__ -exec rm -rf {} +` | 开发者 | P1 | 本周 |
| 4 | 清理 `reports/`（36 个运行时 HTML）、`debug.log`、`.coverage`、各类 `*_cache/` 目录 | 开发者 | P1 | 本周 |
| 5 | 删除空目录 `.msra_cache/` 和过时文件 `overview.md`、`final_verify.py` | 开发者 | P2 | 本月 |
| 6 | 决策 `docs/dev/` 策略：要么 `git rm --cached -r docs/dev/` 落实 `.gitignore`，要么移除该行 | 项目负责人 | P2 | 本月 |
| 7 | 处理 3 个重复 PNG（`skills/pipeline/image/SKILL/*.png`），保留 1 个 | 开发者 | P3 | 下个版本 |
| 8 | 统一 `output/` 与 `deliverables/` 的 git 跟踪策略（当前部分跟踪、部分排除） | 项目负责人 | P3 | 下个版本 |

---

## ⚠️ 待完善 / 已知局限

- 本次评估为**只读扫描**，未执行任何删除操作。所有清理需用户确认后执行
- `.git` 目录（7.8 MB）未纳入清理范围，如需瘦身可考虑 `git gc --aggressive`
- 未深入检查 `shared/templates/` 内部是否有重复模板（该目录 1.9 MB，含大量 .R/.py 模板）
- `skills/pipeline/` 占 8 MB（含已被跟踪的 3 个 PNG + 未跟踪的 PDF），清理 PDF 后将降至约 300 KB
- 未评估各 Skill 内部 `phases/` 子目录的合理性（v1.0.1 瘦身重构产物）

---

## 📚 数据来源 & 成员产出索引

- 目录扫描：`du -sh` / `find` / `ls -la` / `git ls-files`
- .gitignore 规则：`D:\开发\medical-stats-research-assistant\.gitignore`（113 行）
- 项目清单：`manifest.json`（16 个命令定义）
- 依赖配置：`pyproject.toml`（核心 + 4 个可选依赖组）
- 历史记忆：`.workbuddy/memory/MEMORY.md`（docs/dev 曾用 `git add -f` 强制添加，commit 7319625）

---

> 本报告由工程保障团队主理人基于只读目录扫描生成，所有清理操作请由人类开发者确认后执行。
