# =============================================================================
# rstatix 统计检验模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 rstatix 包，提供 dplyr 管道友好的统计检验接口
# 替代 base R 的 t.test() / wilcox.test() / chisq.test()
#
# 优势:
#   - 输出为 tibble 数据框，便于后续操作
#   - 支持 dplyr group_by() 自动分组运行
#   - 自动添加显著性标记
#   - 结果可 pipe 到 gtsummary / ggplot2
#
# 参考:
#   Epi R Handbook: https://epirhandbook.com/en/new_pages/stat_tests.html
#   rstatix: https://rpkgs.datanovia.com/rstatix/
#
# 依赖:
#   install.packages("rstatix")
#   install.packages("dplyr")
# =============================================================================

library(rstatix)
library(dplyr)

# =============================================================================
# 1. 两组比较
# =============================================================================

#' 独立样本 t 检验（管道友好）
#' @param data 数据框
#' @param formula 公式 (value ~ group)
#' @param alternative "two.sided" / "greater" / "less"
rstatix_t_test <- function(data, formula, alternative = "two.sided") {
  result <- data %>%
    t_test(formula, alternative = alternative) %>%
    add_significance()
  
  cat("=== 独立样本 t 检验 ===\n")
  print(result, width = 80)
  
  # 自动检查正态性
  response_var <- all.vars(formula)[1]
  group_var <- all.vars(formula)[2]
  
  norm_check <- data %>%
    group_by(!!sym(group_var)) %>%
    shapiro_test(!!sym(response_var))
  
  cat("\n正态性检验 (Shapiro-Wilk):\n")
  print(norm_check, width = 80)
  
  if (any(norm_check$p < 0.05)) {
    cat("\n⚠ 部分组不满足正态性，建议使用 Wilcoxon 检验\n")
  }
  
  invisible(result)
}

#' 配对 t 检验
rstatix_paired_t_test <- function(data, formula, alternative = "two.sided") {
  result <- data %>%
    t_test(formula, paired = TRUE, alternative = alternative) %>%
    add_significance()
  
  cat("=== 配对 t 检验 ===\n")
  print(result, width = 80)
  
  # 计算差值
  vars <- all.vars(formula)
  diff_var <- paste0(vars[1], "_diff")
  data[[diff_var]] <- data[[vars[1]]]  # 实际需按配对计算
  
  invisible(result)
}

#' Wilcoxon 秩和检验（Mann-Whitney U）
rstatix_wilcox_test <- function(data, formula, alternative = "two.sided") {
  result <- data %>%
    wilcox_test(formula, alternative = alternative) %>%
    add_significance()
  
  cat("=== Wilcoxon 秩和检验 ===\n")
  print(result, width = 80)
  
  # 效应量
  eff_size <- data %>% wilcox_effsize(formula)
  cat("\n效应量:\n")
  print(eff_size, width = 80)
  
  invisible(list(test = result, effectsize = eff_size))
}

#' 配对 Wilcoxon 符号秩检验
rstatix_paired_wilcox <- function(data, formula, alternative = "two.sided") {
  result <- data %>%
    wilcox_test(formula, paired = TRUE, alternative = alternative) %>%
    add_significance()
  
  cat("=== 配对 Wilcoxon 符号秩检验 ===\n")
  print(result, width = 80)
  
  invisible(result)
}

# =============================================================================
# 2. 多组比较
# =============================================================================

#' 单因素方差分析
rstatix_anova <- function(data, formula) {
  result <- data %>% anova_test(formula)
  
  cat("=== 单因素方差分析 ===\n")
  print(result, width = 80)
  
  # 正态性
  response_var <- all.vars(formula)[1]
  group_var <- all.vars(formula)[2]
  
  norm <- data %>%
    group_by(!!sym(group_var)) %>%
    shapiro_test(!!sym(response_var))
  
  cat("\n正态性检验:\n")
  print(norm, width = 80)
  
  # 方差齐性
  var_hom <- data %>% levene_test(formula)
  cat("\n方差齐性检验 (Levene):\n")
  print(var_hom, width = 80)
  
  if (var_hom$p < 0.05) {
    cat("\n⚠ 方差不齐，建议使用 Welch ANOVA 或 Kruskal-Wallis\n")
  }
  
  # 事后比较（如果显著）
  if (result$p < 0.05) {
    cat("\n事后比较 (Tukey HSD):\n")
    posthoc <- data %>% tukey_hsd(formula)
    print(posthoc, width = 80)
  }
  
  invisible(list(anova = result, normality = norm,
                 homogeneity = var_hom))
}

#' Welch ANOVA（方差不齐时的替代）
rstatix_welch_anova <- function(data, formula) {
  result <- data %>% welch_anova_test(formula)
  
  cat("=== Welch ANOVA ===\n")
  print(result, width = 80)
  
  # 事后 Games-Howell
  cat("\n事后比较 (Games-Howell):\n")
  posthoc <- data %>% games_howell_test(formula)
  print(posthoc, width = 80)
  
  invisible(list(test = result, posthoc = posthoc))
}

#' Kruskal-Wallis 检验（非参数多组比较）
rstatix_kruskal <- function(data, formula) {
  result <- data %>% kruskal_test(formula) %>% add_significance()
  
  cat("=== Kruskal-Wallis 检验 ===\n")
  print(result, width = 80)
  
  # 事后 Dunn 检验
  cat("\n事后比较 (Dunn 检验):\n")
  posthoc <- data %>% dunn_test(formula, p.adjust.method = "bonferroni")
  print(posthoc, width = 80)
  
  invisible(list(test = result, posthoc = posthoc))
}

# =============================================================================
# 3. 分类变量检验
# =============================================================================

#' 卡方检验
rstatix_chisq <- function(data, row_var, col_var) {
  # 构建列联表
  tbl <- data %>% tabyl({{ row_var }}, {{ col_var }})
  mat <- as.matrix(tbl[, -1])
  
  result <- chisq_test(mat) %>% add_significance()
  
  cat("=== 卡方检验:",
      deparse(substitute(row_var)), "×",
      deparse(substitute(col_var)), "===\n")
  print(result, width = 80)
  
  # 检查期望频数
  expected <- chisq.test(mat)$expected
  if (any(expected < 5)) {
    cat("\n⚠ 存在期望频数 < 5 的单元格（最小 =",
        round(min(expected), 2), "），建议使用 Fisher 精确检验\n")
  }
  
  invisible(result)
}

#' Fisher 精确检验
rstatix_fisher <- function(data, row_var, col_var) {
  tbl <- data %>% tabyl({{ row_var }}, {{ col_var }})
  mat <- as.matrix(tbl[, -1])
  
  result <- fisher_test(mat, simulate.p.value = TRUE) %>% add_significance()
  
  cat("=== Fisher 精确检验:",
      deparse(substitute(row_var)), "×",
      deparse(substitute(col_var)), "===\n")
  print(result, width = 80)
  
  invisible(result)
}

# =============================================================================
# 4. 正态性检验
# =============================================================================

#' 对多个变量批量进行正态性检验
rstatix_normality_check <- function(data, vars, by_group = NULL) {
  if (!is.null(by_group)) {
    result <- data %>%
      group_by(!!sym(by_group)) %>%
      shapiro_test(all_of(vars))
  } else {
    result <- data %>% shapiro_test(all_of(vars))
  }
  
  cat("=== 正态性检验 (Shapiro-Wilk) ===\n")
  result <- result %>% add_significance()
  print(result, width = 80)
  
  non_normal <- result %>% filter(p < 0.05)
  if (nrow(non_normal) > 0) {
    cat("\n⚠ 以下变量不服从正态分布 (p < 0.05):\n")
    cat(paste(non_normal$variable, collapse = ", "), "\n")
    cat("建议使用非参数检验方法\n")
  }
  
  invisible(result)
}

# =============================================================================
# 5. 自动分组检验（核心功能）
# =============================================================================

#' 自动按分组变量进行统计检验
#' @param data 数据框
#' @param formula 检验公式
#' @param group_col 分组列名（如 "visit", "center"）
#' @param method 检验方法（自动选择或指定）
rstatix_grouped_test <- function(data, formula, group_col,
                                 method = c("auto", "t", "wilcox",
                                            "anova", "kruskal")) {
  method <- match.arg(method)
  
  if (method == "auto") {
    # 自动选择：2组→t/wilcox，多组→anova/kruskal
    group_var <- all.vars(formula)[2]
    n_groups <- data %>% pull(!!sym(group_var)) %>% n_distinct()
    
    if (n_groups == 2) {
      # 检查正态性决定参数/非参数
      response_var <- all.vars(formula)[1]
      norm <- data %>%
        group_by(!!sym(group_var)) %>%
        shapiro_test(!!sym(response_var))
      
      method <- ifelse(any(norm$p < 0.05), "wilcox", "t")
    } else {
      method <- "kruskal"  # 多组默认用非参数
    }
  }
  
  test_func <- switch(method,
    t      = "t_test",
    wilcox = "wilcox_test",
    anova  = "anova_test",
    kruskal = "kruskal_test"
  )
  
  cat("=== 分组检验 (", group_col, ") 方法:", method, "===\n")
  
  result <- data %>%
    group_by(!!sym(group_col)) %>%
    doo(test_func, formula) %>%
    add_significance()
  
  print(result, width = 80)
  invisible(result)
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  # 加载数据
  data("ToothGrowth", package = "datasets")
  data("mtcars")
  
  # 两组比较 - t 检验
  ToothGrowth %>% rstatix_t_test(len ~ supp)
  
  # 两组比较 - Wilcoxon
  ToothGrowth %>% rstatix_wilcox_test(len ~ supp)
  
  # 多组比较 - 方差分析
  ToothGrowth %>% rstatix_anova(len ~ dose)
  
  # 多组比较 - Kruskal-Wallis
  ToothGrowth %>% rstatix_kruskal(len ~ dose)
  
  # 正态性批量检查
  mtcars %>% rstatix_normality_check(c("mpg", "wt", "hp"))
  
  # 自动分组检验
  ToothGrowth %>% rstatix_grouped_test(len ~ supp, group_col = "dose")
}
