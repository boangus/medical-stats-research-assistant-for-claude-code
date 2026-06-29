# roc_visualization_template.R — ROC 曲线可视化模板
# =================================================
# 适用于：诊断试验 ROC 曲线、多模型对比 ROC、PR 曲线
#
# 依赖: ggplot2, pROC, dplyr, plotROC
# 安装: install.packages(c("ggplot2", "pROC", "dplyr", "plotROC"))
#
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)
library(dplyr)

# ============================================================================
# 1. 单条 ROC 曲线
# ============================================================================

#' 绘制单条 ROC 曲线
#'
#' @param y_true 真实标签（0/1）
#' @param y_score 预测概率
#' @param title 标题
#' @param add_ci 是否添加置信区间带
#' @param color 曲线颜色
#' @return ggplot 对象
plot_single_roc <- function(y_true, y_score,
                              title = "ROC Curve",
                              add_ci = TRUE,
                              color = "steelblue") {

  if (requireNamespace("pROC", quietly = TRUE)) {
    library(pROC)
    roc_obj <- roc(y_true, y_score, ci = add_ci)
    auc_val <- auc(roc_obj)
    auc_ci <- ci.auc(roc_obj)

    # 提取 ROC 坐标
    coords_data <- coords(roc_obj, x = "all", ret = c("specificity", "sensitivity"),
                          transpose = FALSE)
    roc_df <- data.frame(
      fpr = 1 - coords_data$specificity,
      tpr = coords_data$sensitivity
    )
  } else {
    # 降级：使用 pROC 不可用时的简单计算
    library(plotROC)
    df_roc <- data.frame(
      D = y_true,
      M = y_score
    )
    p <- ggplot(df_roc, aes(d = D, m = M)) +
      geom_roc(cutoffs.at = NULL) +
      style_roc()
    return(p + labs(title = title))
  }

  p <- ggplot(roc_df, aes(x = fpr, y = tpr)) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed",
                color = "grey60", linewidth = 0.8) +
    geom_line(color = color, linewidth = 1.2) +
    coord_equal() +
    scale_x_continuous(limits = c(0, 1), expand = c(0.01, 0.01)) +
    scale_y_continuous(limits = c(0, 1), expand = c(0.01, 0.01)) +
    labs(
      title = title,
      subtitle = sprintf("AUC = %.3f (95%% CI: %.3f - %.3f)",
                         auc_val, auc_ci[1], auc_ci[3]),
      x = "1 - Specificity (False Positive Rate)",
      y = "Sensitivity (True Positive Rate)"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40"),
      panel.grid.minor = element_blank()
    )

  return(p)
}


# ============================================================================
# 2. 多条 ROC 曲线对比
# ============================================================================

#' 比较多条 ROC 曲线
#'
#' @param roc_list 命名列表，每个元素是 (y_true, y_score) 的 list
#' @param model_names 模型名称向量
#' @param title 标题
#' @return ggplot 对象
plot_multi_roc <- function(roc_list,
                            model_names = NULL,
                            title = "ROC Curve Comparison") {

  if (is.null(model_names)) {
    model_names <- names(roc_list)
  }
  if (is.null(model_names)) {
    model_names <- paste0("Model ", seq_along(roc_list))
  }

  colors <- c("steelblue", "#E74C3C", "#27AE60", "#F39C12",
              "#8E44AD", "#1ABC9C", "#E67E22", "#2C3E50")

  roc_combined <- do.call(rbind, lapply(seq_along(roc_list), function(i) {
    item <- roc_list[[i]]
    y_true <- item[[1]]
    y_score <- item[[2]]
    model_name <- model_names[i]

    if (requireNamespace("pROC", quietly = TRUE)) {
      library(pROC)
      roc_obj <- roc(y_true, y_score, quiet = TRUE)
      auc_val <- auc(roc_obj)
      coords_data <- coords(roc_obj, x = "all",
                            ret = c("specificity", "sensitivity"),
                            transpose = FALSE)
      data.frame(
        model = paste0(model_name, " (AUC=", sprintf("%.3f", auc_val), ")"),
        fpr = 1 - coords_data$specificity,
        tpr = coords_data$sensitivity
      )
    } else {
      # 简单近似
      library(plotROC)
      NULL
    }
  }))

  # 剔除可能的 NULL
  roc_combined <- roc_combined[!sapply(roc_combined, is.null)]

  p <- ggplot(roc_combined, aes(x = fpr, y = tpr, color = model)) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed",
                color = "grey60", linewidth = 0.8) +
    geom_line(linewidth = 1) +
    coord_equal() +
    scale_x_continuous(limits = c(0, 1), expand = c(0.01, 0.01)) +
    scale_y_continuous(limits = c(0, 1), expand = c(0.01, 0.01)) +
    scale_color_manual(values = colors[1:length(unique(roc_combined$model))]) +
    labs(
      title = title,
      x = "1 - Specificity (False Positive Rate)",
      y = "Sensitivity (True Positive Rate)",
      color = "Model"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      panel.grid.minor = element_blank(),
      legend.position = c(0.75, 0.25),
      legend.background = element_rect(fill = "white", color = "grey80")
    )

  return(p)
}


# ============================================================================
# 3. PR 曲线
# ============================================================================

#' 绘制 Precision-Recall 曲线
#'
#' @param y_true 真实标签
#' @param y_score 预测概率
#' @param title 标题
#' @return ggplot 对象
plot_pr_curve <- function(y_true, y_score, title = "Precision-Recall Curve") {

  # 排序
  ord <- order(y_score, decreasing = TRUE)
  y_true_sorted <- y_true[ord]
  y_score_sorted <- y_score[ord]

  # 计算 precision 和 recall
  tp <- cumsum(y_true_sorted)
  fp <- cumsum(1 - y_true_sorted)
  fn <- sum(y_true_sorted) - tp

  precision <- tp / (tp + fp)
  recall <- tp / (tp + fn)

  # 计算 PR-AUC
  pr_auc <- sum(diff(c(0, recall[!is.na(precision)])) *
                 precision[!is.na(precision)], na.rm = TRUE)

  pr_df <- data.frame(
    recall = c(0, recall[!is.na(precision) & !is.na(recall)]),
    precision = c(1, precision[!is.na(precision) & !is.na(recall)])
  )

  # 基线
  baseline <- sum(y_true) / length(y_true)

  p <- ggplot(pr_df, aes(x = recall, y = precision)) +
    geom_hline(yintercept = baseline, linetype = "dashed",
               color = "grey60", linewidth = 0.8, alpha = 0.7) +
    geom_line(color = "steelblue", linewidth = 1.2) +
    coord_cartesian(xlim = c(0, 1), ylim = c(0, 1)) +
    labs(
      title = title,
      subtitle = sprintf("PR-AUC = %.3f (Baseline = %.3f)", pr_auc, baseline),
      x = "Recall (Sensitivity)",
      y = "Precision (PPV)"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40")
    )

  return(p)
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  set.seed(42)
  n <- 200

  # 模拟数据
  y_true <- c(rep(0, n/2), rep(1, n/2))
  y_score1 <- c(rnorm(n/2, mean = 0.3, sd = 0.15),
                rnorm(n/2, mean = 0.7, sd = 0.15))
  y_score1 <- pmin(pmax(y_score1, 0), 1)

  y_score2 <- c(rnorm(n/2, mean = 0.35, sd = 0.15),
                rnorm(n/2, mean = 0.65, sd = 0.15))
  y_score2 <- pmin(pmax(y_score2, 0), 1)

  # 单条 ROC
  p1 <- plot_single_roc(y_true, y_score1, title = "Model A ROC")
  ggsave("roc_single.png", p1, width = 8, height = 7, dpi = 300)

  # 多条 ROC
  roc_list <- list(
    list(y_true, y_score1),
    list(y_true, y_score2)
  )
  p2 <- plot_multi_roc(roc_list, model_names = c("Model A", "Model B"),
                       title = "Model Comparison")
  ggsave("roc_multi.png", p2, width = 8, height = 7, dpi = 300)

  # PR 曲线
  p3 <- plot_pr_curve(y_true, y_score1, title = "PR Curve")
  ggsave("pr_curve.png", p3, width = 8, height = 7, dpi = 300)

  cat("✅ ROC 可视化模板示例完成\n")
}

cat("✅ roc_visualization_template.R 已加载\n")
cat("可用函数:\n")
cat("  plot_single_roc()    - 单条 ROC 曲线\n")
cat("  plot_multi_roc()     - 多条 ROC 曲线对比\n")
cat("  plot_pr_curve()      - Precision-Recall 曲线\n")
