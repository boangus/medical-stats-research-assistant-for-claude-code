# 00_config.R
# 配置脚本 - 加载包和设置全局参数
# 这是分析项目的起点，运行其他脚本前请先运行此脚本

rm(list = ls())

# 包管理 ------------------------------------------------------------
if (!require("pacman")) install.packages("pacman")
library(pacman)

# 加载常用包 --------------------------------------------------------
p_load(
  # 数据处理
  tidyverse,      # dplyr, ggplot2, readr 等
  readxl,         # Excel 文件读取
  haven,          # SAS/SPSS/Stata 文件
  
  # 统计分析
  survival,       # 生存分析
  survminer,      # 生存曲线可视化
  gtsummary,      # 统计表格
  flextable,      # 表格输出到 Word
  officer,        # Office 文档操作
  
  # 倾向性评分/因果推断
  survey,         # 复杂抽样/加权分析
  WeightIt,       # 倾向性评分加权
  MatchIt,        # 倾向性评分匹配
  cobalt,         # 协变量平衡检查
  
  # 可视化
  ggplot2,        # 基础可视化
  ggsci,          # 期刊配色方案
  cowplot,        # 组合图形
  patchwork,      # 图形拼接
  
  # 其他实用工具
  mice,           # 多重插补
  car,            # 回归诊断
  caret,          # 机器学习工具
  tableone        # 基线表
)

cat("[00_config] 所有包加载完成\n")

# 路径设置 ----------------------------------------------------------
base_dir <- getwd()
input_dir <- file.path(base_dir, "input")
script_dir <- file.path(base_dir, "script")
load_dir <- file.path(base_dir, "load")
outcome_dir <- file.path(base_dir, "outcome")

# 创建目录（如果不存在）--------------------------------------------
dirs <- c(
  load_dir,
  outcome_dir,
  file.path(outcome_dir, "tables"),
  file.path(outcome_dir, "figures"),
  file.path(outcome_dir, "reports"),
  file.path(outcome_dir, "data")
)

for (d in dirs) {
  if (!dir.exists(d)) {
    dir.create(d, recursive = TRUE)
    cat("[00_config] 创建目录:", d, "\n")
  }
}

# 全局配置 ----------------------------------------------------------
set.seed(20250101)  # 设置随机种子确保可重复性
options(scipen = 999)  # 禁用科学计数法
options(digits = 4)    # 设置显示小数位数

# 保存配置 ----------------------------------------------------------
save(
  base_dir, input_dir, script_dir, load_dir, outcome_dir,
  file = file.path(load_dir, "00_config.rda")
)

cat("[00_config] 配置完成，目录结构已初始化\n")
cat("[00_config] 工作目录:", base_dir, "\n")
