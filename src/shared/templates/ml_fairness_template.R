# ML 公平性与偏差评估模板: 人口统计均等、机会均等、预测均等、校准均等
# ==========================================================================
# 核心方法: 公平性指标计算、多属性审计、偏差缓解策略、校准曲线分组可视化
# 适用场景: 医疗预测模型的公平性审查、AI 辅助诊断偏差检测
#
# 依赖:
#   install.packages(c("fairness", "fairmodels", "DALEX", "ggplot2",
#                       "dplyr", "tidyr", "caret"))
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("fairness", "fairmodels", "DALEX", "ggplot2",
              "dplyr", "tidyr", "caret")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
library(fairness); library(fairmodels); library(DALEX)
library(ggplot2); library(dplyr); library(tidyr); library(caret)


# ==============================================================================
# 1. 单属性公平性检查
# ==============================================================================

#' 计算公平性指标 (单保护属性)
#'
#' 对保护属性各子组计算人口统计均等、机会均等、预测均等、校准均等。
#'
#' @param model 训练好的分类模型 (需支持 predict)
#' @param data  data.frame, 包含保护属性和结局变量
#' @param protected_attr character, 保护属性列名 (如 "sex", "race")
#' @param outcome     character, 结局变量列名 (二分类, 0/1)
#' @param cutoff      numeric, 概率截断值 (默认 0.5)
#' @return list: metrics (数据框), summary (文本总结)
#' @export
#' @examples
#' \dontrun{
#' res <- fairness_check(model, test_data, "sex", "event")
#' print(res$metrics)
#' }
fairness_check <- function(model, data, protected_attr, outcome,
                           cutoff = 0.5) {
  stopifnot(
    "data 必须是 data.frame" = is.data.frame(data),
    "protected_attr 必须存在于 data 中" = protected_attr %in% names(data),
    "outcome 必须存在于 data 中"     = outcome %in% names(data),
    "cutoff 必须在 0-1 之间"         = cutoff > 0 && cutoff < 1
  )

  # --- 获取预测概率 ---
  if (inherits(model, "glm")) {
    probs <- predict(model, newdata = data, type = "response")
  } else {
    probs <- predict(model, newdata = data, type = "prob")[, 2]
  }

  preds <- as.integer(probs >= cutoff)
  actual <- data[[outcome]]
  group  <- as.factor(data[[protected_attr]])
  levels_g <- levels(group)

  # --- 按子组计算指标 ---
  metrics_list <- lapply(levels_g, function(g) {
    idx <- which(group == g)
    n_g <- length(idx)
    pos_rate_g <- mean(probs[idx])
    tpr_g <- mean(preds[idx] == 1 & actual[idx] == 1) /
             max(sum(actual[idx] == 1), 1)
    fpr_g <- mean(preds[idx] == 1 & actual[idx] == 0) /
             max(sum(actual[idx] == 0), 1)
    ppv_g <- sum(preds[idx] == 1 & actual[idx] == 1) /
             max(sum(preds[idx] == 1), 1)
    fnr_g <- mean(preds[idx] == 0 & actual[idx] == 1) /
             max(sum(actual[idx] == 1), 1)
    # 校准均等: 预测概率均值
    calib_g <- mean(probs[idx])

    data.frame(
      subgroup       = g,
      n              = n_g,
      positive_rate  = round(pos_rate_g, 4),
      TPR            = round(tpr_g, 4),
      FPR            = round(fpr_g, 4),
      PPV            = round(ppv_g, 4),
      FNR            = round(fnr_g, 4),
      mean_predicted = round(calib_g, 4),
      stringsAsFactors = FALSE
    )
  })
  metrics <- do.call(rbind, metrics_list)

  # --- 公平性判定 (4:5 规则) ---
  dp_ratio  <- max(metrics$positive_rate) / max(min(metrics$positive_rate), 1e-6)
  tpr_ratio <- max(metrics$TPR) / max(min(metrics$TPR), 1e-6)
  ppv_ratio <- max(metrics$PPV) / max(min(metrics$PPV), 1e-6)
  calib_ratio <- max(metrics$mean_predicted) / max(min(metrics$mean_predicted), 1e-6)

  dp_fair   <- dp_ratio >= 0.8 && dp_ratio <= 1.25
  eod_fair  <- tpr_ratio >= 0.8 && tpr_ratio <= 1.25
  pp_fair   <- ppv_ratio >= 0.8 && ppv_ratio <= 1.25
  cp_fair   <- calib_ratio >= 0.8 && calib_ratio <= 1.25

  summary_text <- sprintf(
    paste0(
      "公平性检查结果 (保护属性: %s, 截断值: %.2f)\n",
      "  人口统计均等 (DP):  %.3f %s\n",
      "  机会均等 (EO):      %.3f %s\n",
      "  预测均等 (PP):      %.3f %s\n",
      "  校准均等 (CP):      %.3f %s"
    ),
    protected_attr, cutoff,
    dp_ratio,   ifelse(dp_fair, "[通过]", "[未通过]"),
    tpr_ratio,  ifelse(eod_fair, "[通过]", "[未通过]"),
    ppv_ratio,  ifelse(pp_fair, "[通过]", "[未通过]"),
    calib_ratio, ifelse(cp_fair, "[通过]", "[未通过]")
  )

  list(
    metrics   = metrics,
    ratios    = c(DP = dp_ratio, EO = tpr_ratio, PP = ppv_ratio, CP = calib_ratio),
    fair_flags = c(DP = dp_fair, EO = eod_fair, PP = pp_fair, CP = cp_fair),
    summary   = summary_text
  )
}


# ==============================================================================
# 2. 多属性公平性审计
# ==============================================================================

#' 多属性公平性审计
#'
#' 对多个保护属性逐一执行公平性检查, 输出汇总报告。
#'
#' @param model            训练好的分类模型
#' @param data             data.frame
#' @param protected_attrs  character vector, 保护属性列名
#' @param outcome          character, 结局变量列名
#' @param cutoff           numeric, 概率截断值
#' @return list: results (每个属性的结果), overall_summary (数据框)
#' @export
#' @examples
#' \dontrun{
#' audit <- fairness_report(model, test_data, c("sex", "race", "age_group"), "event")
#' print(audit$overall_summary)
#' }
fairness_report <- function(model, data, protected_attrs, outcome,
                            cutoff = 0.5) {
  results <- lapply(protected_attrs, function(attr) {
    message(sprintf("正在检查属性: %s", attr))
    fairness_check(model, data, attr, outcome, cutoff = cutoff)
  })
  names(results) <- protected_attrs

  # --- 汇总表 ---
  overall <- do.call(rbind, lapply(names(results), function(attr) {
    r <- results[[attr]]
    data.frame(
      attribute = attr,
      DP_ratio  = r$ratios["DP"],
      EO_ratio  = r$ratios["EO"],
      PP_ratio  = r$ratios["PP"],
      CP_ratio  = r$ratios["CP"],
      DP_fair   = r$fair_flags["DP"],
      EO_fair   = r$fair_flags["EO"],
      PP_fair   = r$fair_flags["PP"],
      CP_fair   = r$fair_flags["CP"],
      stringsAsFactors = FALSE
    )
  }))

  message("\n=== 多属性公平性审计汇总 ===")
  print(overall)

  list(results = results, overall_summary = overall)
}


# ==============================================================================
# 3. 偏差缓解策略
# ==============================================================================

#' 偏差缓解 (预处理方法)
#'
#' 支持三种预处理缓解策略: 重加权 (reweighing)、阈值调整 (threshold)、
#' 重采样 (resampling)。
#'
#' @param model          训练好的模型 (threshold 和 resampling 策略需要)
#' @param data           data.frame (训练数据或测试数据)
#' @param protected_attr character, 保护属性列名
#' @param outcome        character, 结局变量列名
#' @param method         character, 缓解方法: "reweighing" | "threshold" | "resampling"
#' @param cutoff         numeric, 初始截断值 (默认 0.5, threshold 方法使用)
#' @return list: mitigated_data (或 mitigated_model), method, details
#' @export
#' @examples
#' \dontrun{
#' m <- bias_mitigation(model, train_data, "sex", "event", method = "reweighing")
#' m2 <- bias_mitigation(model, test_data, "sex", "event", method = "threshold")
#' }
bias_mitigation <- function(model, data, protected_attr, outcome,
                            method = c("reweighing", "threshold", "resampling"),
                            cutoff = 0.5) {
  method <- match.arg(method)
  group  <- data[[protected_attr]]
  actual <- data[[outcome]]

  if (method == "reweighing") {
    # --- Reweighing: 调整样本权重使子组-结局联合分布均匀 ---
    weights <- numeric(nrow(data))
    levels_g <- unique(group)

    for (g in levels_g) {
      idx_g <- which(group == g)
      for (y_val in c(0, 1)) {
        idx_gy <- intersect(idx_g, which(actual == y_val))
        if (length(idx_gy) == 0) next
        expected <- (length(idx_g) / nrow(data)) *
                    (sum(actual == y_val) / nrow(data))
        observed <- length(idx_gy) / nrow(data)
        weights[idx_gy] <- expected / max(observed, 1e-10)
      }
    }

    data$fairness_weight <- weights
    message(sprintf("[reweighing] 权重范围: [%.4f, %.4f], 中位数: %.4f",
                    min(weights), max(weights), median(weights)))

    return(list(
      mitigated_data = data,
      method = "reweighing",
      details = list(weight_summary = summary(weights))
    ))

  } else if (method == "threshold") {
    # --- 子组阈值调整: 使各子组正预测率趋于一致 ---
    if (inherits(model, "glm")) {
      probs <- predict(model, newdata = data, type = "response")
    } else {
      probs <- predict(model, newdata = data, type = "prob")[, 2]
    }

    overall_rate <- mean(probs >= cutoff)
    levels_g <- unique(group)
    thresholds <- setNames(rep(cutoff, length(levels_g)), as.character(levels_g))

    for (g in levels_g) {
      idx_g <- which(group == g)
      probs_g <- probs[idx_g]
      # 二分搜索找到使子组正预测率与整体一致的阈值
      lo <- 0.01; hi <- 0.99
      for (iter in 1:50) {
        mid <- (lo + hi) / 2
        rate_g <- mean(probs_g >= mid)
        if (rate_g > overall_rate) lo <- mid else hi <- mid
      }
      thresholds[as.character(g)] <- round((lo + hi) / 2, 4)
    }

    message("[threshold] 子组阈值:")
    print(thresholds)

    # 用子组阈值生成新预测
    preds_new <- integer(nrow(data))
    for (g in levels_g) {
      idx_g <- which(group == g)
      preds_new[idx_g] <- as.integer(probs[idx_g] >= thresholds[as.character(g)])
    }
    data$mitigated_pred <- preds_new

    return(list(
      mitigated_data = data,
      method = "threshold",
      details = list(thresholds = thresholds, overall_positive_rate = overall_rate)
    ))

  } else {
    # --- Resampling: 对少数-不利子组过采样 ---
    # 计算每个 (group, outcome) 的目标样本数
    tab <- table(group, actual)
    max_count <- max(tab)

    resampled_list <- lapply(unique(group), function(g) {
      lapply(c(0, 1), function(y) {
        idx <- which(group == g & actual == y)
        if (length(idx) == 0) return(NULL)
        n_resample <- max_count
        sample(idx, size = n_resample, replace = TRUE)
      })
    })
    all_idx <- unlist(resampled_list)
    data_balanced <- data[all_idx, ]

    message(sprintf("[resampling] 样本量: %d -> %d", nrow(data), nrow(data_balanced)))

    return(list(
      mitigated_data = data_balanced,
      method = "resampling",
      details = list(original_n = nrow(data), new_n = nrow(data_balanced))
    ))
  }
}


# ==============================================================================
# 4. 公平性指标可视化
# ==============================================================================

#' 公平性指标分组对比图
#'
#' 将 fairness_check 返回的指标绘制为分组条形图。
#'
#' @param fairness_obj fairness_check() 返回的 list
#' @return ggplot 对象
#' @export
#' @examples
#' \dontrun{
#' res <- fairness_check(model, data, "sex", "event")
#' p <- fairness_plot(res)
#' print(p)
#' }
fairness_plot <- function(fairness_obj) {
  metrics <- fairness_obj$metrics
  protected_attr <- gsub("公平性检查结果 \\(保护属性: ([^,]+),.*",
                         "\\1", fairness_obj$summary)

  df_long <- tidyr::pivot_longer(
    metrics,
    cols = c("positive_rate", "TPR", "FPR", "PPV", "mean_predicted"),
    names_to  = "metric",
    values_to = "value"
  )

  label_map <- c(
    positive_rate  = "正预测率 (DP)",
    TPR            = "真阳性率 (EO)",
    FPR            = "假阳性率",
    PPV            = "阳性预测值 (PP)",
    mean_predicted = "校准均等 (CP)"
  )
  df_long$metric_label <- label_map[df_long$metric]

  p <- ggplot(df_long, aes(x = subgroup, y = value, fill = subgroup)) +
    geom_col(position = "dodge", width = 0.7) +
    geom_text(aes(label = sprintf("%.3f", value)), vjust = -0.3, size = 3) +
    facet_wrap(~ metric_label, scales = "free_y", ncol = 2) +
    scale_fill_brewer(palette = "Set2") +
    labs(
      title = sprintf("公平性指标分组对比 (保护属性: %s)", protected_attr),
      x = "子组", y = "指标值", fill = "子组"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      axis.text.x  = element_text(angle = 30, hjust = 1),
      legend.position = "bottom",
      strip.text = element_text(face = "bold")
    )

  p
}


# ==============================================================================
# 5. 校准曲线 (按子组)
# ==============================================================================

#' 校准曲线按子组分面
#'
#' 将预测概率分箱后, 比较各子组的实际事件率与预测概率。
#'
#' @param model           训练好的分类模型
#' @param data            data.frame
#' @param protected_attr  character, 保护属性列名
#' @param outcome         character, 结局变量列名
#' @param n_bins          integer, 分箱数 (默认 10)
#' @return ggplot 对象
#' @export
#' @examples
#' \dontrun{
#' p <- calibration_by_subgroup(model, test_data, "sex", "event")
#' print(p)
#' }
calibration_by_subgroup <- function(model, data, protected_attr, outcome,
                                    n_bins = 10) {
  if (inherits(model, "glm")) {
    probs <- predict(model, newdata = data, type = "response")
  } else {
    probs <- predict(model, newdata = data, type = "prob")[, 2]
  }

  df <- data.frame(
    predicted = probs,
    actual    = as.numeric(data[[outcome]]),
    group     = as.factor(data[[protected_attr]])
  )

  # 分箱
  df$bin <- cut(df$predicted, breaks = seq(0, 1, length.out = n_bins + 1),
                include.lowest = TRUE)

  # 按 (group, bin) 计算校准统计
  cal_data <- df %>%
    group_by(group, bin) %>%
    summarise(
      mean_predicted = mean(predicted),
      mean_actual    = mean(actual),
      n              = n(),
      .groups = "drop"
    ) %>%
    filter(n >= 3)

  p <- ggplot(cal_data, aes(x = mean_predicted, y = mean_actual,
                             color = group, shape = group)) +
    geom_point(aes(size = n), alpha = 0.8) +
    geom_line(linewidth = 0.6) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed",
                color = "grey50", linewidth = 0.6) +
    scale_size_continuous(range = c(2, 6)) +
    scale_color_brewer(palette = "Set1") +
    labs(
      title = sprintf("校准曲线 (按 %s 分组)", protected_attr),
      x = "预测概率 (分箱均值)", y = "实际事件率",
      color = "子组", shape = "子组", size = "样本量"
    ) +
    coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
    theme_minimal(base_size = 12) +
    theme(legend.position = "right")

  p
}


# ==============================================================================
# 6. 完整工作流演示
# ==============================================================================

#' ML 公平性完整工作流
#'
#' 使用模拟医疗数据演示: 模型训练 -> 公平性检查 -> 多属性审计 ->
#' 偏差缓解 -> 可视化。
#'
#' @return 无 (控制台输出 + ggplot 图形)
#' @export
full_fairness_workflow <- function() {
  set.seed(42)
  n <- 1000

  # --- 模拟数据 ---
  sex  <- sample(c("Male", "Female"), n, replace = TRUE, prob = c(0.55, 0.45))
  race <- sample(c("White", "Black", "Asian"), n, replace = TRUE,
                 prob = c(0.6, 0.25, 0.15))
  age  <- rnorm(n, mean = 60, sd = 12)
  biomarker <- rnorm(n, mean = 5, sd = 2)

  # 引入偏差: race 影响 baseline 风险
  logit <- -3 + 0.03 * age + 0.4 * biomarker +
           ifelse(race == "Black", 0.5, 0) +
           ifelse(sex == "Male", 0.3, 0)
  prob <- 1 / (1 + exp(-logit))
  event <- rbinom(n, 1, prob)

  train_df <- data.frame(sex, race, age, biomarker, event)

  # 拟合模型 (故意不含 race 以模拟不公平)
  model <- glm(event ~ age + biomarker + sex, data = train_df,
               family = binomial())

  cat("\n====== 工作流 1: 单属性公平性检查 ======\n")
  res <- fairness_check(model, train_df, "race", "event")
  cat(res$summary)

  cat("\n====== 工作流 2: 多属性公平性审计 ======\n")
  audit <- fairness_report(model, train_df, c("sex", "race"), "event")

  cat("\n====== 工作流 3: 偏差缓解 (reweighing) ======\n")
  m_rw <- bias_mitigation(model, train_df, "race", "event",
                          method = "reweighing")

  cat("\n====== 工作流 4: 偏差缓解 (threshold) ======\n")
  m_th <- bias_mitigation(model, train_df, "race", "event",
                          method = "threshold")

  cat("\n====== 工作流 5: 公平性指标可视化 ======\n")
  p1 <- fairness_plot(res)
  print(p1)

  cat("\n====== 工作流 6: 校准曲线 ======\n")
  p2 <- calibration_by_subgroup(model, train_df, "race", "event")
  print(p2)

  cat("\n公平性工作流演示完成。\n")
  invisible(NULL)
}


# --- 运行演示 ---
# full_fairness_workflow()
