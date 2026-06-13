# =============================================================================
# 倾向得分诊断模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 MatchIt + cobalt + ggplot2，提供倾向得分加权后的诊断工具集
#
# 功能:
#   - Love plot: 加权前后标准化均值差
#   - 权重分布: 直方图 + 极端权重检测
#   - 倾向得分重叠: 处理组/对照组密度图
#   - 协变量平衡表: 加权前后 SMD 对比
#   - 综合诊断摘要: 一键汇总全部诊断
#
# 参考:
#   MatchIt: https://kosukeimai.github.io/MatchIt/
#   cobalt: https://ngreifer.github.io/cobalt/
#   Austin (2011) An Introduction to Propensity Score Methods
#
# 依赖:
#   install.packages(c("MatchIt", "cobalt", "ggplot2", "dplyr"))
# =============================================================================

library(cobalt)
library(ggplot2)
library(dplyr)

# =============================================================================
# 1. Love Plot — 标准化均值差图
# =============================================================================

#' 绘制 Love plot（加权前后标准化均值差对比）
#'
#' Love plot 是倾向得分诊断的核心可视化，展示各协变量在
#' 加权前后的标准化均值差 (SMD)。理想情况下加权后所有
#' 协变量的 SMD 应 < 0.1。
#'
#' @param data 数据框
#' @param treatment 处理变量名（字符），应为二分类因子
#' @param covariates 协变量名向量（字符）
#' @param weights 权重向量（数值），通常来自 IPTW 或 MatchIt
#' @param threshold SMD 阈值线，默认 0.1
#' @param title 图表标题
#'
#' @return ggplot 对象
love_plot <- function(data, treatment, covariates, weights,
                      threshold = 0.1,
                      title = "Love Plot: Standardized Mean Differences") {

  # 计算加权前后的 SMD
  smd_before <- numeric(length(covariates))
  smd_after  <- numeric(length(covariates))

  treat_vec <- as.numeric(as.factor(data[[treatment]])) - 1

  for (i in seq_along(covariates)) {
    x <- data[[covariates[i]]]
    if (is.numeric(x)) {
      # 加权前 SMD
      smd_before[i] <- abs(
        (mean(x[treat_vec == 1], na.rm = TRUE) -
           mean(x[treat_vec == 0], na.rm = TRUE)) /
          sqrt((var(x[treat_vec == 1], na.rm = TRUE) +
                  var(x[treat_vec == 0], na.rm = TRUE)) / 2)
      )
      # 加权后 SMD
      w <- weights
      wm1 <- weighted.mean(x[treat_vec == 1], w[treat_vec == 1], na.rm = TRUE)
      wm0 <- weighted.mean(x[treat_vec == 0], w[treat_vec == 0], na.rm = TRUE)
      # 加权方差估计
      wv1 <- Hmisc::wtd.var(x[treat_vec == 1], w[treat_vec == 1], na.rm = TRUE)
      wv0 <- Hmisc::wtd.var(x[treat_vec == 0], w[treat_vec == 0], na.rm = TRUE)
      smd_after[i] <- abs(wm1 - wm0) / sqrt((wv1 + wv0) / 2)
    } else {
      # 因子变量: 使用比例差
      tbl <- table(x, treat_vec)
      prop1 <- tbl[, 2] / sum(tbl[, 2])
      prop0 <- tbl[, 1] / sum(tbl[, 1])
      smd_before[i] <- sqrt(sum((prop1 - prop0)^2))
      # 加权后（简化处理，使用数值化后的 SMD）
      xn <- as.numeric(as.factor(x))
      smd_after[i] <- abs(
        weighted.mean(xn[treat_vec == 1], weights[treat_vec == 1], na.rm = TRUE) -
          weighted.mean(xn[treat_vec == 0], weights[treat_vec == 0], na.rm = TRUE)
      ) / sd(xn, na.rm = TRUE)
    }
  }

  # 构建绘图数据
  plot_df <- data.frame(
    covariate = rep(covariates, 2),
    smd       = c(smd_before, smd_after),
    group     = rep(c("Before Weighting", "After Weighting"), each = length(covariates)),
    stringsAsFactors = FALSE
  )

  p <- ggplot(plot_df, aes(x = smd, y = reorder(covariate, smd),
                            color = group, shape = group)) +
    geom_point(size = 3) +
    geom_vline(xintercept = threshold, linetype = "dashed",
               color = "grey40", linewidth = 0.6) +
    geom_line(aes(group = covariate), color = "grey60",
              linewidth = 0.3, linetype = "dotted") +
    scale_color_manual(values = c("Before Weighting" = "#E64B35",
                                  "After Weighting"  = "#4DBBD5")) +
    scale_shape_manual(values = c("Before Weighting" = 16,
                                  "After Weighting"  = 17)) +
    labs(title = title,
         x = "Absolute Standardized Mean Difference",
         y = NULL,
         color = NULL, shape = NULL) +
    theme_bw(base_size = 12) +
    theme(legend.position = "bottom")

  return(p)
}

# =============================================================================
# 2. 权重分布图
# =============================================================================

#' 绘制权重分布图并检测极端权重
#'
#' 直方图叠加密度曲线，按处理组分面。标注极端权重阈值
#' （默认 99% 分位数或权重 > 10），返回极端权重摘要。
#'
#' @param weights 权重向量
#' @param treatment 处理变量（因子或二分类向量）
#' @param extreme_pct 极端权重百分位阈值，默认 0.99
#' @param extreme_abs 极端权重绝对阈值，默认 10
#' @param binwidth 直方图组距，默认 0.05
#'
#' @return list(plot = ggplot, summary = data.frame)
weight_distribution <- function(weights, treatment,
                                extreme_pct = 0.99,
                                extreme_abs = 10,
                                binwidth = 0.05) {

  plot_df <- data.frame(
    weight    = weights,
    treatment = as.factor(treatment)
  )

  # 极端权重检测
  pct_threshold <- quantile(weights, probs = extreme_pct, na.rm = TRUE)
  abs_threshold <- extreme_abs
  extreme_idx   <- which(weights > pct_threshold | weights > abs_threshold)

  summary_df <- data.frame(
    metric = c("N", "Mean", "SD", "Min", "Median", "Max",
               paste0(extreme_pct * 100, "% Quantile"),
               paste0("N > ", extreme_pct * 100, "% quantile"),
               paste0("N > ", extreme_abs)),
    value = c(length(weights),
              round(mean(weights, na.rm = TRUE), 4),
              round(sd(weights, na.rm = TRUE), 4),
              round(min(weights, na.rm = TRUE), 4),
              round(median(weights, na.rm = TRUE), 4),
              round(max(weights, na.rm = TRUE), 4),
              round(pct_threshold, 4),
              sum(weights > pct_threshold, na.rm = TRUE),
              sum(weights > abs_threshold, na.rm = TRUE)),
    stringsAsFactors = FALSE
  )

  cat("=== 权重分布摘要 ===\n")
  print(summary_df, row.names = FALSE)

  if (length(extreme_idx) > 0) {
    cat("\n! 检测到", length(extreme_idx), "个极端权重值\n")
    cat("  范围:", round(min(weights[extreme_idx]), 3),
        "-", round(max(weights[extreme_idx]), 3), "\n")
    cat("  建议: 考虑使用权重截断 (truncation) 以降低极端值影响\n")
  }

  p <- ggplot(plot_df, aes(x = weight, fill = treatment)) +
    geom_histogram(binwidth = binwidth, alpha = 0.6,
                   position = "identity", color = "white") +
    geom_density(aes(y = after_stat(count) * binwidth, color = treatment),
                 linewidth = 0.8, show.legend = FALSE) +
    geom_vline(xintercept = pct_threshold, linetype = "dashed",
               color = "darkred", linewidth = 0.6) +
    facet_wrap(~treatment, ncol = 1) +
    scale_fill_manual(values = c("#4DBBD5", "#E64B35")) +
    scale_color_manual(values = c("#3C8DBC", "#C43B2B")) +
    labs(title = "Distribution of Propensity Score Weights",
         subtitle = paste0("Red dashed line = ", extreme_pct * 100,
                           "% quantile (", round(pct_threshold, 3), ")"),
         x = "Weight", y = "Count", fill = "Treatment") +
    theme_bw(base_size = 12) +
    theme(legend.position = "bottom")

  return(list(plot = p, summary = summary_df, extreme_idx = extreme_idx))
}

# =============================================================================
# 3. 倾向得分重叠密度图
# =============================================================================

#' 绘制处理组与对照组倾向得分的重叠密度图
#'
#' 检查两组倾向得分的分布重叠程度，这是使用倾向得分方法的
#' 前提假设。若重叠不足（即存在"区域无重叠"），则外部有效性受限。
#'
#' @param ps_treated 处理组的倾向得分向量
#' @param ps_control 对照组的倾向得分向量
#' @param bandwidth 核密度带宽，默认 "SJ"（Sheather-Jones 法）
#'
#' @return list(plot = ggplot, overlap_coefficient = numeric)
ps_overlap_plot <- function(ps_treated, ps_control,
                            bandwidth = "SJ") {

  # 计算重叠系数 (Weitzman, 1970)
  # 使用数值积分估算两个密度曲线的重叠面积
  x_grid <- seq(0, 1, length.out = 512)
  d_t <- density(ps_treated, bw = bandwidth, from = 0, to = 1, n = 512)
  d_c <- density(ps_control, bw = bandwidth, from = 0, to = 1, n = 512)
  overlap <- sum(pmin(d_t$y, d_c$y)) * (d_t$x[2] - d_t$x[1])

  cat("=== 倾向得分重叠诊断 ===\n")
  cat("处理组 N:", length(ps_treated),
      "| 均值:", round(mean(ps_treated), 4),
      "| 范围:", round(range(ps_treated)[1], 3), "-",
      round(range(ps_treated)[2], 3), "\n")
  cat("对照组 N:", length(ps_control),
      "| 均值:", round(mean(ps_control), 4),
      "| 范围:", round(range(ps_control)[1], 3), "-",
      round(range(ps_control)[2], 3), "\n")
  cat("重叠系数 (OVL):", round(overlap, 4), "\n")

  if (overlap < 0.5) {
    cat("! 警告: 重叠系数 < 0.5，两组倾向得分分布差异较大\n")
    cat("  建议: 检查是否存在极端倾向得分，考虑裁剪或限制分析范围\n")
  } else if (overlap < 0.7) {
    cat("! 注意: 重叠系数 < 0.7，部分区域重叠有限\n")
  } else {
    cat("  重叠良好，满足倾向得分方法的前提假设\n")
  }

  plot_df <- data.frame(
    ps    = c(ps_treated, ps_control),
    group = rep(c("Treatment", "Control"),
                c(length(ps_treated), length(ps_control)))
  )

  p <- ggplot(plot_df, aes(x = ps, fill = group)) +
    geom_density(alpha = 0.4, linewidth = 0.6) +
    scale_fill_manual(values = c("Treatment" = "#E64B35",
                                  "Control"   = "#4DBBD5")) +
    labs(title = "Propensity Score Overlap",
         subtitle = sprintf("Overlap Coefficient (OVL) = %.3f", overlap),
         x = "Propensity Score",
         y = "Density",
         fill = "Group") +
    theme_bw(base_size = 12) +
    theme(legend.position = "bottom")

  return(list(plot = p, overlap_coefficient = overlap))
}

# =============================================================================
# 4. 协变量平衡表
# =============================================================================

#' 生成加权前后的协变量平衡表
#'
#' 计算每个协变量在加权前后的标准化均值差 (SMD)，
#' 并标注是否满足平衡标准 (SMD < 0.1)。
#'
#' @param data 数据框
#' @param treatment 处理变量名（字符）
#' @param covariates 协变量名向量（字符）
#' @param weights 权重向量
#' @param threshold SMD 阈值，默认 0.1
#'
#' @return data.frame 包含变量名、加权前后 SMD、是否平衡
balance_table <- function(data, treatment, covariates, weights,
                          threshold = 0.1) {

  treat_vec <- as.numeric(as.factor(data[[treatment]])) - 1

  results <- data.frame(
    variable     = covariates,
    smd_before   = NA_real_,
    smd_after    = NA_real_,
    balanced     = NA_character_,
    stringsAsFactors = FALSE
  )

  for (i in seq_along(covariates)) {
    x <- data[[covariates[i]]]

    if (is.numeric(x)) {
      # 加权前 SMD
      m1 <- mean(x[treat_vec == 1], na.rm = TRUE)
      m0 <- mean(x[treat_vec == 0], na.rm = TRUE)
      pooled_sd <- sqrt((var(x[treat_vec == 1], na.rm = TRUE) +
                           var(x[treat_vec == 0], na.rm = TRUE)) / 2)
      results$smd_before[i] <- abs(m1 - m0) / pooled_sd

      # 加权后 SMD
      wm1 <- weighted.mean(x[treat_vec == 1], weights[treat_vec == 1], na.rm = TRUE)
      wm0 <- weighted.mean(x[treat_vec == 0], weights[treat_vec == 0], na.rm = TRUE)
      # 使用未加权 pooled SD 作为分母（标准做法）
      results$smd_after[i] <- abs(wm1 - wm0) / pooled_sd
    } else {
      # 分类变量: 使用多类别 SMD (Yang & Dalton, 2012)
      xn <- as.numeric(as.factor(x))
      m1 <- mean(xn[treat_vec == 1], na.rm = TRUE)
      m0 <- mean(xn[treat_vec == 0], na.rm = TRUE)
      pooled_sd <- sqrt((var(xn[treat_vec == 1], na.rm = TRUE) +
                           var(xn[treat_vec == 0], na.rm = TRUE)) / 2)
      results$smd_before[i] <- abs(m1 - m0) / pooled_sd

      wm1 <- weighted.mean(xn[treat_vec == 1], weights[treat_vec == 1], na.rm = TRUE)
      wm0 <- weighted.mean(xn[treat_vec == 0], weights[treat_vec == 0], na.rm = TRUE)
      results$smd_after[i] <- abs(wm1 - wm0) / pooled_sd
    }
  }

  # 四舍五入
  results$smd_before <- round(results$smd_before, 4)
  results$smd_after  <- round(results$smd_after, 4)

  # 判断平衡
  results$balanced <- ifelse(results$smd_after < threshold, "Yes", "No")

  cat("=== 协变量平衡表 ===\n")
  cat("阈值: SMD <", threshold, "\n\n")
  print(results, row.names = FALSE)

  n_balanced <- sum(results$balanced == "Yes")
  cat("\n平衡比例:", n_balanced, "/", nrow(results),
      "(", round(n_balanced / nrow(results) * 100, 1), "%)\n")

  if (n_balanced < nrow(results)) {
    cat("! 以下变量未达到平衡:\n")
    cat("  ", paste(results$variable[results$balanced == "No"], collapse = ", "), "\n")
    cat("  建议: 考虑将这些变量纳入模型进行回归调整\n")
  }

  return(results)
}

# =============================================================================
# 5. 综合诊断摘要
# =============================================================================

#' 倾向得分综合诊断摘要
#'
#' 一次性运行全部诊断并输出汇总报告。
#'
#' @param data 数据框
#' @param treatment 处理变量名（字符）
#' @param covariates 协变量名向量（字符）
#' @param weights 权重向量
#' @param ps 倾向得分向量（可选，用于重叠图）
#' @param save_dir 图片保存目录（可选，为 NULL 则不保存）
#'
#' @return list(love_plot, weight_dist, overlap_plot, balance_tbl)
ps_diagnostics_summary <- function(data, treatment, covariates, weights,
                                    ps = NULL, save_dir = NULL) {

  cat("============================================================\n")
  cat(" 倾向得分诊断综合报告\n")
  cat("============================================================\n")
  cat("样本量:", nrow(data), "\n")
  cat("处理变量:", treatment, "\n")
  cat("协变量数:", length(covariates), "\n")
  cat("权重范围:", round(min(weights), 4), "-",
      round(max(weights), 4), "\n\n")

  # 1. Love plot
  cat("--- [1/4] Love Plot ---\n")
  p_love <- love_plot(data, treatment, covariates, weights)

  # 2. 权重分布
  cat("\n--- [2/4] 权重分布 ---\n")
  wt_result <- weight_distribution(weights, data[[treatment]])

  # 3. 倾向得分重叠
  p_overlap <- NULL
  if (!is.null(ps)) {
    cat("\n--- [3/4] 倾向得分重叠 ---\n")
    treat_idx <- as.numeric(as.factor(data[[treatment]])) == 2
    ps_t <- ps[treat_idx]
    ps_c <- ps[!treat_idx]
    overlap_result <- ps_overlap_plot(ps_t, ps_c)
    p_overlap <- overlap_result$plot
  } else {
    cat("\n--- [3/4] 倾向得分重叠 (跳过 - 未提供 ps 向量) ---\n")
  }

  # 4. 平衡表
  cat("\n--- [4/4] 协变量平衡表 ---\n")
  bal_tbl <- balance_table(data, treatment, covariates, weights)

  # 保存图片
  if (!is.null(save_dir)) {
    if (!dir.exists(save_dir)) dir.create(save_dir, recursive = TRUE)

    ggsave(file.path(save_dir, "ps_love_plot.pdf"),
           p_love, width = 10, height = 7)
    ggsave(file.path(save_dir, "ps_weight_distribution.pdf"),
           wt_result$plot, width = 10, height = 8)
    if (!is.null(p_overlap)) {
      ggsave(file.path(save_dir, "ps_overlap_density.pdf"),
             p_overlap, width = 10, height = 6)
    }
    cat("\n图片已保存至:", save_dir, "\n")
  }

  cat("\n============================================================\n")
  cat(" 诊断完成\n")
  cat("============================================================\n")

  invisible(list(
    love_plot      = p_love,
    weight_dist    = wt_result,
    overlap_plot   = p_overlap,
    balance_table  = bal_tbl
  ))
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  library(MatchIt)

  # 1. 模拟数据
  set.seed(20250101)
  n <- 500
  demo_data <- data.frame(
    age    = rnorm(n, 60, 10),
    bmi    = rnorm(n, 25, 4),
    gender = factor(rbinom(n, 1, 0.5), labels = c("Male", "Female")),
    smoke  = factor(rbinom(n, 1, 0.3), labels = c("No", "Yes")),
    treat  = factor(rbinom(n, 1, 0.4), labels = c("Control", "Treatment"))
  )
  # 使倾向得分与协变量相关
  ps_true <- with(demo_data,
                   plogis(-1 + 0.02 * age + 0.05 * bmi +
                            0.5 * (gender == "Female") + 0.3 * (smoke == "Yes")))
  demo_data$treat <- factor(rbinom(n, 1, ps_true), labels = c("Control", "Treatment"))

  covs <- c("age", "bmi", "gender", "smoke")

  # 2. 计算 IPTW 权重 (使用 WeightIt)
  # library(WeightIt)
  # w_out <- weightit(treat ~ age + bmi + gender + smoke,
  #                   data = demo_data, method = "ps", stabilize = TRUE)
  # weights_vec <- w_out$weights
  # ps_vec      <- w_out$ps

  # 或使用 MatchIt
  m_out <- matchit(treat ~ age + bmi + gender + smoke,
                   data = demo_data, method = "nearest", distance = "glm")

  weights_vec <- ifelse(demo_data$treat == "Treatment",
                         1 / m_out$distance,
                         1 / (1 - m_out$distance))
  ps_vec <- m_out$distance

  # 3. 单项诊断
  love_plot(demo_data, "treat", covs, weights_vec)
  weight_distribution(weights_vec, demo_data$treat)
  ps_overlap_plot(ps_vec[demo_data$treat == "Treatment"],
                  ps_vec[demo_data$treat == "Control"])
  balance_table(demo_data, "treat", covs, weights_vec)

  # 4. 综合诊断
  ps_diagnostics_summary(
    data      = demo_data,
    treatment = "treat",
    covariates = covs,
    weights   = weights_vec,
    ps        = ps_vec,
    save_dir  = "outcome/figures/ps_diagnostics"
  )
}
