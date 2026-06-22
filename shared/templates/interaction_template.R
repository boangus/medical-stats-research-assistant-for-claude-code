# interaction_template.R — 交互作用分析模板
# ==========================================
# 适用于：两个暴露因素的相乘交互和相加交互（RERI/AP/S）
# 支持 Logistic 回归 (OR) 和 Cox 回归 (HR)
#
# 核心方法：
#   - 相乘交互: 回归模型中交互项 X1×X2 的 P 值
#   - 相加交互: RERI (Relative Excess Risk due to Interaction)
#               AP (Attributable Proportion due to interaction)
#               S (Synergy Index)
#
# 依赖: epiR, interactionR, survival, ggplot2, visreg (可选)
# 安装: install.packages(c("epiR", "interactionR", "survival", "ggplot2", "visreg"))
#
# 参考: 实战医学统计课程 Ch13, Rothman 相加交互理论
# 作者: MSRA Team
# 版本: 0.1.0

library(ggplot2)

# ============================================================================
# 1. Logistic 相乘+相加交互 (epiR包)
# ============================================================================

#' Logistic 回归交互作用分析 (相乘 + 相加)
#'
#' @param data 数据框
#' @param y 结局变量名 (二分类 0/1)
#' @param x1 暴露因素1 (二分类 0/1)
#' @param x2 暴露因素2 (二分类 0/1)
#' @param covs 协变量名向量 (可选)
#' @param link 链接函数 (默认 "logit")
#'
#' @return list(model = glm对象, multiplicative = 相乘交互结果,
#'              additive = 相加交互结果 (RERI/AP/S))
interaction_logistic <- function(data, y, x1, x2, covs = NULL,
                                  link = "logit") {
  # 确保暴露因素为因子
  data[[x1]] <- as.factor(data[[x1]])
  data[[x2]] <- as.factor(data[[x2]])

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  # 拟合含交互项的 Logistic 回归
  formula_str <- paste0(y, " ~ ", x1, " + ", x2, " + ", x1, ":", x2, covs_str)
  fit <- glm(as.formula(formula_str), data = data, family = binomial(link = link))

  cat("\n📊 Logistic 交互作用分析:\n")
  cat("=" |> rep(50) |> paste(collapse = ""), "\n")

  # 相乘交互 (交互项 P 值)
  coef_names <- names(coef(fit))
  interaction_term <- grep(":", coef_names, value = TRUE)

  if (length(interaction_term) > 0) {
    int_coef <- coef(summary(fit))[interaction_term, ]
    cat(sprintf("\n  相乘交互:\n"))
    cat(sprintf("    交互项: %s\n", interaction_term))
    cat(sprintf("    OR = %.4f, 95%% CI: %.4f ~ %.4f, P = %s\n",
                exp(int_coef[1]),
                exp(int_coef[1] - 1.96 * int_coef[2]),
                exp(int_coef[1] + 1.96 * int_coef[2]),
                format.pval(int_coef[4], digits = 3)))
  }

  # 相加交互 (epiR包)
  additive <- NULL
  tryCatch({
    # 确定交互项在模型中的位置
    coef_idx <- grep(":", coef_names)
    if (length(coef_idx) > 0) {
      additive <- epiR::epi.interaction(model = fit, param = "product",
                                         coef = c(
                                           grep(paste0("^", x1), coef_names)[1],
                                           grep(paste0("^", x2), coef_names)[1],
                                           coef_idx[1]
                                         ),
                                         conf.level = 0.95)

      cat(sprintf("\n  相加交互 (RERI/AP/S):\n"))
      cat(sprintf("    RERI = %.4f (95%% CI: %.4f ~ %.4f)\n",
                  additive$reri[1], additive$reri[2], additive$reri[3]))
      cat(sprintf("    AP    = %.4f (95%% CI: %.4f ~ %.4f)\n",
                  additive$apab[1], additive$apab[2], additive$apab[3]))
      cat(sprintf("    S     = %.4f (95%% CI: %.4f ~ %.4f)\n",
                  additive$s[1], additive$s[2], additive$s[3]))
    }
  }, error = function(e) {
    cat("  ⚠️ epi.interaction 计算失败:", e$message, "\n")
  })

  return(list(
    model = fit,
    multiplicative = if (length(interaction_term) > 0) {
      list(term = interaction_term, coef = int_coef)
    } else NULL,
    additive = additive
  ))
}


# ============================================================================
# 2. Cox 相乘+相加交互 (epiR包)
# ============================================================================

#' Cox 回归交互作用分析 (相乘 + 相加)
#'
#' @param data 数据框
#' @param time 生存时间变量名
#' @param event 事件变量名 (0/1)
#' @param x1 暴露因素1 (二分类 0/1)
#' @param x2 暴露因素2 (二分类 0/1)
#' @param covs 协变量名向量 (可选)
#'
#' @return list(model = coxph对象, multiplicative, additive)
interaction_cox <- function(data, time, event, x1, x2, covs = NULL) {
  library(survival)

  data[[x1]] <- as.factor(data[[x1]])
  data[[x2]] <- as.factor(data[[x2]])

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  # 拟合含交互项的 Cox 回归
  formula_str <- paste0("Surv(", time, ", ", event, ") ~ ",
                         x1, " + ", x2, " + ", x1, ":", x2, covs_str)
  fit <- coxph(as.formula(formula_str), data = data)

  cat("\n📊 Cox 交互作用分析:\n")
  cat("=" |> rep(50) |> paste(collapse = ""), "\n")

  # 相乘交互
  coef_names <- names(coef(fit))
  interaction_term <- grep(":", coef_names, value = TRUE)

  if (length(interaction_term) > 0) {
    int_coef <- coef(summary(fit))[interaction_term, ]
    cat(sprintf("\n  相乘交互:\n"))
    cat(sprintf("    交互项: %s\n", interaction_term))
    cat(sprintf("    HR = %.4f, 95%% CI: %.4f ~ %.4f, P = %s\n",
                exp(int_coef[1]),
                exp(int_coef[1] - 1.96 * int_coef[2]),
                exp(int_coef[1] + 1.96 * int_coef[2]),
                format.pval(int_coef[4], digits = 3)))
  }

  # 相加交互
  additive <- NULL
  tryCatch({
    coef_idx <- grep(":", coef_names)
    if (length(coef_idx) > 0) {
      additive <- epiR::epi.interaction(model = fit, param = "product",
                                         coef = c(
                                           grep(paste0("^", x1), coef_names)[1],
                                           grep(paste0("^", x2), coef_names)[1],
                                           coef_idx[1]
                                         ),
                                         conf.level = 0.95)

      cat(sprintf("\n  相加交互 (RERI/AP/S):\n"))
      cat(sprintf("    RERI = %.4f (95%% CI: %.4f ~ %.4f)\n",
                  additive$reri[1], additive$reri[2], additive$reri[3]))
      cat(sprintf("    AP    = %.4f (95%% CI: %.4f ~ %.4f)\n",
                  additive$apab[1], additive$apab[2], additive$apab[3]))
      cat(sprintf("    S     = %.4f (95%% CI: %.4f ~ %.4f)\n",
                  additive$s[1], additive$s[2], additive$s[3]))
    }
  }, error = function(e) {
    cat("  ⚠️ epi.interaction 计算失败:", e$message, "\n")
  })

  return(list(
    model = fit,
    multiplicative = if (length(interaction_term) > 0) {
      list(term = interaction_term, coef = int_coef)
    } else NULL,
    additive = additive
  ))
}


# ============================================================================
# 3. interactionR 包 (Delta法 + Bootstrap法)
# ============================================================================

#' 使用 interactionR 包进行交互作用分析
#'
#' 提供 Delta 法和 Bootstrap 法两种置信区间估计。
#'
#' @param model 拟合好的 glm 或 coxph 模型 (含交互项)
#' @param exposure_names 暴露因素名向量 (长度为2)
#' @param ci_type CI 估计方法: "delta" (默认) 或 "mover"
#' @param boot_n Bootstrap 次数 (仅 bootstrap 法)
#' @param seed 随机种子
#'
#' @return list(delta = Delta法结果, bootstrap = Bootstrap法结果)
interactionR_analysis <- function(model, exposure_names,
                                   ci_type = "delta",
                                   boot_n = 1000, seed = 12345) {
  library(interactionR)

  cat("\n📊 interactionR 交互作用分析:\n")

  # Delta 法 (默认)
  cat("\n  --- Delta 法 ---\n")
  res_delta <- interactionR(model, exposure_names = exposure_names,
                             ci.type = ci_type, ci.level = 0.95,
                             em = FALSE, recode = FALSE)
  print(interactionR_table(res_delta))

  # Bootstrap 法
  cat("\n  --- Bootstrap 法 ---\n")
  res_boot <- interactionR_boot(model, ci.level = 0.95,
                                 em = FALSE, recode = FALSE,
                                 seed = seed, s = boot_n)
  print(interactionR_table(res_boot))

  return(list(delta = res_delta, bootstrap = res_boot))
}


# ============================================================================
# 4. 交互效应可视化
# ============================================================================

#' 绘制交互效应预测值图 (ggplot2)
#'
#' 展示在不同 X2 水平下，X1 对结局的预测效应。
#'
#' @param model 拟合好的模型 (glm/coxph)
#' @param x1 暴露因素1名 (X轴)
#' @param x2 暴露因素2名 (分层变量)
#' @param x1_label X1 轴标签
#' @param x2_label X2 图例标签
#' @param y_label Y 轴标签
#' @param title 标题
#' @param type 效应尺度: "response" (概率/OR) 或 "link" (log-odds)
#'
#' @return ggplot 对象
interaction_plot <- function(model, x1, x2,
                              x1_label = NULL, x2_label = NULL,
                              y_label = NULL, title = NULL,
                              type = "response") {
  if (is.null(x1_label)) x1_label <- x1
  if (is.null(x2_label)) x2_label <- x2
  if (is.null(y_label)) y_label <- "Predicted Probability"
  if (is.null(title)) title <- paste0("Interaction: ", x1, " × ", x2)

  # 生成预测数据
  data <- model$model
  x1_levels <- unique(data[[x1]])
  x2_levels <- unique(data[[x2]])

  # 构建预测网格
  pred_grid <- expand.grid(
    x1 = x1_levels,
    x2 = x2_levels
  )
  names(pred_grid) <- c(x1, x2)

  # 添加协变量（取均值/众数）
  for (col in names(data)) {
    if (!col %in% c(x1, x2, all.vars(formula(model))[1])) {
      if (is.numeric(data[[col]])) {
        pred_grid[[col]] <- mean(data[[col]], na.rm = TRUE)
      } else {
        pred_grid[[col]] <- names(sort(table(data[[col]]), decreasing = TRUE))[1]
      }
    }
  }

  # 预测
  pred_grid$predicted <- predict(model, newdata = pred_grid, type = type)

  # 标准误 (近似)
  if (type == "response" && inherits(model, "glm")) {
    pred_link <- predict(model, newdata = pred_grid, type = "link", se.fit = TRUE)
    pred_grid$se <- pred_link$se.fit
    # 通过 delta 方法近似
    link_inv <- model$family$linkinv
    pred_grid$lower <- link_inv(pred_link$fit - 1.96 * pred_link$se.fit)
    pred_grid$upper <- link_inv(pred_link$fit + 1.96 * pred_link$se.fit)
  } else {
    pred_grid$lower <- NA
    pred_grid$upper <- NA
  }

  # 绘图
  pred_grid[[x2]] <- as.factor(pred_grid[[x2]])

  p <- ggplot(pred_grid, aes(x = .data[[x1]], y = predicted,
                              color = .data[[x2]], group = .data[[x2]])) +
    geom_point(size = 3, position = position_dodge(width = 0.2)) +
    geom_line(linewidth = 1, position = position_dodge(width = 0.2)) +
    {if (!all(is.na(pred_grid$lower)))
      geom_errorbar(aes(ymin = lower, ymax = upper),
                    width = 0.1, linewidth = 0.8,
                    position = position_dodge(width = 0.2))
    } +
    scale_color_manual(values = c("#2E86C1", "#E74C3C", "#27AE60", "#F39C12")) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = "bottom",
      legend.background = element_rect(fill = "white", color = "grey80")
    ) +
    labs(
      title = title,
      x = x1_label,
      y = y_label,
      color = x2_label
    )

  return(p)
}


#' 绘制 visreg 交互效应图
#'
#' 使用 visreg 包绘制交互效应的偏效应图。
#'
#' @param model 拟合好的模型
#' @param x1 X 轴变量
#' @param x2 分层变量
#' @param scale "response" (概率尺度) 或 "link" (log-odds)
#'
#' @return visreg 图形对象
interaction_plot_visreg <- function(model, x1, x2, scale = "response") {
  if (!requireNamespace("visreg", quietly = TRUE)) {
    stop("请安装 visreg 包: install.packages('visreg')")
  }

  visreg::visreg(model, xvar = x1, by = x2,
                  scale = scale,
                  overlay = TRUE,
                  partial = FALSE,
                  rug = FALSE,
                  line = list(lty = 1:6),
                  xlab = x1,
                  ylab = if (scale == "response") "Predicted Probability" else "Log Odds")

  legend("topleft", legend = levels(as.factor(model$model[[x2]])),
         lty = 1, col = c("red", "blue"), lwd = 2, bty = "n")

  invisible(NULL)
}


#' 使用 sjPlot 绘制交互效应图 + 导出回归表到 Word
#'
#' @param model 拟合好的模型
#' @param x1 暴露因素1
#' @param x2 暴露因素2
#' @param output_file 导出 Word 文件路径 (NULL 则不导出)
#'
#' @return ggplot 对象
interaction_plot_sjplot <- function(model, x1, x2, output_file = NULL) {
  if (!requireNamespace("sjPlot", quietly = TRUE)) {
    stop("请安装 sjPlot 包: install.packages('sjPlot')")
  }

  p <- sjPlot::plot_model(model, type = "pred",
                            terms = c(x1, x2),
                            show.values = TRUE)

  if (!is.null(output_file)) {
    sjPlot::tab_model(model,
                       title = "Interaction Model",
                       show.stat = TRUE,
                       show.reflvl = TRUE,
                       string.ci = "95% CI",
                       string.p = "P-Value",
                       file = output_file)
    cat(sprintf("✅ 回归表已导出: %s\n", output_file))
  }

  return(p)
}


# ============================================================================
# 5. 交互作用汇总表
# ============================================================================

#' 生成交互作用结果汇总表
#'
#' @param inter_result interaction_logistic() 或 interaction_cox() 返回的对象
#' @param x1_label 暴露1标签
#' @param x2_label 暴露2标签
#'
#' @return data.frame
interaction_summary_table <- function(inter_result, x1_label = "X1",
                                       x2_label = "X2") {
  model <- inter_result$model
  is_cox <- inherits(model, "coxph")
  effect_label <- if (is_cox) "HR" else "OR"

  # 提取系数
  coef_tab <- coef(summary(model))
  coef_names <- rownames(coef_tab)

  # 找到交互项
  int_idx <- grep(":", coef_names)

  results <- data.frame(
    Component = character(),
    Estimate = numeric(),
    CI_lower = numeric(),
    CI_upper = numeric(),
    P_value = numeric(),
    stringsAsFactors = FALSE
  )

  # 主效应
  for (x in c(x1_label, x2_label)) {
    idx <- grep(paste0("^", x), coef_names)
    if (length(idx) > 0) {
      b <- coef_tab[idx[1], 1]
      se <- coef_tab[idx[1], 2]
      results <- rbind(results, data.frame(
        Component = paste0(effect_label, " for ", x),
        Estimate = exp(b),
        CI_lower = exp(b - 1.96 * se),
        CI_upper = exp(b + 1.96 * se),
        P_value = coef_tab[idx[1], 4],
        stringsAsFactors = FALSE
      ))
    }
  }

  # 交互项
  if (length(int_idx) > 0) {
    b <- coef_tab[int_idx[1], 1]
    se <- coef_tab[int_idx[1], 2]
    results <- rbind(results, data.frame(
      Component = paste0("Interaction (", x1_label, " × ", x2_label, ")"),
      Estimate = exp(b),
      CI_lower = exp(b - 1.96 * se),
      CI_upper = exp(b + 1.96 * se),
      P_value = coef_tab[int_idx[1], 4],
      stringsAsFactors = FALSE
    ))
  }

  # 相加交互
  if (!is.null(inter_result$additive)) {
    ad <- inter_result$additive
    results <- rbind(results, data.frame(
      Component = c("RERI", "AP", "S"),
      Estimate = c(ad$reri[1], ad$apab[1], ad$s[1]),
      CI_lower = c(ad$reri[2], ad$apab[2], ad$s[2]),
      CI_upper = c(ad$reri[3], ad$apab[3], ad$s[3]),
      P_value = c(NA, NA, NA),
      stringsAsFactors = FALSE
    ))
  }

  return(results)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # ------ 示例 1: Logistic 交互 ------
  set.seed(42)
  n <- 500
  df <- data.frame(
    a = rbinom(n, 1, 0.5),
    b = rbinom(n, 1, 0.5),
    sex = rbinom(n, 1, 0.5)
  )
  # 模拟交互效应
  df$y <- rbinom(n, 1, plogis(-2 + 0.5 * df$a + 0.3 * df$b +
                                0.8 * df$a * df$b + 0.2 * df$sex))

  # 分析
  res_log <- interaction_logistic(df, y = "y", x1 = "a", x2 = "b",
                                   covs = "sex")

  # interactionR
  res_ir <- interactionR_analysis(res_log$model, exposure_names = c("a", "b"))

  # 可视化
  p1 <- interaction_plot(res_log$model, x1 = "a", x2 = "b",
                          x1_label = "Exposure A", x2_label = "Exposure B",
                          y_label = "Predicted Probability")
  ggsave("interaction_logistic.png", p1, width = 8, height = 6, dpi = 300)

  # sjPlot 导出
  interaction_plot_sjplot(res_log$model, "a", "b",
                           output_file = "interaction_model.doc")

  # 汇总表
  tbl <- interaction_summary_table(res_log, x1_label = "a", x2_label = "b")
  print(tbl)

  # ------ 示例 2: Cox 交互 ------
  library(survival)
  df$time <- rexp(n, rate = 0.02)
  df$event <- rbinom(n, 1, 0.8)

  res_cox <- interaction_cox(df, time = "time", event = "event",
                              x1 = "a", x2 = "b", covs = "sex")

  p2 <- interaction_plot(res_cox$model, x1 = "a", x2 = "b",
                          y_label = "Predicted Risk")
  ggsave("interaction_cox.png", p2, width = 8, height = 6, dpi = 300)

  cat("✅ 交互作用模板示例完成\n")
}

cat("✅ interaction_template.R 已加载\n")
cat("可用函数:\n")
cat("  interaction_logistic()       - Logistic 交互 (相乘+相加)\n")
cat("  interaction_cox()            - Cox 交互 (相乘+相加)\n")
cat("  interactionR_analysis()      - interactionR 包 (Delta+Bootstrap)\n")
cat("  interaction_plot()           - 交互效应预测值图 (ggplot2)\n")
cat("  interaction_plot_visreg()    - visreg 偏效应图\n")
cat("  interaction_plot_sjplot()    - sjPlot 交互图 + Word导出\n")
cat("  interaction_summary_table()  - 交互作用汇总表\n")
