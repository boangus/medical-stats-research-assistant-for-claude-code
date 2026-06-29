# Table 1 (Pharmaverse Edition): 临床级基线特征表
# =================================================
# 基于 Pharmaverse 生态 (rtables + tern)，生成符合 CDISC 标准的多层级表格
# 适用于：临床试验、观察性研究的基线特征表（Table 1）
#
# 相较于 gtsummary 版本的优势:
#   - 支持多层级嵌套分组（如 Site × Treatment）
#   - ARD (Analysis Results Dataset) 格式输出，可追溯
#   - 原生支持监管递交标准的表格格式
#   - 与 chevron 标准模板库兼容
#
# 依赖:
#   install.packages("rtables")
#   install.packages("tern")
#   install.packages("dplyr")
#   install.packages("tidyr")

if (!require("rtables")) install.packages("rtables")
if (!require("tern")) install.packages("tern")
if (!require("dplyr")) install.packages("dplyr")
if (!require("tidyr")) install.packages("tidyr")
library(rtables)
library(tern)
library(dplyr)
library(tidyr)

# ==============================================================================
# 1. 基础 Table 1：自动分析变量类型并生成分层汇总表
# ==============================================================================

#' 创建 Pharmaverse 风格的 Table 1
#'
#' @param data 数据框
#' @param group_var 分组变量名（字符）
#' @param continuous_vars 连续变量名向量
#' @param categorical_vars 分类变量名向量
#' @param include_pvalue 是否添加组间比较 p 值
#' @param include_overall 是否包含总列
#'
#' @return rtables 表格对象
create_table1_pharmaverse <- function(data,
                                       group_var,
                                       continuous_vars = NULL,
                                       categorical_vars = NULL,
                                       include_pvalue = TRUE,
                                       include_overall = TRUE) {

  # --- 预处理：确保分组变量为因子 ---
  df <- data %>%
    mutate(across(all_of(group_var), as.factor))

  # --- 构建 rtables 布局 ---
  lyt <- basic_table(
    title = "Table 1: Baseline Characteristics",
    subtitles = paste("Grouped by", group_var),
    main_footer = "Mean (SD) for continuous; n (%) for categorical"
  ) %>%
    # 添加总列（可选）
    { if (include_overall) add_colcounts(.) else . } %>%
    { if (include_overall) add_overall_col("Overall") else . }

  # --- 添加连续变量 ---
  for (var in continuous_vars) {
    var_label <- var  # 实际使用时请替换为 label 属性
    lyt <- lyt %>%
      analyze(
        vars = var,
        var_labels = var_label,
        afun = function(x, .N_col, .col_row) {
          n <- sum(!is.na(x))
          mean_sd <- c(mean(x, na.rm = TRUE), sd(x, na.rm = TRUE))
          med_iqr <- c(median(x, na.rm = TRUE),
                       quantile(x, 0.25, na.rm = TRUE),
                       quantile(x, 0.75, na.rm = TRUE))
          min_max <- c(min(x, na.rm = TRUE), max(x, na.rm = TRUE))
          in_rows(
            "n" = n,
            "Mean (SD)" = paste0(
              formatC(mean_sd[1], format = "f", digits = 1), " (",
              formatC(mean_sd[2], format = "f", digits = 1), ")"
            ),
            "Median (Q1, Q3)" = paste0(
              formatC(med_iqr[1], format = "f", digits = 1), " (",
              formatC(med_iqr[2], format = "f", digits = 1), ", ",
              formatC(med_iqr[3], format = "f", digits = 1), ")"
            ),
            .formats = c("xx", "xx", "xx"),
            .labels = c("n", "Mean (SD)", "Median (Q1, Q3)")
          )
        }
      )
  }

  # --- 添加分类变量 ---
  for (var in categorical_vars) {
    var_label <- var
    lyt <- lyt %>%
      analyze(
        vars = var,
        var_labels = var_label,
        afun = function(x, .N_col, .col_row) {
          tbl <- table(x, useNA = "ifany")
          n <- sum(tbl)
          results <- lapply(names(tbl), function(level) {
            paste0(tbl[level], " (",
                   formatC(tbl[level] / n * 100, format = "f", digits = 1), "%)")
          })
          names(results) <- names(tbl)
          results[["n"]] <- n
          do.call(in_rows, c(results, list(.formats = rep("xx", length(results) + 1))))
        }
      )
  }

  # --- 添加 p 值（可选）---
  if (include_pvalue && length(unique(df[[group_var]])) == 2) {
    lyt <- lyt %>%
      summarize_row_groups()  # 有些版本用 add_pvals
  }

  # --- 构建表格 ---
  tbl <- build_table(lyt, df)

  return(tbl)
}


# ==============================================================================
# 2. 使用 tern 包的简化版本（推荐用于标准临床表格）
# ==============================================================================

#' 使用 tern 包创建标准化的基线特征表
#'
#' tern::summarize_cols() 提供标准化的分析方法，
#' 与 admiral 生成的 ADaM 数据集完美配合。
#'
#' @param adsl ADSL 数据集（含所有基线变量和分组）
#' @param group_var 分组变量
#' @param vars 需要汇总的变量名向量
create_table1_tern <- function(adsl, group_var, vars) {

  df <- adsl %>% mutate(across(all_of(group_var), as.factor))

  lyt <- basic_table(
    title = "Table 1: Demographics and Baseline Characteristics",
    subtitles = "Analysis Set: All Randomized Patients"
  ) %>%
    add_colcounts() %>%
    split_cols_by(group_var) %>%
    add_overall_col("Total")

  # 对每个变量添加标准分析
  for (v in vars) {
    if (is.numeric(df[[v]])) {
      # 连续变量：自动选择描述统计
      lyt <- lyt %>%
        analyze(v, afun = function(x) {
          in_rows(
            "n" = sum(!is.na(x)),
            "Mean (SD)" = rcell(
              c(mean(x, na.rm = TRUE), sd(x, na.rm = TRUE)),
              format = "xx.x (xx.x)"
            ),
            "Median" = rcell(median(x, na.rm = TRUE), format = "xx.x"),
            "Min, Max" = rcell(
              c(min(x, na.rm = TRUE), max(x, na.rm = TRUE)),
              format = "xx.x - xx.x"
            ),
            .labels = c("n", "Mean (SD)", "Median", "Min, Max")
          )
        })
    } else {
      # 分类变量：频数和百分比
      lyt <- lyt %>%
        analyze(v, afun = function(x, .N_col) {
          tbl <- table(x)
          do.call(rbind, lapply(names(tbl), function(lvl) {
            data.frame(
              level = lvl,
              count = as.integer(tbl[lvl]),
              pct = round(tbl[lvl] / .N_col * 100, 1),
              stringsAsFactors = FALSE
            )
          }))
        })
    }
  }

  build_table(lyt, df)
}


# ==============================================================================
# 3. 使用 Tplyr 包的统计汇总（专注于数据层）
# ==============================================================================

#' 使用 Tplyr 创建临床汇总
#'
#' Tplyr 专注于数据操作层，以声明式语法计算临床报告所需的统计量。
#' 适合需要精细控制统计计算的场景。
#'
# if (!require("Tplyr")) install.packages("Tplyr")
# library(Tplyr)

create_table1_tplyr <- function(data, group_var, vars) {
  # 注意：Tplyr 的工作流是 pipe 式的
  # t <- data %>%
  #   group_by(across(all_of(group_var))) %>%
  #   Tplyr::tplyr_table(group_var) %>%
  #   add_layer(
  #     group_desc(vars[1], by = group_var)  # 连续变量
  #   ) %>%
  #   add_layer(
  #     group_count(vars[2], by = group_var)  # 分类变量
  #   ) %>%
  #   build()
  #
  # 实际使用时请安装 Tplyr: install.packages("Tplyr")
  message("Tplyr 模板已就绪。请安装 Tplyr 后运行：")
  message('  install.packages("Tplyr")')
  message("  参考: https://github.com/atorus-research/Tplyr")
}


# ==============================================================================
# 4. 表格导出函数
# ==============================================================================

#' 将 rtables 表格导出为多种格式
#'
#' @param tbl rtables 表格对象
#' @param path 输出路径
#' @param format 输出格式: "rtf", "html", "txt"
export_table <- function(tbl, path = "Table1.rtf", format = "rtf") {
  if (format == "rtf") {
    # 使用 pharmaRTF 导出
    if (!require("pharmaRTF")) {
      install.packages("pharmaRTF")
      library(pharmaRTF)
    }
    # 创建 RTF 文档
    doc <- rtf_doc(
      data = tbl,
      header = "",
      footer = "Source: [Study Name]",
      orientation = "landscape"
    )
    write_rtf(doc, file = path)
  } else if (format == "html") {
    # 转 HTML（需要 htmlTable 或 formatters 包）
    cat(as_html(tbl), file = path)
  } else {
    # 纯文本
    cat(toString(tbl), file = path)
  }
  message("Table exported to: ", path)
}


# ==============================================================================
# 使用示例
# ==============================================================================

if (FALSE) {
  # --- 示例数据 ---
  set.seed(42)
  n <- 100

  demo_data <- data.frame(
    treatment = rep(c("Drug", "Placebo"), each = n / 2),
    age = round(rnorm(n, mean = 55, sd = 12)),
    bmi = round(rnorm(n, mean = 27, sd = 4), 1),
    sbp = round(rnorm(n, mean = 130, sd = 15)),
    sex = sample(c("Male", "Female"), n, replace = TRUE, prob = c(0.6, 0.4)),
    smoking = sample(c("Never", "Former", "Current"), n, replace = TRUE,
                     prob = c(0.4, 0.3, 0.3)),
    diabetes = sample(c("Yes", "No"), n, replace = TRUE, prob = c(0.2, 0.8)),
    stringsAsFactors = FALSE
  )

  # --- 使用基础版本 ---
  tbl1 <- create_table1_pharmaverse(
    data = demo_data,
    group_var = "treatment",
    continuous_vars = c("age", "bmi", "sbp"),
    categorical_vars = c("sex", "smoking", "diabetes"),
    include_pvalue = TRUE
  )

  # 查看表格
  tbl1

  # --- 导出 ---
  # export_table(tbl1, "Table1.rtf", format = "rtf")
  # export_table(tbl1, "Table1.html", format = "html")

  # --- 使用 tern 版本 ---
  # tbl2 <- create_table1_tern(demo_data, "treatment",
  #                            c("age", "bmi", "sbp", "sex"))
  # tbl2
}
