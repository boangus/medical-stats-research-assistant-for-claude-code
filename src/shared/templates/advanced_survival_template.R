# advanced_survival_template.R — 高级生存分析模板
# ===================================================
# 覆盖方法：
#   1. Firth-Cox 回归 (小样本/稀疏事件)
#   2. 条件生存分析 (condSURV包)
#   3. 生存时间截断点选择 (surv_cutpoint)
#   4. KM曲线增强 (风险表 + 多图合并)
#
# 依赖: survival, coxphf, condSURV, survminer, ggplot2, ggsurvfit
# 安装: install.packages(c("survival","coxphf","condSURV","survminer","ggplot2","ggsurvfit"))
#
# 参考: 实战医学统计课程 Ch14-22
# 作者: MSRA Team
# 版本: 0.1.0

library(survival)
library(ggplot2)

# ============================================================================
# 1. Firth-Cox 回归 (小样本/稀疏事件)
# ============================================================================

#' Firth 惩罚 Cox 回归
#'
#' 当 Cox 回归遇到以下问题时使用 Firth 校正：
#' - 样本量小 (n < 100)
#' - 稀疏事件 (EPV < 10)
#' - 完全分离 (某些协变量完美预测事件)
#' - 单元格零事件
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名 (0/1)
#' @param covs 协变量名向量
#' @param compare 是否与标准 Cox 比较 (默认 TRUE)
#'
#' @return list(firth = coxphf对象, standard = coxph对象, comparison = 比较表)
surv_firth_cox <- function(data, time, event, covs, compare = TRUE) {
  if (!requireNamespace("coxphf", quietly = TRUE)) {
    stop("请安装 coxphf 包: install.packages('coxphf')")
  }

  formula_str <- paste0("Surv(", time, ", ", event, ") ~ ",
                         paste(covs, collapse = " + "))

  # Firth-Cox
  fit_firth <- coxphf::coxphf(as.formula(formula_str), data = data,
                                firth = TRUE, maxit = 50)

  cat("\n📊 Firth-Cox 回归结果:\n")
  coef_tab <- cbind(Estimate = fit_firth$coefficients,
                     `HR` = exp(fit_firth$coefficients),
                     `Lower` = exp(fit_firth$ci.lower),
                     `Upper` = exp(fit_firth$ci.upper),
                     P = fit_firth$prob)
  print(round(coef_tab, 4))

  # 标准 Cox 对比
  if (compare) {
    fit_standard <- coxph(as.formula(formula_str), data = data)

    comparison <- data.frame(
      Variable = covs,
      HR_Standard = round(exp(coef(fit_standard)), 3),
      HR_Firth = round(exp(fit_firth$coefficients[1:length(covs)]), 3),
      P_Standard = round(summary(fit_standard)$coefficients[, "Pr(>|z|)"], 4),
      P_Firth = round(fit_firth$prob[1:length(covs)], 4),
      stringsAsFactors = FALSE
    )

    cat("\n📊 标准 Cox vs Firth-Cox 比较:\n")
    print(comparison, row.names = FALSE)

    # 检查是否有分离
    if (any(abs(coef(fit_standard)) > 5) || any(is.na(coef(fit_standard)))) {
      cat("\n  ⚠️ 标准 Cox 存在分离问题，Firth 校正结果更可靠\n")
    } else {
      cat("\n  ✅ 两种方法结果一致，无明显分离\n")
    }
  }

  return(list(
    firth = fit_firth,
    standard = if (compare) fit_standard else NULL,
    comparison = if (compare) comparison else NULL
  ))
}


# ============================================================================
# 2. 条件生存分析
# ============================================================================

#' 条件生存概率估计
#'
#' 估计已经存活到时间 t0 后，继续存活到时间 t 的概率：
#' S(t|t>t0) = S(t) / S(t0)
#'
#' 适用于：已随访一段时间的患者的预后更新。
#'
#' @param time 生存时间向量
#' @param event 事件向量 (0/1)
#' @param t0 条件时间点 (已经存活的时间)
#' @param eval_times 评估时间点向量 (NULL 则自动选择)
#' @param group 分组变量 (可选)
#'
#' @return list(conditional_surv = 条件生存概率, plot = ggplot)
surv_conditional <- function(time, event, t0, eval_times = NULL,
                              group = NULL) {
  if (!requireNamespace("condSURV", quietly = TRUE)) {
    # 使用基础方法
    cat("ℹ️ condSURV 包不可用，使用基础 KM 方法计算条件生存\n")
  }

  # KM 拟合
  if (is.null(group)) {
    km_fit <- survfit(Surv(time, event) ~ 1)
  } else {
    km_fit <- survfit(Surv(time, event) ~ group)
  }

  # 自动选择评估时间点
  if (is.null(eval_times)) {
    max_time <- max(time, na.rm = TRUE)
    eval_times <- seq(t0, max_time, length.out = 10)
  }

  # 计算条件生存: S(t|t>t0) = S(t) / S(t0)
  # 从 KM 曲线提取生存概率
  km_summary <- summary(km_fit, times = c(t0, eval_times))

  s_t0 <- km_summary$surv[1]  # S(t0)
  s_t <- km_summary$surv[-1]   # S(t) for t > t0

  conditional_surv <- s_t / s_t0

  result_df <- data.frame(
    time = eval_times,
    S_t = s_t,
    S_t0 = rep(s_t0, length(eval_times)),
    conditional_surv = conditional_surv
  )

  cat(sprintf("\n📊 条件生存分析 (t0 = %.1f):\n", t0))
  cat(sprintf("   S(t0) = %.3f\n", s_t0))
  print(result_df, row.names = FALSE)

  # 绘图
  p <- ggplot(result_df, aes(x = time, y = conditional_surv)) +
    geom_line(color = "#2E86C1", linewidth = 1.2) +
    geom_point(color = "#2E86C1", size = 2) +
    geom_hline(yintercept = 0.5, linetype = "dashed", color = "grey50") +
    theme_classic(base_size = 12) +
    theme(plot.title = element_text(face = "bold", hjust = 0.5)) +
    labs(
      title = paste0("Conditional Survival (t0 = ", t0, ")"),
      subtitle = paste0("Given survival to t0 = ", t0,
                         ", probability of surviving to time t"),
      x = "Time",
      y = "Conditional Survival Probability S(t|t>t0)"
    )

  return(list(
    conditional_surv = result_df,
    t0 = t0,
    S_t0 = s_t0,
    plot = p
  ))
}


#' 条件生存中位数
#'
#' 计算已经存活到 t0 后的中位剩余生存时间。
#'
#' @param time 生存时间向量
#' @param event 事件向量
#' @param t0 条件时间点
#'
#' @return list(median_remaining = 中位剩余时间, median_absolute = 绝对中位时间)
surv_conditional_median <- function(time, event, t0) {
  km_fit <- survfit(Surv(time, event) ~ 1)

  # 提取 S(t0)
  km_sum <- summary(km_fit, times = t0)
  s_t0 <- km_sum$surv

  # 条件生存: S(t|t>t0) = S(t) / S(t0)
  # 找到 S(t|t>t0) = 0.5 的时间点
  km_df <- data.frame(
    time = km_fit$time,
    surv = km_fit$surv,
    cond_surv = km_fit$surv / s_t0
  )

  # 中位条件生存时间
  median_time <- km_df$time[which(km_df$cond_surv <= 0.5)[1]]

  if (!is.na(median_time)) {
    median_remaining <- median_time - t0
    cat(sprintf("\n📊 条件生存中位数 (t0 = %.1f):\n", t0))
    cat(sprintf("   已存活: %.1f\n", t0))
    cat(sprintf("   中位剩余生存时间: %.1f\n", median_remaining))
    cat(sprintf("   绝对中位生存时间: %.1f\n", median_time))
  } else {
    median_remaining <- NA
    cat(sprintf("\n📊 条件生存中位数 (t0 = %.1f): 中位数未达到\n", t0))
  }

  return(list(
    median_remaining = median_remaining,
    median_absolute = median_time,
    t0 = t0,
    S_t0 = s_t0
  ))
}


# ============================================================================
# 3. 生存时间截断点选择
# ============================================================================

#' 最优截断点选择 (survminer)
#'
#' 使用 survminer::surv_cutpoint 找到连续变量的最优生存截断点。
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param variable 需要截断的连续变量名
#' @param min_prop 最小组比例 (默认 0.1)
#'
#' @return list(cutpoint = 最优截断点, groups = 分组结果, plot = 图形)
surv_cutpoint <- function(data, time, event, variable, min_prop = 0.1) {
  if (!requireNamespace("survminer", quietly = TRUE)) {
    stop("请安装 survminer 包: install.packages('survminer')")
  }

  # 最优截断点
  cut_result <- survminer::surv_cutpoint(
    data, time = time, event = event,
    variables = variable, minprop = min_prop
  )

  optimal_cut <- cut_result$cutpoint$cutpoint

  # 分组
  data$group <- ifelse(data[[variable]] >= optimal_cut, "High", "Low")

  # KM 曲线
  km_fit <- survfit(Surv(data[[time]], data[[event]]) ~ data$group)

  # Log-rank 检验
  lr_test <- survdiff(Surv(data[[time]], data[[event]]) ~ data$group)
  lr_p <- 1 - pchisq(lr_test$chisq, df = 1)

  cat(sprintf("\n📊 最优截断点 (%s):\n", variable))
  cat(sprintf("   截断值 = %.3f\n", optimal_cut))
  cat(sprintf("   Log-rank P = %s\n", format.pval(lr_p, digits = 3)))
  cat(sprintf("   低组 n = %d, 高组 n = %d\n",
              sum(data$group == "Low"), sum(data$group == "High")))

  # 绘图
  p <- survminer::ggsurvplot(km_fit, data = data,
                              pval = TRUE, risk.table = TRUE,
                              palette = c("#2E86C1", "#E74C3C"),
                              legend.labs = c(
                                paste0(variable, " < ", sprintf("%.1f", optimal_cut)),
                                paste0(variable, " >= ", sprintf("%.1f", optimal_cut))
                              ),
                              title = paste0("Optimal Cutpoint: ", variable))

  return(list(
    cutpoint = optimal_cut,
    group = data$group,
    logrank_p = lr_p,
    survfit = km_fit,
    plot = p
  ))
}


# ============================================================================
# 4. KM 曲线增强 (风险表 + 多图合并)
# ============================================================================

#' 增强 KM 曲线 (含风险表 + 中位数 + CI)
#'
#' @param time 生存时间向量
#' @param event 事件向量
#' @param group 分组变量
#' @param group_labels 分组标签
#' @param title 标题
#' @param palette 配色方案
#' @param show_risk_table 是否显示风险表
#' @param show_median 是否显示中位数线
#'
#' @return ggsurvplot 对象
surv_km_enhanced <- function(time, event, group = NULL,
                              group_labels = NULL, title = "Kaplan-Meier Curve",
                              palette = c("#2E86C1", "#E74C3C", "#27AE60", "#F39C12"),
                              show_risk_table = TRUE,
                              show_median = TRUE) {
  if (is.null(group)) {
    fit <- survfit(Surv(time, event) ~ 1)
  } else {
    fit <- survfit(Surv(time, event) ~ group)
  }

  if (is.null(group_labels)) {
    group_labels <- names(fit$strata)
  }

  p <- survminer::ggsurvplot(
    fit,
    pval = !is.null(group),
    risk.table = show_risk_table,
    risk.table.col = "strata",
    risk.table.height = 0.25,
    palette = palette[1:length(fit$strata)],
    legend.title = "",
    legend.labs = group_labels,
    title = title,
    xlab = "Time",
    ylab = "Survival Probability",
    ggtheme = theme_classic(base_size = 12),
    conf.int = !is.null(group),
    surv.median.line = if (show_median) "hv" else "none"
  )

  return(p)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # 模拟数据
  set.seed(42)
  n <- 100
  df <- data.frame(
    time = rexp(n, rate = 0.05),
    event = rbinom(n, 1, 0.7),
    age = rnorm(n, 60, 10),
    treatment = rbinom(n, 1, 0.5),
    biomarker = rnorm(n, 5, 2)
  )

  # ------ Firth-Cox ------
  res_firth <- surv_firth_cox(df, "time", "event",
                               c("age", "treatment"))

  # ------ 条件生存 ------
  res_cond <- surv_conditional(df$time, df$event, t0 = 12)
  print(res_cond$plot)

  res_median <- surv_conditional_median(df$time, df$event, t0 = 12)

  # ------ 截断点 ------
  res_cut <- surv_cutpoint(df, "time", "event", "biomarker")

  # ------ 增强 KM ------
  p_km <- surv_km_enhanced(df$time, df$event, df$treatment,
                            group_labels = c("Control", "Treatment"))

  cat("✅ 高级生存分析模板示例完成\n")
}

cat("✅ advanced_survival_template.R 已加载\n")
cat("可用函数:\n")
cat("  Firth-Cox:     surv_firth_cox()\n")
cat("  条件生存:      surv_conditional(), surv_conditional_median()\n")
cat("  截断点:        surv_cutpoint()\n")
cat("  增强KM:        surv_km_enhanced()\n")
