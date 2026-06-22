# rcs_template.R — 限制性立方样条 (RCS) 非线性关系分析模板
# ================================================================
# 适用于：连续自变量与结局的非线性关系探索（Logistic/Cox/Linear/Quasi-Poisson）
# 核心功能：AIC自动选节点 → 非线性检验 → OR/HR曲线绘制 → 出版级图形
#
# 依赖: rms, survival, ggplot2, ggsci (可选)
# 安装: install.packages(c("rms", "survival", "ggplot2", "ggsci"))
#
# 参考: 实战医学统计课程 Ch10, rcssci包
# 作者: MSRA Team
# 版本: 0.1.0

library(rms)
library(ggplot2)

# ============================================================================
# 1. AIC 自动选择最优节点数
# ============================================================================

#' 通过 AIC 最小化选择 RCS 最优节点数
#'
#' 遍历 knot = 3:max_knot，对每个节点数拟合模型，返回 AIC 最小的节点数。
#' 支持 lrm (Logistic), cph (Cox), ols (Linear), glm (Quasi-Poisson) 四种框架。
#'
#' @param formula_base 基础公式字符串，如 "y ~ age + gender"（不含 RCS 项）
#' @param x 连续自变量名（字符串）
#' @param data 数据框
#' @param type 回归类型: "logistic", "cox", "linear", "quasipoisson"
#' @param time 生存时间变量名（仅 type="cox" 时需要）
#' @param max_knot 最大节点数（默认 7）
#' @param min_knot 最小节点数（默认 3）
#'
#' @return list(best_knot = 最优节点数, aics = 所有AIC值向量)
rcs_select_knot <- function(formula_base, x, data,
                             type = "logistic",
                             time = NULL,
                             max_knot = 7,
                             min_knot = 3) {
  type <- match.arg(type, c("logistic", "cox", "linear", "quasipoisson"))
  knots <- min_knot:max_knot
  aics <- numeric(length(knots))

  for (i in seq_along(knots)) {
    k <- knots[i]
    formula_str <- paste0(formula_base, " + rcs(", x, ", ", k, ")")
    f <- as.formula(formula_str)

    fit <- switch(type,
      "logistic" = lrm(f, data = data, x = TRUE, y = TRUE),
      "cox"      = {
        S <- Surv(data[[time]], data[[gsub(".*~\\s*", "", formula_base)]] == 1)
        cph(update.formula(f, S ~ .), data = data, x = TRUE, y = TRUE, surv = TRUE)
      },
      "linear"   = ols(f, data = data, x = TRUE, y = TRUE),
      "quasipoisson" = glm(f, data = data, family = quasipoisson())
    )

    aics[i] <- if (type == "quasipoisson") extractAIC(fit)[2] else AIC(fit)
  }

  best_knot <- knots[which.min(aics)]
  names(aics) <- paste0("k=", knots)

  cat(sprintf("✅ AIC 选节点: best_knot = %d (AIC = %.2f)\n", best_knot, min(aics)))
  cat("   各节点AIC:", paste(paste0(names(aics), "=", sprintf("%.1f", aics)), collapse = ", "), "\n")

  return(list(best_knot = best_knot, aics = aics))
}


# ============================================================================
# 2. RCS 拟合 + 非线性检验
# ============================================================================

#' 拟合 RCS 模型并检验非线性
#'
#' @param formula_base 基础公式字符串（不含 RCS 项）
#' @param x 连续自变量名
#' @param knot 节点数（NULL 则自动选择）
#' @param data 数据框
#' @param type 回归类型
#' @param time 生存时间变量名（仅 cox）
#' @param ref_prob 参考值分位数（默认 0.1，即 P10 作为 HR=1 的参考点）
#'
#' @return list(fit = 模型对象, knot = 节点数, p_nonlinear = 非线性P值,
#'              anova_table = anova表, pred = Predict对象)
rcs_fit <- function(formula_base, x, knot = NULL, data,
                     type = "logistic", time = NULL,
                     ref_prob = 0.1) {
  type <- match.arg(type, c("logistic", "cox", "linear", "quasipoisson"))

  # 自动选节点
  if (is.null(knot)) {
    sel <- rcs_select_knot(formula_base, x, data, type, time)
    knot <- sel$best_knot
  }

  # 构建完整公式
  formula_str <- paste0(formula_base, " + rcs(", x, ", ", knot, ")")
  f <- as.formula(formula_str)

  # 设定 rms 数据环境
  dd <- datadist(data)
  options(datadist = "dd")

  # 设定参考值 (ref_prob 分位数)
  ref_val <- quantile(data[[x]], probs = ref_prob, na.rm = TRUE)
  dd$limits[[x]][1] <- ref_val  # 设置 reference
  options(datadist = "dd")

  # 拟合模型
  fit <- switch(type,
    "logistic" = lrm(f, data = data, x = TRUE, y = TRUE),
    "cox" = {
      y_var <- trimws(gsub("~.*", "", formula_base))
      S <- Surv(data[[time]], data[[y_var]] == 1)
      cph(update.formula(f, S ~ .), data = data, x = TRUE, y = TRUE, surv = TRUE)
    },
    "linear" = ols(f, data = data, x = TRUE, y = TRUE),
    "quasipoisson" = glm(f, data = data, family = quasipoisson())
  )

  # 非线性检验
  aov <- anova(fit)
  # 提取 p-non-linear (RCS 非线性项的 P 值)
  # anova 表中包含 Nonlinear 行
  p_nl <- NA
  tryCatch({
    # 对于 lrm/cph/ols, anova 返回矩阵，行名含 "Nonlinear" 或 "TOTAL NONLINEAR"
    row_names <- rownames(aov)
    nl_row <- grep("Nonlinear|NONLINEAR", row_names, ignore.case = TRUE)
    if (length(nl_row) > 0) {
      p_nl <- aov[nl_row[length(nl_row)], "P"]
    }
  }, error = function(e) {
    # glm 的 anova 格式不同，尝试 deviance 解释
    p_nl <<- NA
  })

  # 生成预测值
  fun_exp <- if (type %in% c("logistic", "cox")) exp else identity
  y_label <- switch(type,
    "logistic" = "OR",
    "cox"      = "HR",
    "linear"   = "Predicted Y",
    "quasipoisson" = "IRR"
  )

  pred <- rms::Predict(fit, !!sym(x), fun = fun_exp,
                        type = "predictions", ref.zero = TRUE,
                        conf.int = 0.95, digits = 2)

  cat(sprintf("\n📊 RCS 拟合结果 (knot=%d):\n", knot))
  cat(sprintf("   非线性检验 P = %s\n",
              ifelse(is.na(p_nl), "N/A (需手动检查anova表)", format.pval(p_nl, digits = 3))))
  cat(sprintf("   参考值: %s = %.2f (P%.0f)\n", x, ref_val, ref_prob * 100))
  cat(sprintf("   效应尺度: %s\n", y_label))

  return(list(
    fit = fit,
    knot = knot,
    p_nonlinear = p_nl,
    anova_table = aov,
    pred = as.data.frame(pred),
    ref_val = ref_val,
    y_label = y_label,
    type = type
  ))
}


# ============================================================================
# 3. RCS 标准绘图 (ggplot2)
# ============================================================================

#' 绘制 RCS 曲线图 (ggplot2 出版级)
#'
#' @param rcs_result rcs_fit() 返回的对象
#' @param x_label X 轴标签
#' @param y_label Y 轴标签（默认自动根据 type 选择）
#' @param title 标题
#' @param color 曲线颜色
#' @param show_ref 是否显示参考值标注
#' @param add_p 是否在图上标注非线性 P 值
#'
#' @return ggplot 对象
rcs_plot <- function(rcs_result,
                     x_label = NULL,
                     y_label = NULL,
                     title = NULL,
                     color = "#2E86C1",
                     show_ref = TRUE,
                     add_p = TRUE) {

  pred_df <- rcs_result$pred
  x_name <- names(pred_df)[1]  # 第一列是 x 变量

  if (is.null(x_label)) x_label <- x_name
  if (is.null(y_label)) y_label <- rcs_result$y_label
  if (is.null(title)) title <- paste0("RCS: ", x_name, " and outcome")

  # 主曲线图
  p <- ggplot(pred_df, aes(x = .data[[x_name]], y = yhat)) +
    # 置信区间带
    geom_ribbon(aes(ymin = lower, ymax = upper),
                fill = color, alpha = 0.15) +
    # 主曲线
    geom_line(color = color, linewidth = 1.2) +
    # HR/OR = 1 参考线
    geom_hline(yintercept = 1, linetype = "dashed",
               color = "grey40", linewidth = 0.7) +
    # 主题
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5, size = 13),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40", size = 10),
      axis.title = element_text(size = 11),
      panel.grid.minor = element_blank()
    ) +
    labs(
      title = title,
      x = x_label,
      y = paste0(y_label, " (95% CI)")
    )

  # 参考值标注
  if (show_ref) {
    ref_val <- rcs_result$ref_val
    p <- p +
      geom_point(aes(x = ref_val, y = 1),
                 color = "red", size = 3, shape = 19) +
      annotate("text", x = ref_val, y = 0.85,
               label = paste0("Ref = ", sprintf("%.1f", ref_val)),
               color = "red", size = 3.5, fontface = "italic")
  }

  # 非线性 P 值标注
  if (add_p && !is.na(rcs_result$p_nonlinear)) {
    p_text <- paste0("P for nonlinearity = ",
                     format.pval(rcs_result$p_nonlinear, digits = 3))
    p <- p + annotate("text",
                       x = min(pred_df[[x_name]], na.rm = TRUE),
                       y = max(pred_df$upper, na.rm = TRUE) * 0.95,
                       label = p_text, hjust = 0, size = 3.5,
                       color = "grey30", fontface = "italic")
  }

  return(p)
}


# ============================================================================
# 4. 直方图 + RCS 叠加图 (展示数据分布)
# ============================================================================

#' 绘制直方图 + RCS 曲线叠加图
#'
#' 使用 base R 的 par(new=T) 技巧叠加直方图和 RCS 曲线，
#' 左侧 Y 轴为效应尺度 (OR/HR)，右侧 Y 轴为频数。
#'
#' @param rcs_result rcs_fit() 返回的对象
#' @param data 原始数据框
#' @param x 连续自变量名
#' @param x_label X 轴标签
#' @param hist_color 直方图颜色
#' @param line_color 曲线颜色
#' @param output_file 输出文件路径 (PDF/TIFF)，NULL 则不保存
#' @param width 图宽 (cm)
#' @param height 图高 (cm)
#'
#' @return invisible(NULL)，同时在当前设备绘图
rcs_plot_with_hist <- function(rcs_result, data, x,
                                x_label = NULL,
                                hist_color = "#D6EAF8",
                                line_color = "#E74C3C",
                                output_file = NULL,
                                width = 15,
                                height = 15) {

  pred_df <- rcs_result$pred
  if (is.null(x_label)) x_label <- x

  # X 轴范围
  x_range <- range(data[[x]], na.rm = TRUE)
  x_lim <- c(floor(x_range[1] / 10) * 10, ceiling(x_range[2] / 10) * 10)

  # Y 轴范围 (效应尺度)
  y_max <- ceiling(max(pred_df$upper, na.rm = TRUE))
  y_max <- max(y_max, 2)  # 至少到 2

  # 开始绘图
  if (!is.null(output_file)) {
    ext <- tolower(tools::file_ext(output_file))
    if (ext == "pdf") {
      pdf(output_file, onefile = FALSE, width = width / 2.54, height = height / 2.54)
    } else if (ext == "tiff") {
      tiff(output_file, width = width, height = height, units = "cm",
           res = 600, compression = "lzw+p")
    } else {
      png(output_file, width = width, height = height, units = "cm", res = 300)
    }
  }

  # 第一层: 直方图
  par(mar = c(4, 4, 1, 5))
  hist(data[[x]], axes = FALSE, xlab = "", ylab = "",
       xlim = x_lim, col = hist_color, main = "", freq = TRUE,
       border = "grey70")
  axis(4)  # 右侧 Y 轴 (频数)
  mtext("Frequency", side = 4, line = 3, outer = FALSE)

  # 第二层: RCS 曲线
  par(new = TRUE)
  plot(pred_df[[1]], pred_df$yhat, type = "l", lty = 1, lwd = 2,
       col = line_color, xlim = x_lim, ylim = c(0, y_max),
       axes = TRUE, xlab = x_label,
       ylab = paste0(rcs_result$y_label, " (95% CI)"))

  # 置信区间填充
  ci_col <- adjustcolor(line_color, alpha.f = 0.15)
  polygon(c(pred_df[[1]], rev(pred_df[[1]])),
          c(pred_df$lower, rev(pred_df$upper)),
          col = ci_col, border = ci_col)

  # 置信区间虚线
  lines(pred_df[[1]], pred_df$lower, lty = 2, lwd = 1.5, col = line_color)
  lines(pred_df[[1]], pred_df$upper, lty = 2, lwd = 1.5, col = line_color)

  # 参考线
  abline(h = 1, col = "black", lty = 2, lwd = 0.8)

  # 参考值标注
  ref_val <- rcs_result$ref_val
  points(ref_val, 1, pch = 19, col = "red", cex = 1.2)
  text(ref_val + diff(x_lim) * 0.03, 0.5,
       paste0("Ref = ", sprintf("%.1f", ref_val)),
       cex = 0.9, font = 3, col = "red")

  if (!is.null(output_file)) {
    dev.off()
    cat(sprintf("✅ 图形已保存: %s\n", output_file))
  }

  invisible(NULL)
}


# ============================================================================
# 5. 分层 RCS 图 (按亚组)
# ============================================================================

#' 绘制分层 RCS 曲线图
#'
#' @param rcs_result rcs_fit() 返回的对象
#' @param data 原始数据框
#' @param x 连续自变量名
#' @param strat_var 分层变量名
#' @param strat_labels 分层标签（命名向量，如 c("1"="Male", "2"="Female")）
#' @param x_label X 轴标签
#' @param colors 各层颜色向量
#'
#' @return ggplot 对象
rcs_plot_stratified <- function(rcs_result, data, x, strat_var,
                                 strat_labels = NULL,
                                 x_label = NULL,
                                 colors = c("#2E86C1", "#E74C3C", "#27AE60", "#F39C12")) {

  fit <- rcs_result$fit
  type <- rcs_result$type

  fun_exp <- if (type %in% c("logistic", "cox")) exp else identity

  # 获取分层水平
  levels_val <- unique(data[[strat_var]])
  if (is.null(strat_labels)) {
    strat_labels <- setNames(as.character(levels_val), as.character(levels_val))
  }

  # 生成各层预测
  pred_list <- lapply(seq_along(levels_val), function(i) {
    lv <- levels_val[i]
    pred <- rms::Predict(fit, !!sym(x),
                          !!sym(strat_var) := lv,
                          fun = fun_exp, ref.zero = TRUE,
                          conf.int = 0.95)
    df <- as.data.frame(df <- pred)
    df$strata <- strat_labels[as.character(lv)]
    df
  })

  pred_all <- do.call(rbind, pred_list)
  x_name <- names(pred_all)[1]

  if (is.null(x_label)) x_label <- x

  p <- ggplot(pred_all, aes(x = .data[[x_name]], y = yhat,
                             color = strata, fill = strata)) +
    geom_ribbon(aes(ymin = lower, ymax = upper), alpha = 0.1, color = NA) +
    geom_line(linewidth = 1.1) +
    geom_hline(yintercept = 1, linetype = "dashed",
               color = "grey40", linewidth = 0.7) +
    scale_color_manual(values = colors[1:length(levels_val)]) +
    scale_fill_manual(values = colors[1:length(levels_val)]) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = c(0.15, 0.85),
      legend.background = element_rect(fill = "white", color = "grey80"),
      legend.title = element_text(size = 10),
      panel.grid.minor = element_blank()
    ) +
    labs(
      title = paste0("Stratified RCS: ", x, " by ", strat_var),
      x = x_label,
      y = paste0(rcs_result$y_label, " (95% CI)"),
      color = strat_var,
      fill = strat_var
    )

  return(p)
}


# ============================================================================
# 6. PH 假设检验 (仅 Cox 模型)
# ============================================================================

#' Cox 模型 PH 假设检验 + 残差图
#'
#' @param rcs_result rcs_fit() 返回的对象 (type 必须为 "cox")
#'
#' @return list(ph_test = cox.zph 结果, ph_plot = ggplot 残差图)
rcs_ph_test <- function(rcs_result) {
  if (rcs_result$type != "cox") {
    stop("PH 检验仅适用于 Cox 回归模型")
  }

  fit <- rcs_result$fit
  ph <- cox.zph(fit, "rank")

  cat("\n📊 PH 假设检验 (Schoenfeld 残差):\n")
  print(ph)

  # 残差图
  ph_df <- as.data.frame(ph$y)
  ph_df$time <- ph$x

  p_list <- lapply(colnames(ph$y), function(var) {
    ggplot(ph_df, aes(x = time, y = .data[[var]])) +
      geom_point(alpha = 0.4, size = 1, color = "grey40") +
      geom_smooth(method = "loess", se = TRUE, color = "#E74C3C",
                  linewidth = 1, alpha = 0.2) +
      geom_hline(yintercept = 0, linetype = "dashed", color = "grey60") +
      theme_classic(base_size = 10) +
      labs(title = var, x = "Time", y = "Schoenfeld Residual")
  })

  # 合并多图
  if (length(p_list) == 1) {
    p <- p_list[[1]]
  } else {
    p <- patchwork::wrap_plots(p_list, ncol = min(3, length(p_list)))
  }

  return(list(ph_test = ph, ph_plot = p))
}


# ============================================================================
# 7. 多项式/样条/GAM 方法比较
# ============================================================================

#' 比较 RCS 与其他非线性方法
#'
#' 使用相同数据比较 RCS、多项式、样条、GAM 等方法的拟合效果。
#' 适用于连续型结局变量。
#'
#' @param data 数据框
#' @param y 连续结局变量名
#' @param x 连续自变量名
#' @param covs 协变量名向量
#'
#' @return list(metrics = 比较指标表, plot = 可视化图)
rcs_compare_methods <- function(data, y, x, covs = NULL) {
  library(splines)
  library(mgcv)

  # 训练/测试集划分
  set.seed(42)
  train_idx <- sample(nrow(data), 0.8 * nrow(data))
  train <- data[train_idx, ]
  test <- data[-train_idx, ]

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  # 模型列表
  formulas <- list(
    "Linear"     = paste0(y, " ~ ", x, covs_str),
    "Log"        = paste0(y, " ~ log(", x, ")", covs_str),
    "Poly-2"     = paste0(y, " ~ poly(", x, ", 2, raw=TRUE)", covs_str),
    "Poly-3"     = paste0(y, " ~ poly(", x, ", 3, raw=TRUE)", covs_str),
    "RCS-3"      = paste0(y, " ~ rcs(", x, ", 3)", covs_str),
    "RCS-4"      = paste0(y, " ~ rcs(", x, ", 4)", covs_str),
    "Spline-3"   = paste0(y, " ~ bs(", x, ", df=3)", covs_str),
    "GAM"        = paste0(y, " ~ s(", x, ")", covs_str)
  )

  results <- do.call(rbind, lapply(names(formulas), function(m_name) {
    f <- as.formula(formulas[[m_name]])
    tryCatch({
      if (m_name == "GAM") {
        fit <- gam(f, data = train)
      } else {
        fit <- lm(f, data = train)
      }
      pred <- predict(fit, newdata = test)
      data.frame(
        Model = m_name,
        RMSE = sqrt(mean((test[[y]] - pred)^2, na.rm = TRUE)),
        R2 = cor(test[[y]], pred, use = "complete.obs")^2,
        AIC = if (m_name == "GAM") AIC(fit) else AIC(fit),
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      data.frame(Model = m_name, RMSE = NA, R2 = NA, AIC = NA,
                 stringsAsFactors = FALSE)
    })
  }))

  # 可视化
  p <- ggplot(results, aes(x = reorder(Model, RMSE), y = RMSE)) +
    geom_col(fill = "#2E86C1", alpha = 0.7, width = 0.6) +
    geom_text(aes(label = sprintf("%.3f", RMSE)), vjust = -0.5, size = 3.5) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      axis.text.x = element_text(angle = 30, hjust = 1)
    ) +
    labs(
      title = "Nonlinear Methods Comparison (RMSE, lower is better)",
      x = "", y = "RMSE (Test Set)"
    )

  cat("\n📊 非线性方法比较:\n")
  print(results[order(results$RMSE), ])

  return(list(metrics = results, plot = p))
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # ------ 示例 1: Logistic RCS ------
  # 模拟数据
  set.seed(42)
  n <- 500
  sbp <- rnorm(n, 130, 20)
  age <- rnorm(n, 55, 10)
  gender <- rbinom(n, 1, 0.5)
  # 非线性关系: U 型
  logit_p <- -3 + 0.02 * (sbp - 130)^2 / 100 + 0.03 * age + 0.5 * gender
  status <- rbinom(n, 1, plogis(logit_p))
  df <- data.frame(sbp, age, gender, status)

  # 步骤1: 自动选节点 + 拟合
  res_logistic <- rcs_fit(
    formula_base = "status ~ age + gender",
    x = "sbp", data = df, type = "logistic"
  )

  # 步骤2: 标准 RCS 图
  p1 <- rcs_plot(res_logistic, x_label = "Systolic BP (mmHg)")
  ggsave("rcs_logistic.png", p1, width = 8, height = 6, dpi = 300)

  # 步骤3: 直方图叠加
  rcs_plot_with_hist(res_logistic, df, "sbp",
                      x_label = "Systolic BP (mmHg)",
                      output_file = "rcs_logistic_hist.pdf")

  # ------ 示例 2: Cox RCS ------
  library(survival)
  time <- rexp(n, rate = 0.02 * exp(0.01 * (sbp - 120)^2 / 100))
  event <- rbinom(n, 1, 0.8)
  df_surv <- data.frame(sbp, age, gender, time, status = event)

  res_cox <- rcs_fit(
    formula_base = "status ~ age + gender",
    x = "sbp", data = df_surv, type = "cox", time = "time"
  )

  p2 <- rcs_plot(res_cox, x_label = "Systolic BP (mmHg)")
  ggsave("rcs_cox.png", p2, width = 8, height = 6, dpi = 300)

  # PH 检验
  ph_res <- rcs_ph_test(res_cox)

  # ------ 示例 3: 分层 RCS ------
  p3 <- rcs_plot_stratified(res_cox, df_surv, "sbp", "gender",
                              strat_labels = c("0" = "Female", "1" = "Male"))
  ggsave("rcs_stratified.png", p3, width = 8, height = 6, dpi = 300)

  # ------ 示例 4: 方法比较 (连续结局) ------
  df_cont <- data.frame(sbp, age, gender, y_cont = rnorm(n, sbp * 0.5, 10))
  comp <- rcs_compare_methods(df_cont, y = "y_cont", x = "sbp",
                               covs = c("age", "gender"))

  cat("✅ RCS 模板示例完成\n")
}

cat("✅ rcs_template.R 已加载\n")
cat("可用函数:\n")
cat("  rcs_select_knot()         - AIC 自动选节点\n")
cat("  rcs_fit()                 - RCS 拟合 + 非线性检验\n")
cat("  rcs_plot()                - 标准 RCS 曲线图 (ggplot2)\n")
cat("  rcs_plot_with_hist()      - 直方图 + RCS 叠加图\n")
cat("  rcs_plot_stratified()     - 分层 RCS 图\n")
cat("  rcs_ph_test()             - Cox PH 假设检验\n")
cat("  rcs_compare_methods()     - 非线性方法比较\n")
