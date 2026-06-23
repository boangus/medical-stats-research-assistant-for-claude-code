# mediation_template.R — 中介效应分析模板
# ==========================================
# 适用于：探索 X → M → Y 的中介路径（暴露→中介→结局）
# 核心方法：BK两步法（Baron & Kenny + Bootstrap）
#
# 覆盖场景：
#   1. 线性-线性中介 (lm-lm)
#   2. GLM中介 (M连续/Y二分类)
#   3. Cox生存分析中介 (手动权重法 + mets包)
#   4. 批量中介分析 (多个中介变量)
#   5. 敏感性分析 (medsens)
#
# 依赖: mediation, survival, ggplot2 (必选); mets, geepack (可选)
# 安装: install.packages(c("mediation", "survival", "ggplot2", "mets"))
#
# 参考: 实战医学统计课程 Ch13, mediation包, mets包
# 作者: MSRA Team
# 版本: 0.1.0

library(mediation)
library(ggplot2)

# ============================================================================
# 1. 线性-线性中介 (X连续/分类, M连续, Y连续)
# ============================================================================

#' 线性中介效应分析 (BK两步法 + Bootstrap)
#'
#' @param data 数据框
#' @param x 暴露变量名（字符串）
#' @param m 中介变量名（字符串）
#' @param y 结局变量名（字符串）
#' @param covs 协变量名向量（可选）
#' @param sims Bootstrap 重抽样次数（默认 1000）
#' @param seed 随机种子
#'
#' @return list(result = mediate对象, model_m = 中介模型, model_y = 结局模型,
#'              summary_df = 结果汇总表)
mediate_linear <- function(data, x, m, y, covs = NULL,
                            sims = 1000, seed = 2024) {
  set.seed(seed)

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  # 路径 a: M ~ X + covs
  formula_m <- as.formula(paste0(m, " ~ ", x, covs_str))
  model_m <- lm(formula_m, data = data)

  # 路径 b + c': Y ~ X + M + covs
  formula_y <- as.formula(paste0(y, " ~ ", x, " + ", m, covs_str))
  model_y <- lm(formula_y, data = data)

  # 中介效应分析
  med_result <- mediate(model_m, model_y,
                        treat = x, mediator = m,
                        boot = TRUE, sims = sims)

  # 提取结果
  med_sum <- summary(med_result)

  result_df <- data.frame(
    Effect = c("ACME (Indirect)", "ADE (Direct)", "Total Effect", "Prop Mediated"),
    Estimate = c(med_result$d0, med_result$z0,
                 med_result$d0 + med_result$z0,
                 med_result$d0 / (med_result$d0 + med_result$z0)),
    CI_lower = c(med_result$d0.ci[1], med_result$z0.ci[1], NA, NA),
    CI_upper = c(med_result$d0.ci[2], med_result$z0.ci[2], NA, NA),
    P_value = c(med_result$d0.p, med_result$z0.p, NA, NA)
  )

  cat("\n📊 中介效应分析结果 (线性-线性):\n")
  cat(sprintf("   ACME (间接效应 a×b): %.4f (95%% CI: %.4f ~ %.4f), P = %s\n",
              result_df$Estimate[1], result_df$CI_lower[1], result_df$CI_upper[1],
              format.pval(result_df$P_value[1], digits = 3)))
  cat(sprintf("   ADE (直接效应 c'):   %.4f, P = %s\n",
              result_df$Estimate[2], format.pval(result_df$P_value[2], digits = 3)))
  cat(sprintf("   总效应:              %.4f\n", result_df$Estimate[3]))
  cat(sprintf("   中介比例:            %.1f%%\n", result_df$Estimate[4] * 100))

  return(list(
    result = med_result,
    model_m = model_m,
    model_y = model_y,
    summary_df = result_df
  ))
}


# ============================================================================
# 2. GLM 中介 (M连续, Y二分类)
# ============================================================================

#' GLM中介效应分析 (M连续用lm, Y二分类用glm probit)
#'
#' @param data 数据框
#' @param x 暴露变量名
#' @param m 中介变量名 (连续)
#' @param y 结局变量名 (二分类 0/1)
#' @param covs 协变量名向量
#' @param y_family Y的分布族 (默认 binomial("probit"))
#' @param sims Bootstrap次数
#' @param seed 随机种子
#'
#' @return list(result = mediate对象, model_m, model_y, summary_df)
mediate_glm <- function(data, x, m, y, covs = NULL,
                         y_family = binomial("probit"),
                         sims = 1000, seed = 2024) {
  set.seed(seed)

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  # 路径 a: M ~ X + covs (线性)
  formula_m <- as.formula(paste0(m, " ~ ", x, covs_str))
  model_m <- lm(formula_m, data = data)

  # 路径 b + c': Y ~ X + M + covs (GLM)
  formula_y <- as.formula(paste0(y, " ~ ", x, " + ", m, covs_str))
  model_y <- glm(formula_y, data = data, family = y_family,
                  control = glm.control(maxit = 100))

  # 中介效应分析
  med_result <- mediate(model_m, model_y,
                        treat = x, mediator = m,
                        robustSE = TRUE, sims = sims)

  result_df <- data.frame(
    Effect = c("ACME (Indirect)", "ADE (Direct)", "Total Effect", "Prop Mediated"),
    Estimate = c(med_result$d0, med_result$z0,
                 med_result$d0 + med_result$z0,
                 med_result$d0 / (med_result$d0 + med_result$z0)),
    P_value = c(med_result$d0.p, med_result$z0.p, NA, NA)
  )

  cat("\n📊 GLM中介效应分析结果:\n")
  cat(sprintf("   ACME: %.4f, P = %s\n",
              result_df$Estimate[1], format.pval(result_df$P_value[1], digits = 3)))
  cat(sprintf("   ADE:  %.4f, P = %s\n",
              result_df$Estimate[2], format.pval(result_df$P_value[2], digits = 3)))
  cat(sprintf("   中介比例: %.1f%%\n", result_df$Estimate[4] * 100))

  return(list(
    result = med_result,
    model_m = model_m,
    model_y = model_y,
    summary_df = result_df
  ))
}


# ============================================================================
# 3. Cox 生存分析中介 (手动权重法)
# ============================================================================

#' Cox中介效应分析 (手动4步权重法)
#'
#' 适用于 X(二分类) → M(二分类) → Y(生存) 的中介分析。
#' 通过构建中介权重实现效应分解。
#'
#' @param data 数据框
#' @param x 暴露变量名 (二分类 0/1)
#' @param m 中介变量名 (二分类 0/1)
#' @param time 生存时间变量名
#' @param event 事件变量名 (0/1)
#' @param covs 协变量名向量
#' @param id 个体ID变量名 (用于聚类标准误)
#' @param n_boot Bootstrap次数 (默认 1000)
#' @param seed 随机种子
#'
#' @return list(TE=总效应, DE=直接效应, IE=间接效应, PM=中介比例, boot_ci=Bootstrap CI)
mediate_cox <- function(data, x, m, time, event, covs = NULL,
                         id = NULL, n_boot = 1000, seed = 2024) {
  set.seed(seed)
  library(survival)

  # 内部函数: 单次中介权重计算
  compute_mediation_weights <- function(data, x, m, covs) {
    # 步骤1: 路径a - 预测中介变量
    formula_a <- as.formula(paste0(m, " ~ ", x,
                                    if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""))
    model_a <- glm(formula_a, data = data, family = binomial())

    # 步骤2: 构建反事实数据集
    d1 <- d2 <- data
    d1[[paste0("M_", m)]] <- d1[[m]]       # 原始中介值
    d2[[paste0("M_", m)]] <- 1 - d2[[m]]   # 反事实中介值

    # 步骤3: 计算权重
    # 直接效应权重
    w_direct <- predict(model_a, newdata = d1, type = "response")
    w_direct <- ifelse(d1[[m]] == 1, w_direct, 1 - w_direct)

    # 间接效应权重
    w_indirect <- predict(model_a, newdata = d2, type = "response")
    w_indirect <- ifelse(d2[[m]] == 1, w_indirect, 1 - w_indirect)

    weights <- w_indirect / w_direct
    return(weights)
  }

  # 计算总效应 (TE)
  formula_te <- as.formula(paste0("Surv(", time, ", ", event, ") ~ ", x,
                                   if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""))
  if (!is.null(id)) {
    formula_te <- update.formula(formula_te,
                                  paste0(". ~ . + cluster(", id, ")"))
  }
  cox_te <- coxph(formula_te, data = data)

  # 计算加权效应 (DE)
  weights <- compute_mediation_weights(data, x, m, covs)
  data$med_weight <- weights

  formula_de <- as.formula(paste0("Surv(", time, ", ", event, ") ~ ", x,
                                   " + ", m,
                                   if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""))
  if (!is.null(id)) {
    formula_de <- update.formula(formula_de,
                                  paste0(". ~ . + cluster(", id, ")"))
  }
  cox_de <- coxph(formula_de, data = data, weights = med_weight)

  # 提取效应
  coef_x <- coef(cox_te)[x]
  coef_x_de <- coef(cox_de)[x]
  coef_m_de <- coef(cox_de)[m]

  TE <- exp(coef_x)        # 总效应 HR
  DE <- exp(coef_x_de)     # 直接效应 HR
  IE <- exp(coef_m_de)     # 间接效应 HR
  PM <- log(IE) / log(TE)  # 中介比例

  cat("\n📊 Cox中介效应分析结果 (手动权重法):\n")
  cat(sprintf("   总效应 (TE): HR = %.4f\n", TE))
  cat(sprintf("   直接效应 (DE): HR = %.4f\n", DE))
  cat(sprintf("   间接效应 (IE): HR = %.4f\n", IE))
  cat(sprintf("   中介比例 (PM): %.1f%%\n", PM * 100))

  # Bootstrap CI
  boot_results <- replicate(n_boot, {
    boot_idx <- sample(nrow(data), replace = TRUE)
    boot_data <- data[boot_idx, ]

    tryCatch({
      boot_weights <- compute_mediation_weights(boot_data, x, m, covs)
      boot_data$med_weight <- boot_weights

      boot_cox_te <- coxph(formula_te, data = boot_data)
      boot_cox_de <- coxph(formula_de, data = boot_data, weights = med_weight)

      boot_TE <- exp(coef(boot_cox_te)[x])
      boot_DE <- exp(coef(boot_cox_de)[x])
      boot_IE <- exp(coef(boot_cox_de)[m])
      boot_PM <- log(boot_IE) / log(boot_TE)

      c(TE = boot_TE, DE = boot_DE, IE = boot_IE, PM = boot_PM)
    }, error = function(e) rep(NA, 4))
  })

  boot_ci <- apply(boot_results, 1, function(x) {
    quantile(x, probs = c(0.025, 0.975), na.rm = TRUE)
  })

  cat("\n   Bootstrap 95% CI:\n")
  cat(sprintf("     TE: %.4f ~ %.4f\n", boot_ci[1, "TE"], boot_ci[2, "TE"]))
  cat(sprintf("     DE: %.4f ~ %.4f\n", boot_ci[1, "DE"], boot_ci[2, "DE"]))
  cat(sprintf("     IE: %.4f ~ %.4f\n", boot_ci[1, "IE"], boot_ci[2, "IE"]))
  cat(sprintf("     PM: %.1f%% ~ %.1f%%\n", boot_ci[1, "PM"] * 100, boot_ci[2, "PM"] * 100))

  return(list(
    TE = TE, DE = DE, IE = IE, PM = PM,
    boot_ci = boot_ci,
    cox_te = cox_te, cox_de = cox_de
  ))
}


# ============================================================================
# 4. Cox 生存分析中介 (mets包一键法)
# ============================================================================

#' Cox中介效应分析 (mets包 medweight + phreg)
#'
#' 使用 mets 包的 medweight 函数自动生成中介权重，
#' 配合 phreg 进行生存分析。适用于 X(二分类) → M → Y(生存)。
#'
#' @param data 数据框 (需包含 id 列)
#' @param x 暴露变量名 (二分类)
#' @param m 中介变量名
#' @param time 生存时间变量名
#' @param event 事件变量名
#' @param covs 协变量名向量
#' @param cause 事件类型 (竞争风险时指定)
#'
#' @return list(weight_model, weighted_data, phreg_result, mediation_result)
mediate_cox_mets <- function(data, x, m, time, event, covs = NULL,
                              cause = NULL) {
  library(mets)

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  # 步骤1: 中介权重模型
  formula_w <- as.formula(paste0(m, " ~ ", x, covs_str))
  weight_model <- glm(formula_w, data = data, family = binomial)

  # 步骤2: 生成中介权重
  wdata <- medweight(weight_model, data = data)

  # 步骤3: 加权生存分析
  if (!is.null(cause)) {
    # 竞争风险
    formula_cif <- as.formula(paste0("Event(", time, ", ", event, ") ~ ",
                                      x, "0 + ", x, "1",
                                      if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else "",
                                      " + cluster(id)"))
    fit <- cifreg(formula_cif, data = wdata,
                  weights = wdata$weights, propodds = NULL, cause = cause)
  } else {
    # 标准 Cox
    formula_phreg <- as.formula(paste0("Surv(", time, ", ", event, "==1) ~ ",
                                        x, "0 + ", x, "1",
                                        if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else "",
                                        " + cluster(id)"))
    fit <- phreg(formula_phreg, data = wdata, weights = wdata$weights)
  }

  # 步骤4: 中介效应分解
  med_result <- mediatorSurv(fit, weight_model, data = data, wdata = wdata)

  cat("\n📊 Cox中介效应分析结果 (mets包):\n")
  print(summary(med_result))

  return(list(
    weight_model = weight_model,
    weighted_data = wdata,
    phreg_result = fit,
    mediation_result = med_result
  ))
}


# ============================================================================
# 5. 批量中介分析
# ============================================================================

#' 批量中介效应分析 (多个中介变量)
#'
#' 对多个中介变量逐一进行中介效应分析，返回汇总表。
#' 适用于探索性分析阶段筛选有意义的中介变量。
#'
#' @param data 数据框
#' @param x 暴露变量名
#' @param y 结局变量名
#' @param m_vars 中介变量名向量
#' @param covs 协变量名向量
#' @param y_type 结局类型: "continuous" 或 "binary"
#' @param sims Bootstrap次数
#' @param seed 随机种子
#'
#' @return data.frame (每行一个中介变量的结果)
mediate_batch <- function(data, x, y, m_vars, covs = NULL,
                           y_type = "continuous", sims = 500, seed = 2024) {
  set.seed(seed)

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""

  results <- do.call(rbind, lapply(m_vars, function(m) {
    tryCatch({
      # 路径 a
      formula_m <- as.formula(paste0(m, " ~ ", x, covs_str))
      model_m <- lm(formula_m, data = data)

      # 路径 b + c'
      formula_y <- as.formula(paste0(y, " ~ ", x, " + ", m, covs_str))
      if (y_type == "binary") {
        model_y <- glm(formula_y, data = data, family = binomial("probit"),
                        control = glm.control(maxit = 100))
      } else {
        model_y <- lm(formula_y, data = data)
      }

      # 中介分析
      med <- mediate(model_m, model_y, treat = x, mediator = m,
                     boot = TRUE, sims = sims)

      data.frame(
        Mediator = m,
        ACME = med$d0,
        ACME_lower = med$d0.ci[1],
        ACME_upper = med$d0.ci[2],
        ACME_P = med$d0.p,
        ADE = med$z0,
        ADE_P = med$z0.p,
        Total = med$d0 + med$z0,
        Prop_Mediated = round(med$d0 / (med$d0 + med$z0) * 100, 1),
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      data.frame(Mediator = m, ACME = NA, ACME_lower = NA, ACME_upper = NA,
                 ACME_P = NA, ADE = NA, ADE_P = NA, Total = NA,
                 Prop_Mediated = NA, stringsAsFactors = FALSE)
    })
  }))

  # 排序
  results <- results[order(results$ACME_P), ]

  cat("\n📊 批量中介分析结果:\n")
  cat(sprintf("   共 %d 个中介变量，%d 个有效结果\n",
              length(m_vars), sum(!is.na(results$ACME))))
  cat("   按 ACME P 值排序:\n")
  print(results, row.names = FALSE)

  return(results)
}


# ============================================================================
# 6. 中介效应可视化
# ============================================================================

#' 绘制中介效应路径图
#'
#' @param med_result mediate() 返回的对象
#' @param x_label 暴露变量标签
#' @param m_label 中介变量标签
#' @param y_label 结局变量标签
#'
#' @return ggplot 对象
mediate_plot <- function(med_result, x_label = "X", m_label = "M",
                          y_label = "Y") {
  # 提取系数
  acme <- med_result$d0
  ade <- med_result$z0
  acme_p <- med_result$d0.p
  ade_p <- med_result$z0.p

  # 构建路径数据
  path_df <- data.frame(
    x = c(0, 2, 2),
    y = c(2, 2, 0),
    xend = c(2, 2, 4),
    yend = c(2, 0, 0),
    label = c(
      sprintf("a×b = %.3f\n(P = %s)", acme, format.pval(acme_p, digits = 3)),
      sprintf("c' = %.3f\n(P = %s)", ade, format.pval(ade_p, digits = 3)),
      "b"
    ),
    hjust = c(0.5, 0.5, 0.5),
    vjust = c(-0.5, 1.5, -0.5)
  )

  node_df <- data.frame(
    x = c(0, 2, 4),
    y = c(2, 2, 0),
    label = c(x_label, m_label, y_label)
  )

  p <- ggplot() +
    # 箭头 (路径)
    geom_segment(data = path_df,
                 aes(x = x, y = y, xend = xend, yend = yend),
                 arrow = arrow(length = unit(0.3, "cm"), type = "closed"),
                 linewidth = 1, color = "#2E86C1") +
    # 路径标签
    geom_text(data = path_df,
              aes(x = (x + xend) / 2, y = (y + yend) / 2,
                  label = label, hjust = hjust, vjust = vjust),
              size = 4, color = "#E74C3C", fontface = "bold") +
    # 节点
    geom_point(data = node_df, aes(x = x, y = y),
               size = 15, color = "#2E86C1", alpha = 0.1) +
    geom_point(data = node_df, aes(x = x, y = y),
               size = 15, shape = 1, color = "#2E86C1", linewidth = 1.5) +
    geom_text(data = node_df, aes(x = x, y = y, label = label),
              size = 5, fontface = "bold") +
    # 主题
    theme_void(base_size = 14) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5, size = 14),
      plot.subtitle = element_text(hjust = 0.5, color = "grey40", size = 11)
    ) +
    labs(
      title = "Mediation Analysis Path Diagram",
      subtitle = sprintf("ACME (Indirect): %.3f | ADE (Direct): %.3f | Mediated: %.1f%%",
                          acme, ade, abs(acme / (acme + ade)) * 100)
    ) +
    coord_cartesian(xlim = c(-0.5, 4.5), ylim = c(-0.5, 3))

  return(p)
}


#' 绘制批量中介分析森林图
#'
#' @param batch_result mediate_batch() 返回的 data.frame
#' @param title 标题
#'
#' @return ggplot 对象
mediate_batch_forest <- function(batch_result, title = "Batch Mediation Analysis") {
  df <- batch_result[!is.na(batch_result$ACME), ]

  if (nrow(df) == 0) {
    warning("No valid mediation results to plot")
    return(NULL)
  }

  df$sig <- ifelse(df$ACME_P < 0.05, "Significant", "Non-significant")

  p <- ggplot(df, aes(x = reorder(Mediator, ACME), y = ACME)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
    geom_errorbar(aes(ymin = ACME_lower, ymax = ACME_upper, color = sig),
                  width = 0.2, linewidth = 0.8) +
    geom_point(aes(color = sig), size = 3) +
    scale_color_manual(values = c("Significant" = "#E74C3C",
                                   "Non-significant" = "grey50")) +
    coord_flip() +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = "bottom",
      panel.grid.major.y = element_line(color = "grey90")
    ) +
    labs(
      title = title,
      x = "Mediator",
      y = "ACME (Indirect Effect, 95% CI)",
      color = ""
    )

  return(p)
}


# ============================================================================
# 7. 敏感性分析
# ============================================================================

#' 中介效应敏感性分析
#'
#' 评估中介效应对未测混杂变量的稳健性。
#' rho 表示中介变量与结局变量之间未测混杂的相关性。
#'
#' @param med_result mediate() 返回的对象
#' @param rho_by rho 步长 (默认 0.1)
#' @param eps eps 步长 (默认 0.01)
#'
#' @return medsens 对象
mediate_sensitivity <- function(med_result, rho_by = 0.1, eps = 0.01) {
  sens <- medsens(med_result, rho.by = rho_by, eps = eps, effect.type = "both")

  cat("\n📊 中介效应敏感性分析:\n")
  cat("   Rho = 0 表示无混杂效应\n")
  cat("   Rho 值越大表示混杂效应越强，中介效应越可靠\n")
  print(summary(sens))

  return(sens)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # ------ 示例 1: 线性-线性中介 ------
  library(mediation)
  data(jobs)

  # 压力 → 求职行为 → 抑郁
  res_linear <- mediate_linear(
    data = jobs,
    x = "treat", m = "job_seek", y = "depress2",
    covs = c("econ_hard", "sex", "age"),
    sims = 500
  )

  # 路径图
  p1 <- mediate_plot(res_linear$result,
                      x_label = "Treatment", m_label = "Job Seeking",
                      y_label = "Depression")
  ggsave("mediation_path.png", p1, width = 8, height = 6, dpi = 300)

  # 敏感性分析
  sens <- mediate_sensitivity(res_linear$result)

  # ------ 示例 2: GLM中介 (Y二分类) ------
  # 假设 data 有 treat(暴露), emo(中介,连续), cong_mesg(结局,0/1)
  # res_glm <- mediate_glm(data = bc, x = "treat", m = "emo",
  #                         y = "cong_mesg", covs = c("age","educ","gender"))

  # ------ 示例 3: Cox中介 (手动法) ------
  # data$vf: 暴露(0/1), data$wmi: 中介(0/1), data$time/data$status: 生存
  # res_cox <- mediate_cox(data = bc, x = "vf", m = "wmi",
  #                         time = "time", event = "status",
  #                         covs = c("age","sex"), id = "id")

  # ------ 示例 4: Cox中介 (mets包) ------
  # res_mets <- mediate_cox_mets(data = bc, x = "vf", m = "wmi",
  #                               time = "time", event = "status",
  #                               covs = c("age","sex"))

  # ------ 示例 5: 批量中介 ------
  # res_batch <- mediate_batch(data = data, x = "age", y = "status",
  #                             m_vars = c("gender","ethnicity","height","sapsii","sofa"),
  #                             y_type = "binary", sims = 200)
  # p_batch <- mediate_batch_forest(res_batch)
  # ggsave("mediation_batch.png", p_batch, width = 8, height = 6, dpi = 300)

  cat("✅ 中介效应模板示例完成\n")
}

cat("✅ mediation_template.R 已加载\n")
cat("可用函数:\n")
cat("  mediate_linear()         - 线性-线性中介 (lm-lm)\n")
cat("  mediate_glm()            - GLM中介 (M连续/Y二分类)\n")
cat("  mediate_cox()            - Cox中介 (手动权重法)\n")
cat("  mediate_cox_mets()       - Cox中介 (mets包一键法)\n")
cat("  mediate_batch()          - 批量中介分析\n")
cat("  mediate_plot()           - 中介路径图\n")
cat("  mediate_batch_forest()   - 批量中介森林图\n")
cat("  mediate_sensitivity()    - 敏感性分析\n")
