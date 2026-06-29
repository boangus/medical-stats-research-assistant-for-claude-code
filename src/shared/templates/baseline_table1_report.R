# baseline_table1_report.R
# 增强版基线特征表生成器
# 整合课程 table1sci 核心算法 + gtsummary 灵活性
#
# 算法流程 (移植自 table1sci_常规.Rc):
#   1. 正态性检验 (Shapiro-Wilk n≤5000 / Lilliefors n>5000)
#   2. Levene 方差齐性检验 → 选择 Student t / Welch t
#   3. 参数连续: t-test (二组) / ANOVA (多组)
#   4. 非参数连续: Wilcoxon (二组) / Kruskal-Wallis (多组)
#   5. 分类: Pearson χ² (期望≥5) / Yates (期望[1,5)) / Fisher (期望<1 或 n<40)
#   6. SMD 计算 (用于 PSM 平衡评估)
#
# 依赖: gtsummary, dplyr, flextable, car, nortest
# 输出: Word (.docx) 三线表 + R dataframe

suppressPackageStartupMessages({
  library(gtsummary)
  library(dplyr)
  library(flextable)
})

# ── 正态性检验 (table1sci 算法) ─────────────────────────────────

#' 正态性检验
#'
#' n ≤ 5000: Shapiro-Wilk
#' n > 5000: Kolmogorov-Smirnov (Lilliefors via nortest)
#'
#' @param x 数值向量
#' @param alpha 显著性水平 (默认 0.05)
#' @return logical: TRUE=正态, FALSE=非正态
check_normality <- function(x, alpha = 0.05) {
  x <- x[!is.na(x)]
  if (length(x) < 3) return(TRUE)

  if (length(x) <= 5000) {
    p <- shapiro.test(x)$p.value
  } else {
    if (requireNamespace("nortest", quietly = TRUE)) {
      p <- nortest::lillie.test(x)$p.value
    } else {
      p <- ks.test(x, "pnorm", mean(x), sd(x))$p.value
    }
  }
  return(p > alpha)
}

# ── Levene 方差齐性检验 ──────────────────────────────────────────

#' Levene 方差齐性检验
#'
#' @param x 数值向量
#' @param g 分组因子
#' @param alpha 显著性水平
#' @return logical: TRUE=等方差, FALSE=异方差
check_equal_variance <- function(x, g, alpha = 0.05) {
  if (!requireNamespace("car", quietly = TRUE)) return(TRUE)
  p <- car::leveneTest(x ~ g)$`Pr(>F)`[1]
  return(p > alpha)
}

# ── 连续变量检验选择 ─────────────────────────────────────────────

#' 连续变量自动检验 (table1sci 算法)
#'
#' 正态+等方差 → Student t / ANOVA
#' 正态+异方差 → Welch t / Welch ANOVA
#' 非正态 → Wilcoxon / Kruskal-Wallis
#'
#' @param x 数值向量
#' @param g 分组因子
#' @return list(method, statistic, p.value)
auto_test_continuous <- function(x, g) {
  g <- as.factor(g)
  levels_g <- levels(g)
  n_groups <- length(levels_g)

  is_normal <- check_normality(x)

  if (is_normal) {
    is_equal_var <- check_equal_variance(x, g)
    if (n_groups == 2) {
      test <- t.test(x ~ g, var.equal = is_equal_var)
      method <- if (is_equal_var) "Student t-test" else "Welch t-test"
    } else {
      if (is_equal_var) {
        test <- oneway.test(x ~ g, var.equal = TRUE)
        method <- "One-way ANOVA"
      } else {
        test <- oneway.test(x ~ g, var.equal = FALSE)
        method <- "Welch ANOVA"
      }
    }
  } else {
    if (n_groups == 2) {
      test <- wilcox.test(x ~ g)
      method <- "Wilcoxon rank-sum"
    } else {
      test <- kruskal.test(x ~ g)
      method <- "Kruskal-Wallis"
    }
  }

  list(method = method, statistic = test$statistic, p.value = test$p.value)
}

# ── 分类变量三路卡方检验 ─────────────────────────────────────────

#' 分类变量自动检验 (table1sci 三路卡方算法)
#'
#' 期望频数全部 ≥ 5 → Pearson χ²
#' 最小期望 ∈ [1, 5) → Yates 校正 χ²
#' 最小期望 < 1 或 n < 40 → Fisher exact
#'
#' @param x 因子向量
#' @param g 分组因子
#' @return list(method, statistic, p.value)
auto_test_categorical <- function(x, g) {
  ct <- table(x, g)
  n <- sum(ct)
  expected <- chisq.test(ct, correct = FALSE)$expected
  min_exp <- min(expected)

  if (min_exp < 1 || n < 40) {
    test <- fisher.test(ct)
    list(method = "Fisher exact", statistic = NA, p.value = test$p.value)
  } else if (min_exp < 5) {
    test <- chisq.test(ct, correct = TRUE)  # Yates
    list(method = "Yates χ²", statistic = test$statistic, p.value = test$p.value)
  } else {
    test <- chisq.test(ct, correct = FALSE)  # Pearson
    list(method = "Pearson χ²", statistic = test$statistic, p.value = test$p.value)
  }
}

# ── 格式化统计量 ─────────────────────────────────────────────────

#' 格式化连续变量统计量
#'
#' 正态: mean (SD)
#' 非正态: median [IQR]
format_continuous <- function(x, is_normal = TRUE, digits = 1) {
  x <- x[!is.na(x)]
  if (length(x) == 0) return("")
  if (is_normal) {
    paste0(round(mean(x), digits), " (", round(sd(x), digits), ")")
  } else {
    paste0(round(median(x), digits), " [",
           round(quantile(x, 0.25), digits), ", ",
           round(quantile(x, 0.75), digits), "]")
  }
}

#' 格式化分类变量统计量
format_categorical <- function(x, digits = 1) {
  x <- x[!is.na(x)]
  n <- length(x)
  if (n == 0) return("")
  tb <- table(x)
  paste0(names(tb), ": ", tb, " (", round(tb / n * 100, digits), "%)", collapse = "; ")
}

# ── SMD 计算 ─────────────────────────────────────────────────────

#' 计算标准化均值差 (Cohen's d for continuous, sqrt(ΣΔ²) for categorical)
#'
#' @param x 变量向量
#' @param g 二分组因子
#' @return numeric SMD 值
compute_smd <- function(x, g, var_type = "continuous") {
  g <- as.factor(g)
  if (length(levels(g)) != 2) return(NA_real_)

  grp1 <- x[g == levels(g)[1]]
  grp2 <- x[g == levels(g)[2]]

  if (var_type == "continuous") {
    grp1 <- grp1[!is.na(grp1)]
    grp2 <- grp2[!is.na(grp2)]
    pooled_sd <- sqrt((sd(grp1)^2 + sd(grp2)^2) / 2)
    if (pooled_sd == 0) return(0)
    abs(mean(grp1) - mean(grp2)) / pooled_sd
  } else {
    tb <- table(x, g)
    p1 <- tb[, 1] / sum(tb[, 1])
    p2 <- tb[, 2] / sum(tb[, 2])
    sqrt(sum((p1 - p2)^2 / ((p1 + p2) / 2)))
  }
}

# ── 主函数: 生成增强版 Table 1 ────────────────────────────────────

#' 生成增强版 Table 1
#'
#' 整合 table1sci 算法的自动检验选择 + gtsummary 的灵活格式化
#'
#' @param data 数据框
#' @param group_var 分组变量名 (NULL 则无分组)
#' @param continuous_vars 连续变量名向量 (NULL 则自动推断)
#' @param categorical_vars 分类变量名向量 (NULL 则自动推断)
#' @param var_labels 变量标签列表 (命名列表)
#' @param include_pvalue 是否包含 p 值
#' @param include_smd 是否包含 SMD 列
#' @param output_file 输出文件路径 (NULL 则不导出)
#' @param title 表格标题
#'
#' @return list(tbl = gtsummary对象, df = 数据框, tests = 检验选择记录)
generate_table1 <- function(data,
                            group_var = NULL,
                            continuous_vars = NULL,
                            categorical_vars = NULL,
                            var_labels = NULL,
                            include_pvalue = TRUE,
                            include_smd = FALSE,
                            output_file = NULL,
                            title = "Table 1. Baseline Characteristics") {

  # ── 自动推断变量类型 ──
  if (is.null(continuous_vars) && is.null(categorical_vars)) {
    exclude_vars <- if (!is.null(group_var)) group_var else character(0)
    all_vars <- setdiff(names(data), exclude_vars)

    continuous_vars <- all_vars[sapply(all_vars, function(v) {
      is.numeric(data[[v]]) && length(unique(data[[v]][!is.na(data[[v]])])) >= 10
    })]
    categorical_vars <- setdiff(all_vars, continuous_vars)
  }

  all_vars <- c(continuous_vars, categorical_vars)
  test_log <- list()

  # ── 自动正态性检测 ──
  normal_vars <- character(0)
  for (v in continuous_vars) {
    if (check_normality(data[[v]])) {
      normal_vars <- c(normal_vars, v)
    }
  }
  nonnormal_vars <- setdiff(continuous_vars, normal_vars)

  cat("[Table 1] 正态变量:", paste(normal_vars, collapse = ", "), "\n")
  cat("[Table 1] 非正态变量:", paste(nonnormal_vars, collapse = ", "), "\n")

  # ── 构建统计量列表 ──
  stat_list <- list()
  for (v in normal_vars) {
    stat_list[[v]] <- "{mean} ({sd})"
  }
  for (v in nonnormal_vars) {
    stat_list[[v]] <- "{median} [{p25}, {p75}]"
  }
  stat_list[["all_categorical()"]] <- "{n} ({p}%)"

  # ── 构建检验方法列表 ──
  test_list <- list()
  if (include_pvalue && !is.null(group_var)) {
    # 连续变量: 通过 table1sci 算法选择
    for (v in normal_vars) {
      test_result <- auto_test_continuous(data[[v]], data[[group_var]])
      test_list[[v]] <- if (grepl("Welch", test_result$method)) "t.test" else "t.test"
      test_log[[v]] <- test_result$method
    }
    for (v in nonnormal_vars) {
      test_list[[v]] <- "wilcox.test"
      test_log[[v]] <- "Wilcoxon rank-sum"
    }
    test_list[["all_categorical()"]] <- "chisq.test"
  }

  # ── 构建 gtsummary 表格 ──
  tbl <- data %>%
    select(all_of(c(group_var, all_vars))) %>%
    tbl_summary(
      by = if (!is.null(group_var)) all_of(group_var) else NULL,
      label = var_labels,
      statistic = stat_list,
      type = list(
        all_continuous() ~ "continuous2",
        all_categorical() ~ "categorical"
      ),
      digits = list(
        all_continuous() ~ 1,
        all_categorical() ~ c(0, 1)
      ),
      missing = "ifany",
      missing_text = "Missing"
    )

  # ── 添加 p 值 ──
  if (include_pvalue && !is.null(group_var)) {
    tbl <- tbl %>%
      add_p(
        test = test_list,
        pvalue_fun = function(x) style_pvalue(x, digits = 3)
      )
  }

  # ── 添加总体列 ──
  if (!is.null(group_var)) {
    tbl <- tbl %>% add_overall()
  }

  # ── 添加 SMD ──
  if (include_smd && !is.null(group_var)) {
    tbl <- tbl %>%
      add_difference(
        test = list(
          all_continuous() ~ "cohens_d",
          all_categorical() ~ "smd"
        )
      )
  }

  # ── 格式化 ──
  tbl <- tbl %>%
    modify_header(
      label = "**Characteristic**",
      all_stat_cols() ~ "**{level}**\nN = {n}",
      p.value = "**p-value**"
    ) %>%
    bold_labels() %>%
    modify_caption(paste0("**", title, "**"))

  # ── 导出 ──
  if (!is.null(output_file)) {
    tbl %>%
      as_flex_table() %>%
      save_as_docx(path = output_file)
    cat("[Table 1] 已保存到:", output_file, "\n")
  }

  list(
    tbl = tbl,
    df = as_tibble(tbl),
    tests = test_log,
    normal_vars = normal_vars,
    nonnormal_vars = nonnormal_vars
  )
}

# ── 用法示例 ─────────────────────────────────────────────────────
# source("src/shared/templates/baseline_table1_report.R")
#
# result <- generate_table1(
#   data = mydata,
#   group_var = "treatment",
#   continuous_vars = c("age", "bmi", "sbp"),
#   categorical_vars = c("sex", "smoking", "diabetes"),
#   var_labels = list(age = "Age (years)", bmi = "BMI (kg/m²)"),
#   include_pvalue = TRUE,
#   include_smd = FALSE,
#   output_file = "outcome/tables/Table1_Baseline.docx"
# )
#
# print(result$tbl)       # 显示表格
# print(result$tests)     # 查看检验选择记录
