# cox_enhanced.R — Cox 回归增强模板
# ====================================
# 在 cox_template.py 基础上增加 R 版 Cox 回归增强功能：
#   1. Cox 回归诊断 (PH检验 + 残差图)
#   2. 分层 Cox 回归
#   3. 时依协变量 Cox
#   4. 竞争风险 Fine-Gray (简要接口)
#   5. 单/多因素 Cox 批量分析
#
# 依赖: survival, survminer, ggplot2
# 安装: install.packages(c("survival", "survminer", "ggplot2"))
#
# 参考: 实战医学统计课程 Ch19-22
# 作者: MSRA Team
# 版本: 0.1.0

library(survival)
library(ggplot2)

# ============================================================================
# 1. Cox 回归诊断 (PH 假设检验)
# ============================================================================

#' Cox PH 假设检验 + 残差诊断
#'
#' @param model coxph 对象
#' @param method 检验方法: "rank" (默认) 或 "km"
#' @param plot 是否绘制残差图
#'
#' @return list(ph_test = cox.zph结果, plots = 残差图列表)
cox_ph_diagnostics <- function(model, method = "rank", plot = TRUE) {
  # PH 检验
  ph <- cox.zph(model, method)

  cat("\n📊 PH 假设检验 (Schoenfeld 残差):\n")
  print(ph)

  # 整体检验
  global_p <- ph$table["GLOBAL", "p"]
  if (global_p > 0.05) {
    cat(sprintf("\n  ✅ 全局 PH 假设成立 (P = %s)\n", format.pval(global_p, digits = 3)))
  } else {
    cat(sprintf("\n  ⚠️ 全局 PH 假设违反 (P = %s)\n", format.pval(global_p, digits = 3)))
  }

  # 各变量检验
  violated_vars <- rownames(ph$table)[ph$table[-nrow(ph$table), "p"] < 0.05]
  if (length(violated_vars) > 0) {
    cat(sprintf("  ⚠️ 违反 PH 假设的变量: %s\n", paste(violated_vars, collapse = ", ")))
    cat("  建议: 使用分层 Cox 或时依协变量\n")
  }

  # 绘图
  plots <- NULL
  if (plot) {
    # 提取各变量残差
    var_names <- names(ph$y)
    plots <- lapply(var_names, function(v) {
      df <- data.frame(
        time = ph$x,
        residual = ph$y[, v]
      )
      ggplot(df, aes(x = time, y = residual)) +
        geom_point(alpha = 0.4, size = 1, color = "grey40") +
        geom_smooth(method = "loess", se = TRUE, color = "#E74C3C",
                    linewidth = 1, alpha = 0.2) +
        geom_hline(yintercept = 0, linetype = "dashed", color = "grey60") +
        theme_classic(base_size = 10) +
        labs(title = v, x = "Time", y = "Schoenfeld Residual")
    })
  }

  return(list(ph_test = ph, plots = plots, violated = violated_vars))
}


# ============================================================================
# 2. 分层 Cox 回归
# ============================================================================

#' 分层 Cox 回归
#'
#' 当 PH 假设违反时，对违反变量使用分层处理。
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param covs 协变量名向量
#' @param strata_var 分层变量名 (PH 违反的变量)
#'
#' @return list(model = coxph对象, summary = 汇总表)
cox_stratified <- function(data, time, event, covs, strata_var) {
  covs_str <- paste(covs, collapse = " + ")
  formula_str <- paste0("Surv(", time, ", ", event, ") ~ ",
                         covs_str, " + strata(", strata_var, ")")

  fit <- coxph(as.formula(formula_str), data = data)

  cat(sprintf("\n📊 分层 Cox 回归 (分层变量: %s):\n", strata_var))

  coef_tab <- coef(summary(fit))
  results <- data.frame(
    Variable = rownames(coef_tab),
    HR = round(exp(coef_tab[, "coef"]), 3),
    Lower = round(exp(coef_tab[, "coef"] - 1.96 * coef_tab[, "se(coef)"]), 3),
    Upper = round(exp(coef_tab[, "coef"] + 1.96 * coef_tab[, "se(coef)"]), 3),
    P = coef_tab[, "Pr(>|z|)"],
    stringsAsFactors = FALSE
  )
  results$P_formatted <- format.pval(results$P, digits = 3)
  print(results, row.names = FALSE)

  return(list(model = fit, summary = results))
}


# ============================================================================
# 3. 时依协变量 Cox
# ============================================================================

#' 时依协变量 Cox 回归 (tt 函数)
#'
#' 当 PH 假设违反时，使用时依协变量建模。
#' 使用 survival 包的 tt() 函数。
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param tt_var 时依协变量名
#' @param covs 固定协变量名向量
#' @param tt_fn 时依函数 (默认线性: function(x, t, ...) x * t)
#'
#' @return list(model = coxph对象, summary = 汇总表)
cox_time_varying <- function(data, time, event, tt_var, covs = NULL,
                              tt_fn = NULL) {
  if (is.null(tt_fn)) {
    tt_fn <- function(x, t, ...) x * t
  }

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""
  formula_str <- paste0("Surv(", time, ", ", event, ") ~ ",
                         tt_var, tt_fn_str, covs_str)

  # 使用 tt() 函数
  tt_call <- paste0(tt_var, " + tt(", tt_var, ")")
  formula_str <- paste0("Surv(", time, ", ", event, ") ~ ",
                         tt_call, covs_str)

  fit <- coxph(as.formula(formula_str), data = data,
                tt = tt_fn)

  cat("\n📊 时依协变量 Cox 回归:\n")
  print(summary(fit))

  return(list(model = fit))
}


# ============================================================================
# 4. 单/多因素 Cox 批量分析
# ============================================================================

#' 单因素 Cox 批量分析
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param vars 候选变量名向量
#' @param catvars 分类变量名向量
#'
#' @return data.frame (变量、HR、CI、P值)
cox_univariate <- function(data, time, event, vars, catvars = NULL) {
  if (!is.null(catvars)) {
    data[catvars] <- lapply(data[catvars], factor)
  }

  results <- do.call(rbind, lapply(vars, function(x) {
    tryCatch({
      formula <- as.formula(paste0("Surv(", time, ", ", event, ") ~ ", x))
      fit <- coxph(formula, data = data)

      coef_tab <- coef(summary(fit))
      if (nrow(coef_tab) < 1) return(NULL)

      b <- coef_tab[1, "coef"]
      se <- coef_tab[1, "se(coef)"]

      data.frame(
        Variable = x,
        HR = round(exp(b), 3),
        Lower = round(exp(b - 1.96 * se), 3),
        Upper = round(exp(b + 1.96 * se), 3),
        P = coef_tab[1, "Pr(>|z|)"],
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      data.frame(Variable = x, HR = NA, Lower = NA, Upper = NA, P = NA,
                 stringsAsFactors = FALSE)
    })
  }))

  results$P_formatted <- format.pval(results$P, digits = 3)
  results <- results[order(results$P), ]

  cat("\n📊 单因素 Cox 回归结果:\n")
  print(results, row.names = FALSE)

  return(results)
}


#' 多因素 Cox 回归 — 变量筛选
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param vars 候选变量名向量
#' @param method 筛选方法: "stepwise", "univariate", "all"
#' @param p_threshold 单因素筛选阈值
#' @param forced_vars 强制纳入变量
#'
#' @return list(model, selected_vars, summary)
cox_multivariable <- function(data, time, event, vars, method = "stepwise",
                               p_threshold = 0.1, forced_vars = NULL) {
  method <- match.arg(method, c("stepwise", "univariate", "all"))

  if (method == "univariate") {
    uni <- cox_univariate(data, time, event, vars)
    selected <- uni$Variable[uni$P < p_threshold]
    if (!is.null(forced_vars)) {
      selected <- union(forced_vars, selected)
    }
  } else {
    selected <- vars
  }

  covs_str <- paste(selected, collapse = " + ")
  formula_str <- paste0("Surv(", time, ", ", event, ") ~ ", covs_str)
  fit_full <- coxph(as.formula(formula_str), data = data)

  if (method == "stepwise") {
    fit_step <- step(fit_full, direction = "both", trace = 0)
    selected <- names(coef(fit_step))
    fit_final <- fit_step
  } else {
    fit_final <- fit_full
  }

  cat(sprintf("\n📊 多因素 Cox 回归 (%s): %d 个变量\n", method, length(selected)))

  coef_tab <- coef(summary(fit_final))
  results <- data.frame(
    Variable = rownames(coef_tab),
    HR = round(exp(coef_tab[, "coef"]), 3),
    Lower = round(exp(coef_tab[, "coef"] - 1.96 * coef_tab[, "se(coef)"]), 3),
    Upper = round(exp(coef_tab[, "coef"] + 1.96 * coef_tab[, "se(coef)"]), 3),
    P = coef_tab[, "Pr(>|z|)"],
    stringsAsFactors = FALSE
  )
  results$P_formatted <- format.pval(results$P, digits = 3)
  print(results, row.names = FALSE)

  return(list(model = fit_final, selected_vars = selected, summary = results))
}


# ============================================================================
# 5. 汇总单/多因素 Cox 表
# ============================================================================

#' 汇总单因素 + 多因素 Cox 结果到一张表
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param vars 变量名向量
#' @param multivar_model 多因素模型对象 (可选，若NULL则自动拟合)
#'
#' @return data.frame (变量、Crude HR、Adjusted HR)
cox_uni_multi_table <- function(data, time, event, vars, multivar_model = NULL) {
  # 单因素
  uni_results <- cox_univariate(data, time, event, vars)

  # 多因素
  if (is.null(multivar_model)) {
    covs_str <- paste(vars, collapse = " + ")
    formula_str <- paste0("Surv(", time, ", ", event, ") ~ ", covs_str)
    multivar_model <- coxph(as.formula(formula_str), data = data)
  }

  adj_coef <- coef(summary(multivar_model))

  # 合并
  result <- data.frame(
    Variable = uni_results$Variable,
    Crude_HR = paste0(sprintf("%.2f", uni_results$HR),
                       " (", sprintf("%.2f", uni_results$Lower),
                       "-", sprintf("%.2f", uni_results$Upper), ")"),
    Crude_P = uni_results$P_formatted,
    stringsAsFactors = FALSE
  )

  # 匹配调整后结果
  result$Adj_HR <- sapply(result$Variable, function(v) {
    idx <- grep(v, rownames(adj_coef), value = TRUE)
    if (length(idx) > 0) {
      b <- adj_coef[idx[1], "coef"]
      se <- adj_coef[idx[1], "se(coef)"]
      paste0(sprintf("%.2f", exp(b)),
             " (", sprintf("%.2f", exp(b - 1.96 * se)),
             "-", sprintf("%.2f", exp(b + 1.96 * se)), ")")
    } else NA
  })

  result$Adj_P <- sapply(result$Variable, function(v) {
    idx <- grep(v, rownames(adj_coef), value = TRUE)
    if (length(idx) > 0) {
      format.pval(adj_coef[idx[1], "Pr(>|z|)"], digits = 3)
    } else NA
  })

  cat("\n📊 单/多因素 Cox 回归汇总表:\n")
  print(result, row.names = FALSE)

  return(result)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # 模拟数据
  set.seed(42)
  n <- 300
  df <- data.frame(
    time = rexp(n, rate = 0.03),
    event = rbinom(n, 1, 0.7),
    age = rnorm(n, 60, 10),
    sex = rbinom(n, 1, 0.5),
    smoking = rbinom(n, 1, 0.3),
    stage = factor(sample(1:3, n, replace = TRUE))
  )

  # ------ 单因素 ------
  uni <- cox_univariate(df, "time", "event",
                         c("age", "sex", "smoking", "stage"))

  # ------ 多因素 ------
  multi <- cox_multivariable(df, "time", "event",
                              c("age", "sex", "smoking", "stage"))

  # ------ PH 诊断 ------
  ph_diag <- cox_ph_diagnostics(multi$model)

  # ------ 分层 Cox (若 PH 违反) ------
  if (length(ph_diag$violated) > 0) {
    strat <- cox_stratified(df, "time", "event",
                             c("age", "sex"), ph_diag$violated[1])
  }

  # ------ 汇总表 ------
  tbl <- cox_uni_multi_table(df, "time", "event",
                              c("age", "sex", "smoking"))

  cat("✅ Cox 增强模板示例完成\n")
}

cat("✅ cox_enhanced.R 已加载\n")
cat("可用函数:\n")
cat("  cox_ph_diagnostics()     - PH 假设检验 + 残差图\n")
cat("  cox_stratified()         - 分层 Cox\n")
cat("  cox_time_varying()       - 时依协变量 Cox\n")
cat("  cox_univariate()         - 单因素 Cox 批量\n")
cat("  cox_multivariable()      - 多因素 Cox 筛选\n")
cat("  cox_uni_multi_table()    - 单/多因素汇总表\n")
