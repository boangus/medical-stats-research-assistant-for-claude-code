# =============================================================================
# 重复测量方差分析模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 base R (aov/Anova) + rstatix + emmeans，提供重复测量 ANOVA 全流程
#
# 功能:
#   - 单因素 / 两因素重复测量 ANOVA
#   - Mauchly 球形度检验 + GG/HF 校正
#   - 事后多重比较 (Bonferroni / BH)
#   - 效应量计算 (广义 eta² / 偏 eta²)
#   - 格式化结果表
#   - 完整工作流示例
#
# 参考:
#   rstatix: https://rpkgs.datanovia.com/rstatix/
#   emmeans: https://cran.r-project.org/web/packages/emmeans/
#   Bakeman (2005) Effect size guidelines for repeated measures designs
#
# 依赖:
#   install.packages(c("rstatix", "emmeans", "car", "dplyr", "tidyr"))
# =============================================================================

library(rstatix)
library(emmeans)
library(car)
library(dplyr)
library(tidyr)

# =============================================================================
# 1. 重复测量 ANOVA 主函数
# =============================================================================

#' 重复测量方差分析（单因素或两因素）
#'
#' 支持单因素 (one-way) 和两因素 (two-way) 重复测量设计。
#' 内部使用 aov() 拟合模型，自动处理长格式 / 宽格式转换。
#'
#' @param data 数据框（长格式或宽格式均可）
#' @param id_var 被试 ID 变量名（字符）
#' @param within_vars 被试内因素名向量（字符），长度 1 或 2
#' @param dv 因变量名（字符）
#' @param between_vars 被试间因素名向量（字符，可选，用于混合设计）
#'
#' @return list(model = aov, anova_table = data.frame, formula = formula)
rm_anova <- function(data, id_var, within_vars, dv, between_vars = NULL) {

  if (length(within_vars) > 2) {
    stop("本模板最多支持两因素重复测量 ANOVA，请使用 lme4/lme 对更复杂设计建模")
  }

  # 确保 ID 和被试内因素为因子
  data[[id_var]] <- as.factor(data[[id_var]])
  for (wv in within_vars) {
    data[[wv]] <- as.factor(data[[wv]])
  }
  if (!is.null(between_vars)) {
    for (bv in between_vars) {
      data[[bv]] <- as.factor(data[[bv]])
    }
  }

  # 构建公式
  within_str <- paste(within_vars, collapse = "*")
  if (is.null(between_vars)) {
    fml_str <- paste(dv, "~", within_str, "+ Error(", id_var, "/(",
                     within_str, "))")
  } else {
    between_str <- paste(between_vars, collapse = "*")
    fml_str <- paste(dv, "~", between_str, "*", within_str,
                     "+ Error(", id_var, "/(", within_str, "))")
  }
  fml <- as.formula(fml_str)

  cat("=== 重复测量 ANOVA ===\n")
  cat("模型公式:", fml_str, "\n")
  cat("被试内因素:", paste(within_vars, collapse = " x "), "\n")
  if (!is.null(between_vars)) {
    cat("被试间因素:", paste(between_vars, collapse = " x "), "\n")
  }
  cat("因变量:", dv, "\n")
  cat("被试数:", length(unique(data[[id_var]])), "\n\n")

  # 拟合模型
  model <- aov(fml, data = data)

  # 提取 ANOVA 表
  anova_tbl <- summary(model)

  # 打印结果
  cat("--- ANOVA 表 ---\n")
  print(anova_tbl)

  # 使用 car::Anova 获取 Type III SS（对不平衡设计更稳健）
  # 需要先将数据转换为宽格式
  if (length(within_vars) == 1) {
    wide_data <- data %>%
      select(all_of(c(id_var, within_vars, dv, between_vars))) %>%
      pivot_wider(names_from = all_of(within_vars),
                  values_from = all_of(dv))

    idv_names <- levels(data[[within_vars[1]]])
    Y <- as.matrix(wide_data[, idv_names, drop = FALSE])
    id_factor <- wide_data[[id_var]]

    within_design <- data.frame(wv1 = factor(idv_names))
    names(within_design) <- within_vars[1]

    if (!is.null(between_vars)) {
      between_data <- as.data.frame(wide_data[, between_vars, drop = FALSE])
      between_data[[id_var]] <- wide_data[[id_var]]

      # 转换 between 变量为因子
      for (bv in between_vars) between_data[[bv]] <- as.factor(between_data[[bv]])

      idata <- within_design
      mod_lm <- lm(Y ~ 1)
      between_fml <- as.formula(paste("Y ~", paste(between_vars, collapse = "*")))
      mod_lm <- update(mod_lm, between_fml, data = between_data)

      car_anova <- Anova(mod_lm, idata = idata, idesign = as.formula(paste("~", within_vars[1])),
                          type = "III")
    } else {
      idata <- within_design
      mod_lm <- lm(Y ~ 1)
      car_anova <- Anova(mod_lm, idata = idata, idesign = as.formula(paste("~", within_vars[1])),
                          type = "III")
    }

    cat("\n--- car::Anova Type III SS ---\n")
    print(car_anova)
  } else {
    # 两因素: 仅使用 aov 结果
    car_anova <- NULL
    cat("\n(两因素设计: car::Anova 输出简化，以上方 aov 结果为准)\n")
  }

  invisible(list(
    model       = model,
    anova_table = anova_tbl,
    car_anova   = car_anova,
    formula     = fml
  ))
}

# =============================================================================
# 2. 球形度检验与校正
# =============================================================================

#' Mauchly 球形度检验 + Greenhouse-Geisser / Huynh-Feldt 校正
#'
#' 球形度是单因素重复测量 ANOVA 的关键假设。
#' 若违反球形度，F 检验的 I 类错误率会膨胀，
#' 需使用 GG 或 HF 校正自由度。
#'
#' @param data 数据框
#' @param id_var 被试 ID 变量名
#' @param within_var 被试内因素名（单因素，字符）
#' @param dv 因变量名（字符）
#'
#' @return list(mauchly = list, corrections = data.frame, sphericity_met = logical)
sphericity_check <- function(data, id_var, within_var, dv) {

  # 确保因子
  data[[id_var]]    <- as.factor(data[[id_var]])
  data[[within_var]] <- as.factor(data[[within_var]])

  # 使用 rstatix 的 anova_test（自动执行球形度检验）
  anova_res <- data %>%
    anova_test(dv = !!sym(dv), wid = !!sym(id_var),
               within = !!sym(within_var))

  # 提取 Mauchly 检验
  mauchly_res <- data %>%
    select(!!sym(id_var), !!sym(within_var), !!sym(dv)) %>%
    pivot_wider(names_from = !!sym(within_var), values_from = !!sym(dv)) %>%
    select(-!!sym(id_var)) %>%
    as.matrix() %>%
    mauchly.test()

  cat("=== Mauchly 球形度检验 ===\n")
  cat("Mauchly's W:", round(mauchly_res$statistic, 4), "\n")
  cat("Chi-sq:", round(mauchly_res$parameter, 2), "\n")
  cat("p-value:", format.pval(mauchly_res$p.value, digits = 4), "\n")

  sphericity_met <- mauchly_res$p.value >= 0.05

  if (sphericity_met) {
    cat("结论: 球形度假设满足 (p >= 0.05)，可使用未校正结果\n")
  } else {
    cat("结论: 球形度假设违反 (p < 0.05)，应使用校正结果\n")
  }

  # 提取校正结果
  corrections <- anova_res %>%
    filter(!is.na(DFn) & Effect == within_var) %>%
    select(Effect, DFn, DFn, F, p) %>%
    head(1)

  # 获取 GG 和 HF epsilon
  # 使用 rstatix 获取
  epsilon_res <- data %>%
    select(!!sym(id_var), !!sym(within_var), !!sym(dv)) %>%
    pivot_wider(names_from = !!sym(within_var), values_from = !!sym(dv)) %>%
    select(-!!sym(id_var)) %>%
    as.matrix() %>%
    rstatix::get_anova_table() %>%
    suppressWarnings()

  cat("\n--- 球形度校正因子 ---\n")
  cat("注: epsilon = 1.0 表示完全满足球形度\n")
  cat("GG (Greenhouse-Geisser): 适用于 epsilon < 0.75\n")
  cat("HF (Huynh-Feldt):        适用于 epsilon >= 0.75\n")

  # 从 anova_test 输出中提取
  if ("GGe" %in% names(anova_res)) {
    gg_eps  <- anova_res$GGe[anova_res$Effect == within_var]
    hf_eps  <- anova_res$HFe[anova_res$Effect == within_var]
    gg_p    <- anova_res$p[anova_res$Effect == within_var]  # 近似

    correction_df <- data.frame(
      correction = c("None (Sphericity assumed)",
                     "Greenhouse-Geisser",
                     "Huynh-Feldt"),
      epsilon    = c(1.0, gg_eps, hf_eps),
      stringsAsFactors = FALSE
    )

    cat("\nGG epsilon:", round(gg_eps, 4), "\n")
    cat("HF epsilon:", round(hf_eps, 4), "\n")

    if (gg_eps < 0.75) {
      cat("建议: 使用 Greenhouse-Geisser 校正\n")
    } else {
      cat("建议: 使用 Huynh-Feldt 校正\n")
    }
  } else {
    correction_df <- NULL
  }

  invisible(list(
    mauchly        = mauchly_res,
    corrections    = correction_df,
    sphericity_met = sphericity_met,
    anova_table    = anova_res
  ))
}

# =============================================================================
# 3. 事后多重比较
# =============================================================================

#' 重复测量 ANOVA 事后比较
#'
#' 使用 emmeans 进行边际均值估计，再执行配对比较。
#' 支持 Bonferroni 和 Benjamini-Hochberg (BH/FDR) 校正。
#'
#' @param data 数据框
#' @param id_var 被试 ID 变量名
#' @param within_var 被试内因素名
#' @param dv 因变量名
#' @param adjust p 值校正方法: "bonferroni" / "holm" / "BH" / "fdr"
#'
#' @return data.frame 事后比较结果
rm_posthoc <- function(data, id_var, within_var, dv,
                       adjust = "bonferroni") {

  data[[id_var]]     <- as.factor(data[[id_var]])
  data[[within_var]] <- as.factor(data[[within_var]])

  # 方法 1: 使用 rstatix pairwise_t_test
  cat("=== 事后比较 (", adjust, " 校正) ===\n\n")

  rstatix_posthoc <- data %>%
    pairwise_t_test(
      as.formula(paste(dv, "~", within_var)),
      paired = TRUE,
      p.adjust.method = adjust,
      detailed = TRUE
    ) %>%
    add_significance()

  cat("--- rstatix 配对 t 检验 ---\n")
  print(rstatix_posthoc, width = Inf)

  # 方法 2: 使用 emmeans
  fml <- as.formula(paste("pairwise ~", within_var))
  emm <- emmeans(
    object = as.formula(paste(dv, "~", within_var)),
    data   = data,
    specs  = pairwise ~ 1,
    adjust = adjust
  )

  # 提取边际均值
  emm_means <- emmeans(
    as.formula(paste(dv, "~", within_var)),
    data = data
  )

  cat("\n--- 边际均值 (emmeans) ---\n")
  print(summary(emm_means))

  # 配对比较
  pairs_res <- pairs(emm_means, adjust = adjust)
  cat("\n--- emmeans 配对比较 ---\n")
  print(summary(pairs_res))

  # 效应量 (Cohen's d for paired)
  eff_df <- data %>%
    pairwise_t_test(
      as.formula(paste(dv, "~", within_var)),
      paired = TRUE,
      p.adjust.method = adjust,
      detailed = TRUE,
      effsize.type = "cohen"
    ) %>%
    add_significance() %>%
    add_effsize(
      as.formula(paste(dv, "~", within_var)),
      paired = TRUE,
      type = "cohen"
    )

  cat("\n--- 效应量 (Cohen's d) ---\n")
  print(eff_df, width = Inf)

  invisible(list(
    rstatix_result = rstatix_posthoc,
    emmeans_result = summary(pairs_res),
    effect_size    = eff_df,
    marginal_means = summary(emm_means)
  ))
}

# =============================================================================
# 4. 效应量计算
# =============================================================================

#' 重复测量 ANOVA 效应量计算
#'
#' 计算广义 eta² (ges) 和偏 eta² (pes)。
#' 广义 eta² 更适合重复测量设计，因为它对效应的可推广性
#' 提供了更一致的衡量标准。
#'
#' @param model aov 模型对象
#'
#' @return data.frame 包含效应量
rm_effect_size <- function(model) {

  cat("=== 效应量计算 ===\n\n")

  # 从 aov summary 中提取 SS
  aov_summ <- summary(model)

  # 提取各层的 SS
  ss_residual <- 0
  ss_terms    <- list()

  for (layer_name in names(aov_summ)) {
    layer <- aov_summ[[layer_name]]
    if (is.list(layer)) {
      for (tbl_name in names(layer)) {
        tbl <- layer[[tbl_name]]
        if (is.matrix(tbl) || is.data.frame(tbl)) {
          row_names <- rownames(tbl)
          for (rn in row_names) {
            if (grepl("Residuals", rn)) {
              ss_residual <- ss_residual + tbl[rn, "Sum Sq"]
            } else if (rn != "") {
              ss_terms[[rn]] <- tbl[rn, "Sum Sq"]
            }
          }
        }
      }
    }
  }

  # 计算效应量
  ss_total <- sum(unlist(ss_terms)) + ss_residual
  results <- data.frame(
    term       = names(ss_terms),
    ss         = unlist(ss_terms),
    pes        = NA_real_,   # 偏 eta² = SS_effect / (SS_effect + SS_error)
    ges        = NA_real_,   # 广义 eta² = SS_effect / (SS_total)
    stringsAsFactors = FALSE
  )

  results$pes <- results$ss / (results$ss + ss_residual)
  results$ges <- results$ss / ss_total

  # 添加解释
  results$interpretation <- case_when(
    results$pes >= 0.14 ~ "大效应",
    results$pes >= 0.06 ~ "中效应",
    results$pes >= 0.01 ~ "小效应",
    TRUE                ~ "极小效应"
  )

  results$pes <- round(results$pes, 4)
  results$ges <- round(results$ges, 4)

  cat("偏 eta² (pes): SS_effect / (SS_effect + SS_error)\n")
  cat("广义 eta² (ges): SS_effect / SS_total (推荐用于重复测量)\n\n")

  cat("效应量参考标准 (Cohen, 1988; Bakeman, 2005):\n")
  cat("  小效应: eta² = 0.01 | 中效应: eta² = 0.06 | 大效应: eta² = 0.14\n\n")

  print(results, row.names = FALSE)

  invisible(results)
}

# =============================================================================
# 5. 格式化结果表
# =============================================================================

#' 生成格式化的重复测量 ANOVA 结果表
#'
#' 整合 ANOVA 结果、球形度检验、校正后 p 值和效应量，
#' 输出可直接用于论文的格式化表格。
#'
#' @param data 数据框
#' @param id_var 被试 ID 变量名
#' @param within_vars 被试内因素名向量
#' @param dv 因变量名
#'
#' @return data.frame 格式化结果表
rm_anova_table <- function(data, id_var, within_vars, dv) {

  cat("=== 重复测量 ANOVA 结果表 ===\n\n")

  # 运行 ANOVA
  anova_res <- rm_anova(data, id_var, within_vars, dv)
  model <- anova_res$model

  # 球形度检验 (仅单因素)
  if (length(within_vars) == 1) {
    sph_res <- sphericity_check(data, id_var, within_vars[1], dv)
    use_correction <- !sph_res$sphericity_met
  } else {
    sph_res <- NULL
    use_correction <- FALSE
  }

  # 效应量
  eff_res <- rm_effect_size(model)

  # 汇总表
  aov_summ <- summary(model)

  result_rows <- list()
  for (layer_name in names(aov_summ)) {
    layer <- aov_summ[[layer_name]]
    if (is.list(layer)) {
      for (tbl_name in names(layer)) {
        tbl <- layer[[tbl_name]]
        if (is.matrix(tbl) || is.data.frame(tbl)) {
          rn <- rownames(tbl)
          for (i in seq_along(rn)) {
            if (rn[i] != "Residuals" && rn[i] != "") {
              row_data <- list(
                source   = rn[i],
                SS       = round(tbl[i, "Sum Sq"], 3),
                df       = tbl[i, "Df"],
                F        = round(tbl[i, "F value"], 3),
                p        = tbl[i, "Pr(>F)"]
              )
              result_rows[[length(result_rows) + 1]] <- row_data
            }
          }
        }
      }
    }
  }

  # 合并效应量
  result_df <- do.call(rbind, lapply(result_rows, as.data.frame,
                                      stringsAsFactors = FALSE))
  result_df <- result_df[!is.na(result_df$F), ]

  if (nrow(eff_res) > 0) {
    result_df <- merge(result_df, eff_res[, c("term", "pes", "ges", "interpretation")],
                       by.x = "source", by.y = "term", all.x = TRUE)
  }

  # 格式化 p 值
  result_df$p_formatted <- ifelse(
    result_df$p < 0.001, "< 0.001",
    format(round(result_df$p, 3), nsmall = 3)
  )

  cat("--- 格式化结果表 ---\n")
  print(result_df, row.names = FALSE)

  if (use_correction) {
    cat("\n注: 球形度假设违反，建议报告 GG 或 HF 校正后的 p 值\n")
  }

  invisible(list(
    table     = result_df,
    anova     = anova_res,
    sphericity = sph_res,
    effect_size = eff_res
  ))
}

# =============================================================================
# 6. 完整工作流示例
# =============================================================================

#' 重复测量 ANOVA 完整工作流
#'
#' 从模拟数据到最终报告的完整流程演示。
full_rm_anova_workflow <- function() {

  cat("============================================================\n")
  cat(" 重复测量 ANOVA 完整工作流\n")
  cat("============================================================\n\n")

  # --- 步骤 1: 准备数据 ---
  cat(">>> 步骤 1: 准备数据\n")
  set.seed(20250101)
  n_subjects <- 30

  demo_data <- data.frame(
    id     = rep(1:n_subjects, each = 4),
    time   = factor(rep(c("Baseline", "Week4", "Week8", "Week12"),
                        times = n_subjects),
                    levels = c("Baseline", "Week4", "Week8", "Week12")),
    score  = c(
      rnorm(n_subjects, 50, 10),   # Baseline
      rnorm(n_subjects, 48, 10),   # Week4
      rnorm(n_subjects, 42, 10),   # Week8
      rnorm(n_subjects, 38, 10)    # Week12
    )
  )

  cat("数据维度:", nrow(demo_data), "行 x", ncol(demo_data), "列\n")
  cat("被试数:", n_subjects, "\n")
  cat("时间点: Baseline, Week4, Week8, Week12\n")
  cat("因变量: score\n\n")

  # 描述性统计
  desc <- demo_data %>%
    group_by(time) %>%
    summarise(
      n    = n(),
      mean = round(mean(score), 2),
      sd   = round(sd(score), 2),
      se   = round(sd(score) / sqrt(n()), 2),
      .groups = "drop"
    )
  cat("--- 描述性统计 ---\n")
  print(as.data.frame(desc))

  # --- 步骤 2: 重复测量 ANOVA ---
  cat("\n>>> 步骤 2: 重复测量 ANOVA\n")
  anova_res <- rm_anova(demo_data, "id", "time", "score")

  # --- 步骤 3: 球形度检验 ---
  cat("\n>>> 步骤 3: 球形度检验\n")
  sph_res <- sphericity_check(demo_data, "id", "time", "score")

  # --- 步骤 4: 效应量 ---
  cat("\n>>> 步骤 4: 效应量\n")
  eff_res <- rm_effect_size(anova_res$model)

  # --- 步骤 5: 事后比较 ---
  cat("\n>>> 步骤 5: 事后多重比较 (Bonferroni)\n")
  posthoc_res <- rm_posthoc(demo_data, "id", "time", "score",
                             adjust = "bonferroni")

  # --- 步骤 6: 格式化结果表 ---
  cat("\n>>> 步骤 6: 格式化结果表\n")
  tbl_res <- rm_anova_table(demo_data, "id", "time", "score")

  # --- 汇总 ---
  cat("\n============================================================\n")
  cat(" 工作流完成\n")
  cat("============================================================\n")
  cat("输出对象:\n")
  cat("  anova_res   - ANOVA 模型与结果表\n")
  cat("  sph_res     - 球形度检验\n")
  cat("  eff_res     - 效应量\n")
  cat("  posthoc_res - 事后比较\n")
  cat("  tbl_res     - 格式化结果表\n")

  invisible(list(
    anova     = anova_res,
    sphericity = sph_res,
    effect_size = eff_res,
    posthoc   = posthoc_res,
    table     = tbl_res
  ))
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  # ---- 单因素重复测量 ANOVA ----
  set.seed(42)
  n <- 25
  df1 <- data.frame(
    id    = rep(1:n, each = 3),
    treat = factor(rep(c("Pre", "Post1", "Post2"), times = n)),
    y     = c(rnorm(n, 50, 8), rnorm(n, 45, 8), rnorm(n, 40, 8))
  )

  # 运行 ANOVA
  res <- rm_anova(df1, "id", "treat", "y")

  # 球形度
  sph <- sphericity_check(df1, "id", "treat", "y")

  # 事后比较
  ph <- rm_posthoc(df1, "id", "treat", "y", adjust = "bonferroni")

  # 效应量
  es <- rm_effect_size(res$model)

  # 格式化表
  tbl <- rm_anova_table(df1, "id", "treat", "y")

  # ---- 完整工作流 ----
  full <- full_rm_anova_workflow()

  # ---- 带被试间因素的混合设计 ----
  df2 <- data.frame(
    id    = rep(1:40, each = 3),
    group = factor(rep(c("Drug", "Placebo"), each = 60)),
    time  = factor(rep(c("T1", "T2", "T3"), times = 40)),
    y     = rnorm(120, 50, 10)
  )

  mixed_res <- rm_anova(df2, "id", "time", "y", between_vars = "group")
}
