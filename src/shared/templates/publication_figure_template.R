# publication_figure_template.R — 出版级图表 R 模板
# ================================================
# 提供 ggplot2 出版级图表样式、配色、导出功能
#
# 用法:
#   source("src/shared/templates/publication_figure_template.R")
#   apply_publication_style()
#   p <- make_forest_plot(labels, estimates, ci_lower, ci_upper, p_values)
#   export_figure(p, "output/figure1")
#
# 依赖: ggplot2, svglite
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)

# --- 发表级 rcParams ---
apply_publication_style <- function(font_size = 10, support_chinese = FALSE) {
  font_family <- if (support_chinese) "Microsoft YaHei" else "Arial"

  theme_set(theme_minimal(base_size = font_size, base_family = font_family) +
    theme(
      # 仅左+下轴线
      axis.line = element_line(linewidth = 0.5, colour = "black"),
      axis.ticks = element_line(linewidth = 0.3, colour = "black"),
      panel.grid.major = element_line(colour = "#f0f0f0"),
      panel.grid.minor = element_blank(),
      panel.border = element_blank(),
      # 无边框图例
      legend.key = element_blank(),
      legend.background = element_blank(),
      # 标题
      plot.title = element_text(size = font_size + 2, face = "bold"),
      axis.title = element_text(size = font_size),
      axis.text = element_text(size = font_size - 1)
    ))
}

# --- 语义化调色板 ---
PALETTE_SEMANTIC <- list(
  intervention = "#2166AC",
  control = "#B2182B",
  significant = "#D6604D",
  non_significant = "#4393C3",
  highlight = "#F4A582",
  neutral = "#999999"
)

# --- P 值格式化 ---
format_p_value <- function(p) {
  if (is.na(p)) return("NA")
  if (p < 0.001) return("P < 0.001")
  if (p < 0.01) return(sprintf("P = %.3f", p))
  if (p < 0.05) return(sprintf("P = %.3f", p))
  return(sprintf("P = %.2f", p))
}

# --- 森林图 ---
make_forest_plot <- function(labels, estimates, ci_lower, ci_upper,
                              p_values = NULL, xlabel = "HR (95% CI)") {
  df <- data.frame(
    label = factor(labels, levels = rev(labels)),
    estimate = estimates,
    lower = ci_lower,
    upper = ci_upper,
    stringsAsFactors = FALSE
  )

  p <- ggplot(df, aes(x = estimate, y = label)) +
    geom_vline(xintercept = 1, linetype = "dashed", colour = "grey50") +
    geom_errorbarh(aes(xmin = lower, xmax = upper), height = 0.2, linewidth = 0.5) +
    geom_point(size = 3, colour = PALETTE_SEMANTIC$intervention) +
    labs(x = xlabel, y = NULL) +
    theme(
      axis.text.y = element_text(hjust = 1, size = 10),
      plot.margin = margin(5, 15, 5, 5)
    )

  return(p)
}

# --- 导出 ---
export_figure <- function(p, filename, width = 8, height = 6, dpi = 300) {
  # SVG (首要)
  ggsave(paste0(filename, ".svg"), plot = p, width = width, height = height,
         device = svglite::svglite)
  # PNG 300dpi (预览)
  ggsave(paste0(filename, ".png"), plot = p, width = width, height = height,
         dpi = dpi, bg = "white")
  message(sprintf("Exported: %s.svg + %s.png", filename, filename))
}
