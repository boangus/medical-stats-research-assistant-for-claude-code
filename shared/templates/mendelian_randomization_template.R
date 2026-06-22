# 孟德尔随机化 (Mendelian Randomization) 模板
# =============================================================
# 核心方法: IVW, MR-Egger, 加权中位数, 加权众数, 敏感性分析
# 适用场景: 利用遗传变异作为工具变量, 推断暴露与结局的因果关系
#
# 依赖:
#   install.packages(c("MendelianRandomization", "ggplot2", "dplyr"))
#   remotes::install_github("MRCIEU/TwoSampleMR")  # 需要 GitHub 安装
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("MendelianRandomization", "ggplot2", "dplyr")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
if (!requireNamespace("TwoSampleMR", quietly = TRUE)) {
  message("请安装 TwoSampleMR: remotes::install_github('MRCIEU/TwoSampleMR')")
}
library(MendelianRandomization); library(ggplot2); library(dplyr)
tryCatch(library(TwoSampleMR), error = function(e) message("TwoSampleMR 未安装, 部分功能不可用"))


# ==============================================================================
# 1. 准备与协调 GWAS 汇总数据
# ==============================================================================

#' 准备并协调暴露与结局的 GWAS 汇总数据
#'
#' @param exposure_data 数据框, 暴露 GWAS 汇总数据
#'   需包含列: SNP, beta.exposure, se.exposure, effect_allele.exposure, other_allele.exposure
#' @param outcome_data 数据框, 结局 GWAS 汇总数据
#'   需包含列: SNP, beta.outcome, se.outcome, effect_allele.outcome, other_allele.outcome
#' @param clump_r2 数值, LD 聚类 r2 阈值 (默认 0.001)
#' @param clump_kb 数值, LD 聚类窗口 kb (默认 10000)
#' @return list: harmonized (协调后数据), exposure_dat (格式化暴露), outcome_dat (格式化结局)
#' @examples
#' dat <- mr_prepare_data(exposure_gwas, outcome_gwas)
mr_prepare_data <- function(exposure_data, outcome_data,
                            clump_r2 = 0.001, clump_kb = 10000) {

  message("[MR] 开始数据准备与协调...")

  # --- 使用 TwoSampleMR 格式化 (如可用) ---
  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {

    # 格式化暴露数据
    if (!"exposure" %in% names(exposure_data)) exposure_data$exposure <- "exposure"
    exposure_dat <- TwoSampleMR::format_data(
      exposure_data,
      type = "exposure",
      snp_col      = "SNP",
      beta_col     = "beta.exposure",
      se_col       = "se.exposure",
      eaf_col      = if ("eaf.exposure" %in% names(exposure_data)) "eaf.exposure" else NULL,
      effect_col   = "effect_allele.exposure",
      other_col    = "other_allele.exposure",
      pval_col     = if ("pval.exposure" %in% names(exposure_data)) "pval.exposure" else NULL
    )

    # LD 聚类 (去连锁不平衡)
    exposure_dat <- TwoSampleMR::clump_data(exposure_dat,
                                             clump_r2 = clump_r2, clump_kb = clump_kb)
    message("  暴露 IV 数量 (聚类后): ", nrow(exposure_dat))

    # 格式化结局数据
    if (!"outcome" %in% names(outcome_data)) outcome_data$outcome <- "outcome"
    outcome_dat <- TwoSampleMR::format_data(
      outcome_data,
      type = "outcome",
      snp_col      = "SNP",
      beta_col     = "beta.outcome",
      se_col       = "se.outcome",
      eaf_col      = if ("eaf.outcome" %in% names(outcome_data)) "eaf.outcome" else NULL,
      effect_col   = "effect_allele.outcome",
      other_col    = "other_allele.outcome",
      pval_col     = if ("pval.outcome" %in% names(outcome_data)) "pval.outcome" else NULL
    )

    # 协调: 对齐等位基因方向, 去除回文 SNP
    harmonized <- TwoSampleMR::harmonise_data(exposure_dat, outcome_dat)
    harmonized <- harmonized[harmonized$mr_keep == TRUE, ]
    message("  协调后有效 IV 数量: ", nrow(harmonized))

    return(list(
      harmonized   = harmonized,
      exposure_dat = exposure_dat,
      outcome_dat  = outcome_dat
    ))
  }

  # --- 后备: 纯手动协调 (无 TwoSampleMR) ---
  message("  [后备] 使用手动协调 (TwoSampleMR 不可用)")
  merged <- merge(exposure_data, outcome_data, by = "SNP", suffixes = c(".exp", ".out"))
  merged <- merged[!is.na(merged$beta.exposure) & !is.na(merged$beta.outcome), ]

  # 对齐方向: 若等位基因不一致, 取反
  flip_idx <- which(merged$effect_allele.exposure != merged$effect_allele.outcome)
  if (length(flip_idx) > 0) {
    merged$beta.outcome[flip_idx] <- -merged$beta.outcome[flip_idx]
    message("  翻转 ", length(flip_idx), " 个不一致等位基因方向")
  }

  return(list(harmonized = merged, exposure_dat = NULL, outcome_dat = NULL))
}


# ==============================================================================
# 2. 逆方差加权法 (IVW)
# ==============================================================================

#' 逆方差加权法 (IVW)
#'
#' @param harmonized 数据框, 协调后的 MR 数据
#' @return MR 结果列表: beta, se, pval, or (OR 及 CI)
#' @examples
#' ivw_res <- mr_ivw(harmonized)
mr_ivw <- function(harmonized) {

  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {
    res <- TwoSampleMR::mr(harmonized, method_list = "mr_ivw")
    beta <- res$b; se <- res$se; pval <- res$pval
  } else {
    # 手动 IVW: beta_Y ~ beta_X, 加权 by 1/se_Y^2
    bx <- harmonized$beta.exposure
    by <- harmonized$beta.outcome
    se_y <- harmonized$se.outcome

    w <- 1 / se_y^2
    fit <- lm(by ~ bx - 1, weights = w)
    beta <- coef(fit)
    se   <- sqrt(1 / sum(w * bx^2))
    pval <- 2 * pnorm(-abs(beta / se))
  }

  or_val <- exp(beta)
  ci_low <- exp(beta - 1.96 * se)
  ci_high <- exp(beta + 1.96 * se)

  message("[MR] IVW 估计: beta = ", round(beta, 4),
          " | OR = ", round(or_val, 3),
          " (95% CI: ", round(ci_low, 3), "-", round(ci_high, 3), ")",
          " | p = ", formatC(pval, format = "e", digits = 2))

  return(list(method = "IVW", beta = beta, se = se, pval = pval,
              or = or_val, ci_low = ci_low, ci_high = ci_high))
}


# ==============================================================================
# 3. MR-Egger 回归 (多效性检验)
# ==============================================================================

#' MR-Egger 回归
#'
#' @param harmonized 数据框, 协调后的 MR 数据
#' @return list: beta, se, pval, intercept (截距 = 多效性指标), pleiotropy_p
#' @examples
#' egger_res <- mr_egger(harmonized)
mr_egger <- function(harmonized) {

  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {
    res <- TwoSampleMR::mr(harmonized, method_list = "mr_egger_regression")
    beta <- res$b; se <- res$se; pval <- res$pval

    # 获取截距 (多效性检验)
    egger_int <- TwoSampleMR::mr_pleiotropy_test(harmonized)
    intercept    <- egger_int$egger_intercept
    pleiotropy_p <- egger_int$pval
  } else {
    bx <- harmonized$beta.exposure
    by <- harmonized$beta.outcome
    se_y <- harmonized$se.outcome
    w <- 1 / se_y^2

    # Egger 回归: 加权截距 + 斜率
    fit <- lm(by ~ bx, weights = w)
    beta <- coef(fit)[2]
    intercept <- coef(fit)[1]
    se <- summary(fit)$coefficients[2, 2]
    pval <- 2 * pnorm(-abs(beta / se))
    pleiotropy_p <- 2 * pnorm(-abs(intercept / summary(fit)$coefficients[1, 2]))
  }

  or_val <- exp(beta)
  ci_low <- exp(beta - 1.96 * se)
  ci_high <- exp(beta + 1.96 * se)

  message("[MR] MR-Egger: beta = ", round(beta, 4),
          " | OR = ", round(or_val, 3),
          " (95% CI: ", round(ci_low, 3), "-", round(ci_high, 3), ")")
  message("  截距 (多效性): ", round(intercept, 4),
          " | 多效性检验 p = ", formatC(pleiotropy_p, format = "e", digits = 2))

  return(list(method = "MR-Egger", beta = beta, se = se, pval = pval,
              or = or_val, ci_low = ci_low, ci_high = ci_high,
              intercept = intercept, pleiotropy_p = pleiotropy_p))
}


# ==============================================================================
# 4. 加权中位数估计量
# ==============================================================================

#' 加权中位数估计量 (Weighted Median)
#'
#' @param harmonized 数据框, 协调后的 MR 数据
#' @return list: beta, se, pval, or (OR 及 CI)
#' @examples
#' wm_res <- mr_weighted_median(harmonized)
mr_weighted_median <- function(harmonized) {

  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {
    res <- TwoSampleMR::mr(harmonized, method_list = "mr_weighted_median")
    beta <- res$b; se <- res$se; pval <- res$pval
  } else {
    bx <- harmonized$beta.exposure
    by <- harmonized$beta.outcome
    se_y <- harmonized$se.outcome
    se_x <- harmonized$se.exposure

    # Wald ratio for each IV
    ratios <- by / bx
    weights <- bx^2 / se_y^2

    # 加权中位数
    ord <- order(ratios)
    cumw <- cumsum(weights[ord]) / sum(weights)
    median_idx <- which(cumw >= 0.5)[1]
    beta <- ratios[ord][median_idx]

    # Bootstrap SE
    boot_beta <- replicate(500, {
      idx <- sample(length(ratios), replace = TRUE)
      r <- ratios[idx]; w <- weights[idx]
      o <- order(r); cw <- cumsum(w[o]) / sum(w)
      r[o][which(cw >= 0.5)[1]]
    })
    se <- sd(boot_beta, na.rm = TRUE)
    pval <- 2 * pnorm(-abs(beta / se))
  }

  or_val <- exp(beta)
  ci_low <- exp(beta - 1.96 * se)
  ci_high <- exp(beta + 1.96 * se)

  message("[MR] 加权中位数: beta = ", round(beta, 4),
          " | OR = ", round(or_val, 3),
          " (95% CI: ", round(ci_low, 3), "-", round(ci_high, 3), ")")

  return(list(method = "Weighted Median", beta = beta, se = se, pval = pval,
              or = or_val, ci_low = ci_low, ci_high = ci_high))
}


# ==============================================================================
# 5. 加权众数估计量
# ==============================================================================

#' 加权众数估计量 (Weighted Mode)
#'
#' @param harmonized 数据框, 协调后的 MR 数据
#' @return list: beta, se, pval, or (OR 及 CI)
#' @examples
#' mode_res <- mr_mode(harmonized)
mr_mode <- function(harmonized) {

  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {
    res <- TwoSampleMR::mr(harmonized, method_list = "mr_simple_mode")
    beta <- res$b; se <- res$se; pval <- res$pval
  } else {
    bx <- harmonized$beta.exposure
    by <- harmonized$beta.outcome
    se_y <- harmonized$se.outcome

    ratios <- by / bx
    weights <- bx^2 / se_y^2

    # 简单核密度众数估计
    d <- density(ratios, weights = weights / sum(weights), bw = "SJ")
    beta <- d$x[which.max(d$y)]

    # Bootstrap SE
    boot_beta <- replicate(500, {
      idx <- sample(length(ratios), replace = TRUE)
      r <- ratios[idx]; w <- weights[idx]
      dd <- density(r, weights = w / sum(w), bw = "SJ")
      dd$x[which.max(dd$y)]
    })
    se <- sd(boot_beta, na.rm = TRUE)
    pval <- 2 * pnorm(-abs(beta / se))
  }

  or_val <- exp(beta)
  ci_low <- exp(beta - 1.96 * se)
  ci_high <- exp(beta + 1.96 * se)

  message("[MR] 加权众数: beta = ", round(beta, 4),
          " | OR = ", round(or_val, 3),
          " (95% CI: ", round(ci_low, 3), "-", round(ci_high, 3), ")")

  return(list(method = "Weighted Mode", beta = beta, se = se, pval = pval,
              or = or_val, ci_low = ci_low, ci_high = ci_high))
}


# ==============================================================================
# 6. 敏感性分析
# ==============================================================================

#' MR 敏感性分析: 逐一剔除, Cochran Q 异质性, MR-PRESSO
#'
#' @param harmonized 数据框, 协调后的 MR 数据
#' @return list: loo (逐一剔除结果), heterogeneity (Q 检验), presso (全局检验)
#' @examples
#' sens <- mr_sensitivity(harmonized)
mr_sensitivity <- function(harmonized) {

  results <- list()

  # --- 6a. Leave-one-out 分析 ---
  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {
    loo <- TwoSampleMR::mr_leaveoneout(harmonized)
    results$loo <- loo
    message("[MR] LOO 分析: 完成 (", nrow(loo), " 轮)")
  } else {
    bx <- harmonized$beta.exposure
    by <- harmonized$beta.outcome
    se_y <- harmonized$se.outcome
    loo_betas <- sapply(seq_along(bx), function(i) {
      w <- 1 / se_y[-i]^2
      fit <- lm(by[-i] ~ bx[-i] - 1, weights = w)
      coef(fit)
    })
    results$loo <- data.frame(SNP = harmonized$SNP, beta = loo_betas)
    message("[MR] LOO 分析: 完成 (手动计算)")
  }

  # --- 6b. Cochran Q 异质性检验 ---
  bx <- harmonized$beta.exposure
  by <- harmonized$beta.outcome
  se_y <- harmonized$se.outcome
  w <- 1 / se_y^2
  beta_ivw <- sum(w * bx * by) / sum(w * bx^2)

  # 各 IV 的 Wald 比率残差
  residuals <- by - beta_ivw * bx
  Q <- sum(w * residuals^2)
  df <- length(bx) - 1
  Q_pval <- pchisq(Q, df, lower.tail = FALSE)
  I2 <- max(0, (Q - df) / Q * 100)

  results$heterogeneity <- list(Q = Q, df = df, pval = Q_pval, I2 = I2)
  message("[MR] Cochran Q 异质性: Q = ", round(Q, 2), " (df=", df, ")",
          " | p = ", formatC(Q_pval, format = "e", digits = 2),
          " | I2 = ", round(I2, 1), "%")

  # --- 6c. MR-PRESSO (全局检验) ---
  if (requireNamespace("TwoSampleMR", quietly = TRUE)) {
    tryCatch({
      presso_res <- TwoSampleMR::run_mr_presso(harmonized, NbDistribution = 1000)
      results$presso <- presso_res
      message("[MR] MR-PRESSO: 全局检验完成")
    }, error = function(e) {
      message("[MR] MR-PRESSO 不可用: ", e$message)
      results$presso <- NULL
    })
  } else {
    # 简化: 使用 Q 统计量的离群值近似
    outliers <- which(abs(residuals) > 2 * sd(residuals))
    results$presso <- list(
      global_test = Q,
      global_pval = Q_pval,
      outlier_idx = outliers,
      n_outliers  = length(outliers)
    )
    message("[MR] PRESSO 近似: 发现 ", length(outliers), " 个离群 IV")
  }

  return(results)
}


# ==============================================================================
# 7. 森林图
# ==============================================================================

#' 绘制 MR 各方法估计结果的森林图
#'
#' @param mr_results list of lists, 各 MR 方法的结果 (如 mr_ivw(), mr_egger() 的返回值)
#' @param title 字符, 图标题
#' @return ggplot 对象
#' @examples
#' mr_forest_plot(list(ivw_res, egger_res, wm_res, mode_res))
mr_forest_plot <- function(mr_results, title = "MR 各方法因果效应估计") {

  df <- do.call(rbind, lapply(mr_results, function(r) {
    data.frame(
      method = r$method,
      or     = r$or,
      ci_low = r$ci_low,
      ci_high = r$ci_high,
      pval   = r$pval,
      stringsAsFactors = FALSE
    )
  }))

  p <- ggplot(df, aes(x = .data$or, y = reorder(.data$method, -.data$or))) +
    geom_point(size = 4, color = "#2166AC") +
    geom_errorbarh(aes(xmin = .data$ci_low, xmax = .data$ci_high),
                   height = 0.2, color = "#2166AC") +
    geom_vline(xintercept = 1, linetype = "dashed", color = "red", linewidth = 0.8) +
    scale_x_log10() +
    labs(title = title, x = "OR (95% CI)", y = NULL,
         subtitle = paste0("p 值: ", paste(
           sprintf("%s=%.1e", df$method, df$pval), collapse = " | "))) +
    theme_minimal(base_size = 12) +
    theme(panel.grid.minor = element_blank())

  print(p)
  return(p)
}


# ==============================================================================
# 8. 散点图
# ==============================================================================

#' 绘制 MR 散点图 (暴露效应 vs 结局效应, 含回归线)
#'
#' @param harmonized 数据框, 协调后的 MR 数据
#' @param mr_results list of lists, 各 MR 方法结果
#' @return ggplot 对象
#' @examples
#' mr_scatter_plot(harmonized, list(ivw_res, egger_res))
mr_scatter_plot <- function(harmonized, mr_results = NULL) {

  bx <- harmonized$beta.exposure
  by <- harmonized$beta.outcome
  se_x <- harmonized$se.exposure
  se_y <- harmonized$se.outcome

  df <- data.frame(x = bx, y = by, se_x = se_x, se_y = se_y)

  p <- ggplot(df, aes(x = .data$x, y = .data$y)) +
    geom_errorbar(aes(ymin = .data$y - 1.96 * .data$se_y,
                      ymax = .data$y + 1.96 * .data$se_y),
                  width = 0, alpha = 0.3, color = "grey50") +
    geom_errorbarh(aes(xmin = .data$x - 1.96 * .data$se_x,
                       xmax = .data$x + 1.96 * .data$se_x),
                   height = 0, alpha = 0.3, color = "grey50") +
    geom_point(size = 3, alpha = 0.7) +
    geom_hline(yintercept = 0, linetype = "dashed", alpha = 0.5) +
    geom_vline(xintercept = 0, linetype = "dashed", alpha = 0.5) +
    labs(title = "MR 散点图", x = "暴露效应 (beta)", y = "结局效应 (beta)") +
    theme_minimal(base_size = 12)

  # 添加各方法回归线
  if (!is.null(mr_results)) {
    colors <- c("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3")
    for (i in seq_along(mr_results)) {
      r <- mr_results[[i]]
      if (!is.null(r$intercept)) {
        p <- p + geom_abline(slope = r$beta, intercept = r$intercept,
                             color = colors[i], linewidth = 1, linetype = "dashed")
      }
      p <- p + geom_abline(slope = r$beta, intercept = ifelse(is.null(r$intercept), 0, r$intercept),
                           color = colors[i], linewidth = 1)
    }
    if (length(mr_results) > 0) {
      method_names <- sapply(mr_results, `[[`, "method")
      p <- p + scale_color_manual(values = setNames(colors[seq_along(method_names)], method_names))
    }
  }

  print(p)
  return(p)
}


# ==============================================================================
# 9. 端到端演示
# ==============================================================================

#' MR 完整工作流演示
#'
#' 使用模拟 GWAS 数据展示孟德尔随机化的完整流程。
#'
#' @return list, 含各步骤结果
#' @examples
#' demo <- full_mr_workflow()
full_mr_workflow <- function() {

  set.seed(2024)
  message("=" %>% rep(60) %>% paste(collapse = ""))
  message("孟德尔随机化 (MR) 完整工作流演示")
  message("=" %>% rep(60) %>% paste(collapse = ""))

  # --- 模拟 GWAS 汇总数据 ---
  n_iv <- 15
  exposure_gwas <- data.frame(
    SNP               = paste0("rs", 1000 + seq_len(n_iv)),
    beta.exposure     = rnorm(n_iv, 0.05, 0.02),
    se.exposure       = abs(rnorm(n_iv, 0.01, 0.005)),
    effect_allele.exposure = sample(c("A", "C", "G", "T"), n_iv, replace = TRUE),
    other_allele.exposure  = sample(c("A", "C", "G", "T"), n_iv, replace = TRUE),
    pval.exposure     = runif(n_iv, 1e-8, 5e-6),
    eaf.exposure      = runif(n_iv, 0.1, 0.9)
  )
  # 避免相同等位基因
  same_idx <- which(exposure_gwas$effect_allele.exposure == exposure_gwas$other_allele.exposure)
  if (length(same_idx) > 0) exposure_gwas$other_allele.exposure[same_idx] <- "T"

  # 结局 GWAS: 暴露有真实因果效应 (beta = 0.1)
  true_beta <- 0.1
  outcome_gwas <- data.frame(
    SNP               = exposure_gwas$SNP,
    beta.outcome      = true_beta * exposure_gwas$beta.exposure + rnorm(n_iv, 0, 0.005),
    se.outcome        = abs(rnorm(n_iv, 0.015, 0.005)),
    effect_allele.outcome = exposure_gwas$effect_allele.exposure,
    other_allele.outcome  = exposure_gwas$other_allele.exposure,
    pval.outcome      = runif(n_iv, 1e-8, 1e-2),
    eaf.outcome       = exposure_gwas$eaf.exposure
  )

  # Step 1: 数据准备
  dat <- mr_prepare_data(exposure_gwas, outcome_gwas)

  # Step 2: 各 MR 方法
  ivw_res   <- mr_ivw(dat$harmonized)
  egger_res <- mr_egger(dat$harmonized)
  wm_res    <- mr_weighted_median(dat$harmonized)
  mode_res  <- mr_mode(dat$harmonized)

  all_methods <- list(ivw_res, egger_res, wm_res, mode_res)

  # Step 3: 敏感性分析
  sens <- mr_sensitivity(dat$harmonized)

  # Step 4: 可视化
  forest_p  <- mr_forest_plot(all_methods)
  scatter_p <- mr_scatter_plot(dat$harmonized, all_methods)

  message("\n[MR] 完整工作流结束")
  message("  真实因果效应 beta = ", true_beta)
  message("  IVW 估计 = ", round(ivw_res$beta, 4))

  return(list(
    data         = dat,
    ivw          = ivw_res,
    egger        = egger_res,
    weighted_median = wm_res,
    mode         = mode_res,
    sensitivity  = sens,
    forest_plot  = forest_p,
    scatter_plot = scatter_p
  ))
}

# 运行演示:
# demo <- full_mr_workflow()
