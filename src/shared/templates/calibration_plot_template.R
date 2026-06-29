# calibration_plot_template.R — 校准曲线模板
# ===========================================
# 适用于：预测模型校准评估（预测概率 vs 实际发生率）
# 常用于 Logistic 回归、Cox 模型、机器学习的校准评估
#
# 依赖: ggplot2, dplyr, rms (可选)
# 安装: install.packages(c("ggplot2", "dplyr", "rms"))
#
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)
library(dplyr)

# ============================================================================
# 1. 基本校准曲线
# ============================================================================

#' 绘制校准曲线
#'
#' @param y_true 真实标签（0/1）
#' @param y_score 预测概率
#' @param n_bins 分箱数（默认 10）
#' @param title 标题
#' @param add_hist 是否添加预测概率直方图
#'
#' @return list(plot = ggplot, metrics = list)
plot_calibration <- function(y_true, y_score,
                              n_bins = 10,
                              title = "Calibration Plot",
                              add_hist = TRUE) {

  df <- data.frame(
    y_true = y_true,
    y_score = y_score
  )

  # 分箱
  df <- df %>%
    mutate(
      bin = cut(y_score,
                breaks = quantile(y_score, probs = seq(0, 1, 1/n_bins),
                                  na.rm = TRUE),
                include.lowest = TRUE,
                labels = FALSE)
    )

  # 计算每箱的预测均值和实际发生率
  cal_df <- df %>%
    group_by(bin) %>%
    summarise(
      n = n(),
      predicted = mean(y_score, na.rm = TRUE),
      observed = mean(y_true, na.rm = TRUE),
      observed_se = sqrt(observed * (1 - observed) / n()),
      .groups = "drop"
    )

  # 校准指标
  # 1. 校准截距（Intercept）：校准曲线在 45 度线的偏移
  logit_pred <- qlogis(pmax(pmin(y_score, 0.999), 0.001))
  cal_model <- glm(y_true ~ 1 + offset(logit_pred),
                   family = binomial, data = df)
  cal_intercept <- coef(summary(cal_model))[1, 1]
  cal_intercept_p <- coef(summary(cal_model))[1, 4]

  # 2. 校准斜率（Slope）：理想值为 1
  cal_model2 <- glm(y_true ~ logit_pred, family = binomial, data = df)
  cal_slope <- coef(summary(cal_model2))[2, 1]
  cal_slope_p <- coef(summary(cal_model2))[2, 4]

  # 3. Brier Score
  brier <- mean((y_true - y_score)^2)

  # 4. 乐观偏差（Optimism）：E(max - mean)
  # 使用简单近似: mean absolute error
  mae <- mean(abs(y_true - y_score))

  # 绘图
  p <- ggplot(cal_df, aes(x = predicted, y = observed)) +
    # 理想线 (45°)
    geom_abline(intercept = 0, slope = 1, linetype = "dashed",
                color = "grey50", linewidth = 0.8) +
    # 校准曲线
    geom_point(size = 3, color = "steelblue") +
    geom_line(color = "steelblue", linewidth = 1) +
    # 置信区间（利用二项分布 SE）
    geom_errorbar(aes(ymin = observed - 1.96 * observed_se,
                      ymax = observed + 1.96 * observed_se),
                  width = 0.02, color = "steelblue", alpha = 0.5) +
    # 样本量标签
    geom_text(aes(label = paste0("n=", n)),
              vjust = -1, size = 3, color = "grey40") +
    coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
    scale_x_continuous(limits = c(0, 1), labels = scales::percent_format()) +
    scale_y_continuous(limits = c(0, 1), labels = scales::percent_format()) +
    labs(
      title = title,
      subtitle = sprintf(
        "Intercept = %.3f (p=%.3f) | Slope = %.3f (p=%.3f)\nBrier = %.4f | MAE = %.4f",
        cal_intercept, cal_intercept_p, cal_slope, cal_slope_p, brier, mae
      ),
      x = "Predicted Probability",
      y = "Observed Proportion"
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40", size = 8),
      panel.grid.minor = element_blank()
    )

  # 可选：添加预测概率直方图
  if (add_hist) {
    # 使用 annotation_custom 或辅助图
    p <- p +
      annotate("text", x = 0.05, y = 0.95,
               label = sprintf("n = %d\nEvents = %d (%.1f%%)",
                               length(y_true), sum(y_true),
                               mean(y_true) * 100),
               hjust = 0, size = 3.5, color = "grey30")
  }

  metrics <- list(
    cal_intercept = cal_intercept,
    cal_intercept_p = cal_intercept_p,
    cal_slope = cal_slope,
    cal_slope_p = cal_slope_p,
    brier_score = brier,
    mae = mae,
    calibration_data = cal_df
  )

  return(list(plot = p, metrics = metrics))
}


# ============================================================================
# 2. 分组校准曲线（按模型或亚组）
# ============================================================================

#' 比较多个模型的校准曲线
#'
#' @param model_list 命名列表，每个元素是 (y_true, y_score) 的 list
#' @param model_names 模型名称
#' @param n_bins 分箱数
#' @param title 标题
#'
#' @return ggplot 对象
plot_multi_calibration <- function(model_list,
                                    model_names = NULL,
                                    n_bins = 10,
                                    title = "Calibration Curve Comparison") {

  if (is.null(model_names)) {
    model_names <- names(model_list)
  }
  if (is.null(model_names)) {
    model_names <- paste0("Model ", seq_along(model_list))
  }

  colors <- c("steelblue", "#E74C3C", "#27AE60", "#F39C12",
              "#8E44AD", "#1ABC9C")

  cal_all <- do.call(rbind, lapply(seq_along(model_list), function(i) {
    item <- model_list[[i]]
    y_true <- item[[1]]
    y_score <- item[[2]]

    df <- data.frame(y_true = y_true, y_score = y_score, model = model_names[i])

    df <- df %>%
      mutate(
        bin = cut(y_score,
                  breaks = quantile(y_score, probs = seq(0, 1, 1/n_bins),
                                    na.rm = TRUE),
                  include.lowest = TRUE, labels = FALSE)
      )

    df %>%
      group_by(model, bin) %>%
      summarise(
        n = n(),
        predicted = mean(y_score, na.rm = TRUE),
        observed = mean(y_true, na.rm = TRUE),
        .groups = "drop"
      )
  }))

  # 计算各模型 Brier Score
  brier_scores <- sapply(seq_along(model_list), function(i) {
    item <- model_list[[i]]
    mean((item[[1]] - item[[2]])^2)
  })

  # Brier 标签
  brier_labels <- paste0(model_names, " (Brier=",
                         sprintf("%.4f", brier_scores), ")")

  cal_all$model_label <- factor(
    cal_all$model,
    levels = model_names,
    labels = brier_labels
  )

  p <- ggplot(cal_all, aes(x = predicted, y = observed,
                            color = model_label)) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed",
                color = "grey50", linewidth = 0.8) +
    geom_point(size = 2.5) +
    geom_line(linewidth = 1) +
    coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
    scale_color_manual(values = colors[1:length(unique(cal_all$model_label))]) +
    labs(
      title = title,
      x = "Predicted Probability",
      y = "Observed Proportion",
      color = "Model"
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      panel.grid.minor = element_blank(),
      legend.position = c(0.2, 0.8),
      legend.background = element_rect(fill = "white", color = "grey80")
    )

  return(p)
}


# ============================================================================
# 3. 校准指标汇总表
# ============================================================================

#' 生成模型校准指标汇总表
#'
#' @param model_list 命名列表，每个元素是 (y_true, y_score)
#' @return data.frame
calibration_summary_table <- function(model_list) {

  model_names <- names(model_list)
  if (is.null(model_names)) {
    model_names <- paste0("Model ", seq_along(model_list))
  }

  do.call(rbind, lapply(seq_along(model_list), function(i) {
    y_true <- model_list[[i]][[1]]
    y_score <- model_list[[i]][[2]]

    logit_pred <- qlogis(pmax(pmin(y_score, 0.999), 0.001))
    cal_model <- glm(y_true ~ 1 + offset(logit_pred),
                     family = binomial)
    cal_model2 <- glm(y_true ~ logit_pred, family = binomial)

    data.frame(
      Model = model_names[i],
      Brier = mean((y_true - y_score)^2),
      Intercept = coef(summary(cal_model))[1, 1],
      Intercept_p = coef(summary(cal_model))[1, 4],
      Slope = coef(summary(cal_model2))[2, 1],
      Slope_p = coef(summary(cal_model2))[2, 4],
      MAE = mean(abs(y_true - y_score)),
      AUC = as.numeric(pROC::roc(y_true, y_score, quiet = TRUE)$auc)
    )
  }))
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  set.seed(42)
  n <- 500

  # 模拟：完美校准的模型
  y_score1 <- runif(n, 0, 1)
  y_true1 <- rbinom(n, 1, y_score1)

  # 模拟：过度自信的模型（预测极端化）
  y_score2 <- pmin(pmax(y_score1 * 1.5 - 0.25, 0), 1)
  y_true2 <- rbinom(n, 1, y_score1)

  # 基本校准图
  res <- plot_calibration(y_true1, y_score1,
                          title = "Model A - Well Calibrated")
  print(res$metrics)
  ggsave("calibration_well.png", res$plot, width = 8, height = 8, dpi = 300)

  # 多模型比较
  model_list <- list(
    list(y_true1, y_score1),
    list(y_true2, y_score2)
  )
  p <- plot_multi_calibration(model_list,
                              model_names = c("Well Calibrated", "Overconfident"),
                              title = "Calibration Comparison")
  ggsave("calibration_compare.png", p, width = 8, height = 7, dpi = 300)

  # 校准汇总表
  tbl <- calibration_summary_table(model_list)
  print(tbl)

  cat("✅ 校准曲线模板示例完成\n")
}

cat("✅ calibration_plot_template.R 已加载\n")
cat("可用函数:\n")
cat("  plot_calibration()            - 基本校准曲线\n")
cat("  plot_multi_calibration()      - 多模型校准比较\n")
cat("  calibration_summary_table()   - 校准指标汇总表\n")
