# 结构化分析工作流模板

基于 input/script/outcome 目录分离方法论的标准化医学统计分析项目结构。

---

## 目录结构

```
project/
├── input/                    # 输入数据（原始数据，只读）
│   ├── raw_data.csv         # 原始数据文件
│   ├── data_dictionary.xlsx # 数据字典
│   └── inclusion_criteria.md # 纳入排除标准
│
├── script/                   # 分析脚本（按执行顺序编号）
│   ├── 00_config.R          # 全局配置：包加载、路径设置
│   ├── 01_data_extract.R    # 数据提取与初步筛选
│   ├── 02_var_define.R      # 变量定义：标签、分组、协变量
│   ├── 03_baseline.R        # 基线特征分析
│   ├── 04_iptw_matching.R   # 倾向性评分/IPTW
│   ├── 05_survival_analysis.R # 生存分析
│   ├── 06_subgroup_analysis.R # 亚组分析
│   └── 07_sensitivity.R     # 敏感性分析
│
├── load/                     # 中间数据（各步骤缓存，可复用）
│   ├── 01_extracted.rda     # 提取后的数据
│   ├── 02_var_defined.rda   # 变量定义后的数据
│   ├── 03_iptw.rda          # IPTW加权后的数据
│   └── config.rda           # 配置对象
│
└── outcome/                  # 最终结果（图表、表格、报告）
    ├── tables/              # 表格输出
    ├── figures/             # 图表输出
    ├── reports/             # 报告文档
    └── data/                # 最终数据集（去标识化后）
```

---

## 核心原则

### 1. 输入只读原则
- `input/` 目录中的文件**永不修改**
- 所有数据清洗、转换都在 `script/` 中完成，输出到 `load/` 或 `outcome/`
- 保留原始数据的可追溯性

### 2. 脚本编号化
- 使用 `00-`, `01-`, `02-` 前缀表示执行顺序
- 编号规则：
  - `00_`：配置和定义（config, var_define）
  - `01-09`：数据准备阶段（提取、清洗、转换）
  - `10-19`：分析阶段（基线、匹配、回归）
  - `20-29`：高级分析（亚组、敏感性、交互作用）
  - `90-99`：报告生成

### 3. 中间数据缓存
- 每个主要步骤后保存 `.rda` 文件到 `load/`
- 好处：
  - 避免重复运行耗时操作
  - 便于调试和修改后续步骤
  - 支持从任意步骤恢复

### 4. 变量集中定义
在 `02_var_define.R` 中统一定义：
```r
# 变量标签（用于表格）
var_labels <- list(
  Age = "Age (years)",
  Sex = "Sex"
)

# 分类变量值标签
value_list <- list(
  Sex = list("0" = "Female", "1" = "Male")
)

# 协变量列表（用于多变量调整）
covariates <- c("Age", "Sex", "BMI")

# 亚组变量列表
subgroup_vars <- c("Age_group", "Sex")

# 表格展示变量
tbl_vars <- c("Age", "Sex", "BMI")
```

### 5. 输入输出声明
每个脚本顶部必须声明：
```r
# 输入输出声明 --------------------------------------------------
input_file <- "load/01_extracted.rda"   # 输入文件路径
output_dir <- "outcome/"                 # 输出目录
load_dir <- "load/"                      # 中间数据目录

# 创建输出目录（如果不存在）
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
```

---

## 脚本模板

### 00_config.R
```r
# 配置脚本 - 加载包和设置全局参数
rm(list = ls())

# 包管理
if (!require("pacman")) install.packages("pacman")
library(pacman)

# 加载常用包
p_load(
  tidyverse,      # 数据处理
  survival,       # 生存分析
  survminer,      # 生存曲线
  gtsummary,      # 统计表格
  flextable,      # 表格输出
  survey,         # 复杂抽样/加权
  WeightIt,       # 倾向性评分
  cobalt,         # 协变量平衡检查
  ggplot2,        # 可视化
  ggsci           # 期刊配色
)

# 路径设置
base_dir <- getwd()
input_dir <- file.path(base_dir, "input")
load_dir <- file.path(base_dir, "load")
outcome_dir <- file.path(base_dir, "outcome")

# 创建目录
dirs <- c(load_dir, outcome_dir, 
          file.path(outcome_dir, "tables"),
          file.path(outcome_dir, "figures"),
          file.path(outcome_dir, "reports"))
for (d in dirs) {
  if (!dir.exists(d)) dir.create(d, recursive = TRUE)
}

# 保存配置
save(base_dir, input_dir, load_dir, outcome_dir, 
     file = file.path(load_dir, "00_config.rda"))
```

### 标准分析脚本结构
```r
# XX_描述.R
# 目的：简要描述本脚本的功能

rm(list = ls())

# 1. 加载配置和依赖 ---------------------------------------------
load("load/00_config.rda")
load("load/XX_previous_step.rda")  # 加载前一步数据

# 2. 输入输出声明 -----------------------------------------------
input_file <- "load/XX_previous_step.rda"
output_file <- "outcome/XX_result.docx"

# 3. 数据处理/分析 -----------------------------------------------
# ... 分析代码 ...

# 4. 保存中间数据 ------------------------------------------------
save(analysis_result, file = "load/XX_current_step.rda")

# 5. 输出结果 ----------------------------------------------------
# 表格、图表、报告
```

---

## 与 MSRA Pipeline 的整合

此工作流模板可与 MSRA 的 4 阶段流水线结合：

| MSRA 阶段 | 对应脚本 | 输出到 |
|----------|---------|--------|
| Stage 1: 数据准备 | `01_data_extract.R`, `02_var_define.R` | `load/` |
| Stage 1.5: 质量门闸 | 质量检查脚本 | `outcome/reports/quality_report.md` |
| Stage 2: 分析计划 | SAP 文档 | `outcome/reports/SAP.md` |
| Stage 3: 分析执行 | `03_baseline.R` - `07_sensitivity.R` | `outcome/tables/`, `outcome/figures/` |
| Stage 4: 报告生成 | `90_generate_report.R` | `outcome/reports/` |

---

## 最佳实践

1. **版本控制**：将 `script/` 纳入 Git，忽略 `load/`（大文件）
2. **文档化**：每个脚本头部包含目的、输入、输出说明
3. **可重复性**：使用 `set.seed()` 确保随机过程可重复
4. **错误处理**：关键步骤添加验证检查
5. **命名规范**：
   - 文件：`小写_下划线.R`
   - 变量：`snake_case`
   - 函数：`verb_noun()` 格式
