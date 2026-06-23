# forest_plot_template.R — 森林图模板
# =====================================
# 适用于：Meta 分析、多变量回归的 OR/HR/β 可视化
#
# 依赖: ggplot2, dplyr, tidyr
# 安装: install.packages(c("ggplot2", "dplyr", "tidyr"))
#
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)
library(dplyr)

# ============================================================================
# 1. 从回归结果创建森林图
# ============================================================================

#' 从回归结果表创建森林图
#'
#' @param data 数据框，需包含以下列：
#'   - variable: 变量名
#'   - estimate: 效应量 (OR/HR/β)
#'   - lower: 95% CI 下限
#'   - upper: 95% CI 上限
#'   - p_value: p 值（可选）
#' @param ref_line 参考线（OR/HR=1, β=0），默认 1
#' @param x_label X 轴标签
#' @param title 图表标题
#' @param add_pvalue 是否显示 p 值列
#' @param estimate_name 效应量名称（"OR", "HR", "β"）
#'
#' @return ggplot 对象
create_forest_plot <- function(data,
                                ref_line = 1,
                                x_label = "Odds Ratio (95% CI)",
                                title = "Forest Plot",
                                add_pvalue = TRUE,
                                estimate_name = "OR") {

  # 格式化效应量显示
  data <- data %>%
    mutate(
      estimate_display = sprintf("%.3f", estimate),
      ci_display = sprintf("(%.3f, %.3f)", lower, upper),
      label = paste(variable, estimate_display, ci_display, sep = "  ")
    )

  # 按效应量排序
  data <- data %>%
    arrange(desc(estimate)) %>%
    mutate(
      id = row_number(),
      variable = factor(variable, levels = rev(variable))
    )

  p <- ggplot(data, aes(x = estimate, y = variable)) +
    # 参考线
    geom_vline(xintercept = ref_line, linetype = "dashed",
               color = "grey50", linewidth = 0.5) +
    # 置信区间线段
    geom_segment(aes(x = lower, xend = upper, yend = variable),
                 color = "grey40", linewidth = 1.2) +
    # 点估计
    geom_point(size = 3, color = "steelblue") +
    # 坐标轴
    scale_x_continuous(trans = if (ref_line == 1) "log10" else "identity") +
    labs(
      title = title,
      x = x_label,
      y = NULL
    ) +
    theme_minimal(base_size = 12) +
    theme(
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_blank(),
      plot.title = element_text(face = "bold", hjust = 0.5),
      axis.text.y = element_text(size = 10),
      axis.text.x = element_text(size = 9)
    )

  # 添加显著性标记
  if ("p_value" %in% names(data)) {
    data <- data %>%
      mutate(
        sig = case_when(
          p_value < 0.001 ~ "***",
          p_value < 0.01  ~ "**",
          p_value < 0.05  ~ "*",
          TRUE             ~ "ns"
        )
      )
  }

  return(p)
}


#' 从 Cox 模型结果创建森林图
#'
#' @param cox_model CoxPHFitter（R survival 包）的拟合结果
#' @param ... 传递给 create_forest_plot 的其他参数
#'
#' @return ggplot 对象
cox_to_forest <- function(cox_model, ...) {
  s <- summary(cox_model)
  hr <- s$conf.int
  pval <- s$coefficients[, "Pr(>|z|)"]

  data <- data.frame(
    variable = rownames(hr),
    estimate = hr[, "exp(coef)"],
    lower = hr[, "lower .95"],
    upper = hr[, "upper .95"],
    p_value = pval
  )

  create_forest_plot(data, ref_line = 1,
                     x_label = "Hazard Ratio (95% CI)",
                     estimate_name = "HR", ...)
}


#' 从 Logistic 模型结果创建森林图
#'
#' @param log_model glm(family=binomial) 的拟合结果
#' @param ... 传递给 create_forest_plot 的其他参数
#'
#' @return ggplot 对象
logistic_to_forest <- function(log_model, ...) {
  s <- summary(log_model)
  or <- exp(coef(log_model))
  ci <- exp(confint(log_model))
  pval <- coef(s)[, "Pr(>|z|)"]

  data <- data.frame(
    variable = names(or),
    estimate = or,
    lower = ci[, 1],
    upper = ci[, 2],
    p_value = pval
  )
  # 去掉截距
  data <- data[data$variable != "(Intercept)", ]

  create_forest_plot(data, ref_line = 1,
                     x_label = "Odds Ratio (95% CI)",
                     estimate_name = "OR", ...)
}


# ============================================================================
# 2. 分组森林图（按子组分析）
# ============================================================================

#' 创建分组森林图（用于亚组分析）
#'
#' @param data 数据框，需包含：
#'   - subgroup: 亚组名称
#'   - level: 亚组水平
#'   - estimate, lower, upper, p_value
#' @param ref_line 参考线
#' @param title 标题
#'
#' @return ggplot 对象
create_subgroup_forest <- function(data,
                                    ref_line = 1,
                                    title = "Subgroup Analysis") {

  data <- data %>%
    mutate(
      subgroup = factor(subgroup, levels = rev(unique(subgroup))),
      label = paste(level, sprintf("%.3f (%.3f, %.3f)", estimate, lower, upper))
    )

  # 添加亚组间的间隔线
  subgroup_lines <- data %>%
    group_by(subgroup) %>%
    summarise(y_pos = min(as.numeric(factor(level, levels = unique(level))))) %>%
    mutate(y_pos = y_pos - 0.5)

  p <- ggplot(data, aes(x = estimate, y = level)) +
    geom_vline(xintercept = ref_line, linetype = "dashed",
               color = "grey50", linewidth = 0.5) +
    geom_segment(aes(x = lower, xend = upper, yend = level),
                 color = "grey40", linewidth = 1) +
    geom_point(size = 2.5, color = "steelblue") +
    # 亚组标题
    geom_text(data = data %>% group_by(subgroup) %>% slice(1),
              aes(label = paste0("  ", subgroup)),
              x = -Inf, hjust = 0, fontface = "bold", size = 3.5) +
    facet_grid(subgroup ~ ., scales = "free_y", space = "free_y") +
    scale_x_continuous(trans = if (ref_line == 1) "log10" else "identity") +
    labs(title = title, x = "Effect Size (95% CI)", y = NULL) +
    theme_minimal(base_size = 11) +
    theme(
      strip.text = element_blank(),
      panel.spacing = unit(0.1, "lines"),
      panel.grid.minor = element_blank(),
      plot.title = element_text(face = "bold", hjust = 0.5)
    )

  return(p)
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  # 示例数据
  demo_data <- data.frame(
    variable = c("Age (per 10 years)", "BMI (per 5 units)",
                 "Smoking", "Hypertension", "Diabetes",
                 "Physical Activity"),
    estimate = c(1.45, 1.22, 2.10, 1.80, 1.65, 0.75),
    lower = c(1.20, 1.05, 1.60, 1.40, 1.30, 0.58),
    upper = c(1.75, 1.42, 2.75, 2.30, 2.10, 0.97),
    p_value = c(0.001, 0.015, 0.002, 0.008, 0.012, 0.030)
  )

  p <- create_forest_plot(demo_data,
                          title = "Risk Factors for Cardiovascular Disease",
                          x_label = "Odds Ratio (95% CI)")

  ggsave("forest_plot.png", p, width = 10, height = 6, dpi = 300)

  # 亚组分析示例
  subgroup_data <- data.frame(
    subgroup = rep(c("Age", "Gender", "Region"), each = 2),
    level = c("< 60", ">= 60", "Male", "Female", "Urban", "Rural"),
    estimate = c(1.30, 1.60, 1.45, 1.38, 1.50, 1.35),
    lower = c(0.95, 1.20, 1.10, 1.02, 1.15, 1.00),
    upper = c(1.78, 2.13, 1.91, 1.87, 1.96, 1.82),
    p_value = c(0.10, 0.002, 0.01, 0.04, 0.005, 0.05)
  )

  p2 <- create_subgroup_forest(subgroup_data)
  ggsave("subgroup_forest.png", p2, width = 10, height = 7, dpi = 300)
}

cat("✅ forest_plot_template.R 已加载\n")
cat("可用函数:\n")
cat("  create_forest_plot()        - 通用森林图\n")
cat("  cox_to_forest()            - Cox 模型森林图\n")
cat("  logistic_to_forest()       - Logistic 模型森林图\n")
cat("  create_subgroup_forest()   - 亚组分析森林图\n")
