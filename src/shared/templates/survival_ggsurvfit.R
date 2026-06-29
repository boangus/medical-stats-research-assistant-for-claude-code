# 生存分析模板 (ggsurvfit Edition): 出版级生存曲线
# =====================================================
# 基于 Pharmaverse 生态的 ggsurvfit 包，生成符合临床报告标准的生存分析
# 适用于：临床试验、观察性研究的生存数据分析
#
# 相较于 survminer 版本的优势:
#   - ggsurvfit 直接继承 ggplot2，与 tidyverse 生态无缝集成
#   - 原生支持 ggplot2 的 theme/label/scale 定制
#   - 与 cards/cardx 包配合生成 ARD 格式的分析结果
#   - 支持亚组分析的森林图标准输出
#
# 依赖:
#   install.packages("survival")
#   install.packages("ggsurvfit")
#   install.packages("gtsummary")  # 用于 hazared ratio 表格
#   install.packages("tidycmprsk") # 用于竞争风险分析

if (!require("survival")) install.packages("survival")
if (!require("ggsurvfit")) install.packages("ggsurvfit")
if (!require("gtsummary")) install.packages("gtsummary")
if (!require("ggplot2")) install.packages("ggplot2")
library(survival)
library(ggsurvfit)
library(gtsummary)
library(ggplot2)

# ==============================================================================
# 1. Kaplan-Meier 生存曲线 (ggsurvfit 版本)
# ==============================================================================

#' 绘制 ggsurvfit 风格的 KM 曲线
#'
#' @param data 数据框
#' @param time_col 随访时间列名
#' @param status_col 事件状态列名（1=事件, 0=删失）
#' @param group_col 分组列名（可选）
#' @param title 图表标题
#' @param xlab X 轴标签
#' @param ylab Y 轴标签
#' @param add_censor 是否显示删失标记
#' @param add_risktable 是否添加风险表
#' @param conf_int 是否显示置信区间
#' @param add_pval 是否添加 log-rank p 值
#' @param palette 配色方案
#' @param surv_median_line 是否显示中位生存时间线
#'
#' @return ggplot 对象
plot_km_ggsurvfit <- function(data,
                               time_col = "time",
                               status_col = "status",
                               group_col = NULL,
                               title = "Kaplan-Meier Survival Curve",
                               xlab = "Time",
                               ylab = "Survival Probability",
                               add_censor = TRUE,
                               add_risktable = TRUE,
                               conf_int = TRUE,
                               add_pval = TRUE,
                               palette = "Set1",
                               surv_median_line = FALSE) {

  # --- 创建生存对象 ---
  surv_fit <- survfit(
    as.formula(paste0(
      "Surv(", time_col, ", ", status_col, ") ~ ",
      ifelse(is.null(group_col), "1", group_col)
    )),
    data = data
  )

  # --- 使用 ggsurvfit 绘图 ---
  p <- surv_fit %>%
    ggsurvfit() +
    labs(
      title = title,
      x = xlab,
      y = ylab
    ) +
    coord_cartesian(ylim = c(0, 1)) +
    scale_ggsurvfit() +
    theme_classic() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
      legend.position = "bottom"
    )

  # --- 可选：置信区间 ---
  if (!conf_int) {
    p <- p + add_confidence_interval(alpha = 0)
  } else {
    p <- p + add_confidence_interval()
  }

  # --- 可选：删失标记 ---
  if (add_censor) {
    p <- p + add_censor_mark()
  }

  # --- 可选：风险表 ---
  if (add_risktable) {
    # 使用 add_risktable 需要安装 ggsurvfit 较新版本
    p <- tryCatch({
      p + add_risktable(
        risktable_stats = c("n.risk", "n.event"),
        hjust = 0,
        size = 3.5
      )
    }, error = function(e) {
      p  # 回退到无风险表版本
    })
  }

  # --- 可选：log-rank p 值 ---
  if (add_pval && !is.null(group_col)) {
    sdiff <- survdiff(
      as.formula(paste0(
        "Surv(", time_col, ", ", status_col, ") ~ ", group_col
      )),
      data = data
    )
    pval <- 1 - pchisq(sdiff$chisq, length(sdiff$n) - 1)

    p <- p + annotate(
      "text", x = Inf, y = 0.05,
      label = paste("Log-rank p =", formatC(pval, format = "f", digits = 3)),
      hjust = 1.1, vjust = 0, size = 4, fontface = "italic"
    )
  }

  # --- 可选：中位生存时间线 ---
  if (surv_median_line) {
    p <- p + add_quantile(prob = 0.5, linetype = "dashed", color = "grey50")
  }

  # --- 配色 ---
  if (!is.null(group_col)) {
    n_groups <- length(unique(data[[group_col]]))
    colors <- RColorBrewer::brewer.pal(
      min(max(n_groups, 3), 9), palette
    )
    p <- p + scale_color_manual(values = colors)
  }

  return(p)
}


# ==============================================================================
# 2. Cox 回归 + 森林图 (Pharmaverse 风格)
# ==============================================================================

#' 创建 Cox 回归表格（gtsummary 风格，兼容 Pharmaverse）
#'
#' @param data 数据框
#' @param time_col 时间列
#' @param status_col 状态列
#' @param predictors 预测变量向量
#' @param labels 变量标签列表（可选）
cox_regression <- function(data,
                            time_col = "time",
                            status_col = "status",
                            predictors = c("age", "sex", "treatment"),
                            labels = NULL) {

  # 构建公式
  formula <- as.formula(paste0(
    "Surv(", time_col, ", ", status_col, ") ~ ",
    paste(predictors, collapse = " + ")
  ))

  # 拟合 Cox 模型
  model <- coxph(formula, data = data)

  # 创建表格
  tbl <- tbl_regression(
    model,
    exponentiate = TRUE,
    label = labels
  ) %>%
    add_global_p() %>%
    modify_header(
      label = "**Variable**",
      hr_ci = "**HR (95% CI)**",
      p.value = "**p-value**"
    ) %>%
    modify_caption("**Cox Proportional Hazards Model**") %>%
    bold_labels()

  return(list(
    model = model,
    table = tbl,
    # 比例风险假设检验
    ph_test = cox.zph(model),
    # C-index
    c_index = survConcordance(
      Surv(data[[time_col]], data[[status_col]]) ~ predict(model)
    )
  ))
}


# ==============================================================================
# 3. ggsurvfit 风格：累积发病率曲线（竞争风险）
# ==============================================================================

#' 使用 ggsurvfit 绘制累积发病率（竞争风险场景）
#'
#' 需要 tidycmprsk 包：install.packages("tidycmprsk")
#'
#' @param data 数据框
#' @param time_col 时间列
#' @param status_col 事件类型列（0=删失, 1=目标事件, 2=竞争事件）
#' @param group_col 分组列
plot_cumulative_incidence <- function(data,
                                       time_col = "time",
                                       status_col = "event_type",
                                       group_col = "group") {

  if (!require("tidycmprsk")) {
    install.packages("tidycmprsk")
    library(tidycmprsk)
  }

  # 使用 tidycmprsk 进行竞争风险分析
  crr_model <- crr(
    as.formula(paste0(
      "Surv(", time_col, ", ", status_col, ") ~ ", group_col
    )),
    data = data,
    failcode = 1,
    cencode = 0
  )

  # 绘图
  p <- crr_model %>%
    ggsurvfit(type = "risk") +
    labs(
      title = "Cumulative Incidence Function",
      x = "Time",
      y = "Cumulative Incidence"
    ) +
    theme_classic() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold"),
      legend.position = "bottom"
    )

  return(p)
}


# ==============================================================================
# 4. 生存分析完整汇报
# ==============================================================================

#' 生成完整的生存分析报告
#'
#' 整合 KM 曲线 + Cox 回归 + 关键统计量
#'
#' @param data 数据框
#' @param time_col 时间列
#' @param status_col 状态列
#' @param group_col 分组列
#' @param predictors Cox 预测变量
full_survival_report <- function(data,
                                  time_col = "time",
                                  status_col = "status",
                                  group_col = NULL,
                                  predictors = c("age", "sex", "treatment")) {

  results <- list()

  # --- (1) 描述性统计 ---
  surv_obj <- Surv(data[[time_col]], data[[status_col]])

  # 事件和删失计数
  results$n_total <- nrow(data)
  results$n_events <- sum(data[[status_col]] == 1)
  results$n_censored <- sum(data[[status_col]] == 0)
  results$event_rate <- results$n_events / results$n_total

  # 中位随访时间（反向 KM 法）
  rev_surv <- survfit(Surv(data[[time_col]], 1 - data[[status_col]]) ~ 1)
  results$median_followup <- summary(rev_surv)$table["median"]

  cat("=== 生存分析报告 ===\n")
  cat(sprintf("总样本: %d\n", results$n_total))
  cat(sprintf("事件数: %d (%.1f%%)\n", results$n_events, results$event_rate * 100))
  cat(sprintf("删失数: %d\n", results$n_censored))
  cat(sprintf("中位随访时间: %.1f\n", results$median_followup))

  # --- (2) 分组 KM 曲线 ---
  if (!is.null(group_col)) {
    results$km_plot <- plot_km_ggsurvfit(
      data, time_col, status_col, group_col,
      add_pval = TRUE, add_risktable = TRUE
    )

    # 中位生存时间（每组的）
    fit <- survfit(
      as.formula(paste0("Surv(", time_col, ", ", status_col, ") ~ ", group_col)),
      data = data
    )
    results$median_survival <- summary(fit)$table[, "median"]

    # Log-rank 检验
    sdiff <- survdiff(
      as.formula(paste0("Surv(", time_col, ", ", status_col, ") ~ ", group_col)),
      data = data
    )
    results$logrank_p <- 1 - pchisq(sdiff$chisq, length(sdiff$n) - 1)

    cat(sprintf("\nLog-rank 检验: p = %.4f\n", results$logrank_p))
  }

  # --- (3) Cox 回归 ---
  if (length(predictors) > 0) {
    cox_results <- cox_regression(data, time_col, status_col, predictors)
    results$cox_model <- cox_results$model
    results$cox_table <- cox_results$table
    results$ph_test <- cox_results$ph_test
    results$c_index <- cox_results$c_index

    cat(sprintf("\nCox 回归 C-index: %.3f\n",
                results$c_index$concordance))
    cat("比例风险假设 (PH) 全局检验:\n")
    print(results$ph_test)
  }

  # --- (4) 生存率：1年、3年、5年 ---
  if (!is.null(group_col)) {
    fit <- survfit(
      as.formula(paste0("Surv(", time_col, ", ", status_col, ") ~ ", group_col)),
      data = data
    )
  } else {
    fit <- survfit(
      as.formula(paste0("Surv(", time_col, ", ", status_col, ") ~ 1")),
      data = data
    )
  }

  surv_summary <- summary(fit, times = c(12, 36, 60), extend = TRUE)
  results$survival_rates <- data.frame(
    Time = surv_summary$time,
    Survival = surv_summary$surv,
    Lower_CI = surv_summary$lower,
    Upper_CI = surv_summary$upper
  )

  cat("\n生存率估计:\n")
  print(results$survival_rates)

  return(results)
}


# ==============================================================================
# 使用示例
# ==============================================================================

if (FALSE) {
  # --- 示例数据 ---
  set.seed(42)
  n <- 200

  sim_data <- data.frame(
    time = rexp(n, rate = 0.1),
    status = rbinom(n, 1, prob = 0.6),
    treatment = rep(c("Drug", "Placebo"), each = n / 2),
    age = round(rnorm(n, mean = 60, sd = 10)),
    sex = sample(c("Male", "Female"), n, replace = TRUE),
    stage = sample(c("I", "II", "III"), n, replace = TRUE, prob = c(0.3, 0.4, 0.3))
  )

  # --- 绘制 KM 曲线 ---
  km <- plot_km_ggsurvfit(
    sim_data, time_col = "time", status_col = "status",
    group_col = "treatment",
    add_pval = TRUE, add_risktable = TRUE,
    title = "Survival by Treatment Group"
  )
  print(km)

  # --- 保存图片 ---
  # ggsave("KM_curve_pharmaverse.png", km, width = 8, height = 6, dpi = 300)

  # --- 完整生存分析报告 ---
  report <- full_survival_report(
    sim_data,
    time_col = "time",
    status_col = "status",
    group_col = "treatment",
    predictors = c("age", "sex", "treatment", "stage")
  )

  # 查看 Cox 表格
  # report$cox_table
}
