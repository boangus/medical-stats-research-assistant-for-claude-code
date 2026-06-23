# =============================================================================
# 异常值交互决策模板 (Outlier Decision Template)
# 补充 outlier_detection_template.R 的检测功能
# 来源：实战医学统计课程第9章 (outlierKD + KM聚类 + easystats)
# =============================================================================

# 依赖：ggplot2, car, patchwork, cluster, factoextra (可选)

# ---- S1 综合异常值仪表盘 ----

#' 异常值综合检查仪表盘
#' 对单个连续变量生成4面板诊断图
#' @param data 数据框
#' @param var 变量名（不加引号）
#' @return 4面板 ggplot 对象
outlier_inspect <- function(data, var) {
  var_name <- deparse(substitute(var))
  x <- data[[var_name]]
  x <- x[!is.na(x)]

  # 统计量
  q1 <- quantile(x, 0.25)
  q3 <- quantile(x, 0.75)
  iqr_val <- q3 - q1
  lower <- q1 - 1.5 * iqr_val
  upper <- q3 + 1.5 * iqr_val
  outliers <- x[x < lower | x > upper]

  cat(sprintf("变量: %s\n", var_name))
  cat(sprintf("  N=%d, 缺失=%d\n", length(x) + sum(is.na(data[[var_name]])),
              sum(is.na(data[[var_name]]))))
  cat(sprintf("  均值=%.2f, 中位数=%.2f, SD=%.2f\n", mean(x), median(x), sd(x)))
  cat(sprintf("  Q1=%.2f, Q3=%.2f, IQR=%.2f\n", q1, q3, iqr_val))
  cat(sprintf("  异常值边界: [%.2f, %.2f]\n", lower, upper))
  cat(sprintf("  异常值数量: %d (%.1f%%)\n", length(outliers),
              length(outliers) / length(x) * 100))

  # Panel 1: 箱线图
  p1 <- ggplot2::ggplot(data.frame(x = x), ggplot2::aes(y = x)) +
    ggplot2::geom_boxplot(fill = "lightblue", outlier.color = "red") +
    ggplot2::labs(title = "Boxplot", y = var_name) +
    ggplot2::theme_minimal()

  # Panel 2: 直方图
  p2 <- ggplot2::ggplot(data.frame(x = x), ggplot2::aes(x = x)) +
    ggplot2::geom_histogram(bins = 30, fill = "steelblue", alpha = 0.7) +
    ggplot2::geom_vline(xintercept = c(lower, upper), color = "red", linetype = 2) +
    ggplot2::labs(title = "Histogram", x = var_name) +
    ggplot2::theme_minimal()

  # Panel 3: QQ图
  p3 <- ggplot2::ggplot(data.frame(x = x), ggplot2::aes(sample = x)) +
    ggplot2::stat_qq() +
    ggplot2::stat_qq_line(color = "red") +
    ggplot2::labs(title = "Q-Q Plot") +
    ggplot2::theme_minimal()

  # Panel 4: Cook距离（如果有其他变量可做回归）
  # 这里用简化版：Z-score散点
  z <- scale(x)
  p4 <- ggplot2::ggplot(data.frame(index = seq_along(z), z = as.numeric(z)),
                        ggplot2::aes(x = index, y = z)) +
    ggplot2::geom_point(color = ifelse(abs(as.numeric(z)) > 2, "red", "grey50"),
                        size = 1.5) +
    ggplot2::geom_hline(yintercept = c(-2, 2), color = "red", linetype = 2) +
    ggplot2::labs(title = "Z-score (>2 flagged)", x = "Index", y = "Z-score") +
    ggplot2::theme_minimal()

  # 组合
  combined <- p1 + p2 + p3 + p4 +
    patchwork::plot_layout(ncol = 2) +
    patchwork::plot_annotation(title = paste("异常值诊断:", var_name))

  print(combined)

  invisible(list(
    variable = var_name,
    n = length(x),
    n_outlier = length(outliers),
    pct_outlier = round(length(outliers) / length(x) * 100, 1),
    bounds = c(lower = lower, upper = upper),
    outlier_values = outliers
  ))
}

# ---- S2 交互式异常值决策 ----

#' 异常值交互式决策函数
#' 根据异常值比例自动推荐处理方案
#' 基于课程资料 outlierKD 函数改进
#' @param data 数据框
#' @param var 变量名（不加引号）
#' @param method 异常值检测方法: "iqr"(默认), "3sigma", "hampel"
#' @param auto 是否自动执行推荐方案（FALSE=交互确认）
#' @return 处理后的数据框
outlier_decide <- function(data, var, method = "iqr", auto = FALSE) {
  var_name <- deparse(substitute(var))
  x <- data[[var_name]]
  na_before <- sum(is.na(x))

  # 检测异常值
  outlier_values <- switch(method,
    iqr = {
      q <- quantile(x, c(0.25, 0.75), na.rm = TRUE)
      iqr_val <- q[2] - q[1]
      x[!is.na(x) & (x < q[1] - 1.5 * iqr_val | x > q[2] + 1.5 * iqr_val)]
    },
    sigma3 = {
      m <- mean(x, na.rm = TRUE)
      s <- sd(x, na.rm = TRUE)
      x[!is.na(x) & (x < m - 3 * s | x > m + 3 * s)]
    },
    hampel = {
      m <- median(x, na.rm = TRUE)
      mad_val <- mad(x, na.rm = TRUE)
      x[!is.na(x) & (x < m - 3 * mad_val | x > m + 3 * mad_val)]
    }
  )

  n_outlier <- length(outlier_values)
  pct_outlier <- round(n_outlier / sum(!is.na(x)) * 100, 1)

  cat(sprintf("\n========== 异常值决策: %s (方法: %s) ==========\n", var_name, method))
  cat(sprintf("样本量: %d, 缺失: %d, 异常值: %d (%.1f%%)\n",
              length(x), na_before, n_outlier, pct_outlier))
  cat(sprintf("异常值范围: %s\n",
              if (n_outlier > 0) paste(range(outlier_values), collapse = " ~ ") else "无"))

  # 推荐方案
  if (n_outlier == 0) {
    cat("\n推荐: 无异常值，无需处理\n")
    return(data)
  } else if (pct_outlier < 1) {
    cat("\n推荐: 【检查录入错误】\n")
    cat("  异常比例<1%，可能是数据录入错误，建议核查原始数据\n")
    action <- "check"
  } else if (pct_outlier <= 5) {
    cat("\n推荐: 【Winsorize盖帽法】或【敏感性分析】\n")
    cat("  异常比例1-5%，建议盖帽法(P1/P99)处理，同时保留原始数据做敏感性分析\n")
    action <- "winsorize"
  } else {
    cat("\n推荐: 【检查分布 + 考虑变换】\n")
    cat("  异常比例>5%，建议检查数据分布，考虑对数变换或非参数方法\n")
    action <- "transform"
  }

  # 执行决策
  if (auto || action == "check") {
    cat(sprintf("\n自动执行: 标记异常值为NA (共%d个)\n", n_outlier))
    data[[var_name]][data[[var_name]] %in% outlier_values] <- NA
  } else {
    cat("\n请确认处理方案:\n")
    cat("  [1] 标记为NA\n")
    cat("  [2] Winsorize盖帽 (P1/P99)\n")
    cat("  [3] 保持不变\n")

    if (!auto) {
      response <- readline("选择 (1/2/3): ")
      if (response == "1") {
        data[[var_name]][data[[var_name]] %in% outlier_values] <- NA
        cat("已标记为NA\n")
      } else if (response == "2") {
        ll <- quantile(data[[var_name]], 0.01, na.rm = TRUE)
        ul <- quantile(data[[var_name]], 0.99, na.rm = TRUE)
        data[[var_name]][data[[var_name]] < ll & !is.na(data[[var_name]])] <- ll
        data[[var_name]][data[[var_name]] > ul & !is.na(data[[var_name]])] <- ul
        cat(sprintf("已Winsorize: [%.2f, %.2f]\n", ll, ul))
      } else {
        cat("保持不变\n")
      }
    }
  }

  invisible(data)
}

# ---- S3 KM聚类多维异常检测 ----

#' K-Means 聚类异常值检测
#' 基于样本到聚类中心的距离识别异常值
#' @param data 数据框（仅数值列）
#' @param k 聚类数，默认3
#' @param top_n 识别前N个最异常的样本，默认5
#' @param seed 随机种子
#' @return 异常样本索引和距离
outlier_kmeans <- function(data, k = 3, top_n = 5, seed = 123) {
  cat(sprintf("========== KM聚类异常检测 (k=%d) ==========\n", k))

  # 仅保留数值列
  numeric_data <- data[, sapply(data, is.numeric), drop = FALSE]
  numeric_data <- na.omit(numeric_data)

  set.seed(seed)
  km <- kmeans(numeric_data, centers = k)

  # 计算每个样本到其聚类中心的距离
  centers <- km$centers[km$cluster, ]
  distances <- sqrt(rowSums((numeric_data - centers)^2))

  # 识别最远的样本
  outlier_idx <- order(distances, decreasing = TRUE)[1:min(top_n, nrow(numeric_data))]

  cat(sprintf("聚类分布: %s\n", paste(table(km$cluster), collapse = " / ")))
  cat(sprintf("\nTop %d 异常样本 (距聚类中心最远):\n", top_n))
  result <- data.frame(
    index = outlier_idx,
    cluster = km$cluster[outlier_idx],
    distance = round(distances[outlier_idx], 3)
  )
  print(result)

  cat("\n提示: 距离显著大于其他样本的点可能是多维异常值\n")

  invisible(list(
    cluster = km,
    distances = distances,
    outliers = outlier_idx,
    outlier_table = result
  ))
}

# ---- S4 异常值处理报告 ----

#' 生成异常值处理报告
#' @param data 原始数据框
#' @param vars 需要检查的变量列表
#' @param method 检测方法
#' @return 处理报告
outlier_report <- function(data, vars = NULL, method = "iqr") {
  cat("╔══════════════════════════════════════╗\n")
  cat("║     异常值处理报告                    ║\n")
  cat("╚══════════════════════════════════════╝\n\n")

  if (is.null(vars)) {
    vars <- names(data)[sapply(data, is.numeric)]
  }

  report <- data.frame(
    variable = character(),
    n = integer(),
    n_outlier = integer(),
    pct_outlier = numeric(),
    action = character(),
    stringsAsFactors = FALSE
  )

  for (v in vars) {
    x <- data[[v]]
    x <- x[!is.na(x)]

    outlier_values <- switch(method,
      iqr = {
        q <- quantile(x, c(0.25, 0.75))
        iqr_val <- q[2] - q[1]
        x[x < q[1] - 1.5 * iqr_val | x > q[2] + 1.5 * iqr_val]
      },
      hampel = {
        m <- median(x)
        mad_val <- mad(x)
        x[x < m - 3 * mad_val | x > m + 3 * mad_val]
      }
    )

    pct <- round(length(outlier_values) / length(x) * 100, 1)
    action <- if (length(outlier_values) == 0) "无"
              else if (pct < 1) "检查录入"
              else if (pct <= 5) "盖帽/敏感性"
              else "变换/非参数"

    report <- rbind(report, data.frame(
      variable = v, n = length(x),
      n_outlier = length(outlier_values),
      pct_outlier = pct, action = action,
      stringsAsFactors = FALSE
    ))
  }

  report <- report[order(-report$pct_outlier), ]
  print(report)

  cat("\n参照: anti-pattern C1 (禁止自动静默校正异常值)\n")

  invisible(report)
}

# ---- 使用示例 ----
# # 1. 综合仪表盘检查
# outlier_inspect(mydata, age)
#
# # 2. 交互式决策
# mydata <- outlier_decide(mydata, age, method = "iqr")
#
# # 3. KM聚类多维异常检测
# result <- outlier_kmeans(mydata[, c("age", "bmi", "sbp", "dbp")], k = 3)
#
# # 4. 批量异常值报告
# outlier_report(mydata, vars = c("age", "bmi", "sbp", "dbp"))
