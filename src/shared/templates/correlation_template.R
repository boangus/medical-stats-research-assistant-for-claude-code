# =============================================================================
# corrr 相关性分析模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 corrr 包，提供一站式相关性矩阵计算与可视化
#
# 参考:
#   Epi R Handbook: https://epirhandbook.com/en/new_pages/stat_tests.html
#   corrr: https://corrr.tidymodels.org/
#
# 依赖:
#   install.packages("corrr")
#   install.packages("dplyr")
#   install.packages("ggplot2")
# =============================================================================

library(corrr)
library(dplyr)
library(ggplot2)

# =============================================================================
# 1. 相关性矩阵计算
# =============================================================================

#' 计算相关性矩阵
#' @param data 数据框
#' @param vars 变量名向量
#' @param method "pearson" / "spearman" / "kendall"
corr_matrix <- function(data, vars = NULL, method = "spearman") {
  if (is.null(vars)) {
    # 自动选择数值变量
    vars <- data %>% select(where(is.numeric)) %>% names()
  }
  
  data %>%
    select(all_of(vars)) %>%
    correlate(method = method, quiet = TRUE)
}

#' 直接输出格式化相关性矩阵
corr_fashion <- function(data, vars = NULL, method = "spearman",
                          decimals = 2) {
  data %>%
    corr_matrix(vars, method) %>%
    shave() %>%
    fashion(decimals = decimals)
}

# =============================================================================
# 2. 相关性可视化
# =============================================================================

#' 相关性热图
#' @param data 数据框
#' @param vars 变量名向量
#' @param method "pearson" / "spearman" / "kendall"
#' @param colours 颜色向量（低/中/高）
corr_heatmap <- function(data, vars = NULL, method = "spearman",
                          colours = c("#B2182B", "white", "#2166AC")) {
  mat <- data %>% corr_matrix(vars, method)
  
  mat %>%
    ggplot(aes(x = term, y = rowname, fill = r)) +
    geom_tile(color = "white") +
    geom_text(aes(label = round(r, 2)), size = 3) +
    scale_fill_gradient2(low = colours[1], mid = colours[2],
                         high = colours[3], midpoint = 0,
                         limits = c(-1, 1)) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1),
          axis.title = element_blank()) +
    labs(title = paste(method, "correlation matrix"),
         fill = "r")
}

#' 相关性网络图
corr_network <- function(data, vars = NULL, method = "spearman",
                          min_cor = 0.3) {
  data %>%
    corr_matrix(vars, method) %>%
    network_plot(min_cor = min_cor,
                 colours = c("#B2182B", "white", "#2166AC")) +
    ggtitle(paste("Correlation network (|r| >=", min_cor, ")"))
}

#' 相关性散点图矩阵（选定的高相关对）
corr_scatter <- function(data, vars = NULL, method = "spearman",
                          top_n = 6) {
  mat <- data %>% corr_matrix(vars, method)
  
  # 找出相关性最高的对
  corr_pairs <- mat %>%
    shave() %>%
    pivot_longer(-term, names_to = "var2", values_to = "r") %>%
    filter(!is.na(r)) %>%
    arrange(desc(abs(r))) %>%
    head(top_n)
  
  # 绘制散点图
  plots <- list()
  for (i in seq_len(nrow(corr_pairs))) {
    v1 <- corr_pairs$term[i]
    v2 <- corr_pairs$var2[i]
    r_val <- round(corr_pairs$r[i], 3)
    
    p <- data %>%
      ggplot(aes(x = !!sym(v1), y = !!sym(v2))) +
      geom_point(alpha = 0.5) +
      geom_smooth(method = "lm", se = TRUE, color = "#2166AC") +
      annotate("text", x = Inf, y = Inf,
               label = paste("r =", r_val),
               hjust = 1.1, vjust = 1.5, size = 4) +
      theme_minimal() +
      labs(subtitle = paste(v1, "vs", v2))
    
    plots[[i]] <- p
  }
  
  # 在一页中排列
  if (length(plots) > 0) {
    gridExtra::grid.arrange(grobs = plots, ncol = min(3, length(plots)))
  }
  
  invisible(corr_pairs)
}

# =============================================================================
# 3. 相关性显著性检验
# =============================================================================

#' 相关性矩阵显著性检验
#' @param data 数据框
#' @param vars 变量名向量
#' @param method "pearson" / "spearman" / "kendall"
corr_significance <- function(data, vars = NULL, method = "spearman") {
  if (is.null(vars)) {
    vars <- data %>% select(where(is.numeric)) %>% names()
  }
  
  n <- length(vars)
  results <- data.frame(
    var1 = character(),
    var2 = character(),
    r = numeric(),
    p = numeric(),
    stringsAsFactors = FALSE
  )
  
  for (i in 1:(n - 1)) {
    for (j in (i + 1):n) {
      test <- cor.test(data[[vars[i]]], data[[vars[j]]], method = method)
      results <- rbind(results, data.frame(
        var1 = vars[i],
        var2 = vars[j],
        r = round(test$estimate, 3),
        p = test$p.value,
        stringsAsFactors = FALSE
      ))
    }
  }
  
  # 标记显著性
  results <- results %>%
    mutate(
      significance = case_when(
        p < 0.001 ~ "***",
        p < 0.01  ~ "**",
        p < 0.05  ~ "*",
        TRUE      ~ "ns"
      )
    ) %>%
    arrange(p)
  
  cat("=== 相关性显著性检验 (", method, ") ===\n", sep = "")
  cat("Signif. codes: 0 '***' 0.001 '**' 0.01 '*' 0.05 'ns'\n\n")
  print(results, row.names = FALSE)
  
  invisible(results)
}

# =============================================================================
# 4. 完整工作流
# =============================================================================

#' 相关性分析完整工作流
corr_full_analysis <- function(data, vars = NULL, method = "spearman",
                                export_plot = FALSE) {
  
  cat("======== 相关性分析工作流 ========\n")
  cat("方法:", method, "\n\n")
  
  # 1. 计算矩阵
  cat("--- 相关性矩阵 ---\n")
  mat <- data %>% corr_fashion(vars, method)
  print(mat)
  
  # 2. 显著性检验
  cat("\n--- 显著性检验 ---\n")
  sig <- data %>% corr_significance(vars, method)
  
  # 3. 可视化热图
  cat("\n--- 生成热图 ---\n")
  p <- data %>% corr_heatmap(vars, method)
  print(p)
  
  # 4. 网络图
  cat("\n--- 生成网络图 ---\n")
  p2 <- data %>% corr_network(vars, method, min_cor = 0.3)
  print(p2)
  
  invisible(list(matrix = mat, significance = sig))
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  data("mtcars")
  
  # 基础矩阵
  mtcars %>% corr_matrix(c("mpg", "wt", "hp", "disp"))
  
  # 格式化输出
  mtcars %>% corr_fashion(c("mpg", "wt", "hp", "disp", "qsec"))
  
  # 热图
  mtcars %>% corr_heatmap()
  
  # 网络图
  mtcars %>% corr_network(min_cor = 0.4)
  
  # 显著性检验
  mtcars %>% corr_significance(c("mpg", "wt", "hp"))
  
  # 完整工作流
  mtcars %>% corr_full_analysis(c("mpg", "wt", "hp", "disp", "qsec"))
}
