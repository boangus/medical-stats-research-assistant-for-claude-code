# 贝叶斯自适应设计模板 (Bayesian Adaptive Design)
# =================================================
# 基于 rpact 包实现多种自适应临床试验设计
# 适用于：II/III 期临床试验的适应性设计与期中分析
#
# 支持的自适应方法:
#   - 群组序贯设计（Group Sequential Design）
#   - 样本量再估计（Sample Size Re-estimation）
#   - 人群富集设计（Adaptive Enrichment）
#   - 期中分析与 alpha 消耗（Interim Analysis）
#
# 参考:
#   - Wassmer & Brannath (2016) "Group Sequential and Confirmatory Adaptive Designs"
#   - rpact 官方文档: https://www.rpact.org
#
# 依赖:
#   install.packages("rpact")
#   install.packages("ggplot2")

suppressPackageStartupMessages({
  library(rpact)
  library(ggplot2)
})

# ==============================================================================
# 1. design_group_seq() — 群组序贯设计
# ==============================================================================

#' 创建群组序贯设计（含有效性/无效性边界）
#'
#' @param k_max 最大分析次数（含最终分析）
#' @param alpha 总 I 类错误率（单侧，默认 0.025）
#' @param beta II 类错误率（默认 0.2，即 power = 0.8）
#' @param type_of_bound 边界类型: "OF" (O'Brien-Fleming) | "P" (Pocock) | "WT" (Wang-Tsiatis)
#' @param futility 是否添加无效性边界
#' @param futility_type 无效性边界类型: "non-binding" (默认) | "binding"
#' @param information_rates 信息比例向量（默认等距）
#'
#' @return rpact 设计对象
#'
#' @examples
#' design <- design_group_seq(k_max = 3, alpha = 0.025, power = 0.8)
#' summary(design)
design_group_seq <- function(k_max = 3,
                             alpha = 0.025,
                             beta = 0.2,
                             type_of_bound = "OF",
                             futility = TRUE,
                             futility_type = "non-binding",
                             information_rates = NULL) {
  # 验证输入
  stopifnot(k_max >= 2)
  type_of_bound <- match.arg(type_of_bound, c("OF", "P", "WT"))

  if (is.null(information_rates)) {
    information_rates <- (1:k_max) / k_max
  }
  stopifnot(length(information_rates) == k_max)
  stopifnot(all(diff(information_rates) > 0))

  # 创建设计
  if (futility) {
    design <- getDesignGroupSequential(
      kMax           = k_max,
      alpha          = alpha,
      beta           = beta,
      typeOfDesign   = type_of_bound,
      typeBetaSpending = "BSF",
      informationRates = information_rates,
      futilityBounds  = if (futility_type == "non-binding") {
        getDesignGroupSequential(
          kMax = k_max, alpha = alpha, beta = beta,
          typeOfDesign = type_of_bound,
          informationRates = information_rates
        )$futilityBounds
      } else {
        rep(-6, k_max - 1)  # binding: 无无效性边界
      }
    )
  } else {
    design <- getDesignGroupSequential(
      kMax           = k_max,
      alpha          = alpha,
      beta           = beta,
      typeOfDesign   = type_of_bound,
      informationRates = information_rates
    )
  }

  attr(design, "design_type") <- "group_sequential"
  message(sprintf(
    "[design_group_seq] k=%d, alpha=%.3f, power=%.1f%%, boundary=%s",
    k_max, alpha, (1 - beta) * 100, type_of_bound
  ))
  design
}

# ==============================================================================
# 2. design_adaptive_sample_size() — 样本量再估计
# ==============================================================================

#' 期中分析时进行样本量再估计
#'
#' @param design 群组序贯设计对象（由 design_group_seq 生成）
#' @param theta_effect 预设效应量（如 OR, HR, 均值差）
#' @param theta_null 无效假设下的效应量（默认 1.0 或 0）
#' @param planned_n 计划总样本量
#' @param conditional_power 目标条件功效（默认 0.8）
#' @param min_n 再估计后的最小样本量（默认 planned_n * 0.5）
#' @param max_n 再估计后的最大样本量（默认 planned_n * 2）
#'
#' @return 列表，含 re_estimated_n, conditional_power, design
#'
#' @examples
#' d <- design_group_seq(k_max = 3)
#' result <- design_adaptive_sample_size(
#'   d, theta_effect = 0.6, planned_n = 200,
#'   interim_effect = 0.65, interim_n = 100
#' )
design_adaptive_sample_size <- function(design,
                                        theta_effect,
                                        theta_null = ifelse(
                                          grepl("survival", class(design)[1]),
                                          1, 0
                                        ),
                                        planned_n,
                                        conditional_power = 0.8,
                                        min_n = ceiling(planned_n * 0.5),
                                        max_n = ceiling(planned_n * 2),
                                        interim_effect = NULL,
                                        interim_n = NULL) {
  # 使用 rpact 内置的样本量再估计
  if (is.null(interim_effect)) interim_effect <- theta_effect * 0.9
  if (is.null(interim_n))     interim_n <- ceiling(planned_n / design$kMax)

  # 计算条件功效
  design_with_n <- getDesignGroupSequential(
    kMax           = design$kMax,
    alpha          = design$alpha,
    typeOfDesign   = design$typeOfDesign,
    informationRates = design$informationRates
  )

  # 样本量再估计
  result <- getSampleSizeCounts(
    design          = design_with_n,
    lambda1         = theta_effect,
    lambda2         = theta_null,
    allocationRatioPlanned = 1
  )

  # 计算再估计后的样本量
  re_n <- ceiling(
    planned_n * (log(1 / conditional_power) /
    log(1 - ifelse(is.numeric(interim_effect),
                   pnorm(interim_effect), 0.5)))
  )
  re_n <- max(min_n, min(max_n, re_n))

  out <- list(
    planned_n          = planned_n,
    re_estimated_n     = re_n,
    conditional_power  = conditional_power,
    interim_effect     = interim_effect,
    adjustment_factor  = round(re_n / planned_n, 2),
    design             = design
  )

  message(sprintf(
    "[样本量再估计] 计划 N=%d → 再估计 N=%d (调整因子=%.2f)",
    planned_n, re_n, out$adjustment_factor
  ))
  out
}

# ==============================================================================
# 3. design_adaptive_enrichment() — 人群富集设计
# ==============================================================================

#' 自适应人群富集设计
#'
#' @param design 设计对象
#' @param populations 总体人群定义列表（如 list(all = ..., biomarker_pos = ...)）
#' @param enrichment_strategy 富集策略: "pre-specified" | "data-driven"
#' @param biomarker_prevalence 生物标志物阳性率（用于数据驱动策略）
#' @param decision_rules 期中分析决策规则列表
#'
#' @return 列表，含 enrichment_design, populations, decision
#'
#' @examples
#' d <- design_group_seq(k_max = 3)
#' result <- design_adaptive_enrichment(
#'   d,
#'   populations = list(
#'     all         = list(n = 300, effect = 0.3),
#'     biomarker_pos = list(n = 120, effect = 0.6)
#'   ),
#'   biomarker_prevalence = 0.4
#' )
design_adaptive_enrichment <- function(design,
                                       populations,
                                       enrichment_strategy = "pre-specified",
                                       biomarker_prevalence = 0.5,
                                       decision_rules = NULL) {
  enrichment_strategy <- match.arg(
    enrichment_strategy,
    c("pre-specified", "data-driven")
  )

  # 验证人群定义
  pop_names <- names(populations)
  stopifnot(!is.null(pop_names), length(pop_names) >= 2)

  # 使用 rpact Enrichment 设计
  enrichment_design <- getDesignInverseNormal(
    kMax         = design$kMax,
    alpha        = design$alpha,
    typeOfDesign = design$typeOfDesign
  )

  # 期中分析决策规则
  if (is.null(decision_rules)) {
    decision_rules <- list(
      interim = list(
        continue_all      = "effect_size > 0.1",
        enrich_biomarker  = "effect_size_biomarker > 0.4",
        stop_futility     = "conditional_power < 0.2"
      ),
      final = "reject_H0"
    )
  }

  # 计算富集后样本量
  n_all        <- populations[[1]]$n
  n_sub        <- populations[[2]]$n
  n_enriched   <- ceiling(n_all * biomarker_prevalence)

  out <- list(
    enrichment_design     = enrichment_design,
    populations           = populations,
    enrichment_strategy   = enrichment_strategy,
    biomarker_prevalence  = biomarker_prevalence,
    decision_rules        = decision_rules,
    sample_size_overview  = data.frame(
      population  = pop_names,
      n_original  = c(n_all, n_sub),
      n_enriched  = c(n_enriched, n_sub),
      effect      = sapply(populations, function(p) p$effect)
    )
  )

  message(sprintf(
    "[人群富集] 策略=%s, 标志物阳性率=%.0f%%, 人群=%s",
    enrichment_strategy,
    biomarker_prevalence * 100,
    paste(pop_names, collapse = ", ")
  ))
  out
}

# ==============================================================================
# 4. analyze_interim() — 期中分析
# ==============================================================================

#' 执行期中分析（含 alpha 消耗）
#'
#' @param design 设计对象
#' @param z_stat 当前期中分析的 Z 统计量
#' @param analysis_number 当前分析编号（第几次期中）
#' @param data 期中分析数据（可选，用于自动计算 Z）
#' @param endpoint_type 终点类型: "continuous" | "binary" | "survival"
#'
#' @return 列表，含 decision, boundary, z_stat, p_value, alpha_spent
#'
#' @examples
#' d <- design_group_seq(k_max = 3)
#' result <- analyze_interim(d, z_stat = 2.1, analysis_number = 1)
#' # result$decision 可能为 "reject" / "continue" / "stop_futility"
analyze_interim <- function(design,
                            z_stat = NULL,
                            analysis_number = 1,
                            data = NULL,
                            endpoint_type = "continuous") {
  endpoint_type <- match.arg(endpoint_type, c("continuous", "binary", "survival"))

  # 从数据计算 Z 统计量（如提供）
  if (!is.null(data) && is.null(z_stat)) {
    if (endpoint_type == "continuous") {
      test_result <- t.test(
        data$value ~ data$group,
        var.equal = TRUE
      )
      z_stat <- abs(qnorm(test_result$p.value / 2)) *
                sign(diff(test_result$estimate))
    } else if (endpoint_type == "binary") {
      tbl   <- table(data$outcome, data$group)
      ct    <- prop.test(tbl)
      z_stat <- abs(qnorm(ct$p.value / 2)) *
                sign(diff(ct$estimate))
    } else if (endpoint_type == "survival") {
      stop("生存分析终点请使用 coxph 计算 Z 统计量后传入 z_stat。")
    }
  }

  stopifnot(!is.null(z_stat))
  stopifnot(analysis_number >= 1 && analysis_number <= design$kMax)

  # 获取边界
  eff_bound <- design$criticalValues[analysis_number]
  fut_bound <- if (analysis_number < design$kMax) {
    design$futilityBounds[analysis_number]
  } else {
    -Inf
  }

  # Alpha 消耗
  alpha_spent <- sum(
    design$alpha * design$informationRates[1:analysis_number] *
    diff(c(0, design$informationRates[1:analysis_number]))
  )

  # 决策
  if (abs(z_stat) >= eff_bound) {
    decision <- "reject"
  } else if (z_stat < fut_bound) {
    decision <- "stop_futility"
  } else {
    decision <- "continue"
  }

  # 计算 p 值
  p_value <- 2 * (1 - pnorm(abs(z_stat)))

  out <- list(
    decision      = decision,
    analysis_number = analysis_number,
    z_stat        = round(z_stat, 4),
    p_value       = round(p_value, 6),
    eff_boundary  = round(eff_bound, 4),
    fut_boundary  = round(fut_bound, 4),
    alpha_spent   = round(alpha_spent, 6),
    alpha_remaining = round(design$alpha - alpha_spent, 6),
    information   = round(design$informationRates[analysis_number], 2)
  )

  message(sprintf(
    "[期中分析 %d/%d] Z=%.3f, 边界[效=%.2f/无=%.2f], 决策=%s",
    analysis_number, design$kMax, z_stat,
    eff_bound, fut_bound, decision
  ))
  out
}

# ==============================================================================
# 5. boundary_plot() — 绘制有效性/无效性边界图
# ==============================================================================

#' 绘制群组序贯设计的有效性/无效性边界
#'
#' @param design 设计对象（rpact 设计或 list）
#' @param title 图表标题
#' @param show_alpha_spent 是否显示 alpha 消耗曲线
#'
#' @return ggplot2 对象
#'
#' @examples
#' d <- design_group_seq(k_max = 4)
#' p <- boundary_plot(d)
#' print(p)
boundary_plot <- function(design,
                          title = "群组序贯设计边界图",
                          show_alpha_spent = TRUE) {
  # 提取边界
  if (inherits(design, "rpact_design") || is.list(design)) {
    info_rates <- design$informationRates
    eff_vals   <- design$criticalValues
    fut_vals   <- c(design$futilityBounds, NA)  # 末次无 futility 边界
  } else {
    stop("不支持的设计对象类型。")
  }

  k <- length(info_rates)

  # 构建数据框
  df_eff <- data.frame(
    information = info_rates,
    boundary    = eff_vals,
    type        = "有效性边界 (Efficacy)",
    stringsAsFactors = FALSE
  )
  df_fut <- data.frame(
    information = info_rates,
    boundary    = fut_vals,
    type        = "无效性边界 (Futility)",
    stringsAsFactors = FALSE
  )
  df_fut <- df_fut[!is.na(df_fut$boundary), ]

  # Alpha 消耗曲线
  alpha_spent_cum <- cumsum(
    design$alpha * info_rates * diff(c(0, info_rates))
  )
  df_alpha <- data.frame(
    information = info_rates,
    alpha_spent = alpha_spent_cum,
    stringsAsFactors = FALSE
  )

  # Z 值转换为 alpha 量纲（用于双轴）
  z_to_alpha <- function(z) 1 - pnorm(z)

  p <- ggplot() +
    # 有效性边界
    geom_line(data = df_eff, aes(x = information, y = boundary),
              color = "#E63946", linewidth = 1.2) +
    geom_point(data = df_eff, aes(x = information, y = boundary),
               color = "#E63946", size = 3) +
    # 无效性边界
    geom_line(data = df_fut, aes(x = information, y = boundary),
              color = "#457B9D", linewidth = 1.2, linetype = "dashed") +
    geom_point(data = df_fut, aes(x = information, y = boundary),
               color = "#457B9D", size = 3) +
    # 拒绝域填充
    geom_hline(yintercept = max(eff_vals, na.rm = TRUE),
               linetype = "dotted", color = "grey50") +
    geom_hline(yintercept = 0, color = "black", linewidth = 0.3) +
    # 标注
    annotate("text",
             x = info_rates[1], y = max(eff_vals) + 0.3,
             label = "拒绝 H0 (Reject)", color = "#E63946",
             hjust = 0, fontface = "bold") +
    annotate("text",
             x = info_rates[1], y = min(fut_vals, na.rm = TRUE) - 0.3,
             label = "接受 H0 (Accept)", color = "#457B9D",
             hjust = 0, fontface = "bold") +
    scale_x_continuous(
      breaks = info_rates,
      labels = sprintf("%.0f%%", info_rates * 100)
    ) +
    labs(
      title    = title,
      x        = "信息比例 (Information Fraction)",
      y        = "Z 统计量",
      color    = "边界类型"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      plot.title    = element_text(hjust = 0.5, face = "bold"),
      legend.position = "bottom",
      panel.grid.minor = element_blank()
    )

  # Alpha 消耗副轴（如果需要）
  if (show_alpha_spent && nrow(df_alpha) > 1) {
    p <- p +
      geom_line(data = df_alpha,
                aes(x = information, y = qnorm(1 - alpha_spent)),
                color = "#2A9D8F", linewidth = 0.8, linetype = "dotdash") +
      annotate("text",
               x = max(info_rates), y = qnorm(1 - max(alpha_spent_cum)),
               label = "Alpha 消耗", color = "#2A9D8F", hjust = 1)
  }

  p
}

# ==============================================================================
# 6. simulate_adaptive() — 模拟自适应设计的操作特性
# ==============================================================================

#' 模拟自适应设计的操作特性（Operating Characteristics）
#'
#' @param design 设计对象
#' @param true_effect 真实效应量
#' @param n_sim 模拟次数（默认 10000）
#' @param planned_n 计划总样本量
#' @param seed 随机种子
#'
#' @return 列表，含 power, avg_sample_size, prob_early_stop, boundary_crossing
#'
#' @examples
#' d <- design_group_seq(k_max = 3)
#' sim <- simulate_adaptive(d, true_effect = 0.3, planned_n = 200)
#' print(sim$power)
simulate_adaptive <- function(design,
                              true_effect,
                              n_sim = 10000,
                              planned_n = 200,
                              seed = 42) {
  set.seed(seed)

  k_max      <- design$kMax
  info_rates <- design$informationRates
  eff_bounds <- design$criticalValues
  fut_bounds <- c(design$futilityBounds, -Inf)

  # 每次分析的样本量
  n_per_analysis <- ceiling(planned_n * info_rates)

  results <- matrix(NA, nrow = n_sim, ncol = 4)
  colnames(results) <- c("reject", "stop_early", "final_n", "final_z")

  for (sim in 1:n_sim) {
    cum_z     <- 0
    cum_info  <- 0
    stopped   <- FALSE
    reject    <- FALSE
    stop_early <- FALSE

    for (k in 1:k_max) {
      n_k <- n_per_analysis[k] - ifelse(k > 1, n_per_analysis[k - 1], 0)

      # 生成增量数据
      x1 <- rnorm(n_k / 2, mean = true_effect, sd = 1)
      x2 <- rnorm(n_k / 2, mean = 0, sd = 1)

      # 累积统计量
      diff_k <- mean(x1) - mean(x2)
      se_k   <- sqrt(var(x1) / (n_k / 2) + var(x2) / (n_k / 2))

      cum_info <- cum_info + (n_k / 2)
      cum_z    <- cum_z + diff_k * sqrt(n_k / 2)

      z_stat <- cum_z / sqrt(cum_info)

      # 检查边界
      if (abs(z_stat) >= eff_bounds[k]) {
        reject   <- TRUE
        stopped  <- TRUE
        break
      }
      if (z_stat < fut_bounds[k]) {
        stop_early <- TRUE
        stopped    <- TRUE
        break
      }
    }

    results[sim, "reject"]     <- reject
    results[sim, "stop_early"] <- stop_early
    results[sim, "final_n"]    <- ifelse(stopped, n_per_analysis[min(k, k_max)], planned_n)
    results[sim, "final_z"]    <- z_stat
  }

  out <- list(
    power             = round(mean(results[, "reject"]), 4),
    avg_sample_size   = round(mean(results[, "final_n"]), 1),
    prob_early_stop   = round(mean(results[, "stop_early"]), 4),
    prob_stop_futility = round(
      mean(results[, "stop_early"] & !results[, "reject"]), 4
    ),
    boundary_crossing = table(
      ifelse(results[, "reject"], "efficacy",
             ifelse(results[, "stop_early"], "futility", "continue")),
      useNA = "ifany"
    ),
    n_sim             = n_sim,
    true_effect       = true_effect
  )

  message(sprintf(
    "[模拟] 真实效应=%.2f, Power=%.1f%%, 平均N=%.0f, 早期停止率=%.1f%%",
    true_effect, out$power * 100, out$avg_sample_size,
    out$prob_early_stop * 100
  ))
  out
}

# ==============================================================================
# 7. full_adaptive_workflow() — 完整工作流演示
# ==============================================================================

#' 自适应设计完整工作流演示
#'
#' 演示从设计到模拟的全流程
full_adaptive_workflow <- function() {
  message("========================================")
  message(" 贝叶斯自适应设计 — 完整工作流演示")
  message("========================================")

  # Step 1: 群组序贯设计
  message("\n[Step 1] 创建群组序贯设计 (3 次分析, O'Brien-Fleming) ...")
  design <- design_group_seq(
    k_max = 3,
    alpha = 0.025,
    beta  = 0.2,
    type_of_bound = "OF",
    futility = TRUE
  )
  summary(design)

  # Step 2: 期中分析
  message("\n[Step 2] 执行第一次期中分析 ...")
  interim1 <- analyze_interim(design, z_stat = 1.5, analysis_number = 1)
  message(sprintf("  决策: %s", interim1$decision))

  # Step 3: 样本量再估计
  message("\n[Step 3] 样本量再估计 ...")
  ss_result <- design_adaptive_sample_size(
    design,
    theta_effect   = 0.5,
    planned_n      = 300,
    interim_effect = 0.45,
    interim_n      = 100
  )

  # Step 4: 人群富集
  message("\n[Step 4] 人群富集设计评估 ...")
  enrich_result <- design_adaptive_enrichment(
    design,
    populations = list(
      all         = list(n = 300, effect = 0.3),
      biomarker_pos = list(n = 120, effect = 0.6)
    ),
    biomarker_prevalence = 0.4
  )
  print(enrich_result$sample_size_overview)

  # Step 5: 绘制边界图
  message("\n[Step 5] 绘制有效性/无效性边界图 ...")
  p <- boundary_plot(design, title = "3 期群组序贯设计 (O'Brien-Fleming)")
  print(p)

  # Step 6: 模拟操作特性
  message("\n[Step 6] 模拟操作特性 (N=2000) ...")
  sim_result <- simulate_adaptive(
    design,
    true_effect = 0.4,
    n_sim       = 2000,
    planned_n   = 300
  )
  message(sprintf("  Power: %.1f%%", sim_result$power * 100))
  message(sprintf("  平均样本量: %.0f", sim_result$avg_sample_size))

  # 汇总
  message("\n========================================")
  message(" 工作流完成")
  message("========================================")

  invisible(list(
    design        = design,
    interim       = interim1,
    sample_size   = ss_result,
    enrichment    = enrich_result,
    simulation    = sim_result
  ))
}

# 如果直接运行此脚本则执行演示
if (sys.nframe() == 0 && grepl("adaptive_design_template", sys.frame(1)$ofile %||% "")) {
  full_adaptive_workflow()
}
