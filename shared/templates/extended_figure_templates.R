# extended_figure_templates.R — 扩展图表 R 模板
# ================================================
# 提供出版级图表的扩展类型
# 依赖: ggplot2, survminer, survfit, svglite
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)
library(survival)
library(survminer)

PALETTE <- list(
  blue_main = '#0F4D92',
  blue_secondary = '#3775BA',
  green_1 = '#DDF3DE',
  green_2 = '#AADCA9',
  green_3 = '#8BCF8B',
  red_1 = '#F6CFCB',
  red_2 = '#E9A6A1',
  red_strong = '#B64342',
  neutral_light = '#CFCECE',
  neutral_mid = '#767676',
  neutral_dark = '#4D4D4D',
  gold = '#FFD700',
  teal = '#42949E',
  violet = '#9A4D8E'
)

COLOR_BLIND_SAFE <- c(
  '#0072B2', '#E69F00', '#009E73', '#F0E442',
  '#56B4E9', '#D55E00', '#CC79A7'
)

format_p_value <- function(p) {
  if (is.na(p)) return('NA')
  if (p < 0.001) return('P < 0.001')
  if (p < 0.01) return(sprintf('P = %.3f', p))
  if (p < 0.05) return(sprintf('P = %.3f', p))
  return(sprintf('P = %.2f', p))
}

make_histogram <- function(data, bins = 'auto', xlabel = NULL, 
                           ylabel = 'Frequency', title = NULL, 
                           color = NULL, figsize = c(6, 4)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(value = data)
  p <- ggplot(df, aes(x = value)) +
    geom_histogram(fill = color, color = 'white', alpha = 0.8, 
                   bins = if (bins == 'auto') 30 else bins) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_density_plot <- function(data, xlabel = NULL, ylabel = 'Density',
                              title = NULL, color = NULL, figsize = c(6, 4)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(value = data)
  p <- ggplot(df, aes(x = value)) +
    geom_histogram(aes(y = ..density..), fill = color, alpha = 0.3, 
                   color = NA, bins = 30) +
    geom_density(color = color, size = 1.2) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_violin_plot <- function(data, labels, xlabel = NULL, ylabel = NULL,
                             title = NULL, colors = NULL, figsize = c(7, 4)) {
  if (is.null(colors)) colors <- COLOR_BLIND_SAFE[1:length(data)]
  df <- data.frame(
    value = unlist(data),
    group = rep(labels, sapply(data, length))
  )
  p <- ggplot(df, aes(x = group, y = value)) +
    geom_violin(aes(fill = group), alpha = 0.7) +
    geom_boxplot(width = 0.1, fill = 'white') +
    scale_fill_manual(values = colors) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      legend.position = 'none',
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_dot_plot <- function(data, labels, xlabel = NULL, ylabel = NULL,
                          title = NULL, colors = NULL, figsize = c(7, 4)) {
  if (is.null(colors)) colors <- COLOR_BLIND_SAFE[1:length(data)]
  df <- data.frame(
    value = unlist(data),
    group = rep(labels, sapply(data, length))
  )
  p <- ggplot(df, aes(x = group, y = value)) +
    geom_jitter(width = 0.15, size = 2, alpha = 0.8, color = PALETTE[1]) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_pie_chart <- function(values, labels, title = NULL, colors = NULL,
                           autopct = '%1.1f%%', figsize = c(5, 5)) {
  if (is.null(colors)) colors <- COLOR_BLIND_SAFE[1:length(values)]
  df <- data.frame(
    category = labels,
    value = values
  )
  p <- ggplot(df, aes(x = '', y = value, fill = category)) +
    geom_bar(stat = 'identity', width = 1) +
    coord_polar('y', start = 0) +
    geom_text(aes(label = sprintf(autopct, value / sum(value) * 100)), 
              position = position_stack(vjust = 0.5), size = 3.5) +
    scale_fill_manual(values = colors) +
    labs(title = title) +
    theme_void(base_size = 10) +
    theme(
      plot.title = element_text(face = 'bold', size = 12, hjust = 0.5)
    )
  return(p)
}

make_line_graph <- function(x, y, xlabel = NULL, ylabel = NULL, title = NULL,
                            color = NULL, show_ci = TRUE, ci_lower = NULL,
                            ci_upper = NULL, figsize = c(7, 4)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(x = x, y = y)
  p <- ggplot(df, aes(x = x, y = y)) +
    geom_line(color = color, size = 1.2) +
    geom_point(color = color, size = 2.5)
  if (show_ci && !is.null(ci_lower) && !is.null(ci_upper)) {
    df$lower <- ci_lower
    df$upper <- ci_upper
    p <- p + geom_ribbon(aes(ymin = lower, ymax = upper), 
                         fill = color, alpha = 0.15)
  }
  p <- p +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_area_chart <- function(x, y, xlabel = NULL, ylabel = NULL, title = NULL,
                            color = NULL, figsize = c(7, 4)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(x = x, y = y)
  p <- ggplot(df, aes(x = x, y = y)) +
    geom_area(fill = color, alpha = 0.3) +
    geom_line(color = color, size = 1.2) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_bubble_plot <- function(x, y, size, xlabel = NULL, ylabel = NULL, 
                             title = NULL, color = NULL, figsize = c(6, 5)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(x = x, y = y, size = size)
  p <- ggplot(df, aes(x = x, y = y, size = size)) +
    geom_point(color = color, alpha = 0.6, stroke = 0.5, fill = color) +
    scale_size_continuous(range = c(5, 30)) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_pair_plot <- function(data, columns = NULL, title = NULL, figsize = c(8, 8)) {
  if (is.null(columns)) columns <- colnames(data)
  n <- length(columns)
  df <- data[, columns, drop = FALSE]
  p <- ggpairs(df, 
               lower = list(continuous = wrap('points', size = 1, alpha = 0.5)),
               upper = list(continuous = wrap('cor', size = 3)),
               diag = list(continuous = wrap('barDiag', fill = PALETTE[1]))) +
    theme_minimal(base_size = 8) +
    theme(
      plot.title = element_text(face = 'bold', size = 12)
    )
  if (!is.null(title)) {
    p <- p + ggtitle(title)
  }
  return(p)
}

make_bland_altman_plot <- function(x1, x2, xlabel = NULL, ylabel = 'Difference',
                                   title = NULL, color = NULL, figsize = c(6, 5)) {
  if (is.null(color)) color <- PALETTE
  mean_vals <- (x1 + x2) / 2
  diff <- x1 - x2
  mean_diff <- mean(diff)
  std_diff <- sd(diff)
  upper_limit <- mean_diff + 1.96 * std_diff
  lower_limit <- mean_diff - 1.96 * std_diff
  df <- data.frame(mean = mean_vals, diff = diff)
  p <- ggplot(df, aes(x = mean, y = diff)) +
    geom_point(color = color, size = 2.5, alpha = 0.7) +
    geom_hline(yintercept = mean_diff, color = 'black', size = 1) +
    geom_hline(yintercept = upper_limit, color = PALETTE[1], 
               linetype = 'dashed', size = 0.8) +
    geom_hline(yintercept = lower_limit, color = PALETTE[1], 
               linetype = 'dashed', size = 0.8) +
    labs(x = ifelse(is.null(xlabel), 'Mean of two measurements', xlabel), 
         y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_decision_curve <- function(prob_thresholds, net_benefit,
                                treat_all = NULL, treat_none = NULL,
                                xlabel = 'Threshold Probability',
                                ylabel = 'Net Benefit', title = NULL,
                                color = NULL, figsize = c(7, 5)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(threshold = prob_thresholds, net_benefit = net_benefit)
  p <- ggplot(df, aes(x = threshold, y = net_benefit)) +
    geom_line(color = color, size = 1.2)
  if (!is.null(treat_all)) {
    p <- p + geom_line(aes(y = treat_all), color = PALETTE[1], 
                       linetype = 'dashed', size = 0.8)
  }
  if (!is.null(treat_none)) {
    p <- p + geom_line(aes(y = treat_none), color = PALETTE[1], 
                       linetype = 'dotted', size = 0.8)
  }
  p <- p +
    scale_x_continuous(limits = c(0, 1)) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_funnel_plot <- function(effect_sizes, standard_errors,
                             xlabel = 'Effect Size', ylabel = 'Standard Error',
                             title = NULL, color = NULL, figsize = c(5, 5)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(effect = effect_sizes, se = standard_errors)
  p <- ggplot(df, aes(x = effect, y = se)) +
    geom_point(color = color, size = 3, stroke = 0.5) +
    geom_vline(xintercept = mean(effect_sizes), color = PALETTE[1], 
               linetype = 'dashed', size = 0.8) +
    scale_y_reverse() +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

make_rmst_plot <- function(time, event, group, group_labels = NULL,
                           group_colors = NULL, xlabel = 'Time',
                           ylabel = 'RMST', title = NULL, figsize = c(7, 5)) {
  if (is.null(group_labels)) group_labels <- as.character(unique(group))
  if (is.null(group_colors)) group_colors <- COLOR_BLIND_SAFE[1:length(group_labels)]
  df <- data.frame(time = time, event = event, group = as.factor(group))
  surv_fit <- survfit(Surv(time, event) ~ group, data = df)
  p <- ggsurvplot(surv_fit, data = df,
                  palette = group_colors,
                  legend.labs = group_labels,
                  xlab = xlabel, ylab = ylabel,
                  main = title,
                  conf.int = TRUE,
                  risk.table = FALSE,
                  theme = theme_minimal(base_size = 10))
  return(p)
}

make_cumulative_incidence_curve <- function(time, event, competing_event,
                                            group = NULL, group_labels = NULL,
                                            xlabel = 'Time', ylabel = 'Cumulative Incidence',
                                            title = NULL, colors = NULL, figsize = c(7, 5)) {
  if (is.null(colors)) colors <- COLOR_BLIND_SAFE
  if (!is.null(group)) {
    df <- data.frame(time = time, event = event, 
                     competing = competing_event, group = as.factor(group))
    if (is.null(group_labels)) group_labels <- levels(df$group)
    fit <- survfit(Surv(time, event, type = 'mstate') ~ group, data = df)
  } else {
    df <- data.frame(time = time, event = event, competing = competing_event)
    fit <- survfit(Surv(time, event, type = 'mstate') ~ 1, data = df)
  }
  p <- ggsurvplot(fit, data = df,
                  palette = colors[1:length(unique(group))],
                  legend.labs = group_labels,
                  xlab = xlabel, ylab = ylabel,
                  main = title,
                  conf.int = TRUE,
                  theme = theme_minimal(base_size = 10))
  return(p)
}

make_det_curve <- function(y_true, y_score, xlabel = 'False Positive Rate',
                           ylabel = 'False Negative Rate', title = NULL,
                           color = NULL, figsize = c(5, 5)) {
  if (is.null(color)) color <- PALETTE
  df <- data.frame(true = y_true, score = y_score)
  df <- df[order(df$score), ]
  n <- nrow(df)
  fpr <- cumsum(1 - df$true) / sum(1 - df$true)
  fnr <- (sum(df$true) - cumsum(df$true)) / sum(df$true)
  det_df <- data.frame(fpr = fpr, fnr = fnr)
  p <- ggplot(det_df, aes(x = fpr, y = fnr)) +
    geom_line(color = color, size = 1.2) +
    labs(x = xlabel, y = ylabel, title = title) +
    theme_minimal(base_size = 10) +
    theme(
      panel.grid.minor = element_blank(),
      axis.line = element_line(size = 0.5),
      axis.ticks = element_line(size = 0.3),
      plot.title = element_text(face = 'bold', size = 12)
    )
  return(p)
}

export_figure <- function(p, filename, width = 8, height = 6, dpi = 300) {
  if (!requireNamespace('svglite', quietly = TRUE)) {
    warning('svglite not installed, skipping SVG export')
  } else {
    ggsave(paste0(filename, '.svg'), plot = p, width = width, height = height,
           device = svglite::svglite)
  }
  ggsave(paste0(filename, '.png'), plot = p, width = width, height = height,
         dpi = dpi, bg = 'white')
  message(sprintf('Exported: %s.svg + %s.png', filename, filename))
}
