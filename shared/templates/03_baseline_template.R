# 03_baseline.R
# 基线特征分析脚本
# 输入: load/01_extracted.rda, load/02_var_defined.rda
# 输出: outcome/tables/Table1_Baseline.docx

rm(list = ls())

# 1. 加载配置和依赖 -------------------------------------------------
load("load/00_config.rda")
load("load/01_extracted.rda")
load("load/02_var_defined.rda")

cat("[03_baseline] 开始基线特征分析\n")

# 2. 输入输出声明 ---------------------------------------------------
input_file <- "load/01_extracted.rda"
output_file <- file.path(outcome_dir, "tables", "Table1_Baseline.docx")

# 3. 正态分布检验函数 -----------------------------------------------
check_normality <- function(data, continuous_vars, alpha = 0.05) {
  normal_vars <- character(0)
  
  for (var in continuous_vars) {
    if (var %in% names(data)) {
      var_data <- data[[var]]
      var_data <- var_data[!is.na(var_data)]
      
      # 样本量 3-5000 使用 Shapiro-Wilk 检验
      if (length(var_data) > 3 && length(var_data) <= 5000) {
        test_result <- shapiro.test(var_data)
        if (test_result$p.value > alpha) {
          normal_vars <- c(normal_vars, var)
        }
      } else if (length(var_data) > 5000) {
        # 大样本使用 KS 检验
        sample_mean <- mean(var_data)
        sample_sd <- sd(var_data)
        test_result <- ks.test(var_data, "pnorm", mean = sample_mean, sd = sample_sd)
        if (test_result$p.value > alpha) {
          normal_vars <- c(normal_vars, var)
        }
      }
    }
  }
  
  return(normal_vars)
}

# 4. 数据预处理 -----------------------------------------------------
# 应用变量标签（如果数据中有对应变量）
for (var in names(var_labels)) {
  if (var %in% names(data_select)) {
    attr(data_select[[var]], "label") <- var_labels[[var]]
  }
}

# 5. 正态分布检验 ---------------------------------------------------
normal_vars <- check_normality(data_select, continuous_vars)
cat("[03_baseline] 符合正态分布的变量:", paste(normal_vars, collapse = ", "), "\n")

# 6. 创建统计表示方式列表 -------------------------------------------
statistic_list <- list()

# 分类变量：计数和百分比
statistic_list["all_categorical()"] <- "{n} ({p}%)"

# 连续变量默认：中位数和四分位数
statistic_list["all_continuous()"] <- "{median} [{p25}, {p75}]"

# 正态分布变量：均值和标准差
if (length(normal_vars) > 0) {
  for (var in normal_vars) {
    statistic_list[[var]] <- "{mean} ({sd})"
  }
}

# 7. 生成基线表 -----------------------------------------------------
# 检查是否有分组变量
if (treatment_var %in% names(data_select)) {
  # 有分组变量的基线表
  tbl <- tbl_summary(
    data = data_select,
    by = all_of(treatment_var),
    include = all_of(tbl_vars),
    label = var_labels,
    statistic = statistic_list,
    type = list(
      all_continuous() ~ "continuous",
      all_categorical() ~ "categorical"
    ),
    digits = list(all_continuous() ~ 2, all_categorical() ~ 0),
    missing = "no"
  ) %>%
    add_overall() %>%
    add_difference(
      test = list(
        all_continuous() ~ "cohens_d",
        all_categorical() ~ "smd"
      )
    ) %>%
    modify_header(
      label = "**Characteristic**",
      all_stat_cols() ~ "**{level}**\nN = {n}",
      difference = "**SMD**"
    ) %>%
    modify_fmt_fun(
      difference = function(x) {
        ifelse(!is.na(x),
               ifelse(abs(as.numeric(x)) < 0.1,
                      paste0(x, "*"), x),
               x)
      }
    ) %>%
    modify_footnote(difference = "*SMD < 0.1 indicates excellent balance") %>%
    modify_caption("**Table 1. Baseline Characteristics**")
} else {
  # 无分组变量的基线表
  tbl <- tbl_summary(
    data = data_select,
    include = all_of(tbl_vars),
    label = var_labels,
    statistic = statistic_list,
    type = list(
      all_continuous() ~ "continuous",
      all_categorical() ~ "categorical"
    ),
    digits = list(all_continuous() ~ 2, all_categorical() ~ 0),
    missing = "no"
  ) %>%
    modify_header(label = "**Characteristic**") %>%
    modify_caption("**Table 1. Baseline Characteristics**")
}

# 8. 保存结果 -------------------------------------------------------
tbl %>%
  as_flex_table() %>%
  flextable::save_as_docx(path = output_file)

cat("[03_baseline] 基线表已保存到:", output_file, "\n")

# 9. 保存中间数据 ---------------------------------------------------
save(tbl, normal_vars, file = file.path(load_dir, "03_baseline.rda"))
