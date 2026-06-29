# =============================================================================
# gtsummary 出版级表格模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 gtsummary 包，生成符合期刊发表要求的统计表格
#
# 参考:
#   Epi R Handbook: https://epirhandbook.com/en/new_pages/stat_tests.html
#   gtsummary: https://www.danieldsjoberg.com/gtsummary/
#
# 核心优势:
#   - 一行代码生成出版级 Table 1
#   - 自动添加统计检验 p 值
#   - 支持多重比较校正 (add_q)
#   - 支持自定义统计量（中位数+IQR、均数±SD等）
#   - 输出与 gt / flextable / kable 兼容
#
# 依赖:
#   install.packages("gtsummary")
#   install.packages("gt")
#   install.packages("flextable")
# =============================================================================

library(gtsummary)
library(gt)
library(dplyr)

# =============================================================================
# 1. 基线特征表（Table 1）
# =============================================================================

#' 标准基线特征表（RCT 适用）
#' @param data 数据框
#' @param trt_var 分组变量名（字符串）
#' @param continuous_stat 连续变量统计量
#' @param categorical_stat 分类变量统计量
#' @param digits 小数位数
#' @param include_pval 是否包含 p 值
#' @param include_overall 是否包含合计列
#' @param pval_method p 值计算方法
table1_standard <- function(data, trt_var,
                            continuous_stat = "{median} ({p25}, {p75})",
                            categorical_stat = "{n} ({p}%)",
                            digits = 1,
                            include_pval = TRUE,
                            include_overall = TRUE,
                            pval_method = "auto") {
  
  tbl <- data %>%
    tbl_summary(
      by = all_of(trt_var),
      statistic = list(
        all_continuous()  ~ continuous_stat,
        all_categorical() ~ categorical_stat
      ),
      digits = all_continuous() ~ digits,
      missing = "ifany",
      missing_text = "缺失"
    )
  
  if (include_overall) {
    tbl <- tbl %>% add_overall()
  }
  
  if (include_pval) {
    tbl <- tbl %>% add_p(pvalue_fun = ~style_pvalue(., digits = 3))
  }
  
  tbl
}

#' 非正态分布基线表（中位数+IQR）
#' @description 适用于小样本/非正态数据
table1_nonparametric <- function(data, trt_var, digits = 1) {
  data %>%
    tbl_summary(
      by          = all_of(trt_var),
      statistic   = list(
        all_continuous()  ~ "{median} ({p25}, {p75})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits      = all_continuous() ~ digits,
      missing     = "ifany",
      missing_text = "缺失"
    ) %>%
    add_overall() %>%
    add_p(test = all_continuous() ~ "wilcox.test") %>%
    bold_labels()
}

#' 正态分布基线表（均数±SD）
table1_parametric <- function(data, trt_var, digits = 1) {
  data %>%
    tbl_summary(
      by          = all_of(trt_var),
      statistic   = list(
        all_continuous()  ~ "{mean} ({sd})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits      = all_continuous() ~ digits,
      missing     = "ifany",
      missing_text = "缺失"
    ) %>%
    add_overall() %>%
    add_p(test = all_continuous() ~ "t.test") %>%
    bold_labels()
}

# =============================================================================
# 2. 结果表（Outcome Table）
# =============================================================================

#' 结局变量汇总表
#' @param data 数据框
#' @param outcome_vars 结局变量向量
#' @param trt_var 分组变量
#' @param include_ci 是否包含置信区间
table1_outcome <- function(data, outcome_vars, trt_var,
                           include_ci = FALSE) {
  tbl <- data %>%
    select(all_of(c(outcome_vars, trt_var))) %>%
    tbl_summary(
      by        = all_of(trt_var),
      statistic = list(
        all_continuous()  ~ "{median} ({p25}, {p75})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      missing   = "no"
    ) %>%
    add_p()
  
  if (include_ci) {
    tbl <- tbl %>%
      add_ci(pattern = "{stat} ({ci})",
             conf.level = 0.95,
             statistic = all_continuous() ~ "{median} ({p25}, {p75})")
  }
  
  tbl
}

# =============================================================================
# 3. 回归结果汇总表
# =============================================================================

#' 单变量回归结果汇总
#' @param data 数据框
#' @param outcome 结局变量
#' @param predictors 自变量向量
#' @param method "linear" / "logistic" / "coxph"
table1_univariate_regression <- function(data, outcome, predictors,
                                         method = "linear") {
  
  if (method == "linear") {
    tbl <- data %>%
      tbl_uvregression(
        method = lm,
        y      = all_of(outcome),
        include = all_of(predictors),
        label  = NULL
      ) %>%
      bold_p(t = 0.05)
  } else if (method == "logistic") {
    tbl <- data %>%
      tbl_uvregression(
        method = glm,
        method.args = list(family = binomial),
        exponentiate = TRUE,
        y      = all_of(outcome),
        include = all_of(predictors)
      ) %>%
      bold_p(t = 0.05)
  }
  
  tbl
}

#' 多变量回归结果表
#' @param model 拟合好的回归模型
table1_multivariate_regression <- function(model) {
  tbl <- model %>%
    tbl_regression(
      exponentiate = ifelse(
        inherits(model, "glm") && 
          model$family$family == "binomial",
        TRUE, FALSE)
    ) %>%
    bold_p(t = 0.05) %>%
    add_global_p() %>%
    bold_labels()
  
  tbl
}

# =============================================================================
# 4. 统计检验集成（自动添加 p 值）
# =============================================================================

#' 带自定义检验的汇总表
#' @param data 数据框
#' @param trt_var 分组变量
#' @param custom_tests 自定义检验列表
#'   list(variable1 ~ "t.test", variable2 ~ "wilcox.test")
table1_custom_test <- function(data, trt_var, custom_tests) {
  data %>%
    tbl_summary(
      by      = all_of(trt_var),
      statistic = list(
        all_continuous()  ~ "{median} ({p25}, {p75})",
        all_categorical() ~ "{n} ({p}%)"
      )
    ) %>%
    add_p(test = custom_tests) %>%
    add_q()  # 多重比较校正
}

# =============================================================================
# 5. 表格导出
# =============================================================================

#' 导出为 HTML 表格
table1_to_html <- function(tbl, filename = "table1.html") {
  tbl %>%
    as_gt() %>%
    gt::gtsave(filename = filename)
  
  cat("表格已导出:", filename, "\n")
}

#' 导出为 Word (flextable)
#' @description 注意: 需要安装 flextable 包
table1_to_word <- function(tbl) {
  tbl %>%
    as_flex_table()
}

#' 导出为 LaTeX (kable)
table1_to_latex <- function(tbl) {
  tbl %>%
    as_kable()
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  # 加载数据
  data("trial", package = "gtsummary")
  
  # 标准 Table 1
  trial %>% table1_standard("trt")
  
  # 非正态分布 Table 1
  trial %>% table1_nonparametric("trt")
  
  # 正态分布 Table 1（均数±SD）
  trial %>% table1_parametric("trt")
  
  # 结局变量汇总
  trial %>% table1_outcome(c("response", "death", "ttdeath"), "trt")
  
  # 单变量回归
  trial %>%
    table1_univariate_regression("response", 
                                 c("age", "marker", "stage"),
                                 method = "logistic")
  
  # 多变量回归
  model <- glm(response ~ age + marker + stage,
               data = trial, family = binomial)
  model %>% table1_multivariate_regression()
  
  # 导出
  tbl <- trial %>% table1_standard("trt")
  tbl %>% table1_to_html("table1.html")
}
