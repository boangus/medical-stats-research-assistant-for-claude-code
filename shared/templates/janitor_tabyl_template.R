# =============================================================================
# janitor tabyl 制表模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 janitor R 包 (https://sfirke.github.io/janitor/)
# tabyl + adorn_* 系列函数用于生成出版级频数表与交叉表
#
# 设计理念:
#   计数与格式化分离 —— tabyl 生成含元数据的 data.frame,
#   adorn_* 函数进行逐层美化。调用顺序至关重要:
#   totals → percentages → formatting → ns → title
#
# 依赖:
#   install.packages("janitor")
#   install.packages("dplyr")
#   install.packages("tidyr")
#   install.packages("knitr")    # 用于 kable 输出
#   install.packages("kableExtra") # 用于增强表格样式
# =============================================================================

library(janitor)
library(dplyr)
library(knitr)
library(kableExtra)

# ----- 1. 单变量频数表（描述性统计）--------------------------------------

#' 单变量频数表
#' @param data 数据框
#' @param var 分类变量（非引号或字符串）
tabyl_1way <- function(data, var) {
  var_name <- deparse(substitute(var))
  tab <- data %>% tabyl({{ var }})
  
  cat("\n=== 单变量频数表:", var_name, "===\n")
  print(tab)
  
  # 如果含 NA，会显示 valid_percent
  invisible(tab)
}

# 示例：
# data %>% tabyl_1way(gender)
# data %>% tabyl_1way(race)

# ----- 2. 双变量交叉表（列联表）------------------------------------------

#' 双变量列联表（带百分比和计数）
#' @param data 数据框
#' @param row_var 行变量
#' @param col_var 列变量
#' @param pct_type 百分比类型："row" / "col" / "all"
#' @param digits 小数位数
#' @param add_totals 是否添加合计（"row" / "col" / "both" / "none"）
tabyl_2way <- function(data, row_var, col_var,
                       pct_type = "col", digits = 1,
                       add_totals = "row") {
  
  tab <- data %>% tabyl({{ row_var }}, {{ col_var }})
  
  if (add_totals != "none") {
    tab <- tab %>% adorn_totals(add_totals)
  }
  
  tab <- tab %>%
    adorn_percentages(pct_type) %>%
    adorn_pct_formatting(digits = digits) %>%
    adorn_ns() %>%
    adorn_title("combined")
  
  cat("\n=== 交叉表:", 
      deparse(substitute(row_var)), "×", 
      deparse(substitute(col_var)), 
      "(", pct_type, "%) ===\n")
  print(tab)
  
  # 自动进行卡方检验
  ct <- chisq.test(data %>% pull({{ row_var }}), 
                   data %>% pull({{ col_var }}))
  cat("\n卡方检验: χ² =", round(ct$statistic, 2),
      ", df =", ct$parameter,
      ", p =", format.pval(ct$p.value, digits = 3), "\n")
  
  invisible(list(table = tab, chisq = ct))
}

# 示例：
# data %>% tabyl_2way(treatment, response)
# data %>% tabyl_2way(gender, outcome, pct_type = "row", digits = 2)

# ----- 3. 三变量分层交叉表 ------------------------------------------------

#' 三变量分层列联表（按 strat_var 分组）
#' 返回列表，每个元素是一个双变量 tabyl
#' @param data 数据框
#' @param row_var 行变量
#' @param col_var 列变量
#' @param strat_var 分层变量
#' @param digits 小数位数
tabyl_3way <- function(data, row_var, col_var, strat_var,
                       digits = 1) {
  
  tabs <- data %>%
    tabyl({{ row_var }}, {{ col_var }}, {{ strat_var }}) %>%
    adorn_totals("row") %>%
    adorn_percentages("col") %>%
    adorn_pct_formatting(digits = digits) %>%
    adorn_ns() %>%
    adorn_title("combined")
  
  cat("\n=== 分层交叉表:", 
      deparse(substitute(row_var)), "×", 
      deparse(substitute(col_var)), 
      "|", deparse(substitute(strat_var)), "===\n")
  print(tabs)
  
  invisible(tabs)
}

# 示例：
# data %>% tabyl_3way(race, outcome, gender)

# ----- 4. 出版级 kable 输出 ------------------------------------------------

#' 将 tabyl 输出为格式化 kable 表格
#' @param tabyl_obj tabyl 对象
#' @param caption 表格标题
#' @param font_size 字体大小
tabyl_kable <- function(tabyl_obj, caption = "", font_size = 10) {
  tabyl_obj %>%
    kable(
      caption    = caption,
      format     = "html",
      align      = "c",
      booktabs   = TRUE,
      linesep    = ""
    ) %>%
    kable_styling(
      bootstrap_options = c("striped", "hover", "condensed"),
      font_size = font_size,
      full_width = FALSE,
      position = "center"
    )
}

# 示例：
# data %>% tabyl(gender, treatment) %>%
#   adorn_percentages("col") %>%
#   adorn_pct_formatting(digits = 1) %>%
#   adorn_ns() %>%
#   tabyl_kable(caption = "Gender Distribution by Treatment")

# ----- 5. 自动统计检验（双变量 tabyl 直接调用）----------------------------

#' 对 tabyl 对象自动进行适当的统计检验
#' @param tab tabyl 对象（双变量）
tabyl_test <- function(tab) {
  # tabyl 存储了原始计数作为 row.cell.counts 属性
  raw <- attr(tab, "core")
  
  if (is.null(raw)) {
    # 如果没有 core 属性，尝试从原始数据重建
    warning("无法获取原始计数，直接从矩阵检验")
    mat <- as.matrix(tab[, -1])
    # 移除 totals 行
    if (any(grepl("Total", tab[[1]]))) {
      mat <- mat[-nrow(mat), , drop = FALSE]
    }
  } else {
    mat <- as.matrix(raw[, -1])
  }
  
  # 检查期望频数
  expected <- chisq.test(mat)$expected
  if (any(expected < 5)) {
    cat("\n⚠ 存在期望频数 < 5 的格子，使用 Fisher 精确检验\n")
    fisher.test(mat, simulate.p.value = TRUE)
  } else {
    chisq.test(mat)
  }
}

# 示例：
# data %>% tabyl(treatment, response) %>% tabyl_test()

# =============================================================================
# 完整工作流示例
# =============================================================================

if (FALSE) {
  # 加载示例数据
  data("starwars", package = "dplyr")
  
  # 1. 单变量
  starwars %>% tabyl_1way(gender)
  
  # 2. 双变量交叉表
  starwars %>% tabyl_2way(gender, eye_color)
  
  # 3. 带检验
  starwars %>% tabyl(gender, sex) %>% tabyl_test()
  
  # 4. 三变量分层
  starwars %>% tabyl_3way(eye_color, skin_color, gender)
  
  # 5. kable 报告（适用于 R Markdown）
  starwars %>%
    tabyl(gender, species) %>%
    adorn_totals("row") %>%
    adorn_percentages("col") %>%
    adorn_pct_formatting(digits = 1) %>%
    adorn_ns() %>%
    tabyl_kable("Species by Gender")
}
