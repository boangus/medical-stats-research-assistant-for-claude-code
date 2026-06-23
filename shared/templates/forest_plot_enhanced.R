# forest_plot_enhanced.R — 森林图增强模板
# ==========================================
# 在 forest_plot_template.R 基础上增加：
#   1. 亚组分析森林图 (HR/OR 圆点图 + 总HR阴影)
#   2. NEJM 风格森林图 (带表格列)
#   3. 单/多因素同图森林图
#   4. Meta 分析森林图 (异质性标注)
#
# 依赖: ggplot2, grid, gridExtra
# 安装: install.packages(c("ggplot2", "grid", "gridExtra"))
#
# 参考: 实战医学统计课程 Ch12, NEJM/Lancet 森林图样式
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)

# ============================================================================
# 1. 亚组分析森林图 (临床研究最常用)
# ============================================================================

#' 亚组分析森林图
#'
#' 绘制亚组 HR/OR 森林图，含总效应汇总线和交互作用 P 值。
#' 样式参考 NEJM/Lancet 常见的亚组分析图。
#'
#' @param data 数据框，需包含列：
#'   - subgroup: 亚组名称
#'   - n: 亚组样本量
#'   - hr: 效应量 (HR/OR)
#'   - lower: 95% CI 下限
#'   - upper: 95% CI 上限
#'   - p_interaction: 交互作用 P 值 (可选，仅亚组行)
#'   - is_overall: 是否为总体行 (逻辑值)
#' @param x_label X 轴标签
#' @param effect_name 效应量名称 ("HR" 或 "OR")
#' @param ref_line 参考线 (默认 1)
#' @param xlim X 轴范围
#'
#' @return ggplot 对象
forest_subgroup <- function(data, x_label = "Hazard Ratio (95% CI)",
                             effect_name = "HR", ref_line = 1,
                             xlim = NULL) {

  # 格式化标签
  data$label_text <- ifelse(
    data$is_overall,
    paste0(data$subgroup, "    ", sprintf("%.2f", data$hr),
           " (", sprintf("%.2f", data$lower), "-", sprintf("%.2f", data$upper), ")"),
    paste0("  ", data$subgroup, "    ", sprintf("%.2f", data$hr),
           " (", sprintf("%.2f", data$lower), "-", sprintf("%.2f", data$upper), ")")
  )

  # 交互作用 P 值标签
  data$p_label <- ifelse(!is.na(data$p_interaction),
                          paste0("P = ", format.pval(data$p_interaction, digits = 2)),
                          "")

  # Y 轴位置 (倒序)
  data$y_pos <- nrow(data):1

  # 分类: 亚组标题 vs 数据行
  data$line_type <- ifelse(data$is_overall, "overall", "subgroup")

  # 默认 X 轴范围
  if (is.null(xlim)) {
    xlim <- c(max(0.1, min(data$lower, na.rm = TRUE) * 0.8),
              max(data$upper, na.rm = TRUE) * 1.2)
  }

  p <- ggplot(data, aes(x = hr, y = y_pos)) +
    # 参考线
    geom_vline(xintercept = ref_line, linetype = "dashed",
               color = "grey60", linewidth = 0.6) +
    # 置信区间线
    geom_segment(aes(x = lower, xend = upper, yend = y_pos,
                     linewidth = line_type),
                 color = "#2E86C1") +
    # 点估计
    geom_point(aes(size = line_type, color = line_type)) +
    # 尺度
    scale_linewidth_manual(values = c("subgroup" = 0.8, "overall" = 1.5), guide = "none") +
    scale_size_manual(values = c("subgroup" = 2.5, "overall" = 4), guide = "none") +
    scale_color_manual(values = c("subgroup" = "#2E86C1", "overall" = "#E74C3C"),
                        guide = "none") +
    # X 轴
    scale_x_continuous(trans = "log10", limits = xlim,
                        breaks = c(0.5, 0.75, 1, 1.5, 2, 3)) +
    # Y 轴标签
    scale_y_continuous(breaks = data$y_pos, labels = data$label_text,
                        expand = c(0.02, 0)) +
    # 交互作用 P 值标注
    geom_text(aes(x = max(xlim) * 0.95, label = p_label),
              hjust = 1, size = 3.2, color = "grey30") +
    # 主题
    theme_classic(base_size = 11) +
    theme(
      axis.text.y = element_text(hjust = 0, size = 9, family = "mono"),
      axis.ticks.y = element_blank(),
      axis.line.y = element_blank(),
      panel.grid = element_blank(),
      plot.title = element_text(face = "bold", hjust = 0.5)
    ) +
    labs(
      title = paste0("Subgroup Analysis: ", effect_name),
      x = x_label,
      y = NULL
    )

  return(p)
}


# ============================================================================
# 2. NEJM 风格森林图 (带表格列)
# ============================================================================

#' NEJM 风格森林图 (左侧表格 + 右侧图形)
#'
#' @param data 数据框，需包含：variable, n, events, hr, lower, upper, p_value
#' @param table_width 左侧表格宽度比例 (默认 0.4)
#'
#' @return gtable 对象 (可用 grid::grid.draw 绘制)
forest_nejm <- function(data, table_width = 0.4) {
  library(grid)
  library(gridExtra)

  # 格式化表格文本
  data$hr_text <- sprintf("%.2f (%.2f-%.2f)", data$hr, data$lower, data$upper)
  data$p_text <- format.pval(data$p_value, digits = 2)

  # 排序
  data <- data[order(-data$hr), ]
  data$y_pos <- nrow(data):1

  # 左侧表格
  table_grob <- tableGrob(
    data.frame(
      Variable = data$variable,
      N = data$n,
      Events = data$events,
      `HR (95% CI)` = data$hr_text,
      P = data$p_text
    ),
    rows = NULL,
    theme = ttheme_minimal(
      core = list(fg_params = list(size = 9)),
      colhead = list(fg_params = list(size = 9, fontface = "bold"))
    )
  )

  # 右侧森林图
  p_forest <- ggplot(data, aes(x = hr, y = y_pos)) +
    geom_vline(xintercept = 1, linetype = "dashed", color = "grey60") +
    geom_segment(aes(x = lower, xend = upper, yend = y_pos),
                 color = "#2E86C1", linewidth = 1) +
    geom_point(color = "#2E86C1", size = 3) +
    scale_x_continuous(trans = "log10",
                        breaks = c(0.5, 0.75, 1, 1.5, 2, 3)) +
    scale_y_continuous(breaks = data$y_pos, labels = data$variable) +
    theme_classic(base_size = 10) +
    theme(axis.text.y = element_blank(), axis.ticks.y = element_blank()) +
    labs(x = "HR (95% CI)", y = NULL)

  # 合并
  combined <- arrangeGrob(
    table_grob, p_forest,
    ncol = 2,
    widths = c(table_width, 1 - table_width)
  )

  return(combined)
}


# ============================================================================
# 3. 单/多因素同图森林图
# ============================================================================

#' 单因素 + 多因素同图森林图
#'
#' 在同一张图上展示单因素和多因素回归结果，便于比较。
#'
#' @param data 数据框，需包含：variable, hr_crude, lower_crude, upper_crude,
#'   hr_adjusted, lower_adjusted, upper_adjusted
#' @param effect_name 效应量名称 ("HR" 或 "OR")
#'
#' @return ggplot 对象
forest_crude_adjusted <- function(data, effect_name = "HR") {

  # 转换为长格式
  df_crude <- data.frame(
    variable = data$variable,
    hr = data$hr_crude,
    lower = data$lower_crude,
    upper = data$upper_crude,
    model = "Crude",
    stringsAsFactors = FALSE
  )

  df_adj <- data.frame(
    variable = data$variable,
    hr = data$hr_adjusted,
    lower = data$lower_adjusted,
    upper = data$upper_adjusted,
    model = "Adjusted",
    stringsAsFactors = FALSE
  )

  df_all <- rbind(df_crude, df_adj)
  df_all$model <- factor(df_all$model, levels = c("Crude", "Adjusted"))

  # Y 轴位置 (每个变量两个点)
  var_levels <- rev(unique(data$variable))
  df_all$variable <- factor(df_all$variable, levels = var_levels)
  df_all$y_pos <- as.numeric(df_all$variable)

  # 偏移
  df_all$y_offset <- ifelse(df_all$model == "Crude",
                             df_all$y_pos - 0.15,
                             df_all$y_pos + 0.15)

  p <- ggplot(df_all, aes(x = hr, y = y_offset, color = model)) +
    geom_vline(xintercept = 1, linetype = "dashed", color = "grey60") +
    geom_segment(aes(x = lower, xend = upper, yend = y_offset),
                 linewidth = 1) +
    geom_point(size = 2.5) +
    scale_color_manual(values = c("Crude" = "#2E86C1", "Adjusted" = "#E74C3C")) +
    scale_x_continuous(trans = "log10") +
    scale_y_continuous(breaks = 1:length(var_levels), labels = var_levels) +
    theme_classic(base_size = 12) +
    theme(
      panel.grid.major.y = element_line(color = "grey95"),
      legend.position = "bottom"
    ) +
    labs(
      title = paste0(effect_name, ": Crude vs Adjusted"),
      x = paste0(effect_name, " (95% CI)"),
      y = NULL,
      color = ""
    )

  return(p)
}


# ============================================================================
# 4. Meta 分析森林图 (异质性标注)
# ============================================================================

#' Meta 分析森林图
#'
#' @param studies 研究名称向量
#' @param hr 各研究的效应量
#' @param lower 下限
#' @param upper 上限
#' @param weights 权重 (可选)
#' @param pooled_hr 合并效应量
#' @param pooled_lower 合并下限
#' @param pooled_upper 合并上限
#' @param i2 异质性 I² 统计量
#' @param p_heterogeneity 异质性 P 值
#' @param effect_name 效应量名称
#'
#' @return ggplot 对象
forest_meta <- function(studies, hr, lower, upper, weights = NULL,
                         pooled_hr, pooled_lower, pooled_upper,
                         i2 = NULL, p_heterogeneity = NULL,
                         effect_name = "HR") {

  n <- length(studies)

  # 合并行
  all_studies <- c(studies, "Overall")
  all_hr <- c(hr, pooled_hr)
  all_lower <- c(lower, pooled_lower)
  all_upper <- c(upper, pooled_upper)
  all_weights <- if (!is.null(weights)) c(weights, 100) else rep(1, n + 1)
  is_pooled <- c(rep(FALSE, n), TRUE)

  df <- data.frame(
    study = all_studies,
    hr = all_hr,
    lower = all_lower,
    upper = all_upper,
    weight = all_weights,
    is_pooled = is_pooled,
    y_pos = (n + 1):1,
    stringsAsFactors = FALSE
  )

  # 权重大小映射
  df$point_size <- ifelse(df$is_pooled, 5, sqrt(df$weight) / 2)

  p <- ggplot(df, aes(x = hr, y = y_pos)) +
    # 参考线
    geom_vline(xintercept = 1, linetype = "dashed", color = "grey60") +
    # 置信区间
    geom_segment(aes(x = lower, xend = upper, yend = y_pos,
                     linewidth = is_pooled)) +
    # 点估计 (大小按权重)
    geom_point(aes(size = point_size, color = is_pooled)) +
    # 尺度
    scale_linewidth_manual(values = c("FALSE" = 0.8, "TRUE" = 1.5), guide = "none") +
    scale_size_continuous(range = c(2, 6), guide = "none") +
    scale_color_manual(values = c("FALSE" = "#2E86C1", "TRUE" = "#E74C3C"), guide = "none") +
    # X 轴
    scale_x_continuous(trans = "log10") +
    # Y 轴
    scale_y_continuous(breaks = df$y_pos, labels = df$study,
                        expand = c(0.02, 0)) +
    # 主题
    theme_classic(base_size = 12) +
    theme(
      axis.text.y = element_text(hjust = 0, size = 10),
      axis.ticks.y = element_blank(),
      panel.grid = element_blank(),
      plot.title = element_text(face = "bold", hjust = 0.5)
    ) +
    labs(
      title = paste0("Forest Plot: ", effect_name),
      x = paste0(effect_name, " (95% CI)"),
      y = NULL
    )

  # 异质性标注
  if (!is.null(i2)) {
    het_text <- paste0("I² = ", sprintf("%.1f%%", i2))
    if (!is.null(p_heterogeneity)) {
      het_text <- paste0(het_text, ", P = ", format.pval(p_heterogeneity, digits = 2))
    }
    p <- p + annotate("text", x = min(df$lower, na.rm = TRUE),
                       y = 0.5, label = het_text,
                       hjust = 0, size = 3.5, color = "grey30", fontface = "italic")
  }

  return(p)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # ------ 示例 1: 亚组分析森林图 ------
  subgroup_data <- data.frame(
    subgroup = c("Overall", "Age < 65", "Age >= 65",
                 "Male", "Female", "Diabetes", "No Diabetes"),
    n = c(500, 250, 250, 280, 220, 150, 350),
    hr = c(0.75, 0.65, 0.88, 0.70, 0.82, 0.60, 0.80),
    lower = c(0.60, 0.45, 0.65, 0.50, 0.60, 0.40, 0.62),
    upper = c(0.95, 0.95, 1.20, 0.98, 1.12, 0.90, 1.03),
    p_interaction = c(NA, 0.08, NA, 0.15, NA, 0.03, NA),
    is_overall = c(TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)
  )
  p1 <- forest_subgroup(subgroup_data)
  ggsave("forest_subgroup.png", p1, width = 10, height = 6, dpi = 300)

  # ------ 示例 2: 单/多因素同图 ------
  data <- data.frame(
    variable = c("Age", "Male", "Smoking", "Diabetes", "Hypertension"),
    hr_crude = c(1.02, 1.5, 1.8, 2.1, 1.4),
    lower_crude = c(1.01, 1.1, 1.3, 1.5, 1.0),
    upper_crude = c(1.03, 2.0, 2.5, 2.9, 1.9),
    hr_adjusted = c(1.01, 1.3, 1.5, 1.7, 1.2),
    lower_adjusted = c(1.00, 0.95, 1.1, 1.2, 0.85),
    upper_adjusted = c(1.02, 1.8, 2.1, 2.4, 1.7)
  )
  p2 <- forest_crude_adjusted(data)
  ggsave("forest_crude_adjusted.png", p2, width = 10, height = 5, dpi = 300)

  # ------ 示例 3: Meta 分析森林图 ------
  p3 <- forest_meta(
    studies = c("Smith 2020", "Wang 2021", "Chen 2022", "Li 2023"),
    hr = c(0.72, 0.85, 0.68, 0.78),
    lower = c(0.55, 0.65, 0.50, 0.60),
    upper = c(0.95, 1.10, 0.92, 1.02),
    weights = c(30, 25, 20, 25),
    pooled_hr = 0.76, pooled_lower = 0.65, pooled_upper = 0.88,
    i2 = 42.3, p_heterogeneity = 0.16
  )
  ggsave("forest_meta.png", p3, width = 10, height = 5, dpi = 300)

  cat("✅ 森林图增强模板示例完成\n")
}

cat("✅ forest_plot_enhanced.R 已加载\n")
cat("可用函数:\n")
cat("  forest_subgroup()        - 亚组分析森林图 (最常用)\n")
cat("  forest_nejm()            - NEJM 风格森林图 (带表格)\n")
cat("  forest_crude_adjusted()  - 单/多因素同图\n")
cat("  forest_meta()            - Meta 分析森林图\n")
