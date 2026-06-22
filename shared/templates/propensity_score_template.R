# propensity_score_template.R — 倾向性评分匹配分析模板（R）
# ================================================================
# 适用于：观察性研究的因果推断、混杂调整、处理效应估计
#
# 功能：
#   - 倾向性评分估计（logistic 回归）
#   - 多种匹配方法（最近邻匹配、卡钳匹配、最优匹配）
#   - 平衡诊断（SMD 计算、标准化差异图）
#   - 效应估计（ATT/ATE）
#   - 敏感性分析（Rosenbaum bounds）
#
# 依赖: MatchIt, tableone, survey, cobalt, ggplot2, rbounds
# 安装: install.packages(c("MatchIt", "tableone", "survey", "cobalt",
#                          "ggplot2", "rbounds"))
#
# 作者: MSRA Team
# 版本: 0.1.0
# ============================================================================

# 抑制不必要的警告，但保留收敛警告
suppressWarnings(suppressMessages({
  library(MatchIt)
  library(tableone)
  library(survey)
  library(cobalt)
  library(ggplot2)
}))

# 辅助函数：安全加载可选依赖
.safe_require <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    warning(sprintf("包 '%s' 未安装，部分功能不可用。请运行 install.packages('%s')", pkg, pkg))
    return(FALSE)
  }
  return(TRUE)
}

# ============================================================================
# 1. 倾向性评分估计
# ============================================================================

#' 估计倾向性评分
#'
#' 使用 logistic 回归估计每个个体接受处理的概率（倾向性评分）。
#'
#' @param data data.frame，分析数据集
#' @param treatment 字符串，处理变量名（0/1 编码）
#' @param covariates 字符向量，协变量名列表
#' @param cat_vars 字符向量，分类协变量名（可选）
#' @param link 字符串，链接函数，"logit"（默认）或 "probit"
#'
#' @return list，包含：
#'   \item{data}{带 ps_score 列的数据框}
#'   \item{model}{logistic 回归模型对象}
#'   \item{c_statistic}{C-统计量（AUC）}
#'
#' @examples
#' \dontrun{
#' ps <- estimate_propensity(df, "treatment", c("age", "bmi", "sex"),
#'                           cat_vars = "sex")
#' }
estimate_propensity <- function(data, treatment, covariates,
                                cat_vars = NULL, link = "logit") {
  # 构建公式
  fml <- as.formula(paste(treatment, "~", paste(covariates, collapse = " + ")))

  # 拟合倾向性评分模型
  if (link == "logit") {
    ps_model <- glm(fml, data = data, family = binomial(link = "logit"))
  } else if (link == "probit") {
    ps_model <- glm(fml, data = data, family = binomial(link = "probit"))
  } else {
    stop("link 必须是 'logit' 或 'probit'")
  }

  # 计算倾向性评分
  data$ps_score <- predict(ps_model, type = "response")

  # 计算 C-统计量（AUC）
  pROC_available <- .safe_require("pROC")
  if (pROC_available) {
    roc_obj <- pROC::roc(data[[treatment]], data$ps_score, quiet = TRUE)
    c_stat <- as.numeric(pROC::auc(roc_obj))
  } else {
    # 手动计算 AUC（Wilcoxon-Mann-Whitney）
    treated_ps <- data$ps_score[data[[treatment]] == 1]
    control_ps <- data$ps_score[data[[treatment]] == 0]
    n_t <- length(treated_ps)
    n_c <- length(control_ps)
    c_stat <- mean(outer(treated_ps, control_ps, function(a, b) (a > b) + 0.5 * (a == b)))
  }

  cat(sprintf("  C-statistic (AUC): %.3f\n", c_stat))
  if (c_stat > 0.8) {
    warning("C-statistic > 0.8，倾向性评分模型可能过度拟合，匹配质量可能受影响。")
  }

  return(list(data = data, model = ps_model, c_statistic = c_stat))
}


# ============================================================================
# 2. 匹配方法
# ============================================================================

#' 最近邻匹配
#'
#' 使用 MatchIt 进行最近邻倾向性评分匹配。
#'
#' @param data data.frame，含倾向性评分的数据（或原始数据）
#' @param treatment 字符串，处理变量名
#' @param covariates 字符向量，协变量名
#' @param ratio 整数，每个处理组个体匹配的对照数（默认 1）
#' @param caliper 数值，卡钳值（倾向性评分 logit 尺度的 SD 倍数，默认 0.2）
#' @param replace 逻辑，是否允许有放回匹配（默认 FALSE）
#'
#' @return list，包含：
#'   \item{matched_data}{匹配后数据框}
#'   \item{match_obj}{MatchIt 对象}
#'   \item{n_treated_before}{匹配前处理组样本量}
#'   \item{n_treated_after}{匹配后处理组样本量}
#'
#' @examples
#' \dontrun{
#' res <- nearest_neighbor_match(df, "treatment", c("age", "bmi"), ratio = 1)
#' }
nearest_neighbor_match <- function(data, treatment, covariates,
                                   ratio = 1, caliper = 0.2,
                                   replace = FALSE) {
  fml <- as.formula(paste(treatment, "~", paste(covariates, collapse = " + ")))

  set.seed(42)
  m.out <- matchit(fml, data = data, method = "nearest",
                   distance = "glm", link = "logit",
                   ratio = ratio, caliper = caliper,
                   replace = replace)

  matched_data <- match.data(m.out)

  cat(sprintf("  匹配前: 处理组 %d, 对照组 %d\n",
              sum(data[[treatment]] == 1), sum(data[[treatment]] == 0)))
  cat(sprintf("  匹配后: 处理组 %d, 对照组 %d\n",
              sum(matched_data[[treatment]] == 1),
              sum(matched_data[[treatment]] == 0)))

  return(list(
    matched_data = matched_data,
    match_obj = m.out,
    n_treated_before = sum(data[[treatment]] == 1),
    n_treated_after = sum(matched_data[[treatment]] == 1)
  ))
}

#' 最优匹配
#'
#' 使用 MatchIt 的最优匹配方法（optimal），最小化总匹配距离。
#'
#' @param data data.frame，分析数据集
#' @param treatment 字符串，处理变量名
#' @param covariates 字符向量，协变量名
#' @param ratio 整数，匹配比例（默认 1）
#' @param caliper 数值，卡钳值（默认 0.2）
#'
#' @return list，同 nearest_neighbor_match
#'
#' @examples
#' \dontrun{
#' res <- optimal_match(df, "treatment", c("age", "bmi"))
#' }
optimal_match <- function(data, treatment, covariates,
                          ratio = 1, caliper = 0.2) {
  fml <- as.formula(paste(treatment, "~", paste(covariates, collapse = " + ")))

  set.seed(42)
  m.out <- matchit(fml, data = data, method = "optimal",
                   distance = "glm", link = "logit",
                   ratio = ratio, caliper = caliper)

  matched_data <- match.data(m.out)

  cat(sprintf("  最优匹配完成: %d 对\n", sum(matched_data[[treatment]] == 1)))

  return(list(
    matched_data = matched_data,
    match_obj = m.out,
    n_treated_before = sum(data[[treatment]] == 1),
    n_treated_after = sum(matched_data[[treatment]] == 1)
  ))
}

#' 全匹配（Full Matching）
#'
#' 使用 MatchIt 的全匹配方法，保留所有样本并分配权重。
#'
#' @param data data.frame，分析数据集
#' @param treatment 字符串，处理变量名
#' @param covariates 字符向量，协变量名
#'
#' @return list，同 nearest_neighbor_match（matched_data 含 weights 列）
full_match <- function(data, treatment, covariates) {
  fml <- as.formula(paste(treatment, "~", paste(covariates, collapse = " + ")))

  set.seed(42)
  m.out <- matchit(fml, data = data, method = "full",
                   distance = "glm", link = "logit")

  matched_data <- match.data(m.out)

  cat(sprintf("  全匹配完成: 保留 %d 个样本\n", nrow(matched_data)))

  return(list(
    matched_data = matched_data,
    match_obj = m.out,
    n_treated_before = sum(data[[treatment]] == 1),
    n_treated_after = sum(matched_data[[treatment]] == 1)
  ))
}


# ============================================================================
# 3. 平衡诊断
# ============================================================================

#' 计算标准化均值差（SMD）
#'
#' 计算匹配前后各协变量的标准化均值差。
#'
#' @param data data.frame，数据集
#' @param treatment 字符串，处理变量名
#' @param covariates 字符向量，协变量名
#' @param weights 数值向量，权重（可选，用于加权后的 SMD）
#'
#' @return data.frame，包含变量名、处理组均值、对照组均值、SMD、平衡标记
#'
#' @examples
#' \dontrun{
#' smd_df <- compute_smd(df, "treatment", c("age", "bmi"))
#' }
compute_smd <- function(data, treatment, covariates, weights = NULL) {
  results <- data.frame(
    Variable = character(),
    Treated_Mean = numeric(),
    Control_Mean = numeric(),
    SMD = numeric(),
    Balance = character(),
    stringsAsFactors = FALSE
  )

  for (var in covariates) {
    t_vals <- data[[var]][data[[treatment]] == 1]
    c_vals <- data[[var]][data[[treatment]] == 0]

    if (!is.null(weights)) {
      t_w <- weights[data[[treatment]] == 1]
      c_w <- weights[data[[treatment]] == 0]
      t_mean <- sum(t_vals * t_w, na.rm = TRUE) / sum(t_w, na.rm = TRUE)
      c_mean <- sum(c_vals * c_w, na.rm = TRUE) / sum(c_w, na.rm = TRUE)
      t_var <- sum(t_w * (t_vals - t_mean)^2, na.rm = TRUE) / sum(t_w, na.rm = TRUE)
      c_var <- sum(c_w * (c_vals - c_mean)^2, na.rm = TRUE) / sum(c_w, na.rm = TRUE)
    } else {
      t_mean <- mean(t_vals, na.rm = TRUE)
      c_mean <- mean(c_vals, na.rm = TRUE)
      t_var <- var(t_vals, na.rm = TRUE)
      c_var <- var(c_vals, na.rm = TRUE)
    }

    pooled_sd <- sqrt((t_var + c_var) / 2)
    smd <- if (pooled_sd > 0) abs(t_mean - c_mean) / pooled_sd else 0

    balance <- ifelse(smd < 0.1, "OK",
                      ifelse(smd < 0.2, "Caution", "Imbalanced"))

    results <- rbind(results, data.frame(
      Variable = var,
      Treated_Mean = round(t_mean, 3),
      Control_Mean = round(c_mean, 3),
      SMD = round(smd, 4),
      Balance = balance,
      stringsAsFactors = FALSE
    ))
  }

  return(results)
}

#' 平衡诊断（使用 cobalt）
#'
#' 使用 cobalt 包进行全面的平衡诊断，包括 SMD、方差比等。
#'
#' @param match_obj MatchIt 对象
#' @param covariates 字符向量，协变量名
#' @param data 原始数据框（匹配前）
#'
#' @return list，包含：
#'   \item{balance_before}{匹配前平衡表}
#'   \item{balance_after}{匹配后平衡表}
#'   \item{summary}{平衡摘要统计}
balance_diagnostics <- function(match_obj, covariates, data) {
  # 匹配前平衡
  bal_before <- bal.tab(match_obj, data = data, un = TRUE,
                        stats = c("mean.diffs", "variance.ratios"),
                        imbalanced.only = FALSE)

  # 提取 SMD 表
  smd_table <- bal_before$Balance

  # 汇总
  n_imbalanced_before <- sum(abs(smd_table$Diff.Un) > 0.1, na.rm = TRUE)
  n_imbalanced_after <- sum(abs(smd_table$Diff.Adj) > 0.1, na.rm = TRUE)

  cat(sprintf("  匹配前 SMD > 0.1 的协变量数: %d\n", n_imbalanced_before))
  cat(sprintf("  匹配后 SMD > 0.1 的协变量数: %d\n", n_imbalanced_after))

  return(list(
    balance_table = smd_table,
    n_imbalanced_before = n_imbalanced_before,
    n_imbalanced_after = n_imbalanced_after,
    bal_obj = bal_before
  ))
}

#' Love Plot（标准化差异图）
#'
#' 绘制匹配前后的协变量标准化均值差对比图。
#'
#' 注意：ps_diagnostics_template.R 中的 ps_love_plot() 提供了更详细的PS诊断可视化（含权重分布图、重叠密度图）。
#' 本函数专注于匹配后的平衡诊断可视化。
#'
#' @param match_obj MatchIt 对象
#' @param title 字符串，图表标题
#' @param threshold 数值，SMD 阈值线（默认 0.1）
#'
#' @return ggplot 对象
#'
#' @examples
#' \dontrun{
#' p <- love_plot(m.out, "Covariate Balance")
#' print(p)
#' }
love_plot <- function(match_obj, title = "Covariate Balance (Love Plot)",
                      threshold = 0.1) {
  p <- love.plot(match_obj, var.order = "unadjusted",
                 line = TRUE, thresholds = c(m = threshold),
                 abs = TRUE, colors = c("red", "steelblue"),
                 shapes = c("circle", "triangle"),
                 sample.names = c("Before Matching", "After Matching"),
                 title = title) +
    theme_minimal(base_size = 12) +
    theme(plot.title = element_text(face = "bold"))

  return(p)
}


# ============================================================================
# 4. 效应估计（ATT/ATE）
# ============================================================================

#' 估计处理效应（ATT）
#'
#' 在匹配后数据上估计平均处理效应（处理组上的平均效应，ATT）。
#'
#' @param matched_data data.frame，匹配后数据（含 weights 列）
#' @param treatment 字符串，处理变量名
#' @param outcome 字符串，结局变量名
#' @param covariates 字符向量，回归调整协变量（可选）
#' @param estimand 字符串，"ATT"（默认）或 "ATE"
#'
#' @return list，包含：
#'   \item{estimate}{效应估计值}
#'   \item{se}{标准误}
#'   \item{ci_lower}{置信区间下限}
#'   \item{ci_upper}{置信区间上限}
#'   \item{p_value}{p 值}
#'   \item{method}{使用的方法}
#'
#' @examples
#' \dontrun{
#' eff <- estimate_effect(matched_df, "treatment", "outcome")
#' }
estimate_effect <- function(matched_data, treatment, outcome,
                            covariates = NULL, estimand = "ATT") {
  # 创建调查设计对象（考虑匹配权重）
  if ("weights" %in% names(matched_data)) {
    design <- svydesign(ids = ~1, data = matched_data,
                        weights = ~weights)
  } else {
    design <- svydesign(ids = ~1, data = matched_data)
  }

  if (is.null(covariates)) {
    # 简单均值差异
    fml <- as.formula(paste(outcome, "~", treatment))
    fit <- svyglm(fml, design = design)
  } else {
    # 回归调整
    fml <- as.formula(paste(outcome, "~", treatment, "+",
                            paste(covariates, collapse = " + ")))
    fit <- svyglm(fml, design = design)
  }

  estimate <- coef(fit)[treatment]
  se <- sqrt(diag(vcov(fit)))[treatment]
  z <- estimate / se
  p_value <- 2 * pnorm(abs(z), lower.tail = FALSE)
  ci_lower <- estimate - 1.96 * se
  ci_upper <- estimate + 1.96 * se

  cat(sprintf("  %s = %.4f (SE = %.4f, 95%% CI: [%.4f, %.4f], p = %.4f)\n",
              estimand, estimate, se, ci_lower, ci_upper, p_value))

  return(list(
    estimate = estimate,
    se = se,
    ci_lower = ci_lower,
    ci_upper = ci_upper,
    p_value = p_value,
    method = sprintf("Survey-weighted regression (%s)", estimand),
    model = fit
  ))
}

#' 估计 ATE（使用 IPTW）
#'
#' 使用逆概率处理加权（IPTW）估计平均处理效应（ATE）。
#'
#' @param data data.frame，原始数据
#' @param treatment 字符串，处理变量名
#' @param outcome 字符串，结局变量名
#' @param covariates 字符向量，协变量名
#' @param stabilize 逻辑，是否使用稳定化权重（默认 TRUE）
#'
#' @return list，同 estimate_effect
estimate_ate_iptw <- function(data, treatment, outcome, covariates,
                              stabilize = TRUE) {
  # 估计倾向性评分
  ps_result <- estimate_propensity(data, treatment, covariates)
  ps <- ps_result$data$ps_score

  # 计算权重
  p_treat <- mean(data[[treatment]] == 1)
  if (stabilize) {
    weights <- ifelse(data[[treatment]] == 1,
                      p_treat / ps,
                      (1 - p_treat) / (1 - ps))
  } else {
    weights <- ifelse(data[[treatment]] == 1,
                      1 / ps,
                      1 / (1 - ps))
  }

  # 截断极端权重
  weights <- pmin(weights, quantile(weights, 0.99, na.rm = TRUE))

  data$iptw_weight <- weights
  design <- svydesign(ids = ~1, data = data, weights = ~iptw_weight)

  fml <- as.formula(paste(outcome, "~", treatment))
  fit <- svyglm(fml, design = design)

  estimate <- coef(fit)[treatment]
  se <- sqrt(diag(vcov(fit)))[treatment]
  z <- estimate / se
  p_value <- 2 * pnorm(abs(z), lower.tail = FALSE)

  cat(sprintf("  ATE (IPTW) = %.4f (SE = %.4f, p = %.4f)\n",
              estimate, se, p_value))

  return(list(
    estimate = estimate,
    se = se,
    ci_lower = estimate - 1.96 * se,
    ci_upper = estimate + 1.96 * se,
    p_value = p_value,
    method = "IPTW (survey-weighted)",
    weights = weights,
    model = fit
  ))
}


# ============================================================================
# 5. 敏感性分析（Rosenbaum bounds）
# ============================================================================

#' Rosenbaum bounds 敏感性分析
#'
#' 评估隐藏偏倚对匹配后因果结论的影响。
#'
#' @param matched_data data.frame，匹配后数据
#' @param treatment 字符串，处理变量名
#' @param outcome 字符串，结局变量名（需为连续变量）
#' @param Gamma 数值向量，要测试的 Gamma 值（隐藏偏倚强度）
#'
#' @return list，包含：
#'   \item{results}{各 Gamma 值下的 p 值表}
#'   \item{critical_gamma}{临界 Gamma 值（结论开始不显著的 Gamma）}
#'
#' @examples
#' \dontrun{
#' sens <- rosenbaum_sensitivity(matched_df, "treatment", "outcome",
#'                                Gamma = seq(1, 2, 0.1))
#' }
rosenbaum_sensitivity <- function(matched_data, treatment, outcome,
                                  Gamma = seq(1, 2, by = 0.1)) {
  if (!.safe_require("rbounds")) {
    stop("需要安装 rbounds 包: install.packages('rbounds')")
  }

  # 准备配对数据
  treated <- matched_data[matched_data[[treatment]] == 1, outcome]
  control <- matched_data[matched_data[[treatment]] == 0, outcome]

  # 确保配对
  n_pairs <- min(length(treated), length(control))
  treated <- treated[1:n_pairs]
  control <- control[1:n_pairs]

  # 计算配对差异
  diffs <- treated - control

  # 使用 Wilcoxon signed rank 检验的 Rosenbaum bounds
  results <- data.frame(
    Gamma = Gamma,
    p_lower = NA_real_,
    p_upper = NA_real_,
    stringsAsFactors = FALSE
  )

  for (i in seq_along(Gamma)) {
    g <- Gamma[i]
    # 使用 rbounds::psens 计算敏感性 bounds
    sens_result <- rbounds::psens(diffs, gamma = g)
    results$p_lower[i] <- sens_result$lower
    results$p_upper[i] <- sens_result$upper
  }

  # 找到临界 Gamma（上界 p 值首次超过 0.05）
  critical_gamma <- NA
  for (i in seq_along(Gamma)) {
    if (results$p_upper[i] > 0.05) {
      critical_gamma <- Gamma[i]
      break
    }
  }

  if (!is.na(critical_gamma)) {
    cat(sprintf("  临界 Gamma = %.1f（超过此值结论不再稳健）\n", critical_gamma))
  } else {
    cat("  在测试的 Gamma 范围内，结论均稳健。\n")
  }

  return(list(
    results = results,
    critical_gamma = critical_gamma,
    diffs = diffs
  ))
}

#' 绘制 Rosenbaum bounds 敏感性图
#'
#' @param sens_result rosenbaum_sensitivity 的返回结果
#' @param title 字符串，标题
#'
#' @return ggplot 对象
plot_rosenbaum_bounds <- function(sens_result, title = "Rosenbaum Bounds Sensitivity Analysis") {
  df <- sens_result$results

  p <- ggplot(df, aes(x = Gamma)) +
    geom_ribbon(aes(ymin = p_lower, ymax = p_upper),
                fill = "steelblue", alpha = 0.3) +
    geom_line(aes(y = p_lower), color = "steelblue", linewidth = 0.8) +
    geom_line(aes(y = p_upper), color = "red", linewidth = 0.8) +
    geom_hline(yintercept = 0.05, linetype = "dashed", color = "grey50") +
    annotate("text", x = max(df$Gamma), y = 0.06,
             label = "p = 0.05", hjust = 1, size = 3, color = "grey50") +
    labs(title = title,
         x = expression(Gamma ~ "(Hidden Bias)"),
         y = "p-value",
         color = "Bound") +
    theme_minimal(base_size = 12) +
    theme(plot.title = element_text(face = "bold"))

  if (!is.na(sens_result$critical_gamma)) {
    p <- p +
      geom_vline(xintercept = sens_result$critical_gamma,
                 linetype = "dotted", color = "darkred") +
      annotate("text", x = sens_result$critical_gamma, y = 0.5,
               label = sprintf("Critical Gamma = %.1f", sens_result$critical_gamma),
               angle = 90, hjust = 0, vjust = -0.5, size = 3, color = "darkred")
  }

  return(p)
}


# ============================================================================
# 6. 完整 PSM 工作流
# ============================================================================

#' 完整倾向性评分匹配工作流
#'
#' 执行完整的 PSM 分析：PS 估计 → 匹配 → 平衡诊断 → 效应估计 → 敏感性分析
#'
#' @param data data.frame，分析数据集
#' @param treatment 字符串，处理变量名
#' @param outcome 字符串，结局变量名
#' @param covariates 字符向量，协变量名
#' @param cat_vars 字符向量，分类协变量名（可选）
#' @param method 字符串，匹配方法："nearest"（默认）、"optimal"、"full"
#' @param ratio 整数，匹配比例
#' @param caliper 数值，卡钳值
#' @param do_sensitivity 逻辑，是否执行敏感性分析
#'
#' @return list，包含所有分析结果
#'
#' @examples
#' \dontrun{
#' results <- full_psm_workflow(df, "treatment", "outcome",
#'                              c("age", "bmi", "sex"))
#' }
full_psm_workflow <- function(data, treatment, outcome, covariates,
                              cat_vars = NULL, method = "nearest",
                              ratio = 1, caliper = 0.2,
                              do_sensitivity = TRUE) {
  results <- list()

  # Step 1: 倾向性评分估计
  cat("=" , rep("=", 49), "\n", sep = "")
  cat("Step 1: 倾向性评分估计\n")
  cat("=" , rep("=", 49), "\n", sep = "")
  ps_result <- estimate_propensity(data, treatment, covariates)
  results$ps_result <- ps_result
  data_ps <- ps_result$data

  # Step 2: 匹配
  cat("\n", rep("=", 50), "\n", sep = "")
  cat("Step 2: 匹配 (", method, ")\n", sep = "")
  cat(rep("=", 50), "\n", sep = "")
  if (method == "nearest") {
    match_result <- nearest_neighbor_match(data_ps, treatment, covariates,
                                           ratio = ratio, caliper = caliper)
  } else if (method == "optimal") {
    match_result <- optimal_match(data_ps, treatment, covariates,
                                  ratio = ratio, caliper = caliper)
  } else if (method == "full") {
    match_result <- full_match(data_ps, treatment, covariates)
  } else {
    stop("method 必须是 'nearest', 'optimal' 或 'full'")
  }
  results$match_result <- match_result
  matched_data <- match_result$matched_data

  # Step 3: 平衡诊断
  cat("\n", rep("=", 50), "\n", sep = "")
  cat("Step 3: 平衡诊断\n")
  cat(rep("=", 50), "\n", sep = "")
  smd_before <- compute_smd(data, treatment, covariates)
  smd_after <- compute_smd(matched_data, treatment, covariates,
                           weights = if ("weights" %in% names(matched_data))
                             matched_data$weights else NULL)
  results$smd_before <- smd_before
  results$smd_after <- smd_after

  bal_diag <- balance_diagnostics(match_result$match_obj, covariates, data)
  results$balance_diagnostics <- bal_diag

  # Love plot
  results$love_plot <- love_plot(match_result$match_obj)

  # Step 4: 效应估计
  cat("\n", rep("=", 50), "\n", sep = "")
  cat("Step 4: 处理效应估计\n")
  cat(rep("=", 50), "\n", sep = "")
  effect <- estimate_effect(matched_data, treatment, outcome, estimand = "ATT")
  results$effect <- effect

  # Step 5: 敏感性分析
  if (do_sensitivity) {
    cat("\n", rep("=", 50), "\n", sep = "")
    cat("Step 5: Rosenbaum bounds 敏感性分析\n")
    cat(rep("=", 50), "\n", sep = "")
    sens <- rosenbaum_sensitivity(matched_data, treatment, outcome)
    results$sensitivity <- sens
    results$sensitivity_plot <- plot_rosenbaum_bounds(sens)
  }

  cat("\n PSM 分析完成\n")

  return(results)
}


# ============================================================================
# 示例用法
# ============================================================================

if (interactive() || isTRUE(getOption("run_psm_example"))) {
  set.seed(42)
  n <- 500

  # 模拟观察性数据
  age <- rnorm(n, mean = 60, sd = 10)
  bmi <- rnorm(n, mean = 26, sd = 5)
  smoking <- rbinom(n, 1, 0.3)

  # 处理分配（受协变量影响 → 存在混杂）
  logit_treat <- -2 + 0.03 * age + 0.05 * bmi + 0.5 * smoking
  prob_treat <- 1 / (1 + exp(-logit_treat))
  treatment <- rbinom(n, 1, prob_treat)

  # 结局（连续变量，受处理和协变量影响）
  outcome <- 10 + 2 * treatment + 0.1 * age + 0.3 * bmi + 1 * smoking + rnorm(n, sd = 2)

  df <- data.frame(
    treatment = treatment,
    outcome = outcome,
    age = age,
    bmi = bmi,
    smoking = smoking
  )

  # 运行完整 PSM 工作流
  results <- full_psm_workflow(
    data = df,
    treatment = "treatment",
    outcome = "outcome",
    covariates = c("age", "bmi", "smoking"),
    method = "nearest",
    ratio = 1,
    caliper = 0.2,
    do_sensitivity = TRUE
  )

  cat("\n=== 匹配前 SMD ===\n")
  print(results$smd_before)
  cat("\n=== 匹配后 SMD ===\n")
  print(results$smd_after)
  cat("\n=== 处理效应 ===\n")
  cat(sprintf("ATT = %.4f (95%% CI: [%.4f, %.4f], p = %.4f)\n",
              results$effect$estimate,
              results$effect$ci_lower,
              results$effect$ci_upper,
              results$effect$p_value))

  cat("\n PSM 分析示例完成\n")
}
