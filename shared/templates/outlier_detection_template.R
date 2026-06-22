# outlier_detection_template.R — 异常值检测与处理模板
# =======================================================
# 适用于：连续变量的异常值检测、可视化和处理
#
# 覆盖 4 大类方法：
#   1. 图形法: 散点图、箱线图、残差图、QQ图、Cook距离
#   2. 分布法: 3σ标准差、IQR法(1.5倍)、Hampel滤波(3MAD)、LOF
#   3. 经验法: 盖帽法(P1/P99)、批量盖帽
#   4. 检验法: Grubbs检验、Rosner检验
#
# 依赖: ggplot2, car, outliers, EnvStats, DMwR2 (可选)
# 安装: install.packages(c("ggplot2","car","outliers","EnvStats"))
#
# 参考: 实战医学统计课程 Ch9
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)

# ============================================================================
# 1. 图形法
# ============================================================================

#' 箱线图异常值检测
#'
#' @param x 数值向量
#' @param var_name 变量名 (用于标题)
#' @param coef IQR 系数 (默认 1.5)
#'
#' @return list(outliers = 异常值, n = 异常值数量, plot = ggplot)
outlier_boxplot <- function(x, var_name = "Variable", coef = 1.5) {
  x <- x[!is.na(x)]

  # IQR 法
  q1 <- quantile(x, 0.25)
  q3 <- quantile(x, 0.75)
  iqr <- q3 - q1
  lower <- q1 - coef * iqr
  upper <- q3 + coef * iqr

  outliers <- x[x < lower | x > upper]

  df <- data.frame(x = x)
  df$is_outlier <- ifelse(df$x < lower | df$x > upper, "Outlier", "Normal")

  p <- ggplot(df, aes(y = x)) +
    geom_boxplot(fill = "#2E86C1", alpha = 0.3, coef = coef) +
    geom_point(data = df[df$is_outlier == "Outlier", ],
               aes(x = 0, y = x), color = "#E74C3C", size = 3, shape = 17) +
    annotate("text", x = 0.3, y = max(outliers, Inf),
             label = paste0("n = ", length(outliers), " outliers\n",
                            "Limits: [", sprintf("%.1f", lower), ", ",
                            sprintf("%.1f", upper), "]"),
             hjust = 0, size = 3.5, color = "grey30") +
    theme_classic(base_size = 12) +
    theme(axis.text.x = element_blank(), axis.ticks.x = element_blank()) +
    labs(title = paste0("Boxplot: ", var_name), y = var_name)

  cat(sprintf("📊 箱线图异常值 (%s): n = %d (%.1f%%)\n",
              var_name, length(outliers), length(outliers) / length(x) * 100))
  cat(sprintf("   IQR = %.2f, Limits: [%.2f, %.2f]\n", iqr, lower, upper))

  return(list(outliers = outliers, n = length(outliers), lower = lower,
              upper = upper, plot = p))
}


#' QQ图异常值检测
#'
#' @param x 数值向量
#' @param var_name 变量名
#' @param labels 标签向量 (可选，用于标注异常点)
#'
#' @return list(outlier_idx = 异常值索引, plot = ggplot)
outlier_qqplot <- function(x, var_name = "Variable", labels = NULL) {
  n <- length(x)
  if (is.null(labels)) labels <- as.character(1:n)

  # 理论分位数
  theoretical <- qnorm(ppoints(n))[order(order(x))]

  # 标准化残差
  x_std <- (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)

  df <- data.frame(
    theoretical = theoretical,
    sample = x_std,
    label = labels,
    is_outlier = abs(x_std) > 2
  )

  p <- ggplot(df, aes(x = theoretical, y = sample)) +
    geom_point(aes(color = is_outlier), size = 2) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "grey50") +
    geom_hline(yintercept = c(-2, 2), linetype = "dotted", color = "#E74C3C") +
    scale_color_manual(values = c("FALSE" = "#2E86C1", "TRUE" = "#E74C3C"),
                        labels = c("Normal", "|z| > 2")) +
    theme_classic(base_size = 12) +
    theme(legend.position = "bottom") +
    labs(title = paste0("Q-Q Plot: ", var_name),
         x = "Theoretical Quantiles", y = "Standardized Values",
         color = "")

  outlier_idx <- which(df$is_outlier)
  cat(sprintf("📊 QQ图异常值 (%s): %d 个点 |z| > 2\n", var_name, length(outlier_idx)))

  return(list(outlier_idx = outlier_idx, plot = p))
}


#' 模型诊断仪表盘 (残差图 + Cook距离 + 杠杆值)
#'
#' @param model lm 或 glm 对象
#' @param n_labels 标注的极端点数量 (默认 3)
#'
#' @return list(plots = ggplot列表, outliers = 异常点, influential = 强影响点)
outlier_diagnostics <- function(model, n_labels = 3) {
  n <- length(fitted(model))
  p <- length(coef(model))

  # 标准化残差
  std_resid <- rstandard(model)

  # Cook 距离
  cook_d <- cooks.distance(model)
  cook_threshold <- 4 / (n - p - 1)

  # 杠杆值
  hat_vals <- hatvalues(model)
  hat_threshold <- 2 * p / n

  # 强影响点
  influential <- which(cook_d > cook_threshold)
  outlier_idx <- which(abs(std_resid) > 2)

  df <- data.frame(
    index = 1:n,
    fitted = fitted(model),
    std_resid = std_resid,
    cook_d = cook_d,
    hat_val = hat_vals,
    label = names(cook_d) %||% as.character(1:n)
  )

  # 图1: 残差 vs 拟合值
  p1 <- ggplot(df, aes(x = fitted, y = std_resid)) +
    geom_point(aes(color = abs(std_resid) > 2), size = 1.5, alpha = 0.6) +
    geom_hline(yintercept = c(-2, 0, 2), linetype = c("dotted","solid","dotted"),
               color = c("grey50","grey70","grey50")) +
    scale_color_manual(values = c("FALSE" = "#2E86C1", "TRUE" = "#E74C3C")) +
    theme_classic(base_size = 10) +
    theme(legend.position = "none") +
    labs(title = "Residuals vs Fitted", x = "Fitted", y = "Std. Residual")

  # 图2: QQ 残差图
  p2 <- ggplot(df, aes(sample = std_resid)) +
    stat_qq(size = 1.5, color = "#2E86C1") +
    stat_qq_line(color = "grey50") +
    theme_classic(base_size = 10) +
    labs(title = "Normal Q-Q", x = "Theoretical", y = "Std. Residual")

  # 图3: Cook 距离
  p3 <- ggplot(df, aes(x = index, y = cook_d)) +
    geom_col(aes(fill = cook_d > cook_threshold), width = 0.8) +
    geom_hline(yintercept = cook_threshold, linetype = "dashed", color = "#E74C3C") +
    scale_fill_manual(values = c("FALSE" = "#2E86C1", "TRUE" = "#E74C3C")) +
    theme_classic(base_size = 10) +
    theme(legend.position = "none") +
    labs(title = "Cook's Distance", x = "Observation", y = "Cook's D")

  # 图4: 杠杆值
  p4 <- ggplot(df, aes(x = index, y = hat_val)) +
    geom_point(aes(color = hat_val > hat_threshold), size = 1.5) +
    geom_hline(yintercept = hat_threshold, linetype = "dashed", color = "#E74C3C") +
    scale_color_manual(values = c("FALSE" = "#2E86C1", "TRUE" = "#E74C3C")) +
    theme_classic(base_size = 10) +
    theme(legend.position = "none") +
    labs(title = "Leverage (Hat Values)", x = "Observation", y = "Hat Value")

  # 合并
  p_combined <- patchwork::wrap_plots(p1, p2, p3, p4, ncol = 2)

  cat(sprintf("\n📊 模型诊断:\n"))
  cat(sprintf("   异常残差点 (|z|>2): %d\n", length(outlier_idx)))
  cat(sprintf("   强影响点 (Cook>D): %d\n", length(influential)))

  return(list(
    plots = p_combined,
    outliers = outlier_idx,
    influential = influential,
    data = df
  ))
}


# ============================================================================
# 2. 分布法
# ============================================================================

#' 3σ 标准差法
#'
#' @param x 数值向量
#' @param k 标准差倍数 (默认 3)
#'
#' @return list(outliers, lower, upper)
outlier_3sigma <- function(x, k = 3) {
  x <- x[!is.na(x)]
  m <- mean(x)
  s <- sd(x)
  lower <- m - k * s
  upper <- m + k * s
  outliers <- x[x < lower | x > upper]

  cat(sprintf("📊 3σ法: mean=%.2f, sd=%.2f, limits=[%.2f, %.2f], outliers=%d\n",
              m, s, lower, upper, length(outliers)))

  return(list(outliers = outliers, n = length(outliers),
              lower = lower, upper = upper, mean = m, sd = s))
}


#' IQR 法 (箱线图标准)
#'
#' @param x 数值向量
#' @param coef IQR 系数 (默认 1.5)
#'
#' @return list(outliers, lower, upper)
outlier_iqr <- function(x, coef = 1.5) {
  x <- x[!is.na(x)]
  q1 <- quantile(x, 0.25)
  q3 <- quantile(x, 0.75)
  iqr <- q3 - q1
  lower <- q1 - coef * iqr
  upper <- q3 + coef * iqr
  outliers <- x[x < lower | x > upper]

  cat(sprintf("📊 IQR法: Q1=%.2f, Q3=%.2f, IQR=%.2f, limits=[%.2f, %.2f], outliers=%d\n",
              q1, q3, iqr, lower, upper, length(outliers)))

  return(list(outliers = outliers, n = length(outliers),
              lower = lower, upper = upper))
}


#' Hampel 滤波法 (基于中位数和MAD)
#'
#' 对偏态分布更稳健。MAD = Median Absolute Deviation。
#'
#' @param x 数值向量
#' @param k MAD 倍数 (默认 3)
#'
#' @return list(outliers, lower, upper)
outlier_hampel <- function(x, k = 3) {
  x <- x[!is.na(x)]
  med <- median(x)
  mad_val <- mad(x, constant = 1)
  lower <- med - k * mad_val
  upper <- med + k * mad_val
  outliers <- x[x < lower | x > upper]

  cat(sprintf("📊 Hampel法: median=%.2f, MAD=%.2f, limits=[%.2f, %.2f], outliers=%d\n",
              med, mad_val, lower, upper, length(outliers)))

  return(list(outliers = outliers, n = length(outliers),
              lower = lower, upper = upper))
}


#' LOF 局部异常因子
#'
#' 基于密度的异常检测，适用于多维数据。
#'
#' @param data 数据框 (数值列)
#' @param k 邻居数 (默认 10)
#' @param top_n 返回前 N 个异常点
#'
#' @return list(scores = LOF分数, outlier_idx = 异常点索引)
outlier_lof <- function(data, k = 10, top_n = NULL) {
  if (!requireNamespace("DMwR2", quietly = TRUE)) {
    stop("请安装 DMwR2 包: install.packages('DMwR2')")
  }

  # 仅保留数值列
  num_data <- data[, sapply(data, is.numeric), drop = FALSE]
  num_data <- na.omit(num_data)

  scores <- DMwR2::lofactor(num_data, k = k)

  if (is.null(top_n)) top_n <- min(5, ceiling(nrow(num_data) * 0.01))
  outlier_idx <- order(scores, decreasing = TRUE)[1:top_n]

  cat(sprintf("📊 LOF法 (k=%d): %d 个异常点\n", k, length(outlier_idx)))
  cat(sprintf("   异常点索引: %s\n", paste(outlier_idx, collapse = ", ")))

  return(list(scores = scores, outlier_idx = outlier_idx,
              outlier_data = num_data[outlier_idx, ]))
}


# ============================================================================
# 3. 经验法
# ============================================================================

#' 盖帽法 (Winsorize) — 单变量
#'
#' 将极端值替换为指定分位数。
#'
#' @param x 数值向量
#' @param lower_pct 下限分位数 (默认 0.01)
#' @param upper_pct 上限分位数 (默认 0.99)
#'
#' @return 处理后的向量
winsorize <- function(x, lower_pct = 0.01, upper_pct = 0.99) {
  lower <- quantile(x, lower_pct, na.rm = TRUE)
  upper <- quantile(x, upper_pct, na.rm = TRUE)

  n_lower <- sum(x < lower, na.rm = TRUE)
  n_upper <- sum(x > upper, na.rm = TRUE)

  x[x < lower] <- lower
  x[x > upper] <- upper

  cat(sprintf("📊 盖帽法 [P%.0f, P%.0f]: 替换 %d 个下限 + %d 个上限\n",
              lower_pct * 100, upper_pct * 100, n_lower, n_upper))

  return(x)
}


#' 批量盖帽法 (数据框)
#'
#' 对数据框中所有连续变量执行盖帽法。
#'
#' @param df 数据框
#' @param lower_pct 下限分位数 (默认 0.01)
#' @param upper_pct 上限分位数 (默认 0.99)
#'
#' @return 处理后的数据框
winsorize_df <- function(df, lower_pct = 0.01, upper_pct = 0.99) {
  num_cols <- which(sapply(df, is.numeric))

  for (i in num_cols) {
    q <- quantile(df[, i], c(lower_pct, upper_pct), na.rm = TRUE)
    n_lower <- sum(df[, i] < q[1], na.rm = TRUE)
    n_upper <- sum(df[, i] > q[2], na.rm = TRUE)
    df[, i][df[, i] < q[1]] <- q[1]
    df[, i][df[, i] > q[2]] <- q[2]

    if (n_lower + n_upper > 0) {
      cat(sprintf("  %s: 替换 %d 个值\n", names(df)[i], n_lower + n_upper))
    }
  }

  cat(sprintf("📊 批量盖帽法: 处理了 %d 个连续变量\n", length(num_cols)))

  return(df)
}


# ============================================================================
# 4. 检验法
# ============================================================================

#' Grubbs 检验 (正态分布异常值)
#'
#' @param x 数值向量
#' @param alpha 显著性水平 (默认 0.05)
#'
#' @return list(test = grubbs.test结果, is_outlier = 是否存在异常值)
outlier_grubbs <- function(x, alpha = 0.05) {
  if (!requireNamespace("outliers", quietly = TRUE)) {
    stop("请安装 outliers 包: install.packages('outliers')")
  }

  x <- x[!is.na(x)]
  result <- outliers::grubbs.test(x)

  cat(sprintf("📊 Grubbs检验: G = %.4f, P = %s\n",
              result$statistic, format.pval(result$p.value, digits = 3)))

  is_outlier <- result$p.value < alpha
  if (is_outlier) {
    cat(sprintf("  ⚠️ 存在异常值 (P < %.2f)\n", alpha))
  } else {
    cat(sprintf("  ✅ 无显著异常值 (P > %.2f)\n", alpha))
  }

  return(list(test = result, is_outlier = is_outlier))
}


#' Rosner 检验 (多个异常值)
#'
#' @param x 数值向量
#' @param k 检测的异常值数量 (默认 3)
#'
#' @return list(test = rosnerTest结果, outliers = 异常值)
outlier_rosner <- function(x, k = 3) {
  if (!requireNamespace("EnvStats", quietly = TRUE)) {
    stop("请安装 EnvStats 包: install.packages('EnvStats')")
  }

  x <- x[!is.na(x)]
  result <- EnvStats::rosnerTest(x, k = k, warn = FALSE)

  cat(sprintf("📊 Rosner检验 (k=%d):\n", k))
  print(result)

  return(list(test = result))
}


# ============================================================================
# 5. 异常值处理决策
# ============================================================================

#' 异常值处理决策向导
#'
#' 根据异常值类型和数据特征推荐处理方案。
#'
#' @param x 数值向量
#' @param var_name 变量名
#' @param method 检测方法: "iqr" (默认), "3sigma", "hampel"
#'
#' @return list(detection = 检测结果, recommendation = 推荐方案, processed = 处理后数据)
outlier_handle <- function(x, var_name = "Variable", method = "iqr") {
  cat(sprintf("\n🔍 异常值处理决策: %s\n", var_name))
  cat("=" |> rep(50) |> paste(collapse = ""), "\n")

  # 检测
  detection <- switch(method,
    "iqr" = outlier_iqr(x),
    "3sigma" = outlier_3sigma(x),
    "hampel" = outlier_hampel(x)
  )

  # 推荐
  pct_outlier <- detection$n / length(x[!is.na(x)]) * 100

  if (pct_outlier == 0) {
    recommendation <- "无异常值，无需处理"
    processed <- x
  } else if (pct_outlier < 1) {
    recommendation <- "极少异常值(<1%): 建议检查数据录入错误，可删除"
    processed <- x
  } else if (pct_outlier < 5) {
    recommendation <- "少量异常值(1-5%): 建议盖帽法(Winsorize)或保留并做敏感性分析"
    processed <- winsorize(x)
  } else {
    recommendation <- "较多异常值(>5%): 建议检查分布，考虑对数变换或非参数方法"
    processed <- x
  }

  cat(sprintf("\n  推荐: %s\n", recommendation))

  return(list(
    detection = detection,
    recommendation = recommendation,
    processed = processed
  ))
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # 模拟带异常值的数据
  set.seed(42)
  x <- c(rnorm(100, 50, 10), 120, 130, -20, -30)  # 4个异常值

  # ------ 方法 1: 箱线图 ------
  res_box <- outlier_boxplot(x, "Blood Pressure")
  print(res_box$plot)

  # ------ 方法 2: 3σ ------
  res_3s <- outlier_3sigma(x)

  # ------ 方法 3: IQR ------
  res_iqr <- outlier_iqr(x)

  # ------ 方法 4: Hampel ------
  res_hampel <- outlier_hampel(x)

  # ------ 方法 5: Grubbs ------
  res_grubbs <- outlier_grubbs(x)

  # ------ 方法 6: 盖帽法 ------
  x_winsorized <- winsorize(x)

  # ------ 方法 7: 批量盖帽 ------
  df <- data.frame(bp = x, hr = rnorm(104, 70, 12))
  df_clean <- winsorize_df(df)

  # ------ 方法 8: 决策向导 ------
  res_handle <- outlier_handle(x, "Blood Pressure")

  # ------ 方法 9: 模型诊断 ------
  model <- lm(mpg ~ wt + hp + cyl, data = mtcars)
  res_diag <- outlier_diagnostics(model)
  print(res_diag$plots)

  cat("✅ 异常值检测模板示例完成\n")
}

cat("✅ outlier_detection_template.R 已加载\n")
cat("可用函数:\n")
cat("  图形法: outlier_boxplot(), outlier_qqplot(), outlier_diagnostics()\n")
cat("  分布法: outlier_3sigma(), outlier_iqr(), outlier_hampel(), outlier_lof()\n")
cat("  经验法: winsorize(), winsorize_df()\n")
cat("  检验法: outlier_grubbs(), outlier_rosner()\n")
cat("  决策:  outlier_handle()\n")
