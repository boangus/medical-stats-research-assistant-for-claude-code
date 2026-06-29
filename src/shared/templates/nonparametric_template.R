# =============================================================================
# 非参数检验模板 — Medical Statistics Research Assistant
# =============================================================================
# 涵盖医学研究中常用的非参数统计检验方法:
#   1. Mann-Whitney U 检验 (Wilcoxon 秩和检验) — 两独立样本
#   2. Kruskal-Wallis 检验 + Dunn 事后检验 — 多独立样本
#   3. Wilcoxon 符号秩检验 — 两配对样本
#   4. Friedman 检验 + Nemenyi 事后检验 — 多配对样本 (重复测量)
#   5. 非参数 Table 1 — 中位数 [IQR] 基线特征表
#   6. 完整工作流编排器 — 模拟数据演示全部方法
#
# 适用场景:
#   - 数据不满足正态性假设 (Shapiro-Wilk p < 0.05)
#   - 样本量较小 (n < 30)
#   - 数据为有序分类变量 (如 Likert 量表)
#   - 存在离群值
#
# 依赖:
#   install.packages("rstatix")
#   install.packages("dplyr")
#   install.packages("tidyr")
#   install.packages("stats")
#
# 参考:
#   rstatix: https://rpkgs.datanovia.com/rstatix/
#   Epi R Handbook: https://epirhandbook.com/en/new_pages/stat_tests.html
#   Dunn, O.J. (1964). Multiple comparisons using rank sums.
# =============================================================================

library(rstatix)
library(dplyr)
library(tidyr)

# =============================================================================
# 1. Mann-Whitney U 检验 (Wilcoxon 秩和检验)
# =============================================================================

#' Mann-Whitney U 检验 (两独立样本非参数检验)
#'
#' 适用于两组独立样本的比较，不依赖正态性假设。
#' 效应量 r = Z / sqrt(N)，其中 N 为总样本量。
#'
#' @param data 数据框
#' @param x 连续变量名 (字符串)
#' @param group 分组变量名 (字符串，须恰好含两个水平)
#' @param alternative 双侧检验方向: "two.sided" (默认) / "greater" / "less"
#' @return 包含检验统计量、p 值和效应量的列表
#'
#' @examples
#' data(mtcars)
#' mtcars$am <- factor(mtcars$am, labels = c("automatic", "manual"))
#' mann_whitney_test(mtcars, "mpg", "am")
mann_whitney_test <- function(data, x, group,
                               alternative = "two.sided") {
  # --- 参数验证 ---
  stopifnot(is.data.frame(data))
  stopifnot(x %in% names(data))
  stopifnot(group %in% names(data))
  stopifnot(alternative %in% c("two.sided", "greater", "less"))

  grp_vec <- data[[group]]
  grp_levels <- unique(grp_vec[!is.na(grp_vec)])

  if (length(grp_levels) != 2) {
    stop("分组变量须恰好含 2 个水平，当前为 ", length(grp_levels), " 个。")
  }

  val_vec <- data[[x]]
  n_obs <- sum(!is.na(val_vec) & !is.na(grp_vec))
  if (n_obs < 3) {
    stop("有效观测值不足 (n=", n_obs, ")，至少需要 3 个。")
  }

  # --- 执行检验 (使用 rstatix 管道) ---
  formula_str <- paste0(x, " ~ ", group)
  formula_obj <- as.formula(formula_str)

  test_result <- data %>%
    wilcox_test(formula_obj, alternative = alternative) %>%
    add_significance()

  # --- 效应量 r = Z / sqrt(N) ---
  # rstatix 输出 statistic 为 W，需转换为 Z
  z_val <- qnorm(test_result$p / 2)  # 双侧近似
  if (alternative != "two.sided") {
    z_val <- qnorm(test_result$p)
  }
  # 保留符号: 若 group2 > group1 则 z 为正
  if (!is.na(test_result$statistic)) {
    # 使用 rstatix 内置效应量计算
    eff <- data %>% wilcox_effsize(formula_obj, alternative = alternative)
    r_val <- abs(eff$effsize)
    r_interp <- interpret_r(r_val)
  } else {
    r_val <- NA_real_
    r_interp <- "无法计算"
  }

  # --- 结果汇总 ---
  result <- list(
    test_name    = "Mann-Whitney U 检验 (Wilcoxon 秩和检验)",
    variable     = x,
    group        = group,
    group_levels = as.character(grp_levels),
    n1           = sum(grp_vec == grp_levels[1], na.rm = TRUE),
    n2           = sum(grp_vec == grp_levels[2], na.rm = TRUE),
    statistic    = test_result$statistic,
    p_value      = test_result$p,
    significance = test_result$p.signif,
    effect_size_r = r_val,
    effect_interp = r_interp,
    method_detail = paste0("U = ", round(test_result$statistic, 2),
                           ", p = ", format_p(test_result$p),
                           ", r = ", round(r_val, 3),
                           " (", r_interp, ")")
  )

  cat("=== Mann-Whitney U 检验 ===\n")
  cat("变量:", x, " | 分组:", group, "\n")
  cat("组1 (", grp_levels[1], "): n = ", result$n1, "\n", sep = "")
  cat("组2 (", grp_levels[2], "): n = ", result$n2, "\n", sep = "")
  cat("U = ", round(test_result$statistic, 2), "\n", sep = "")
  cat("p = ", format_p(test_result$p),
      " ", test_result$p.signif, "\n", sep = "")
  cat("效应量 r = ", round(r_val, 3), " (", r_interp, ")\n", sep = "")
  cat("---\n")
  print(test_result, width = 80)

  invisible(result)
}

# =============================================================================
# 2. Kruskal-Wallis 检验 + Dunn 事后检验
# =============================================================================

#' Kruskal-Wallis 检验 (多独立样本非参数检验)
#'
#' 适用于三组及以上独立样本的比较。
#' 效应量 epsilon-squared = H / ((N^2 - 1) / (N + 1))。
#' 若 p < 0.05，自动执行 Dunn 事后两两比较。
#'
#' @param data 数据框
#' @param x 连续变量名 (字符串)
#' @param group 分组变量名 (字符串，须含 >= 3 个水平)
#' @param p.adjust.method 事后检验 p 值校正方法: "bonferroni" (默认) / "BH" / "holm" 等
#' @return 包含检验统计量、p 值、效应量和事后检验的列表
#'
#' @examples
#' data(ToothGrowth)
#' ToothGrowth$dose <- factor(ToothGrowth$dose)
#' kruskal_wallis_test(ToothGrowth, "len", "dose")
kruskal_wallis_test <- function(data, x, group,
                                 p.adjust.method = "bonferroni") {
  # --- 参数验证 ---
  stopifnot(is.data.frame(data))
  stopifnot(x %in% names(data))
  stopifnot(group %in% names(data))

  grp_vec <- data[[group]]
  grp_levels <- unique(grp_vec[!is.na(grp_vec)])

  if (length(grp_levels) < 3) {
    warning("分组变量仅含 ", length(grp_levels),
            " 个水平，建议使用 mann_whitney_test() 两两比较。")
  }

  val_vec <- data[[x]]
  n_obs <- sum(!is.na(val_vec) & !is.na(grp_vec))
  if (n_obs < 5) {
    stop("有效观测值不足 (n=", n_obs, ")，至少需要 5 个。")
  }

  # --- 执行检验 ---
  formula_obj <- as.formula(paste0(x, " ~ ", group))

  kw_result <- data %>%
    kruskal_test(formula_obj) %>%
    add_significance()

  # --- 效应量 epsilon-squared ---
  # epsilon^2 = H / ((N^2 - 1) / (N + 1))
  H <- kw_result$statistic
  N <- sum(complete.cases(data[, c(x, group)]))
  eps_sq <- H / ((N^2 - 1) / (N + 1))
  eps_interp <- interpret_epsilon_sq(eps_sq)

  # --- 事后 Dunn 检验 ---
  posthoc <- NULL
  if (kw_result$p < 0.05) {
    posthoc <- data %>%
      dunn_test(formula_obj, p.adjust.method = p.adjust.method) %>%
      add_significance()

    cat("\n--- Dunn 事后两两比较 (", p.adjust.method, " 校正) ---\n", sep = "")
    print(posthoc, width = 80)
  }

  # --- 结果汇总 ---
  result <- list(
    test_name      = "Kruskal-Wallis 检验",
    variable       = x,
    group          = group,
    n_groups       = length(grp_levels),
    statistic      = H,
    df             = kw_result$df,
    p_value        = kw_result$p,
    significance   = kw_result$p.signif,
    effectsize_eps2 = eps_sq,
    effect_interp  = eps_interp,
    posthoc        = posthoc,
    p_adjust       = p.adjust.method
  )

  cat("=== Kruskal-Wallis 检验 ===\n")
  cat("变量:", x, " | 分组:", group,
      " | 水平数:", length(grp_levels), "\n")
  cat("H(", kw_result$df, ") = ", round(H, 3),
      ", p = ", format_p(kw_result$p),
      " ", kw_result$p.signif, "\n", sep = "")
  cat("epsilon-squared = ", round(eps_sq, 3),
      " (", eps_interp, ")\n", sep = "")

  if (kw_result$p >= 0.05) {
    cat("整体检验不显著 (p >= 0.05)，未执行事后比较。\n")
  }

  invisible(result)
}

# =============================================================================
# 3. Wilcoxon 符号秩检验 (配对样本)
# =============================================================================

#' Wilcoxon 符号秩检验 (两配对样本非参数检验)
#'
#' 适用于前后测量、配对设计等场景。
#' 效应量 r = Z / sqrt(N)，其中 N 为配对数。
#'
#' @param data 数据框
#' @param before 前测变量名 (字符串)
#' @param after 后测变量名 (字符串)
#' @param alternative 双侧检验方向: "two.sided" (默认) / "greater" / "less"
#' @return 包含检验统计量、p 值和效应量的列表
#'
#' @examples
#' set.seed(42)
#' df <- data.frame(
#'   before = rnorm(20, mean = 10, sd = 2),
#'   after  = rnorm(20, mean = 11, sd = 2)
#' )
#' wilcoxon_signed_rank(df, "before", "after")
wilcoxon_signed_rank <- function(data, before, after,
                                  alternative = "two.sided") {
  # --- 参数验证 ---
  stopifnot(is.data.frame(data))
  stopifnot(before %in% names(data))
  stopifnot(after %in% names(data))
  stopifnot(alternative %in% c("two.sided", "greater", "less"))

  # 去除含缺失值的配对
  complete_idx <- complete.cases(data[, c(before, after)])
  n_pairs <- sum(complete_idx)

  if (n_pairs < 5) {
    stop("有效配对不足 (n=", n_pairs, ")，至少需要 5 个。")
  }

  before_vals <- data[[before]][complete_idx]
  after_vals  <- data[[after]][complete_idx]
  diff_vals   <- after_vals - before_vals

  # 处理差值为 0 的情况 (ties)
  n_zeros <- sum(diff_vals == 0)
  if (n_zeros > 0) {
    message("注意: 存在 ", n_zeros, " 个差值为 0 的配对，已自动移除。")
    keep <- diff_vals != 0
    before_vals <- before_vals[keep]
    after_vals  <- after_vals[keep]
    n_pairs     <- sum(keep)
  }

  # --- 构建长格式数据用于 rstatix ---
  long_data <- data.frame(
    id    = rep(seq_len(n_pairs), 2),
    time  = rep(c("before", "after"), each = n_pairs),
    value = c(before_vals, after_vals)
  )

  test_result <- long_data %>%
    wilcox_test(value ~ time, paired = TRUE,
                alternative = alternative) %>%
    add_significance()

  # --- 效应量 r = Z / sqrt(N) ---
  # 从 p 值反推 Z
  if (test_result$p < 1) {
    z_val <- qnorm(test_result$p / 2)
    if (alternative != "two.sided") z_val <- qnorm(test_result$p)
    r_val <- abs(z_val) / sqrt(n_pairs)
  } else {
    z_val <- 0
    r_val <- 0
  }
  r_interp <- interpret_r(r_val)

  # --- 描述统计 ---
  median_before <- median(before_vals, na.rm = TRUE)
  median_after  <- median(after_vals, na.rm = TRUE)
  median_diff   <- median(after_vals - before_vals, na.rm = TRUE)

  # --- 结果汇总 ---
  result <- list(
    test_name     = "Wilcoxon 符号秩检验 (配对样本)",
    variable_before = before,
    variable_after  = after,
    n_pairs       = n_pairs,
    n_zeros_removed = sum(!complete.cases(data[, c(before, after)])) + n_zeros,
    statistic     = test_result$statistic,
    p_value       = test_result$p,
    significance  = test_result$p.signif,
    effect_size_r = r_val,
    effect_interp = r_interp,
    median_before = median_before,
    median_after  = median_after,
    median_diff   = median_diff
  )

  cat("=== Wilcoxon 符号秩检验 (配对样本) ===\n")
  cat("配对变量:", before, " vs ", after, "\n")
  cat("有效配对数:", n_pairs, "\n")
  cat("中位数 ", before, " = ", round(median_before, 2),
      " | ", after, " = ", round(median_after, 2),
      " | 差值 = ", round(median_diff, 2), "\n", sep = "")
  cat("V = ", round(test_result$statistic, 2),
      ", p = ", format_p(test_result$p),
      " ", test_result$p.signif, "\n", sep = "")
  cat("效应量 r = ", round(r_val, 3), " (", r_interp, ")\n", sep = "")

  invisible(result)
}

# =============================================================================
# 4. Friedman 检验 + Nemenyi 事后检验
# =============================================================================

#' Friedman 检验 (多配对样本 / 重复测量非参数检验)
#'
#' 适用于同一受试者在多个时间点或条件下的测量比较。
#' 效应量 Kendall's W = chi2 / (N * k * (k - 1))。
#' 若 p < 0.05，自动执行 Nemenyi 事后两两比较。
#'
#' @param data 数据框 (长格式)
#' @param id 受试者 ID 变量名 (字符串)
#' @param within 重复测量因子变量名 (字符串，须含 >= 3 个水平)
#' @param value 结果变量名 (字符串)
#' @return 包含检验统计量、p 值、Kendall's W 和事后检验的列表
#'
#' @examples
#' # 模拟重复测量数据
#' set.seed(42)
#' n <- 30
#' df <- data.frame(
#'   id    = rep(1:n, 3),
#'   time  = rep(c("T1", "T2", "T3"), each = n),
#'   score = c(rnorm(n, 50, 10), rnorm(n, 55, 10), rnorm(n, 60, 10))
#' )
#' friedman_test(df, "id", "time", "score")
friedman_test <- function(data, id, within, value) {
  # --- 参数验证 ---
  stopifnot(is.data.frame(data))
  stopifnot(id %in% names(data))
  stopifnot(within %in% names(data))
  stopifnot(value %in% names(data))

  within_levels <- unique(data[[within]])
  n_levels <- length(within_levels)

  if (n_levels < 3) {
    stop("重复测量因子须含 >= 3 个水平，当前为 ", n_levels,
         " 个。两水平请使用 wilcoxon_signed_rank()。")
  }

  # 检查完整性: 每个 id 应有所有时间点
  id_counts <- table(data[[id]])
  if (any(id_counts != n_levels)) {
    incomplete_ids <- names(id_counts[id_counts != n_levels])
    warning("以下受试者数据不完整，已移除: ",
            paste(incomplete_ids, collapse = ", "))
    data <- data[!data[[id]] %in% incomplete_ids, ]
  }

  n_subjects <- length(unique(data[[id]]))
  if (n_subjects < 2) {
    stop("有效受试者不足 (n=", n_subjects, ")，至少需要 2 个。")
  }

  # --- 处理 ties: 宽格式转换 ---
  wide_data <- data %>%
    pivot_wider(names_from = all_of(within),
                values_from = all_of(value)) %>%
    select(-all_of(id)) %>%
    as.data.frame()

  # --- 执行 Friedman 检验 ---
  fr_test <- friedman.test(as.matrix(wide_data))

  chi2 <- fr_test$statistic
  df   <- fr_test$parameter
  p    <- fr_test$p.value

  # --- 效应量 Kendall's W ---
  # W = chi2 / (N * k * (k - 1))
  kendall_w <- chi2 / (n_subjects * n_levels * (n_levels - 1))
  w_interp <- interpret_kendall_w(kendall_w)

  # --- 事后 Nemenyi 检验 (基于秩的两两比较) ---
  posthoc <- NULL
  if (p < 0.05) {
    posthoc <- friedman_posthoc_nemenyi(data, id, within, value)
  }

  # --- 结果汇总 ---
  result <- list(
    test_name    = "Friedman 检验 (重复测量非参数检验)",
    variable     = value,
    within       = within,
    n_subjects   = n_subjects,
    n_levels     = n_levels,
    statistic    = chi2,
    df           = df,
    p_value      = p,
    significance = sig_label(p),
    kendall_w    = kendall_w,
    effect_interp = w_interp,
    posthoc      = posthoc
  )

  cat("=== Friedman 检验 ===\n")
  cat("变量:", value, " | 重复测量因子:", within,
      " | 受试者数:", n_subjects, "\n")
  cat("chi2(", df, ") = ", round(chi2, 3),
      ", p = ", format_p(p),
      " ", sig_label(p), "\n", sep = "")
  cat("Kendall's W = ", round(kendall_w, 3),
      " (", w_interp, ")\n", sep = "")

  if (p >= 0.05) {
    cat("整体检验不显著 (p >= 0.05)，未执行事后比较。\n")
  }

  invisible(result)
}

#' Nemenyi 事后检验 (Friedman 检验的事后两两比较)
#'
#' @param data 长格式数据框
#' @param id 受试者 ID 变量名
#' @param within 重复测量因子变量名
#' @param value 结果变量名
#' @return 两两比较结果数据框
friedman_posthoc_nemenyi <- function(data, id, within, value) {
  levels_vec <- unique(data[[within]])
  k <- length(levels_vec)
  n <- length(unique(data[[id]]))

  # 计算每个水平的平均秩
  wide <- data %>%
    pivot_wider(names_from = all_of(within),
                values_from = all_of(value)) %>%
    select(-all_of(id))

  rank_mat <- t(apply(as.data.frame(wide), 1, rank))
  mean_ranks <- colMeans(rank_mat)

  # Nemenyi 临界差值: CD = q_alpha * sqrt(k*(k+1)/(6*N))
  # q_alpha for alpha=0.05: 使用 Tukey 近似
  q_alpha <- sqrt(2) * qtukey(0.95, k, Inf) / sqrt(2)
  cd <- q_alpha * sqrt(k * (k + 1) / (6 * n))

  # 两两比较
  pairs_list <- combn(levels_vec, 2, simplify = FALSE)
  results <- do.call(rbind, lapply(pairs_list, function(pair) {
    i <- pair[1]
    j <- pair[2]
    diff_rank <- abs(mean_ranks[i] - mean_ranks[j])
    z_val <- diff_rank / sqrt(k * (k + 1) / (6 * n))
    p_val <- 2 * pnorm(-abs(z_val))

    data.frame(
      group1    = i,
      group2    = j,
      rank_diff = round(diff_rank, 3),
      z         = round(z_val, 3),
      p         = p_val,
      p.signif  = sig_label(p_val),
      stringsAsFactors = FALSE
    )
  }))

  cat("\n--- Nemenyi 事后两两比较 ---\n")
  cat("平均秩: ",
      paste(names(mean_ranks), round(mean_ranks, 2), sep = "=", collapse = ", "),
      "\n")
  cat("临界差值 (CD) = ", round(cd, 3), "\n", sep = "")
  print(results, row.names = FALSE)

  results
}

# =============================================================================
# 5. 非参数 Table 1 (基线特征表)
# =============================================================================

#' 非参数基线特征表 (中位数 [IQR] + 非参数 p 值)
#'
#' 生成 Table 1 格式的基线特征表，连续变量以中位数 [IQR] 表示，
#' p 值通过 Wilcoxon/Kruskal-Wallis 检验计算。
#' 分类变量以 n (%) 表示，p 值通过卡方/Fisher 检验计算。
#'
#' @param data 数据框
#' @param vars 连续变量名向量
#' @param group 分组变量名 (字符串)
#' @param cat_vars 分类变量名向量 (可选)
#' @param digits 小数位数 (默认 1)
#' @return 数据框格式的 Table 1
#'
#' @examples
#' data(mtcars)
#' mtcars$am <- factor(mtcars$am, labels = c("auto", "manual"))
#' nonparametric_table1(mtcars, vars = c("mpg", "hp", "wt"), group = "am")
nonparametric_table1 <- function(data, vars, group, cat_vars = NULL,
                                  digits = 1) {
  # --- 参数验证 ---
  stopifnot(is.data.frame(data))
  stopifnot(group %in% names(data))
  stopifnot(all(vars %in% names(data)))

  grp_levels <- levels(factor(data[[group]]))
  n_groups <- length(grp_levels)

  # --- 辅助函数: 格式化中位数 [IQR] ---
  fmt_median_iqr <- function(x, d = digits) {
    med <- median(x, na.rm = TRUE)
    q1  <- quantile(x, 0.25, na.rm = TRUE)
    q3  <- quantile(x, 0.75, na.rm = TRUE)
    paste0(round(med, d), " [", round(q1, d), ", ", round(q3, d), "]")
  }

  # --- 辅助函数: 格式化 n (%) ---
  fmt_n_pct <- function(x, total) {
    n <- sum(!is.na(x))
    pct <- round(n / total * 100, 1)
    paste0(n, " (", pct, "%)")
  }

  # --- 构建结果表 ---
  table_rows <- list()

  # 受试者计数
  n_row <- c("n", table(data[[group]]))
  table_rows[["n"]] <- n_row

  # 连续变量: 中位数 [IQR]
  for (v in vars) {
    row <- c(v)
    for (gl in grp_levels) {
      subset_vals <- data[[v]][data[[group]] == gl]
      row <- c(row, fmt_median_iqr(subset_vals))
    }

    # p 值: 两组用 Wilcoxon，多组用 Kruskal-Wallis
    if (n_groups == 2) {
      formula_obj <- as.formula(paste0(v, " ~ ", group))
      test <- tryCatch(
        data %>% wilcox_test(formula_obj),
        error = function(e) data.frame(p = NA)
      )
      p_val <- test$p[1]
    } else {
      formula_obj <- as.formula(paste0(v, " ~ ", group))
      test <- tryCatch(
        data %>% kruskal_test(formula_obj),
        error = function(e) data.frame(p = NA)
      )
      p_val <- test$p[1]
    }

    row <- c(row, format_p(p_val))
    table_rows[[v]] <- row
  }

  # 分类变量: n (%)
  if (!is.null(cat_vars)) {
    for (cv in cat_vars) {
      if (!cv %in% names(data)) {
        warning("分类变量 ", cv, " 不在数据中，跳过。")
        next
      }

      cv_levels <- levels(factor(data[[cv]]))
      total_per_group <- table(data[[group]])

      for (cl in cv_levels) {
        row <- c(paste0("  ", cv, ": ", cl))
        obs_vec <- c()

        for (gl in grp_levels) {
          idx <- data[[group]] == gl
          sub_vals <- data[[cv]][idx]
          n_cl <- sum(sub_vals == cl, na.rm = TRUE)
          pct_cl <- round(n_cl / sum(idx, na.rm = TRUE) * 100, 1)
          row <- c(row, paste0(n_cl, " (", pct_cl, "%)"))
          obs_vec <- c(obs_vec, sum(idx, na.rm = TRUE))
        }

        row <- c(row, "")  # p 值只在变量级别填
        table_rows[[paste0(cv, "_", cl)]] <- row
      }

      # 分类变量的 p 值 (卡方/Fisher)
      tbl <- table(data[[cv]], data[[group]])
      p_val <- tryCatch({
        if (any(tbl < 5)) {
          fisher.test(tbl, simulate.p.value = TRUE)$p.value
        } else {
          chisq.test(tbl)$p.value
        }
      }, error = function(e) NA)

      # 回填 p 值到该分类变量的最后一个类别行
      last_key <- paste0(cv, "_", cv_levels[length(cv_levels)])
      if (last_key %in% names(table_rows)) {
        table_rows[[last_key]][length(table_rows[[last_key]])] <- format_p(p_val)
      }
    }
  }

  # --- 组装最终表格 ---
  col_names <- c("Variable", paste0(grp_levels, " (n)"), "P-value")
  result_df <- do.call(rbind, lapply(table_rows, function(r) {
    length(r) <- length(col_names)
    r
  }))
  result_df <- as.data.frame(result_df, stringsAsFactors = FALSE)
  names(result_df) <- col_names
  rownames(result_df) <- NULL

  cat("=== 非参数基线特征表 (Table 1) ===\n")
  cat("分组:", group, " | 水平: ",
      paste(grp_levels, collapse = ", "), "\n")
  cat("连续变量: 中位数 [Q1, Q3] | 分类变量: n (%)\n")
  cat("p 值: 两组 Wilcoxon / 多组 Kruskal-Wallis / 分类 Chi-sq / Fisher\n\n")
  print(result_df, right = FALSE)

  invisible(result_df)
}

# =============================================================================
# 6. 完整工作流编排器
# =============================================================================

#' 非参数检验完整工作流 (模拟数据演示)
#'
#' 使用模拟数据依次演示所有非参数检验方法:
#'   1. Mann-Whitney U 检验
#'   2. Kruskal-Wallis + Dunn 事后检验
#'   3. Wilcoxon 符号秩检验
#'   4. Friedman + Nemenyi 事后检验
#'   5. 非参数 Table 1
#'
#' @param seed 随机种子 (默认 42)
#' @return 所有检验结果的列表 (invisible)
full_nonparametric_workflow <- function(seed = 42) {
  set.seed(seed)

  cat("================================================================\n")
  cat("  非参数检验完整工作流 — 模拟数据演示\n")
  cat("================================================================\n\n")

  # ---------------------------------------------------------------
  # 模拟数据生成
  # ---------------------------------------------------------------
  n <- 60
  sim_data <- data.frame(
    id       = 1:n,
    group    = factor(rep(c("A", "B"), each = n / 2)),
    dose     = factor(rep(c("低", "中", "高"), each = n / 3)),
    score_T1 = c(rnorm(n / 2, 50, 12), rnorm(n / 2, 58, 15)),
    score_T2 = c(rnorm(n / 2, 55, 12), rnorm(n / 2, 62, 15)),
    score_T3 = c(rnorm(n / 2, 60, 12), rnorm(n / 2, 65, 15)),
    age      = c(rpois(n / 2, 45), rpois(n / 2, 50)),
    gender   = factor(sample(c("男", "女"), n, replace = TRUE))
  )

  cat("模拟数据: n =", n, "受试者\n")
  cat("  group: A (n=", n / 2, "), B (n=", n / 2, ")\n", sep = "")
  cat("  dose: 低/中/高 (各 n=", n / 3, ")\n", sep = "")
  cat("  score_T1/T2/T3: 三时间点测量\n\n")

  # ---------------------------------------------------------------
  # 检验 1: Mann-Whitney U
  # ---------------------------------------------------------------
  cat("\n================================================================\n")
  cat("  [1/5] Mann-Whitney U 检验\n")
  cat("================================================================\n")
  mw_result <- mann_whitney_test(sim_data, "score_T1", "group")

  # ---------------------------------------------------------------
  # 检验 2: Kruskal-Wallis + Dunn
  # ---------------------------------------------------------------
  cat("\n================================================================\n")
  cat("  [2/5] Kruskal-Wallis 检验 + Dunn 事后比较\n")
  cat("================================================================\n")
  kw_result <- kruskal_wallis_test(sim_data, "score_T1", "dose")

  # ---------------------------------------------------------------
  # 检验 3: Wilcoxon 符号秩检验
  # ---------------------------------------------------------------
  cat("\n================================================================\n")
  cat("  [3/5] Wilcoxon 符号秩检验 (配对样本)\n")
  cat("================================================================\n")
  ws_result <- wilcoxon_signed_rank(sim_data, "score_T1", "score_T2")

  # ---------------------------------------------------------------
  # 检验 4: Friedman + Nemenyi
  # ---------------------------------------------------------------
  cat("\n================================================================\n")
  cat("  [4/5] Friedman 检验 + Nemenyi 事后比较\n")
  cat("================================================================\n")
  long_data <- sim_data %>%
    select(id, score_T1, score_T2, score_T3) %>%
    pivot_longer(cols = starts_with("score_"),
                 names_to = "time",
                 values_to = "score") %>%
    mutate(time = factor(time,
                         levels = c("score_T1", "score_T2", "score_T3")))

  fr_result <- friedman_test(long_data, "id", "time", "score")

  # ---------------------------------------------------------------
  # 检验 5: 非参数 Table 1
  # ---------------------------------------------------------------
  cat("\n================================================================\n")
  cat("  [5/5] 非参数基线特征表 (Table 1)\n")
  cat("================================================================\n")
  tbl1 <- nonparametric_table1(
    sim_data,
    vars     = c("score_T1", "age"),
    group    = "group",
    cat_vars = c("gender")
  )

  # ---------------------------------------------------------------
  # 汇总
  # ---------------------------------------------------------------
  cat("\n================================================================\n")
  cat("  工作流完成\n")
  cat("================================================================\n")
  cat("所有非参数检验已执行完毕。\n")
  cat("结果列表:\n")
  cat("  $mw_result  — Mann-Whitney U\n")
  cat("  $kw_result  — Kruskal-Wallis + Dunn\n")
  cat("  $ws_result  — Wilcoxon 符号秩\n")
  cat("  $fr_result  — Friedman + Nemenyi\n")
  cat("  $tbl1       — 非参数 Table 1\n")

  invisible(list(
    mw_result = mw_result,
    kw_result = kw_result,
    ws_result = ws_result,
    fr_result = fr_result,
    table1    = tbl1
  ))
}

# =============================================================================
# 辅助函数
# =============================================================================

#' 格式化 p 值
#' @param p 原始 p 值
#' @return 格式化后的字符串
format_p <- function(p) {
  if (is.na(p)) return("NA")
  if (p < 0.001) return("<0.001")
  if (p < 0.01)  return(sprintf("%.3f", p))
  sprintf("%.3f", p)
}

#' 显著性标记
#' @param p 原始 p 值
#' @return 显著性符号
sig_label <- function(p) {
  if (is.na(p)) return("")
  if (p < 0.001) return("***")
  if (p < 0.01)  return("**")
  if (p < 0.05)  return("*")
  "ns"
}

#' 解释效应量 r (|r|)
#' @param r 效应量绝对值
#' @return Cohen (1988) 解释
interpret_r <- function(r) {
  if (is.na(r)) return("NA")
  if (r < 0.1)  return("可忽略")
  if (r < 0.3)  return("小效应")
  if (r < 0.5)  return("中等效应")
  "大效应"
}

#' 解释 epsilon-squared
#' @param eps2 效应量
#' @return 解释标签
interpret_epsilon_sq <- function(eps2) {
  if (is.na(eps2)) return("NA")
  if (eps2 < 0.01)  return("可忽略")
  if (eps2 < 0.06)  return("小效应")
  if (eps2 < 0.14)  return("中等效应")
  "大效应"
}

#' 解释 Kendall's W
#' @param w 效应量
#' @return 解释标签
interpret_kendall_w <- function(w) {
  if (is.na(w)) return("NA")
  if (w < 0.1)  return("可忽略")
  if (w < 0.3)  return("小效应")
  if (w < 0.5)  return("中等效应")
  "大效应"
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  # --- Mann-Whitney U 检验 ---
  data(mtcars)
  mtcars$am <- factor(mtcars$am, labels = c("automatic", "manual"))
  mann_whitney_test(mtcars, "mpg", "am")
  mann_whitney_test(mtcars, "hp", "am", alternative = "greater")

  # --- Kruskal-Wallis + Dunn ---
  data(ToothGrowth)
  ToothGrowth$dose <- factor(ToothGrowth$dose)
  kruskal_wallis_test(ToothGrowth, "len", "dose")
  kruskal_wallis_test(ToothGrowth, "len", "dose", p.adjust.method = "BH")

  # --- Wilcoxon 符号秩检验 ---
  set.seed(42)
  df <- data.frame(
    before = rnorm(30, 10, 2),
    after  = rnorm(30, 11, 2)
  )
  wilcoxon_signed_rank(df, "before", "after")

  # --- Friedman 检验 + Nemenyi ---
  set.seed(42)
  n <- 30
  wide <- data.frame(
    id = 1:n,
    T1 = rnorm(n, 50, 10),
    T2 = rnorm(n, 55, 10),
    T3 = rnorm(n, 60, 10)
  )
  long <- wide %>%
    pivot_longer(-id, names_to = "time", values_to = "score") %>%
    mutate(time = factor(time))
  friedman_test(long, "id", "time", "score")

  # --- 非参数 Table 1 ---
  mtcars$cyl <- factor(mtcars$cyl)
  nonparametric_table1(mtcars,
                        vars = c("mpg", "hp", "wt"),
                        group = "cyl",
                        cat_vars = c("am"))

  # --- 完整工作流 ---
  full_nonparametric_workflow()
}
