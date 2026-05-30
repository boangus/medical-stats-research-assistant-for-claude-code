# bland_altman_template.R — Bland-Altman 图模板
# ==============================================
# 适用于：方法比较研究、测量一致性评估（如新旧仪器、不同阅片者）
#
# 依赖: ggplot2, dplyr, blandr (可选)
# 安装: install.packages(c("ggplot2", "dplyr", "blandr"))
#
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)
library(dplyr)

# ============================================================================
# 1. 基本 Bland-Altman 图
# ============================================================================

#' 绘制 Bland-Altman 图
#'
#' @param method1 方法1的测量值
#' @param method2 方法2的测量值
#' @param title 图表标题
#' @param x_label X 轴标签
#' @param y_label Y 轴标签
#' @param conf_int 是否显示置信区间带
#' @param proportional_bias 是否检查比例偏差（可选）
#'
#' @return list(plot = ggplot, stats = list)
plot_bland_altman <- function(method1, method2,
                               title = "Bland-Altman Plot",
                               x_label = "Mean of Two Methods",
                               y_label = "Difference (Method1 - Method2)",
                               conf_int = TRUE,
                               proportional_bias = FALSE) {

  # 计算平均值和差值
  mean_vals <- (method1 + method2) / 2
  diff_vals <- method1 - method2

  n <- length(diff_vals)
  mean_diff <- mean(diff_vals, na.rm = TRUE)
  sd_diff <- sd(diff_vals, na.rm = TRUE)

  # 一致性界限 (LoA)
  loa_upper <- mean_diff + 1.96 * sd_diff
  loa_lower <- mean_diff - 1.96 * sd_diff

  # LoA 的置信区间
  se_loa <- sqrt(3 * sd_diff^2 / n)
  loa_upper_ci_upper <- loa_upper + 1.96 * se_loa
  loa_upper_ci_lower <- loa_upper - 1.96 * se_loa
  loa_lower_ci_upper <- loa_lower + 1.96 * se_loa
  loa_lower_ci_lower <- loa_lower - 1.96 * se_loa

  # 计算在 LoA 内的比例
  within_loa <- sum(diff_vals >= loa_lower & diff_vals <= loa_upper, na.rm = TRUE)
  pct_within <- within_loa / n * 100

  # 计算重复系数 (Repeatability Coefficient)
  rc <- 1.96 * sqrt(2) * sd_diff

  df <- data.frame(
    mean = mean_vals,
    diff = diff_vals
  )

  p <- ggplot(df, aes(x = mean, y = diff)) +
    # 零线
    geom_hline(yintercept = 0, linetype = "dotted", color = "grey50",
               linewidth = 0.5) +
    # 平均差异线
    geom_hline(yintercept = mean_diff, color = "steelblue", linewidth = 1) +
    # 一致性界限
    geom_hline(yintercept = loa_upper, linetype = "dashed", color = "#E74C3C",
               linewidth = 0.8) +
    geom_hline(yintercept = loa_lower, linetype = "dashed", color = "#E74C3C",
               linewidth = 0.8) +
    # 置信区间带
    ...  # (conf_int 区域，后续实现)

  # 散点
  p <- p + geom_point(alpha = 0.6, size = 2.5, color = "steelblue") +
    labs(
      title = title,
      subtitle = sprintf(
        "Mean diff = %.2f (SD = %.2f)\nUpper LoA = %.2f, Lower LoA = %.2f\n%.1f%% within LoA",
        mean_diff, sd_diff, loa_upper, loa_lower, pct_within
      ),
      x = x_label,
      y = y_label
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40", size = 9)
    )

  # 可选：添加 LoA 置信区间带
  if (conf_int) {
    p <- p +
      annotate("rect",
               xmin = -Inf, xmax = Inf,
               ymin = loa_lower_ci_lower, ymax = loa_lower_ci_upper,
               fill = "#E74C3C", alpha = 0.05) +
      annotate("rect",
               xmin = -Inf, xmax = Inf,
               ymin = loa_upper_ci_lower, ymax = loa_upper_ci_upper,
               fill = "#E74C3C", alpha = 0.05)
  }

  # 可选：比例偏差检查
  if (proportional_bias) {
    lm_fit <- lm(diff ~ mean, data = df)
    p_val <- summary(lm_fit)$coefficients[2, 4]
    if (p_val < 0.05) {
      p <- p +
        geom_smooth(method = "lm", se = TRUE, color = "darkorange",
                    linewidth = 0.8, alpha = 0.2) +
        annotate("text", x = max(mean_vals, na.rm = TRUE) * 0.8,
                 y = max(diff_vals, na.rm = TRUE) * 0.9,
                 label = sprintf("Proportional bias p = %.3f", p_val),
                 size = 3.5, color = "darkorange", hjust = 1)
    }
  }

  stats <- list(
    n = n,
    mean_diff = mean_diff,
    sd_diff = sd_diff,
    loa_upper = loa_upper,
    loa_lower = loa_lower,
    pct_within_loa = pct_within,
    rc = rc,
    loa_upper_ci = c(loa_upper_ci_lower, loa_upper_ci_upper),
    loa_lower_ci = c(loa_lower_ci_lower, loa_lower_ci_upper)
  )

  return(list(plot = p, stats = stats))
}


# ============================================================================
# 2. 百分比差异 Bland-Altman 图（比例差异较大时用）
# ============================================================================

#' 绘制百分比 Bland-Altman 图
#'
#' 当差异与测量值成正比时使用（如测量范围跨越数量级）
#'
#' @param method1,method2 两种方法的测量值
#' @param title 标题
#' @return list(plot, stats)
plot_bland_altman_pct <- function(method1, method2,
                                   title = "Bland-Altman Plot (% Difference)") {

  mean_vals <- (method1 + method2) / 2
  pct_diff <- (method1 - method2) / mean_vals * 100

  n <- length(pct_diff)
  mean_pct <- mean(pct_diff, na.rm = TRUE)
  sd_pct <- sd(pct_diff, na.rm = TRUE)

  loa_upper <- mean_pct + 1.96 * sd_pct
  loa_lower <- mean_pct - 1.96 * sd_pct

  within_loa <- sum(pct_diff >= loa_lower & pct_diff <= loa_upper, na.rm = TRUE) / n * 100

  df <- data.frame(mean = mean_vals, pct_diff = pct_diff)

  p <- ggplot(df, aes(x = mean, y = pct_diff)) +
    geom_hline(yintercept = 0, linetype = "dotted", color = "grey50") +
    geom_hline(yintercept = mean_pct, color = "steelblue", linewidth = 1) +
    geom_hline(yintercept = loa_upper, linetype = "dashed", color = "#E74C3C") +
    geom_hline(yintercept = loa_lower, linetype = "dashed", color = "#E74C3C") +
    geom_point(alpha = 0.6, size = 2.5, color = "steelblue") +
    labs(
      title = title,
      subtitle = sprintf("Mean %% diff = %.1f%% (SD = %.1f%%)\nLoA: %.1f%% to %.1f%%",
                         mean_pct, sd_pct, loa_lower, loa_upper),
      x = "Mean of Two Methods",
      y = "% Difference (Method1 - Method2) / Mean × 100"
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40", size = 9)
    )

  return(list(
    plot = p,
    stats = list(
      mean_pct_diff = mean_pct,
      sd_pct_diff = sd_pct,
      loa_upper = loa_upper,
      loa_lower = loa_lower,
      pct_within = within_loa
    )
  ))
}


# ============================================================================
# 3. 分组 Bland-Altman 图
# ============================================================================

#' 分组 Bland-Altman 图（如不同阅片者、不同批次）
#'
#' @param method1,method2 测量值
#' @param group 分组变量
#' @param title 标题
#' @return ggplot 对象
plot_bland_altman_grouped <- function(method1, method2, group,
                                       title = "Bland-Altman Plot by Group") {

  mean_vals <- (method1 + method2) / 2
  diff_vals <- method1 - method2

  df <- data.frame(
    mean = mean_vals,
    diff = diff_vals,
    group = factor(group)
  )

  # 计算每组统计量
  group_stats <- df %>%
    group_by(group) %>%
    summarise(
      n = n(),
      mean_diff = mean(diff, na.rm = TRUE),
      sd_diff = sd(diff, na.rm = TRUE),
      loa_upper = mean_diff + 1.96 * sd_diff,
      loa_lower = mean_diff - 1.96 * sd_diff,
      .groups = "drop"
    )

  p <- ggplot(df, aes(x = mean, y = diff, color = group)) +
    geom_point(alpha = 0.6, size = 2) +
    geom_hline(yintercept = 0, linetype = "dotted", color = "grey50") +
    # 各组的平均差异线
    geom_hline(data = group_stats,
               aes(yintercept = mean_diff, color = group),
               linewidth = 1, alpha = 0.8) +
    # 一致性界限（使用虚线，各组的稍微偏移以避免重叠）
    geom_hline(data = group_stats,
               aes(yintercept = loa_upper, color = group),
               linetype = "dashed", linewidth = 0.6, alpha = 0.6) +
    geom_hline(data = group_stats,
               aes(yintercept = loa_lower, color = group),
               linetype = "dashed", linewidth = 0.6, alpha = 0.6) +
    labs(
      title = title,
      x = "Mean of Two Methods",
      y = "Difference"
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = "bottom"
    )

  attr(p, "group_stats") <- group_stats
  return(p)
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  set.seed(42)
  n <- 100

  # 模拟数据
  true_val <- runif(n, 10, 100)
  method1 <- true_val + rnorm(n, 0, 3)
  method2 <- true_val + rnorm(n, 2, 4)  # 有系统偏差

  # 基本 Bland-Altman
  res <- plot_bland_altman(method1, method2,
                           title = "Device A vs Device B")
  print(res$plot)
  print(res$stats)
  ggsave("bland_altman.png", res$plot, width = 8, height = 7, dpi = 300)

  # 百分比 Bland-Altman（当差异与值成比例时）
  method1_prop <- true_val * rnorm(n, 1, 0.05) + 2
  method2_prop <- true_val * rnorm(n, 0.95, 0.08) + 3
  res2 <- plot_bland_altman_pct(method1_prop, method2_prop)
  ggsave("bland_altman_pct.png", res2$plot, width = 8, height = 7, dpi = 300)

  cat("✅ Bland-Altman 模板示例完成\n")
}

cat("✅ bland_altman_template.R 已加载\n")
cat("可用函数:\n")
cat("  plot_bland_altman()          - 基本 BA 图\n")
cat("  plot_bland_altman_pct()      - 百分比差异 BA 图\n")
cat("  plot_bland_altman_grouped()  - 分组 BA 图\n")
