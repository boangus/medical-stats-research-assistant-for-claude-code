# =============================================================================
# 多重插补模板 (Multiple Imputation Template)
# 基于 mice 包的完整 MI 流程
# 来源：实战医学统计课程第9章 + 文献支撑 (NEJM/Lancet/Circulation)
# =============================================================================

# 依赖：mice, misty, naniar, dlookr, VIM, miceadds, ggplot2, gridExtra

# ---- S1 缺失模式诊断 ----

#' 缺失模式综合诊断
#' @param data 数据框
#' @param core_vars 核心变量列表（缺失>=3个样本将被剔除）
#' @param threshold 核心变量缺失阈值，默认3
#' @return 包含诊断结果的列表
mi_diagnose <- function(data, core_vars = NULL, threshold = 3) {
  cat("========== 缺失模式诊断 ==========\n\n")

  # 1.1 缺失率总览
  missing_summary <- data.frame(
    variable = names(data),
    n_missing = colSums(is.na(data)),
    pct_missing = round(colSums(is.na(data)) / nrow(data) * 100, 2)
  )
  missing_summary <- missing_summary[order(-missing_summary$pct_missing), ]
  cat("【缺失率排名 Top 10】\n")
  print(head(missing_summary, 10))

  # 1.2 核心变量缺失样本剔除建议
  if (!is.null(core_vars)) {
    core_missing <- rowSums(is.na(data[, core_vars, drop = FALSE]))
    n_drop <- sum(core_missing >= threshold)
    cat(sprintf("\n【核心变量缺失】%d个核心变量中，缺失>=%d个的样本: %d/%d (%.1f%%)\n",
                length(core_vars), threshold, n_drop, nrow(data),
                n_drop / nrow(data) * 100))
    cat("建议：核心变量缺失过多的样本应考虑剔除\n")
  }

  # 1.3 MCAR 检验 (Little's MCAR test)
  cat("\n【MCAR 检验 (Little's Test)】\n")
  tryCatch({
    mcar_result <- misty::na.test(data)
    cat(sprintf("  Chi-squared = %.2f, df = %d, P = %.4f\n",
                mcar_result$chi2, mcar_result$df, mcar_result$p))
    if (mcar_result$p > 0.05) {
      cat("  结论: 不能拒绝MCAR假设 (P>0.05)，缺失可能完全随机\n")
    } else {
      cat("  结论: 拒绝MCAR假设 (P<0.05)，缺失非完全随机，需进一步判断MAR/MNAR\n")
    }
  }, error = function(e) {
    cat("  misty::na.test 执行失败，请手动检验\n")
  })

  # 1.4 缺失模式可视化
  cat("\n【缺失模式可视化】\n")
  tryCatch({
    # naniar 缺失模式图
    p1 <- naniar::gg_miss_var(data, show_pct = TRUE) +
      ggplot2::labs(title = "各变量缺失率")
    print(p1)

    # VIM 缺失模式矩阵
    p2 <- VIM::aggr(data, col = c("navyblue", "red"), numbers = TRUE,
                    sortVars = TRUE, labels = names(data),
                    cex.axis = 0.7, gap = 3,
                    ylab = c("Missing Pattern", "Frequency"))
  }, error = function(e) {
    cat("  可视化执行失败\n")
  })

  invisible(list(
    missing_summary = missing_summary,
    total_missing_pct = round(sum(is.na(data)) / prod(dim(data)) * 100, 2)
  ))
}

# ---- S2 多重插补 ----

#' 多重插补执行
#' @param data 数据框
#' @param m 插补次数，默认5
#' @param method 插补方法: "pmm"(默认), "rf", "cart", "norm"
#' @param maxit 最大迭代次数，默认10
#' @param seed 随机种子
#' @param exclude_vars 不参与插补的变量（如ID）
#' @return mice 对象
mi_impute <- function(data, m = 5, method = "pmm", maxit = 10,
                      seed = 2024, exclude_vars = NULL) {
  cat(sprintf("========== 多重插补 (m=%d, method=%s, maxit=%d) ==========\n",
              m, method, maxit))

  # 排除指定变量
  if (!is.null(exclude_vars)) {
    data_imp <- data[, !names(data) %in% exclude_vars]
  } else {
    data_imp <- data
  }

  # 自动检测变量类型设置方法
  meth <- rep(method, ncol(data_imp))
  names(meth) <- names(data_imp)

  # 分类变量使用 logistic 回归插补
  for (i in seq_along(data_imp)) {
    if (is.factor(data_imp[[i]]) || is.character(data_imp[[i]])) {
      if (method == "pmm") meth[i] <- "logreg"
      if (method == "rf") meth[i] <- "rfcat"
    }
  }

  # 完全无缺失的变量不插补
  for (i in seq_along(data_imp)) {
    if (sum(is.na(data_imp[[i]])) == 0) meth[i] <- ""
  }

  set.seed(seed)
  imp <- mice::mice(data_imp, m = m, method = meth, maxit = maxit,
                    seed = seed, printFlag = TRUE)

  cat(sprintf("\n插补完成: %d 个变量, %d 次插补\n",
              sum(meth != ""), m))
  cat(sprintf("完整案例: %d / %d (%.1f%%)\n",
              sum(complete.cases(data_imp)), nrow(data_imp),
              sum(complete.cases(data_imp)) / nrow(data_imp) * 100))

  return(imp)
}

# ---- S3 收敛诊断 ----

#' 插补收敛诊断 (Trace Plot)
#' @param imp mice 对象
#' @param vars 需要检查的变量，默认全部
mi_convergence <- function(imp, vars = NULL) {
  cat("========== 收敛诊断 ==========\n")
  cat("观察 Trace Plot: 各链应在均值附近波动，无明显趋势\n\n")

  if (is.null(vars)) {
    vars <- names(imp$predictorMatrix[rowSums(imp$predictorMatrix) > 0, ])
  }

  # 提取trace数据并绘图
  plot(imp, layout = c(2, 1))

  cat("判断标准: 各插补链混合良好、无发散趋势 → 收敛\n")
}

# ---- S4 插补密度图 ----

#' 插补前后密度图对比
#' @param imp mice 对象
#' @param vars 需要可视化的变量
mi_density <- function(imp, vars = NULL) {
  cat("========== 插补密度图 ==========\n")
  cat("蓝色=观测值, 红色=插补值 → 两分布应接近\n\n")

  if (is.null(vars)) {
    # 选择有缺失的变量
    vars <- names(which(colSums(is.na(imp$data)) > 0))
  }

  densityplot(imp, ~ ., layout = c(2, 2))
}

# ---- S5 汇总分析 ----

#' 多重插补汇总分析
#' @param imp mice 对象
#' @param formula 分析公式
#' @param model_type 模型类型: "lm", "glm", "cox"
#' @param family glm 的族函数（仅 glm 时需要）
#' @return pooled 结果
mi_pool <- function(imp, formula, model_type = "lm", family = NULL) {
  cat(sprintf("========== 汇总分析 (%s) ==========\n", model_type))

  # 对每个插补数据集拟合模型
  fits <- with(imp, {
    switch(model_type,
      lm = lm(formula, data = .),
      glm = glm(formula, data = ., family = family),
      cox = survival::coxph(formula, data = .)
    )
  })

  # Rubin 规则汇总
  pooled <- mice::pool(fits)
  cat("\n【Pooled 结果 (Rubin's Rules)】\n")
  print(summary(pooled))

  # 汇总信息
  cat(sprintf("\n相对效率 (RE): %.3f\n", (1 + pooled$r) / pooled$m))
  cat("RE > 0.95 表明插补次数 m 足够\n")

  return(pooled)
}

# ---- S6 多方法对比 ----

#' 多种插补方法对比
#' @param data 数据框
#' @param methods 要对比的方法向量，默认 c("pmm", "rf", "cart")
#' @param m 插补次数
#' @param outcome_var 结局变量名（用于对比各方法的插补效果）
#' @return 各方法插补结果的汇总
mi_compare <- function(data, methods = c("pmm", "rf", "cart"),
                       m = 5, outcome_var = NULL) {
  cat("========== 多方法插补对比 ==========\n\n")

  results <- list()
  for (meth in methods) {
    cat(sprintf("--- 方法: %s ---\n", meth))
    imp <- mi_impute(data, m = m, method = meth, seed = 2024)

    # 提取第一个插补数据集的描述统计
    completed <- complete(imp, 1)
    stats <- data.frame(
      method = meth,
      mean_outcome = if (!is.null(outcome_var))
        mean(completed[[outcome_var]], na.rm = TRUE) else NA,
      sd_outcome = if (!is.null(outcome_var))
        sd(completed[[outcome_var]], na.rm = TRUE) else NA
    )
    results[[meth]] <- stats
  }

  comparison <- do.call(rbind, results)
  cat("\n【方法对比汇总】\n")
  print(comparison)

  return(comparison)
}

# ---- S7 完整MI报告 ----

#' 生成完整MI报告
#' @param data 原始数据框
#' @param core_vars 核心变量
#' @param formula 分析公式
#' @param model_type 模型类型
#' @param m 插补次数
#' @param method 插补方法
#' @return 包含全流程结果的列表
mi_report <- function(data, core_vars = NULL, formula,
                      model_type = "lm", m = 5, method = "pmm") {
  cat("╔══════════════════════════════════════╗\n")
  cat("║     多重插补完整报告                  ║\n")
  cat("╚══════════════════════════════════════╝\n\n")

  # Step 1: 诊断
  diag <- mi_diagnose(data, core_vars)

  # Step 2: 插补
  imp <- mi_impute(data, m = m, method = method)

  # Step 3: 收敛诊断
  mi_convergence(imp)

  # Step 4: 密度图
  mi_density(imp)

  # Step 5: 汇总分析
  pooled <- mi_pool(imp, formula, model_type)

  cat("\n========== 报告摘要 ==========\n")
  cat(sprintf("总缺失率: %.1f%%\n", diag$total_missing_pct))
  cat(sprintf("插补方法: %s (m=%d)\n", method, m))
  cat(sprintf("分析模型: %s\n", model_type))
  cat("参照: ICH E9(R1), STROBE Article 12\n")

  invisible(list(diagnosis = diag, imputation = imp, pooled = pooled))
}

# ---- 使用示例 ----
# # 1. 诊断缺失模式
# mi_diagnose(mydata, core_vars = c("age", "bmi", "outcome"))
#
# # 2. 执行多重插补 (pmm方法, 5次)
# imp <- mi_impute(mydata, m = 5, method = "pmm")
#
# # 3. 收敛诊断
# mi_convergence(imp)
#
# # 4. 插补密度图
# mi_density(imp)
#
# # 5. 汇总分析 (Logistic回归)
# pooled <- mi_pool(imp, formula = outcome ~ age + bmi + treatment,
#                   model_type = "glm", family = binomial())
#
# # 6. 完整报告
# mi_report(mydata, core_vars = c("age", "bmi"),
#           formula = outcome ~ age + bmi + treatment,
#           model_type = "glm", family = binomial())
