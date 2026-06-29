# 临床分析可复现性规范 (v1.0)

## 为什么需要此规范

临床研究分析的可复现性是循证医学的基石。当审稿人、监管机构或其他研究者试图验证分析结果时，他们需要知道：

- 使用了什么版本的分析代码？
- 数据经历了哪些处理步骤？
- 运行环境是什么？
- 随机化过程是否可追溯？

MSRA Pipeline 产出的分析结果必须携带完整的可复现性信息——不是为了完美重放，而是为了诚实记录。

> **核心原则**: 本规范提供**配置文档**以支持**事后调查**，而非**确定性重放保证**。LLM 辅助的分析在不同运行中可能产生细微差异，这是已知限制。

---

## 什么不是可复现性（必须先读）

1. **LLM 输出不可逐字节复现。** 即使温度设为 0，模型权重可能在两次调用间变化。`model.weight_stable: false` 明确承认这一点。`model.id` 是标识符，不是权重哈希。

2. **外部 API 查询记录为协议版本，而非快照。** PubMed/NCBI API 每天可能返回不同的元数据。我们记录查询逻辑的版本，而非响应的快照。

3. **运行时动态修改未被捕获。** 代码中的条件分支、用户提供的额外参数、运行时的配置调整均未反映在哈希中。这是已知的不精确性。

4. **随机性声明是强制的。** 省略它会使可复现性声明隐含地不诚实。每个生成的护照必须逐字包含此声明。

---

## 四大支柱

### 支柱 1: 代码版本管理 (Code Versioning)

**要求**: 所有分析代码必须使用版本控制，并记录运行时的代码状态。

**Git 版本控制**:
```
code_version:
  git_repo: "https://github.com/[org]/[repo]"
  git_commit: "sha256:..."           # 运行时的 commit hash
  git_branch: "main"                 # 分支名称
  git_dirty: false                   # 是否有未提交的修改
  commit_message: "..."              # 提交信息
```

**依赖管理**:
```
dependencies:
  tool: "renv"                       # 或 pip/conda/requirements.txt
  lockfile_hash: "sha256:..."        # lockfile 的哈希值
  r_version: "4.3.2"                 # R 版本（如适用）
  python_version: "3.11.5"           # Python 版本（如适用）
  key_packages:                      # 关键分析包及其版本
    - name: "survival"
      version: "3.5-7"
    - name: "lme4"
      version: "1.1-34"
```

**renv 快照**（R 项目）:
- 使用 `renv::snapshot()` 创建可复现的库快照
- `renv.lock` 文件必须包含在版本控制中
- 运行时 `renv::restore()` 可重建完全相同的库环境

**requirements.txt**（Python 项目）:
- 使用 `pip freeze > requirements.txt` 生成精确版本
- 或使用 `pip-tools` / `poetry` 管理精确依赖

---

### 支柱 2: 数据溯源 (Data Provenance)

**要求**: 记录数据从原始状态到分析就绪状态的完整处理链。

**CDISC 标准追踪**（如适用）:
```
data_provenance:
  source_type: "CDISC"               # 或 "local" / "database" / "API"
  source_identifier: "SDTM-datasets-v1.0"
  data_dictionary_version: "2024-01"
  
  processing_steps:
    - step: 1
      action: "数据导入"
      input: "原始数据/clinical_data.sas7bdat"
      output: "processed/step1_import.rds"
      timestamp: "2026-06-21T10:30:00Z"
      script: "scripts/01_data_import.R"
      
    - step: 2
      action: "变量重编码"
      input: "processed/step1_import.rds"
      output: "processed/step2_recode.rds"
      timestamp: "2026-06-21T11:15:00Z"
      script: "scripts/02_recode_variables.R"
      changes: "年龄分组重编码为 4 组；BMI 分类按 WHO 标准"
      
    - step: 3
      action: "缺失值处理"
      input: "processed/step2_recode.rds"
      output: "processed/step3_impute.rds"
      timestamp: "2026-06-21T14:00:00Z"
      script: "scripts/03_missing_data.R"
      method: "多重填补 (m=20, PMM, seed=12345)"
      
    - step: 4
      action: "分析数据集构建"
      input: "processed/step3_impute.rds"
      output: "data/analysis_dataset.rds"
      timestamp: "2026-06-21T15:30:00Z"
      script: "scripts/04_analysis_dataset.R"
```

**数据哈希清单**:
```
data_manifest:
  - filename: "analysis_dataset.rds"
    sha256: "sha256:..."
    rows: 1234
    columns: 45
    created_by: "scripts/04_analysis_dataset.R"
  - filename: "analysis_dataset.csv"
    sha256: "sha256:..."
    rows: 1234
    columns: 45
    created_by: "scripts/04_analysis_dataset.R"
```

**数据处理链可视化**:
```
原始数据 → [导入] → [重编码] → [缺失值处理] → [分析数据集] → [分析] → [结果]
   ↓           ↓           ↓              ↓              ↓          ↓
  哈希       哈希        哈希           哈希           哈希       哈希
```

---

### 支柱 3: 环境捕获 (Environment Capture)

**要求**: 记录分析运行时的完整计算环境。

**Docker/Singularity 容器**:
```
environment:
  container:
    type: "docker"                   # 或 "singularity"
    image: "[registry]/[image]:[tag]"
    image_hash: "sha256:..."
    base_image: "rocker/verse:4.3.2"
    
  system:
    os: "Ubuntu 22.04"
    architecture: "x86_64"
    cpu_model: "Intel Xeon E5-2680 v4"
    ram_gb: 64
    gpu: "NVIDIA A100 (if applicable)"
    
  software:
    r_version: "4.3.2"
    python_version: "3.11.5"
    stan_version: "2.33.1"           # 如果使用 Stan
    jags_version: "4.3.4"            # 如果使用 JAGS
    
  key_packages:
    - name: "survival"
      version: "3.5-7"
      source: "CRAN"
    - name: "lme4"
      version: "1.1-34"
      source: "CRAN"
    - name: "brms"
      version: "2.21.0"
      source: "CRAN"
```

**环境哈希**:
- Docker 镜像的 `sha256` 哈希
- `renv.lock` 或 `requirements.txt` 的哈希
- 关键包版本的清单

**为什么不依赖系统包管理器**:
- `apt`/`yum` 的包版本可能在不同时间点不同
- Docker 镜像提供完全一致的环境
- Singularity 适用于 HPC 集群环境

---

### 支柱 4: 随机种子管理 (Random Seed Management)

**要求**: 记录所有涉及随机性的操作的种子，确保分析可精确重放。

**R 随机种子**:
```
random_seeds:
  r_main_seed: 12345                # set.seed(12345)
  r_state: "Mersenne-Twister"       # RNG 算法
  r_normal_kind: "NORM-INV"         # 正态随机数生成方式
  
  per_analysis:
    - analysis: "多重填补"
      seed: 12345
      package: "mice"
      method: "PMM"
      m: 20
      
    - analysis: "Bootstrap"
      seed: 67890
      package: "boot"
      n_replications: 1000
      
    - analysis: "贝叶斯 MCMC"
      seed: 11111
      package: "brms"
      chains: 4
      iter: 4000
      warmup: 1000
```

**Python 随机种子**:
```
random_seeds:
  python_random: 42                  # random.seed(42)
  numpy_random: 42                   # np.random.seed(42)
  torch_random: 42                   # torch.manual_seed(42)
  tensorflow_random: 42              # tf.random.set_seed(42)
  cuda_deterministic: true           # torch.backends.cudnn.deterministic = True
```

**种子管理最佳实践**:
- 每个分析步骤使用不同的种子（避免伪相关）
- 记录种子的派生方式（如 `seed = base_seed + analysis_index`）
- 多重填补使用递增种子序列（`12345, 12346, ..., 12364`）
- 贝叶斯分析使用 `chains` 个不同的种子

---

## 完整的可复现性护照

将四大支柱整合为一个完整的可复现性护照：

```yaml
reproducibility_passport:
  schema_version: "1.0"
  stochasticity_declaration: "LLM 辅助的分析不可逐字节复现。本护照记录配置以支持事后调查，而非确定性重放保证。"
  pipeline_version: "MSRA v0.9.0"
  
  code:
    git_repo: "..."
    git_commit: "sha256:..."
    git_branch: "main"
    dependencies_hash: "sha256:..."
    
  data:
    source_type: "CDISC"
    processing_steps: [...]
    manifest_hash: "sha256:..."
    
  environment:
    container_image: "..."
    container_hash: "sha256:..."
    os: "Ubuntu 22.04"
    r_version: "4.3.2"
    
  random_seeds:
    main_seed: 12345
    per_analysis: [...]
    
  timestamp: "2026-06-21T15:30:00Z"
```

---

## 红旗：审查可复现性护照时的警告信号

| 信号 | 含义 | 行动 |
|------|------|------|
| `stochasticity_declaration` 被修改 | 作者暗示比实际情况更强的可复现性保证 | 仔细审查整份护照 |
| 空的或占位符哈希（`"sha256:"` 无内容） | 生成器损坏或作者填了占位符 | 要求完整哈希 |
| `git_dirty: true` | 有未提交的修改在运行时被使用 | 这些修改未被追踪，结果可能不可复现 |
| 缺失 `data_manifest` | 数据处理链未被完整记录 | 无法验证数据处理步骤 |
| 随机种子未记录 | 分析中的随机性不可追溯 | 无法精确重放分析 |
| Docker 镜像无哈希 | 镜像可能已被更新 | 无法重建相同环境 |

---

## 与 MSRA Pipeline 的集成

| 阶段 | 可复现性动作 |
|------|-------------|
| Stage 1 (数据准备) | 记录数据来源和处理步骤；创建数据哈希清单 |
| Stage 2 (分析计划) | 预声明分析代码仓库和随机种子策略 |
| Stage 3 (分析执行) | 运行时捕获环境信息；记录每个分析步骤的种子 |
| Stage 4 (统计报告) | 生成完整的可复现性护照；嵌入稿件的附录中 |

---

## 生成指南（面向 Agent 作者）

1. **代码哈希**: 在代码加载时计算 `skill_md_hash` 和 `agents_bundle_hash`
2. **数据清单**: 列出所有会话文件及其 SHA-256 摘要，按文件名排序，然后哈希 JSON 序列化
3. **随机种子**: 从 `set.seed()` 调用中提取，或在分析开始时初始化并记录
4. **环境信息**: 从运行时系统中提取（`R.version.string`、`Sys.info()`、Docker 标签）
5. **时间戳**: ISO 8601 格式，UTC 时区
6. **随机性声明**: 必须逐字包含，不可修改或缩写

---

## 未来演进

- v1.1: 支持 `data_snapshot_available: true` — 当分析数据集被缓存时，快照路径出现在护照中
- v2.0: 支持模型权重签名 — 当 LLM 提供商提供权重稳定性签名时，`model.weight_stable: true` 变得有意义
- v2.1: 支持分析流程图（DAG）自动验证 — 确保数据处理链的完整性
- 永远不: 逐字节重放保证 — LLM 不像传统软件那样工作，没有版本号能改变这一事实

---

## 参考标准

- ICMJE: 建议作者在稿件中提供分析代码和数据的可及性声明
- TOP Guidelines: 透明性与开放性促进准则（要求代码和数据共享）
- EQUATOR Network: 报告规范联盟（要求分析方法的完整描述）
- FDA: 美国食品药品监督管理局要求临床试验数据的完整溯源链
- CDISC: 临床数据交换标准协会（数据标准）
- CONSORT: 随机对照试验报告统一标准（要求报告随机化和分析方法的完整细节）
