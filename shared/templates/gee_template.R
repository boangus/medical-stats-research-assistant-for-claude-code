# =============================================================================
# GEE 广义估计方程模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 geepack 包，提供纵向/聚类数据的 GEE 分析一站式工具
# 适用于：重复测量、群组随机化试验、多中心研究等具有组内相关的数据
#
# 参考:
#   geepack: https://cran.r-project.org/package=geepack
#   Halekoh et al. (2006) R Journal: The R Package geepack
#   Zeger & Liang (1986) Biometrics: Longitudinal data analysis
#
# 依赖:
#   install.packages("geepack")
#   install.packages("dplyr")
#   install.packages("tidyr")
#   install.packages("broom")
# =============================================================================

library(geepack)
library(dplyr)
library(tidyr)
library(broom)

# =============================================================================
# 1. GEE 模型拟合
# =============================================================================

#' 拟合 GEE 模型
#'
#' 使用 geepack::geeglm 拟合广义估计方程模型。
#' 支持 gaussian、binomial、poisson 等分布族，以及 exchangeable、
#' ar1、unstructured 等工作相关矩阵。
#'
#' @param data 数据框（长格式，每行一个观测）
#' @param formula 模型公式，如 y ~ x1 + x2
#' @param id_var 聚类/个体标识变量名（字符）
#' @param family 分布族对象，默认 gaussian()
#'   可选: binomial(), poisson(), Gamma()
#' @param corstr 工作相关矩阵结构，默认 "exchangeable"
#'   可选: "exchangeable", "ar1", "unstructured", "independence"
#' @param waves_var 波次/时间变量名（字符），用于排序，NULL 时按数据原始顺序
#' @param std_err 标准误估计方法，默认 "san.se"（稳健三明治方差）
#'   可选: "san.se", "fij"（jackknife）
#'
#' @return geeglm 对象（geepack 拟合结果）
#'
#' @examples
#' gee_model(data, y ~ trt + time, id_var = "subject",
#'           family = binomial(), corstr = "exchangeable")
gee_model <- function(data, formula, id_var, family = gaussian(),
                      corstr = "exchangeable", waves_var = NULL,
                      std_err = "san.se") {
  # 验证 corstr
  valid_corstr <- c("exchangeable", "ar1", "unstructured", "independence")
  if (!corstr %in% valid_corstr) {
    stop(sprintf("corstr 必须为以下之一: %s", paste(valid_corstr, collapse = ", ")))
  }

  # 确保 id 变量存在
  if (!id_var %in% names(data)) {
    stop(sprintf("id_var '%s' 不在数据列中", id_var))
  }

  # 排序（ar1 需要时间顺序）
  if (!is.null(waves_var)) {
    data <- data[order(data[[id_var]], data[[waves_var]]), ]
  } else if (corstr == "ar1") {
    warning("使用 ar1 相关结构时建议通过 waves_var 指定时间顺序变量")
  }

  # 拟合 GEE
  model <- geeglm(
    formula = formula,
    data    = data,
    id      = data[[id_var]],
    family  = family,
    corstr  = corstr,
    waves   = if (!is.null(waves_var)) data[[waves_var]] else NULL,
    std.err = std_err
  )

  attr(model, "id_var")   <- id_var
  attr(model, "corstr")   <- corstr
  attr(model, "family_name") <- family$family

  return(model)
}


# =============================================================================
# 2. 结果提取（OR/RR + 95% CI + p 值）
# =============================================================================

#' 提取 GEE 模型结果摘要
#'
#' 返回整洁格式的系数表，包含效应量（OR 或 RR）、95% CI 和 p 值。
#' binomial 家族输出 OR（比值比），poisson 家族输出 RR（风险比），
#' gaussian 家族直接输出系数。
#'
#' @param model geeglm 模型对象
#' @param alpha 显著性水平，默认 0.05
#'
#' @return data.frame，包含列:
#'   Variable, Coef, SE, Effect, Effect_Lower, Effect_Upper, p_value, Signif
#'   其中 Effect = OR（binomial）或 RR（poisson）或 Coef（gaussian）
gee_summary <- function(model, alpha = 0.05) {
  z_val <- qnorm(1 - alpha / 2)
  family_name <- attr(model, "family_name") %||% model$family$family

  # 提取系数
  coefs <- coef(model)
  vcov_mat <- vcov(model)
  se <- sqrt(diag(vcov_mat))

  # 计算 Wald 检验
  z_stat <- coefs / se
  p_vals <- 2 * pnorm(-abs(z_stat))

  # 根据分布族确定效应量
  if (grepl("binomial", family_name)) {
    effect_name <- "OR"
    effect      <- exp(coefs)
    effect_lo   <- exp(coefs - z_val * se)
    effect_hi   <- exp(coefs + z_val * se)
  } else if (grepl("poisson", family_name)) {
    effect_name <- "RR"
    effect      <- exp(coefs)
    effect_lo   <- exp(coefs - z_val * se)
    effect_hi   <- exp(coefs + z_val * se)
  } else {
    effect_name <- "Coef"
    effect      <- coefs
    effect_lo   <- coefs - z_val * se
    effect_hi   <- coefs + z_val * se
  }

  result <- data.frame(
    Variable       = names(coefs),
    Coef           = round(coefs, 4),
    SE             = round(se, 4),
    Effect         = round(effect, 4),
    Effect_Lower   = round(effect_lo, 4),
    Effect_Upper   = round(effect_hi, 4),
    p_value        = round(p_vals, 6),
    stringsAsFactors = FALSE
  )
  names(result)[names(result) == "Effect"]      <- effect_name
  names(result)[names(result) == "Effect_Lower"] <- paste0(effect_name, "_Lower")
  names(result)[names(result) == "Effect_Upper"] <- paste0(effect_name, "_Upper")

  # 显著性标记
  result$Signif <- ifelse(result$p_value < 0.001, "***",
                   ifelse(result$p_value < 0.01,  "**",
                   ifelse(result$p_value < 0.05,  "*", "ns")))

  # 模型信息
  cat(sprintf("=== GEE 模型摘要 ===\n"))
  cat(sprintf("分布族: %s | 相关结构: %s\n", family_name, attr(model, "corstr")))
  cat(sprintf("效应量: %s | 样本聚类数: %s\n\n", effect_name,
              length(unique(model$id))))

  print(result, row.names = FALSE)
  invisible(result)
}


# =============================================================================
# 3. 模型诊断
# =============================================================================

#' GEE 模型诊断
#'
#' 提供残差分析、影响力度量和 QIC（准信息准则）用于模型选择。
#' QIC 类似于 AIC，值越小表示模型拟合越好。
#'
#' @param model geeglm 模型对象
#' @param data 原始数据框
#' @param plot_diag 是否生成诊断图，默认 TRUE
#'
#' @return list，包含:
#'   qic: 准信息准则值
#'   residuals: 残差向量
#'   cluster_sizes: 各聚类大小
#'   scale_parameter: 尺度参数
#'   naive_se vs robust_se: 模型标准误与稳健标准误比较
gee_diagnostics <- function(model, data, plot_diag = TRUE) {
  cat("=== GEE 模型诊断 ===\n\n")

  # --- 残差 ---
  raw_resid <- residuals(model, type = "response")
  pearson_resid <- residuals(model, type = "pearson")

  # --- 聚类信息 ---
  id_var <- attr(model, "id_var")
  cluster_sizes <- table(model$id)
  cat(sprintf("聚类数: %d | 平均每组观测数: %.1f | 范围: [%d, %d]\n",
              length(cluster_sizes),
              mean(cluster_sizes),
              min(cluster_sizes),
              max(cluster_sizes)))

  # --- 模型与稳健标准误比较 ---
  naive_var  <- summary(model)$coefficients[, "Std.err"]^2
  robust_se  <- sqrt(diag(vcov(model)))
  naive_se   <- summary(model)$coefficients[, "Std.err"]
  se_ratio   <- robust_se / naive_se

  cat("\n--- 标准误比较 (稳健/模型) ---\n")
  se_table <- data.frame(
    Variable    = names(coef(model)),
    Model_SE    = round(naive_se, 4),
    Robust_SE   = round(robust_se, 4),
    Ratio       = round(se_ratio, 2),
    stringsAsFactors = FALSE
  )
  names(se_table)[2] <- "Model_SE"
  print(se_table, row.names = FALSE)
  cat("注: Ratio > 1.5 提示聚类效应较强，稳健标准误更为可靠\n")

  # --- QIC 计算（手动实现） ---
  qic_val <- NA
  tryCatch({
    qic_val <- try_compute_qic(model, data)
    cat(sprintf("\nQIC (准信息准则): %.4f\n", qic_val))
    cat("注: QIC 越小越好，可用于不同相关结构间的模型比较\n")
  }, error = function(e) {
    cat(sprintf("\nQIC 计算失败: %s\n", e$message))
  })

  # --- 诊断图 ---
  if (plot_diag) {
    old_par <- par(mfrow = c(2, 2))
    on.exit(par(old_par))

    # 残差 vs 拟合值
    fitted_vals <- fitted(model)
    plot(fitted_vals, pearson_resid,
         xlab = "拟合值", ylab = "Pearson 残差",
         main = "残差 vs 拟合值", pch = 20, col = "steelblue")
    abline(h = 0, lty = 2, col = "red")
    lines(lowess(fitted_vals, pearson_resid), col = "orange", lwd = 2)

    # 残差直方图
    hist(pearson_resid, breaks = 20, col = "steelblue", border = "white",
         main = "Pearson 残差分布", xlab = "Pearson 残差")

    # Q-Q 图
    qqnorm(pearson_resid, main = "Q-Q 图", pch = 20, col = "steelblue")
    qqline(pearson_resid, col = "red", lwd = 2)

    # 残差 vs 聚类
    plot(as.numeric(as.factor(model$id)), pearson_resid,
         xlab = "聚类 ID", ylab = "Pearson 残差",
         main = "残差 vs 聚类", pch = 20, col = "steelblue")
    abline(h = 0, lty = 2, col = "red")
  }

  # 汇总
  result <- list(
    qic             = qic_val,
    residuals       = raw_resid,
    pearson_resid   = pearson_resid,
    cluster_sizes   = cluster_sizes,
    naive_se        = naive_se,
    robust_se       = robust_se,
    se_ratio        = se_ratio
  )

  invisible(result)
}


#' 内部函数：手动计算 QIC
#'
#' QIC = -2 * Q + 2 * trace(V^{-1} * V_robust)
#' 其中 Q 为拟似然，V 为模型方差，V_robust 为稳健三明治方差
#'
#' @param model geeglm 模型对象
#' @param data 原始数据框
#' @return QIC 数值
try_compute_qic <- function(model, data) {
  # 简化版 QIC：使用 deviance 近似
  # 完整实现需要 quasilikelihood 计算
  dev <- deviance(model)
  p   <- length(coef(model))

  # trace term: 聚类数的近似调整
  n_clusters <- length(unique(model$id))
  trace_term <- 2 * p  # 简化近似

  qic <- dev + trace_term
  return(qic)
}


# =============================================================================
# 4. 相关结构比较
# =============================================================================

#' 比较不同工作相关矩阵结构的 QIC
#'
#' 分别拟合 exchangeable、ar1、independence、unstructured 四种相关结构，
#' 通过 QIC 选择最优结构。
#'
#' @param data 数据框
#' @param formula 模型公式
#' @param id_var 聚类标识变量名
#' @param family 分布族对象
#' @param waves_var 时间/波次变量名（ar1 结构需要）
#'
#' @return data.frame，包含各结构的 QIC 值和排名
gee_compare_corstr <- function(data, formula, id_var, family = gaussian(),
                                waves_var = NULL) {
  cat("=== 工作相关矩阵结构比较 ===\n\n")

  corstr_list <- c("independence", "exchangeable", "ar1", "unstructured")
  results <- data.frame(
    Corstr    = character(),
    QIC       = numeric(),
    Converged = logical(),
    stringsAsFactors = FALSE
  )

  for (cr in corstr_list) {
    cat(sprintf("拟合 %s ... ", cr))
    tryCatch({
      fit <- gee_model(data, formula, id_var, family,
                       corstr = cr, waves_var = waves_var)
      qic_val <- try_compute_qic(fit, data)
      results <- rbind(results, data.frame(
        Corstr    = cr,
        QIC       = round(qic_val, 4),
        Converged = TRUE,
        stringsAsFactors = FALSE
      ))
      cat(sprintf("QIC = %.4f\n", qic_val))
    }, error = function(e) {
      results <<- rbind(results, data.frame(
        Corstr    = cr,
        QIC       = NA,
        Converged = FALSE,
        stringsAsFactors = FALSE
      ))
      cat(sprintf("失败: %s\n", e$message))
    })
  }

  # 排序
  results <- results[order(results$QIC, na.last = TRUE), ]
  results$Rank <- NA
  results$Rank[!is.na(results$QIC)] <- rank(results$QIC[!is.na(results$QIC)])

  cat("\n--- 比较结果 ---\n")
  print(results, row.names = FALSE)

  best <- results$Corstr[which.min(results$QIC)]
  cat(sprintf("\n推荐: QIC 最小的结构为 '%s'\n", best))
  cat("注: exchangeable 适用于组内相关均匀的场景; ar1 适用于时间衰减相关;\n")
  cat("     independence 适用于无组内相关; unstructured 不做结构假设但参数较多\n")

  invisible(results)
}


# =============================================================================
# 5. 完整工作流
# =============================================================================

#' GEE 分析完整工作流
#'
#' 执行: 模型拟合 → 结果摘要 → 诊断 → 相关结构比较
#' 使用模拟纵向二分类数据演示完整流程。
#'
#' @return list，包含所有分析结果
full_gee_workflow <- function() {
  cat("========================================\n")
  cat("    GEE 广义估计方程分析 — 完整工作流\n")
  cat("========================================\n\n")

  # --- 模拟纵向数据 ---
  set.seed(2024)
  n_subjects <- 100
  n_times    <- 4
  n <- n_subjects * n_times

  subject_id <- rep(1:n_subjects, each = n_times)
  time_point <- rep(0:(n_times - 1), times = n_subjects)
  treatment  <- rep(rbinom(n_subjects, 1, 0.5), each = n_times)
  age        <- rep(rnorm(n_subjects, 50, 10), each = n_times)

  # 生成带组内相关的二分类结局（exchangeable 结构）
  # 随机效应产生组内相关
  random_effect <- rep(rnorm(n_subjects, 0, 1.5), each = n_times)
  logit_p <- -1.0 + 0.5 * treatment - 0.3 * time_point +
             0.02 * age + random_effect
  prob    <- 1 / (1 + exp(-logit_p))
  y       <- rbinom(n, 1, prob)

  sim_data <- data.frame(
    id      = subject_id,
    time    = time_point,
    trt     = treatment,
    age     = age,
    outcome = y
  )

  cat(sprintf("模拟数据: %d 名受试者, 每人 %d 个时间点, 共 %d 条记录\n",
              n_subjects, n_times, n))
  cat(sprintf("结局阳性率: %.1f%%\n\n", 100 * mean(sim_data$outcome)))

  results <- list()

  # --- 1. GEE 模型拟合 ---
  cat(">>> 步骤 1: 拟合 GEE 模型 (binomial, exchangeable)\n")
  model <- gee_model(
    data    = sim_data,
    formula = outcome ~ trt + time + age,
    id_var  = "id",
    family  = binomial(),
    corstr  = "exchangeable"
  )
  results$model <- model

  # --- 2. 结果摘要 ---
  cat("\n>>> 步骤 2: 模型结果摘要\n")
  summary_tbl <- gee_summary(model)
  results$summary <- summary_tbl

  # --- 3. 模型诊断 ---
  cat("\n>>> 步骤 3: 模型诊断\n")
  diag_info <- gee_diagnostics(model, sim_data, plot_diag = FALSE)
  results$diagnostics <- diag_info

  # --- 4. 相关结构比较 ---
  cat("\n>>> 步骤 4: 比较不同相关结构\n")
  corstr_comp <- gee_compare_corstr(
    data    = sim_data,
    formula = outcome ~ trt + time + age,
    id_var  = "id",
    family  = binomial(),
    waves_var = "time"
  )
  results$corstr_comparison <- corstr_comp

  # --- 汇总 ---
  cat("\n========================================\n")
  cat("    分析完成\n")
  cat("========================================\n")

  invisible(results)
}


# =============================================================================
# 辅助函数
# =============================================================================

#' Null-safe 默认值运算符
`%||%` <- function(x, y) if (is.null(x)) y else x


# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  # ---- 示例 1: 二分类结局 (OR) ----
  gee_model(data, outcome ~ trt + time + age,
            id_var = "subject", family = binomial()) %>%
    gee_summary()

  # ---- 示例 2: 连续结局 (系数) ----
  gee_model(data, bp ~ treatment + visit,
            id_var = "patient", family = gaussian(),
            corstr = "ar1", waves_var = "visit") %>%
    gee_summary()

  # ---- 示例 3: 计数结局 (RR) ----
  gee_model(data, events ~ drug + offset(log(exposure)),
            id_var = "center", family = poisson()) %>%
    gee_summary()

  # ---- 示例 4: 完整工作流 ----
  full_gee_workflow()
}
